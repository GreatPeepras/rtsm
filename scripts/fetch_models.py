"""
Fetch all RTSM models into model_store/.

Usage:
    python scripts/fetch_models.py              # fetch all
    python scripts/fetch_models.py --only clip   # fetch only clip
    python scripts/fetch_models.py --only yolo   # fetch only yolo
    python scripts/fetch_models.py --only fastsam # fetch only fastsam

Directory layout:
    model_store/
      clip/ViT-B-32-openai/model.pt
      fastsam/FastSAM-x.pt
      yolo/yoloe-26s-seg.pt
      yolo/yoloe-26s-seg-pf.pt
"""
import argparse
import os
import sys
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_STORE = os.path.join(ROOT, "model_store")


def fetch_clip():
    """Fetch CLIP ViT-B-32 (openai) into model_store/clip/."""
    import torch
    import open_clip

    out = os.path.join(MODEL_STORE, "clip", "ViT-B-32-openai")
    ckpt = os.path.join(out, "model.pt")
    if os.path.isfile(ckpt):
        print(f"[clip] Already present: {ckpt}")
        return

    os.makedirs(out, exist_ok=True)
    print("[clip] Downloading ViT-B-32 (openai) ...")
    model, _, _ = open_clip.create_model_and_transforms(
        "ViT-B-32", pretrained="openai", device="cpu"
    )
    torch.save(model.state_dict(), ckpt)
    print(f"[clip] Saved: {ckpt}")


def fetch_fastsam():
    """Fetch FastSAM-x into model_store/fastsam/."""
    out = os.path.join(MODEL_STORE, "fastsam")
    ckpt = os.path.join(out, "FastSAM-x.pt")
    if os.path.isfile(ckpt):
        print(f"[fastsam] Already present: {ckpt}")
        return

    os.makedirs(out, exist_ok=True)
    print("[fastsam] Downloading FastSAM-x via ultralytics ...")
    from ultralytics import FastSAM
    # ultralytics auto-downloads to CWD or cache; load then copy
    model = FastSAM("FastSAM-x.pt")
    src = model.ckpt_path if hasattr(model, "ckpt_path") else "FastSAM-x.pt"
    if os.path.isfile(src) and os.path.abspath(src) != os.path.abspath(ckpt):
        shutil.move(src, ckpt)
    print(f"[fastsam] Saved: {ckpt}")


def fetch_yolo():
    """Fetch YOLOE-26s-seg and YOLOE-26s-seg-pf into model_store/yolo/."""
    out = os.path.join(MODEL_STORE, "yolo")
    os.makedirs(out, exist_ok=True)

    from ultralytics import YOLOE

    variants = [
        "yoloe-26s-seg.pt",       # prompted (text/visual vocab)
        "yoloe-26s-seg-pf.pt",    # prompt-free (1200+ built-in LVIS categories)
    ]
    for variant in variants:
        ckpt = os.path.join(out, variant)
        if os.path.isfile(ckpt):
            print(f"[yolo] Already present: {ckpt}")
            continue

        print(f"[yolo] Downloading {variant} via ultralytics ...")
        model = YOLOE(variant)
        src = model.ckpt_path if hasattr(model, "ckpt_path") else variant
        if os.path.isfile(src) and os.path.abspath(src) != os.path.abspath(ckpt):
            shutil.move(src, ckpt)
        print(f"[yolo] Saved: {ckpt}")


FETCHERS = {
    "clip": fetch_clip,
    "fastsam": fetch_fastsam,
    "yolo": fetch_yolo,
}


def main():
    ap = argparse.ArgumentParser(description="Fetch RTSM models into model_store/")
    ap.add_argument("--only", choices=list(FETCHERS.keys()), help="Fetch only this model")
    args = ap.parse_args()

    targets = [args.only] if args.only else list(FETCHERS.keys())
    for name in targets:
        try:
            FETCHERS[name]()
        except Exception as e:
            print(f"[{name}] ERROR: {e}", file=sys.stderr)
            raise


if __name__ == "__main__":
    main()
