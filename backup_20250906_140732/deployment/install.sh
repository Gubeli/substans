#!/bin/bash

# Script d'installation automatique Substans.AI Enterprise v3.0.1
# Usage: ./install.sh

set -e

echo "🚀 Installation de Substans.AI Enterprise v3.0.1"
echo "=================================================="

# Vérification des prérequis
echo "🔍 Vérification des prérequis..."

# Python 3.11+
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 requis. Installation..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv
fi

# Node.js 20+
if ! command -v node &> /dev/null; then
    echo "❌ Node.js requis. Installation..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

# Autres dépendances système
echo "📦 Installation des dépendances système..."
sudo apt update
sudo apt install -y \
    build-essential \
    sqlite3 \
    libsqlite3-dev \
    nginx \
    supervisor \
    git \
    curl \
    wget \
    unzip

# Configuration des répertoires
echo "📁 Configuration des répertoires..."
mkdir -p logs
mkdir -p data
mkdir -p backups
mkdir -p temp

# Installation Backend Python
echo "🐍 Installation du backend Python..."
cd backend/flask_app
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cd ../..

# Installation Frontend React (si présent)
if [ -d "frontend/react_interface" ]; then
    echo "⚛️ Installation du frontend React..."
    cd frontend/react_interface
    npm install
    npm run build
    cd ../..
fi

# Configuration de la base de données
echo "🗄️ Configuration de la base de données..."
cd backend/flask_app
source venv/bin/activate
python -c "
import sqlite3
import os

# Création de la base de données
conn = sqlite3.connect('../../data/substans.db')
cursor = conn.cursor()

# Tables principales
cursor.execute('''
CREATE TABLE IF NOT EXISTS agents (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    performance REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS missions (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    client TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    progress INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS deliverables (
    id TEXT PRIMARY KEY,
    mission_id TEXT NOT NULL,
    title TEXT NOT NULL,
    filename TEXT NOT NULL,
    size_mb REAL DEFAULT 0.0,
    pages INTEGER DEFAULT 0,
    fact_check_score REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (mission_id) REFERENCES missions (id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS intelligence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    content TEXT NOT NULL,
    category TEXT NOT NULL,
    confidence REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS system_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Données de test
cursor.execute('''
INSERT OR REPLACE INTO missions (id, title, client, status, progress) 
VALUES ('bull_vision_strategy_bp', 'Vision, plan stratégique et BP', 'Bull', 'completed', 100)
''')

cursor.execute('''
INSERT OR REPLACE INTO deliverables (id, mission_id, title, filename, size_mb, pages, fact_check_score) 
VALUES 
('bull_prop_comm', 'bull_vision_strategy_bp', 'Proposition Commerciale Bull - Vision Stratégique', 'proposition_commerciale.pdf', 2.4, 15, 98.5),
('bull_bp_2025', 'bull_vision_strategy_bp', 'Business Plan Bull 2025-2027', 'business_plan.pdf', 3.1, 24, 96.8),
('bull_analyse_concur', 'bull_vision_strategy_bp', 'Analyse Concurrentielle et Positionnement', 'analyse_concurrentielle.pdf', 1.8, 12, 97.2)
''')

conn.commit()
conn.close()
print('✅ Base de données initialisée')
"
cd ../..

# Configuration des variables d'environnement
echo "⚙️ Configuration des variables d'environnement..."
cat > .env << EOF
# Substans.AI Enterprise v3.0.1 Configuration
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
DATABASE_URL=sqlite:///data/substans.db
API_HOST=0.0.0.0
API_PORT=5000
FRONTEND_PORT=3000

# Sécurité
JWT_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
ENCRYPTION_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# Performance
MAX_WORKERS=4
CACHE_TIMEOUT=3600
REQUEST_TIMEOUT=30

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/substans.log

# Backup
BACKUP_INTERVAL=3600
BACKUP_RETENTION=168
EOF

# Configuration Nginx (optionnel)
echo "🌐 Configuration Nginx..."
sudo tee /etc/nginx/sites-available/substans > /dev/null << EOF
server {
    listen 80;
    server_name localhost;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static/ {
        alias $(pwd)/frontend/static_interface/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/substans /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# Configuration Supervisor
echo "👥 Configuration Supervisor..."
sudo tee /etc/supervisor/conf.d/substans.conf > /dev/null << EOF
[program:substans-backend]
command=$(pwd)/backend/flask_app/venv/bin/python $(pwd)/backend/flask_app/src/main.py
directory=$(pwd)
user=$USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=$(pwd)/logs/substans-backend.log
environment=PATH="$(pwd)/backend/flask_app/venv/bin"
EOF

sudo supervisorctl reread
sudo supervisorctl update

# Permissions
echo "🔐 Configuration des permissions..."
chmod +x deployment/*.sh
chmod 755 backend/flask_app/src/main.py
chown -R $USER:$USER .

echo ""
echo "✅ Installation terminée avec succès !"
echo ""
echo "🚀 Pour démarrer Substans.AI Enterprise v3.0.1 :"
echo "   ./deployment/start.sh"
echo ""
echo "🌐 Accès web : http://localhost"
echo "📊 API : http://localhost:5000"
echo "📝 Logs : tail -f logs/substans.log"
echo ""
echo "📚 Documentation complète dans : documentation/"
echo ""

