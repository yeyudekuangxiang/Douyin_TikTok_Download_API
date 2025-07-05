import os
import yaml
def getConfig():
    config_path = os.path.join(os.path.dirname(__file__),'config', 'config.yaml')
    print(config_path)
    with open(config_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)