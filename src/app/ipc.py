from flask import Flask, request

import time

from flask import Flask, request, jsonify
import base64
import io
import binascii # Base64 디코딩 오류 처리를 위해

from PIL import Image
from src.ai import trans
from src.ai import ocr, performance_manage, detect_paragraph

app= Flask("HTTP API")

# Performance 수치
# TODO : 작업 종료 시에 로컬에 저장하고 다시 불러오는 기능 필요

ocr_perf = performance_manage.PerformanceManager(500*500)
trans_perf = performance_manage.PerformanceManager(50)

@app.route('/', methods=['GET'])
def test():
    return "Hello World", 200

@app.route('/getStatus', methods=['GET'])
def getStatus():
    return "ACTIVE", 200

@app.route('/ocr', methods=['POST'])
def ocr_():
    """POST 요청의 JSON 본문에서 Base64 인코딩된 이미지를 받아 OCR 처리하는 API"""

    # 1. 요청 본문이 JSON인지 확인하고 데이터 가져오기
    if not request.is_json:
        return jsonify({"error": "요청 형식이 JSON이 아닙니다 (Content-Type: application/json 필요)"}), 415 # Unsupported Media Type

    try:
        data = request.get_json()
    except Exception as e:
        # JSON 파싱 오류 등
        return jsonify({"error": f"잘못된 JSON 데이터입니다: {e}"}), 400

    # 2. JSON 데이터 안에 'image' 키가 있는지 확인
    if not data or 'image' not in data:
        return jsonify({"error": "JSON 본문에 'image' 키가 없습니다."}), 400

    base64_string = data['image']

    # (선택 사항) 데이터 URI 스킴 처리 (예: "data:image/png;base64,iVBOR...")
    # 실제 Base64 데이터만 추출
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

        try:
            img = Image.open(io.BytesIO(image_bytes))
            img.verify() # 이미지 데이터 유효성 검사
            # verify() 후에는 다시 열어야 실제 작업 가능
            img = Image.open(io.BytesIO(image_bytes))
            print(f"이미지 형식: {img.format}, 크기: {img.size}, 모드: {img.mode}")
            # img 객체로 추가 처리 가능
        except Exception as e:
            print(f"Pillow 처리 오류: {e}")
            # 유효하지 않은 이미지 파일일 수 있음
            return jsonify({"error": "디코딩된 데이터가 유효한 이미지 파일이 아닙니다."}), 400
        
        # 전체 이미지 판단이므로 일단은 이렇게
        # x, y = 0, 0
        # width, height = img.width, img.height
        # text = ocr_trans.ocr(img)

        start_time = time.time()
        bounding_box = detect_paragraph.detect_paragraph(img)
        result = { "captions": [] }
        for x, y, w, h in bounding_box:
            crop_img = img.crop((x, y, x+w, y+h))
            text = ocr.ocr(crop_img)
            result["captions"].append({
                "x": x,
                "y": y,
                "width": w,
                "height": h,
                "text": text
            })
        end_time = time.time()
        calc_perf = (img.height * img.width) ** 1.5 / (end_time - start_time)
        ocr_perf.update(calc_perf=calc_perf)
        print(f"ocr_perf: {ocr_perf.perf}")

        # 4. 성공 응답 반환
        return jsonify(result), 200

    except binascii.Error as e: # Base64 디코딩 오류
        print(f"Base64 디코딩 오류: {e}")
        return jsonify({"error": "잘못된 Base64 문자열입니다."}), 400
    except Exception as e:
        print(f"이미지 처리 중 오류 발생: {e}")
        return jsonify({"error": f"이미지 처리 중 서버 오류 발생 : {str(e)}"}), 500
    
@app.route('/translation', methods=['post'])
def translation_():
    """POST 요청의 JSON 본문에서 텍스트를 번역해주는 API"""

    # 1. 요청 본문이 JSON인지 확인하고 데이터 가져오기
    if not request.is_json:
        return jsonify({"error": "요청 형식이 JSON이 아닙니다 (Content-Type: application/json 필요)"}), 415 # Unsupported Media Type

    try:
        data = request.get_json()
    except Exception as e:
        # JSON 파싱 오류 등
        return jsonify({"error": f"잘못된 JSON 데이터입니다: {e}"}), 400
    
    # 2. JSON 데이터 안에 'originalText', 'translateFrom', 'translateTo' 키가 있는지 확인
    if not data:
        return jsonify({"error": "JSON 본문이 비어있습니다."}), 400
    if 'originalText' not in data:
        return jsonify({"error": "JSON 본문에 'originalText' 키가 비어있습니다."}), 400
    if 'translateFrom' not in data:
        return jsonify({"error": "JSON 본문에 'translateFrom' 키가 비어있습니다."}), 400
    if 'translateTo' not in data:
        return jsonify({"error": "JSON 본문에 'translateTo' 키가 비어있습니다."}), 400
    
    try:
        start_time = time.time()
        translated_text = trans.trans(data['originalText'])
        end_time = time.time()
        calc_perf = len(data['originalText']) ** 1.5 / (end_time - start_time)
        trans_perf.update(calc_perf=calc_perf)
        print(f"trans_perf: {trans_perf.perf}")

        return jsonify({
            'originalText': data['originalText'],
            'translatedText': translated_text
        }), 200
    except Exception as e:
        return jsonify({"error": f"번역 처리 중 서버 오류 발생 : {str(e)}"}), 500

def run_server():
    app.run(host="127.0.0.1", port=57858)