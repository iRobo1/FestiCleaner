"""
Festiclean trash detector — single-cell Colab training script.

Paste this entire file into ONE Colab cell (T4 GPU runtime). Before running
the cell, upload these two things into the Colab working directory:

    • data.zip   — your dataset, packed with the layout described in
                    training/README.md (images/{train,val} + labels/{train,val})
    • data.yaml  — class names + train/val paths (already in this folder)

The script will:
  1. install ultralytics + onnx + tensorflow (~30 s on a fresh Colab)
  2. unzip data.zip (skipped if already done)
  3. train YOLOv8n with our augmentation config (~15-35 min on T4)
  4. validate and print mAP / per-class precision & recall
  5. export the trained weights in EVERY format Arduino/Qualcomm might
     plausibly accept — ONNX, TorchScript, TF SavedModel, TFLite FP32,
     TFLite INT8 — so you can try whichever one the Bricks brick wants
  6. zip them into festiclean_weights.zip and trigger a browser download

Total wall-clock: about 30–60 minutes end-to-end. Don't kill the cell when
training "finishes" — TFLite INT8 PTQ takes another 5–10 min after that.
"""

import subprocess
import sys
import zipfile
from pathlib import Path


# ── 0. Install dependencies ────────────────────────────────────────────────
def pip_install(*pkgs: str) -> None:
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", *pkgs],
        check=True,
    )


print("[setup] installing ultralytics + onnx + tensorflow …")
pip_install("ultralytics", "onnx", "onnxruntime", "tensorflow")


# ── 1. Unpack the dataset ──────────────────────────────────────────────────
ROOT = Path.cwd()
DATA_DIR = ROOT / "data"
DATA_ZIP = ROOT / "data.zip"
DATA_YAML = ROOT / "data.yaml"

if DATA_ZIP.exists() and not DATA_DIR.exists():
    print(f"[setup] unzipping {DATA_ZIP.name} → {DATA_DIR}/")
    with zipfile.ZipFile(DATA_ZIP) as zf:
        zf.extractall(DATA_DIR)

assert DATA_YAML.exists(), (
    "data.yaml missing — upload it into the Colab working dir before running"
)
assert DATA_DIR.exists(), (
    "data/ missing — upload data.zip first (or extract it into ./data/)"
)


# ── 2. Configuration ───────────────────────────────────────────────────────
MODEL = "yolov8n.pt"  # COCO-pretrained; transfer-learns `bottle` for free
EPOCHS = 200           # capped by PATIENCE
PATIENCE = 30          # plateau tolerance on val mAP
IMGSZ = 416            # matches the Uno Q deploy target
BATCH = 16             # comfortable on a T4 (16 GB)
SEED = 42
RUN_NAME = "festiclean"
PROJECT = str(ROOT / "runs" / "detect")

# Aggressive augmentation — only ~50 imgs per class.
# `flipud` is OFF: bottles, walls and chair legs all have a real "up".
AUGMENT = dict(
    mosaic=1.0,
    mixup=0.15,
    copy_paste=0.3,
    hsv_h=0.015,
    hsv_s=0.7,
    hsv_v=0.4,
    degrees=10,
    translate=0.1,
    scale=0.5,
    shear=2,
    perspective=0.0005,
    flipud=0.0,
    fliplr=0.5,
)


# ── 3. Train ────────────────────────────────────────────────────────────────
from ultralytics import YOLO  # noqa: E402  (imported after install)

print(f"[train] {MODEL}  →  {RUN_NAME}")
print(f"[train] imgsz={IMGSZ}  batch={BATCH}  epochs≤{EPOCHS}  patience={PATIENCE}")

model = YOLO(MODEL)
model.train(
    data=str(DATA_YAML),
    epochs=EPOCHS,
    patience=PATIENCE,
    imgsz=IMGSZ,
    batch=BATCH,
    seed=SEED,
    name=RUN_NAME,
    project=PROJECT,
    cos_lr=True,
    optimizer="SGD",
    **AUGMENT,
)


# ── 4. Validate ────────────────────────────────────────────────────────────
metrics = model.val()
print(f"\n[val] mAP50-95 = {metrics.box.map:.4f}")
print(f"[val] mAP50    = {metrics.box.map50:.4f}")
print(f"[val] precision per class: {metrics.box.p}")
print(f"[val] recall    per class: {metrics.box.r}")


# ── 5. Export every plausible format ───────────────────────────────────────
# We don't know which the UNO Q brick accepts, so we ship them all and let
# the deployment step pick. Each is ~3-15 MB — total bundle stays small.
weights_dir = Path(PROJECT) / RUN_NAME / "weights"
print(f"\n[export] weights dir: {weights_dir}")

EXPORT_TARGETS = [
    # (format, extra kwargs, friendly description)
    ("onnx",        dict(opset=12, simplify=True, dynamic=False),     "ONNX (opset 12, simplified)"),
    ("torchscript", dict(),                                           "TorchScript"),
    ("saved_model", dict(),                                           "TensorFlow SavedModel"),
    ("tflite",      dict(int8=False),                                 "TFLite FP32"),
    ("tflite",      dict(int8=True, data=str(DATA_YAML)),             "TFLite INT8 (PTQ-calibrated)"),
]

for fmt, kwargs, desc in EXPORT_TARGETS:
    print(f"[export] → {desc}")
    try:
        model.export(format=fmt, imgsz=IMGSZ, **kwargs)
    except Exception as e:
        print(f"  ⚠ {desc} export failed: {e}")


# ── 6. Bundle everything for one-click download ────────────────────────────
print("\n[bundle] zipping every weight artifact…")
out_zip = ROOT / f"{RUN_NAME}_weights.zip"
with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as zf:
    for p in weights_dir.rglob("*"):
        if p.is_file():
            zf.write(p, arcname=str(p.relative_to(weights_dir)))

print(f"[bundle] wrote {out_zip.name}. Contents:")
for name in zipfile.ZipFile(out_zip).namelist():
    print(f"  • {name}")


# ── 7. Trigger the browser download (Colab only — silent elsewhere) ────────
try:
    from google.colab import files  # type: ignore

    print(f"\n[download] auto-downloading {out_zip.name} …")
    files.download(str(out_zip))
except ImportError:
    print(f"\n[download] not in Colab; grab {out_zip} from the file panel.")
