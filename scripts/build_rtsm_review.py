#!/usr/bin/env python3
"""
build_rtsm_review.py  (v2)  --  RTSM object triage gallery (read-only)

Run on .53. Reads every object's metadata from the live API and ALL its crops
straight off disk, then bakes a self-contained review.html (crops embedded).
Open it, click through crops, triage keep/name/merge/delete, Export a decisions
JSON for the cleanup executor.

Read-only: GET /objects + reads crop JPEGs. Commits nothing.

    python3 build_rtsm_review.py
    python3 build_rtsm_review.py --crops /mnt/rtsm-data/rtsm-workdir/crops \
        --base http://localhost:8002 --out review.html --max-crops 8 --thumb 180
"""

import argparse, base64, glob, io, json, os, sys, urllib.request

def fetch_all(base):
    objs, offset, limit = [], 0, 500
    while True:
        url = (f"{base}/objects?include_snapshot=true&pose_state=any"
               f"&limit={limit}&offset={offset}")
        with urllib.request.urlopen(url, timeout=60) as r:
            page = json.loads(r.read().decode())
        got = page.get("objects", [])
        objs.extend(got)
        total = page.get("total", len(objs))
        offset += len(got)
        if not got or offset >= total:
            break
    return objs

def thumb_bytes(raw, size, quality):
    try:
        from PIL import Image
        im = Image.open(io.BytesIO(raw)).convert("RGB")
        im.thumbnail((size, size))
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=quality)
        return base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return base64.b64encode(raw).decode()

def load_crops(oid, crops_dir, max_crops, size, quality, fallback_b64):
    """All crops for oid from disk (newest last), thumbnailed. API fallback."""
    imgs = []
    d = os.path.join(crops_dir, oid)
    if os.path.isdir(d):
        files = sorted(f for f in glob.glob(os.path.join(d, "*.jpg")))
        files = files[-max_crops:] if max_crops else files
        for fp in files:
            try:
                with open(fp, "rb") as fh:
                    imgs.append(thumb_bytes(fh.read(), size, quality))
            except Exception:
                pass
    if not imgs and fallback_b64:
        try:
            imgs.append(thumb_bytes(base64.b64decode(fallback_b64), size, quality))
        except Exception:
            pass
    return imgs

def default_action(o):
    if o.get("label_user"):
        return "keep"
    if o.get("movability_class") in ("static", "semi_static"):
        return "keep"          # localization-anchor candidate -> you decide
    return "delete"            # unnamed movable -> presumed garbage

def build_rows(objs, crops_dir, max_crops, size, quality):
    rows, n = [], len(objs)
    for i, o in enumerate(objs):
        if i % 50 == 0:
            print(f"    ...{i}/{n} crops loaded", file=sys.stderr)
        oid = o.get("id", "")
        imgs = load_crops(oid, crops_dir, max_crops, size, quality,
                          o.get("snapshot_b64"))
        xyz = o.get("xyz_world") or [0, 0, 0]
        rows.append({
            "id": oid, "sid": oid[:8],
            "lp": o.get("label_primary"), "dl": o.get("display_label"),
            "lu": o.get("label_user"),
            "mv": o.get("movability_class") or "movable",
            "vb": o.get("view_bins"), "hits": o.get("hits"),
            "lth": o.get("label_top_hits"),
            "xyz": [round(float(v), 2) for v in xyz],
            "imgs": imgs, "act": default_action(o),
        })
    return rows

HTML = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>RTSM object triage</title>
<style>
:root{--bg:#0f1115;--panel:#171a21;--line:#262b36;--txt:#e6e9ef;--mut:#8b93a3;
--keep:#3a4150;--del:#7a2531;--name:#1f6d3d;--merge:#1f4f7a;--accent:#5aa9ff}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--txt);
font:14px/1.4 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
header{position:sticky;top:0;z-index:20;background:var(--panel);
border-bottom:1px solid var(--line);padding:10px 14px}
.bar{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.bar input[type=text]{background:#0d0f14;border:1px solid var(--line);color:var(--txt);
border-radius:6px;padding:6px 9px;min-width:170px}
.tally{margin-left:auto;display:flex;gap:8px;font-variant-numeric:tabular-nums}
.pill{padding:2px 8px;border-radius:999px;font-size:12px}
.pill.del{background:var(--del)}.pill.keep{background:var(--keep)}
.pill.name{background:var(--name)}.pill.merge{background:var(--merge)}
button{background:#232833;border:1px solid var(--line);color:var(--txt);
border-radius:6px;padding:6px 10px;cursor:pointer;font:inherit}
button:hover{border-color:var(--accent)}
label.chk{display:flex;gap:5px;align-items:center;color:var(--mut);cursor:pointer}
.hint{color:var(--mut);font-size:12px;margin:6px 14px 0}
#mt{margin:6px 14px 0;font-size:13px}
#mt .tgt{background:var(--merge);padding:2px 8px;border-radius:6px}
.grp{margin:16px 14px 0}
.grph{display:flex;gap:10px;align-items:center;position:sticky;top:96px;z-index:10;
background:var(--bg);padding:6px 0;border-bottom:1px solid var(--line)}
.grph h2{margin:0;font-size:15px}.grph .c{color:var(--mut)}
.grid{display:grid;gap:10px;padding:10px 0;
grid-template-columns:repeat(auto-fill,minmax(210px,1fr))}
.card{background:var(--panel);border:1px solid var(--line);border-radius:9px;
overflow:hidden;display:flex;flex-direction:column;position:relative}
.card.act-delete{outline:2px solid var(--del)}
.card.act-keep{outline:2px solid var(--keep)}
.card.act-name{outline:2px solid var(--name)}
.card.act-merge{outline:2px solid var(--merge)}
.card.istarget{box-shadow:0 0 0 3px var(--accent) inset}
.tw{position:relative;width:100%;aspect-ratio:1;background:#000}
.tw img{width:100%;height:100%;object-fit:cover;cursor:zoom-in}
.noimg{width:100%;height:100%;display:flex;align-items:center;justify-content:center;color:var(--mut)}
.cyc{position:absolute;left:0;right:0;bottom:0;display:flex;justify-content:space-between;
align-items:center;padding:3px;background:linear-gradient(transparent,rgba(0,0,0,.6))}
.cyc button{padding:1px 8px;font-size:14px;background:rgba(0,0,0,.5)}
.cyc .cnt{font-size:11px;color:#fff}
.pin{position:absolute;top:4px;right:4px;padding:2px 7px;font-size:13px;
background:rgba(0,0,0,.55)}
.meta{padding:7px 9px;font-size:12px}
.meta .id{font-family:ui-monospace,Menlo,monospace;color:var(--accent)}
.meta .lbl{font-weight:600}.meta .k{color:var(--mut)}
.mv{display:inline-block;padding:1px 6px;border-radius:4px;font-size:11px;background:#2a3140}
.mv.static,.mv.semi_static{background:#2d3a2d;color:#bfe6bf}
.acts{display:flex;border-top:1px solid var(--line)}
.acts button{flex:1;border:0;border-radius:0;border-right:1px solid var(--line);
padding:6px 0;font-size:12px;background:#141821;color:var(--mut)}
.acts button:last-child{border-right:0}
.acts button.on.k{background:var(--keep);color:#fff}
.acts button.on.d{background:var(--del);color:#fff}
.acts button.on.n{background:var(--name);color:#fff}
.acts button.on.m{background:var(--merge);color:#fff}
.xtra{padding:6px 9px}.xtra input{width:100%;background:#0d0f14;border:1px solid var(--line);
color:var(--txt);border-radius:5px;padding:5px 7px;font:inherit}
.xtra .to{color:var(--mut);font-size:11px;margin-bottom:3px}
#lb{position:fixed;inset:0;background:rgba(0,0,0,.92);display:none;z-index:50;
align-items:center;justify-content:center;flex-direction:column}
#lb img{max-width:92vw;max-height:82vh}
#lb .nav{margin-top:10px;display:flex;gap:14px;align-items:center;color:#fff}
#lb .nav button{font-size:18px;padding:4px 14px}
dialog{background:var(--panel);color:var(--txt);border:1px solid var(--line);
border-radius:10px;max-width:640px;width:92%}
dialog textarea{width:100%;height:220px;background:#0d0f14;color:var(--txt);
border:1px solid var(--line);border-radius:6px;font:12px ui-monospace,monospace}
</style></head><body>
<header>
 <div class="bar">
  <strong>RTSM triage</strong>
  <input type="text" id="q" placeholder="filter id / label…">
  <label class="chk"><input type="checkbox" id="fUnnamed">unnamed only</label>
  <label class="chk"><input type="checkbox" id="fMov">movable only</label>
  <label class="chk"><input type="checkbox" id="fGroup" checked>group by label</label>
  <button id="exp">Export decisions</button>
  <button id="imp">Import…</button>
  <div class="tally" id="tally"></div>
 </div>
 <div id="mt"></div>
 <div class="hint">Defaults: named &amp; static/semi &rarr; <b>keep</b>; unnamed movable &rarr; <b>delete</b>.
 To merge: click <b>◎</b> on the object you want to KEEP (the winner), then hit <b>merge</b> on the dups.
 Click a crop to zoom; ‹ › to cycle crops.</div>
</header>
<div id="app"></div>

<div id="lb">
 <img>
 <div class="nav"><button data-lb="-1">‹</button><span class="cnt"></span><button data-lb="1">›</button>
   <button data-lb="x">close (Esc)</button></div>
</div>

<dialog id="dlg">
 <h3>Decisions JSON</h3>
 <p class="k">Copied here + downloaded as rtsm_decisions.json. Paste + "Load" to resume.</p>
 <textarea id="dlgtx"></textarea>
 <div style="margin-top:8px;display:flex;gap:8px">
   <button id="dlgload">Load pasted JSON</button><button id="dlgclose">Close</button>
 </div>
</dialog>

<script>
const DATA = /*__DATA__*/[];
const state={}, byShort={}, imgsById={};
DATA.forEach(o=>{state[o.id]={act:o.act,name:'',merge:''};byShort[o.sid]=o.id;imgsById[o.id]=o.imgs||[];});
let mergeTarget=null, lb={id:null,idx:0};

const $=s=>document.querySelector(s), app=$('#app');
function esc(s){return(s==null?'':(''+s)).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}
function labelOf(o){return o.lu||o.dl||o.lp||'?';}
function resolveTarget(raw){
 raw=(raw||'').trim(); if(!raw) return '';
 if(state[raw]) return raw;
 if(byShort[raw]) return byShort[raw];
 const ex=DATA.filter(o=>labelOf(o).toLowerCase()===raw.toLowerCase());
 if(ex.length===1) return ex[0].id;
 const pre=DATA.filter(o=>o.id.startsWith(raw)||o.sid.startsWith(raw));
 if(pre.length===1) return pre[0].id;
 return raw;
}
function tally(){
 let d=0,k=0,n=0,m=0;
 for(const id in state){const a=state[id].act;a=='delete'?d++:a=='keep'?k++:a=='name'?n++:m++;}
 $('#tally').innerHTML=`<span class="pill keep">keep ${k}</span><span class="pill name">name ${n}</span>`+
  `<span class="pill merge">merge ${m}</span><span class="pill del">delete ${d}</span>`;
 const t=mergeTarget?DATA.find(o=>o.id===mergeTarget):null;
 $('#mt').innerHTML=t?`Merge winner: <span class="tgt">${t.sid} — ${esc(labelOf(t))}</span> <button id="clrmt">clear</button>`
   :`<span class="k">No merge winner pinned — click ◎ on the object you want to keep.</span>`;
 if(t) $('#clrmt').onclick=()=>{mergeTarget=null;render();};
}
function passFilter(o){
 const q=$('#q').value.trim().toLowerCase();
 if($('#fUnnamed').checked&&o.lu) return false;
 if($('#fMov').checked&&o.mv!=='movable') return false;
 if(q){const h=(o.sid+' '+(o.lp||'')+' '+(o.dl||'')+' '+(o.lu||'')).toLowerCase();if(!h.includes(q))return false;}
 return true;
}
function card(o){
 const st=state[o.id], imgs=o.imgs||[];
 const tw = imgs.length
  ? `<div class="tw" data-id="${o.id}" data-idx="0">
       <img src="data:image/jpeg;base64,${imgs[0]}" data-zoom="1">
       ${imgs.length>1?`<div class="cyc"><button data-cyc="-1">‹</button>
         <span class="cnt">1/${imgs.length}</span><button data-cyc="1">›</button></div>`:''}
       <button class="pin" data-pin="1" title="set as merge winner">◎</button>
     </div>`
  : `<div class="tw"><div class="noimg">no crop</div>
       <button class="pin" data-pin="1" title="set as merge winner">◎</button></div>`;
 const on=a=>st.act===a?'on':''; const cl=a=>({keep:'k',delete:'d',name:'n',merge:'m'}[a]);
 let xtra='';
 if(st.act==='name') xtra=`<div class="xtra"><input placeholder="label_user…" value="${esc(st.name)}" data-name="1"></div>`;
 if(st.act==='merge'){
   const tgt=resolveTarget(st.merge); const to=tgt&&state[tgt]?DATA.find(x=>x.id===tgt):null;
   xtra=`<div class="xtra"><div class="to">${to?('→ '+to.sid+' — '+esc(labelOf(to))):'no winner — pin ◎ or type below'}</div>
     <input placeholder="winner short id or name…" value="${esc(st.merge)}" data-merge="1"></div>`;
 }
 return `<div class="card act-${st.act} ${mergeTarget===o.id?'istarget':''}" data-id="${o.id}">
  ${tw}
  <div class="meta">
   <div><span class="id">${o.sid}</span> <span class="mv ${o.mv}">${o.mv}</span></div>
   <div class="lbl">${esc(labelOf(o))}${o.lu?' <span class="k">(named)</span>':''}</div>
   <div class="k">vb ${o.vb} · hits ${o.hits} · lth ${o.lth} · [${o.xyz.join(', ')}]</div>
  </div>
  <div class="acts">
   <button class="${cl('keep')} ${on('keep')}"   data-a="keep">keep</button>
   <button class="${cl('name')} ${on('name')}"   data-a="name">name</button>
   <button class="${cl('merge')} ${on('merge')}" data-a="merge">merge</button>
   <button class="${cl('delete')} ${on('delete')}" data-a="delete">del</button>
  </div>${xtra}</div>`;
}
function grpKey(o){return o.lu?('★ '+o.lu):(o.dl||o.lp||'?');}
function render(){
 const shown=DATA.filter(passFilter); let html='';
 if($('#fGroup').checked){
  const g={}; shown.forEach(o=>{(g[grpKey(o)]=g[grpKey(o)]||[]).push(o);});
  Object.keys(g).sort((a,b)=>g[b].length-g[a].length).forEach(k=>{
   html+=`<div class="grp"><div class="grph"><h2>${esc(k)}</h2><span class="c">${g[k].length}</span>`+
     `<button data-bulk="delete" data-grp="${esc(k)}">delete all</button>`+
     `<button data-bulk="keep" data-grp="${esc(k)}">keep all</button></div>`+
     `<div class="grid">${g[k].map(card).join('')}</div></div>`;
  });
 } else html=`<div class="grp"><div class="grid">${shown.map(card).join('')}</div></div>`;
 app.innerHTML=html; tally();
}
function grpItems(k){return DATA.filter(o=>grpKey(o)===k&&passFilter(o));}

app.addEventListener('click',e=>{
 const t=e.target;
 if(t.dataset.zoom){const w=t.closest('.tw');lb={id:w.dataset.id,idx:+w.dataset.idx||0};openLB();return;}
 if(t.dataset.cyc){const w=t.closest('.tw');const id=w.dataset.id;const imgs=imgsById[id];
   let i=(+w.dataset.idx+ +t.dataset.cyc+imgs.length)%imgs.length;w.dataset.idx=i;
   w.querySelector('img').src='data:image/jpeg;base64,'+imgs[i];
   w.querySelector('.cnt').textContent=(i+1)+'/'+imgs.length;return;}
 if(t.dataset.pin){mergeTarget=t.closest('.card').dataset.id;render();return;}
 if(t.dataset.a){const id=t.closest('.card').dataset.id;state[id].act=t.dataset.a;
   if(t.dataset.a==='merge'&&!state[id].merge&&mergeTarget)state[id].merge=mergeTarget;render();return;}
 if(t.dataset.bulk){grpItems(t.dataset.grp).forEach(o=>state[o.id].act=t.dataset.bulk);render();return;}
});
app.addEventListener('input',e=>{const c=e.target.closest('.card');if(!c)return;const id=c.dataset.id;
 if(e.target.dataset.name!=null)state[id].name=e.target.value;
 if(e.target.dataset.merge!=null)state[id].merge=e.target.value;});
['q','fUnnamed','fMov','fGroup'].forEach(i=>$('#'+i).addEventListener('input',render));

function openLB(){const imgs=imgsById[lb.id]||[];if(!imgs.length)return;
 $('#lb').style.display='flex';paintLB();}
function paintLB(){const imgs=imgsById[lb.id]||[];lb.idx=(lb.idx+imgs.length)%imgs.length;
 $('#lb img').src='data:image/jpeg;base64,'+imgs[lb.idx];
 $('#lb .cnt').textContent=(lb.idx+1)+'/'+imgs.length;}
$('#lb').addEventListener('click',e=>{const v=e.target.dataset.lb;
 if(v==='x'||e.target.id==='lb'){$('#lb').style.display='none';}
 else if(v){lb.idx+=+v;paintLB();}});
document.addEventListener('keydown',e=>{if($('#lb').style.display!=='flex')return;
 if(e.key==='Escape')$('#lb').style.display='none';
 if(e.key==='ArrowLeft'){lb.idx--;paintLB();} if(e.key==='ArrowRight'){lb.idx++;paintLB();}});

function decisions(){
 const out={generated_utc:Date.now()/1000,source:'rtsm-review',decisions:{}};
 for(const id in state){const s=state[id],d={action:s.act};
  if(s.act==='name')d.name=(s.name||'').trim();
  if(s.act==='merge'){d.merge_into=resolveTarget(s.merge);d.merge_into_raw=(s.merge||'').trim();}
  out.decisions[id]=d;}
 return out;
}
$('#exp').addEventListener('click',()=>{const j=JSON.stringify(decisions(),null,1);
 const b=new Blob([j],{type:'application/json'});const a=document.createElement('a');
 a.href=URL.createObjectURL(b);a.download='rtsm_decisions.json';a.click();
 $('#dlgtx').value=j;$('#dlg').showModal();try{localStorage.setItem('rtsm_decisions',j);}catch(_){}});
$('#imp').addEventListener('click',()=>{$('#dlgtx').value='';$('#dlg').showModal();});
$('#dlgclose').addEventListener('click',()=>$('#dlg').close());
$('#dlgload').addEventListener('click',()=>{try{const j=JSON.parse($('#dlgtx').value);
 const dec=j.decisions||j;for(const id in dec){if(state[id]){state[id].act=dec[id].action||'keep';
  state[id].name=dec[id].name||'';state[id].merge=dec[id].merge_into_raw||dec[id].merge_into||'';}}
 $('#dlg').close();render();}catch(err){alert('Bad JSON: '+err);}});
try{const s=localStorage.getItem('rtsm_decisions');if(s)$('#dlgtx').value=s;}catch(_){}
render();
</script></body></html>"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:8002")
    ap.add_argument("--crops", default="/mnt/rtsm-data/rtsm-workdir/crops")
    ap.add_argument("--out", default="review.html")
    ap.add_argument("--max-crops", type=int, default=8)
    ap.add_argument("--thumb", type=int, default=180)
    ap.add_argument("--quality", type=int, default=62)
    args = ap.parse_args()

    print(f"[*] fetching object metadata from {args.base} ...", file=sys.stderr)
    objs = fetch_all(args.base)
    print(f"[*] {len(objs)} objects; loading crops from {args.crops} ...", file=sys.stderr)
    if not os.path.isdir(args.crops):
        print(f"[!] crops dir not found: {args.crops} "
              f"(falling back to the single API snapshot per object)", file=sys.stderr)

    rows = build_rows(objs, args.crops, args.max_crops, args.thumb, args.quality)
    named = sum(1 for r in rows if r["lu"])
    dele = sum(1 for r in rows if r["act"] == "delete")
    withimg = sum(1 for r in rows if r["imgs"])
    print(f"[*] named={named}  default-delete={dele}  with-crops={withimg}/{len(rows)}",
          file=sys.stderr)

    html = HTML.replace("/*__DATA__*/[]", json.dumps(rows, separators=(",", ":")))
    with open(args.out, "w") as f:
        f.write(html)
    print(f"[*] wrote {args.out}  ({len(html)/1e6:.1f} MB) -- open it in a browser",
          file=sys.stderr)

if __name__ == "__main__":
    main()
