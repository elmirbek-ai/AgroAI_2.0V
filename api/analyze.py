from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import io
import os
import numpy as np
from PIL import Image

# TensorFlow'ну каталарды (Warning) чыгарбашы үчүн тууралоо
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import tensorflow as tf

analyze_router = APIRouter(prefix='/analyze', tags=['ИИ Анализ (Ооруларды аныктоо)'])

# Моделдер жайгашкан папка
MODELS_DIR = "ml_models"

# Кэш үчүн сөздүк: Моделдерди кайра-кайра жүктөбөш үчүн эс тутумда сактайбыз
loaded_models = {}

# Класстар (Colab'дагы алфавит тартибиндегидей так жазылышы керек)
PLANT_CLASSES = {
    "tomato": sorted([
        "Tomato___Bacterial_spot", "Tomato___Early_blight", "Tomato___Late_blight",
        "Tomato___Leaf_Mold", "Tomato___Septoria_leaf_spot", "Tomato___Spider_mites Two-spotted_spider_mite",
        "Tomato___Target_Spot", "Tomato___Tomato_Yellow_Leaf_Curl_Virus", "Tomato___Tomato_mosaic_virus",
        "Tomato___healthy"
    ]),
    "potato": sorted([
        "Potato___Early_blight", "Potato___Late_blight", "Potato___healthy"
    ]),
    "apple": sorted(["Apple___Apple_scab", "Apple___Black_rot", "Apple___Cedar_apple_rust", "Apple___healthy"]),
    "corn": sorted(["Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot", "Corn_(maize)___Common_rust_",
                    "Corn_(maize)___Northern_Leaf_Blight", "Corn_(maize)___healthy"]),
    "pepper": sorted(["Pepper,_bell___Bacterial_spot", "Pepper,_bell___healthy"]),
    "grape": sorted(["Grape___Black_rot", "Grape___Esca_(Black_Measles)", "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
                     "Grape___healthy"]),
    "strawberry": sorted(["Strawberry___Leaf_scorch", "Strawberry___healthy"])
}

# Агро-Кеңештер (Кийинчерээк муну маалымат базасынан ала тургандай кылсаңыз болот)
RECOMMENDATIONS = {
    "Tomato___Late_blight": "Бул Фитофтороз. Тез арада фунгициддерди (мисалы, Ридомил Голд, Ревус) чачыңыз. Оорулуу жалбырактарды жулуп жок кылыңыз.",
    "Tomato___healthy": "Сиздин помидор дени сак! Ушул бойдон жакшы карап өстүрө бериңиз.",
    "Potato___Early_blight": "Альтернариоз (Эрте жалбырак илдети). Жез камтыган препараттарды колдонуу сунушталат."
    # ... калгандарын акырундук менен толуктап койсоңуз болот
}


# Сүрөттү моделге даярдоо (Colab'дагы ImageDataGenerator сыяктуу)
def preprocess_image(image_bytes: bytes):
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img = img.resize((224, 224))  # MobileNetV2 өлчөмү
        img_array = np.array(img) / 255.0  # Rescale 1./255
        img_array = np.expand_dims(img_array, axis=0)  # Формат: (1, 224, 224, 3)
        return img_array
    except Exception:
        raise ValueError("Сүрөттү окууда ката кетти. Туура форматтагы сүрөт жүктөңүз.")


# Негизги Endpoint
@analyze_router.post("/", summary="Өсүмдүктүн сүрөтүн анализдеп, оорусун аныктоо")
async def analyze_plant_disease(
        plant_type: str = Form(..., description="Өсүмдүктүн түрү (мисалы: tomato, apple, potato)"),
        file: UploadFile = File(...)
):
    plant_type = plant_type.lower()

    # 1. Текшерүү: Бул өсүмдүк биздин системада барбы?
    if plant_type not in PLANT_CLASSES:
        raise HTTPException(status_code=400,
                            detail=f"Бул өсүмдүк түрү колдоого алынбайт. Жеткиликтүүлөр: {', '.join(PLANT_CLASSES.keys())}")

    # 2. Моделди жүктөө (Эгер жүктөлө элек болсо гана)
    if plant_type not in loaded_models:
        model_path = os.path.join(MODELS_DIR, f"{plant_type}_model.keras")
        if not os.path.exists(model_path):
            raise HTTPException(status_code=500,
                                detail=f"{plant_type} үчүн модель табылган жок. ml_models папкасын текшериңиз.")

        try:
            loaded_models[plant_type] = tf.keras.models.load_model(model_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Моделди жүктөөдө ката кетти: {str(e)}")

    # 3. Сүрөттү даярдоо
    image_bytes = await file.read()
    try:
        img_tensor = preprocess_image(image_bytes)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    # 4. Моделге берүү жана жыйынтык алуу (Inference)
    model = loaded_models[plant_type]
    predictions = model.predict(img_tensor)

    # 5. Эң жогорку пайызды табуу
    class_index = np.argmax(predictions[0])
    confidence = float(predictions[0][class_index]) * 100
    class_name = PLANT_CLASSES[plant_type][class_index]

    # 6. Сунуш издөө
    advice = RECOMMENDATIONS.get(class_name, "Бул оору боюнча толук маалымат жакында кошулат. Агрономго кайрылыңыз.")

    return {
        "status": "success",
        "plant": plant_type,
        "disease": class_name,
        "confidence": round(confidence, 2),  # Пайызды 2 санга чейин тегеректөө (мисалы: 95.45)
        "recommendation": advice
    }