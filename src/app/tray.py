import logging
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from pystray import Icon, MenuItem, Menu
from PIL import Image

from src.ai.ocr import ocr, fully_operating_ocr
from src.ai.trans import trans
from src.config import get_config

def show_tray():
    logging.info("show_tray()")
    config = get_config()
    icon_path = config['tray']['icon_path']
    icon_image = Image.open(icon_path)
    icon = Icon(
        "test_tray",
        icon_image,
        menu=Menu(
            MenuItem("연구검토단 Grid System Prototype", print_something, enabled=False),
            MenuItem("기여도: 391", print_something),
            MenuItem("OCR 테스트", file_select_ocr),
            MenuItem("번역 테스트", translate_text),
            MenuItem("종료", on_exit),
        )
    )
    icon.run()



def on_exit(icon:Icon):
    icon.stop()

def print_something(icon:Icon):
    logging.info("HELLO")

def file_select_ocr(icon: Icon):
    window = tk.Tk()
    window.withdraw()
    file_path = filedialog.askopenfilename(
        title="이미지 선택",
        filetypes=[("이미지 파일", "*.png *.jpg *.jpeg *.bmp")]
    )
    if file_path:
        image = Image.open(file_path)
        print(fully_operating_ocr(image))






def translate_text(icon: Icon):
    user_input = simpledialog.askstring("입력", "originalText를 입력하십시오")
    if user_input:
        trans_result = trans(user_input)
        messagebox.showinfo("결과", trans_result)
    else:
        messagebox.showerror("실패", "이유를 알 수 없음")
