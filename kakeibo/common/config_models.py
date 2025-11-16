from dataclasses import dataclass

from pandas import DataFrame


@dataclass
class Entry():
    date: str = 'date'
    transaction_type: str = 'transaction_type'
    category: str = 'category'
    note: str = 'note'
    payment_method: str = 'payment_method'
    amount: str = 'amount'

    def to_list(self) -> list[str]: return [
            self.date,
            self.transaction_type,
            self.category,
            self.note,
            self.payment_method,
            self.amount,
        ]

    def to_dict(self) -> dict[str, str]: return {
            'date': self.date,
            'transaction_type': self.transaction_type,
            'category': self.category,
            'note': self.note,
            'payment_method': self.payment_method,
            'amount': self.amount,
        }

ENTRY_LABELS_EN = Entry()
ENTRY_LABELS_JP = Entry(
    '日付',
    '収入/支出',
    'カテゴリー',
    '内容',
    '支払方法',
    '金額',
)

@dataclass
class BankAccountConfig():
    name: str = ''
    init_balance: int = 0

    def to_dataframe(self) -> DataFrame:
        return DataFrame([{
            '名前': self.name,
            '初期残高': self.init_balance,
        }])

    def to_dict(self) -> dict[str, str]:
        return {
            'name': self.name,
            'init_balance': str(self.init_balance),
        }

    def to_dict_jp(self) -> dict[str, str]:
        return {
            '名前': self.name,
            '初期残高': str(self.init_balance),
        }

@dataclass
class CreditCardConfig():
    name: str = ''
    closing_day: int = 31
    payment_day: int = 10
    limit: int = 300000
    bank_name: str = ''

    def to_dataframe(self) -> DataFrame:
        return DataFrame([{
            '名前': self.name,
            '締め日': self.closing_day,
            '支払日': self.payment_day,
            '利用限度額': self.limit,
            '引き落とし銀行名': self.bank_name,
        }])

    def to_dict(self) -> dict[str, str]:
        return {
            'name': self.name,
            'closing_day': str(self.closing_day),
            'payment_day': str(self.payment_day),
            'limit': str(self.limit),
            'bank_name': self.bank_name,
        }

    def to_dict_jp(self) -> dict[str, str]:
        return {
            '名前': self.name,
            '締め日': str(self.closing_day),
            '支払日': str(self.payment_day),
            '利用限度額': str(self.limit),
            '引き落とし銀行名': self.bank_name,
        }
