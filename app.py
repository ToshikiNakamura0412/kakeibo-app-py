import streamlit as st

from kakeibo import utils

utils.rendar_sidebar()

st.title(':material/Home: 家計簿')

row = st.columns(3)
with row[0]:
	if st.button(':material/Input: データ入力', use_container_width=True):
		st.switch_page("pages/input_form.py")
with row[1]:
	if st.button(':material/Edit: 照会/編集', use_container_width=True):
		st.switch_page("pages/input_form.py")
with row[2]:
	if st.button(':material/Settings: 設定', use_container_width=True):
		st.switch_page("pages/input_form.py")
