import pandas as pd
import streamlit as st

from kakeibo.common import utils, config_models
from kakeibo.model import database

utils.set_page_config()
utils.rendar_sidebar()
utils.rendar_home_button()

st.title(":material/Edit: 編集画面")

database.create_table()
# すべての記録を取得して表示
df = database.fetch_all_entries()

@st.dialog(title='削除確認')
def detete_confirmation(id_to_delete):
	st.write('本当に削除しますか？')
	if st.button('はい'):
		database.delete_entry(id_to_delete)
		st.session_state['delete_success'] = id_to_delete
		st.session_state['selected_id'] = id_to_delete
		st.rerun()
	if st.button('いいえ'):
		st.rerun()

# update
update_success = True if 'update_success' in st.session_state else False
delete_success = True if 'delete_success' in st.session_state else False
if update_success and st.session_state['selected_id']:
	st.success(f'ID {st.session_state['selected_id']} の記録を更新しました。')
	del st.session_state['update_success']
if delete_success and st.session_state['selected_id']:
	st.success(f'ID {st.session_state['selected_id']} の記録を削除しました。')
	del st.session_state['delete_success']
if 'selected_id' in st.session_state:
	del st.session_state['selected_id']

row = st.columns(5, vertical_alignment='bottom')
with row[0]:
	selected_id = st.selectbox('ID：', df['id'].tolist())
with row[1]:
	col_name = st.selectbox('項目：', ['date', 'transaction_type', 'category', 'note', 'payment_method', 'amount'])
with row[2]:
	new_value = st.text_input('新しい値：')
with row[3]:
	if st.button('更新'):
		database.update_entry(selected_id, col_name, new_value)
		st.session_state['update_success'] = True
		st.session_state['selected_id'] = selected_id
		st.rerun()
with row[4]:
	if st.button('削除'):
		detete_confirmation(selected_id)


# if st.button('ダミーデータ追加'):
# 	dummy_entry = config_models.Entry(
# 		'2023-01-01',
# 		'支出',
# 		'食費',
# 		'ランチ',
# 		'クレジット',
# 		'1000'
# 	)
# 	database.add_entry(dummy_entry)

# インポート
uploaded_file = st.file_uploader("**CSVファイルをアップロード**", type=["csv"])
temp_df = pd.DataFrame(columns=config_models.ENTRY_LABELS_JP.to_list())
temp_df.loc[0] = [
	'2023-01-01',  # 日付
	'支出',        # 収入/支出
	'食費',        # カテゴリ
	'ランチ',      # メモ
	'クレジット',  # 支払い方法
	'1000'        # 金額
]
temp_csv = temp_df.to_csv(index=False).encode('utf-8-sig')
st.download_button(
	label='Download CSV Template',
	data=temp_csv,
	file_name='kakeibo_template.csv',
	mime='text/csv',
	icon=":material/download:",
)

st.subheader('記録一覧')

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
