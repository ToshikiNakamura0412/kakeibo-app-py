import os

import pandas as pd
import streamlit as st

from kakeibo.common import ui_components
from kakeibo.model import database


def convert_format_for_table(df: pd.DataFrame) -> pd.DataFrame:
    df_for_table = df[["category", "amount"]].copy()
    df_for_table["percentage"] = (
        df_for_table["amount"] / df_for_table["amount"].sum() * 100
    ).round(1)
    df_for_table["amount"] = df_for_table["amount"].apply(lambda x: f"{x:,}")
    df_for_table = df_for_table.sort_values(
        by="percentage", ascending=False
    ).reset_index(drop=True)
    df_for_table["percentage"] = df_for_table["percentage"].apply(
        lambda x: f"{x}%"
    )
    df_for_table.rename(
        columns={
            "category": "カテゴリー",
            "amount": "合計金額（円）",
            "percentage": "割合",
        },
        inplace=True,
    )

    return df_for_table


def render_data_guard(df: pd.DataFrame) -> None:
    if len(df) == 0:
        st.warning("表示するデータがありません。")
        st.stop()


def render_balance_notice() -> None:
    ui_components.render_current_balance()
    if not os.path.exists(database.CUSTOM_DB_PATH):
        st.info(
            "デモデータを表示しています。データを入力またはインポートすると、新規データベースが作成されます。"
        )


def select_period(df: pd.DataFrame) -> tuple[str, int, int | None]:
    view_type_options = ["月別", "年別"]
    view_type = st.segmented_control(
        "", view_type_options, key="view_type", default=view_type_options[0]
    )
    year_options = sorted(df["year"].unique())
    selected_year = st.pills(
        "Year", year_options, key="selected_year", default=year_options[-1]
    )
    if selected_year is None:
        st.warning("表示する年を選択してください。")
        st.stop()

    selected_month = None
    if view_type == "月別":
        month_options = sorted(
            df[df["year"] == int(selected_year)]["month"].unique()
        )
        if not month_options:
            st.warning("表示する月がありません。")
            st.stop()
        selected_month = st.pills(
            "Month",
            month_options,
            key="selected_month",
            default=month_options[-1],
        )
        if selected_month is None:
            st.warning("表示する月を選択してください。")
            st.stop()
    return (
        view_type,
        int(selected_year),
        (int(selected_month) if selected_month is not None else None),
    )


def render_monthly_view(df: pd.DataFrame, year: int, month: int) -> None:
    monthly_df = df[(df["year"] == year) & (df["month"] == month)]
    agg_df_income = (
        monthly_df[monthly_df["transaction_type"] == "収入"]
        .groupby(["category"])
        .sum()
        .reset_index()
    )
    agg_df_expense = (
        monthly_df[monthly_df["transaction_type"] == "支出"]
        .groupby(["category"])
        .sum()
        .reset_index()
    )
    sum_income = 0 if agg_df_income.empty else agg_df_income["amount"].sum()
    sum_expense = 0 if agg_df_expense.empty else agg_df_expense["amount"].sum()
    st.markdown("### 収支")
    st.write(f"**合計：{sum_income - sum_expense:,} 円**")

    if not agg_df_income.empty:
        st.markdown("### 収入")
        st.write(f"**合計：{sum_income:,} 円**")
        income_view_type = st.segmented_control(
            "表示形式",
            ["棒グラフ", "表"],
            key="income_view_type",
            default="棒グラフ",
        )
        if income_view_type == "棒グラフ":
            st.bar_chart(
                agg_df_income,
                x="category",
                y="amount",
                x_label="合計金額（円）",
                y_label="カテゴリー",
                color="category",
                horizontal=True,
            )
        else:
            st.table(
                convert_format_for_table(agg_df_income), border="horizontal"
            )

    if not agg_df_expense.empty:
        st.markdown("### 支出")
        st.write(f"**合計：{sum_expense:,} 円**")
        expense_view_type = st.segmented_control(
            "表示形式",
            ["棒グラフ", "表"],
            key="expense_view_type",
            default="棒グラフ",
        )
        if expense_view_type == "棒グラフ":
            st.bar_chart(
                agg_df_expense,
                x="category",
                y="amount",
                x_label="合計金額（円）",
                y_label="カテゴリー",
                color="category",
                horizontal=True,
            )
        else:
            st.table(
                convert_format_for_table(agg_df_expense), border="horizontal"
            )


def render_yearly_view(df: pd.DataFrame, year: int) -> None:
    yearly_df = df[df["year"] == year]
    agg_df_income = (
        yearly_df[yearly_df["transaction_type"] == "収入"]
        .groupby(["category", "month"])
        .sum()
        .reset_index()
    )
    agg_df_expense = (
        yearly_df[yearly_df["transaction_type"] == "支出"]
        .groupby(["category", "month"])
        .sum()
        .reset_index()
    )
    sum_income = 0 if agg_df_income.empty else agg_df_income["amount"].sum()
    sum_expense = 0 if agg_df_expense.empty else agg_df_expense["amount"].sum()
    avg_income = 0 if agg_df_income.empty else agg_df_income["amount"].mean()
    avg_expense = (
        0 if agg_df_expense.empty else agg_df_expense["amount"].mean()
    )
    st.markdown("### 収支")
    st.write(f"**合計：{sum_income - sum_expense:,} 円**")
    st.write(f"**平均：{avg_income - avg_expense:,.0f} 円**")

    if not agg_df_income.empty:
        st.markdown("### 収入")
        st.write(f"**合計：{sum_income:,} 円**")
        st.write(f"**平均：{avg_income:,.0f} 円**")
        category_selection_income = st.pills(
            "Tags",
            agg_df_income["category"].unique().tolist(),
            key="category_selection_income",
            default=agg_df_income["category"].tolist(),
            selection_mode="multi",
        )
        if category_selection_income:
            agg_df_income = agg_df_income[
                agg_df_income["category"].isin(category_selection_income)
            ]
        st.line_chart(agg_df_income, x="month", y="amount", color="category")

    if not agg_df_expense.empty:
        st.markdown("### 支出")
        st.write(f"**合計：{sum_expense:,} 円**")
        st.write(f"**平均：{avg_expense:,.0f} 円**")
        category_selection_expense = st.pills(
            "Tags",
            agg_df_expense["category"].unique().tolist(),
            key="category_selection_expense",
            default=agg_df_expense["category"].tolist(),
            selection_mode="multi",
        )
        if category_selection_expense:
            agg_df_expense = agg_df_expense[
                agg_df_expense["category"].isin(category_selection_expense)
            ]
        st.line_chart(agg_df_expense, x="month", y="amount", color="category")


def render_view_page() -> None:
    ui_components.render_common_components(":material/Bar_Chart: 照会画面")
    database.create_table()
    df = database.fetch_all_entries()
    render_data_guard(df)
    df = df.copy()
    df["year"] = pd.to_datetime(df["date"]).dt.year
    df["month"] = pd.to_datetime(df["date"]).dt.month
    render_balance_notice()
    view_type, selected_year, selected_month = select_period(df)
    if view_type == "月別" and selected_month is not None:
        render_monthly_view(df, selected_year, selected_month)
    elif view_type == "年別":
        render_yearly_view(df, selected_year)


render_view_page()
