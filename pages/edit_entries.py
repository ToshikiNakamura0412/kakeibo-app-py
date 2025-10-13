import pandas as pd
import streamlit as st

from kakeibo.common import utils, config_models
from kakeibo.model import database

utils.set_page_config()
utils.rendar_sidebar()
utils.rendar_home_button()

st.title(":material/Edit: 編集画面")

database.create_table()

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
		database.update_entry(id_to_update, col_name, new_value)
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
	if not database.check_entry_exists(st.session_state['delete_id']):
		st.error(f'ID {st.session_state["delete_id"]} の記録は存在しません。')
	else:
		# delete the entry
		database.delete_entry(st.session_state['delete_id'])
		st.success(f'ID {id_to_delete} の記録を削除しました。')
	del st.session_state['delete_id']

if not detele_success:
	st.error('IDは0以上の整数を入力してください。')

if st.button('ダミーデータ追加'):
	dummy_entry = config_models.Entry(
		'2023-01-01',
		'支出',
		'食費',
		'ランチ',
		'クレジット',
		'1000'
	)
	database.add_entry(dummy_entry)

st.subheader('記録一覧')
# すべての記録を取得して表示
df = database.fetch_all_entries()

jp_col_label = config_models.ENTRY_LABELS_JP.to_list()
jp_col_label.insert(0, 'ID')
df.columns = jp_col_label
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
