import calendar
from datetime import datetime

import pandas as pd

from kakeibo.common.config_manager import ConfigManager


def create_bank_and_credit_card_list(config_manger: ConfigManager) -> list:
    bank_list = []
    for i in range(1, 11):
        if config_manger.is_in_config(f"bank_account_{i}"):
            bank_account_config = config_manger.get_bank_account(i)
            bank_list.append(
                {
                    "name": bank_account_config.name,
                    "display_name": f"{bank_account_config.name}（銀行）",
                    "credit_card": [],
                }
            )
        else:
            break
    for bank_account in bank_list:
        for i in range(1, 11):
            if config_manger.is_in_config(f"credit_card_{i}"):
                credit_card_config = config_manger.get_credit_card(i)
                bank_name = credit_card_config.bank_name
                if bank_name == bank_account["name"]:
                    bank_account["credit_card"].append(
                        credit_card_config.to_dict()
                    )
            else:
                break

    return bank_list


class Aggregation:
    _config_manger = ConfigManager()
    _bank_and_credit_card_list = create_bank_and_credit_card_list(
        _config_manger
    )

    def get_bank_and_credit_card_list(self) -> list:
        return self._bank_and_credit_card_list

    def get_cash_init_balance(self) -> int:
        return self._config_manger.get_cash_init_balance()

    def sum_cash_income(self, df: pd.DataFrame) -> int:
        try:
            cash_income = df[
                (df["transaction_type"] == "収入")
                & (df["payment_method"] == "現金")
            ]
            return cash_income["amount"].sum()
        except KeyError:
            return 0

    def sum_cash_expenses(self, df: pd.DataFrame) -> int:
        try:
            cash_expenses = df[
                (df["transaction_type"] == "支出")
                & (df["payment_method"] == "現金")
            ]
            return cash_expenses["amount"].sum()
        except KeyError:
            return 0

    def calc_cash_balance(self, df: pd.DataFrame) -> int:
        initial_balance = self.get_cash_init_balance()
        total_income = self.sum_cash_income(df)
        total_expenses = self.sum_cash_expenses(df)
        cash_balance = initial_balance + total_income - total_expenses
        return cash_balance

    def get_bank_init_balance(self, bank_name: str) -> int:
        for i in range(1, 11):
            if self._config_manger.is_in_config(f"bank_account_{i}"):
                bank_account_config = self._config_manger.get_bank_account(i)
                if bank_account_config.name == bank_name:
                    return int(bank_account_config.init_balance)
            else:
                break
        return 0

    def sum_bank_income(self, df: pd.DataFrame, bank_name: str) -> int:
        try:
            bank_income = df[
                (df["transaction_type"] == "収入")
                & (df["payment_method"] == f"{bank_name}（銀行）")
            ]
            return bank_income["amount"].sum()
        except KeyError:
            return 0

    def sum_bank_expenses(self, df: pd.DataFrame, bank_name: str) -> int:
        try:
            bank_expenses = df[
                (df["transaction_type"] == "支出")
                & (df["payment_method"] == f"{bank_name}（銀行）")
            ]
            return bank_expenses["amount"].sum()
        except KeyError:
            return 0

    def make_valid_date(self, year, month, day) -> datetime:
        last_day = calendar.monthrange(year, month)[1]
        return datetime(year, month, min(day, last_day))

    def sum_credit_card_expenses(
        self, df: pd.DataFrame, bank_name: str
    ) -> int:
        credit_cards = []
        for bank_account in self._bank_and_credit_card_list:
            if bank_account["name"] == bank_name:
                credit_cards = bank_account["credit_card"]
                break

        sum_expenses = 0
        for credit_card in credit_cards:
            credit_card_name = credit_card["name"]
            try:
                credit_card_expenses = df[
                    (df["transaction_type"] == "支出")
                    & (
                        df["payment_method"]
                        == f"{credit_card_name}（クレジット）"
                    )
                ]

                today = datetime.today()
                if not credit_card_expenses.empty:
                    if (
                        self.make_valid_date(
                            today.year,
                            today.month,
                            int(credit_card["payment_day"]),
                        )
                        <= today
                    ):
                        date_th = self.make_valid_date(
                            today.year,
                            today.month - 1,
                            int(credit_card["closing_day"]),
                        )
                    else:
                        date_th = self.make_valid_date(
                            today.year,
                            today.month - 2,
                            int(credit_card["closing_day"]),
                        )
                    credit_card_expenses = credit_card_expenses[
                        pd.to_datetime(credit_card_expenses["date"]) <= date_th
                    ]

                sum_expenses += credit_card_expenses["amount"].sum()

            except KeyError:
                continue

        return sum_expenses

    def calc_bank_balance(self, df: pd.DataFrame, bank_name: str) -> int:
        # transaction in bank
        initial_balance = self.get_bank_init_balance(bank_name)
        total_income = self.sum_bank_income(df, bank_name)
        total_expenses = self.sum_bank_expenses(df, bank_name)
        bank_balance = initial_balance + total_income - total_expenses

        # transaction in credit card
        credit_card_expenses = self.sum_credit_card_expenses(df, bank_name)
        bank_balance -= credit_card_expenses

        return bank_balance

    def calc_unbilled_amount(self, df: pd.DataFrame, bank_name: str) -> int:
        credit_cards = []
        for bank_account in self._bank_and_credit_card_list:
            if bank_account["name"] == bank_name:
                credit_cards = bank_account["credit_card"]
                break

        sum_expenses = 0
        for credit_card in credit_cards:
            credit_card_name = credit_card["name"]
            try:
                credit_card_expenses = df[
                    (df["transaction_type"] == "支出")
                    & (
                        df["payment_method"]
                        == f"{credit_card_name}（クレジット）"
                    )
                ]
                sum_expenses += credit_card_expenses["amount"].sum()

            except KeyError:
                continue

        sum_expenses -= self.sum_credit_card_expenses(df, bank_name)

        return sum_expenses
