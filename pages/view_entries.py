from datetime import datetime
import pandas as pd
import streamlit as st

from kakeibo.common import utils
from kakeibo.common.config_manager import ConfigManager
from kakeibo.model import database

utils.set_page_config()
utils.rendar_sidebar()
utils.rendar_home_button()

st.title(':material/Bar_Chart: 照会画面')

database.create_table()
df = database.fetch_all_entries()
if len(df) == 0:
	st.warning('表示するデータがありません。')
	st.stop()

config_manger = ConfigManager()

# render current balance
init_balance = config_manger.get_cash_init_balance()
expenses_sum = df[(df['transaction_type'] == '支出') & (df['payment_method'] == '現金')]['amount'].sum()
current_balance = init_balance - expenses_sum
st.subheader(f'初期残高: :money_with_wings: {init_balance} 円')
st.subheader(f'支出合計: :shopping_cart: {expenses_sum} 円')
st.subheader(f'現在残高: :bank: {current_balance} 円')

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

selected_year = st.pills('Year', df['year'].unique(), key='selected_year', default=df['year'].unique()[-1])

if selected_year is None:
	st.warning('表示する年を選択してください。')
	st.stop()

if view_type == '月別':
	selected_month = st.pills('Month', df['month'].unique(), key='selected_month', default=df['month'].unique()[-1])

	# 集計用df → 次ごとのcategoryごとの合計金額を表示
	agg_df_income = df[(df['year'] == int(selected_year)) & (df['month'] == int(selected_month)) & (df['transaction_type'] == '収入')].groupby(['category']).sum().reset_index()
	agg_df_expense = df[(df['year'] == int(selected_year)) & (df['month'] == int(selected_month)) & (df['transaction_type'] == '支出')].groupby(['category']).sum().reset_index()

	sum_income = 0
	sum_expense = 0
	if len(agg_df_income) != 0:
		st.markdown(f"### 収入")
		sum_income = agg_df_income['amount'].sum()
		st.write(f"**合計：{sum_income:,} 円**")
		st.bar_chart(agg_df_income, x='category', y='amount', x_label='合計金額（円）', y_label='カテゴリー', color='category', horizontal=True)
	if len(agg_df_expense) != 0:
		st.markdown(f"### 支出")
		sum_expense = agg_df_expense['amount'].sum()
		st.write(f"**合計：{sum_expense:,} 円**")
		st.bar_chart(agg_df_expense, x='category', y='amount', x_label='合計金額（円）', y_label='カテゴリー', color='category', horizontal=True)

	st.markdown(f"### 収支合計：{sum_income - sum_expense:,} 円")

else:
	# 集計用df → 次ごとのcategoryごとの合計金額を表示
	agg_df_income = df[(df['year'] == int(selected_year)) & (df['transaction_type'] == '収入')].groupby(['category', 'month']).sum().reset_index()
	agg_df_expense = df[(df['year'] == int(selected_year)) & (df['transaction_type'] == '支出')].groupby(['category', 'month']).sum().reset_index()

	if len(agg_df_income) != 0:
		st.markdown('### 収入')
		category_selection_income = st.pills('Tags', agg_df_income['category'].unique().tolist(), key='category_selection_income', default=agg_df_income['category'].tolist(), selection_mode="multi")
		if category_selection_income:
			agg_df_income = agg_df_income[agg_df_income['category'].isin(category_selection_income)]
		st.line_chart(agg_df_income, x='month', y='amount', color='category')

	if len(agg_df_expense) != 0:
		st.markdown('### 支出')
		category_selection_expense = st.pills('Tags', agg_df_expense['category'].unique().tolist(), key='category_selection_expense', default=agg_df_expense['category'].tolist(), selection_mode="multi")
		if category_selection_expense:
			agg_df_expense = agg_df_expense[agg_df_expense['category'].isin(category_selection_expense)]
		st.line_chart(agg_df_expense, x='month', y='amount', color='category')
