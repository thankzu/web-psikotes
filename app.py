from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'rahasia12345'

# Database SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "database", "psikotes.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ============ MODEL DATABASE ============
class Pegawai(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    usia = db.Column(db.Integer)
    jenis_kelamin = db.Column(db.String(20))
    tanggal_tes = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ============ ROUTES ============
@app.route('/')
def index():
    return '''
    <h1>🧠 Psikotes Online</h1>
    <p>Halo! Website ini sedang dalam pengembangan.</p>
    <p>Coba buka: <a href="/disc">/disc</a></p>
    '''

@app.route('/disc')
def disc():
    return '''
    <h1>📊 Tes DISC</h1>
    <p>Ini adalah halaman tes DISC.</p>
    <p>Silakan isi data diri:</p>
    <form method="POST" action="/disc">
        <input type="text" name="nama" placeholder="Nama" required>
        <button type="submit">Simpan</button>
    </form>
    '''

@app.route('/disc', methods=['POST'])
def disc_save():
    nama = request.form.get('nama')
    
    pegawai = Pegawai(nama=nama, tanggal_tes=datetime.now().strftime('%Y-%m-%d'))
    db.session.add(pegawai)
    db.session.commit()
    
    return f'''
    <h1>✅ Berhasil!</h1>
    <p>Halo {nama}, data sudah disimpan.</p>
    <p>ID Pegawai: {pegawai.id}</p>
    <a href="/">Kembali ke Beranda</a>
    '''

# ============ JALANKAN ============
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)