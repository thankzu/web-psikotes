from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import os
import io
from utils.scoring import *

app = Flask(__name__)
app.secret_key = 'rahasia12345'

# Konfigurasi database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "database", "psikotes.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

# ==================== MODEL ====================

class Pegawai(db.Model):
    __tablename__ = 'pegawai'
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    usia = db.Column(db.Integer)
    jenis_kelamin = db.Column(db.String(20))
    tanggal_tes = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    hasil_disc = db.relationship('HasilDISC', backref='pegawai', uselist=False)
    hasil_mbti = db.relationship('HasilMBTI', backref='pegawai', uselist=False)
    hasil_kmsp = db.relationship('HasilKMSP', backref='pegawai', uselist=False)

class HasilDISC(db.Model):
    __tablename__ = 'hasil_disc'
    id = db.Column(db.Integer, primary_key=True)
    pegawai_id = db.Column(db.Integer, db.ForeignKey('pegawai.id'))
    d = db.Column(db.Integer, default=0)
    i = db.Column(db.Integer, default=0)
    s = db.Column(db.Integer, default=0)
    c = db.Column(db.Integer, default=0)
    tipe_public = db.Column(db.String(50))
    tipe_private = db.Column(db.String(50))
    tipe_mirror = db.Column(db.String(50))
    tipe_gabungan = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class HasilMBTI(db.Model):
    __tablename__ = 'hasil_mbti'
    id = db.Column(db.Integer, primary_key=True)
    pegawai_id = db.Column(db.Integer, db.ForeignKey('pegawai.id'))
    e = db.Column(db.Integer, default=0)
    i = db.Column(db.Integer, default=0)
    s = db.Column(db.Integer, default=0)
    n = db.Column(db.Integer, default=0)
    t = db.Column(db.Integer, default=0)
    f = db.Column(db.Integer, default=0)
    j = db.Column(db.Integer, default=0)
    p = db.Column(db.Integer, default=0)
    tipe_mbti = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class HasilKMSP(db.Model):
    __tablename__ = 'hasil_kmsp'
    id = db.Column(db.Integer, primary_key=True)
    pegawai_id = db.Column(db.Integer, db.ForeignKey('pegawai.id'))
    skor_k = db.Column(db.Integer, default=0)
    skor_m = db.Column(db.Integer, default=0)
    skor_s = db.Column(db.Integer, default=0)
    skor_p = db.Column(db.Integer, default=0)
    temperamen = db.Column(db.String(10))
    nama_temperamen = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class JawabanDISC(db.Model):
    __tablename__ = 'jawaban_disc'
    id = db.Column(db.Integer, primary_key=True)
    pegawai_id = db.Column(db.Integer, db.ForeignKey('pegawai.id'))
    nomor = db.Column(db.Integer)
    pilihan_p = db.Column(db.Integer)
    pilihan_k = db.Column(db.Integer)

class JawabanMBTI(db.Model):
    __tablename__ = 'jawaban_mbti'
    id = db.Column(db.Integer, primary_key=True)
    pegawai_id = db.Column(db.Integer, db.ForeignKey('pegawai.id'))
    nomor = db.Column(db.Integer)
    pilihan = db.Column(db.String(1))

class JawabanKMSP(db.Model):
    __tablename__ = 'jawaban_kmsp'
    id = db.Column(db.Integer, primary_key=True)
    pegawai_id = db.Column(db.Integer, db.ForeignKey('pegawai.id'))
    pernyataan_id = db.Column(db.Integer)
    urutan = db.Column(db.Integer)

# ==================== AUTH ====================

class Admin(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    if user_id == 'admin':
        return Admin('admin')
    return None

# ==================== DATA SOAL ====================

DISC_SOAL = [
    {"nomor": 1, "pilihan": ["Gampangan, Mudah setuju", "Percaya, Mudah percaya pada orang", "Petualang, Mengambil resiko", "Toleran, Menghormati"]},
    {"nomor": 2, "pilihan": ["Hasil adalah penting", "Lakukan dengan benar, Akurasi penting", "Dibuat menyenangkan", "Mari kerjakan bersama"]},
    {"nomor": 3, "pilihan": ["Pendidikan, Kebudayaan", "Prestasi, Ganjaran", "Keselamatan, keamanan", "Sosial, Perkumpulan kelompok"]},
    {"nomor": 4, "pilihan": ["Lembut suara, Pendiam", "Optimistik, Visioner", "Pusat Perhatian, Suka gaul", "Pendamai, Membawa Harmoni"]},
    {"nomor": 5, "pilihan": ["Akan berjalan terus tanpa kontrol diri", "Akan membeli sesuai dorongan hati", "Akan menunggu, Tanpa tekanan", "Akan mengusahakan yang kuinginkan"]},
    {"nomor": 6, "pilihan": ["Memimpin, Pendekatan langsung", "Suka bergaul, Antusias", "Dapat diramal, Konsisten", "Waspada, Hati-hati"]},
    {"nomor": 7, "pilihan": ["Menyemangati orang", "Berusaha sempurna", "Bagian dari kelompok", "Ingin membuat tujuan"]},
    {"nomor": 8, "pilihan": ["Ramah, Mudah bergabung", "Unik, Bosan rutinitas", "Aktif mengubah sesuatu", "Ingin hal-hal yang pasti"]},
    {"nomor": 9, "pilihan": ["Tidak mudah dikalahkan", "Kerjakan sesuai perintah, Ikut pimpinan", "Mudah terangsang, Riang", "Ingin segalanya teratur, Rapi"]},
    {"nomor": 10, "pilihan": ["Menjadi frustrasi", "Menyimpan perasaan saya", "Menceritakan sisi saya", "Siap beroposisi"]},
    {"nomor": 11, "pilihan": ["Non-konfrontasi, Menyerah", "Dipenuhi hal detail", "Perubahan pada menit terakhir", "Menuntut, Kasar"]},
    {"nomor": 12, "pilihan": ["Saya akan pimpin mereka", "Saya akan melaksanakan", "Saya akan meyakinkan mereka", "Saya dapatkan fakta"]},
    {"nomor": 13, "pilihan": ["Hidup, Suka bicara", "Gerak cepat, Tekun", "Usaha menjaga keseimbangan", "Usaha mengikuti aturan"]},
    {"nomor": 14, "pilihan": ["Ingin kemajuan", "Puas dengan segalanya", "Terbuka memperlihatkan perasaan", "Rendah hati, Sederhana"]},
    {"nomor": 15, "pilihan": ["Memikirkan orang dahulu", "Kompetitif, Suka tantangan", "Optimis, Positif", "Pemikir logis, Sistematik"]},
    {"nomor": 16, "pilihan": ["Kelola waktu secara efisien", "Sering terburu-buru, Merasa tertekan", "Masalah sosial itu penting", "Suka selesaikan apa yang saya mulai"]},
    {"nomor": 17, "pilihan": ["Tenang, Pendiam", "Bahagia, Tanpa beban", "Menyenangkan, Baik hati", "Tak gentar, Berani"]},
    {"nomor": 18, "pilihan": ["Menyenangkan orang, Mudah setuju", "Tertawa lepas, Hidup", "Berani, Tak gentar", "Tenang, Pendiam"]},
    {"nomor": 19, "pilihan": ["Tolak perubahan mendadak", "Cenderung janji berlebihan", "Tarik diri di tengah tekanan", "Tidak takut bertempur"]},
    {"nomor": 20, "pilihan": ["Menggunakan waktu berkualitas dgn teman", "Rencanakan masa depan, Bersiap", "Bepergian demi petualangan baru", "Menerima ganjaran atas tujuan yg dicapai"]},
    {"nomor": 21, "pilihan": ["Ingin otoritas lebih", "Ingin kesempatan baru", "Menghindari konflik", "Ingin petunjuk yang jelas"]},
    {"nomor": 22, "pilihan": ["Penyemangat yang baik", "Pendengar yang baik", "Penganalisa yang baik", "Delegator yang baik"]},
    {"nomor": 23, "pilihan": ["Aturan perlu dipertanyakan", "Aturan membuat adil", "Aturan membuat bosan", "Aturan membuat aman"]},
    {"nomor": 24, "pilihan": ["Dapat diandalkan, Dapat dipercaya", "Kreatif, Unik", "Garis dasar, Orientasi hasil", "Jalankan standar yang tinggi, Akurat"]}
]

MBTI_SOAL = []
for i in range(1, 61):
    MBTI_SOAL.append({"nomor": i, "A": f"Pernyataan A untuk nomor {i}", "B": f"Pernyataan B untuk nomor {i}"})

KMSP_SOAL = []
for i in range(1, 9):
    KMSP_SOAL.append({"nomor": i, "pilihan": [f"Pilihan {j+1} untuk pernyataan {i}" for j in range(4)]})

# ==================== ROUTES ====================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'psikotes2026':
            user = Admin('admin')
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        return render_template('login.html', error='Username atau password salah!')
    return render_template('login.html')

@app.route('/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('index'))

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
        
        return redirect(url_for('mbti_form', pegawai_id=pegawai.id))
    return render_template('disc_form.html', soal=DISC_SOAL)

@app.route('/mbti')
def mbti_form():
    pegawai_id = request.args.get('pegawai_id')
    return render_template('mbti_form.html', pegawai_id=pegawai_id, soal=MBTI_SOAL)

@app.route('/kmsp')
def kmsp_form():
    pegawai_id = request.args.get('pegawai_id')
    return render_template('kmsp_form.html', pegawai_id=pegawai_id, soal=KMSP_SOAL)

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/admin')
@login_required
def admin_dashboard():
    pegawai_list = Pegawai.query.order_by(Pegawai.created_at.desc()).all()
    return render_template('admin_dashboard.html', pegawai_list=pegawai_list)

@app.route('/admin/<int:pegawai_id>')
@login_required
def admin_detail(pegawai_id):
    pegawai = Pegawai.query.get_or_404(pegawai_id)
    return render_template('admin_detail.html', pegawai=pegawai)

# ==================== RUN ====================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)