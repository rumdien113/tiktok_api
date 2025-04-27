import os
import pickle
import tensorflow as tf
from tensorflow.keras.models import load_model
from django.apps import AppConfig
from django.conf import settings
from ultralytics import YOLO
import logging

logger = logging.getLogger(__name__)


class AiResultConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai_result'

    text_model = None
    text_tokenizer = None
    yolo_model = None
    TARGET_CLASSES = ['-', 'This dataset was exported via roboflow.com on April 11- 2024 at 8-18 AM GMT', 'violence-Guns and blod-']
    CONFIDENCE_THRESHOLD = 0.5

    def ready(self):
        # Đường dẫn tới thư mục chứa model
        models_dir = os.path.join(settings.BASE_DIR, 'ai_result', 'models_data')
        logger.info(f"Looking for models in directory: {models_dir}")
        # Tải Text Model và Tokenizer
        text_model_path = os.path.join(models_dir, 'my_model.h5')
        logger.info(f"Attempting to load text model from: {text_model_path}")
        try:
            AiResultConfig.text_model = load_model(text_model_path)
            logger.info(f"Text model '{text_model_path}' loaded successfully.")
        except FileNotFoundError:
            logger.warning(f"Warning: Text model '{text_model_path}' not found. Text prediction functionality will not work.")
        except Exception as e:
            logger.error(f"Error loading text model: {e}")

        tokenizer_path = os.path.join(models_dir, 'tokenizer.pkl')
        logger.info(f"Attempting to load tokenizer from: {tokenizer_path}")
        try:
            with open(tokenizer_path, 'rb') as file:
                AiResultConfig.text_tokenizer = pickle.load(file)
            logger.info(f"Tokenizer '{tokenizer_path}' loaded successfully.")
        except FileNotFoundError:
            logger.warning(f"Warning: Tokenizer '{tokenizer_path}' not found. Text prediction functionality will not work.")
        except Exception as e:
            logger.error(f"Error loading tokenizer: {e}")

        # Tải YOLO Model
        yolo_model_path = os.path.join(models_dir, 'best.pt')
        logger.info(f"Attempting to load YOLO model from: {yolo_model_path}")
        try:
            AiResultConfig.yolo_model = YOLO(yolo_model_path)
            logger.info(f"YOLO model '{yolo_model_path}' loaded successfully.")
        except FileNotFoundError:
            logger.warning(f"Warning: YOLO model '{yolo_model_path}' not found. Object detection functionality will not work.")
        except Exception as e:
            logger.error(f"Error loading YOLO model: {e}")


