import logging
import yaml

config = None

def load_config():
    global config
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logging.info("load_config()")
    with open("config.yaml", 'r') as stream:
        config = yaml.safe_load(stream)
        if 'node' not in config:
            config['node'] = {}
            config['node']['uuid'] = 'TEST01'
def get_config():
    return config