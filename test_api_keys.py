#!/usr/bin/env python3
"""
Test de validation des clés API
"""

import os
import asyncio
import aiohttp
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

async def test_google_api():
    """Test de l'API Google Fact Check"""
    api_key = os.getenv('GOOGLE_API_KEY')
    
    if not api_key:
        print("[ERREUR] GOOGLE_API_KEY non configurée dans .env")
        return False
    
    print(f"[TEST] Google API Key: {api_key[:10]}...")
    
    url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
    params = {
        'key': api_key,
        'query': 'climate change',
        'languageCode': 'en'
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print("[OK] Google Fact Check API fonctionnelle!")
                    print(f"    Résultats trouvés: {len(data.get('claims', []))}")
                    return True
                elif resp.status == 403:
                    print("[ERREUR] Clé API invalide ou API non activée")
                    print("    Vérifiez que 'Fact Check Tools API' est activée dans Google Cloud Console")
                else:
                    print(f"[ERREUR] Code HTTP: {resp.status}")
                    error_text = await resp.text()
                    print(f"    Détails: {error_text[:200]}")
                    
    except Exception as e:
        print(f"[ERREUR] Exception: {e}")
    
    return False

async def test_claimbuster_api():
    """Test de l'API ClaimBuster"""
    api_key = os.getenv('CLAIMBUSTER_API_KEY')
    
    if not api_key:
        print("[ERREUR] CLAIMBUSTER_API_KEY non configurée dans .env")
        return False
    
    print(f"[TEST] ClaimBuster API Key: {api_key[:10]}...")
    
    url = "https://idir.uta.edu/claimbuster/api/v2/score/text"
    headers = {
        'x-api-key': api_key,
        'Content-Type': 'application/json'
    }
    
    payload = {
        'input_text': 'The Earth is round and orbits around the Sun.'
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print("[OK] ClaimBuster API fonctionnelle!")
                    print(f"    Score retourné: {data.get('results', [{}])[0].get('score', 'N/A')}")
                    return True
                elif resp.status == 401:
                    print("[ERREUR] Clé API invalide")
                    print("    Vérifiez votre clé ClaimBuster")
                else:
                    print(f"[ERREUR] Code HTTP: {resp.status}")
                    
    except Exception as e:
        print(f"[ERREUR] Exception: {e}")
    
    return False

async def test_wikipedia():
    """Test de Wikipedia (pas de clé nécessaire)"""
    print("[TEST] Wikipedia API (sans clé)...")
    
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        'action': 'query',
        'format': 'json',
        'list': 'search',
        'srsearch': 'artificial intelligence',
        'srlimit': 1
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print("[OK] Wikipedia API fonctionnelle!")
                    return True
                    
    except Exception as e:
        print(f"[ERREUR] Wikipedia: {e}")
    
    return False

async def main():
    print("=" * 60)
    print("TEST DE VALIDATION DES APIS")
    print("=" * 60)
    print()
    
    # Vérifier que le fichier .env existe
    if not os.path.exists('.env'):
        print("[ERREUR] Fichier .env non trouvé!")
        print("Créez-le à partir de .env.template")
        return
    
    # Tests
    results = []
    
    # Test Google
    google_ok = await test_google_api()
    results.append(("Google Fact Check", google_ok))
    print()
    
    # Test ClaimBuster
    claimbuster_ok = await test_claimbuster_api()
    results.append(("ClaimBuster", claimbuster_ok))
    print()
    
    # Test Wikipedia
    wiki_ok = await test_wikipedia()
    results.append(("Wikipedia", wiki_ok))
    
    # Résumé
    print()
    print("=" * 60)
    print("RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    all_ok = True
    for api_name, status in results:
        status_text = "✅ OK" if status else "❌ ÉCHEC"
        print(f"{api_name:20} : {status_text}")
        if not status:
            all_ok = False
    
    print()
    if all_ok:
        print("🎉 SUCCÈS! Toutes les APIs sont configurées correctement!")
        print("Vous pouvez maintenant tester les agents: python test_agents.py")
    else:
        print("⚠️ Certaines APIs ne fonctionnent pas.")
        print("Vérifiez les clés dans le fichier .env")

if __name__ == "__main__":
    # Installer les dépendances si nécessaire
    try:
        import dotenv
    except ImportError:
        print("Installation de python-dotenv...")
        import subprocess
        subprocess.check_call(["pip", "install", "python-dotenv"])
        print("Relancez le script")
        exit(1)
    
    asyncio.run(main())
