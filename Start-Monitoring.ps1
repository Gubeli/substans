Write-Host "========================================"
Write-Host "  Démarrage du Monitoring Substans.AI" -ForegroundColor Cyan
Write-Host "========================================"
Write-Host ""

# Vérifier que le fichier existe
$metricsFile = "backend\monitoring\metrics_endpoint.py"

if (-not (Test-Path $metricsFile)) {
    Write-Host "❌ Fichier $metricsFile non trouvé!" -ForegroundColor Red
    Write-Host "Création du fichier..." -ForegroundColor Yellow
    
    # Créer le dossier si nécessaire
    New-Item -ItemType Directory -Force -Path "backend\monitoring" | Out-Null
    
    # Créer un serveur de métriques minimal
    $metricsCode = @'
from flask import Flask, Response
import json
from datetime import datetime

app = Flask(__name__)

@app.route('/metrics')
def metrics():
    """Endpoint pour Prometheus"""
    return Response("# Substans Metrics\nsubstans_up 1\n", mimetype='text/plain')

@app.route('/health')
def health():
    """Endpoint de santé"""
    return {'status': 'healthy', 'timestamp': datetime.now().isoformat()}

@app.route('/test_metrics')
def test_metrics():
    """Endpoint de test"""
    return {'status': 'ok', 'message': 'Test metrics endpoint'}

if __name__ == '__main__':
    print("🚀 Serveur de métriques démarré sur http://localhost:8000")
    app.run(host='0.0.0.0', port=8000, debug=False)
'@
    
    $metricsCode | Out-File -FilePath $metricsFile -Encoding UTF8
    Write-Host "✅ Fichier créé!" -ForegroundColor Green
}

Write-Host "[1/3] Installation de Flask si nécessaire..." -ForegroundColor Yellow
python -m pip show flask > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Installation de Flask..." -ForegroundColor Gray
    python -m pip install flask --quiet
}

Write-Host "[2/3] Démarrage du serveur de métriques..." -ForegroundColor Yellow

# Démarrer le serveur dans un nouveau processus
$process = Start-Process python -ArgumentList $metricsFile -PassThru -WindowStyle Normal

Start-Sleep -Seconds 3

Write-Host "[3/3] Vérification du serveur..." -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host ""
        Write-Host "✅ Monitoring démarré avec succès!" -ForegroundColor Green
        Write-Host ""
        Write-Host "URLs disponibles:" -ForegroundColor Cyan
        Write-Host "  📊 Métriques: http://localhost:8000/metrics" -ForegroundColor White
        Write-Host "  ❤️  Health:    http://localhost:8000/health" -ForegroundColor White
        Write-Host "  🧪 Test:      http://localhost:8000/test_metrics" -ForegroundColor White
    }
} catch {
    Write-Host "⚠️  Le serveur met du temps à démarrer..." -ForegroundColor Yellow
    Write-Host "    Vérifiez dans quelques secondes" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Process ID: $($process.Id)" -ForegroundColor Gray
Write-Host "Pour arrêter le serveur: Stop-Process -Id $($process.Id)" -ForegroundColor Gray
Write-Host ""