from datetime import datetime
import pandas as pd
import sqlite3
import streamlit as st

from kakeibo.common import utils
from kakeibo.model import database

utils.set_page_config()
utils.rendar_sidebar()
utils.rendar_home_button()

st.title(':material/Bar_Chart: 照会画面')

database.create_table()
df = database.fetch_all_entries()

categories = ['食費', '交通費', '娯楽費', 'その他']

# view_type = st.radio('表示形式を選択してください', ('年別', '月別'))
view_type_options = ['年別', '月別']
view_type = st.segmented_control('', view_type_options, key="view_type", default=view_type_options[0])

start_year = datetime.now().year - 5
end_year = datetime.now().year + 1
years = list(range(start_year, end_year + 1))
init_year_index: int = 0
for i, year in enumerate(years):
	if year == datetime.now().year:
		init_year_index: int = i
selected_year: int = st.selectbox('Year', years, index=init_year_index)

if view_type == '月別':
	months = []
	for month in range(1, 13):
		months.append(str(month))
	selected_month = st.pills('Month', months, key='selected_month', default=str(datetime.now().month))
	# extract data for selected year and Month
	df['year'] = pd.to_datetime(df['date']).dt.year
	df['month'] = pd.to_datetime(df['date']).dt.month

	# 集計用df → 次ごとのcategoryごとの合計金額を表示
	agg_df = df[(df['year'] == int(selected_year)) & (df['month'] == int(selected_month))].groupby(['category']).sum().reset_index()
	st.bar_chart(agg_df, x='category', y='amount')

else:
	# insert year from date column
	df['year'] = pd.to_datetime(df['date']).dt.year
	# insert month from date column
	df['month'] = pd.to_datetime(df['date']).dt.month

	category_selection = st.pills('Tags', categories, selection_mode="multi")

	# st.dataframe(df[df['year'] == int(selected_year)])

	# 集計用df → 次ごとのcategoryごとの合計金額を表示
	agg_df = df[df['year'] == int(selected_year)].groupby(['month', 'category']).sum().reset_index()
	# select only selected categories
	if category_selection:
		agg_df = agg_df[agg_df['category'].isin(category_selection)]
	st.line_chart(agg_df, x='month', y='amount', color='category')
