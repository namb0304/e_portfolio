from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, User, AttendanceRecord, ChannelPost, ProjectAssignment, Portfolio, Message
from config import Config
from datetime import datetime, date
import os

app = Flask(__name__)
app.config.from_object(Config)

# データベース初期化
db.init_app(app)

# ログイン管理
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ファイルの拡張子チェック
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# ============================================
# 認証関連
# ============================================

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'student':
            return redirect(url_for('student_dashboard'))
        else:
            return redirect(url_for('teacher_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('ログインしました', 'success')
            return redirect(url_for('index'))
        else:
            flash('ユーザー名またはパスワードが間違っています', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('ログアウトしました', 'success')
    return redirect(url_for('login'))

# ============================================
# 学生用ページ
# ============================================

@app.route('/student/dashboard')
@login_required
def student_dashboard():
    if current_user.role != 'student':
        flash('学生としてログインしてください', 'error')
        return redirect(url_for('index'))
    
    # 最近の出席記録
    recent_attendance = AttendanceRecord.query.filter_by(
        student_id=current_user.id
    ).order_by(AttendanceRecord.date.desc()).limit(5).all()
    
    # プロジェクト配属
    projects = ProjectAssignment.query.filter_by(
        student_id=current_user.id
    ).all()
    
    # 未読メッセージ数
    unread_count = Message.query.filter_by(
        receiver_id=current_user.id,
        is_read=False
    ).count()
    
    return render_template('student/dashboard.html',
                         attendance=recent_attendance,
                         projects=projects,
                         unread_count=unread_count)

@app.route('/student/attendance', methods=['GET', 'POST'])
@login_required
def student_attendance():
    if current_user.role != 'student':
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        date_str = request.form.get('date')
        status = request.form.get('status')
        note = request.form.get('note')
        
        attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        record = AttendanceRecord(
            student_id=current_user.id,
            date=attendance_date,
            status=status,
            note=note
        )
        db.session.add(record)
        db.session.commit()
        
        flash('出席記録を登録しました', 'success')
        return redirect(url_for('student_dashboard'))
    
    return render_template('student/dashboard.html')

@app.route('/student/channel_post', methods=['POST'])
@login_required
def student_channel_post():
    if current_user.role != 'student':
        return redirect(url_for('index'))
    
    channel_name = request.form.get('channel_name')
    content = request.form.get('content')
    
    post = ChannelPost(
        student_id=current_user.id,
        channel_name=channel_name,
        content=content
    )
    db.session.add(post)
    db.session.commit()
    
    flash('投稿しました', 'success')
    return redirect(url_for('student_dashboard'))

@app.route('/student/portfolio', methods=['GET', 'POST'])
@login_required
def student_portfolio():
    if current_user.role != 'student':
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        portfolio_type = request.form.get('type')
        
        portfolio = Portfolio(
            student_id=current_user.id,
            title=title,
            description=description,
            portfolio_type=portfolio_type
        )
        
        if portfolio_type == 'file':
            if 'file' not in request.files:
                flash('ファイルが選択されていません', 'error')
                return redirect(request.url)
            
            file = request.files['file']
            if file.filename == '':
                flash('ファイルが選択されていません', 'error')
                return redirect(request.url)
            
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # ユーザーIDを含めてファイル名を一意にする
                unique_filename = f"{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(filepath)
                portfolio.file_path = unique_filename
            else:
                flash('許可されていないファイル形式です', 'error')
                return redirect(request.url)
        
        elif portfolio_type == 'link':
            external_url = request.form.get('external_url')
            portfolio.external_url = external_url
        
        db.session.add(portfolio)
        db.session.commit()
        
        flash('ポートフォリオを登録しました', 'success')
        return redirect(url_for('student_portfolio'))
    
    # 自分のポートフォリオ一覧
    portfolios = Portfolio.query.filter_by(
        student_id=current_user.id
    ).order_by(Portfolio.created_at.desc()).all()
    
    return render_template('student/portfolio.html', portfolios=portfolios)

@app.route('/student/chat')
@login_required
def student_chat():
    if current_user.role != 'student':
        return redirect(url_for('index'))
    
    # 教員一覧
    teachers = User.query.filter_by(role='teacher').all()
    
    # 選択された教員
    teacher_id = request.args.get('teacher_id', type=int)
    messages = []
    selected_teacher = None
    
    if teacher_id:
        selected_teacher = User.query.get(teacher_id)
        messages = Message.query.filter(
            db.or_(
                db.and_(Message.sender_id == current_user.id, Message.receiver_id == teacher_id),
                db.and_(Message.sender_id == teacher_id, Message.receiver_id == current_user.id)
            )
        ).order_by(Message.created_at).all()
        
        # 未読メッセージを既読にする
        Message.query.filter_by(
            sender_id=teacher_id,
            receiver_id=current_user.id,
            is_read=False
        ).update({Message.is_read: True})
        db.session.commit()
    
    return render_template('student/chat.html',
                         teachers=teachers,
                         messages=messages,
                         selected_teacher=selected_teacher)

@app.route('/student/send_message', methods=['POST'])
@login_required
def student_send_message():
    if current_user.role != 'student':
        return redirect(url_for('index'))
    
    teacher_id = request.form.get('teacher_id', type=int)
    content = request.form.get('content')
    
    if not content:
        flash('メッセージを入力してください', 'error')
        return redirect(url_for('student_chat', teacher_id=teacher_id))
    
    message = Message(
        sender_id=current_user.id,
        receiver_id=teacher_id,
        content=content
    )
    db.session.add(message)
    db.session.commit()
    
    return redirect(url_for('student_chat', teacher_id=teacher_id))

# ============================================
# 教員用ページ
# ============================================

@app.route('/teacher/dashboard')
@login_required
def teacher_dashboard():
    if current_user.role != 'teacher':
        flash('教員としてログインしてください', 'error')
        return redirect(url_for('index'))
    
    # 学生一覧
    students = User.query.filter_by(role='student').all()
    
    # 未読メッセージ数
    unread_count = Message.query.filter_by(
        receiver_id=current_user.id,
        is_read=False
    ).count()
    
    return render_template('teacher/dashboard.html',
                         students=students,
                         unread_count=unread_count)

@app.route('/teacher/student/<int:student_id>')
@login_required
def teacher_student_detail(student_id):
    if current_user.role != 'teacher':
        return redirect(url_for('index'))
    
    student = User.query.get_or_404(student_id)
    
    # 出席記録
    attendance = AttendanceRecord.query.filter_by(
        student_id=student_id
    ).order_by(AttendanceRecord.date.desc()).all()
    
    # チャンネル投稿
    posts = ChannelPost.query.filter_by(
        student_id=student_id
    ).order_by(ChannelPost.posted_at.desc()).all()
    
    # プロジェクト配属
    projects = ProjectAssignment.query.filter_by(
        student_id=student_id
    ).all()
    
    # ポートフォリオ
    portfolios = Portfolio.query.filter_by(
        student_id=student_id
    ).order_by(Portfolio.created_at.desc()).all()
    
    return render_template('teacher/student_detail.html',
                         student=student,
                         attendance=attendance,
                         posts=posts,
                         projects=projects,
                         portfolios=portfolios)

@app.route('/teacher/chat')
@login_required
def teacher_chat():
    if current_user.role != 'teacher':
        return redirect(url_for('index'))
    
    # 学生一覧
    students = User.query.filter_by(role='student').all()
    
    # 選択された学生
    student_id = request.args.get('student_id', type=int)
    messages = []
    selected_student = None
    
    if student_id:
        selected_student = User.query.get(student_id)
        messages = Message.query.filter(
            db.or_(
                db.and_(Message.sender_id == current_user.id, Message.receiver_id == student_id),
                db.and_(Message.sender_id == student_id, Message.receiver_id == current_user.id)
            )
        ).order_by(Message.created_at).all()
        
        # 未読メッセージを既読にする
        Message.query.filter_by(
            sender_id=student_id,
            receiver_id=current_user.id,
            is_read=False
        ).update({Message.is_read: True})
        db.session.commit()
    
    return render_template('teacher/chat.html',
                         students=students,
                         messages=messages,
                         selected_student=selected_student)

@app.route('/teacher/send_message', methods=['POST'])
@login_required
def teacher_send_message():
    if current_user.role != 'teacher':
        return redirect(url_for('index'))
    
    student_id = request.form.get('student_id', type=int)
    content = request.form.get('content')
    
    if not content:
        flash('メッセージを入力してください', 'error')
        return redirect(url_for('teacher_chat', student_id=student_id))
    
    message = Message(
        sender_id=current_user.id,
        receiver_id=student_id,
        content=content
    )
    db.session.add(message)
    db.session.commit()
    
    return redirect(url_for('teacher_chat', student_id=student_id))

# ============================================
# ファイル配信
# ============================================

@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ============================================
# データベース初期化＆テストデータ
# ============================================

@app.route('/init_db')
def init_db():
    with app.app_context():
        db.create_all()
        
        # テストユーザーが存在しない場合のみ作成
        if not User.query.filter_by(username='student1').first():
            # 学生ユーザー
            student = User(
                username='student1',
                password=generate_password_hash('password'),
                name='田中太郎',
                role='student'
            )
            db.session.add(student)
            
            # 教員ユーザー
            teacher = User(
                username='teacher1',
                password=generate_password_hash('password'),
                name='山田先生',
                role='teacher'
            )
            db.session.add(teacher)
            
            db.session.commit()
            
            return 'データベースを初期化しました。<br>学生: username=student1, password=password<br>教員: username=teacher1, password=password<br><a href="/login">ログインページへ</a>'
        else:
            return 'データベースは既に初期化されています。<a href="/login">ログインページへ</a>'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
