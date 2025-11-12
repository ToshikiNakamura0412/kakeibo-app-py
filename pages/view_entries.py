from datetime import datetime
import pandas as pd
import streamlit as st

from kakeibo.common import utils, ui_components
from kakeibo.model import database

utils.set_page_config()
utils.rendar_sidebar()
utils.rendar_home_button()

st.title(':material/Bar_Chart: 照会画面')

database.create_table()
df = database.fetch_all_entries()

def convert_format_for_table(df: pd.DataFrame) -> pd.DataFrame:
	df_for_table = df[['category', 'amount']].copy()
	df_for_table['percentage'] = (df_for_table['amount'] / df_for_table['amount'].sum() * 100).round(1)
	df_for_table['amount'] = df_for_table['amount'].apply(lambda x: f"{x:,}")
	df_for_table = df_for_table.sort_values(by='percentage', ascending=False).reset_index(drop=True)
	df_for_table['percentage'] = df_for_table['percentage'].apply(lambda x: f"{x}%")
	df_for_table.rename(columns={'category': 'カテゴリー', 'amount': '合計金額（円）', 'percentage': '割合'}, inplace=True)

	return df_for_table

if len(df) == 0:
	st.warning('表示するデータがありません。')
	st.stop()

ui_components.render_current_balance()

view_type_options = ['月別', '年別']
view_type = st.segmented_control('', view_type_options, key="view_type", default=view_type_options[0])

start_year = datetime.now().year - 5
end_year = datetime.now().year + 1
years = list(range(start_year, end_year + 1))
init_year_index: int = 0
for i, year in enumerate(years):
	if year == datetime.now().year:
		init_year_index: int = i

df['year'] = pd.to_datetime(df['date']).dt.year
df['month'] = pd.to_datetime(df['date']).dt.month

year_options = list(df['year'].unique())
year_options = sorted(year_options)
selected_year = st.pills('Year', year_options, key='selected_year', default=year_options[-1])

if selected_year is None:
	st.warning('表示する年を選択してください。')
	st.stop()

if view_type == '月別':
	month_options = list(df[df['year'] == int(selected_year)]['month'].unique())
	month_options = sorted(month_options)
	selected_month = st.pills('Month', month_options, key='selected_month', default=month_options[-1])
	if selected_month is None:
		st.warning('表示する月を選択してください。')
		st.stop()

	# 集計用df → 次ごとのcategoryごとの合計金額を表示
	agg_df_income = df[(df['year'] == int(selected_year)) & (df['month'] == int(selected_month)) & (df['transaction_type'] == '収入')].groupby(['category']).sum().reset_index()
	agg_df_expense = df[(df['year'] == int(selected_year)) & (df['month'] == int(selected_month)) & (df['transaction_type'] == '支出')].groupby(['category']).sum().reset_index()

	sum_income = 0 if len(agg_df_income) == 0 else agg_df_income['amount'].sum()
	sum_expense = 0 if len(agg_df_expense) == 0 else agg_df_expense['amount'].sum()

	st.markdown(f"### 収支")
	st.write(f"**合計：{sum_income - sum_expense:,} 円**")

	if len(agg_df_income) != 0:
		st.markdown(f"### 収入")
		st.write(f"**合計：{sum_income:,} 円**")

		view_type = st.segmented_control('表示形式', ['棒グラフ', '表'], key='income_view_type', default='棒グラフ')
		if view_type == '棒グラフ':
			st.bar_chart(agg_df_income, x='category', y='amount', x_label='合計金額（円）', y_label='カテゴリー', color='category', horizontal=True)
		elif view_type == '表':
			df_income_for_table = convert_format_for_table(agg_df_income)
			st.table(df_income_for_table, border='horizontal')

	if len(agg_df_expense) != 0:
		st.markdown(f"### 支出")
		st.write(f"**合計：{sum_expense:,} 円**")

		view_type = st.segmented_control('表示形式', ['棒グラフ', '表'], key='expense_view_type', default='棒グラフ')
		if view_type == '棒グラフ':
			st.bar_chart(agg_df_expense, x='category', y='amount', x_label='合計金額（円）', y_label='カテゴリー', color='category', horizontal=True)
		elif view_type == '表':
			df_expense_for_table = convert_format_for_table(agg_df_expense)
			st.table(df_expense_for_table, border='horizontal')


elif view_type == '年別':
	# 集計用df → 次ごとのcategoryごとの合計金額を表示
	agg_df_income = df[(df['year'] == int(selected_year)) & (df['transaction_type'] == '収入')].groupby(['category', 'month']).sum().reset_index()
	agg_df_expense = df[(df['year'] == int(selected_year)) & (df['transaction_type'] == '支出')].groupby(['category', 'month']).sum().reset_index()

	# agg
	# - income
	sum_income = 0 if len(agg_df_income) == 0 else agg_df_income['amount'].sum()
	avg_income = 0 if len(agg_df_income) == 0 else agg_df_income['amount'].mean()
	# - expense
	sum_expense = 0 if len(agg_df_expense) == 0 else agg_df_expense['amount'].sum()
	avg_expense = 0 if len(agg_df_expense) == 0 else agg_df_expense['amount'].mean()

	st.markdown(f"### 収支")
	st.write(f'**合計：{sum_income - sum_expense:,} 円**')
	st.write(f'**平均：{avg_income - avg_expense:,.0f} 円**')

	if len(agg_df_income) != 0:
		st.markdown('### 収入')
		st.write(f"**合計：{sum_income:,} 円**")
		st.write(f"**平均：{avg_income:,.0f} 円**")
		category_selection_income = st.pills('Tags', agg_df_income['category'].unique().tolist(), key='category_selection_income', default=agg_df_income['category'].tolist(), selection_mode="multi")
		if category_selection_income:
			agg_df_income = agg_df_income[agg_df_income['category'].isin(category_selection_income)]
		st.line_chart(agg_df_income, x='month', y='amount', color='category')

	if len(agg_df_expense) != 0:
		st.markdown('### 支出')
		st.write(f"**合計：{sum_expense:,} 円**")
		st.write(f"**平均：{avg_expense:,.0f} 円**")
		category_selection_expense = st.pills('Tags', agg_df_expense['category'].unique().tolist(), key='category_selection_expense', default=agg_df_expense['category'].tolist(), selection_mode="multi")
		if category_selection_expense:
			agg_df_expense = agg_df_expense[agg_df_expense['category'].isin(category_selection_expense)]
		st.line_chart(agg_df_expense, x='month', y='amount', color='category')
