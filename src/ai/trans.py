import logging

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# 모델 및 토크나이저 로드
model_name = "facebook/nllb-200-1.3B"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

def trans(text_ja):
    # 언어 코드: 일본어 ja → 한국어 ko
    src_lang = "jpn_Jpan"   # 일본어 (일본 문자, 주로 한자/가나)
    tgt_lang = "kor_Hang"   # 한국어 (한글)

    # 토크나이저에 소스 언어 지정
    tokenizer.src_lang = src_lang

    # 토큰화 및 모델 입력
    inputs = tokenizer(text_ja, return_tensors="pt")
    generated_tokens = model.generate(**inputs, forced_bos_token_id=tokenizer.lang_code_to_id[tgt_lang])

    # 디코딩
    decode_result = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
    logging.info(decode_result)
    translated_text = decode_result[0]
    return translated_text

