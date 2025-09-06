#!/bin/bash

# Script d'arrêt Substans.AI Enterprise v3.0.1
# Usage: ./stop.sh

echo "🛑 Arrêt de Substans.AI Enterprise v3.0.1"
echo "=========================================="

# Arrêt du backend
if [ -f logs/backend.pid ]; then
    BACKEND_PID=$(cat logs/backend.pid)
    if ps -p $BACKEND_PID > /dev/null; then
        echo "🐍 Arrêt du backend Flask (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        sleep 2
        if ps -p $BACKEND_PID > /dev/null; then
            echo "⚠️ Arrêt forcé du backend..."
            kill -9 $BACKEND_PID
        fi
        echo "✅ Backend arrêté"
    fi
    rm -f logs/backend.pid
fi

# Arrêt du frontend
if [ -f logs/frontend.pid ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null; then
        echo "⚛️ Arrêt du frontend React (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        sleep 2
        if ps -p $FRONTEND_PID > /dev/null; then
            echo "⚠️ Arrêt forcé du frontend..."
            kill -9 $FRONTEND_PID
        fi
        echo "✅ Frontend arrêté"
    fi
    rm -f logs/frontend.pid
fi

# Nettoyage des processus restants
pkill -f "substans" 2>/dev/null || true
pkill -f "flask" 2>/dev/null || true

echo ""
echo "✅ Substans.AI Enterprise v3.0.1 arrêté avec succès"
echo ""

