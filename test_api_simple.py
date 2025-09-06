#!/usr/bin/env python3
"""
Test de validation des clés API - Version sans dotenv
"""

import os
import asyncio
import aiohttp

def load_env_file():
    """Charge manuellement le fichier .env"""
    env_vars = {}
    try:
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
                    # Définir dans l'environnement
                    os.environ[key.strip()] = value.strip()
        return env_vars
    except FileNotFoundError:
        print("[ERREUR] Fichier .env non trouvé!")
        return {}

async def test_google_api():
    """Test de l'API Google Fact Check"""
    api_key = os.getenv('GOOGLE_API_KEY', '').replace('your_google_api_key_here', '')
    
    if not api_key or api_key == '':
        print("[ERREUR] GOOGLE_API_KEY non configurée dans .env")
        print("        Remplacez 'your_google_api_key_here' par votre vraie clé")
        return False
    
    print(f"[TEST] Google API Key: {api_key[:20]}...")
    
    # Test simple avec l'API Custom Search (plus simple que Fact Check Tools)
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': api_key,
        'q': 'test',
        'num': 1
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    print("[OK] Google API Key valide!")
                    return True
                elif resp.status == 403:
                    error_data = await resp.json()
                    error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                    print(f"[ERREUR] API non autorisée: {error_msg}")
                    
                    if 'Custom Search API has not been used' in error_msg:
                        print("\n[ACTION REQUISE]:")
                        print("1. Allez sur: https://console.cloud.google.com/apis/library")
                        print("2. Recherchez 'Custom Search API'")
                        print("3. Cliquez sur 'ENABLE'")
                        print("4. Attendez 1 minute et réessayez")
                    elif 'API key not valid' in error_msg:
                        print("\n[ACTION REQUISE]:")
                        print("1. Vérifiez que vous avez copié la clé complète")
                        print("2. Assurez-vous qu'il n'y a pas d'espaces avant/après")
                else:
                    print(f"[ERREUR] Code HTTP: {resp.status}")
                    
    except Exception as e:
        print(f"[ERREUR] Exception: {e}")
    
    return False

async def test_claimbuster_api():
    """Test de l'API ClaimBuster"""
    api_key = os.getenv('CLAIMBUSTER_API_KEY', '').replace('your_claimbuster_key_here', '')
    
    if not api_key or api_key == '':
        print("[INFO] CLAIMBUSTER_API_KEY non configurée")
        print("      ClaimBuster est optionnel, l'agent AFC fonctionnera sans")
        return None  # Pas un échec critique
    
    print(f"[TEST] ClaimBuster API Key: {api_key[:15]}...")
    
    url = "https://idir.uta.edu/claimbuster/api/v2/score/text"
    headers = {
        'x-api-key': api_key,
        'Content-Type': 'application/json'
    }
    
    payload = {
        'input_text': 'The Earth is round.'
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=10) as resp:
                if resp.status == 200:
                    print("[OK] ClaimBuster API fonctionnelle!")
                    return True
                elif resp.status == 401:
                    print("[ERREUR] Clé ClaimBuster invalide")
                else:
                    print(f"[ERREUR] ClaimBuster Code HTTP: {resp.status}")
                    
    except asyncio.TimeoutError:
        print("[ERREUR] ClaimBuster timeout - le service peut être lent")
    except Exception as e:
        print(f"[ERREUR] ClaimBuster Exception: {e}")
    
    return False

async def test_wikipedia():
    """Test de Wikipedia (pas de clé nécessaire)"""
    print("[TEST] Wikipedia API (sans clé)...")
    
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        'action': 'query',
        'format': 'json',
        'list': 'search',
        'srsearch': 'Python programming',
        'srlimit': 1
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=5) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if 'query' in data:
                        print("[OK] Wikipedia API fonctionnelle!")
                        return True
                    
    except Exception as e:
        print(f"[ERREUR] Wikipedia: {e}")
    
    return False

async def main():
    print("=" * 60)
    print("TEST DE VALIDATION DES APIS POUR SUBSTANS.AI")
    print("=" * 60)
    print()
    
    # Charger le fichier .env
    print("[INFO] Chargement du fichier .env...")
    env_vars = load_env_file()
    
    if not env_vars:
        print("\n[ACTION REQUISE]:")
        print("1. Copiez .env.template vers .env")
        print("   copy .env.template .env")
        print("2. Éditez .env et ajoutez vos clés API")
        print("   notepad .env")
        return
    
    print(f"[INFO] {len(env_vars)} variables chargées depuis .env\n")
    
    # Tests
    results = []
    
    # Test Wikipedia (toujours disponible)
    wiki_ok = await test_wikipedia()
    results.append(("Wikipedia", wiki_ok))
    print()
    
    # Test Google
    google_ok = await test_google_api()
    results.append(("Google API", google_ok))
    print()
    
    # Test ClaimBuster (optionnel)
    claimbuster_result = await test_claimbuster_api()
    if claimbuster_result is not None:
        results.append(("ClaimBuster", claimbuster_result))
    print()
    
    # Résumé
    print("=" * 60)
    print("RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    all_critical_ok = True
    for api_name, status in results:
        if status is None:
            status_text = "⏭️ IGNORÉ (optionnel)"
        elif status:
            status_text = "✅ OK"
        else:
            status_text = "❌ ÉCHEC"
            if api_name != "ClaimBuster":  # ClaimBuster est optionnel
                all_critical_ok = False
        
        print(f"{api_name:20} : {status_text}")
    
    print()
    if all_critical_ok and wiki_ok:
        print("🎉 SUCCÈS! Les APIs critiques sont configurées!")
        print("\n[PROCHAINES ÉTAPES]:")
        print("1. Si Google API a échoué, activez les APIs dans Google Cloud Console")
        print("2. Pour ClaimBuster (optionnel), créez un compte sur idir.uta.edu/claimbuster")
        print("3. Testez les agents: python test_agents.py")
    else:
        print("⚠️ Configuration incomplète")
        print("\n[ACTIONS REQUISES]:")
        
        if not wiki_ok:
            print("- Vérifiez votre connexion Internet (Wikipedia doit fonctionner)")
        
        if not google_ok:
            print("\n[POUR GOOGLE API]:")
            print("1. Créez un projet sur https://console.cloud.google.com/")
            print("2. Activez 'Custom Search API' dans la bibliothèque d'APIs")
            print("3. Créez une clé API dans Credentials")
            print("4. Copiez la clé dans .env: GOOGLE_API_KEY=votre_clé_ici")

if __name__ == "__main__":
    print("[INFO] Test des APIs pour les agents AFC et AGR\n")
    
    # Vérifier aiohttp
    try:
        import aiohttp
    except ImportError:
        print("[INSTALLATION] Installation d'aiohttp...")
        import subprocess
        subprocess.check_call(["pip", "install", "aiohttp"])
        print("[OK] aiohttp installé, relancez le script\n")
        exit(1)
    
    # Lancer les tests
    asyncio.run(main())
