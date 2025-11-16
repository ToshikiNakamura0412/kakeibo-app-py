import streamlit as st

from kakeibo.common import ui_components


def render_input_form():
    st.title(":material/Input: 入力フォーム")
    if (
        "update_success" in st.session_state
        and st.session_state.update_success
    ):
        st.success(":material/Check: 保存しました！")
        del st.session_state["update_success"]
    if "selected_id" in st.session_state:
        del st.session_state["selected_id"]

    ui_components.render_input_form()


ui_components.render_common_components()
render_input_form()
