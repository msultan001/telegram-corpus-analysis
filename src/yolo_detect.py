import os
import csv
import json
import argparse
from datetime import datetime
import torch
from pathlib import Path

# Minimal YOLO runner using ultralytics/yolov5 or yolov8 if installed
# This script supports CPU fallback and produces a CSV sidecar of detections.

IMAGE_DIR = "data/raw/images"
OUTPUT_DIR = "data/derived/image_detections"

os.makedirs(OUTPUT_DIR, exist_ok=True)

CLASS_MAP = {
    # map model class names or indices to our categories
    'product': 'product_display',
    'packaging': 'product_display',
    'label': 'promotional',
    'logo': 'promotional',
}


def run_inference(weights: str, device: str = 'cpu', conf_thresh: float = 0.25):
    try:
        from ultralytics import YOLO
        model = YOLO(weights)
    except Exception:
        try:
            # fallback to torch.hub yolov5
            model = torch.hub.load('ultralytics/yolov5', 'custom', path=weights, force_reload=False)
        except Exception as e:
            raise RuntimeError('No YOLO model available')

    results_rows = []
    for channel_dir in Path(IMAGE_DIR).iterdir():
        if not channel_dir.is_dir():
            continue
        for img in channel_dir.iterdir():
            if img.suffix.lower() not in ['.jpg', '.jpeg', '.png']:
                continue
            try:
                res = model(str(img))
                # ultralytics returns a special results object; normalize
                boxes = []
                if hasattr(res, 'boxes'):
                    boxes = res.boxes
                elif isinstance(res, list) and len(res) > 0 and hasattr(res[0], 'boxes'):
                    boxes = res[0].boxes

                for b in boxes:
                    # attempt to extract label and confidence
                    try:
                        if hasattr(b, 'cls'):
                            cls = int(b.cls)
                            label = model.names[cls] if hasattr(model, 'names') else str(cls)
                        else:
                            label = str(b.label) if hasattr(b, 'label') else 'unknown'
                    except Exception:
                        label = 'unknown'
                    score = float(b.conf) if hasattr(b, 'conf') else float(b[4])

                    product_label = CLASS_MAP.get(label, 'other')
                    detection_ts = datetime.utcnow().isoformat()
                    results_rows.append({
                        'channel_id': channel_dir.name,
                        'image_path': str(img),
                        'product_label': product_label,
                        'original_label': label,
                        'score': score,
                        'detection_timestamp': detection_ts
                    })
            except Exception as e:
                print(f"Failed inference on {img}: {e}")

    csv_path = os.path.join(OUTPUT_DIR, f'detections_{datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")}.csv')
    with open(csv_path, 'w', newline='', encoding='utf-8') as cf:
        writer = csv.DictWriter(cf, fieldnames=['channel_id','image_path','product_label','original_label','score','detection_timestamp'])
        writer.writeheader()
        for r in results_rows:
            writer.writerow(r)

    print(f"Wrote {len(results_rows)} detections to {csv_path}")
    return csv_path


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', required=True)
    parser.add_argument('--device', default='cpu')
    parser.add_argument('--conf', type=float, default=0.25)
    args = parser.parse_args()
    run_inference(args.weights, args.device, args.conf)
