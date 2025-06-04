import logging
import threading
import time

import cpuinfo
import psutil
import requests
from pynvml_utils import nvidia_smi

from src.app.ipc import ocr_perf, trans_perf

def print_system_info():
    cpu_info = cpuinfo.get_cpu_info()
    nvsmi = nvidia_smi.getInstance()
    nodeId = "TEST01"
    while True:
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        res_util_list = nvsmi.DeviceQuery("name, utilization.gpu, memory.free, memory.total, memory.used")["gpu"]

        gpu_util = res_util_list[0]['utilization']['gpu_util']
        if isinstance(gpu_util, str):
            gpu_util = 100

        payload = {
            'cpu': cpu_info['brand_raw'],
            'cpuUsage': cpu_usage,
            'ram': memory.total / (1024*1024),
            'ramUsage': memory.used / (1024*1024),
            'gpu': res_util_list[0]['product_name'],
            'gpuUsage': gpu_util,
            'vram': res_util_list[0]['fb_memory_usage']['total'],
            'vramUsage': res_util_list[0]['fb_memory_usage']['used'],
            'ocr_perf': ocr_perf.perf,
            'trans_perf': trans_perf.perf
        }

        response = requests.post(f"https://js.thxx.xyz/node/keepalive?nodeId={nodeId}", json=payload)

        time.sleep(10)




def initiate_interval():
    hello_thread = threading.Thread(target=print_system_info)
    hello_thread.daemon = True
    hello_thread.start()
    return hello_thread