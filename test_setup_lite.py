"""
Script de test de configuration Windows (version allégée)
"""

import sys
import subprocess
import importlib
import os

def test_imports():
    """Test des imports Python essentiels"""
    modules = {
        'flask': 'pip install flask',
        'sqlalchemy': 'pip install sqlalchemy',
        'pytest': 'pip install pytest',
        'aiohttp': 'pip install aiohttp',
        'prometheus_client': 'pip install prometheus-client'
    }
    
    print("Test des modules Python essentiels:")
    missing = []
    
    for module, install_cmd in modules.items():
        try:
            importlib.import_module(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module} - Installer avec: {install_cmd}")
            missing.append(install_cmd)
    
    if missing:
        print("\nPour installer tous les modules manquants:")
        print("pip install " + " ".join(m.split()[-1] for m in missing))
        return False
    return True

def test_redis_optional():
    """Test de Redis (optionnel)"""
    print("\nTest de Redis (optionnel):")
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, socket_connect_timeout=1)
        r.ping()
        print("  ✅ Redis accessible")
        return True
    except ImportError:
        print("  ⚠️ Module redis non installé (pip install redis)")
        return False
    except:
        print("  ⚠️ Redis non accessible - Mode cache mémoire activé")
        print("     Pour de meilleures performances, installez Redis")
        return True  # On continue sans Redis

def test_structure():
    """Test de la structure de dossiers"""
    print("\nVérification de la structure:")
    
    required_dirs = [
        'backend',
        'backend/cache',
        'backend/monitoring',
        'tests',
        'tests/unit',
        'config',
        'logs',
        'monitoring',
        'monitoring/prometheus'
    ]
    
    all_ok = True
    missing_dirs = []
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"  ✅ {dir_path}")
        else:
            print(f"  ❌ {dir_path} manquant")
            missing_dirs.append(dir_path)
            all_ok = False
    
    if missing_dirs:
        print("\nPour créer les dossiers manquants:")
        for d in missing_dirs:
            print(f"  mkdir {d}")
    
    return all_ok

def test_database():
    """Test de la base de données"""
    print("\nTest de la base de données:")
    
    # Vérifier SQLite (toujours disponible)
    try:
        import sqlite3
        print("  ✅ SQLite disponible")
    except:
        print("  ❌ SQLite non disponible")
        return False
    
    # Vérifier PostgreSQL (optionnel)
    try:
        import psycopg2
        print("  ✅ Module psycopg2 installé (PostgreSQL)")
    except ImportError:
        print("  ⚠️ psycopg2 non installé - Utilisation de SQLite uniquement")
    
    return True

def test_existing_project():
    """Vérifie les fichiers du projet existant"""
    print("\nVérification du projet Substans existant:")
    
    critical_files = [
        'backend/substans_ai_megacabinet/__init__.py',
        'frontend/react_interface/package.json',
        'deployment/requirements.txt'
    ]
    
    for file_path in critical_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ⚠️ {file_path} non trouvé")
    
    return True

if __name__ == "__main__":
    print("="*50)
    print("  Test de configuration Substans.AI")
    print("  Mode : Développement Windows")
    print("="*50)
    
    results = []
    results.append(test_imports())
    results.append(test_redis_optional())
    results.append(test_structure())
    results.append(test_database())
    results.append(test_existing_project())
    
    print("\n" + "="*50)
    
    # Compter les tests réussis
    essential_ok = results[0] and results[2] and results[3]
    
    if essential_ok:
        print("✅ Configuration minimale OK")
        print("   Vous pouvez continuer le développement")
        if not results[1]:
            print("\n⚠️ Recommandations:")
            print("   - Installer Redis pour de meilleures performances")
    else:
        print("❌ Configuration incomplète")
        print("   Corrigez les erreurs essentielles ci-dessus")
    
    print("="*50)