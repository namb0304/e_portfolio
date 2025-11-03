from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# ユーザーテーブル（学生と教員の両方）
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)  # ログインID
    password = db.Column(db.String(200), nullable=False)  # パスワード（ハッシュ化）
    name = db.Column(db.String(100), nullable=False)  # 実名
    role = db.Column(db.String(20), nullable=False)  # 'student' or 'teacher'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # リレーション
    records = db.relationship('AttendanceRecord', backref='student', lazy=True)
    projects = db.relationship('ProjectAssignment', backref='student', lazy=True)
    portfolios = db.relationship('Portfolio', backref='student', lazy=True)
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy=True)
    received_messages = db.relationship('Message', foreign_keys='Message.receiver_id', backref='receiver', lazy=True)

# 出席記録テーブル
class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_records'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # '出席', '欠席', '遅刻'
    note = db.Column(db.Text)  # メモ
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# 授業チャンネル書き込みテーブル
class ChannelPost(db.Model):
    __tablename__ = 'channel_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    channel_name = db.Column(db.String(100), nullable=False)  # 授業名
    content = db.Column(db.Text, nullable=False)  # 書き込み内容
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    student = db.relationship('User', backref='channel_posts')

# 未来創造PJ配属テーブル
class ProjectAssignment(db.Model):
    __tablename__ = 'project_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_name = db.Column(db.String(100), nullable=False)  # プロジェクト名
    role = db.Column(db.String(100))  # 役割
    description = db.Column(db.Text)  # 活動内容
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ポートフォリオ（作品）テーブル
class Portfolio(db.Model):
    __tablename__ = 'portfolios'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)  # 作品タイトル
    description = db.Column(db.Text)  # 説明
    portfolio_type = db.Column(db.String(20), nullable=False)  # 'file' or 'link'
    file_path = db.Column(db.String(300))  # ファイルの場合のパス
    external_url = db.Column(db.String(500))  # 外部リンクの場合のURL
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# メッセージテーブル
class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)  # 既読フラグ
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
