#!/usr/bin/env python3
"""
Agents AFC et AGR en mode local (sans APIs externes)
Pour test immédiat sans configuration
"""

import json
import random
from datetime import datetime

class AFCAgentLocal:
    """Agent Fact Checker en mode local"""
    
    def __init__(self):
        self.name = "Agent Fact Checker (Mode Local)"
        
    async def process(self, document: str) -> dict:
        """Simulation de fact-checking local"""
        
        # Analyse basique du document
        word_count = len(document.split())
        has_numbers = any(char.isdigit() for char in document)
        has_percentages = '%' in document
        
        # Score simulé basé sur l'analyse
        base_score = 0.7
        if has_numbers:
            base_score += 0.1
        if has_percentages:
            base_score += 0.1
        if word_count > 50:
            base_score += 0.05
            
        confidence_score = min(base_score + random.uniform(-0.1, 0.1), 1.0)
        
        return {
            'status': 'completed',
            'mode': 'local_simulation',
            'confidence_score': round(confidence_score, 2),
            'facts_checked': random.randint(3, 8),
            'report': {
                'summary': {
                    'status': 'PASSED' if confidence_score > 0.75 else 'REVIEW_NEEDED',
                    'word_count': word_count,
                    'has_numbers': has_numbers,
                    'has_percentages': has_percentages
                }
            },
            'timestamp': datetime.now().isoformat()
        }

class AGRAgentLocal:
    """Agent Graphiste en mode local"""
    
    def __init__(self):
        self.name = "Agent Graphiste (Mode Local)"
        
    async def process(self, document: dict, style: str = 'professional') -> dict:
        """Génération de visuels en local"""
        
        # Détection des opportunités visuelles
        content = str(document.get('content', ''))
        visuals = []
        
        if '%' in content:
            visuals.append(self._create_pie_chart())
        if any(word in content.lower() for word in ['evolution', 'growth', 'progression']):
            visuals.append(self._create_line_chart())
        if any(word in content.lower() for word in ['comparison', 'versus', 'vs']):
            visuals.append(self._create_bar_chart())
            
        if not visuals:
            visuals.append(self._create_bar_chart())  # Par défaut
        
        # Génération du HTML
        html = self._generate_html(visuals, style)
        
        return {
            'status': 'completed',
            'mode': 'local_generation',
            'visuals_created': len(visuals),
            'style_applied': style,
            'visuals': visuals,
            'html_code': html,
            'timestamp': datetime.now().isoformat()
        }
    
    def _create_bar_chart(self):
        """Crée une config de bar chart"""
        return {
            'type': 'bar',
            'config': {
                'type': 'bar',
                'data': {
                    'labels': ['Q1', 'Q2', 'Q3', 'Q4'],
                    'datasets': [{
                        'label': 'Performance',
                        'data': [65, 75, 85, 95],
                        'backgroundColor': ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0']
                    }]
                }
            }
        }
    
    def _create_line_chart(self):
        """Crée une config de line chart"""
        return {
            'type': 'line',
            'config': {
                'type': 'line',
                'data': {
                    'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    'datasets': [{
                        'label': 'Évolution',
                        'data': [12, 19, 23, 25, 29, 32],
                        'borderColor': '#36A2EB',
                        'fill': False
                    }]
                }
            }
        }
    
    def _create_pie_chart(self):
        """Crée une config de pie chart"""
        return {
            'type': 'pie',
            'config': {
                'type': 'pie',
                'data': {
                    'labels': ['Segment A', 'Segment B', 'Segment C'],
                    'datasets': [{
                        'data': [45, 30, 25],
                        'backgroundColor': ['#FF6384', '#36A2EB', '#FFCE56']
                    }]
                }
            }
        }
    
    def _generate_html(self, visuals, style):
        """Génère le HTML complet"""
        charts_json = json.dumps(visuals, indent=2)
        
        return f'''<!DOCTYPE html>
<html>
<head>
    <title>Visualisations Substans.AI (Mode Local)</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }}
        .chart-container {{ max-width: 600px; margin: 20px auto; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ text-align: center; color: #333; }}
    </style>
</head>
<body>
    <h1>Tableau de Bord - Mode Local</h1>
    <div class="chart-container"><canvas id="chart1"></canvas></div>
    <div class="chart-container"><canvas id="chart2"></canvas></div>
    
    <script>
        const charts = {charts_json};
        charts.forEach((chart, index) => {{
            const ctx = document.getElementById('chart' + (index + 1)).getContext('2d');
            new Chart(ctx, chart.config);
        }});
    </script>
</body>
</html>'''

# Test immédiat
async def test_local_agents():
    print("=" * 60)
    print("TEST DES AGENTS EN MODE LOCAL")
    print("=" * 60)
    
    # Test AFC Local
    print("\n[TEST] Agent Fact Checker (Local)")
    afc = AFCAgentLocal()
    doc = "En 2024, 75% des entreprises ont adopté l'IA. Une croissance de 25% vs 2023."
    result_afc = await afc.process(doc)
    print(f"  Score de confiance: {result_afc['confidence_score']}")
    print(f"  Statut: {result_afc['report']['summary']['status']}")
    
    # Test AGR Local  
    print("\n[TEST] Agent Graphiste (Local)")
    agr = AGRAgentLocal()
    doc = {'content': 'Évolution des ventes: Q1 100K, Q2 120K, Q3 140K, Q4 160K. Croissance de 60%.'}
    result_agr = await agr.process(doc)
    print(f"  Visuels créés: {result_agr['visuals_created']}")
    
    # Sauvegarder le HTML
    with open('visualization_local.html', 'w', encoding='utf-8') as f:
        f.write(result_agr['html_code'])
    
    print(f"\n[OK] Visualisation sauvegardée: visualization_local.html")
    print("[INFO] Ouvrez le fichier HTML dans votre navigateur")
    
    return True

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_local_agents())
