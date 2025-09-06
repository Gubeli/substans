
# agents/agents_consultants/afc.py - VERSION CORRIGÉE
import os
import asyncio
import aiohttp
import json
import re
from datetime import datetime
from typing import Dict, List, Any

class AFCAgent:
    '''Agent Fact Checker avec Google API'''
    
    def __init__(self):
        self.name = "Agent Fact Checker"
        self.google_api_key = os.environ.get('GOOGLE_API_KEY', '')
        
    async def process(self, document: str) -> Dict[str, Any]:
        '''Processus de fact-checking avec Google'''
        
        # Extraction des faits clés
        facts = self.extract_key_facts(document)
        verification_results = []
        
        async with aiohttp.ClientSession() as session:
            for fact in facts[:5]:  # Limiter à 5 pour les tests
                result = await self.verify_with_google(session, fact)
                verification_results.append(result)
        
        # Calcul du score CORRIGÉ
        confidence_score = self.calculate_confidence(verification_results)
        
        return {
            'status': 'completed',
            'confidence_score': confidence_score,
            'facts_checked': len(facts),
            'verification_results': verification_results,
            'report': {
                'summary': {
                    'status': 'PASSED' if confidence_score >= 0.7 else 'REVIEW_NEEDED',
                    'details': f'{len(verification_results)} sources consultées'
                }
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def extract_key_facts(self, document: str) -> List[str]:
        '''Extraction des faits vérifiables'''
        # Diviser en phrases ou segments
        sentences = re.split(r'[.!?]', document)
        facts = []
        
        for sentence in sentences[:5]:  # Max 5 faits
            if len(sentence.strip()) > 10:
                facts.append(sentence.strip())
        
        # Si pas assez de phrases, prendre les premiers mots
        if not facts:
            words = document.split()
            facts = [' '.join(words[i:i+5]) for i in range(0, min(len(words), 20), 5)]
        
        return facts
    
    async def verify_with_google(self, session: aiohttp.ClientSession, fact: str) -> Dict:
        '''Vérification via Google Search'''
        
        try:
            # Utiliser Google Custom Search
            url = "https://customsearch.googleapis.com/customsearch/v1"
            params = {
                'key': self.google_api_key,
                'cx': '017576662512468239146:omuauf_lfve',  # Moteur de recherche public
                'q': fact[:100],  # Limiter la longueur de la requête
                'num': 1
            }
            
            async with session.get(url, params=params, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    items = data.get('items', [])
                    
                    if items:
                        # Résultat trouvé = fait probablement vrai
                        return {
                            'fact': fact[:50] + '...' if len(fact) > 50 else fact,
                            'source': 'Google Search',
                            'found': True,
                            'confidence': 0.8,  # Confiance élevée si trouvé
                            'title': items[0].get('title', '')[:100]
                        }
                    else:
                        # Pas de résultat = incertain
                        return {
                            'fact': fact[:50] + '...',
                            'source': 'Google Search',
                            'found': False,
                            'confidence': 0.4
                        }
                        
                else:
                    # Erreur API
                    return {
                        'fact': fact[:50] + '...',
                        'source': 'Google Search',
                        'error': f'HTTP {resp.status}',
                        'confidence': 0.5  # Neutre en cas d'erreur
                    }
                    
        except Exception as e:
            return {
                'fact': fact[:50] + '...',
                'source': 'Google Search',
                'error': str(e)[:50],
                'confidence': 0.5
            }
    
    def calculate_confidence(self, results: List[Dict]) -> float:
        '''Calcul du score de confiance global CORRIGÉ'''
        
        if not results:
            return 0.5  # Score neutre si pas de résultats
        
        # Calculer la moyenne des confiances
        total_confidence = sum(r.get('confidence', 0.5) for r in results)
        avg_confidence = total_confidence / len(results)
        
        # Bonus si beaucoup de faits vérifiés avec succès
        verified_count = sum(1 for r in results if r.get('found', False))
        verification_rate = verified_count / len(results) if results else 0
        
        # Score final pondéré
        final_score = (avg_confidence * 0.7) + (verification_rate * 0.3)
        
        return round(final_score, 2)
