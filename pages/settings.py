import streamlit as st

from kakeibo.common import config_models, ui_components
from kakeibo.common.config_manager import ConfigManager
from kakeibo.model import database

config_manger = ConfigManager()

selected_options = ["ユーザー設定", "カテゴリー設定"]


def user_setting_change_callback():
    st.session_state["user_setting_changed"] = True


def income_df_change_callback():
    st.session_state["income_df_changed"] = True


def expense_df_change_callback():
    st.session_state["expense_df_changed"] = True


def bank_account_change_callback():
    st.session_state["bank_account_changed"] = True


def credit_card_change_callback():
    st.session_state["credit_card_changed"] = True


@st.dialog(title="削除確認")
def delete_config_confirmation(key):
    st.write("本当に削除しますか？")
    if st.button("はい"):
        config_manger.delete_config(key)
        st.rerun()
    if st.button("いいえ"):
        st.rerun()


def is_used_in_db(df, column_name, value):
    mask = df[column_name] == value
    return mask.any()


def render_cash_settings(manager: ConfigManager):
    manager.reload()
    cols = st.columns([11, 1], vertical_alignment="center")
    with cols[0]:
        st.markdown("##### ユーザー設定")
    with cols[-1]:
        if st.button("", icon=":material/edit:"):
            if "edit_cash" not in st.session_state:
                st.session_state["edit_cash"] = True
            else:
                del st.session_state["edit_cash"]
    if "edit_cash" in st.session_state:
        cols = st.columns([2, 5], vertical_alignment="bottom")
        with cols[0]:
            cash_init_balance = st.number_input(
                "初期残高（現金）",
                value=int(manager.get_cash_init_balance()),
            )
        if st.button(":material/save: 保存"):
            manager.update_cash_init_balance(cash_init_balance)
            st.success(":material/Check: ユーザー設定を更新しました！")
    else:
        cols = st.columns([4, 10], vertical_alignment="center")
        with cols[0]:
            st.markdown("初期残高（現金）")
        with cols[1]:
            st.markdown(f"{manager.get_cash_init_balance():,} 円")


def render_bank_account_settings(manager: ConfigManager):
    manager.reload()
    st.markdown("##### 銀行口座設定")
    size_of_bank = 0
    for i in range(1, 11):
        if manager.is_in_config(f"bank_account_{i}"):
            size_of_bank += 1
        else:
            break
    if size_of_bank > 0:
        for i in range(size_of_bank):
            cols = st.columns([8, 1, 1], vertical_alignment="bottom")
            with cols[0]:
                st.markdown(f"**銀行口座 {i+1}**")
            with cols[1]:
                if st.button(f"{i+1}", icon=":material/edit:"):
                    key = f"edit_bank_{i+1}"
                    if key not in st.session_state:
                        st.session_state[key] = True
                    else:
                        del st.session_state[key]
            with cols[-1]:
                if st.button(f"{i+1}", icon=":material/delete:"):
                    delete_config_confirmation(f"bank_account_{i+1}")
            bank_account_config = manager.get_bank_account(i + 1)
            if f"edit_bank_{i+1}" in st.session_state:
                cols = st.columns([2, 5, 2], vertical_alignment="bottom")
                with cols[1]:
                    bank_account_config.name = st.text_input(
                        f"名前 (銀行 {i+1})", value=bank_account_config.name
                    )
                    bank_account_config.init_balance = st.number_input(
                        f"初期残高 (銀行 {i+1})",
                        value=int(bank_account_config.init_balance),
                    )
                    if st.button(
                        f"銀行口座設定 {i+1} 保存", icon=":material/save:"
                    ):
                        manager.update_bank_accounts(
                            bank_account_config.to_dict(), index=i + 1
                        )
                        st.session_state[f"bank_account_{i+1}_changed"] = True
                        del st.session_state[f"edit_bank_{i+1}"]
                        st.rerun()
            else:
                cols = st.columns([4, 10], vertical_alignment="bottom")
                for field, value in bank_account_config.to_dict_jp().items():
                    with cols[0]:
                        st.markdown(f"- {field}")
                    with cols[1]:
                        display = (
                            f"{int(value):,} 円"
                            if field == "初期残高"
                            else value
                        )
                        st.markdown(display)
            if st.session_state.get(f"bank_account_{i+1}_changed", False):
                st.success(":material/Check: 銀行口座設定を更新しました！")
                del st.session_state[f"bank_account_{i+1}_changed"]
    if st.button("銀行口座設定を追加", icon=":material/add:"):
        manager.update_bank_accounts(
            config_models.BankAccountConfig().to_dict(), index=size_of_bank + 1
        )
        st.rerun()


def render_credit_card_settings(manager: ConfigManager):
    manager.reload()
    st.markdown("##### クレジットカード設定")
    size_of_credit_card = 0
    for i in range(1, 11):
        if manager.is_in_config(f"credit_card_{i}"):
            size_of_credit_card += 1
        else:
            break
    if size_of_credit_card > 0:
        for i in range(size_of_credit_card):
            cols = st.columns([8, 1, 1], vertical_alignment="bottom")
            with cols[0]:
                st.markdown(f"**クレジットカード {i+1}**")
            with cols[1]:
                if st.button(f" {i+1}", icon=":material/edit:"):
                    key = f"edit_credit_{i+1}"
                    if key not in st.session_state:
                        st.session_state[key] = True
                    else:
                        del st.session_state[key]
            with cols[-1]:
                if st.button(f" {i+1}", icon=":material/delete:"):
                    delete_config_confirmation(f"credit_card_{i+1}")
            credit_card_config = manager.get_credit_card(i + 1)
            if f"edit_credit_{i+1}" in st.session_state:
                cols = st.columns([2, 5, 2], vertical_alignment="bottom")
                with cols[1]:
                    credit_card_config.name = st.text_input(
                        f"名前 (カード {i+1})", value=credit_card_config.name
                    )
                    credit_card_config.closing_day = st.selectbox(
                        f"締め日 (カード {i+1})",
                        options=list(range(1, 32)),
                        index=int(credit_card_config.closing_day) - 1,
                    )
                    credit_card_config.payment_day = st.selectbox(
                        f"支払日 (カード {i+1})",
                        options=list(range(1, 32)),
                        index=int(credit_card_config.payment_day) - 1,
                    )
                    credit_card_config.limit = st.number_input(
                        f"利用限度額 (カード {i+1})",
                        value=int(credit_card_config.limit),
                    )
                    credit_card_config.bank_name = st.text_input(
                        f"引き落とし銀行名 (カード {i+1})",
                        value=credit_card_config.bank_name,
                    )
                    if st.button(
                        f"クレジットカード設定 {i+1}　保存",
                        icon=":material/save:",
                    ):
                        manager.update_credit_cards(
                            credit_card_config.to_dict(), index=i + 1
                        )
                        st.session_state[f"credit_card_{i+1}_changed"] = True
                        del st.session_state[f"edit_credit_{i+1}"]
                        st.rerun()
            else:
                for field, value in credit_card_config.to_dict_jp().items():
                    cols = st.columns([4, 10], vertical_alignment="bottom")
                    with cols[0]:
                        st.markdown(f"- {field}")
                    with cols[1]:
                        display = (
                            f"{int(value):,} 円"
                            if field == "利用限度額"
                            else value
                        )
                        st.markdown(display)
            if st.session_state.get(f"credit_card_{i+1}_changed", False):
                st.success(
                    ":material/Check: クレジットカード設定を更新しました！"
                )
                del st.session_state[f"credit_card_{i+1}_changed"]
    if st.button("クレジットカード設定を追加", icon=":material/add:"):
        manager.update_credit_cards(
            config_models.CreditCardConfig().to_dict(),
            index=size_of_credit_card + 1,
        )
        st.rerun()


def render_user_settings_section(manager: ConfigManager):
    render_cash_settings(manager)
    st.markdown("---")
    render_bank_account_settings(manager)
    st.markdown("---")
    render_credit_card_settings(manager)


def render_category_settings_section(manager: ConfigManager, df):
    manager.reload()
    categories_df = manager.categories_df
    edit_mode = st.segmented_control(
        "編集モード", ["編集", "統合"], default="編集"
    )
    if edit_mode == "編集":
        original_income_categories = list(categories_df["income"])
        original_expense_categories = list(categories_df["expense"])
        row = st.columns(2)
        with row[0]:
            st.markdown("**収入カテゴリー設定**")
            updated_categories_income = st.data_editor(
                categories_df["income"],
                num_rows="dynamic",
                use_container_width=True,
                on_change=income_df_change_callback,
            )
        with row[1]:
            st.markdown("**支出カテゴリー設定**")
            updated_categories_expense = st.data_editor(
                categories_df["expense"],
                num_rows="dynamic",
                use_container_width=True,
                on_change=expense_df_change_callback,
            )
        if st.button(":material/save: 保存"):
            if st.session_state.get("income_df_changed", False):
                xor_list = list(
                    set(original_income_categories)
                    ^ set(updated_categories_income)
                )
                if len(original_income_categories) - len(xor_list) > 0 and any(
                    is_used_in_db(df, "category", cat) for cat in xor_list
                ):
                    st.error(
                        ":material/Warning: 使用中のカテゴリーを削除することはできません。"
                    )
                else:
                    categories_df["income"] = updated_categories_income
                    manager.update_categories(categories_df)
                    st.success(
                        ":material/Check: 収入カテゴリーを更新しました！"
                    )
                    del st.session_state["income_df_changed"]
            if st.session_state.get("expense_df_changed", False):
                xor_list = list(
                    set(original_expense_categories)
                    ^ set(updated_categories_expense)
                )
                if len(original_expense_categories) - len(
                    xor_list
                ) > 0 and any(
                    is_used_in_db(df, "category", cat) for cat in xor_list
                ):
                    st.error(
                        ":material/Warning: 使用中のカテゴリーを削除することはできません。"
                    )
                else:
                    categories_df["expense"] = updated_categories_expense
                    manager.update_categories(categories_df)
                    st.success(
                        ":material/Check: 支出カテゴリーを更新しました！"
                    )
                    del st.session_state["expense_df_changed"]
    else:
        st.markdown("**カテゴリー統合**")
        selected_transaction = st.radio(
            "タイプを選択", ["収入", "支出"], horizontal=True
        )
        transaction_type = (
            "income" if selected_transaction == "収入" else "expense"
        )
        category_list = list(categories_df[transaction_type])
        if not category_list:
            st.warning("統合できるカテゴリーがありません。")
            return
        row = st.columns([5, 1, 5, 8], vertical_alignment="center")
        with row[0]:
            merge_source = st.selectbox(
                "統合元", category_list, key="merge_source_income"
            )
        with row[1]:
            st.markdown(":material/arrow_forward_ios:")
        target_options = [cat for cat in category_list if cat != merge_source]
        if not target_options:
            st.warning("統合先がありません。")
            return
        with row[2]:
            merge_target = st.selectbox(
                "統合先", target_options, key="merge_target_income"
            )
        if st.button("統合"):
            mask = (df["transaction_type"] == selected_transaction) & (
                df["category"] == merge_source
            )
            df.loc[mask, "category"] = merge_target
            database.override_db(df)
            categories_df[transaction_type] = target_options
            manager.update_categories(categories_df)
            st.success(":material/Check: カテゴリーを統合しました！")


def render_settings_page():
    ui_components.render_common_components(":material/Settings: 設定")
    database.create_table()
    df = database.fetch_all_entries()
    selected_option = st.segmented_control(
        "設定メニュー", selected_options, default=selected_options[0]
    )
    st.markdown("---")
    if selected_option == "ユーザー設定":
        render_user_settings_section(config_manger)
    else:
        render_category_settings_section(config_manger, df)


render_settings_page()
