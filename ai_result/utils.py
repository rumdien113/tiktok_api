# ai_result/utils.py

import os
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
import logging
import cv2
import shutil
import numpy as np

import pickle
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
# Import các model và config từ apps.py
# Đảm bảo bạn đã cấu hình apps.py để load model như hướng dẫn trước
from .apps import AiResultConfig # Thay AiResultConfig bằng tên class AppConfig của bạn nếu khác
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile # Import kiểu dữ liệu file upload

logger = logging.getLogger(__name__)

# Cấu hình Cloudinary (giữ nguyên như trước)
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME", "dnnocayyr"),
    api_key=os.getenv("CLOUDINARY_API_KEY", "488191887775447"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET", "Dc5mZk8bYzzMcOMRhaLODa-NmHs"),
    secure=True
)

# Các hàm upload_image, get_optimized_url, upload_video, get_optimized_video_url (giữ nguyên như trước)
def upload_image(image_path, public_id=None):
    """Tải ảnh lên Cloudinary."""
    try:
        result = cloudinary.uploader.upload(image_path, public_id=public_id)
        logger.info(f"Ảnh đã tải lên Cloudinary thành công: {result.get('url')}")
        return result
    except Exception as e:
        logger.error(f"Lỗi khi tải ảnh lên Cloudinary: {str(e)}")
        raise ValueError(f"Đã xảy ra lỗi khi tải ảnh lên Cloudinary: {str(e)}")

def get_optimized_url(public_id):
    """Lấy URL ảnh được tối ưu hóa từ public ID."""
    url, _ = cloudinary_url(public_id, fetch_format="auto", quality="auto")
    return url

def upload_video(video_path: str, public_id: str = None):
    """Tải video lên Cloudinary."""
    try:
        result = cloudinary.uploader.upload(
            video_path,
            resource_type="video",
            public_id=public_id,
            chunk_size=6000000 # Tăng chunk_size cho file lớn hơn nếu cần
        )
        logger.info(f"Video đã tải lên Cloudinary thành công: {result.get('url')}")
        return result
    except Exception as e:
        logger.error(f"Lỗi khi tải video lên Cloudinary: {str(e)}")
        raise ValueError(f"Đã xảy ra lỗi khi tải video lên Cloudinary: {str(e)}")

def get_optimized_video_url(public_id: str):
    """Lấy URL video được tối ưu hóa từ public ID."""
    url, _ = cloudinary_url(public_id, resource_type="video", fetch_format="auto", quality="auto")
    return url

# Hàm kiểm tra frame (copy từ file gốc ai_tiktok_v0.py)
def check_frame_for_violence(frame, model, target_classes, confidence_threshold):
    if model is None:
        logger.warning("YOLO model is not loaded. Cannot check for violence.")
        return False

    results = model.predict(frame, conf=confidence_threshold, verbose=False)

    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0])
            detected_class_name = model.names[class_id]
            confidence = float(box.conf[0])

            if detected_class_name in target_classes:
                logger.warning(f"Violent content detected: Class '{detected_class_name}' with confidence {confidence:.2f}")
                return True
    return False

# --- Các hàm mới để xử lý và upload ---

def process_and_upload_image(image_file: InMemoryUploadedFile):
    """
    Kiểm tra ảnh bạo lực bằng AI và tải lên Cloudinary nếu hợp lệ.
    Trả về URL ảnh nếu thành công, raise ValueError nếu có lỗi hoặc nội dung bạo lực.
    """
    if AiResultConfig.yolo_model is None:
        logger.error("YOLO model not loaded, cannot process image.")
        raise ValueError('Hệ thống xử lý ảnh AI chưa sẵn sàng.')

    temp_dir = os.path.join(settings.MEDIA_ROOT, "temp_files")
    os.makedirs(temp_dir, exist_ok=True)
    temp_file_path = os.path.join(temp_dir, image_file.name)

    try:
        # Lưu file tạm thời
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(image_file, buffer)
        logger.info(f"Successfully saved temporary image file: {temp_file_path}")

        # Đọc ảnh
        image = cv2.imread(temp_file_path)
        if image is None:
            raise ValueError('Không thể đọc file ảnh.')

        logger.info(f"AI processing started for image: {image_file.name}")

        # Kiểm tra bạo lực
        violent_detected = check_frame_for_violence(image, AiResultConfig.yolo_model, AiResultConfig.TARGET_CLASSES, AiResultConfig.CONFIDENCE_THRESHOLD)

        logger.info(f"AI processing finished for image: {image_file.name}")

        if violent_detected:
            raise ValueError('Ảnh chứa nội dung bạo lực và không hợp lệ.')
        else:
            logger.info(f"No violent content detected in {image_file.name}. Uploading image to Cloudinary...")
            # Tải lên Cloudinary
            public_id = os.path.splitext(image_file.name)[0] + "_image"
            upload_result = upload_image(temp_file_path, public_id=public_id)
            image_url = upload_result.get("url")
            if not image_url:
                 raise ValueError('Không nhận được URL từ Cloudinary sau khi tải lên.')

            logger.info(f"Image {image_file.name} uploaded successfully to Cloudinary. URL: {image_url}")
            return image_url # Trả về URL thành công

    except Exception as e:
        logger.error(f"An error occurred during image processing and upload for {image_file.name}: {str(e)}")
        # Raise lại lỗi để serializer bắt
        raise ValueError(f'Lỗi xử lý ảnh: {str(e)}')

    finally:
        # Dọn dẹp file tạm, bất kể có lỗi hay không
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            logger.info(f"Removed temporary image file: {temp_file_path}")


def process_and_upload_video(video_file: InMemoryUploadedFile):
    """
    Kiểm tra video bạo lực bằng AI và tải lên Cloudinary nếu hợp lệ.
    Trả về URL video nếu thành công, raise ValueError nếu có lỗi hoặc nội dung bạo lực.
    """
    if AiResultConfig.yolo_model is None:
        logger.error("YOLO model not loaded, cannot process video.")
        raise ValueError('Hệ thống xử lý video AI chưa sẵn sàng.')

    temp_dir = os.path.join(settings.MEDIA_ROOT, "temp_files")
    os.makedirs(temp_dir, exist_ok=True)
    temp_file_path = os.path.join(temp_dir, video_file.name)

    try:
        # Lưu file tạm thời
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(video_file, buffer)
        logger.info(f"Successfully saved temporary video file: {temp_file_path}")

        # Mở video
        video_capture = cv2.VideoCapture(temp_file_path)
        if not video_capture.isOpened():
            raise ValueError('Không thể mở file video.')

        logger.info(f"AI processing started for video: {video_file.name}")

        violent_detected = False
        frame_count = 0
        # Kiểm tra mỗi 5 frame (giữ nguyên logic từ file gốc)
        frame_check_interval = 5

        while True:
            ret, frame = video_capture.read()
            if not ret:
                break

            frame_count += 1

            if frame_count % frame_check_interval == 0:
                logging.info(f"Processing frame {frame_count}...")
                if check_frame_for_violence(frame, AiResultConfig.yolo_model, AiResultConfig.TARGET_CLASSES, AiResultConfig.CONFIDENCE_THRESHOLD):
                    violent_detected = True
                    logging.warning(f"Violent content detected at frame {frame_count}. Stopping processing.")
                    break

        video_capture.release()

        logger.info(f"AI processing finished for video: {video_file.name}")

        if violent_detected:
            raise ValueError('Video chứa nội dung bạo lực và không hợp lệ.')
        else:
            logger.info(f"No violent content detected in {video_file.name}. Uploading video to Cloudinary...")
            # Tải lên Cloudinary
            public_id = os.path.splitext(video_file.name)[0] + "_video"
            upload_result = upload_video(temp_file_path, public_id=public_id)
            video_url = upload_result.get("url")
            if not video_url:
                raise ValueError('Không nhận được URL từ Cloudinary sau khi tải lên.')

            logger.info(f"Video {video_file.name} uploaded successfully to Cloudinary. URL: {video_url}")
            return video_url # Trả về URL thành công

    except Exception as e:
        logger.error(f"An error occurred during video processing and upload for {video_file.name}: {str(e)}")
        # Raise lại lỗi để serializer bắt
        raise ValueError(f'Lỗi xử lý video: {str(e)}')

    finally:
        # Dọn dẹp file tạm, bất kể có lỗi hay không
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            logger.info(f"Removed temporary video file: {temp_file_path}")

# Hàm xử lý text
def get_sequences(texts, tokenizer, train=True, max_seq_length=2138):
    if tokenizer is None:
        logger.warning("Text tokenizer is not loaded. Cannot process text sequences.")
        return None
    # Sử dụng pad_sequences đã được import ở đầu file
    sequences = tokenizer.texts_to_sequences(texts)
    sequences = pad_sequences(sequences, maxlen=max_seq_length, padding='post', truncating='post')
    return sequences

# Hàm để phân tích văn bản comment - Đã sửa để trả về trạng thái và thông báo
def analyze_comment_text(comment_content: str):
    """
    Phân tích nội dung comment bằng text model AI.
    Trả về tuple (status, message).
    Status: 0 (hợp lệ), 1 (không phù hợp), -1 (AI chưa sẵn sàng), -2 (lỗi xử lý).
    Message: Thông báo chi tiết (rỗng nếu hợp lệ).
    """
    if AiResultConfig.text_model is None or AiResultConfig.text_tokenizer is None:
        logger.error("Text model or tokenizer not loaded, cannot analyze comment.")
        return (-1, 'Hệ thống phân tích văn bản AI chưa sẵn sàng.') # Trả về trạng thái và thông báo

    if not isinstance(comment_content, str) or not comment_content.strip():
        return (0, '') # Hợp lệ, comment rỗng hoặc chỉ có khoảng trắng

    try:
        # Tiền xử lý văn bản
        processed_text = get_sequences([comment_content], AiResultConfig.text_tokenizer, train=False, max_seq_length=2138)

        if processed_text is None:
             logger.error('Lỗi tiền xử lý văn bản.')
             return (-2, 'Lỗi tiền xử lý văn bản.') # Trả về trạng thái và thông báo

        # Dự đoán bằng model
        prediction = AiResultConfig.text_model.predict(processed_text, verbose=False) # Tắt verbose để không in tiến trình

        # Ngưỡng phân loại (giữ nguyên ngưỡng 0.4 từ file gốc)
        prediction_label = 1 if np.squeeze(prediction) >= 0.4 else 0

        if prediction_label == 1:
            logger.warning(f"Text analysis detected potentially harmful content in comment: '{comment_content[:50]}...'") # Log 50 ký tự đầu
            return (1, 'Nội dung comment chứa từ ngữ không phù hợp.') # Trả về trạng thái và thông báo
        else:
            logger.info(f"Text analysis deemed comment valid: '{comment_content[:50]}...'")
            return (0, '') # Trả về trạng thái và thông báo rỗng

    except Exception as e:
        logger.error(f"An error occurred during text analysis for comment: {str(e)}", exc_info=True)
        return (-2, f'Lỗi phân tích văn bản: {str(e)}') # Trả về trạng thái và thông báo lỗi

