import pandas as pd
import streamlit as st

from kakeibo.common import config_models, config_manager
from kakeibo.model import database

database.create_table()

def render_input_form(selected_entry = pd.Series(), selected_id = None, update_button_label='保存') -> None:
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
	for i in range(int(config_manger.user_settings_df['利用銀行数'])):
		payment_method_options.append(f"銀行{i+1}")
	for i in range(int(config_manger.user_settings_df['利用クレジットカード数'])):
		payment_method_options.append(f"クレジット{i+1}")
	try:
		entry.payment_method = str(st.segmented_control('', payment_method_options, default=selected_entry['payment_method']))
	except:
		entry.payment_method = str(st.segmented_control('', payment_method_options, default=payment_method_options[0]))

	# category
	category_options = config_manger.categories_df['income'] if entry.transaction_type == '収入' else config_manger.categories_df['expense']
	category_options = list(category_options)
	try:
		entry.category = str(st.pills('', category_options, default=selected_entry['category']))
	except:
		entry.category = str(st.pills('', category_options, default=category_options[0]))

	row = st.columns(4)
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
