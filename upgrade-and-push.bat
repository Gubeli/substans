@echo off
echo ========================================
echo MISE A JOUR GIT AUTOMATIQUE SUBSTANS v3.1.0
echo ========================================
echo.

REM Étape 1: Voir où nous en sommes
echo [ETAPE 1] Verification du statut Git...
git status

echo.
echo [ETAPE 2] Ajout de TOUS les nouveaux fichiers...
git add .

echo.
echo [ETAPE 3] Creation du commit avec message detaille...
git commit -m "🚀 Major Upgrade v3.0.1 to v3.1.0 - Complete Implementation" -m "AGENTS ENHANCED:" -m "- Enhanced base agent class with memory system" -m "- AFC Fact Checker fully implemented" -m "- AGR Graphiste with visual generation" -m "" -m "ORCHESTRATION:" -m "- 6 orchestration patterns added" -m "- Enhanced Senior Advisor with intelligent routing" -m "" -m "DOCUMENTS:" -m "- Complete document management system" -m "- Multi-format support (PDF, DOCX, Excel)" -m "- Fixed PDF viewer and download issues" -m "" -m "INFRASTRUCTURE:" -m "- PostgreSQL migration support" -m "- Redis caching implementation" -m "- Docker-compose enhanced" -m "- Monitoring stack (Prometheus/Grafana)" -m "" -m "TESTING & CI/CD:" -m "- Complete test structure" -m "- GitHub Actions workflow" -m "- Load testing with Locust"

echo.
echo [ETAPE 4] Envoi vers GitHub...
git push origin main

echo.
echo ========================================
echo ✅ MISE A JOUR TERMINEE !
echo ========================================
echo.
echo Votre code est maintenant sur GitHub !
echo Vous pouvez verifier sur : https://github.com/votre-username/substans-ai
echo.
pause