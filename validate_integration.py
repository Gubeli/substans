"""
Validation complète de l'intégration v3.1.0
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime

async def validate_integration():
    """Validation de tous les composants"""
    
    print("🔍 VALIDATION DE L'INTÉGRATION v3.1.0")
    print("=" * 60)
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'version': '3.1.0',
        'tests': [],
        'status': 'pending'
    }
    
    # Test 1: Vérifier les fichiers systèmes
    print("\n📁 Test 1: Vérification des fichiers...")
    systems_path = Path("backend/substans_ai_megacabinet/systems")
    expected_files = [
        'predictive_intelligence_system.py',
        'trend_detection_system.py',
        'advanced_performance_analytics.py',
        'content_scheduler.py',
        'mobile_interface_optimizer.py',
        '__init__.py',
        'systems_config.json'
    ]
    
    files_ok = True
    for file in expected_files:
        if (systems_path / file).exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} manquant")
            files_ok = False
    
    results['tests'].append({
        'name': 'files_check',
        'passed': files_ok
    })
    
    # Test 2: Import des modules
    print("\n📦 Test 2: Import des modules...")
    try:
        from backend.substans_ai_megacabinet.systems.predictive_intelligence_system import PredictiveIntelligenceSystem
        from backend.substans_ai_megacabinet.systems.trend_detection_system import TrendDetectionSystem
        print("   ✅ Imports réussis")
        results['tests'].append({
            'name': 'imports_check',
            'passed': True
        })
    except ImportError as e:
        print(f"   ❌ Erreur d'import: {e}")
        results['tests'].append({
            'name': 'imports_check',
            'passed': False,
            'error': str(e)
        })
    
    # Test 3: Instanciation et test basique
    print("\n🧪 Test 3: Instanciation des systèmes...")
    try:
        system = PredictiveIntelligenceSystem()
        result = await system.predict('revenue', {'current_revenue': 100000})
        if result['status'] == 'success':
            print("   ✅ Système prédictif fonctionnel")
            results['tests'].append({
                'name': 'system_functionality',
                'passed': True
            })
        else:
            print("   ❌ Système prédictif non fonctionnel")
            results['tests'].append({
                'name': 'system_functionality',
                'passed': False
            })
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        results['tests'].append({
            'name': 'system_functionality',
            'passed': False,
            'error': str(e)
        })
    
    # Test 4: Configuration
    print("\n⚙️ Test 4: Vérification de la configuration...")
    config_path = systems_path / "systems_config.json"
    if config_path.exists():
        config = json.loads(config_path.read_text())
        total_systems = config['systems']['implemented']
        print(f"   ✅ {total_systems} systèmes configurés")
        results['tests'].append({
            'name': 'configuration',
            'passed': True,
            'systems_count': total_systems
        })
    else:
        print("   ❌ Configuration manquante")
        results['tests'].append({
            'name': 'configuration',
            'passed': False
        })
    
    # Résultat final
    all_passed = all(test['passed'] for test in results['tests'])
    results['status'] = 'success' if all_passed else 'failure'
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ TOUTES LES VALIDATIONS RÉUSSIES!")
        print("🎉 Substans.AI Enterprise v3.1.0 est prêt!")
    else:
        print("⚠️ Certaines validations ont échoué")
        print("Vérifiez les erreurs ci-dessus")
    
    # Sauvegarder le rapport
    report_path = Path(f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    report_path.write_text(json.dumps(results, indent=2))
    print(f"\n📄 Rapport sauvegardé: {report_path}")
    
    return results

if __name__ == "__main__":
    asyncio.run(validate_integration())