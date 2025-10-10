import pandas as pd
import streamlit as st

from kakeibo.common import utils, config_models

utils.set_page_config()
utils.rendar_sidebar()
utils.rendar_home_button()

st.title(':material/Settings: 設定')

selected_option = st.selectbox('設定メニュー', ['ユーザー設定', 'カテゴリー設定'])

st.markdown('---')

JSON_FILE_PATH = 'configs/config.json'

def user_setting_change_callback():
	st.session_state['user_setting_changed'] = True

def income_df_change_callback():
	st.session_state['income_df_changed'] = True

def expense_df_change_callback():
	st.session_state['expense_df_changed'] = True

def bank_account_change_callback():
	st.session_state['bank_account_changed'] = True

def credit_card_change_callback():
	st.session_state['credit_card_changed'] = True

with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
	df = pd.read_json(f)
	user_settings_df = df['configs']['user_settings']
	categories_df = df['configs']['categories']

if selected_option == 'ユーザー設定':
	st.markdown('**ユーザー設定**')
	updated_user_settings = st.data_editor(user_settings_df, num_rows='dynamic', use_container_width=True, on_change=user_setting_change_callback)

	if st.button(':material/save: 保存'):
		if st.session_state.get('user_setting_changed', False):
			st.success(':material/Check: ユーザー設定を更新しました！')
			df['configs']['user_settings'] = updated_user_settings
			df.to_json(JSON_FILE_PATH, force_ascii=False, indent=2)
			del st.session_state['user_setting_changed']
			st.rerun()

	# bank account settings
	size_of_bank = int(user_settings_df['利用銀行数'])
	if size_of_bank > 0:
		st.markdown('**銀行口座設定**')
		st.data_editor(config_models.BankAccountConfig().to_dataframe(), hide_index=True, on_change=bank_account_change_callback)
		if st.button(':material/save: 銀行口座設定 保存'):
			if st.session_state.get('bank_account_changed', False):
				st.success(':material/Check: 銀行口座設定を更新しました！')
				del st.session_state['bank_account_changed']

	# credit card settings
	size_of_credit_card = int(user_settings_df['利用クレジットカード数'])
	if size_of_credit_card > 0:
		st.markdown('**クレジットカード設定**')
		st.data_editor(config_models.CreditCardConfig().to_dataframe(), hide_index=True, on_change=credit_card_change_callback)
		if st.button(':material/save: クレジットカード設定 保存'):
			if st.session_state.get('credit_card_changed', False):
				st.success(':material/Check: クレジットカード設定を更新しました！')
				del st.session_state['credit_card_changed']

else:
	row = st.columns(2)

	with row[0]:
		st.markdown('**収入カテゴリー設定**')
		updated_categories_income = st.data_editor(categories_df['income'], num_rows='dynamic', use_container_width=True, on_change=income_df_change_callback)
	with row[1]:
		st.markdown('**支出カテゴリー設定**')
		updated_categories_expense = st.data_editor(categories_df['expense'], num_rows='dynamic', use_container_width=True, on_change=expense_df_change_callback)

	if st.button(':material/save: 保存'):
		if st.session_state.get('income_df_changed', False):
			st.success(':material/Check: 収入カテゴリーを更新しました！')
			del st.session_state['income_df_changed']

		if st.session_state.get('expense_df_changed', False):
			st.success(':material/Check: 支出カテゴリーを更新しました！')
			del st.session_state['expense_df_changed']
