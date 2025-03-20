import logging
from src.app import tray, keepalive
from src import config


def main():
    config.load_config()
    logging.info("Grid client for projectTS initiated")
    keepalive_thread = keepalive.initiate_interval() # TODO: not needed to be joined but do make sure
    tray.show_tray()


if __name__ == "__main__":
    main()