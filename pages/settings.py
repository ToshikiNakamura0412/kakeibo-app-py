from typing import dataclass_transform
from unicodedata import category
from pandas import merge
import streamlit as st

from kakeibo.common import utils, config_models
from kakeibo.common.config_manager import ConfigManager
from kakeibo.model import database

utils.set_page_config()
utils.rendar_sidebar()
utils.rendar_home_button()

st.title(':material/Settings: 設定')

database.create_table()
df = database.fetch_all_entries()

config_manger = ConfigManager()
user_settings_df = config_manger.user_settings_df
categories_df = config_manger.categories_df

selected_options = ['ユーザー設定', 'カテゴリー設定']
selected_option = st.segmented_control('設定メニュー', selected_options, default=selected_options[0])

st.markdown('---')

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

@st.dialog(title='削除確認')
def delete_config_confirmation(key):
	st.write('本当に削除しますか？')
	if st.button('はい'):
		config_manger.delete_config(key)
		st.rerun()
	if st.button('いいえ'):
		st.rerun()

if selected_option == 'ユーザー設定':
	cols = st.columns([11,1], vertical_alignment='center')
	with cols[0]:
		st.markdown('##### ユーザー設定')
	with cols[-1]:
		if st.button(f'', icon=':material/edit:'):
			if f'edit_cash' not in st.session_state:
				st.session_state[f'edit_cash'] = True
			else:
				del st.session_state[f'edit_cash']
	if 'edit_cash' in st.session_state:
		cols = st.columns([2, 5], vertical_alignment='bottom')
		with cols[0]:
			cash_init_balance = st.number_input('初期残高（現金）', value=int(config_manger.get_cash_init_balance()))
		if st.button(':material/save: 保存'):
			config_manger.update_cash_init_balance(cash_init_balance)
			st.success(':material/Check: ユーザー設定を更新しました！')
	else:
		cols = st.columns([4,10], vertical_alignment='center')
		with cols[0]:
			st.markdown('初期残高（現金）')
		with cols[1]:
			st.markdown(f'{config_manger.get_cash_init_balance():,} 円')

	# bank account settings
	st.markdown('---')
	st.markdown('##### 銀行口座設定')
	size_of_bank = 0
	for i in range(1, 11):
		if config_manger.is_in_config(f'bank_account_{i}'):
			size_of_bank += 1
		else:
			break
	if size_of_bank > 0:
		for i in range(size_of_bank):
			cols = st.columns([8,1,1], vertical_alignment='bottom')
			with cols[0]:
				st.markdown(f'**銀行口座 {i+1}**')
			with cols[1]:
				if st.button(f'{i+1}', icon=':material/edit:'):
					if f'edit_bank_{i+1}' not in st.session_state:
						st.session_state[f'edit_bank_{i+1}'] = True
					else:
						del st.session_state[f'edit_bank_{i+1}']
			with cols[-1]:
				if st.button(f'{i+1}', icon=':material/delete:'):
					delete_config_confirmation(f'bank_account_{i+1}')
			bank_account_config = config_manger.get_bank_account(i+1)
			if f'edit_bank_{i+1}' in st.session_state:
				cols = st.columns([2, 5, 2], vertical_alignment='bottom')
				with cols[1]:
					bank_account_config.name = st.text_input(f'名前 (銀行 {i+1})', value=bank_account_config.name)
					bank_account_config.init_balance = st.number_input(f'初期残高 (銀行 {i+1})', value=int(bank_account_config.init_balance))
					if st.button(f'銀行口座設定 {i+1} 保存', icon=':material/save:'):
						config_manger.update_bank_accounts(bank_account_config.to_dict(), index=i+1)
						st.session_state[f'bank_account_{i+1}_changed'] = True
						del st.session_state[f'edit_bank_{i+1}']
						st.rerun()
			else:
				cols = st.columns([4, 10], vertical_alignment='bottom')
				for field, value in bank_account_config.to_dict_jp().items():
					with cols[0]:
						st.markdown(f'- {field}')
					with cols[1]:
						st.markdown(f'{value}')
			if st.session_state.get(f'bank_account_{i+1}_changed', False):
				st.success(':material/Check: 銀行口座設定を更新しました！')
				del st.session_state[f'bank_account_{i+1}_changed']

	if st.button('銀行口座設定を追加', icon=':material/add:'):
		config_manger.update_bank_accounts(config_models.BankAccountConfig().to_dict(), index=size_of_bank + 1)
		st.rerun()

	# credit card settings
	st.markdown('---')
	st.markdown('##### クレジットカード設定')
	size_of_credit_card = 0
	for i in range(1, 11):
		if config_manger.is_in_config(f'credit_card_{i}'):
			size_of_credit_card += 1
		else:
			break
	if size_of_credit_card > 0:
		for i in range(size_of_credit_card):
			cols = st.columns([8,1,1], vertical_alignment='bottom')
			with cols[0]:
				st.markdown(f'**クレジットカード {i+1}**')
			with cols[1]:
				if st.button(f' {i+1}', icon=':material/edit:'):
					if f'edit_credit_{i+1}' not in st.session_state:
						st.session_state[f'edit_credit_{i+1}'] = True
					else:
						del st.session_state[f'edit_credit_{i+1}']
			with cols[-1]:
				if st.button(f' {i+1}', icon=':material/delete:'):
					delete_config_confirmation(f'credit_card_{i+1}')
			credit_card_config = config_manger.get_credit_card(i+1)
			if f'edit_credit_{i+1}' in st.session_state:
				cols = st.columns([2, 5, 2], vertical_alignment='bottom')
				with cols[1]:
					credit_card_config.name = st.text_input(f'名前 (カード {i+1})', value=credit_card_config.name)
					credit_card_config.closing_day = st.selectbox(f'締め日 (カード {i+1})', options=list(range(1,32)), index=int(credit_card_config.closing_day) -1)
					credit_card_config.payment_day = st.selectbox(f'支払日 (カード {i+1})', options=list(range(1,32)), index=int(credit_card_config.payment_day) -1)
					credit_card_config.limit = st.number_input(f'利用限度額 (カード {i+1})', value=int(credit_card_config.limit))
					credit_card_config.bank_name = st.text_input(f'引き落とし銀行名 (カード {i+1})', value=credit_card_config.bank_name)
					if st.button(f'クレジットカード設定 {i+1}　保存', icon=':material/save:'):
						config_manger.update_credit_cards(credit_card_config.to_dict(), index=i+1)
						st.session_state[f'credit_card_{i+1}_changed'] = True
						del st.session_state[f'edit_credit_{i+1}']
						st.rerun()
			else:
				for field, value in credit_card_config.to_dict_jp().items():
					cols = st.columns([4, 10], vertical_alignment='bottom')
					with cols[0]:
						st.markdown(f'- {field}')
					with cols[1]:
						st.markdown(f'{value}')
			if st.session_state.get(f'credit_card_{i+1}_changed', False):
				st.success(':material/Check: クレジットカード設定を更新しました！')
				del st.session_state[f'credit_card_{i+1}_changed']

	if st.button('クレジットカード設定を追加', icon=':material/add:'):
		config_manger.update_credit_cards(config_models.CreditCardConfig().to_dict(), index=size_of_credit_card + 1)
		st.rerun()

elif selected_option == 'カテゴリー設定':
	edit_mode = st.segmented_control('編集モード', ['編集', '統合'], default='編集')

	if edit_mode == '編集':
		row = st.columns(2)
		with row[0]:
			st.markdown('**収入カテゴリー設定**')
			updated_categories_income = st.data_editor(categories_df['income'], num_rows='dynamic', use_container_width=True, on_change=income_df_change_callback)
		with row[1]:
			st.markdown('**支出カテゴリー設定**')
			updated_categories_expense = st.data_editor(categories_df['expense'], num_rows='dynamic', use_container_width=True, on_change=expense_df_change_callback)

		if st.button(':material/save: 保存'):
			if st.session_state.get('income_df_changed', False):
				categories_df['income'] = updated_categories_income
				config_manger.update_categories(categories_df)
				st.success(':material/Check: 収入カテゴリーを更新しました！')
				del st.session_state['income_df_changed']

			if st.session_state.get('expense_df_changed', False):
				categories_df['expense'] = updated_categories_expense
				config_manger.update_categories(categories_df)
				st.success(':material/Check: 支出カテゴリーを更新しました！')
				del st.session_state['expense_df_changed']

	elif edit_mode == '統合':
		st.markdown('**カテゴリー統合**')
		selected_transaction = st.radio('タイプを選択', ['収入', '支出'], horizontal=True)
		transaction_type = 'income' if selected_transaction == '収入' else 'expense'
		category_list = categories_df[transaction_type]
		row = st.columns([5,1,5,8], vertical_alignment='center')
		with row[0]:
			merge_source = st.selectbox('統合元', category_list, key='merge_source_income')
		with row[1]:
			st.markdown(':material/arrow_forward_ios:')
		with row[2]:
			category_list.remove(merge_source)
			merge_target = st.selectbox('統合先', category_list, key='merge_target_income')

		if st.button('統合'):
			mask = (df['transaction_type'] == selected_transaction) & (df['category'] == merge_source)
			df.loc[mask, 'category'] = merge_target
			database.override_db(df)
			categories_df[transaction_type] = category_list
			config_manger.update_categories(categories_df)
			st.success(':material/Check: カテゴリーを統合しました！')
