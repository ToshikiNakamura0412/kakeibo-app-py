import pandas as pd

from kakeibo.common import utils

CONFIG_FILE_PATH = 'configs/config.json'
CUSTOM_CONFIG_FILE_PATH = 'configs/custom_config.json'

class ConfigManager:
    def __init__(self):
        self.json_path = CUSTOM_CONFIG_FILE_PATH if utils.check_file_exists(CUSTOM_CONFIG_FILE_PATH) else CONFIG_FILE_PATH
        self._load()

    def _load(self):
        with open(self.json_path, 'r', encoding='utf-8') as f:
            self.config_df = pd.read_json(f)
        self.user_settings_df = self.config_df['configs']['user_settings']
        self.categories_df = self.config_df['configs']['categories']

    def reload(self):
        self._load()
