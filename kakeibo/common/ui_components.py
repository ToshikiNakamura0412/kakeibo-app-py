import pandas as pd
import streamlit as st

from kakeibo.common import config_models, config_manager
from kakeibo.model import aggregation, database
from kakeibo.model import aggregation as agg

database.create_table()

def render_input_form(selected_entry = pd.Series(), selected_id = None, update_button_label='保存') -> None:
	df = database.fetch_all_entries()
	entry = config_models.Entry()
	config_manger = config_manager.ConfigManager()

	# date
	row = st.columns(4)
	with row[0]:
		if 'date' in selected_entry.index:
			entry.date = str(st.date_input('日付：', pd.to_datetime(selected_entry['date'])))
		else:
			entry.date = str(st.date_input('日付：'))

	# transaction_type
	if 'transaction_type' in selected_entry.index:
		entry.transaction_type = str(st.segmented_control('', ['収入', '支出'], default=selected_entry['transaction_type']))
	else:
		entry.transaction_type = str(st.segmented_control('', ['収入', '支出'], default='支出'))

	# payment_method
	payment_method_options = ['現金']
	for i in range(1, 11):
		if config_manger.is_in_config(f'bank_account_{i}'):
			bank_account_config = config_manger.get_bank_account(i)
			payment_method_options.append(f"{bank_account_config.name}（銀行）")
		else:
			break
	for i in range(1, 11):
		if config_manger.is_in_config(f'credit_card_{i}'):
			credit_card_config = config_manger.get_credit_card(i)
			payment_method_options.append(f"{credit_card_config.name}（クレジット）")
		else:
			break
	payment_method_options.extend(df['payment_method'].tolist())
	payment_method_options = list(dict.fromkeys(payment_method_options))
	if 'nan' in payment_method_options:
		payment_method_options.remove('nan')

	try:
		entry.payment_method = str(st.segmented_control('', payment_method_options, default=selected_entry['payment_method']))
	except:
		entry.payment_method = str(st.segmented_control('', payment_method_options, default=payment_method_options[0]))

	# category
	category_options = config_manger.categories_df['income'] if entry.transaction_type == '収入' else config_manger.categories_df['expense']
	category_options = list(category_options)
	category_options.extend(df[(df['transaction_type'] == entry.transaction_type)]['category'].tolist())
	category_options = list(dict.fromkeys(category_options))
	if 'nan' in category_options:
		category_options.remove('nan')

	try:
		entry.category = str(st.pills('', category_options, default=selected_entry['category']))
	except:
		entry.category = str(st.pills('', category_options, default=category_options[0]))

	row = st.columns(3)
	with row[0]:
		if 'note' in selected_entry.index:
			entry.note = str(st.text_input('メモ：', selected_entry['note']))
		else:
			entry.note = str(st.text_input('メモ：'))
	with row[1]:
		if 'amount' in selected_entry.index:
			entry.amount = str(st.number_input('金額：', min_value=0, value=int(selected_entry['amount'])))
		else:
			entry.amount = str(st.number_input('金額：', min_value=0))

	if st.button(update_button_label):
		if selected_id is not None:
			database.update_entry(selected_id, entry)
		else:
			database.add_entry(entry)

		st.session_state['update_success'] = True
		st.session_state['selected_id'] = selected_id
		st.rerun()

	st.write('※ カテゴリーなどの統合は、設定画面から行ってください。')

def render_current_balance() -> None:
	aggregation = agg.Aggregation()
	df = database.fetch_all_entries()

	# cash
	cash_balance = aggregation.calc_cash_balance(df)
	st.markdown('### 現金')
	st.write(f'残高：{cash_balance:,} 円')

	# bank
	bank_list = aggregation.get_bank_and_credit_card_list()
	if len(bank_list) > 0:
		st.markdown('### 銀行口座残高')
		for bank in bank_list:
			bank_name = bank['name']
			bank_balance = aggregation.calc_bank_balance(df, bank_name)
			unbilled_amount = aggregation.calc_unbilled_amount(df, bank_name)
			st.write(f'{bank_name}：{bank_balance:,} 円（未請求額：{unbilled_amount:,} 円）')

			if bank_balance < unbilled_amount:
				st.warning(f'⚠️ {bank_name}の残高が未請求額を下回っています。')

