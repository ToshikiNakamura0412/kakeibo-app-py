# kakeibo-app-py

[![lint](https://github.com/ToshikiNakamura0412/kakeibo-app-py/actions/workflows/lint.yml/badge.svg)](https://github.com/ToshikiNakamura0412/kakeibo-app-py/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

![スクリーンショット1](https://github.com/ToshikiNakamura0412/kakeibo-app-py/wiki/images/screenshot1.png)
[スクリーンショット](#スクリーンショット)

## 概要
kakeibo-app-pyは、Pythonで構築された個人向け財務管理アプリケーションです。

主に以下の機能を提供します。
- 収入と支出の追跡
- カテゴリー別集計
- グラフや表による可視化
- クレジット引き落とし自動適応
- スマホからのアクセス対応

無料で長期利用したい個人ユーザーに最適です。（他のサービスのデータを長期保存したい場合など）

## インストール方法
1. クローン
    ```bash
    git clone https://github.com/ToshikiNakamura0412/kakeibo-app-py.git
    ```
2. 依存関係のインストール
    ```bash
    cd kakeibo-app-py
    pip install -r requirements.txt
    ```
3. 起動
    ```bash
    cd kakeibo-app-py
    streamlit run app.py
    ```
    - 画面が自動で立ち上がります
    - ターミナルに表示されるURLにはスマホからもアクセス可能です

## 設定/DBファイルについて
- `data/my_entries.db` : 家計簿データを保存するSQLiteデータベースファイル
- `configs/custom_config.json` : アプリケーションの設定を保存するJSONファイル

自分のファイルを使いたい場合は、上記のパスにシンボリックリンクを作成してください。
```bash
ln -s /path/to/your/my_entries.db ./kakeibo-app-py/data/my_entries.db
ln -s /path/to/your/custom_config.json ./kakeibo-app-py/configs/custom_config.json
```

## スクリーンショット
![スクリーンショット2](https://github.com/ToshikiNakamura0412/kakeibo-app-py/wiki/images/screenshot2.png)
![スクリーンショット3](https://github.com/ToshikiNakamura0412/kakeibo-app-py/wiki/images/screenshot3.png)
![スクリーンショット4](https://github.com/ToshikiNakamura0412/kakeibo-app-py/wiki/images/screenshot4.png)
![スクリーンショット5](https://github.com/ToshikiNakamura0412/kakeibo-app-py/wiki/images/screenshot5.png)
![スクリーンショット6](https://github.com/ToshikiNakamura0412/kakeibo-app-py/wiki/images/screenshot6.png)
![スクリーンショット7](https://github.com/ToshikiNakamura0412/kakeibo-app-py/wiki/images/screenshot7.png)
