#!/bin/bash

# Script de redémarrage Substans.AI Enterprise v3.0.1
# Usage: ./restart.sh

echo "🔄 Redémarrage de Substans.AI Enterprise v3.0.1"
echo "==============================================="

# Arrêt
./deployment/stop.sh

# Attente
echo "⏳ Attente de 3 secondes..."
sleep 3

# Redémarrage
./deployment/start.sh

echo ""
echo "✅ Redémarrage terminé"
echo ""

