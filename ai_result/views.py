import os
import cv2
import numpy as np
import shutil
import logging
import json

from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt 
from django.conf import settings

from .apps import AiResultConfig 
from tensorflow.keras.preprocessing.sequence import pad_sequences

from .utils import upload_video, upload_image, get_optimized_video_url, get_optimized_url

logger = logging.getLogger(__name__)

def get_sequences(texts, tokenizer, train=True, max_seq_length=2138):
    if tokenizer is None:
        return None
    sequences = tokenizer.texts_to_sequences(texts)
    sequences = pad_sequences(sequences, maxlen=max_seq_length, padding='post', truncating='post')
    return sequences

def check_frame_for_violence(frame, model, target_classes, confidence_threshold):
    if model is None:
        logger.warning("YOLO model is not loaded. Cannot check for violence.")
        return False # Không thể kiểm tra nếu model không tải

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

@csrf_exempt # Cân nhắc việc xử lý CSRF token nếu đây là API nội bộ hoặc bạn có cơ chế bảo mật khác
def predict_text(request):
    if request.method == 'POST':
        if YourAppConfig.text_model is None or YourAppConfig.text_tokenizer is None:
            return HttpResponseServerError(json.dumps({'error': 'Text prediction model or tokenizer not loaded.'}), content_type='application/json')

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponseBadRequest(json.dumps({'error': 'Invalid JSON format.'}), content_type='application/json')

        text = data.get('text')

        if not text or not isinstance(text, str) or not text.strip():
            return HttpResponseBadRequest(json.dumps({'error': 'Valid text string is required.'}), content_type='application/json')

        try:
            test_processed = get_sequences([text], YourAppConfig.text_tokenizer, train=False, max_seq_length=2138)
            if test_processed is None:
                 return HttpResponseServerError(json.dumps({'error': 'Error processing text sequence.'}), content_type='application/json')

        except Exception as e:
             logger.error(f"Error processing text: {str(e)}")
             return HttpResponseServerError(json.dumps({'error': f'Error processing text: {str(e)}'}), content_type='application/json')

        try:
            prediction = YourAppConfig.text_model.predict(test_processed)
        except Exception as e:
             logger.error(f"Error during model prediction: {str(e)}")
             return HttpResponseServerError(json.dumps({'error': f'Error during model prediction: {str(e)}'}), content_type='application/json')

        prediction_label = 1 if np.squeeze(prediction) >= 0.4 else 0

        return JsonResponse({'text': text, 'prediction': prediction_label})
    else:
        return HttpResponseBadRequest("Only POST method is allowed.")


@csrf_exempt # Cân nhắc việc xử lý CSRF token
def check_video(request):
    if request.method == 'POST':
        if YourAppConfig.yolo_model is None:
            logger.error("YOLO model not loaded, cannot process video.")
            return HttpResponseServerError(json.dumps({'error': 'YOLO model not loaded.'}), content_type='application/json')

        if 'file' not in request.FILES:
            return HttpResponseBadRequest(json.dumps({'error': 'No file provided.'}), content_type='application/json')

        uploaded_file = request.FILES['file']
        temp_dir = os.path.join(settings.MEDIA_ROOT, "temp_files") # Sử dụng MEDIA_ROOT để lưu file tạm
        os.makedirs(temp_dir, exist_ok=True)
        temp_file_path = os.path.join(temp_dir, uploaded_file.name)

        try:
            with open(temp_file_path, "wb") as buffer:
                shutil.copyfileobj(uploaded_file, buffer)
            logger.info(f"Successfully saved temporary video file: {temp_file_path}")
        except Exception as e:
            logger.error(f"Could not save file {uploaded_file.name}: {e}")
            return HttpResponseServerError(json.dumps({'error': f'Could not save file: {e}'}), content_type='application/json')

        video_capture = cv2.VideoCapture(temp_file_path)
        if not video_capture.isOpened():
            logger.error(f"Could not open video file: {temp_file_path}")
            os.remove(temp_file_path)
            return HttpResponseBadRequest(json.dumps({'error': 'Could not open video file.'}), content_type='application/json')

        logger.info(f"AI processing started for video: {uploaded_file.name}")

        violent_detected = False
        frame_count = 0

        while True:
            ret, frame = video_capture.read()
            if not ret:
                break

            frame_count += 1

            if frame_count % 5 == 0: # Kiểm tra mỗi 5 frame
                logging.info(f"Processing frame {frame_count}...")
                if check_frame_for_violence(frame, YourAppConfig.yolo_model, YourAppConfig.TARGET_CLASSES, YourAppConfig.CONFIDENCE_THRESHOLD):
                    violent_detected = True
                    logging.warning(f"Violent content detected at frame {frame_count}. Stopping processing.")
                    break

        video_capture.release()

        logger.info(f"AI processing finished for video: {uploaded_file.name}")

        if violent_detected:
            os.remove(temp_file_path)
            logger.info(f"Video {uploaded_file.name} contains violent content, temporary file removed.")
            return HttpResponseBadRequest(json.dumps({'message': 'Video contains violent content and is not valid.'}), content_type='application/json')
        else:
            logger.info(f"No violent content detected in {uploaded_file.name}. Uploading video to Cloudinary...")
            try:
                public_id = os.path.splitext(uploaded_file.name)[0] + "_video"
                upload_result = upload_video(temp_file_path, public_id=public_id)
                video_url = upload_result.get("url")
                os.remove(temp_file_path)
                logger.info(f"Video {uploaded_file.name} uploaded successfully to Cloudinary. URL: {video_url}")
                return JsonResponse({'message': 'Video is valid and uploaded successfully.', 'video_url': video_url})
            except ValueError as e:
                os.remove(temp_file_path)
                logger.error(f"Cloudinary upload failed for video {uploaded_file.name}: {str(e)}")
                return HttpResponseServerError(json.dumps({'error': str(e)}), content_type='application/json')
            except Exception as e:
                os.remove(temp_file_path)
                logger.error(f"An unexpected error occurred during video upload for {uploaded_file.name}: {str(e)}")
                return HttpResponseServerError(json.dumps({'error': f'An unexpected error occurred during upload: {str(e)}'}), content_type='application/json')
    else:
        return HttpResponseBadRequest("Only POST method is allowed.")


@csrf_exempt # Cân nhắc việc xử lý CSRF token
def check_image(request):
    if request.method == 'POST':
        if YourAppConfig.yolo_model is None:
            logger.error("YOLO model not loaded, cannot process image.")
            return HttpResponseServerError(json.dumps({'error': 'YOLO model not loaded.'}), content_type='application/json')

        if 'file' not in request.FILES:
            return HttpResponseBadRequest(json.dumps({'error': 'No file provided.'}), content_type='application/json')

        uploaded_file = request.FILES['file']
        temp_dir = os.path.join(settings.MEDIA_ROOT, "temp_files") # Sử dụng MEDIA_ROOT để lưu file tạm
        os.makedirs(temp_dir, exist_ok=True)
        temp_file_path = os.path.join(temp_dir, uploaded_file.name)

        try:
            with open(temp_file_path, "wb") as buffer:
                shutil.copyfileobj(uploaded_file, buffer)
            logger.info(f"Successfully saved temporary image file: {temp_file_path}")
        except Exception as e:
            logger.error(f"Could not save file {uploaded_file.name}: {e}")
            return HttpResponseServerError(json.dumps({'error': f'Could not save file: {e}'}), content_type='application/json')

        image = cv2.imread(temp_file_path)
        if image is None:
            logger.error(f"Could not read image file: {temp_file_path}")
            os.remove(temp_file_path)
            return HttpResponseBadRequest(json.dumps({'error': 'Could not read image file.'}), content_type='application/json')

        logger.info(f"AI processing started for image: {uploaded_file.name}")

        violent_detected = check_frame_for_violence(image, YourAppConfig.yolo_model, YourAppConfig.TARGET_CLASSES, YourAppConfig.CONFIDENCE_THRESHOLD)

        logger.info(f"AI processing finished for image: {uploaded_file.name}")

        if violent_detected:
            os.remove(temp_file_path)
            logger.info(f"Image {uploaded_file.name} contains violent content, temporary file removed.")
            return HttpResponseBadRequest(json.dumps({'message': 'Image contains violent content and is not valid.'}), content_type='application/json')
        else:
            logger.info(f"No violent content detected in {uploaded_file.name}. Uploading image to Cloudinary...")
            try:
                public_id = os.path.splitext(uploaded_file.name)[0] + "_image"
                upload_result = upload_image(temp_file_path, public_id=public_id)
                image_url = upload_result.get("url")
                os.remove(temp_file_path)
                logger.info(f"Image {uploaded_file.name} uploaded successfully to Cloudinary. URL: {image_url}")
                return JsonResponse({'message': 'Image is valid and uploaded successfully.', 'image_url': image_url})
            except ValueError as e:
                os.remove(temp_file_path)
                logger.error(f"Cloudinary upload failed for image {uploaded_file.name}: {str(e)}")
                return HttpResponseServerError(json.dumps({'error': str(e)}), content_type='application/json')
            except Exception as e:
                os.remove(temp_file_path)
                logger.error(f"An unexpected error occurred during image upload for {uploaded_file.name}: {str(e)}")
                return HttpResponseServerError(json.dumps({'error': f'An unexpected error occurred during upload: {str(e)}'}), content_type='application/json')
    else:
        return HttpResponseBadRequest("Only POST method is allowed.")
