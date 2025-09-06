
#!/usr/bin/env python3
"""
Script de test des agents AFC et AGR
"""

import asyncio
import sys
sys.path.append('.')

from agents.agents_consultants.afc import AFCAgent
from agents.agents_consultants.agr import AGRAgent

async def test_afc():
    """Test de l'agent Fact Checker"""
    print("\n[TEST] Agent Fact Checker (AFC)")
    print("-" * 40)
    
    afc = AFCAgent()
    
    # Document de test avec faits vérifiables
    test_document = """
    Selon les dernières statistiques, 75% des entreprises françaises ont adopté 
    l'intelligence artificielle en 2024. Cette augmentation représente une 
    croissance de 25% par rapport à 2023. Paris reste la capitale de la France
    et compte environ 2.2 millions d'habitants. Les études montrent que le 
    marché de l'IA atteindra 500 milliards de dollars d'ici 2025.
    """
    
    result = await afc.process(test_document)
    
    print(f"Score de confiance: {result['confidence_score']}")
    print(f"Faits vérifiés: {result['facts_checked']}")
    print(f"APIs utilisées: {', '.join(result.get('apis_used', []))}")
    print(f"Statut: {result['report']['summary']['status']}")
    
    return result

async def test_agr():
    """Test de l'agent Graphiste"""
    print("\n[TEST] Agent Graphiste (AGR)")
    print("-" * 40)
    
    agr = AGRAgent()
    
    # Document de test avec opportunités visuelles
    test_document = {
        'content': """
        Rapport Q4 2024: Performance Commerciale
        
        Nos ventes ont progressé de façon constante:
        - Q1: 125K€
        - Q2: 145K€  
        - Q3: 165K€
        - Q4: 185K€
        
        Répartition par segment:
        - Enterprise: 45%
        - PME: 30%
        - Startups: 25%
        
        Évolution depuis 2020 jusqu'à 2024 avec une croissance de 280%.
        KPIs principaux: Satisfaction client 92%, Rétention 88%, NPS 75.
        """
    }
    
    result = await agr.process(test_document, style='professional')
    
    print(f"Visuels créés: {result['visuals_created']}")
    print(f"Style appliqué: {result['style_applied']}")
    print(f"Types de charts: {[v['type'] for v in result['visuals']]}")
    
    # Sauvegarder le HTML si généré
    if 'html_code' in result:
        with open('test_visualization.html', 'w', encoding='utf-8') as f:
            f.write(result['html_code'])
        print("[OK] Visualisation sauvegardée dans test_visualization.html")
    
    return result

async def main():
    """Tests principaux"""
    print("=" * 60)
    print("TEST DES AGENTS AFC ET AGR")
    print("=" * 60)
    
    # Test AFC
    afc_result = await test_afc()
    
    # Test AGR
    agr_result = await test_agr()
    
    print("\n" + "=" * 60)
    print("[SUCCES] Tous les tests completés!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
