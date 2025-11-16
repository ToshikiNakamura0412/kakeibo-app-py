import os
from copy import deepcopy

import pandas as pd
import streamlit as st

from kakeibo.common import config_models, ui_components
from kakeibo.model import database


@st.dialog(title="削除確認")
def delete_confirmation(id_to_delete):
    st.write("本当に削除しますか？")
    if st.button("はい"):
        database.delete_entry(id_to_delete)
        st.session_state["delete_success"] = id_to_delete
        st.session_state["selected_id"] = id_to_delete
        st.rerun()
    if st.button("いいえ"):
        st.rerun()


def show_session_messages():
    if st.session_state.get("update_success") and st.session_state.get(
        "selected_id"
    ):
        st.success(
            f"ID {st.session_state['selected_id']} の記録を更新しました。"
        )
        del st.session_state["update_success"]
        del st.session_state["selected_id"]
    elif st.session_state.get("delete_success") and st.session_state.get(
        "selected_id"
    ):
        st.success(
            f"ID {st.session_state['selected_id']} の記録を削除しました。"
        )
        del st.session_state["delete_success"]
        del st.session_state["selected_id"]


def render_entry_details(entry):
    jp_col_label = config_models.ENTRY_LABELS_JP.to_list()
    jp_col_label.insert(0, "ID")
    entry_for_display = deepcopy(entry)
    entry_for_display = pd.DataFrame(entry_for_display)
    entry_for_display.columns = ["データ"]
    entry_for_display.index = jp_col_label
    st.dataframe(entry_for_display)


def render_view_mode(df, transaction_type):
    view_df = df.copy()
    jp_col_label = config_models.ENTRY_LABELS_JP.to_list()
    jp_col_label.insert(0, "ID")
    view_df.columns = jp_col_label
    view_df["金額"] = view_df["金額"].apply(lambda x: f"¥{x:,}")
    row = st.columns(3)
    view_df["year"] = pd.to_datetime(view_df["日付"]).dt.year
    view_df["month"] = pd.to_datetime(view_df["日付"]).dt.month
    with row[0]:
        start_date = st.date_input(
            "開始日",
            value=pd.to_datetime(
                f"{view_df['year'].min()}-{view_df['month'].min()}-01"
            ),
        )
    with row[1]:
        end_date = st.date_input("終了日")
    if transaction_type is not None:
        view_df = view_df[view_df["収入/支出"] == transaction_type]
    view_df = view_df[
        (pd.to_datetime(view_df["日付"]) >= pd.to_datetime(start_date))
        & (pd.to_datetime(view_df["日付"]) <= pd.to_datetime(end_date))
    ]
    view_df = view_df.drop(columns=["year", "month"])
    st.dataframe(view_df, hide_index=True)


def render_edit_mode(selected_entry, selected_id):
    render_entry_details(selected_entry)
    ui_components.render_input_form(
        selected_entry, selected_id, update_button_label="更新"
    )


def render_delete_mode(selected_entry, selected_id):
    render_entry_details(selected_entry)
    if st.button("削除"):
        delete_confirmation(selected_id)


def select_entry(df, transaction_type):
    row = st.columns([2, 1, 1, 11], vertical_alignment="bottom")
    with row[0]:
        id_df = (
            df[df["transaction_type"] == transaction_type]
            if transaction_type is not None
            else df
        )
        if id_df.empty:
            st.warning("選択した種別のデータがありません。")
            st.stop()
        current_index = 0
        if st.session_state.get("selected_id"):
            try:
                current_index = id_df.index[
                    id_df["id"] == st.session_state["selected_id"]
                ][0]
            except IndexError:
                current_index = 0
        selected_id = st.selectbox(
            "ID：", id_df["id"].tolist(), index=int(current_index)
        )
    with row[1]:
        if st.button("", icon=":material/chevron_left:"):
            current_index = df.index[df["id"] == selected_id][0]
            if 0 < current_index:
                st.session_state["selected_id"] = df.iloc[current_index - 1][
                    "id"
                ]
                st.rerun()
    with row[2]:
        if st.button("", icon=":material/chevron_right:"):
            current_index = df.index[df["id"] == selected_id][0]
            if current_index < len(df) - 1:
                st.session_state["selected_id"] = df.iloc[current_index + 1][
                    "id"
                ]
                st.rerun()
    selected_entry = df[df["id"] == selected_id].iloc[0]
    return selected_id, selected_entry


def render_page():
    ui_components.render_common_components()
    st.title(":material/Edit: 編集画面")

    database.create_table()
    # すべての記録を取得して表示
    df = database.fetch_all_entries()

    if len(df) == 0:
        st.warning("表示するデータがありません。")
        st.stop()

    if not os.path.exists(database.CUSTOM_DB_PATH):
        st.info(
            "デモデータを表示しています。データを入力またはインポートすると、新規データベースが作成されます。"
        )

    # notice
    show_session_messages()

    transaction_type = st.segmented_control("", ["収入", "支出"])
    selected_id, selected_entry = select_entry(df, transaction_type)
    mode_options = ["表示モード", "編集モード", "削除モード"]
    mode = st.segmented_control(
        "mode：", mode_options, default=mode_options[0]
    )

    if mode == "表示モード":
        render_view_mode(df.copy(), transaction_type)
    elif mode == "編集モード":
        render_edit_mode(selected_entry, selected_id)
    elif mode == "削除モード":
        render_delete_mode(selected_entry, selected_id)


render_page()
