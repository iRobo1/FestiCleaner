"""
Festiclean trash detector — single-cell Colab training script.

Paste this entire file into ONE Colab cell (T4 GPU runtime). Before running
the cell, upload ONE thing into the Colab working directory:

    • data.zip — Edge Impulse object-detection export (default settings).
                  Expected layout inside the zip:
                      training/  *.jpg + bounding_boxes.labels
                      testing/   *.jpg + bounding_boxes.labels   (optional)

The script will:
  1. install ultralytics + onnx + tensorflow (~30 s)
  2. unzip data.zip and convert EI format → YOLO format
  3. auto-generate data.yaml from the EI class list
  4. train YOLOv8n with our augmentation config (~15-35 min on T4)
  5. validate and print mAP / per-class precision & recall
  6. export ONNX, TorchScript, TF SavedModel, TFLite FP32, TFLite INT8
  7. zip everything to festiclean_weights.zip and trigger a browser download

If `testing/` is missing in the EI export, the script does an 80/20
random split of `training/` so val metrics still mean something.
"""

import json
import random
import shutil
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
pip_install("ultralytics", "onnx", "onnxruntime", "tensorflow", "pillow")


# ── 1. Unpack the dataset ──────────────────────────────────────────────────
ROOT = Path.cwd()
EI_DIR = ROOT / "ei_raw"        # where the EI export lands
YOLO_DIR = ROOT / "data"        # YOLO-format dataset (built from EI)
DATA_ZIP = ROOT / "data.zip"
DATA_YAML = ROOT / "data.yaml"  # auto-generated below

assert DATA_ZIP.exists(), "data.zip missing — upload the Edge Impulse export"

if not EI_DIR.exists():
    print(f"[setup] unzipping {DATA_ZIP.name} → {EI_DIR}/")
    with zipfile.ZipFile(DATA_ZIP) as zf:
        zf.extractall(EI_DIR)


# ── 1b. Convert Edge Impulse → YOLO ────────────────────────────────────────
from PIL import Image  # noqa: E402


def find_ei_split(name: str) -> Path | None:
    """EI export sometimes nests one level deep (e.g. ei_raw/<project>/training)."""
    for p in EI_DIR.rglob(name):
        if p.is_dir() and (p / "bounding_boxes.labels").exists():
            return p
    return None


def parse_ei_labels(labels_file: Path) -> list[tuple[str, list[dict]]]:
    """Return list of (image_filename, boxes). Handles both EI label schemas."""
    data = json.loads(labels_file.read_text())
    if isinstance(data.get("boundingBoxes"), dict):
        # schema: {"boundingBoxes": {"img.jpg": [box, ...]}}
        return list(data["boundingBoxes"].items())
    if "files" in data:
        # schema: {"files": [{"path": "img.jpg", "boundingBoxes": [box, ...]}]}
        return [(f["path"], f.get("boundingBoxes", [])) for f in data["files"]]
    raise ValueError(f"unknown EI label schema in {labels_file}")


def write_yolo_split(
    pairs: list[tuple[Path, list[dict]]],
    yolo_split: str,
    classes: dict[str, int],
) -> None:
    img_out = YOLO_DIR / "images" / yolo_split
    lbl_out = YOLO_DIR / "labels" / yolo_split
    img_out.mkdir(parents=True, exist_ok=True)
    lbl_out.mkdir(parents=True, exist_ok=True)

    for src_img, boxes in pairs:
        if not src_img.exists():
            continue
        shutil.copy2(src_img, img_out / src_img.name)
        with Image.open(src_img) as im:
            W, H = im.size

        lbl_path = lbl_out / (src_img.stem + ".txt")
        with lbl_path.open("w") as f:
            for b in boxes:
                if b["label"] not in classes:
                    classes[b["label"]] = len(classes)
                cls = classes[b["label"]]
                cx = (b["x"] + b["width"] / 2) / W
                cy = (b["y"] + b["height"] / 2) / H
                bw = b["width"] / W
                bh = b["height"] / H
                f.write(f"{cls} {cx:.6f} {cy:.6f} {bw:.6f} {bh:.6f}\n")


print("[convert] Edge Impulse → YOLO")
if YOLO_DIR.exists():
    shutil.rmtree(YOLO_DIR)

train_dir = find_ei_split("training")
test_dir = find_ei_split("testing")
assert train_dir is not None, "no training/ folder with bounding_boxes.labels found"

train_entries = parse_ei_labels(train_dir / "bounding_boxes.labels")
train_pairs = [(train_dir / name, boxes) for name, boxes in train_entries]

if test_dir is not None:
    test_entries = parse_ei_labels(test_dir / "bounding_boxes.labels")
    val_pairs = [(test_dir / name, boxes) for name, boxes in test_entries]
    print(f"[convert] using EI testing/ split: {len(val_pairs)} val images")
else:
    print("[convert] no testing/ in EI export — doing 80/20 split of training/")
    random.seed(42)
    random.shuffle(train_pairs)
    cut = int(len(train_pairs) * 0.8)
    train_pairs, val_pairs = train_pairs[:cut], train_pairs[cut:]

CLASSES: dict[str, int] = {}
write_yolo_split(train_pairs, "train", CLASSES)
write_yolo_split(val_pairs, "val", CLASSES)

class_names = [n for n, _ in sorted(CLASSES.items(), key=lambda x: x[1])]
print(f"[convert] classes ({len(class_names)}): {class_names}")
print(f"[convert] train={len(train_pairs)}  val={len(val_pairs)}")


# ── 1c. Generate data.yaml ─────────────────────────────────────────────────
DATA_YAML.write_text(
    f"path: {YOLO_DIR}\n"
    f"train: images/train\n"
    f"val: images/val\n"
    f"nc: {len(class_names)}\n"
    f"names: {class_names}\n"
)
print(f"[convert] wrote {DATA_YAML}")


# ── 2. Configuration ───────────────────────────────────────────────────────
MODEL = "yolov8n.pt"
EPOCHS = 200
PATIENCE = 30
IMGSZ = 416
BATCH = 16
SEED = 42
RUN_NAME = "festiclean"
PROJECT = str(ROOT / "runs" / "detect")

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
from ultralytics import YOLO  # noqa: E402

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
weights_dir = Path(PROJECT) / RUN_NAME / "weights"
print(f"\n[export] weights dir: {weights_dir}")

EXPORT_TARGETS = [
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