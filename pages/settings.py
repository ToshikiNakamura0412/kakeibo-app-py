import json
import pandas as pd
import streamlit as st

from kakeibo import utils

utils.set_page_config()
utils.rendar_sidebar()
utils.rendar_home_button()

st.title(':material/Settings: 設定')

selected_option = st.selectbox('設定メニュー', ['ユーザー設定', 'カテゴリー設定'])

st.markdown('---')

with open('configs/config.json', 'r', encoding='utf-8') as f:
	df = pd.read_json(f)

if selected_option == 'ユーザー設定':
	pass
else:
	row = st.columns(2)
	with row[0]:
		st.markdown('**収入カテゴリー設定**')
		st.data_editor(df['categories']['income'], num_rows='dynamic', use_container_width=True)
	with row[1]:
		st.markdown('**支出カテゴリー設定**')
		st.data_editor(df['categories']['expense'], num_rows='dynamic', use_container_width=True)

	if st.button(':material/save: 保存'):
		st.success(':material/Check: 保存しました！')
