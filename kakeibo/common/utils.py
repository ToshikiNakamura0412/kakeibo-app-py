import streamlit as st

def set_page_config():
	st.set_page_config(page_title="家計簿アプリ")

def rendar_sidebar():
	with st.sidebar:
		st.page_link("app.py", label=":material/Home: ホーム")
		st.page_link("pages/input_form.py", label=":material/Input: 入力フォーム")
		st.page_link("pages/view_entries.py", label=":material/Bar_Chart: 照会画面")
		st.page_link("pages/edit_entries.py", label=":material/Edit: 編集画面")
		st.page_link("pages/settings.py", label=":material/Settings: 設定")

def rendar_home_button():
	st.page_link("app.py", label=":material/Home:")

def check_file_exists(file_path):
	import os
	return os.path.exists(file_path)
