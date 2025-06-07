import logging

# encoder_model_name = "cl-tohoku/bert-base-japanese-v2"
# decoder_model_name = "skt/kogpt2-base-v2"
#
# src_tokenizer = BertJapaneseTokenizer.from_pretrained(encoder_model_name)
# trg_tokenizer = PreTrainedTokenizerFast.from_pretrained(decoder_model_name)
#
# model = EncoderDecoderModel.from_pretrained("sappho192/ffxiv-ja-ko-translator")
#
# def trans(text_src):
#     device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#     embeddings = src_tokenizer(text_src, return_attention_mask=False, return_token_type_ids=False, return_tensors='pt')
#     embeddings = {k: v.to(device) for k, v in embeddings.items()}
#     model.to(device)
#     output = model.generate(**embeddings, max_length=500)[0, 1:-1]
#     text_trg = trg_tokenizer.decode(output.cpu())
#     return text_trg
#

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

