import pandas as pd
import sqlite3
import streamlit as st

from kakeibo import utils

utils.set_page_config()
utils.rendar_sidebar()
utils.rendar_home_button()

st.title(':material/Bar_Chart: 照会画面')

categories = ['食費', '交通費', '娯楽費', 'その他']

view_type = st.radio('表示形式を選択してください', ('年別', '月別'))

years: list[int] = []
for year in range(2020, 2031):
	years.append(year)
selected_year: int = st.selectbox('年を選択してください', years)

if view_type == '月別':
	months = []
	for month in range(1, 13):
		months.append(str(month))
	selected_month = st.selectbox('月を選択してください', months)
else:
	dbname = 'data/entries.db'
	conn = sqlite3.connect(dbname)

	df = pd.read_sql_query('SELECT * FROM entries', conn)
	# insert year from date column
	df['year'] = pd.to_datetime(df['date']).dt.year
	# insert month from date column
	df['month'] = pd.to_datetime(df['date']).dt.month

	category_selection = st.pills("category selection", categories, selection_mode="multi")

	# st.dataframe(df[df['year'] == int(selected_year)])

	# 集計用df → 次ごとのcategoryごとの合計金額を表示
	agg_df = df[df['year'] == int(selected_year)].groupby(['month', 'category']).sum().reset_index()
	# select only selected categories
	if category_selection:
		agg_df = agg_df[agg_df['category'].isin(category_selection)]
	st.line_chart(agg_df, x='month', y='amount', color='category')

	conn.close()
