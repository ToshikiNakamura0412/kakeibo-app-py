import streamlit as st

from kakeibo.common import utils

utils.set_page_config()
utils.rendar_sidebar()
utils.rendar_home_button()

st.title(':material/Input: 入力フォーム')

date = st.date_input('日付：')

col1, col2, col3 = st.columns(3)
with col1:
	transaction_type = st.radio('収支：', ['支出', '収入'])
with col2:
	if transaction_type == '支出':
		category = st.radio('項目：', ['食費', '交通費', '娯楽費', 'その他'])
	else:
		category = st.radio('項目：', ['給料', '副業', 'その他'])
with col3:
	payment_methods = ['クレジットカード１', 'クレジットカード２', '現金']
	payment_method = st.radio('支払い方法：', payment_methods)

note = st.text_input('内容：')

amount = st.number_input('金額：', min_value=0)

if st.button(':material/save: 保存'):
	st.success(':material/Check: 保存しました！')

	st.markdown('---')

	st.subheader('保存内容')
	input_data = {
		'日付': date,
		'収支': transaction_type,
		'項目': category,
		'支払い方法': payment_method,
		'内容': note,
		'金額': amount
	}
	st.table(input_data)
