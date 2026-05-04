import os
import pickle
import json
import numpy as np
from ultralytics import YOLO
from tensorflow.keras.preprocessing import image as keras_image
from tensorflow import keras
import joblib


# =======================
# BASE DIR
# =======================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# =======================
# BOY TESPİTİ MODELİ (YOLO)
# =======================
MODEL_PATH = os.path.join(BASE_DIR, "models_ai", "best.pt")
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


# =======================
# TÜR TESPİTİ MODELİ (Keras)
# =======================
CONFIG_PATH = os.path.join(BASE_DIR, "models_ai", "plant_classifier", "en_iyi_model.keras", "config.json")
WEIGHTS_PATH = os.path.join(BASE_DIR, "models_ai", "plant_classifier", "en_iyi_model.keras", "model.weights.h5")
CLASS_INDICES_PATH = os.path.join(BASE_DIR, "models_ai", "plant_classifier", "class_indices.json")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config_json = f.read()

classifier_model = keras.models.model_from_json(config_json)
classifier_model.load_weights(WEIGHTS_PATH)
print("Classifier model yüklendi.")

with open(CLASS_INDICES_PATH, "r", encoding="utf-8") as f:
    class_indices = json.load(f)

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


# =======================
# SAĞLIK TESPİTİ MODELİ (Keras)
# =======================
HEALTH_MODEL_PATH = os.path.join(BASE_DIR, "models_ai", "bitki_saglik_modeli.h5")
HEALTH_CLASS_INDICES_PATH = os.path.join(BASE_DIR, "models_ai", "health_class_indices.json")

health_model = keras.models.load_model(HEALTH_MODEL_PATH)
print("Health model yüklendi.")

with open(HEALTH_CLASS_INDICES_PATH, "r", encoding="utf-8") as f:
    health_class_indices = json.load(f)

health_index_to_class = {v: k for k, v in health_class_indices.items()}

HEALTH_CLASS_MAP = {
    "saglikli": "healthy",
    "sararma": "slightly_stressed",
    "erken_yaniklik": "slightly_stressed",
    "geç_yaniklik": "unhealthy",
    "bakteriyel_leke": "unhealthy",
    "yaprak_kufu": "unhealthy",
    "yaprak_lekesi": "slightly_stressed",
}

DISEASE_CLASSES = {
    "bakteriyel_leke", "erken_yaniklik", "geç_yaniklik",
    "yaprak_kufu", "yaprak_lekesi", "sararma"
}


def predict_plant_health(image_path, top_k=3):
    img = keras_image.load_img(image_path, target_size=(224, 224))
    img_array = keras_image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0

    predictions = health_model.predict(img_array)
    probs = predictions[0]
    top_indices = np.argsort(probs)[::-1][:top_k]

    predicted_class = health_index_to_class.get(int(top_indices[0]), "unknown")
    confidence = round(float(probs[top_indices[0]]), 4)

    top_results = [
        {
            "class": health_index_to_class.get(int(i), "unknown"),
            "confidence": round(float(probs[i]), 4)
        }
        for i in top_indices
    ]

    health_status = HEALTH_CLASS_MAP.get(predicted_class, "unhealthy")
    disease_detected = predicted_class in DISEASE_CLASSES
    disease_name = predicted_class if disease_detected else None

    return {
        "health_status": health_status,
        "disease_detected": disease_detected,
        "disease_name": disease_name,
        "confidence": confidence,
        "top_predictions": top_results,
        "model_version": "bitki_saglik_modeli.h5"
    }


# =======================
# SİMÜLASYON MODELİ (joblib / sklearn)
# =======================

SIMULATION_MODEL_PATH = os.path.join(BASE_DIR, "models_ai", "plant_ml_model.pkl")
SIMULATION_SCALER_PATH = os.path.join(BASE_DIR, "models_ai", "plant_scaler.pkl")

simulation_model = joblib.load(SIMULATION_MODEL_PATH)
simulation_scaler = joblib.load(SIMULATION_SCALER_PATH)

print("Simülasyon modeli yüklendi:", SIMULATION_MODEL_PATH)
print("Simülasyon scaler yüklendi:", SIMULATION_SCALER_PATH)


def predict_simulation(temperature, humidity, soil_moisture, light,
                       water_level, ph, last_watering_day, plant_age_days):

    features = np.array([[
        temperature,
        humidity,
        soil_moisture,
        light,
        water_level,
        ph,
        last_watering_day,
        plant_age_days
    ]])

    features_scaled = simulation_scaler.transform(features)
    prediction = simulation_model.predict(features_scaled)

    predicted_growth_cm = round(float(prediction[0]), 2)

    return {
        "predicted_growth_cm": predicted_growth_cm,
        "recommended_watering_ml": 250,
        "confidence": 0.85,
    }

# =======================
# ML-004 OPTİMAL KARAR MODELİ (joblib / sklearn)
# =======================

ML004_SCALER_PATH     = os.path.join(BASE_DIR, "models_ai", "ml004_scaler.pkl")
ML004_CLF_LIGHT_PATH  = os.path.join(BASE_DIR, "models_ai", "ml004_clf_light.pkl")
ML004_CLF_TEMP_PATH   = os.path.join(BASE_DIR, "models_ai", "ml004_clf_temp.pkl")
ML004_CLF_WATER_PATH  = os.path.join(BASE_DIR, "models_ai", "ml004_clf_water.pkl")
ML004_REG_PATH        = os.path.join(BASE_DIR, "models_ai", "ml004_reg_watering_ml.pkl")
ML004_LE_LIGHT_PATH   = os.path.join(BASE_DIR, "models_ai", "ml004_le_light.pkl")
ML004_LE_TEMP_PATH    = os.path.join(BASE_DIR, "models_ai", "ml004_le_temp.pkl")

ml004_scaler    = joblib.load(ML004_SCALER_PATH)
ml004_clf_light = joblib.load(ML004_CLF_LIGHT_PATH)
ml004_clf_temp  = joblib.load(ML004_CLF_TEMP_PATH)
ml004_clf_water = joblib.load(ML004_CLF_WATER_PATH)
ml004_reg       = joblib.load(ML004_REG_PATH)
ml004_le_light  = joblib.load(ML004_LE_LIGHT_PATH)
ml004_le_temp   = joblib.load(ML004_LE_TEMP_PATH)

print("ML-004 modelleri yüklendi.")


def predict_ml004_decision(soil_moisture, temperature, light, air_humidity):
    features = np.array([[soil_moisture, temperature, light, air_humidity]])
    features_scaled = ml004_scaler.transform(features)

    light_label = ml004_le_light.inverse_transform(
        ml004_clf_light.predict(features_scaled)
    )[0]
    temp_label = ml004_le_temp.inverse_transform(
        ml004_clf_temp.predict(features_scaled)
    )[0]

    # le_water yok, classifier çıktısını direkt kullan
    water_pred = int(ml004_clf_water.predict(features_scaled)[0])
    # 0 → sulama gerekli, 1 → gerekli değil (modelinin etiketine göre değişir)
    watering_needed = water_pred == 0

    recommended_ml = float(ml004_reg.predict(features_scaled)[0])

    conf_light = float(np.max(ml004_clf_light.predict_proba(features_scaled)))
    conf_temp  = float(np.max(ml004_clf_temp.predict_proba(features_scaled)))
    conf_water = float(np.max(ml004_clf_water.predict_proba(features_scaled)))
    confidence = round((conf_light + conf_temp + conf_water) / 3, 4)

    def to_adjustment(label):
        label = label.lower()
        if label == "low":
            return "increase"
        elif label == "high":
            return "decrease"
        return "none"

    return {
        "watering_needed": watering_needed,
        "recommended_watering_ml": round(recommended_ml, 2),
        "light_adjustment": to_adjustment(light_label),
        "temperature_adjustment": to_adjustment(temp_label),
        "confidence": confidence,
    }