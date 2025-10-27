import pandas as pd
import streamlit as st
from copy import deepcopy

from kakeibo.common import utils, config_models, ui_components, config_manager
from kakeibo.model import database

utils.set_page_config()
utils.rendar_sidebar()
utils.rendar_home_button()

st.title(":material/Edit: 編集画面")

database.create_table()
# すべての記録を取得して表示
df = database.fetch_all_entries()

config_manger = config_manager.ConfigManager()
user_settings_df = config_manger.user_settings_df
categories_df = config_manger.categories_df

@st.dialog(title='削除確認')
def delete_confirmation(id_to_delete):
	st.write('本当に削除しますか？')
	if st.button('はい'):
		database.delete_entry(id_to_delete)
		st.session_state['delete_success'] = id_to_delete
		st.session_state['selected_id'] = id_to_delete
		st.rerun()
	if st.button('いいえ'):
		st.rerun()

# notice
if st.session_state.get('update_success') and st.session_state.get('selected_id'):
	st.success(f'ID {st.session_state['selected_id']} の記録を更新しました。')
	del st.session_state['update_success']
	del st.session_state['selected_id']
elif st.session_state.get('delete_success') and st.session_state.get('selected_id'):
	st.success(f'ID {st.session_state['selected_id']} の記録を削除しました。')
	del st.session_state['delete_success']
	del st.session_state['selected_id']

# id setting
row = st.columns([2, 1, 1, 11], vertical_alignment='bottom')
with row[0]:
	# ID選択
	if st.session_state.get('selected_id'):
		current_index = df.index[df['id'] == st.session_state['selected_id']][0]
		selected_id = st.selectbox('ID：', df['id'].tolist(), index=int(current_index))
	else:
		selected_id = st.selectbox('ID：', df['id'].tolist())
with row[1]:
	if st.button('', icon=':material/chevron_left:'):
		if len(df) != 0:
			current_index = df.index[df['id'] == selected_id][0]
			if 0 < current_index:
				st.session_state['selected_id'] = df.iloc[current_index - 1]['id']
				st.rerun()
with row[2]:
	if st.button('', icon=':material/chevron_right:'):
		if len(df) != 0:
			current_index = df.index[df['id'] == selected_id][0]
			if current_index < len(df) - 1:
				st.session_state['selected_id'] = df.iloc[current_index + 1]['id']
				st.rerun()
selected_entry = df[df['id'] == selected_id].iloc[0]
mode_options = ['表示モード', '編集モード', '削除モード']
mode = st.segmented_control('mode：', mode_options, default=mode_options[0])

# mode
if mode == '表示モード':
	jp_col_label = config_models.ENTRY_LABELS_JP.to_list()
	jp_col_label.insert(0, 'ID')
	selected_entry_for_display = deepcopy(selected_entry)
	selected_entry_for_display = pd.DataFrame(selected_entry_for_display)
	selected_entry_for_display.columns = ['データ']
	selected_entry_for_display.index = jp_col_label
	st.dataframe(selected_entry_for_display)

	df.columns = jp_col_label
	# 金額列を通貨形式に変換
	df['金額'] = df['金額'].apply(lambda x: f"¥{x:,}")

	row = st.columns(3)
	with row[0]:
		# 年月範囲
		start_date = st.date_input('開始日')
	with row[1]:
		end_date = st.date_input('終了日')
	with row[2]:
		# 収入/支出フィルタ
		transaction_type = st.selectbox(
			"収支を選択",
			["全て", "収入", "支出"]
		)

	# フィルタリング
	if transaction_type != "全て":
		df = df[df["収入/支出"] == transaction_type]
	df = df[(pd.to_datetime(df['日付']) >= pd.to_datetime(start_date)) & (pd.to_datetime(df['日付']) <= pd.to_datetime(end_date))]
	st.dataframe(df, hide_index=True)
elif mode == '編集モード':
	ui_components.render_input_form(selected_entry, selected_id, update_button_label='更新')
elif mode == '削除モード':
	jp_col_label = config_models.ENTRY_LABELS_JP.to_list()
	jp_col_label.insert(0, 'ID')
	selected_entry_for_display = deepcopy(selected_entry)
	selected_entry_for_display = pd.DataFrame(selected_entry_for_display)
	selected_entry_for_display.columns = ['データ']
	selected_entry_for_display.index = jp_col_label
	st.dataframe(selected_entry_for_display)
	if st.button('削除'):
		delete_confirmation(selected_id)
