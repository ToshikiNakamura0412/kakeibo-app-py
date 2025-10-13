import pandas as pd
import sqlite3

from kakeibo.common import config_models

def execute_commit(sql, db_path = 'data/entries.db'):
	conn = sqlite3.connect(db_path)
	cursor = conn.cursor()

	try:
		cursor.execute(sql)
		conn.commit()
	except Exception as e:
		print(f"Error: {e}")
	finally:
		cursor.close()
		conn.close()

def create_table():
	labels = config_models.ENTRY_LABELS_EN
	sql = f"""
		CREATE TABLE IF NOT EXISTS entries (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			{labels.date} TEXT NOT NULL,
			{labels.transaction_type} TEXT NOT NULL,
			{labels.category} TEXT NOT NULL,
			{labels.note} TEXT,
			{labels.payment_method} TEXT,
			{labels.amount} INTEGER NOT NULL
		)
	"""
	execute_commit(sql)

def add_entry(entry):
	labels = config_models.ENTRY_LABELS_EN
	sql = f"""
		INSERT INTO entries (
			{labels.date},
			{labels.transaction_type},
			{labels.category},
			{labels.note},
			{labels.payment_method},
			{labels.amount}
		)
		VALUES (
			'{entry.date}',
			'{entry.transaction_type}',
			'{entry.category}',
			'{entry.note}',
			'{entry.payment_method}',
			{entry.amount}
		)
	"""
	execute_commit(sql)

def delete_entry(entry_id):
	sql = f"DELETE FROM entries WHERE id = {entry_id}"
	execute_commit(sql)

def update_entry(id, col_name, value):
	sql = f"UPDATE entries SET {col_name} = '{value}' WHERE id = {id}"
	execute_commit(sql)

def check_entry_exists(id, db_path = 'data/entries.db'):
	conn = sqlite3.connect(db_path)
	cursor = conn.cursor()

	count = 0
	try:
		cursor.execute('SELECT COUNT(*) FROM entries WHERE id = ?', (id,))
		count = cursor.fetchone()[0]
	except Exception as e:
		print(f"Error: {e}")
	finally:
		cursor.close()
		conn.close()

	return count > 0

def fetch_all_entries(db_path = 'data/entries.db'):
	conn = sqlite3.connect(db_path)

	entries = pd.DataFrame()
	try:
		entries = pd.read_sql_query('SELECT * FROM entries', conn)
	except Exception as e:
		print(f"Error: {e}")
	finally:
		conn.close()

	return entries
