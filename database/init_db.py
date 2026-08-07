import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'psikotes.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pegawai (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            usia INTEGER,
            jenis_kelamin TEXT,
            tanggal_tes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database berhasil dibuat!")

if __name__ == '__main__':
    init_db()