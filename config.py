import os

# プロジェクトのルートディレクトリを取得
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # セキュリティキー（本番環境では環境変数から取得）
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # データベース設定
    # 環境変数DATABASE_URLがあればそれを使用（Render本番環境）
    # なければSQLiteを使用（ローカル開発環境）
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if DATABASE_URL:
        # RenderのPostgreSQLは "postgres://" で始まるが、SQLAlchemyは "postgresql://" が必要
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # ローカル開発環境用（SQLite）
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'instance', 'database.db')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # ファイルアップロード設定
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB制限
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'zip', 'mp4'}