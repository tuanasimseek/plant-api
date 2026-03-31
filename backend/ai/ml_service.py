import os
from ultralytics import YOLO

# MODEL YOLU
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models_ai", "best.pt")

# MODEL YÜKLE
model = YOLO(MODEL_PATH)

print("Model yüklendi:", MODEL_PATH)
print("Model class names:", model.names)


def predict_plant_height(image_path, reference_object_cm=9):
    results = model(image_path)

    if not results or len(results) == 0:
        raise ValueError("Model tahmin üretemedi.")

    r = results[0]

    if r.boxes is None or len(r.boxes) == 0:
        raise ValueError("Görüntüde nesne bulunamadı.")

    names = model.names

    plant_box = None
    pot_box = None
    plant_conf = 0.0
    pot_conf = 0.0

    for box in r.boxes:
        cls_id = int(box.cls[0].item())
        conf = float(box.conf[0].item())
        xyxy = box.xyxy[0].tolist()

        class_name = names.get(cls_id, str(cls_id))

        if class_name == "plant" and conf > plant_conf:
            plant_box = xyxy
            plant_conf = conf

        elif class_name == "pot" and conf > pot_conf:
            pot_box = xyxy
            pot_conf = conf

    if plant_box is None:
        raise ValueError("Bitki bulunamadı")

    if pot_box is None:
        raise ValueError("Saksı bulunamadı")

    plant_height_px = plant_box[3] - plant_box[1]
    pot_height_px = pot_box[3] - pot_box[1]

    if pot_height_px <= 0:
        raise ValueError("Saksı yüksekliği hatalı")

    estimated_height_cm = (plant_height_px / pot_height_px) * float(reference_object_cm)
    confidence = min(plant_conf, pot_conf)

    return {
        "estimated_height_cm": round(estimated_height_cm, 2),
        "confidence": round(confidence, 4),
        "model_version": "best.pt"
    }