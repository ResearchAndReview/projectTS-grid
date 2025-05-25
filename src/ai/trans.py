from google.cloud import translate_v3

PROJECT_ID = "youtubeapi3-277821"

def trans(
    text: str = "YOUR_TEXT_TO_TRANSLATE",
    language_code: str = "ko",
) -> str:

    client = translate_v3.TranslationServiceClient()
    parent = f"projects/{PROJECT_ID}/locations/global"
    response = client.translate_text(
        contents=[text],
        target_language_code=language_code,
        parent=parent,
        mime_type="text/plain",
        source_language_code="ja"
    )

    for translation in response.translations:
        return translation.translated_text
    
    return ""