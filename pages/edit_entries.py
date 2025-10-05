import pandas as pd
import sqlite3
import streamlit as st

from kakeibo import utils

utils.set_page_config()
utils.rendar_sidebar()
utils.rendar_home_button()

st.title(":material/Edit: 編集画面")

dbname = 'data/entries.db'
conn = sqlite3.connect(dbname)

cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    transaction_type TEXT NOT NULL,
    category TEXT NOT NULL,
    note TEXT,
    payment_method TEXT,
    amount INTEGER NOT NULL
)
""")
conn.commit()

# update
update_success = False
row = st.columns(4, vertical_alignment='bottom')
with row[0]:
	id_to_update = st.number_input('ID：', min_value=0, step=1)
with row[1]:
	col_name = st.selectbox('項目：', ['date', 'transaction_type', 'category', 'note', 'payment_method', 'amount'])
with row[2]:
	new_value = st.text_input('新しい値：')
with row[3]:
	if st.button('更新'):
		cur.execute(f'UPDATE entries SET {col_name} = ? WHERE id = ?', (new_value, id_to_update))
		conn.commit()
		update_success = True

if update_success:
	st.success(f'ID {id_to_update} の記録を更新しました。')

@st.dialog(title='削除確認')
def detete_confirmation(id_to_delete):
	st.write('本当に削除しますか？')
	if st.button('はい'):
		st.session_state['delete_id'] = id_to_delete
		st.rerun()
	if st.button('いいえ'):
		st.rerun()

row = st.columns(4, vertical_alignment='bottom')

detele_success = True
with row[0]:
	id_to_delete = st.number_input('ID：', min_value=-1, step=1)
with row[1]:
	if st.button('削除'):
		if id_to_delete >= 0:
			if 'delete_id' not in st.session_state:
				detete_confirmation(id_to_delete)
		elif id_to_delete < 0:
			detele_success = False

if 'delete_id' in st.session_state:
	# check if the id exists
	cur.execute('SELECT COUNT(*) FROM entries WHERE id = ?', (st.session_state['delete_id'],))
	count = cur.fetchone()[0]
	if count == 0:
		st.error(f'ID {st.session_state["delete_id"]} の記録は存在しません。')
	else:
		# delete the entry
		cur.execute('DELETE FROM entries WHERE id = ?', (st.session_state['delete_id'],))
		conn.commit()
		st.success(f'ID {id_to_delete} の記録を削除しました。')
	del st.session_state['delete_id']

if not detele_success:
	st.error('IDは0以上の整数を入力してください。')

if st.button('ダミーデータ追加'):
	cur.execute("""
	INSERT INTO entries (date, transaction_type, category, note, payment_method, amount)
	VALUES ('2023-01-01', '支出', '食費', 'ランチ', 'クレジット', 10000)
	""")
	conn.commit()

st.subheader('記録一覧')
# すべての記録を取得して表示
cur.execute('SELECT * FROM entries')
# cur.fetchall()の結果をDataFrameに変換して表示する方法もある
df = pd.read_sql_query('SELECT * FROM entries', conn)

df.columns = ['ID', '日付', '収入/支出', 'カテゴリ', '内容', '支払方法', '金額']
# 金額列を通貨形式に変換
df['金額'] = df['金額'].apply(lambda x: f"¥{x:,}")

# 年月範囲
start_date = st.date_input('開始日')
end_date = st.date_input('終了日')
# if st.button('フィルタ適用'):
# 	if start_date > end_date:
# 		st.error('開始日は終了日より前の日付を選択してください。')
# 	else:
# 		df = df[(df["日付"] >= pd.to_datetime(start_date)) & (df["日付"] <= pd.to_datetime(end_date))]

# 収入/支出フィルタ
transaction_type = st.selectbox(
    "収支を選択",
    ["全て", "収入", "支出"]
)

# フィルタリング
if transaction_type != "全て":
    df = df[df["収入/支出"] == transaction_type]

st.dataframe(df, hide_index=True)

cur.close()
conn.close()
