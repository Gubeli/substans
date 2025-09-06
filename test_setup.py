"""
Script de test de configuration Windows
"""

import sys
import subprocess
import importlib

def test_imports():
    """Test des imports Python"""
    modules = [
        'redis',
        'psycopg2',
        'prometheus_client',
        'pytest',
        'aiohttp',
        'sqlalchemy'
    ]
    
    print("Test des modules Python:")
    for module in modules:
        try:
            importlib.import_module(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module} - Installation requise")
            return False
    return True

def test_redis():
    """Test de Redis"""
    print("\nTest de Redis:")
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379)
        r.ping()
        print("  ✅ Redis accessible")
        return True
    except:
        print("  ❌ Redis non accessible")
        print("     Lancez Redis avec: redis-server")
        return False

def test_structure():
    """Test de la structure de dossiers"""
    print("\nVérification de la structure:")
    import os
    
    required_dirs = [
        'monitoring/prometheus',
        'backend/cache',
        'tests/unit',
        'config',
        'logs'
    ]
    
    all_ok = True
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"  ✅ {dir_path}")
        else:
            print(f"  ❌ {dir_path} manquant")
            all_ok = False
    
    return all_ok

if __name__ == "__main__":
    print("="*50)
    print("  Test de configuration Substans.AI")
    print("="*50)
    
    results = []
    results.append(test_imports())
    results.append(test_redis())
    results.append(test_structure())
    
    print("\n" + "="*50)
    if all(results):
        print("✅ Configuration OK - Prêt pour la stabilisation")
    else:
        print("❌ Des éléments manquent - Vérifiez les erreurs")
    print("="*50)