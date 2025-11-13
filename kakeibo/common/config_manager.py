import pandas as pd

from kakeibo.common import utils, config_models

CONFIG_FILE_PATH = 'configs/config.json'
CUSTOM_CONFIG_FILE_PATH = 'configs/custom_config.json'

class ConfigManager:
    def __init__(self):
        self._load()

    def _load(self):
        self.json_path = CUSTOM_CONFIG_FILE_PATH if utils.check_file_exists(CUSTOM_CONFIG_FILE_PATH) else CONFIG_FILE_PATH
        with open(self.json_path, 'r', encoding='utf-8') as f:
            self.config_df = pd.read_json(f)
        self.renumber_configs()
        self.user_settings_df = self.config_df['configs']['user_settings']
        self.categories_df = self.config_df['configs']['categories']

    def _save(self):
        self.renumber_configs()
        with open(CUSTOM_CONFIG_FILE_PATH, 'w', encoding='utf-8') as f:
            self.config_df.to_json(f, force_ascii=False, indent=2)

    def reload(self):
        self._load()

    def get_cash_init_balance(self) -> int:
        self.reload()
        return int(self.config_df['configs']['user_settings']['init_balance'])

    def update_cash_init_balance(self, value: int):
        self.reload()
        self.config_df['configs']['user_settings']['init_balance'] = value
        self._save()

    def update_user_settings(self, new_settings: pd.DataFrame):
        self.reload()
        self.config_df['configs']['user_settings'] = new_settings
        self._save()

    def update_categories(self, new_categories: pd.DataFrame):
        self.reload()
        self.config_df['configs']['categories'] = new_categories
        self._save()

    def get_bank_account(self, index: int = 0) -> config_models.BankAccountConfig:
        key = f'bank_account_{index}'
        if not self.is_in_config(key):
            return config_models.BankAccountConfig()

        bank_account_dict = dict(self.config_df.loc[key][0])
        return config_models.BankAccountConfig(**bank_account_dict)

    def update_bank_accounts(self, new_accounts: dict, index: int = 0):
        self.reload()
        self.config_df.loc[f'bank_account_{index}'] = [new_accounts]
        self._save()

    def get_credit_card(self, index: int = 0) -> config_models.CreditCardConfig:
        key = f'credit_card_{index}'
        if not self.is_in_config(key):
            return config_models.CreditCardConfig()

        credit_card_dict = dict(self.config_df.loc[key][0])
        return config_models.CreditCardConfig(**credit_card_dict)

    def update_credit_cards(self, new_cards: dict, index: int = 0):
        self.reload()
        self.config_df.loc[f'credit_card_{index}'] = [new_cards]
        self._save()

    def is_in_config(self, key: str) -> bool:
        return key in self.config_df.index

    def renumber_configs(self):
        # Renumber bank accounts
        bank_account_keys = [f'bank_account_{i}' for i in range(1, 11)]
        existing_bank_accounts = [key for key in bank_account_keys if self.is_in_config(key)]
        for i, key in enumerate(existing_bank_accounts):
            if key != f'bank_account_{i + 1}':
                self.config_df.loc[f'bank_account_{i + 1}'] = self.config_df.loc[key]
                self.config_df = self.config_df.drop(index=key)

        # Renumber credit cards
        credit_card_keys = [f'credit_card_{k}' for k in range(1, 11)]
        existing_credit_cards = [key for key in credit_card_keys if self.is_in_config(key)]
        for j, key in enumerate(existing_credit_cards):
            if key != f'credit_card_{j + 1}':
                self.config_df.loc[f'credit_card_{j + 1}'] = self.config_df.loc[key]
                self.config_df = self.config_df.drop(index=key)

    def delete_config(self, key: str) -> bool:
        if not self.is_in_config(key):
            return False
        self.reload()
        self.config_df = self.config_df.drop(index=key)
        self._save()
        return True

