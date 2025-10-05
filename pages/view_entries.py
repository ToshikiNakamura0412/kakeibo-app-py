import streamlit as st

from kakeibo import utils

utils.set_page_config()
utils.rendar_sidebar()
utils.rendar_home_button()

st.title(':material/Bar_Chart: 照会画面')

