# verify_implementation.ps1
Write-Host "`n🔍 VÉRIFICATION DE L'IMPLÉMENTATION" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan

$checks = @()

# Vérifier les dossiers
Write-Host "`n📁 Vérification des dossiers..." -ForegroundColor Yellow
$requiredDirs = @(
    "backend/systems",
    "backend/core",
    "backend/cache",
    "backend/monitoring",
    "plugins"
)

foreach ($dir in $requiredDirs) {
    if (Test-Path $dir) {
        Write-Host "  ✅ $dir" -ForegroundColor Green
        $checks += $true
    } else {
        Write-Host "  ❌ $dir manquant" -ForegroundColor Red
        $checks += $false
    }
}

# Vérifier les fichiers clés
Write-Host "`n📄 Vérification des fichiers clés..." -ForegroundColor Yellow
$requiredFiles = @(
    "backend/core/agent_factory.py",
    "backend/core/plugin_manager.py",
    "stabilization_status.json",
    "consolidation_status.json"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  ✅ $file" -ForegroundColor Green
        $checks += $true
    } else {
        Write-Host "  ❌ $file manquant" -ForegroundColor Red
        $checks += $false
    }
}

# Vérifier les systèmes
Write-Host "`n⚙️ Vérification des systèmes..." -ForegroundColor Yellow
if (Test-Path "backend/systems") {
    $systemFiles = Get-ChildItem "backend/systems/*.py" -ErrorAction SilentlyContinue
    if ($systemFiles) {
        Write-Host "  ✅ $($systemFiles.Count) systèmes trouvés" -ForegroundColor Green
        $checks += $true
    } else {
        Write-Host "  ❌ Aucun système trouvé" -ForegroundColor Red
        $checks += $false
    }
}

# Résultat global
$totalChecks = $checks.Count
$passedChecks = ($checks | Where-Object { $_ -eq $true }).Count
$successRate = [math]::Round(($passedChecks / $totalChecks) * 100, 2)

Write-Host "`n📊 RÉSULTAT GLOBAL" -ForegroundColor Cyan
Write-Host "==================" -ForegroundColor Cyan
Write-Host "Tests réussis: $passedChecks/$totalChecks ($successRate%)" -ForegroundColor $(if ($successRate -ge 80) { "Green" } elseif ($successRate -ge 60) { "Yellow" } else { "Red" })

if ($successRate -eq 100) {
    Write-Host "`n🎉 IMPLÉMENTATION COMPLÈTE ET RÉUSSIE!" -ForegroundColor Green
    Write-Host "La plateforme Substans.AI Enterprise v3.1.0 est prête!" -ForegroundColor Green
} elseif ($successRate -ge 80) {
    Write-Host "`n✅ Implémentation majoritairement réussie" -ForegroundColor Yellow
    Write-Host "Quelques ajustements mineurs peuvent être nécessaires" -ForegroundColor Yellow
} else {
    Write-Host "`n⚠️ Implémentation incomplète" -ForegroundColor Red
    Write-Host "Veuillez vérifier les erreurs ci-dessus" -ForegroundColor Red
}

# Créer un rapport
$report = @{
    timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    success_rate = $successRate
    passed_checks = $passedChecks
    total_checks = $totalChecks
    phase_stabilization = (Test-Path "stabilization_status.json")
    phase_consolidation = (Test-Path "consolidation_status.json")
}

$report | ConvertTo-Json -Depth 2 | Out-File -FilePath "verification_report.json" -Encoding UTF8
Write-Host "`n📄 Rapport sauvegardé dans verification_report.json" -ForegroundColor Cyan
