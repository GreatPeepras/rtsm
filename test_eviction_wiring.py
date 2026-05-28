"""Behavioral test of the ACTUAL wired _maybe_evict_stale method.

Can't import pipeline.py here (torch/heavy deps), so we ast-extract the real
method source from the patched file and exec it with stubbed time/logger.
This tests the deployed text, not a copy.
"""
import ast, types

PIPE = "/tmp/work/pipe_patched.py"
src = open(PIPE).read()
tree = ast.parse(src)
fn = next(n for n in ast.walk(tree)
          if isinstance(n, ast.FunctionDef) and n.name == "_maybe_evict_stale")
method_src = ast.get_source_segment(src, fn)

# Fakes for module globals the method closes over.
class FakeClock:
    def __init__(self): self.t = 0.0
    def monotonic(self): return self.t
clock = FakeClock()
logs = []
class FakeLogger:
    def info(self, m): logs.append(("info", m))
    def warning(self, m): logs.append(("warning", m))
ns = {"time": clock, "logger": FakeLogger()}
exec(method_src, ns)
method = ns["_maybe_evict_stale"]

class FakeWM:
    def __init__(self, result=None, raises=False):
        self.calls = 0; self._result = result or {"evicted": [], "by_class": {}, "dry_run": False}; self._raises = raises
    def evict_stale(self):
        self.calls += 1
        if self._raises: raise RuntimeError("boom")
        return self._result

class Pipe:  # minimal stand-in for self
    def __init__(self, wm, cfg):
        self.working_mem = wm; self.cfg = cfg; self._last_evict_ts = 0.0
    _maybe_evict_stale = method

results = []
def check(name, cond, detail=""):
    results.append(cond); print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  -- {detail}" if detail else "")); assert cond, detail

print("=== test_eviction_wiring.py ===\n")

print("[1] throttle: sweeps once, skips within period, sweeps after period")
wm = FakeWM(result={"evicted": [{"oid": "x"}], "by_class": {"movable": 1}, "dry_run": False})
p = Pipe(wm, {"eviction": {"period_s": 100.0}})
clock.t = 0.0;   p._maybe_evict_stale()          # first call at t=0 -> sweeps (0 - 0 not < 100? 0<100 True -> SKIP!)
# NOTE: with _last_evict_ts=0 and t=0, (0-0)=0 < 100 -> skip. Advance past period for first real sweep.
clock.t = 101.0; p._maybe_evict_stale()          # now sweeps
first = wm.calls
clock.t = 150.0; p._maybe_evict_stale()          # within period -> skip
second = wm.calls
clock.t = 260.0; p._maybe_evict_stale()          # past period -> sweep
third = wm.calls
check("1a swept after period elapsed", first == 1, f"calls={first}")
check("1b skipped within period", second == 1, f"calls={second}")
check("1c swept again after next period", third == 2, f"calls={third}")
check("1d eviction logged when objects evicted", any("evicted 1 stale" in m for _,m in logs))

print("\n[2] frozen/serve WM (no evict_stale) -> guarded no-op")
class FrozenWM:  # mimics frozen_wm: no evict_stale attr
    pass
p2 = Pipe(FrozenWM(), {"eviction": {"period_s": 1.0}})
clock.t = 9999.0
p2._maybe_evict_stale()  # must not raise
check("2a no crash on frozen WM", True)

print("\n[3] working_mem is None -> no-op")
p3 = Pipe(None, {})
p3._maybe_evict_stale()
check("3a no crash when WM is None", True)

print("\n[4] exception in evict_stale is caught and warned, not raised")
wm4 = FakeWM(raises=True)
p4 = Pipe(wm4, {"eviction": {"period_s": 1.0}})
clock.t = 100000.0
p4._maybe_evict_stale()
check("4a swallowed exception", any(lvl == "warning" for lvl,_ in logs))

print("\n[5] default period_s = 300 when cfg omits it")
wm5 = FakeWM(result={"evicted": [{"oid":"y"}], "by_class":{}, "dry_run": False})
p5 = Pipe(wm5, {})  # no eviction cfg at all
p5._last_evict_ts = 0.0
clock.t = 299.0; p5._maybe_evict_stale(); a = wm5.calls   # < 300 -> skip
clock.t = 301.0; p5._maybe_evict_stale(); b = wm5.calls   # > 300 -> sweep
check("5a default 300s throttle honored", a == 0 and b == 1, f"a={a} b={b}")

print(f"\n=== {sum(results)}/{len(results)} checks passed ===")
