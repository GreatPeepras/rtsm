#!/usr/bin/env python3
"""Normalize a raw rtsm-review export into the executor's schema.
Adds `winner` (survivor oid) to every merge, resolving raw-name merge_into
against live corpus label_user (case/backtick-insensitive). Refuses on any
unresolved/ambiguous name. GET /objects only (read-only)."""
import argparse, json, urllib.request, sys, re

def _norm(s):
    return re.sub(r"[`'\s]+", " ", s).strip().lower() if s else ""

def fetch_oids(base):
    oids = {}; off = 0
    while True:
        req = urllib.request.Request(f"{base}/objects?pose_state=any&limit=500&offset={off}")
        with urllib.request.urlopen(req, timeout=60) as r:
            p = json.loads(r.read().decode() or "{}")
        got = p.get("objects", [])
        for o in got:
            oids[o["id"]] = o.get("label_user") or o.get("display_label")
        total = p.get("total", len(oids)); off += len(got)
        if not got or off >= total: break
    return oids

def is_hexoid(s):
    return isinstance(s,str) and len(s)==16 and all(c in "0123456789abcdef" for c in s)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", default="rtsm_decisions.json")
    ap.add_argument("--out", default="rtsm_decisions_normalized.json")
    ap.add_argument("--base", default="http://localhost:8002")
    args = ap.parse_args()
    data = json.load(open(args.inp)); dec = data["decisions"]
    live = fetch_oids(args.base)
    by_label = {}
    for oid, lab in live.items():
        if lab: by_label.setdefault(_norm(lab), []).append(oid)
    named_this_run = {}
    for k,v in dec.items():
        if v["action"]=="name" and (v.get("name") or "").strip():
            named_this_run.setdefault(_norm(v["name"]), []).append(k)
    survset = {k for k,v in dec.items() if v["action"] in ("keep","name")}
    problems = []
    for k,v in dec.items():
        if v["action"] != "merge": continue
        mi = v.get("merge_into")
        if is_hexoid(mi):
            v["winner"] = mi
        else:
            key = _norm(mi)
            all_c = list(dict.fromkeys(by_label.get(key,[]) + named_this_run.get(key,[])))
            surv_c = [o for o in all_c if o in survset]
            pick = surv_c or all_c
            if len(pick)==1: v["winner"] = pick[0]
            elif not pick: problems.append(("UNRESOLVED", k[:8], mi))
            else: problems.append(("AMBIGUOUS", k[:8], mi, [c[:8] for c in pick]))
        w = v.get("winner")
        if w and w not in survset and w not in live:
            problems.append(("WINNER_NOT_IN_CORPUS", k[:8], (w[:8] if w else None)))
    print(f"[*] {len(dec)} decisions, {sum(1 for v in dec.values() if v['action']=='merge')} merges")
    if problems:
        print(f"[REFUSE] {len(problems)} resolution problem(s):")
        for p in problems: print("   ", p)
        print("\n[no file written]")
        # help: dump live labels containing a hint of each unresolved name
        miss_names = {p[2] for p in problems if p[0] in ("UNRESOLVED","AMBIGUOUS")}
        for mn in miss_names:
            hint = _norm(mn).split()[0]
            near = sorted({lab for lab in live.values() if lab and hint[:4] in _norm(lab)})
            if near: print(f"    live labels near {mn!r}: {near}")
        return 1
    json.dump(data, open(args.out,"w"), indent=1)
    from collections import Counter
    print(f"[OK] wrote {args.out}:", dict(Counter(v['action'] for v in dec.values())))
    return 0

if __name__ == "__main__":
    sys.exit(main())
