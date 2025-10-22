import pandas as pd
import streamlit as st

from kakeibo.common import utils, config_models
from kakeibo.model import database

utils.set_page_config()
utils.rendar_sidebar()
utils.rendar_home_button()

st.title(":material/Place_Item: インポートフォーム")

database.create_table()

uploaded_file = st.file_uploader("**CSVファイルをアップロード**", type=["csv"])
temp_df = pd.DataFrame(columns=config_models.ENTRY_LABELS_JP.to_list())
temp_df.loc[0] = [
	'2023-01-01',  # 日付
	'支出',        # 収入/支出
	'食費',        # カテゴリ
	'ランチ',      # メモ
	'クレジット',  # 支払い方法
	'1000'        # 金額
]
temp_csv = temp_df.to_csv(index=False).encode('utf-8-sig')
st.download_button(
	label='Download CSV Template',
	data=temp_csv,
	file_name='kakeibo_template.csv',
	mime='text/csv',
	icon=":material/download:",
)

if uploaded_file is not None:
	try:
		df = pd.read_csv(uploaded_file)
		st.success("CSVファイルの読み込みに成功しました。")
		st.dataframe(df, hide_index=True)

		if st.button("インポートを実行"):
			df.columns = config_models.ENTRY_LABELS_EN.to_list()
			database.import_entries_from_df(df)
			st.success("データのインポートが完了しました。")
	except Exception as e:
		st.error(f"エラーが発生しました: {e}")
