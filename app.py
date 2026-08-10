from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return "🧠 Website Psikotes - Versi Testing Berhasil!"

if __name__ == '__main__':
    app.run(debug=True)