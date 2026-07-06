#!/usr/bin/env python3
"""
rtsm_cleanup_exec_2026-07-02.py

Executes a normalized RTSM cleanup decision set against the live API.
Order: delete -> merge -> name(+flush) -> verify index rebuilt.

Endpoints used (all confirmed live 2026-07-02):
  DELETE /objects/{oid}                      (FAISS sidecar removed)
  POST   /objects/merge {winner_oid,loser_oid,dry_run}   (FAISS-synced)
  PATCH  /objects/{oid} {label_user}          (force_flush_now + upsert -> rebuild)

Modes:
  --check    compare normalized set against the live corpus, no writes
  --dryrun   validate + print the ordered plan, no writes   (DEFAULT)
  --apply    back up FAISS sidecars, then execute; writes remap + audit
  --revert   stop container, restore the FAISS backup, start container

Safety:
  * refuses to run if the normalized file still has any blocker
  * --apply always snapshots the FAISS sidecars first
  * idempotent-ish: 404s (already gone / already merged) are skipped, not fatal
  * emits rtsm_cleanup_remap_<ts>.json  (loser->winner, deleted[], names{})
    to drive the Albert memory-link (rtsm_oid) reconciliation next bench session
"""
import argparse, json, os, shutil, subprocess, sys, time, urllib.request, urllib.error

def _req(method, url, body=None, timeout=60):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, method=method,
                               headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        try: payload = json.loads(e.read().decode() or "{}")
        except Exception: payload = {}
        return e.code, payload

def fetch_oids(base):
    oids = {}
    off = 0
    while True:
        s, p = _req("GET", f"{base}/objects?pose_state=any&limit=500&offset={off}")
        got = p.get("objects", [])
        for o in got:
            oids[o["id"]] = o.get("label_user") or o.get("display_label")
        total = p.get("total", len(oids))
        off += len(got)
        if not got or off >= total: break
    return oids

def load_norm(path):
    d = json.load(open(path))
    dec = d["decisions"]
    survset = {k for k, v in dec.items() if v["action"] in ("keep", "name")}
    blockers = []
    for k, v in dec.items():
        if v["action"] == "name" and not (v.get("name") or "").strip():
            blockers.append(("empty_name", k))
        if v["action"] == "merge":
            w = v.get("winner")
            if w not in survset: blockers.append(("winner_not_survivor", k, w))
            if dec.get(w, {}).get("action") == "merge": blockers.append(("chain", k, w))
            if w == k: blockers.append(("self_merge", k))
    return dec, survset, blockers

def plan(dec):
    dels  = [k for k, v in dec.items() if v["action"] == "delete"]
    merges= [(k, v["winner"]) for k, v in dec.items() if v["action"] == "merge"]
    names = [(k, v["name"]) for k, v in dec.items() if v["action"] == "name"]
    keeps = [k for k, v in dec.items() if v["action"] == "keep"]
    return dels, merges, names, keeps

def backup_faiss(faiss_dir, backup_root):
    ts = time.strftime("%Y%m%d-%H%M%S")
    dst = os.path.join(backup_root, f"faiss.bak.{ts}")
    shutil.copytree(faiss_dir, dst)
    return dst

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--normalized", default="rtsm_decisions_normalized.json")
    ap.add_argument("--base", default="http://localhost:8002")
    ap.add_argument("--faiss-dir", default="/mnt/rtsm-data/model_store/faiss")
    ap.add_argument("--backup-root", default="/mnt/rtsm-data/model_store")
    ap.add_argument("--compose-dir", default=os.path.expanduser("~/rtsm/docker"))
    ap.add_argument("--restore-from", default=None, help="faiss.bak dir for --revert")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--dryrun", action="store_true")
    g.add_argument("--apply", action="store_true")
    g.add_argument("--revert", action="store_true")
    g.add_argument("--check", action="store_true")
    args = ap.parse_args()
    mode = ("apply" if args.apply else "revert" if args.revert
            else "check" if args.check else "dryrun")

    # ---------- revert ----------
    if mode == "revert":
        if not args.restore_from or not os.path.isdir(args.restore_from):
            sys.exit("--revert needs --restore-from <faiss.bak.DIR>")
        print(f"[revert] stopping rtsm-dev (must stop or it re-saves stale state)")
        subprocess.run(["docker", "compose", "stop", "rtsm-dev"], cwd=args.compose_dir, check=True)
        for f in os.listdir(args.restore_from):
            shutil.copy2(os.path.join(args.restore_from, f), os.path.join(args.faiss_dir, f))
        print(f"[revert] restored sidecars from {args.restore_from}")
        subprocess.run(["docker", "compose", "start", "rtsm-dev"], cwd=args.compose_dir, check=True)
        print("[revert] rtsm-dev restarted. Corpus is back to the pre-clean snapshot.")
        return

    dec, survset, blockers = load_norm(args.normalized)
    if blockers:
        print(f"[REFUSE] {len(blockers)} blocker(s) in {args.normalized}:")
        for b in blockers[:20]: print("   ", b)
        sys.exit(1)
    dels, merges, names, keeps = plan(dec)

    live = fetch_oids(args.base)
    print(f"[*] live corpus: {len(live)} objects   normalized: {len(dec)} decisions")
    print(f"[*] plan: delete {len(dels)} | merge {len(merges)} | name {len(names)} | keep {len(keeps)}")
    expected = len(survset)
    print(f"[*] expected corpus after apply: {expected} survivors "
          f"({sum(1 for k in survset if dec[k].get('name'))} named this run + kept)")

    # existence validation
    missing = {"delete": [], "merge_loser": [], "merge_winner": [], "name": []}
    for k in dels:
        if k not in live: missing["delete"].append(k)
    for k, w in merges:
        if k not in live: missing["merge_loser"].append(k)
        if w not in live: missing["merge_winner"].append(w)
    for k, _ in names:
        if k not in live: missing["name"].append(k)
    anymiss = any(missing.values())
    if anymiss:
        print("[!] referenced oids not in live corpus (will be skipped):")
        for kind, lst in missing.items():
            if lst: print(f"    {kind}: {len(lst)}  e.g. {[x[:8] for x in lst[:6]]}")

    if mode == "check":
        print("[check] no writes performed.")
        return
    if mode == "dryrun":
        print("\n-- ordered plan preview --")
        print(f"  1) DELETE {len(dels)} objects")
        print(f"  2) MERGE  {len(merges)} losers into winners")
        print(f"  3) PATCH  {len(names)} names (+flush)")
        print("     e.g. names:", [(k[:8], n) for k, n in names[:8]])
        print("\n[dryrun] no writes. Re-run with --apply to execute.")
        return

    # ---------- apply ----------
    if not os.path.isdir(args.faiss_dir):
        sys.exit(f"faiss dir not found: {args.faiss_dir}")
    bak = backup_faiss(args.faiss_dir, args.backup_root)
    print(f"[apply] FAISS sidecars backed up -> {bak}")
    print(f"[apply] revert with:  python3 {os.path.basename(sys.argv[0])} --revert --restore-from {bak}")

    ts = time.strftime("%Y%m%d-%H%M%S")
    remap = {"deleted": [], "merged": {}, "named": {}, "errors": []}
    log = open(f"rtsm_cleanup_log_{ts}.tsv", "w")
    def logline(*a): log.write("\t".join(str(x) for x in a) + "\n"); log.flush()

    # 1) DELETE
    print(f"\n[1/3] deleting {len(dels)} ...")
    for i, k in enumerate(dels):
        if k not in live: logline("delete", k, "skip_absent"); continue
        s, p = _req("DELETE", f"{args.base}/objects/{k}")
        if s == 200 and p.get("removed"):
            remap["deleted"].append(k); logline("delete", k, "ok", p.get("faiss_sidecar_removed"))
        elif s == 404: logline("delete", k, "skip_404")
        else: remap["errors"].append(("delete", k, s, p)); logline("delete", k, "ERR", s, p)
        if i % 50 == 0: print(f"    ...{i}/{len(dels)}")

    # 2) MERGE
    print(f"[2/3] merging {len(merges)} ...")
    for i, (k, w) in enumerate(merges):
        s, p = _req("POST", f"{args.base}/objects/merge",
                    {"winner_oid": w, "loser_oid": k, "dry_run": False})
        if s == 200:
            remap["merged"][k] = w
            if p.get("faiss_sync_warning"): logline("merge", k, w, "ok_warn", p["faiss_sync_warning"])
            else: logline("merge", k, w, "ok")
        elif s == 404: logline("merge", k, w, "skip_404")
        else: remap["errors"].append(("merge", k, w, s, p)); logline("merge", k, w, "ERR", s, p)
        if i % 50 == 0: print(f"    ...{i}/{len(merges)}")

    # 3) NAME (PATCH -> force_flush_now -> upsert -> index rebuild)
    print(f"[3/3] naming {len(names)} ...")
    for k, n in names:
        s, p = _req("PATCH", f"{args.base}/objects/{k}", {"label_user": n})
        if s == 200:
            remap["named"][k] = n; logline("name", k, n, "ok")
        else: remap["errors"].append(("name", k, n, s, p)); logline("name", k, n, "ERR", s, p)

    # verify index rebuilt (delete() empties it; last upserts should have rebuilt)
    s, st = _req("GET", f"{args.base}/stats")
    s2, probe = _req("GET", f"{args.base}/search/semantic?query=bed&top_k=3&pose_state=any")
    idx_ok = bool(probe.get("results"))
    print(f"\n[done] corpus now: {st.get('objects')} objects "
          f"(expected {expected})   semantic-index probe: {'OK' if idx_ok else 'EMPTY'}")
    if not idx_ok:
        print("[!] semantic index reads empty. Re-PATCH any named object to force a rebuild, "
              "or restart rtsm-dev (rehydrate reloads embeddings). WM/nav are unaffected.")
    if remap["errors"]:
        print(f"[!] {len(remap['errors'])} errors — see log; safe to re-run --apply (idempotent).")

    json.dump(remap, open(f"rtsm_cleanup_remap_{ts}.json", "w"), indent=1)
    log.close()
    print(f"[apply] remap -> rtsm_cleanup_remap_{ts}.json   log -> rtsm_cleanup_log_{ts}.tsv")
    print("        (remap drives the Albert memory rtsm_oid reconciliation next bench session)")

if __name__ == "__main__":
    main()
