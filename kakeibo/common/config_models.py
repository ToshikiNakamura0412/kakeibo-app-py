from dataclasses import dataclass
from pandas import DataFrame

@dataclass
class EntryLabelConfig():
    date: str = 'data'
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

ENTRY_LABELS_EN = EntryLabelConfig()
ENTRY_LABELS_JP = EntryLabelConfig(
    '日付',
    '収入/支出',
    'カテゴリー',
    '内容',
    '支払方法',
    '金額',
)

@dataclass
class BankAccountConfig():
    name: str = 'name'
    init_balance: int = 0

    def to_dataframe(self) -> DataFrame:
        return DataFrame([{
            '名前': self.name,
            '初期残高': self.init_balance,
        }])

@dataclass
class CreditCardConfig():
    name: str = ''
    closing_day: int = 31
    payment_day: int = 10
    limit: int = 0
    bank_name: str = ''

    def to_dataframe(self) -> DataFrame:
        return DataFrame([{
            '名前': self.name,
            '締め日': self.closing_day,
            '支払日': self.payment_day,
            '利用限度額': self.limit,
            '引き落とし銀行名': self.bank_name,
        }])

