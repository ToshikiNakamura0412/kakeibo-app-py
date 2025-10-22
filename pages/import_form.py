import pandas as pd
import streamlit as st

from kakeibo.common import utils, config_models

utils.set_page_config()
utils.rendar_sidebar()
utils.rendar_home_button()

st.title(":material/Place_Item: インポートフォーム")

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
