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

def user_setting_change_callback():
	st.session_state['user_setting_changed'] = True

def income_df_change_callback():
	st.session_state['income_df_changed'] = True

def expense_df_change_callback():
	st.session_state['expense_df_changed'] = True

with open('configs/config.json', 'r', encoding='utf-8') as f:
	df = pd.read_json(f)

if selected_option == 'ユーザー設定':
	st.markdown('**ユーザー設定**')
	updated_user_settings = st.data_editor(df['configs']['user_settings'], num_rows='dynamic', use_container_width=True, on_change=user_setting_change_callback)

	if st.button(':material/save: 保存'):
		if st.session_state.get('user_setting_changed', False):
			st.success(':material/Check: ユーザー設定を更新しました！')
			del st.session_state['user_setting_changed']

else:
	row = st.columns(2)

	with row[0]:
		st.markdown('**収入カテゴリー設定**')
		updated_categories_income = st.data_editor(df['configs']['categories']['income'], num_rows='dynamic', use_container_width=True, on_change=income_df_change_callback)
	with row[1]:
		st.markdown('**支出カテゴリー設定**')
		updated_categories_expense = st.data_editor(df['configs']['categories']['expense'], num_rows='dynamic', use_container_width=True, on_change=expense_df_change_callback)

	if st.button(':material/save: 保存'):
		if st.session_state.get('income_df_changed', False):
			st.success(':material/Check: 収入カテゴリーを更新しました！')
			del st.session_state['income_df_changed']

		if st.session_state.get('expense_df_changed', False):
			st.success(':material/Check: 支出カテゴリーを更新しました！')
			del st.session_state['expense_df_changed']
