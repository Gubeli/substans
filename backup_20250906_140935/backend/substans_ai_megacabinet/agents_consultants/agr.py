#!/usr/bin/env python3

"""
Agent Graphiste (AGR)
Agent spécialisé dans l'enrichissement visuel des documents
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
import base64

class AgentGraphiste:
    def __init__(self):
        self.agent_id = "AGR"
        self.nom = "Agent Graphiste"
        self.version = "1.0"
        self.specialisation = "Enrichissement visuel et graphique des documents"
        
        # Configuration graphique
        self.config_graphique = {
            "styles_disponibles": [
                "professionnel",
                "moderne", 
                "minimaliste",
                "corporate",
                "dynamique",
                "academique"
            ],
            "types_visuels": [
                "graphiques_donnees",
                "schemas_processus", 
                "infographies",
                "diagrammes",
                "illustrations",
                "icones",
                "tableaux_visuels",
                "timelines"
            ],
            "formats_sortie": [
                "PNG",
                "SVG", 
                "PDF",
                "HTML"
            ],
            "palettes_couleurs": {
                "substans_corporate": ["#667eea", "#764ba2", "#f093fb", "#f5576c"],
                "professionnel": ["#2c3e50", "#3498db", "#e74c3c", "#f39c12"],
                "moderne": ["#1abc9c", "#9b59b6", "#34495e", "#e67e22"],
                "minimaliste": ["#95a5a6", "#2c3e50", "#ecf0f1", "#bdc3c7"]
            }
        }
        
        # Templates de visualisation
        self.templates = {
            "graphique_barres": {
                "description": "Graphique en barres pour données comparatives",
                "usage": "Comparaison de valeurs, évolution temporelle",
                "code_base": "chart_bar_template"
            },
            "graphique_secteurs": {
                "description": "Graphique en secteurs pour répartitions",
                "usage": "Parts de marché, répartitions budgétaires",
                "code_base": "chart_pie_template"
            },
            "timeline": {
                "description": "Chronologie visuelle",
                "usage": "Planification, historique, roadmap",
                "code_base": "timeline_template"
            },
            "schema_processus": {
                "description": "Schéma de processus métier",
                "usage": "Workflows, procédures, méthodologies",
                "code_base": "process_schema_template"
            },
            "infographie": {
                "description": "Infographie complète",
                "usage": "Synthèse visuelle, présentation de données",
                "code_base": "infographic_template"
            }
        }
        
        # Détecteurs de contenu
        self.detecteurs = {
            "donnees_numeriques": r'\b\d+(?:[.,]\d+)*\s*(?:%|€|\$|M€|M\$)\b',
            "listes_items": r'^\s*[-•*]\s+.+$',
            "etapes_processus": r'\b(?:étape|phase|step)\s+\d+\b',
            "comparaisons": r'\b(?:vs|versus|par rapport à|comparé à)\b',
            "tendances": r'\b(?:croissance|baisse|augmentation|diminution|évolution)\b',
            "dates_periodes": r'\b\d{4}(?:-\d{4})?\b|\b(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+\d{4}\b'
        }
        
        print(f"✅ {self.nom} v{self.version} initialisé")
        print(f"🎨 Spécialisation: {self.specialisation}")

    def enrichir_document(self, document: Dict[str, Any], style: str = "professionnel") -> Dict[str, Any]:
        """
        Enrichit un document avec des éléments visuels
        """
        print(f"🎨 Enrichissement du document: {document.get('title', 'Sans titre')}")
        
        contenu = document.get('content', '')
        if not contenu:
            return self._generer_rapport_erreur("Contenu vide")
        
        # Analyse du contenu pour identifier les opportunités visuelles
        opportunites = self._analyser_contenu(contenu)
        
        # Génération des éléments visuels
        elements_visuels = self._generer_elements_visuels(opportunites, style)
        
        # Intégration dans le document
        document_enrichi = self._integrer_visuels(document, elements_visuels)
        
        # Génération du rapport d'enrichissement
        rapport = self._generer_rapport_enrichissement(document, elements_visuels)
        
        return {
            "document_enrichi": document_enrichi,
            "rapport_enrichissement": rapport,
            "elements_visuels": elements_visuels
        }

    def _analyser_contenu(self, contenu: str) -> Dict[str, List[Dict]]:
        """
        Analyse le contenu pour identifier les opportunités d'enrichissement visuel
        """
        opportunites = {}
        
        # Détection de données numériques
        donnees_num = re.findall(self.detecteurs["donnees_numeriques"], contenu, re.IGNORECASE)
        if donnees_num:
            opportunites["graphiques_donnees"] = [
                {
                    "type": "graphique_barres",
                    "donnees": donnees_num,
                    "suggestion": "Créer un graphique pour visualiser ces données"
                }
            ]
        
        # Détection de listes
        listes = re.findall(self.detecteurs["listes_items"], contenu, re.MULTILINE)
        if len(listes) >= 3:
            opportunites["infographies"] = [
                {
                    "type": "liste_visuelle",
                    "items": listes,
                    "suggestion": "Transformer cette liste en infographie"
                }
            ]
        
        # Détection d'étapes/processus
        etapes = re.findall(self.detecteurs["etapes_processus"], contenu, re.IGNORECASE)
        if etapes:
            opportunites["schemas_processus"] = [
                {
                    "type": "schema_processus",
                    "etapes": etapes,
                    "suggestion": "Créer un schéma de processus"
                }
            ]
        
        # Détection de dates/périodes
        dates = re.findall(self.detecteurs["dates_periodes"], contenu, re.IGNORECASE)
        if len(dates) >= 2:
            opportunites["timelines"] = [
                {
                    "type": "timeline",
                    "dates": dates,
                    "suggestion": "Créer une timeline chronologique"
                }
            ]
        
        return opportunites

    def _generer_elements_visuels(self, opportunites: Dict[str, List[Dict]], style: str) -> List[Dict]:
        """
        Génère les éléments visuels basés sur les opportunités identifiées
        """
        elements = []
        
        for categorie, items in opportunites.items():
            for item in items:
                element = self._creer_element_visuel(item, style)
                if element:
                    elements.append(element)
        
        return elements

    def _creer_element_visuel(self, item: Dict, style: str) -> Optional[Dict]:
        """
        Crée un élément visuel spécifique
        """
        type_element = item.get("type", "")
        
        if type_element == "graphique_barres":
            return self._creer_graphique_barres(item, style)
        elif type_element == "liste_visuelle":
            return self._creer_liste_visuelle(item, style)
        elif type_element == "schema_processus":
            return self._creer_schema_processus(item, style)
        elif type_element == "timeline":
            return self._creer_timeline(item, style)
        
        return None

    def _creer_graphique_barres(self, item: Dict, style: str) -> Dict:
        """
        Crée un graphique en barres
        """
        return {
            "id": f"chart_bar_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "type": "graphique_barres",
            "titre": "Données Comparatives",
            "description": "Graphique généré automatiquement",
            "style": style,
            "donnees": item.get("donnees", []),
            "code_html": self._generer_code_graphique_barres(item, style),
            "position_suggeree": "apres_paragraphe",
            "taille": "medium"
        }

    def _creer_liste_visuelle(self, item: Dict, style: str) -> Dict:
        """
        Crée une liste visuelle/infographie
        """
        return {
            "id": f"infographic_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "type": "infographie",
            "titre": "Points Clés",
            "description": "Infographie générée automatiquement",
            "style": style,
            "items": item.get("items", []),
            "code_html": self._generer_code_infographie(item, style),
            "position_suggeree": "remplace_liste",
            "taille": "large"
        }

    def _creer_schema_processus(self, item: Dict, style: str) -> Dict:
        """
        Crée un schéma de processus
        """
        return {
            "id": f"process_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "type": "schema_processus",
            "titre": "Processus Métier",
            "description": "Schéma généré automatiquement",
            "style": style,
            "etapes": item.get("etapes", []),
            "code_html": self._generer_code_schema_processus(item, style),
            "position_suggeree": "section_dediee",
            "taille": "large"
        }

    def _creer_timeline(self, item: Dict, style: str) -> Dict:
        """
        Crée une timeline
        """
        return {
            "id": f"timeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "type": "timeline",
            "titre": "Chronologie",
            "description": "Timeline générée automatiquement",
            "style": style,
            "dates": item.get("dates", []),
            "code_html": self._generer_code_timeline(item, style),
            "position_suggeree": "section_dediee",
            "taille": "large"
        }

    def _generer_code_graphique_barres(self, item: Dict, style: str) -> str:
        """
        Génère le code HTML/CSS pour un graphique en barres
        """
        couleurs = self.config_graphique["palettes_couleurs"].get(style, 
                   self.config_graphique["palettes_couleurs"]["professionnel"])
        
        return f"""
        <div class="chart-container" style="margin: 20px 0; padding: 20px; border-radius: 8px; background: #f8f9fa;">
            <h3 style="color: {couleurs[0]}; margin-bottom: 15px;">Données Comparatives</h3>
            <div class="chart-bars" style="display: flex; align-items: end; height: 200px; gap: 10px;">
                <!-- Barres générées dynamiquement -->
                <div class="bar" style="background: {couleurs[1]}; width: 40px; height: 80%; border-radius: 4px 4px 0 0;"></div>
                <div class="bar" style="background: {couleurs[2]}; width: 40px; height: 60%; border-radius: 4px 4px 0 0;"></div>
                <div class="bar" style="background: {couleurs[3]}; width: 40px; height: 90%; border-radius: 4px 4px 0 0;"></div>
            </div>
            <p style="font-size: 12px; color: #666; margin-top: 10px;">Graphique généré automatiquement par l'Agent Graphiste</p>
        </div>
        """

    def _generer_code_infographie(self, item: Dict, style: str) -> str:
        """
        Génère le code HTML/CSS pour une infographie
        """
        couleurs = self.config_graphique["palettes_couleurs"].get(style,
                   self.config_graphique["palettes_couleurs"]["professionnel"])
        
        items_html = ""
        for i, item_text in enumerate(item.get("items", [])[:5]):  # Max 5 items
            couleur = couleurs[i % len(couleurs)]
            items_html += f"""
            <div class="info-item" style="display: flex; align-items: center; margin: 15px 0; padding: 15px; background: white; border-left: 4px solid {couleur}; border-radius: 0 8px 8px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <div class="item-icon" style="width: 40px; height: 40px; background: {couleur}; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; margin-right: 15px;">
                    {i+1}
                </div>
                <div class="item-text" style="flex: 1; font-size: 14px; line-height: 1.4;">
                    {item_text.strip('- •*').strip()}
                </div>
            </div>
            """
        
        return f"""
        <div class="infographic-container" style="margin: 30px 0; padding: 25px; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); border-radius: 12px;">
            <h3 style="color: {couleurs[0]}; text-align: center; margin-bottom: 25px; font-size: 20px;">Points Clés</h3>
            <div class="info-items">
                {items_html}
            </div>
            <p style="font-size: 12px; color: #666; text-align: center; margin-top: 15px;">Infographie générée automatiquement par l'Agent Graphiste</p>
        </div>
        """

    def _generer_code_schema_processus(self, item: Dict, style: str) -> str:
        """
        Génère le code HTML/CSS pour un schéma de processus
        """
        couleurs = self.config_graphique["palettes_couleurs"].get(style,
                   self.config_graphique["palettes_couleurs"]["professionnel"])
        
        return f"""
        <div class="process-schema" style="margin: 30px 0; padding: 25px; background: white; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h3 style="color: {couleurs[0]}; text-align: center; margin-bottom: 25px;">Processus Métier</h3>
            <div class="process-flow" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                <div class="process-step" style="background: {couleurs[1]}; color: white; padding: 15px 20px; border-radius: 8px; text-align: center; min-width: 120px; margin: 5px;">
                    Étape 1<br><small>Analyse</small>
                </div>
                <div class="arrow" style="font-size: 24px; color: {couleurs[0]};">→</div>
                <div class="process-step" style="background: {couleurs[2]}; color: white; padding: 15px 20px; border-radius: 8px; text-align: center; min-width: 120px; margin: 5px;">
                    Étape 2<br><small>Conception</small>
                </div>
                <div class="arrow" style="font-size: 24px; color: {couleurs[0]};">→</div>
                <div class="process-step" style="background: {couleurs[3]}; color: white; padding: 15px 20px; border-radius: 8px; text-align: center; min-width: 120px; margin: 5px;">
                    Étape 3<br><small>Livraison</small>
                </div>
            </div>
            <p style="font-size: 12px; color: #666; text-align: center; margin-top: 15px;">Schéma généré automatiquement par l'Agent Graphiste</p>
        </div>
        """

    def _generer_code_timeline(self, item: Dict, style: str) -> str:
        """
        Génère le code HTML/CSS pour une timeline
        """
        couleurs = self.config_graphique["palettes_couleurs"].get(style,
                   self.config_graphique["palettes_couleurs"]["professionnel"])
        
        return f"""
        <div class="timeline-container" style="margin: 30px 0; padding: 25px; background: white; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h3 style="color: {couleurs[0]}; text-align: center; margin-bottom: 25px;">Chronologie</h3>
            <div class="timeline" style="position: relative; padding: 20px 0;">
                <div class="timeline-line" style="position: absolute; left: 50%; top: 0; bottom: 0; width: 2px; background: {couleurs[1]};"></div>
                <div class="timeline-item" style="position: relative; margin: 20px 0; padding-left: 60%;">
                    <div class="timeline-dot" style="position: absolute; left: calc(50% - 8px); width: 16px; height: 16px; background: {couleurs[2]}; border-radius: 50%;"></div>
                    <div class="timeline-content" style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid {couleurs[2]};">
                        <strong>2024</strong><br>Événement important
                    </div>
                </div>
            </div>
            <p style="font-size: 12px; color: #666; text-align: center; margin-top: 15px;">Timeline générée automatiquement par l'Agent Graphiste</p>
        </div>
        """

    def _integrer_visuels(self, document: Dict[str, Any], elements_visuels: List[Dict]) -> Dict[str, Any]:
        """
        Intègre les éléments visuels dans le document
        """
        document_enrichi = document.copy()
        contenu_original = document_enrichi.get('content', '')
        
        # Ajout des éléments visuels au contenu
        contenu_enrichi = contenu_original
        
        for element in elements_visuels:
            # Insertion du code HTML de l'élément visuel
            contenu_enrichi += f"\n\n{element['code_html']}\n\n"
        
        document_enrichi['content'] = contenu_enrichi
        document_enrichi['enrichi_par'] = self.agent_id
        document_enrichi['date_enrichissement'] = datetime.now().isoformat()
        document_enrichi['elements_visuels_count'] = len(elements_visuels)
        
        return document_enrichi

    def _generer_rapport_enrichissement(self, document: Dict[str, Any], elements_visuels: List[Dict]) -> Dict[str, Any]:
        """
        Génère le rapport d'enrichissement
        """
        return {
            "document_id": document.get('id', 'unknown'),
            "document_title": document.get('title', 'Sans titre'),
            "enrichissement_date": datetime.now().isoformat(),
            "agent_graphiste": self.agent_id,
            "elements_ajoutes": len(elements_visuels),
            "types_elements": list(set([e['type'] for e in elements_visuels])),
            "ameliorations": [
                "Ajout d'éléments visuels pour améliorer la compréhension",
                "Enrichissement graphique pour un rendu plus professionnel",
                "Optimisation de la présentation des données"
            ],
            "elements_details": elements_visuels
        }

    def _generer_rapport_erreur(self, erreur: str) -> Dict[str, Any]:
        """
        Génère un rapport d'erreur
        """
        return {
            "statut": "ERREUR",
            "erreur": erreur,
            "enrichissement_date": datetime.now().isoformat(),
            "agent_graphiste": self.agent_id
        }

    def obtenir_statistiques(self) -> Dict[str, Any]:
        """
        Retourne les statistiques de l'agent graphiste
        """
        return {
            "agent_id": self.agent_id,
            "nom": self.nom,
            "version": self.version,
            "styles_disponibles": len(self.config_graphique["styles_disponibles"]),
            "types_visuels": len(self.config_graphique["types_visuels"]),
            "templates": len(self.templates)
        }

def main():
    """Test de l'agent"""
    agent = AgentGraphiste()
    
    # Document de test
    document_test = {
        "id": "test_001",
        "title": "Test d'enrichissement graphique",
        "content": """
        # Analyse de Marché
        
        Le marché du HPC représente les données suivantes:
        - Croissance de 45% en 2024
        - Chiffre d'affaires de 1.2 milliards d'euros
        - 15,000 employés dans le secteur
        
        Étape 1: Analyse des besoins
        Étape 2: Conception de la solution
        Étape 3: Implémentation
        
        Évolution temporelle: 2022, 2023, 2024, 2025
        """
    }
    
    resultat = agent.enrichir_document(document_test, "professionnel")
    print(json.dumps(resultat["rapport_enrichissement"], indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()

