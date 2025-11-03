# eポートフォリオシステム（カルテシステム）

## 概要
学生の日々の活動記録、作品管理、教員とのコミュニケーションを一元管理するFlaskベースのWebアプリケーション

## 機能
### 学生機能
- 出席記録の登録
- 授業チャンネルへの書き込み
- 作品（ポートフォリオ）の登録（ファイル/リンク）
- 教員とのメッセージ機能

### 教員機能
- 学生一覧の閲覧
- 学生の詳細情報閲覧（出席、投稿、プロジェクト、作品）
- 学生とのメッセージ機能

## セットアップ手順

### 1. 必要なライブラリのインストール
```bash
pip install -r requirements.txt --break-system-packages
```

### 2. データベースの初期化
ブラウザで以下のURLにアクセス：
```
http://localhost:5000/init_db
```
これでデータベースとテストユーザーが作成されます。

### 3. アプリケーションの起動
```bash
python app.py
```

### 4. ブラウザでアクセス
```
http://localhost:5000
```

## テストアカウント
### 学生アカウント
- ユーザー名: `student1`
- パスワード: `password`

### 教員アカウント
- ユーザー名: `teacher1`
- パスワード: `password`

## フォルダ構造
```
e_portfolio/
├── app.py                 # メインアプリケーション
├── config.py              # 設定ファイル
├── models.py              # データベースモデル定義
├── requirements.txt       # 必要なライブラリ
├── README.md             # このファイル
├── static/               # 静的ファイル
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── uploads/          # アップロードファイル保存先
├── templates/            # HTMLテンプレート
│   ├── base.html
│   ├── login.html
│   ├── student/
│   │   ├── dashboard.html
│   │   ├── portfolio.html
│   │   └── chat.html
│   └── teacher/
│       ├── dashboard.html
│       ├── student_detail.html
│       └── chat.html
└── instance/            # データベース保存先
    └── database.db
```

## 使い方

### 学生として
1. ログイン後、ダッシュボードで出席記録や授業チャンネルへの投稿ができます
2. 「ポートフォリオ」ページで作品を登録（ファイルアップロードまたは外部リンク）
3. 「メッセージ」ページで教員とチャット

### 教員として
1. ログイン後、学生一覧が表示されます
2. 学生名をクリックすると詳細情報（出席、投稿、プロジェクト、作品）を閲覧
3. 「メッセージ」ページで学生とチャット

## 技術スタック
- **バックエンド**: Flask
- **データベース**: SQLite
- **フロントエンド**: HTML, CSS, JavaScript, Bootstrap 5
- **認証**: Flask-Login

## 注意事項
- これは課題用の開発環境です。本番環境では以下を変更してください：
  - SECRET_KEYを安全なものに変更
  - DEBUG=Falseに設定
  - より強固な認証システムの導入
  - ファイルアップロードのセキュリティ強化
