import os
import psycopg2
import bcrypt
from flask import Flask, request, jsonify, session, render_template
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
CORS(app)

# Configuration PostgreSQL pour Render
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.environ.get('PGHOST'),
            database=os.environ.get('PGDATABASE'),
            user=os.environ.get('PGUSER'),
            password=os.environ.get('PGPASSWORD'),
            port=os.environ.get('PGPORT', 5432)
        )
        return conn
    except Exception as e:
        print(f"❌ Impossible de se connecter à la base: {e}")
        return None

# Fonction d'initialisation pour PostgreSQL
def init_database():
    conn = get_db_connection()
    if conn is None:
        print("⚠️ Base de données non disponible - initialisation ignorée")
        return
    
    try:
        cursor = conn.cursor()
        
        # Table utilisateurs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS utilisateurs (
                id SERIAL PRIMARY KEY,
                nom VARCHAR(100) NOT NULL,
                matricule VARCHAR(50) UNIQUE NOT NULL,
                mot_de_passe VARCHAR(255) NOT NULL,
                telephone VARCHAR(20),
                photo VARCHAR(255) DEFAULT 'default.jpg',
                serie VARCHAR(10) CHECK (serie IN ('TI-RSI', 'TI-PAM')) NOT NULL,
                niveau VARCHAR(1) CHECK (niveau IN ('1', '2')) NOT NULL,
                est_disponible BOOLEAN DEFAULT TRUE,
                date_inscription TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table parrainages
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS parrainages (
                id SERIAL PRIMARY KEY,
                id_filleul INTEGER UNIQUE,
                id_parrain INTEGER UNIQUE,
                date_parrainage TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_filleul) REFERENCES utilisateurs(id) ON DELETE CASCADE,
                FOREIGN KEY (id_parrain) REFERENCES utilisateurs(id) ON DELETE CASCADE
            )
        """)
        
        # Vérifier si des parrains existent déjà
        cursor.execute("SELECT COUNT(*) as count FROM utilisateurs WHERE niveau = '2'")
        result = cursor.fetchone()
        
        if result[0] == 0:
            # Hasher un mot de passe pour les parrains
            hashed_password = bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Insérer parrains initiaux
            cursor.execute("""
                INSERT INTO utilisateurs 
                (nom, matricule, mot_de_passe, telephone, serie, niveau, est_disponible) VALUES
                (%s, %s, %s, %s, %s, %s, %s),
                (%s, %s, %s, %s, %s, %s, %s),
                (%s, %s, %s, %s, %s, %s, %s),
                (%s, %s, %s, %s, %s, %s, %s),
                (%s, %s, %s, %s, %s, %s, %s),
                (%s, %s, %s, %s, %s, %s, %s)
            """, (
                'Jean Koffi', 'TI-RSI2001', hashed_password, '+2250700000001', 'TI-RSI', '2', True,
                'Marie Traoré', 'TI-RSI2002', hashed_password, '+2250700000002', 'TI-RSI', '2', True,
                'Pierre Kouadio', 'TI-RSI2003', hashed_password, '+2250700000003', 'TI-RSI', '2', True,
                'Alice Koné', 'TI-PAM2001', hashed_password, '+2250700000004', 'TI-PAM', '2', True,
                'Paul NGuessan', 'TI-PAM2002', hashed_password, '+2250700000005', 'TI-PAM', '2', True,
                'Sophie Bamba', 'TI-PAM2003', hashed_password, '+2250700000006', 'TI-PAM', '2', True
            ))
        
        conn.commit()
        cursor.close()
        print("✅ Base de données PostgreSQL initialisée avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur d'initialisation: {e}")
        conn.rollback()
    finally:
        conn.close()

# Initialisation au démarrage
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

# Route API de test
@app.route('/api/test-db')
def test_db():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM utilisateurs")
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return jsonify({"status": "success", "users_count": result[0]})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
    else:
        return jsonify({"status": "error", "message": "No database connection"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)