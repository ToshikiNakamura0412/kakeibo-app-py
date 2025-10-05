import streamlit as st

def rendar_sidebar():
	with st.sidebar:
		st.page_link("app.py", label=":material/Home: ホーム")
		st.page_link("pages/input_form.py", label=":material/Input: 入力フォーム")

def rendar_home_button():
	st.page_link("app.py", label=":material/Home:")
