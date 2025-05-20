import logging
import threading

import pynvml

from src.app import tray, keepalive
from src import config
from src.app.ipc import run_server
from src.mq.rabbitmq import keep_consuming, get_rabbitmq_connection


def main():
    config.load_config()

    pynvml.nvmlInit()
    mqconn, mqchannel = get_rabbitmq_connection()
    logging.info("Grid client for projectTS initiated")
    keepalive_thread = keepalive.initiate_interval() # TODO: not needed to be joined but do make sure
    threading.Thread(target=keep_consuming(mqchannel), daemon=True).start()
    threading.Thread(target=run_server, daemon=True).start()
    tray.show_tray()
    # keepalive_thread.join() # not available currently
    pynvml.nvmlShutdown()


if __name__ == "__main__":
    main()