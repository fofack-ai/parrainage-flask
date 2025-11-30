import os
import sqlite3
import bcrypt
from flask import Flask, request, jsonify, session, render_template
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
CORS(app)

# Configuration SQLite (plus simple pour commencer)
def get_db_connection():
    conn = sqlite3.connect('parrainage.db')
    conn.row_factory = sqlite3.Row
    return conn

# Fonction d'initialisation
def init_database():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Table utilisateurs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS utilisateurs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                matricule TEXT UNIQUE NOT NULL,
                mot_de_passe TEXT NOT NULL,
                telephone TEXT,
                photo TEXT DEFAULT 'default.jpg',
                serie TEXT CHECK(serie IN ('TI-RSI', 'TI-PAM')) NOT NULL,
                niveau TEXT CHECK(niveau IN ('1', '2')) NOT NULL,
                est_disponible BOOLEAN DEFAULT TRUE,
                date_inscription DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table parrainages
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS parrainages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_filleul INTEGER UNIQUE,
                id_parrain INTEGER UNIQUE,
                date_parrainage DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_filleul) REFERENCES utilisateurs(id) ON DELETE CASCADE,
                FOREIGN KEY (id_parrain) REFERENCES utilisateurs(id) ON DELETE CASCADE
            )
        """)
        
        # Vérifier si des parrains existent déjà
        cursor.execute("SELECT COUNT(*) as count FROM utilisateurs WHERE niveau = '2'")
        result = cursor.fetchone()
        
        if result[0] == 0:
            hashed_password = bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Insérer parrains initiaux
            parrains = [
                ('Jean Koffi', 'TI-RSI2001', hashed_password, '+2250700000001', 'TI-RSI', '2', 1),
                ('Marie Traoré', 'TI-RSI2002', hashed_password, '+2250700000002', 'TI-RSI', '2', 1),
                ('Pierre Kouadio', 'TI-RSI2003', hashed_password, '+2250700000003', 'TI-RSI', '2', 1),
                ('Alice Koné', 'TI-PAM2001', hashed_password, '+2250700000004', 'TI-PAM', '2', 1),
                ('Paul NGuessan', 'TI-PAM2002', hashed_password, '+2250700000005', 'TI-PAM', '2', 1),
                ('Sophie Bamba', 'TI-PAM2003', hashed_password, '+2250700000006', 'TI-PAM', '2', 1)
            ]
            
            cursor.executemany("""
                INSERT INTO utilisateurs 
                (nom, matricule, mot_de_passe, telephone, serie, niveau, est_disponible) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, parrains)
        
        conn.commit()
        print("✅ Base de données SQLite initialisée avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur d'initialisation: {e}")
    finally:
        conn.close()

# Initialisation
init_database()

# Routes principales
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Route de test
@app.route('/api/test-db')
def test_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM utilisateurs")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return jsonify({"status": "success", "users_count": result[0]})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)