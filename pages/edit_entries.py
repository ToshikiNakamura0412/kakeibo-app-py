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

CONFIG_FILE_PATH = 'configs/config.json'
CUSTOM_CONFIG_FILE_PATH = 'configs/custom_config.json'
JSON_FILE_PATH = CUSTOM_CONFIG_FILE_PATH if utils.check_file_exists(CUSTOM_CONFIG_FILE_PATH) else CONFIG_FILE_PATH
with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
	config_df = pd.read_json(f)
	user_settings_df = config_df['configs']['user_settings']
	categories_df = config_df['configs']['categories']

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

selected_id = st.selectbox('ID：', df['id'].tolist())
selected_entry = df[df['id'] == selected_id].iloc[0]
mode_options = ['表示モード', '編集モード', '削除モード', 'インポート']
mode = st.segmented_control('mode：', mode_options, default=mode_options[0])
if mode == '編集モード':
	date = st.date_input('日付：', pd.to_datetime(selected_entry['date']))
	transaction_type = st.segmented_control('', ['収入', '支出'], default=selected_entry['transaction_type'])
	payment_method_options = ['現金']
	for i in range(int(user_settings_df['利用銀行数'])):
		payment_method_options.append(f"銀行{i+1}")
	for i in range(int(user_settings_df['利用クレジットカード数'])):
		payment_method_options.append(f"クレジット{i+1}")
	try:
		payment_method = st.segmented_control('', payment_method_options, default=selected_entry['payment_method'])
	except Exception as e:
		payment_method = st.segmented_control('', payment_method_options, default=payment_method_options[0])
	category_options = categories_df['income'] if transaction_type == '収入' else categories_df['expense']
	category_options = list(category_options)
	category = None
	try:
		category = st.pills('', category_options, default=selected_entry['category'])
	except Exception as e:
		category = st.pills('', category_options, default=category_options[0])
	row = st.columns(4)
	with row[0]:
		note = st.text_input('メモ：', selected_entry['note'])
	with row[1]:
		amount = st.number_input('金額：', min_value=0, value=int(selected_entry['amount']))

	row = st.columns(5, vertical_alignment='bottom')
	with row[0]:
		col_name = st.selectbox('項目：', ['date', 'transaction_type', 'category', 'note', 'payment_method', 'amount'])
	with row[1]:
		new_value = st.text_input('新しい値：')
	with row[2]:
		if st.button('更新'):
			database.update_entry(selected_id, col_name, new_value)
			st.session_state['update_success'] = True
			st.session_state['selected_id'] = selected_id
			st.rerun()


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

if mode == '削除モード':
	st.dataframe(selected_entry)
	if st.button('削除'):
		detete_confirmation(selected_id)

# インポート
if mode == 'インポート':
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

if mode == '表示モード':
	jp_col_label = config_models.ENTRY_LABELS_JP.to_list()
	jp_col_label.insert(0, 'ID')
	df.columns = jp_col_label
	# 金額列を通貨形式に変換
	df['金額'] = df['金額'].apply(lambda x: f"¥{x:,}")

	row = st.columns(3)
	with row[0]:
		# 年月範囲
		start_date = st.date_input('開始日')
	with row[1]:
		end_date = st.date_input('終了日')
		# if st.button('フィルタ適用'):
		# 	if start_date > end_date:
		# 		st.error('開始日は終了日より前の日付を選択してください。')
		# 	else:
		# 		df = df[(df["日付"] >= pd.to_datetime(start_date)) & (df["日付"] <= pd.to_datetime(end_date))]
	with row[2]:
		# 収入/支出フィルタ
		transaction_type = st.selectbox(
			"収支を選択",
			["全て", "収入", "支出"]
		)

	# フィルタリング
	if transaction_type != "全て":
		df = df[df["収入/支出"] == transaction_type]

	st.dataframe(df, hide_index=True)
