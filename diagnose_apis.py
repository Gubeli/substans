#!/usr/bin/env python3
"""
Diagnostic détaillé des APIs avec résolution des problèmes
"""

import os
import json
import asyncio
import aiohttp
import socket
import urllib.parse

def load_env_file():
    """Charge le fichier .env"""
    env_vars = {}
    try:
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
                    os.environ[key.strip()] = value.strip()
        return env_vars
    except FileNotFoundError:
        return {}

async def test_internet_connection():
    """Test de la connexion Internet"""
    print("[TEST] Connexion Internet...")
    
    try:
        # Test DNS
        socket.gethostbyname('www.google.com')
        
        # Test HTTP
        async with aiohttp.ClientSession() as session:
            async with session.get('https://www.google.com', timeout=5) as resp:
                if resp.status == 200:
                    print("[OK] Connexion Internet fonctionnelle")
                    return True
    except Exception as e:
        print(f"[ERREUR] Pas de connexion Internet: {e}")
        return False
    
    return False

async def test_wikipedia_detailed():
    """Test détaillé de Wikipedia"""
    print("\n[TEST] Wikipedia API...")
    
    urls_to_try = [
        "https://en.wikipedia.org/w/api.php",
        "https://fr.wikipedia.org/w/api.php",
        "https://api.wikimedia.org/core/v1/wikipedia/en/search/page"
    ]
    
    for url in urls_to_try:
        print(f"  Essai: {url}")
        
        try:
            params = {
                'action': 'query',
                'format': 'json',
                'list': 'search',
                'srsearch': 'test',
                'srlimit': 1
            } if 'api.php' in url else {
                'q': 'test',
                'limit': 1
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        print(f"  [OK] Wikipedia fonctionne via {url}")
                        return True
                    else:
                        print(f"  [ERREUR] Code {resp.status}")
                        
        except asyncio.TimeoutError:
            print(f"  [TIMEOUT] Délai dépassé")
        except Exception as e:
            print(f"  [ERREUR] {str(e)[:50]}")
    
    return False

async def test_google_api_detailed():
    """Test détaillé de l'API Google"""
    print("\n[TEST] Google API...")
    
    api_key = os.getenv('GOOGLE_API_KEY', '').strip()
    
    if not api_key or api_key == 'your_google_api_key_here':
        print("[ERREUR] Clé Google non configurée")
        return False
    
    print(f"  Clé: {api_key[:20]}...")
    
    # Test 1: Validation basique de la clé
    test_urls = [
        {
            'name': 'Fact Check Tools API',
            'url': 'https://factchecktools.googleapis.com/v1alpha1/claims:search',
            'params': {
                'key': api_key,
                'query': 'climate'
            }
        },
        {
            'name': 'Custom Search API',
            'url': 'https://customsearch.googleapis.com/customsearch/v1',
            'params': {
                'key': api_key,
                'cx': '017576662512468239146:omuauf_lfve',  # CSE ID public de test
                'q': 'test'
            }
        },
        {
            'name': 'Simple Key Validation',
            'url': f'https://www.googleapis.com/customsearch/v1?key={api_key}&cx=017576662512468239146:omuauf_lfve&q=test',
            'params': None
        }
    ]
    
    for test in test_urls:
        print(f"\n  Test: {test['name']}")
        
        try:
            async with aiohttp.ClientSession() as session:
                if test['params']:
                    async with session.get(test['url'], params=test['params'], timeout=10) as resp:
                        await process_google_response(resp, test['name'])
                else:
                    async with session.get(test['url'], timeout=10) as resp:
                        await process_google_response(resp, test['name'])
                        
                        if resp.status == 200:
                            return True
                            
        except Exception as e:
            print(f"    [ERREUR] {str(e)[:100]}")
    
    return False

async def process_google_response(resp, api_name):
    """Traite la réponse Google API"""
    
    if resp.status == 200:
        print(f"    [OK] {api_name} fonctionne!")
        return True
    elif resp.status == 400:
        error_data = await resp.json()
        error = error_data.get('error', {})
        print(f"    [ERREUR 400] Requête invalide")
        print(f"    Message: {error.get('message', 'Unknown')[:100]}")
        
        if 'cx' in str(error.get('message', '')):
            print("\n    [SOLUTION] Pour Custom Search:")
            print("    1. Créez un moteur de recherche: https://programmablesearchengine.google.com/")
            print("    2. Ou utilisez Fact Check Tools API à la place")
            
    elif resp.status == 403:
        error_data = await resp.json()
        error = error_data.get('error', {})
        message = error.get('message', '')
        
        print(f"    [ERREUR 403] Accès refusé")
        print(f"    Message: {message[:100]}")
        
        if 'has not been used' in message:
            api_to_enable = message.split(' has not been used')[0]
            print(f"\n    [ACTION REQUISE] Activez l'API '{api_to_enable}':")
            print(f"    1. Allez sur: https://console.cloud.google.com/apis/library")
            print(f"    2. Recherchez: {api_to_enable}")
            print(f"    3. Cliquez sur ENABLE")
            print(f"    4. Attendez 1 minute")
            
        elif 'API key not valid' in message:
            print("\n    [ACTION REQUISE] Clé invalide:")
            print("    1. Vérifiez que la clé est correcte dans .env")
            print("    2. Créez une nouvelle clé si nécessaire")
            
    else:
        print(f"    [ERREUR] Code HTTP: {resp.status}")
        try:
            error_text = await resp.text()
            print(f"    Détails: {error_text[:200]}")
        except:
            pass

async def test_claimbuster_detailed():
    """Test détaillé de ClaimBuster"""
    print("\n[TEST] ClaimBuster API...")
    
    api_key = os.getenv('CLAIMBUSTER_API_KEY', '').strip()
    
    if not api_key or api_key == 'your_claimbuster_key_here':
        print("  [INFO] ClaimBuster non configuré (optionnel)")
        return None
    
    print(f"  Clé: {api_key[:15]}...")
    
    # URLs possibles pour ClaimBuster
    endpoints = [
        {
            'name': 'API v2 Score',
            'url': 'https://idir.uta.edu/claimbuster/api/v2/score/text',
            'method': 'POST'
        },
        {
            'name': 'API v2 Score Alt',
            'url': 'https://idir.uta.edu/claimbuster/api/v2/score',
            'method': 'POST'
        },
        {
            'name': 'API v1 Legacy',
            'url': 'https://idir.uta.edu/claimbuster/api/v1/score/text',
            'method': 'POST'
        }
    ]
    
    headers = {
        'x-api-key': api_key,
        'Content-Type': 'application/json'
    }
    
    payload = {
        'input_text': 'The Earth is round.'
    }
    
    for endpoint in endpoints:
        print(f"\n  Test: {endpoint['name']}")
        print(f"  URL: {endpoint['url']}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    endpoint['url'], 
                    headers=headers, 
                    json=payload, 
                    timeout=15
                ) as resp:
                    
                    if resp.status == 200:
                        data = await resp.json()
                        print(f"    [OK] ClaimBuster fonctionne!")
                        print(f"    Réponse: {str(data)[:100]}")
                        return True
                    elif resp.status == 401:
                        print(f"    [ERREUR 401] Clé API invalide")
                    elif resp.status == 404:
                        print(f"    [ERREUR 404] Endpoint non trouvé")
                    else:
                        print(f"    [ERREUR] Code HTTP: {resp.status}")
                        
        except asyncio.TimeoutError:
            print(f"    [TIMEOUT] Délai dépassé (15s)")
        except Exception as e:
            print(f"    [ERREUR] {str(e)[:100]}")
    
    print("\n  [INFO] ClaimBuster semble indisponible ou la clé est incorrecte")
    print("  [NOTE] L'agent AFC fonctionnera sans ClaimBuster (Wikipedia + Google)")
    
    return False

async def test_alternative_apis():
    """Test des APIs alternatives gratuites"""
    print("\n[TEST] APIs Alternatives Gratuites...")
    
    alternatives = []
    
    # Test de NewsAPI (si configuré)
    newsapi_key = os.getenv('NEWSAPI_KEY', '')
    if newsapi_key and newsapi_key != 'your_newsapi_key_here':
        try:
            url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={newsapi_key}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as resp:
                    if resp.status == 200:
                        print("  [OK] NewsAPI disponible")
                        alternatives.append('NewsAPI')
        except:
            pass
    
    # Test de JSONPlaceholder (toujours gratuit)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://jsonplaceholder.typicode.com/posts/1', timeout=5) as resp:
                if resp.status == 200:
                    print("  [OK] JSONPlaceholder disponible (pour tests)")
                    alternatives.append('JSONPlaceholder')
    except:
        pass
    
    return alternatives

async def main():
    print("=" * 70)
    print("DIAGNOSTIC DÉTAILLÉ DES APIs - SUBSTANS.AI")
    print("=" * 70)
    
    # Charger .env
    env_vars = load_env_file()
    print(f"\n[INFO] {len(env_vars)} variables chargées depuis .env")
    
    # Test de connexion Internet
    internet_ok = await test_internet_connection()
    
    if not internet_ok:
        print("\n[ERREUR CRITIQUE] Pas de connexion Internet!")
        print("[SOLUTION]:")
        print("1. Vérifiez votre connexion réseau")
        print("2. Vérifiez les paramètres proxy si vous êtes en entreprise")
        print("3. Désactivez temporairement le firewall pour tester")
        return
    
    # Tests détaillés
    wiki_ok = await test_wikipedia_detailed()
    google_ok = await test_google_api_detailed()
    claimbuster_result = await test_claimbuster_detailed()
    alternatives = await test_alternative_apis()
    
    # Résumé et recommandations
    print("\n" + "=" * 70)
    print("RÉSUMÉ ET RECOMMANDATIONS")
    print("=" * 70)
    
    print("\n[STATUT DES APIs]")
    print(f"  Wikipedia     : {'✅ OK' if wiki_ok else '❌ ÉCHEC'}")
    print(f"  Google API    : {'✅ OK' if google_ok else '❌ À CONFIGURER'}")
    print(f"  ClaimBuster   : {'✅ OK' if claimbuster_result else '⚠️ OPTIONNEL'}")
    
    if alternatives:
        print(f"\n[APIs ALTERNATIVES DISPONIBLES]")
        for alt in alternatives:
            print(f"  - {alt}")
    
    if not google_ok:
        print("\n[ACTION IMMÉDIATE POUR GOOGLE]")
        print("1. Allez sur: https://console.cloud.google.com/")
        print("2. Sélectionnez votre projet")
        print("3. Menu > APIs & Services > Library")
        print("4. Activez ces APIs:")
        print("   - Custom Search API")
        print("   - OU Fact Check Tools API")
        print("5. Créez/vérifiez votre clé dans Credentials")
        print("6. Assurez-vous que la clé n'a pas de restrictions IP")
    
    if wiki_ok and not google_ok:
        print("\n[MODE DÉGRADÉ DISPONIBLE]")
        print("✓ L'agent AFC peut fonctionner avec Wikipedia seul")
        print("✓ L'agent AGR fonctionne avec Chart.js (pas d'API nécessaire)")
        print("✓ Vous pouvez tester les agents même sans Google API")
    
    print("\n[COMMANDE DE TEST]")
    print("Une fois configuré, testez avec:")
    print("  python test_agents.py")

if __name__ == "__main__":
    asyncio.run(main())
