from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import os
import io

app = Flask(__name__)
app.secret_key = 'rahasia12345'

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "database", "psikotes.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

class Pegawai(db.Model):
    __tablename__ = 'pegawai'
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    usia = db.Column(db.Integer)
    jenis_kelamin = db.Column(db.String(20))
    tanggal_tes = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Admin(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    if user_id == 'admin':
        return Admin('admin')
    return None

@app.route('/')
def index():
    return '<h1>🧠 Psikotes Online</h1><p>Silakan <a href="/disc">isi tes DISC</a></p>'

@app.route('/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'psikotes2026':
            from flask_login import login_user
            user = Admin('admin')
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        return '<h1>Login Gagal!</h1><a href="/login">Coba lagi</a>'
    return '''
    <h1>🔐 Login Admin</h1>
    <form method="POST">
        <input type="text" name="username" placeholder="Username" required><br>
        <input type="password" name="password" placeholder="Password" required><br>
        <button type="submit">Login</button>
    </form>
    '''

@app.route('/logout')
def admin_logout():
    from flask_login import logout_user
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin')
def admin_dashboard():
    from flask_login import login_required, current_user
    @login_required
    def protected():
        pegawai_list = Pegawai.query.order_by(Pegawai.created_at.desc()).all()
        html = '<h1>📊 Dashboard Admin</h1><table border="1"><tr><th>ID</th><th>Nama</th><th>Usia</th><th>JK</th><th>Tanggal</th></tr>'
        for p in pegawai_list:
            html += f'<tr><td>{p.id}</td><td>{p.nama}</td><td>{p.usia or "-"}</td><td>{p.jenis_kelamin or "-"}</td><td>{p.tanggal_tes or "-"}</td></tr>'
        html += '</table><a href="/logout">Logout</a>'
        return html
    return protected()

@app.route('/disc', methods=['GET', 'POST'])
def disc_form():
    if request.method == 'POST':
        nama = request.form.get('nama')
        usia = request.form.get('usia', 0)
        jenis_kelamin = request.form.get('jenis_kelamin')
        pegawai = Pegawai(
            nama=nama,
            usia=usia,
            jenis_kelamin=jenis_kelamin,
            tanggal_tes=datetime.now().strftime('%A, %d %B %Y')
        )
        db.session.add(pegawai)
        db.session.commit()
        return f'<h1>✅ Berhasil!</h1><p>Terima kasih {nama}, data sudah disimpan.</p><a href="/">Kembali</a>'
    
    html = '''
    <h1>📊 Tes DISC</h1>
    <form method="POST">
        <input type="text" name="nama" placeholder="Nama" required><br>
        <input type="number" name="usia" placeholder="Usia"><br>
        <select name="jenis_kelamin">
            <option value="">Pilih...</option>
            <option value="Laki-laki">Laki-laki</option>
            <option value="Perempuan">Perempuan</option>
        </select><br><br>
        <button type="submit">Submit</button>
    </form>
    '''
    return html

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)