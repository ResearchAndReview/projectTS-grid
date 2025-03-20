import logging
import threading
import time

def print_hello():
    while True:
        logging.info("HELLO")
        time.sleep(10)


def initiate_interval():
    hello_thread = threading.Thread(target=print_hello)
    hello_thread.daemon = True
    hello_thread.start()
    return hello_thread