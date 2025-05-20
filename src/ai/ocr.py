from manga_ocr import MangaOcr

mocr = MangaOcr()

def ocr(img, src_lang="일본어"):
    global mocr
    return mocr(img)
