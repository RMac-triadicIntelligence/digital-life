"""Runs the century (V2_FULL, 36,500 days = 292,000 ticks) on October's seeds in order, two at a time.
PREREG: seeds are started in order until a 35-minute window closes; those in flight finish; all that finish are reported."""
import hashlib, json, multiprocessing as mp, sys, time
from pathlib import Path
import commons_century as CC

HERE = Path(__file__).resolve().parent
T = 36500 * CC.TICKS_PER_DAY
WINDOW_S = 35 * 60

def worker(next_seed, lock, t0, outdir):
    while True:
        with lock:
            if time.time() - t0 > WINDOW_S or next_seed.value >= 20:
                return
            seed = next_seed.value; next_seed.value += 1
        s0 = time.time()
        res, packed = CC.run("V2_FULL", seed, T, stop_when_extinct=True)
        packed["october_style_summary"] = res
        txt = CC.dumps(packed)
        (outdir / f"seed_{seed:02d}.json").write_text(txt)
        with lock:
            with open(outdir / "log.txt", "a") as f:
                f.write(f"seed {seed} sha256 {hashlib.sha256(txt.encode()).hexdigest()} wall_s {time.time()-s0:.0f} pop_final {res['pop_final']}\n")

if __name__ == "__main__":
    outdir = HERE / (sys.argv[1] if len(sys.argv) > 1 else "century"); outdir.mkdir(exist_ok=True)
    t0 = time.time(); nxt = mp.Value("i", 0); lock = mp.Lock()
    ps = [mp.Process(target=worker, args=(nxt, lock, t0, outdir)) for _ in range(2)]
    [p.start() for p in ps]; [p.join() for p in ps]
    (outdir / "DONE").write_text(f"started_seeds {nxt.value} wall_s {time.time()-t0:.0f}\n")
