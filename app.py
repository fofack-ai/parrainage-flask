import os
from flask import Flask, request, jsonify, session, render_template
from flask_cors import CORS
import pymysql
import bcrypt
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
CORS(app)

# Configuration base de données
def get_db_connection():
    return pymysql.connect(
        host=os.environ.get('MYSQL_HOST', 'localhost'),
        user=os.environ.get('MYSQL_USER', 'root'),
        password=os.environ.get('MYSQL_PASSWORD', ''),
        database=os.environ.get('MYSQL_DB', 'parrainage'),
        port=int(os.environ.get('MYSQL_PORT', 3306)),
        cursorclass=pymysql.cursors.DictCursor
    )

# Fonction d'initialisation de la base
def init_database():
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Table utilisateurs
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS utilisateurs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nom VARCHAR(100) NOT NULL,
                    matricule VARCHAR(50) UNIQUE NOT NULL,
                    mot_de_passe VARCHAR(255) NOT NULL,
                    telephone VARCHAR(20),
                    photo VARCHAR(255) DEFAULT 'default.jpg',
                    serie ENUM('TI-RSI', 'TI-PAM') NOT NULL,
                    niveau ENUM('1', '2') NOT NULL,
                    est_disponible BOOLEAN DEFAULT TRUE,
                    date_inscription DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table parrainages
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS parrainages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    id_filleul INT UNIQUE,
                    id_parrain INT UNIQUE,
                    date_parrainage DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id_filleul) REFERENCES utilisateurs(id) ON DELETE CASCADE,
                    FOREIGN KEY (id_parrain) REFERENCES utilisateurs(id) ON DELETE CASCADE
                )
            """)
            
            # Vérifier si des parrains existent déjà
            cursor.execute("SELECT COUNT(*) as count FROM utilisateurs WHERE niveau = '2'")
            result = cursor.fetchone()
            
            if result['count'] == 0:
                # Insérer parrains initiaux
                cursor.execute("""
                    INSERT INTO utilisateurs 
                    (nom, matricule, mot_de_passe, telephone, serie, niveau, est_disponible) VALUES
                    ('Jean Koffi', 'TI-RSI2001', '$2b$12$hash', '+2250700000001', 'TI-RSI', '2', TRUE),
                    ('Marie Traoré', 'TI-RSI2002', '$2b$12$hash', '+2250700000002', 'TI-RSI', '2', TRUE),
                    ('Pierre Kouadio', 'TI-RSI2003', '$2b$12$hash', '+2250700000003', 'TI-RSI', '2', TRUE),
                    ('Alice Koné', 'TI-PAM2001', '$2b$12$hash', '+2250700000004', 'TI-PAM', '2', TRUE),
                    ('Paul NGuessan', 'TI-PAM2002', '$2b$12$hash', '+2250700000005', 'TI-PAM', '2', TRUE),
                    ('Sophie Bamba', 'TI-PAM2003', '$2b$12$hash', '+2250700000006', 'TI-PAM', '2', TRUE)
                """)
            
            conn.commit()
            print("✅ Base de données initialisée avec succès!")
            
    except Exception as e:
        print(f"❌ Erreur d'initialisation: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

# Initialiser au premier démarrage
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

# ... TES AUTRES ROUTES API RESTENT IDENTIQUES ...

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)