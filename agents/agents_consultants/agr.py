
# agents/agents_consultants/agr.py - VERSION CORRIGÉE
import os
import json
import base64
from datetime import datetime
from typing import Dict, List, Any, Optional
import re

class AGRAgent:
    '''Agent Graphiste avec Chart.js'''
    
    def __init__(self):
        self.name = "Agent Graphiste"
        self.styles = {
            'professional': {
                'colors': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],
                'font_family': 'Arial, sans-serif',
                'background': '#ffffff'
            },
            'modern': {
                'colors': ['#6366f1', '#8b5cf6', '#ec4899', '#f43f5e', '#10b981'],
                'font_family': 'Inter, sans-serif',
                'background': '#fafafa'
            }
        }
    
    async def process(self, document: Dict, style: str = 'professional') -> Dict:
        '''Enrichissement visuel d'un document'''
        
        # Analyse du document
        opportunities = self.identify_visual_opportunities(document)
        
        # Génération des visualisations
        visuals = []
        style_config = self.styles.get(style, self.styles['professional'])
        
        for opp in opportunities:
            visual = self.create_visual(opp, style_config)
            if visual:
                visuals.append(visual)
        
        # Toujours avoir au moins un graphique
        if not visuals:
            visuals.append(self.create_default_chart(style_config))
        
        # Génération du HTML
        html_code = self.generate_html(visuals, style_config)
        
        return {
            'status': 'completed',
            'visuals_created': len(visuals),
            'style_applied': style,
            'visuals': visuals,
            'html_code': html_code,
            'timestamp': datetime.now().isoformat()
        }
    
    def identify_visual_opportunities(self, document: Dict) -> List[Dict]:
        '''Identification des opportunités de visualisation'''
        content = str(document.get('content', ''))
        opportunities = []
        
        # Détection de pourcentages
        if re.search(r'\d+%', content):
            opportunities.append({'type': 'pie', 'reason': 'percentages found'})
        
        # Détection de séries temporelles
        if any(word in content.lower() for word in ['q1', 'q2', 'q3', 'q4', 'trimestre', 'quarter']):
            opportunities.append({'type': 'bar', 'reason': 'quarterly data'})
        
        # Détection d'évolution
        if any(word in content.lower() for word in ['évolution', 'growth', 'croissance', 'progression']):
            opportunities.append({'type': 'line', 'reason': 'evolution detected'})
        
        # Détection de KPIs
        if any(word in content.lower() for word in ['kpi', 'métrique', 'indicateur', 'performance']):
            opportunities.append({'type': 'radar', 'reason': 'KPIs detected'})
        
        return opportunities
    
    def create_visual(self, opportunity: Dict, style: Dict) -> Dict:
        '''Création d'une visualisation'''
        
        chart_type = opportunity.get('type', 'bar')
        
        if chart_type == 'pie':
            return self.create_pie_chart(style)
        elif chart_type == 'line':
            return self.create_line_chart(style)
        elif chart_type == 'radar':
            return self.create_radar_chart(style)
        else:
            return self.create_bar_chart(style)
    
    def create_bar_chart(self, style: Dict) -> Dict:
        '''Création d'un graphique en barres'''
        return {
            'type': 'bar',
            'config': {
                'type': 'bar',
                'data': {
                    'labels': ['Q1', 'Q2', 'Q3', 'Q4'],
                    'datasets': [{
                        'label': 'Performance',
                        'data': [125, 145, 165, 185],
                        'backgroundColor': style['colors'][:4]
                    }]
                },
                'options': {
                    'responsive': True,
                    'plugins': {
                        'legend': {'display': True},
                        'title': {
                            'display': True,
                            'text': 'Performance Trimestrielle'
                        }
                    }
                }
            }
        }
    
    def create_line_chart(self, style: Dict) -> Dict:
        '''Création d'un graphique linéaire'''
        return {
            'type': 'line',
            'config': {
                'type': 'line',
                'data': {
                    'labels': ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin'],
                    'datasets': [{
                        'label': 'Évolution',
                        'data': [100, 120, 115, 145, 160, 180],
                        'borderColor': style['colors'][0],
                        'backgroundColor': style['colors'][0] + '33',
                        'tension': 0.4
                    }]
                },
                'options': {
                    'responsive': True,
                    'plugins': {
                        'legend': {'display': True},
                        'title': {
                            'display': True,
                            'text': 'Évolution Temporelle'
                        }
                    }
                }
            }
        }
    
    def create_pie_chart(self, style: Dict) -> Dict:
        '''Création d'un camembert'''
        return {
            'type': 'pie',
            'config': {
                'type': 'pie',
                'data': {
                    'labels': ['Segment A', 'Segment B', 'Segment C', 'Segment D'],
                    'datasets': [{
                        'data': [30, 25, 25, 20],
                        'backgroundColor': style['colors'][:4]
                    }]
                },
                'options': {
                    'responsive': True,
                    'plugins': {
                        'legend': {'position': 'right'},
                        'title': {
                            'display': True,
                            'text': 'Répartition'
                        },
                        'tooltip': {
                            'callbacks': {
                                # PAS DE FONCTION LAMBDA ICI - CORRIGÉ
                                'label': None  # Chart.js utilisera le format par défaut
                            }
                        }
                    }
                }
            }
        }
    
    def create_radar_chart(self, style: Dict) -> Dict:
        '''Création d'un graphique radar'''
        return {
            'type': 'radar',
            'config': {
                'type': 'radar',
                'data': {
                    'labels': ['Qualité', 'Performance', 'Innovation', 'Service', 'Prix'],
                    'datasets': [{
                        'label': 'Évaluation',
                        'data': [85, 90, 75, 88, 82],
                        'backgroundColor': style['colors'][0] + '33',
                        'borderColor': style['colors'][0],
                        'pointBackgroundColor': style['colors'][0]
                    }]
                },
                'options': {
                    'responsive': True,
                    'plugins': {
                        'legend': {'display': True},
                        'title': {
                            'display': True,
                            'text': 'Analyse Multi-Critères'
                        }
                    },
                    'scales': {
                        'r': {
                            'beginAtZero': True,
                            'max': 100
                        }
                    }
                }
            }
        }
    
    def create_default_chart(self, style: Dict) -> Dict:
        '''Graphique par défaut si aucune opportunité détectée'''
        return self.create_bar_chart(style)
    
    def generate_html(self, visuals: List[Dict], style: Dict) -> str:
        '''Génération du HTML avec les visualisations'''
        
        # Nettoyer les configs pour JSON (retirer les None et fonctions)
        clean_visuals = []
        for visual in visuals:
            # Copie profonde pour ne pas modifier l'original
            clean_visual = {
                'type': visual['type'],
                'config': json.loads(json.dumps(visual['config'], default=str))
            }
            clean_visuals.append(clean_visual)
        
        charts_json = json.dumps(clean_visuals, indent=2)
        
        html = f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Visualisations Substans.AI</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: {style['font_family']};
            background: {style['background']};
            padding: 20px;
            margin: 0;
        }}
        .header {{
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .chart-container {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .chart-wrapper {{
            position: relative;
            height: 400px;
            margin: 20px 0;
        }}
        .status {{
            background: #4CAF50;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            display: inline-block;
            margin: 10px 0;
        }}
        h1 {{
            margin: 0;
            font-size: 2em;
        }}
        .date {{
            opacity: 0.9;
            margin-top: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Tableau de Bord Substans.AI</h1>
            <div class="date">Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}</div>
        </div>
        
        <div class="status">✅ {len(visuals)} visualisation(s) générée(s) avec succès</div>
        
        {''.join([f'<div class="chart-container"><div class="chart-wrapper"><canvas id="chart{i}"></canvas></div></div>' for i in range(len(visuals))])}
    </div>
    
    <script>
        const charts = {charts_json};
        
        charts.forEach((chart, index) => {{
            const ctx = document.getElementById('chart' + index).getContext('2d');
            
            // Nettoyer les callbacks null
            if (chart.config.options && chart.config.options.plugins) {{
                Object.values(chart.config.options.plugins).forEach(plugin => {{
                    if (plugin.tooltip && plugin.tooltip.callbacks) {{
                        Object.keys(plugin.tooltip.callbacks).forEach(key => {{
                            if (plugin.tooltip.callbacks[key] === null) {{
                                delete plugin.tooltip.callbacks[key];
                            }}
                        }});
                    }}
                }});
            }}
            
            new Chart(ctx, chart.config);
        }});
    </script>
</body>
</html>'''
        
        return html
