import logging

from pystray import Icon, MenuItem, Menu
from PIL import Image
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
            MenuItem("Exit", on_exit),
            MenuItem("Print", print_something),
        )
    )
    icon.run()


def on_exit(icon:Icon):
    icon.stop()

def print_something(icon:Icon):
    logging.info("HELLO")


