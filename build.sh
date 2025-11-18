#!/usr/bin/env bash
# exit on error
set -o errexit

# パッケージのインストール
pip install --upgrade pip
pip install -r requirements.txt

# データベースのマイグレーション（テーブル作成）
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('Database tables created')"