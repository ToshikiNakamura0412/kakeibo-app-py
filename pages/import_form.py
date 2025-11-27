import pandas as pd
import streamlit as st

from kakeibo.common import config_models, ui_components
from kakeibo.common.config_manager import ConfigManager
from kakeibo.model import database


def render_template_download():
    temp_df = pd.DataFrame(columns=config_models.ENTRY_LABELS_JP.to_list())
    temp_df.loc[0] = [
        "2023-01-01",
        "支出",
        "食費",
        "ランチ",
        "クレジット",
        "1000",
    ]
    temp_csv = temp_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="Download CSV Template",
        data=temp_csv,
        file_name="kakeibo_template.csv",
        mime="text/csv",
        icon=":material/download:",
    )


def align_columns_with_labels(df: pd.DataFrame) -> pd.DataFrame:
    expected_cols = len(config_models.ENTRY_LABELS_JP.to_list())
    if len(df.columns) != expected_cols:
        df = df.iloc[:, :expected_cols]
    df.columns = config_models.ENTRY_LABELS_EN.to_list()
    return df


def update_categories_from_df(df: pd.DataFrame):
    config_manger = ConfigManager()
    categories_df = config_manger.categories_df

    categories_income_list = categories_df["income"]
    categories_income_list.extend(
        df[df["transaction_type"] == "収入"]["category"].unique().tolist()
    )
    categories_df["income"] = list(set(categories_income_list))

    categories_expense_list = categories_df["expense"]
    categories_expense_list.extend(
        df[df["transaction_type"] == "支出"]["category"].unique().tolist()
    )
    categories_df["expense"] = list(set(categories_expense_list))

    config_manger.update_categories(categories_df)


def import_data(df: pd.DataFrame):
    df = format_date_df(df)
    database.import_entries_from_df(df)
    update_categories_from_df(df)
    st.success("データのインポートが完了しました。")


def handle_uploaded_file(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)
        st.success("CSVファイルの読み込みに成功しました。")
        df = align_columns_with_labels(df)
        st.dataframe(df, hide_index=True)
        if st.button("インポートを実行"):
            import_data(df)
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")


def format_date(date_str):
    try:
        return pd.to_datetime(date_str).strftime("%Y-%m-%d")
    except ValueError:
        return date_str


def format_date_df(df):
    if "date" in df.columns:
        df["date"] = df["date"].apply(format_date)
    if "amount" in df.columns:
        df["amount"] = (
            df["amount"].str.replace(r'[^\d]', '', regex=True)
            .astype(int)
        )
    return df


def render_page():
    ui_components.render_common_components(
        ":material/Place_Item: インポートフォーム"
    )
    database.create_table()
    uploaded_file = st.file_uploader(
        "**CSVファイルをアップロード**", type=["csv"]
    )
    render_template_download()
    if uploaded_file is not None:
        handle_uploaded_file(uploaded_file)


render_page()
