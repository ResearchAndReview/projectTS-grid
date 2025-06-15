import base64
import io
import json
import logging
import time
import traceback
from time import sleep

import pika
import requests
from PIL import Image

from src.ai import detect_paragraph
from src.ai.ocr import fully_operating_ocr, ocr
from src.ai.trans import trans
from src.ai.performance_manage import PerformanceManager
from src.config import get_config

ocr_perf = PerformanceManager(500*500)
trans_perf = PerformanceManager(50)

def handle_ocr_task(message):
    uuid = get_config()['node']['uuid']
    response = requests.post(f"https://js.thxx.xyz/task/accept-ocr?ocrTaskId={message['ocrTaskId']}",
                             headers={"x-uuid": uuid})
    start_time = time.time()
    base64_string = message['imageData']
    if ',' in base64_string:
        header, base64_data = base64_string.split(',', 1)
        print(f"데이터 URI 헤더 발견: {header}")
        # 필요하다면 header에서 MIME 타입 등을 파싱할 수 있습니다.
        # e.g., mime_type = header.split(';')[0].split(':')[1]
    else:
        # 순수 Base64 문자열이라고 가정
        base64_data = base64_string
    try:
        # 3. Base64 문자열을 바이너리 데이터로 디코딩
        image_bytes = base64.b64decode(base64_data)
        decoded_size = len(image_bytes)
        print(f"Base64 디코딩 완료, 크기: {decoded_size} bytes")

        img = Image.open(io.BytesIO(image_bytes))
        img.verify()  # 이미지 데이터 유효성 검사
        # verify() 후에는 다시 열어야 실제 작업 가능
        img = Image.open(io.BytesIO(image_bytes))
        print(f"이미지 형식: {img.format}, 크기: {img.size}, 모드: {img.mode}")
        # img 객체로 추가 처리 가능
        bounding_box = detect_paragraph.detect_paragraph(img)
        result = {"captions": []}
        for x, y, w, h in bounding_box:
            crop_img = img.crop((x, y, x + w, y + h))
            text = ocr(crop_img)
            result["captions"].append({
                "x": x,
                "y": y,
                "width": w,
                "height": h,
                "text": text
            })
        end_time = time.time()
        elapsed_time = end_time - start_time
        logging.info(f"OCR 작업 완료, 소요 시간: {elapsed_time}초")

        result['elapsedTime'] = elapsed_time

        notify_ocr_success_response = requests.post(
            f"https://js.thxx.xyz/task/notify/ocr-success?ocrTaskId={message['ocrTaskId']}", json=result, headers={'x-uuid': uuid})
    except Exception as e:
        logging.error(traceback.format_exc())
        payload = {
            "error": e
        }
        notify_ocr_failed_response = requests.post(
            f"https://js.thxx.xyz/task/notify/ocr-failed?ocrTaskId={message['ocrTaskId']}", json=payload, headers={'x-uuid': uuid})

def handle_trans_task(message):
    uuid = get_config()['node']['uuid']
    try:
        response = requests.post(f"https://js.thxx.xyz/task/accept-trans?transTaskId={message['transTaskId']}",
                                 headers={"x-uuid": uuid})
        start_time = time.time()
        translated_text = trans(message['originalText'])
        logging.info(f"번역된 텍스트: {translated_text}")
        payload = {
            'translatedText': translated_text,
        }
        end_time = time.time()
        elapsed_time = end_time - start_time
        logging.info(f"번역 작업 완료, 소요 시간: {elapsed_time}초")
        payload['elapsedTime'] = elapsed_time


        requests.post(f"https://js.thxx.xyz/task/notify/trans-success?transTaskId={message['transTaskId']}",
                      json=payload, headers={'x-uuid': uuid})
    except Exception as e:
        logging.error(traceback.format_exc())
        payload = {
            "error": "gTrans FAILED"
        }
        notify_trans_failed_response = requests.post(
            f"https://js.thxx.xyz/task/notify/trans-failed?transTaskId={message['transTaskId']}",
            json=payload, headers={'x-uuid': uuid})


def callback(channel, method, properties, body):
    message = json.loads(body.decode())
    #logging.info(f"Received message: {message}")
    if message["taskType"] == 0: # OCR
        handle_ocr_task(message)

    elif message["taskType"] == 1: # Trans
        handle_trans_task(message)

def get_rabbitmq_connection():
    config = get_config()['mq']['rabbitmq']
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=config['host'],
            port=config['port'],
            virtual_host=config['vhost'],
            credentials=pika.PlainCredentials(
                username=config['user'],
                password=config['pass'],
            ),
        )
    )
    channel = connection.channel()
    return connection, channel

def keep_consuming(mqchannel):
    uuid = get_config()['node']['uuid']
    def inner_method():
        while True:
            try:
                mqchannel.queue_declare(queue=f'node.{uuid}', durable=True)
                mqchannel.basic_consume(
                    queue=f'node.{uuid}',
                    on_message_callback=callback,
                    auto_ack=True
                )
                mqchannel.start_consuming()
            except Exception as e:
                traceback.print_exc()
                sleep(10)

    return inner_method