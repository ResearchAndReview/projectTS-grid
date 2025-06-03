import logging
from json import JSONEncoder

from manga_ocr import MangaOcr

from src.ai.detect_paragraph import detect_paragraph

mocr = MangaOcr()

def ocr(img, src_lang="일본어"):
    global mocr
    return mocr(img)

def fully_operating_ocr(img):
    try:
        bounding_box = detect_paragraph(img)
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

        return result

    except Exception as e:
        logging.error(f"이미지 처리 중 오류 발생: {e}")
