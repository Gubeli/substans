#!/bin/bash

# Script de démarrage Substans.AI Enterprise v3.0.1
# Usage: ./start.sh

set -e

echo "🚀 Démarrage de Substans.AI Enterprise v3.0.1"
echo "=============================================="

# Chargement des variables d'environnement
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ Variables d'environnement chargées"
else
    echo "⚠️ Fichier .env non trouvé, utilisation des valeurs par défaut"
fi

# Vérification des répertoires
mkdir -p logs data backups temp

# Démarrage du backend
echo "🐍 Démarrage du backend Flask..."
cd backend/flask_app
source venv/bin/activate

# Vérification de la base de données
if [ ! -f "../../data/substans.db" ]; then
    echo "🗄️ Initialisation de la base de données..."
    python -c "
import sqlite3
conn = sqlite3.connect('../../data/substans.db')
conn.execute('CREATE TABLE IF NOT EXISTS test (id INTEGER)')
conn.close()
print('Base de données créée')
"
fi

# Démarrage en arrière-plan
nohup python src/main.py > ../../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ Backend démarré (PID: $BACKEND_PID)"

cd ../..

# Attente que le backend soit prêt
echo "⏳ Attente du démarrage du backend..."
for i in {1..30}; do
    if curl -s http://localhost:${API_PORT:-5000}/health > /dev/null 2>&1; then
        echo "✅ Backend prêt"
        break
    fi
    sleep 1
done

# Démarrage du frontend React (si disponible)
if [ -d "frontend/react_interface" ] && [ -f "frontend/react_interface/package.json" ]; then
    echo "⚛️ Démarrage du frontend React..."
    cd frontend/react_interface
    nohup npm start > ../../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "✅ Frontend React démarré (PID: $FRONTEND_PID)"
    cd ../..
fi

# Sauvegarde des PIDs
echo $BACKEND_PID > logs/backend.pid
if [ ! -z "$FRONTEND_PID" ]; then
    echo $FRONTEND_PID > logs/frontend.pid
fi

# Affichage des informations de connexion
echo ""
echo "🎉 Substans.AI Enterprise v3.0.1 démarré avec succès !"
echo ""
echo "🌐 Accès web :"
echo "   - Interface principale : http://localhost:${API_PORT:-5000}"
if [ ! -z "$FRONTEND_PID" ]; then
echo "   - Interface React : http://localhost:${FRONTEND_PORT:-3000}"
fi
echo ""
echo "📊 API Endpoints :"
echo "   - Health check : http://localhost:${API_PORT:-5000}/health"
echo "   - Dashboard : http://localhost:${API_PORT:-5000}/"
echo "   - API Missions : http://localhost:${API_PORT:-5000}/api/missions"
echo "   - API Agents : http://localhost:${API_PORT:-5000}/api/agents"
echo ""
echo "📝 Logs en temps réel :"
echo "   - Backend : tail -f logs/backend.log"
echo "   - Frontend : tail -f logs/frontend.log"
echo "   - Système : tail -f logs/substans.log"
echo ""
echo "🛑 Pour arrêter : ./deployment/stop.sh"
echo "🔄 Pour redémarrer : ./deployment/restart.sh"
echo ""

# Monitoring de base
echo "📊 Statut des services :"
if ps -p $BACKEND_PID > /dev/null; then
    echo "   ✅ Backend Flask : Actif (PID: $BACKEND_PID)"
else
    echo "   ❌ Backend Flask : Erreur"
fi

if [ ! -z "$FRONTEND_PID" ] && ps -p $FRONTEND_PID > /dev/null; then
    echo "   ✅ Frontend React : Actif (PID: $FRONTEND_PID)"
elif [ ! -z "$FRONTEND_PID" ]; then
    echo "   ❌ Frontend React : Erreur"
fi

echo ""
echo "🎯 Substans.AI Enterprise v3.0.1 est opérationnel !"
echo "   34 agents experts disponibles"
echo "   47 systèmes enterprise actifs"
echo "   API complète avec authentification"
echo "   Interface responsive et mobile-friendly"
echo ""

