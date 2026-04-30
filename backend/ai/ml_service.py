import os
from ultralytics import YOLO
import json
import numpy as np
from tensorflow.keras.preprocessing import image as keras_image
from tensorflow import keras
from tensorflow import keras


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

# Classifier model yolu
CLASSIFIER_MODEL_PATH = os.path.join(BASE_DIR, "models_ai", "plant_classifier", "en_iyi_model.keras")
CLASS_INDICES_PATH = os.path.join(BASE_DIR, "models_ai", "plant_classifier", "class_indices.json")

# Model ve class map yükle
CONFIG_PATH = os.path.join(BASE_DIR, "models_ai", "plant_classifier", "en_iyi_model.keras", "config.json")
WEIGHTS_PATH = os.path.join(BASE_DIR, "models_ai", "plant_classifier", "en_iyi_model.keras", "model.weights.h5")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config_json = f.read()

classifier_model = keras.models.model_from_json(config_json)
classifier_model.load_weights(WEIGHTS_PATH)
print("Classifier model yüklendi:", CLASSIFIER_MODEL_PATH)

with open(CLASS_INDICES_PATH, "r", encoding="utf-8") as f:
    class_indices = json.load(f)

# {"ClassName": 0, ...} → {0: "ClassName", ...}
index_to_class = {v: k for k, v in class_indices.items()}


def predict_plant_species(image_path, top_k=3):
    img = keras_image.load_img(image_path, target_size=(224, 224))
    img_array = keras_image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0

    predictions = classifier_model.predict(img_array)
    probs = predictions[0]

    top_indices = np.argsort(probs)[::-1][:top_k]

    top_results = [
        {
            "species": index_to_class.get(int(i), "unknown"),
            "confidence": round(float(probs[i]), 4)
        }
        for i in top_indices
    ]

    return {
        "predicted_species": top_results[0]["species"],
        "confidence": top_results[0]["confidence"],
        "top_predictions": top_results,
        "model_version": "en_iyi_model.keras"
    }