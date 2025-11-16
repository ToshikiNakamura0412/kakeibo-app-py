import streamlit as st

from kakeibo.common import ui_components


def render_home_page():
    ui_components.render_common_components(":material/Home: 家計簿")

    row = st.columns(5)
    with row[0]:
        if st.button(":material/Input: データ入力", use_container_width=True):
            st.switch_page("pages/input_form.py")
    with row[1]:
        if st.button(":material/Bar_Chart: 照会", use_container_width=True):
            st.switch_page("pages/view_entries.py")
    with row[2]:
        if st.button(":material/Edit: 編集", use_container_width=True):
            st.switch_page("pages/edit_entries.py")
    with row[3]:
        if st.button(
            ":material/Place_Item: インポート", use_container_width=True
        ):
            st.switch_page("pages/import_form.py")
    with row[4]:
        if st.button(":material/Settings: 設定", use_container_width=True):
            st.switch_page("pages/settings.py")


render_home_page()
