import pandas as pd
import streamlit as st

from kakeibo.common import config_models, ui_components
from kakeibo.common.config_manager import ConfigManager
from kakeibo.model import database

st.title(":material/Place_Item: インポートフォーム")
ui_components.render_common_components()

database.create_table()

uploaded_file = st.file_uploader("**CSVファイルをアップロード**", type=["csv"])
temp_df = pd.DataFrame(columns=config_models.ENTRY_LABELS_JP.to_list())
temp_df.loc[0] = [
    "2023-01-01",  # 日付
    "支出",  # 収入/支出
    "食費",  # カテゴリ
    "ランチ",  # メモ
    "クレジット",  # 支払い方法
    "1000",  # 金額
]
temp_csv = temp_df.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    label="Download CSV Template",
    data=temp_csv,
    file_name="kakeibo_template.csv",
    mime="text/csv",
    icon=":material/download:",
)


def format_date(date_str):
    try:
        return pd.to_datetime(date_str).strftime("%Y-%m-%d")
    except ValueError:
        return date_str


def format_date_df(df):
    if "date" in df.columns:
        df["date"] = df["date"].apply(format_date)
    return df


if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("CSVファイルの読み込みに成功しました。")
        if len(df.columns) != len(config_models.ENTRY_LABELS_JP.to_list()):
            df = df.iloc[:, : len(config_models.ENTRY_LABELS_JP.to_list())]
        df.columns = config_models.ENTRY_LABELS_EN.to_list()
        st.dataframe(df, hide_index=True)

        if st.button("インポートを実行"):
            df = format_date_df(df)

            # データベースにインポート
            database.import_entries_from_df(df)

            # カテゴリの更新
            config_manger = ConfigManager()
            categories_df = config_manger.categories_df
            # - 収入カテゴリの更新
            categories_income_list = categories_df["income"]
            categories_income_list.extend(
                df[df["transaction_type"] == "収入"]["category"]
                .unique()
                .tolist()
            )
            categories_income_list = list(set(categories_income_list))
            categories_df["income"] = categories_income_list
            # - 支出カテゴリの更新
            categories_expense_list = categories_df["expense"]
            categories_expense_list.extend(
                df[df["transaction_type"] == "支出"]["category"]
                .unique()
                .tolist()
            )
            categories_expense_list = list(set(categories_expense_list))
            categories_df["expense"] = categories_expense_list
            # - 更新反映
            config_manger.update_categories(categories_df)

            st.success("データのインポートが完了しました。")
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
