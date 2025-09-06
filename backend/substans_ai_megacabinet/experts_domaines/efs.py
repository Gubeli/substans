"""
Expert en Finance & Stratégie Financière (EFS)
Agent spécialisé dans la finance d'entreprise, M&A, analyse financière et stratégie financière
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import numpy as np

class ExpertFinanceStrategieFinanciere:
    def __init__(self):
        self.agent_id = "EFS"
        self.nom = "Expert en Finance & Stratégie Financière"
        self.version = "1.0"
        self.specialisation = "Finance d'entreprise, M&A, Analyse financière, Stratégie financière"
        
        # Domaines de spécialisation prioritaires
        self.domaines_expertise = {
            "analyse_financiere": {
                "focus": "Analyse des états financiers, ratios, performance",
                "outils": ["DCF", "Multiples", "Ratios financiers", "Analyse de tendances"],
                "secteurs": ["Tous secteurs", "Focus Tech/Industrie/Services"]
            },
            "fusions_acquisitions": {
                "focus": "Due diligence, valorisation, structuration, intégration",
                "outils": ["LBO", "DCF", "Comparable transactions", "Synergies"],
                "types": ["Acquisition", "Fusion", "LBO", "MBO", "Spin-off"]
            },
            "strategie_financiere": {
                "focus": "Structure financière, financement, politique dividende",
                "outils": ["WACC", "Structure optimale", "Politique financière"],
                "decisions": ["Investissement", "Financement", "Dividendes"]
            },
            "valorisation": {
                "focus": "Évaluation d'entreprises et d'actifs",
                "methodes": ["DCF", "Multiples", "Actif net", "Options réelles"],
                "contextes": ["M&A", "IPO", "Restructuration", "Litiges"]
            },
            "finance_marches": {
                "focus": "Marchés financiers, instruments, risques",
                "instruments": ["Actions", "Obligations", "Dérivés", "Structured products"],
                "risques": ["Marché", "Crédit", "Liquidité", "Opérationnel"]
            }
        }
        
        # Métriques financières clés
        self.metriques_cles = {
            "rentabilite": [
                "ROE", "ROA", "ROIC", "Marge nette", "Marge EBITDA", 
                "Marge opérationnelle", "Marge brute"
            ],
            "liquidite": [
                "Current ratio", "Quick ratio", "Cash ratio", 
                "Working capital", "Cash conversion cycle"
            ],
            "endettement": [
                "Debt/Equity", "Debt/EBITDA", "Interest coverage", 
                "DSCR", "Net debt/EBITDA"
            ],
            "efficacite": [
                "Asset turnover", "Inventory turnover", "Receivables turnover",
                "Days sales outstanding", "Days payable outstanding"
            ],
            "valorisation": [
                "P/E", "EV/EBITDA", "P/B", "EV/Sales", "PEG ratio",
                "Price/Cash flow", "EV/EBIT"
            ]
        }
        
        # Secteurs d'expertise prioritaires
        self.secteurs_prioritaires = {
            "technologie": {
                "specificites": ["Croissance rapide", "Intangibles", "Scalabilité"],
                "metriques": ["ARR", "CAC", "LTV", "Churn rate", "Unit economics"],
                "valorisation": ["Revenue multiples", "DCF ajusté", "Comparable SaaS"]
            },
            "industrie": {
                "specificites": ["Actifs lourds", "Cycles", "Commodités"],
                "metriques": ["ROIC", "Asset turnover", "Capacity utilization"],
                "valorisation": ["Asset-based", "DCF", "Replacement cost"]
            },
            "services_financiers": {
                "specificites": ["Réglementation", "Capital", "Risque"],
                "metriques": ["ROE", "Tier 1 ratio", "NIM", "Cost/Income"],
                "valorisation": ["P/B", "P/E", "Price/TBV"]
            },
            "sante_pharma": {
                "specificites": ["R&D", "Pipeline", "Réglementation"],
                "metriques": ["R&D/Sales", "Pipeline value", "Patent cliff"],
                "valorisation": ["Risk-adjusted NPV", "Peak sales", "Probability of success"]
            }
        }
        
        self.knowledge_base_path = "/home/ubuntu/substans_ai_megacabinet/knowledge_base/finance_strategie/"
        self.veille_active = True
        self.derniere_mise_a_jour = datetime.now().isoformat()
        
        # Sources de veille financière
        self.sources_veille = [
            "Financial Times", "Wall Street Journal", "Bloomberg", "Reuters",
            "Dealbook (NYT)", "PitchBook", "CB Insights", "McKinsey Global Institute",
            "BCG Insights", "Bain Insights", "Deloitte CFO Insights"
        ]

    def analyser_performance_financiere(self, donnees_financieres: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse complète de la performance financière d'une entreprise"""
        
        analyse = {
            "resume_executif": {},
            "ratios_calcules": {},
            "tendances": {},
            "points_forts": [],
            "points_faibles": [],
            "recommandations": [],
            "score_global": 0
        }
        
        # Extraction des données clés
        ca = donnees_financieres.get("chiffre_affaires", [])
        ebitda = donnees_financieres.get("ebitda", [])
        resultat_net = donnees_financieres.get("resultat_net", [])
        actif_total = donnees_financieres.get("actif_total", [])
        capitaux_propres = donnees_financieres.get("capitaux_propres", [])
        dette_nette = donnees_financieres.get("dette_nette", [])
        
        if len(ca) >= 2:  # Au moins 2 années de données
            # Calcul des ratios de rentabilité
            if ca[-1] > 0:
                marge_ebitda = (ebitda[-1] / ca[-1]) * 100 if ebitda else 0
                marge_nette = (resultat_net[-1] / ca[-1]) * 100 if resultat_net else 0
                
                analyse["ratios_calcules"]["marge_ebitda"] = round(marge_ebitda, 2)
                analyse["ratios_calcules"]["marge_nette"] = round(marge_nette, 2)
            
            # Calcul de la croissance
            croissance_ca = ((ca[-1] / ca[-2]) - 1) * 100 if ca[-2] > 0 else 0
            analyse["ratios_calcules"]["croissance_ca"] = round(croissance_ca, 2)
            
            # ROE et ROA
            if capitaux_propres and capitaux_propres[-1] > 0:
                roe = (resultat_net[-1] / capitaux_propres[-1]) * 100 if resultat_net else 0
                analyse["ratios_calcules"]["roe"] = round(roe, 2)
                
            if actif_total and actif_total[-1] > 0:
                roa = (resultat_net[-1] / actif_total[-1]) * 100 if resultat_net else 0
                analyse["ratios_calcules"]["roa"] = round(roa, 2)
            
            # Ratio d'endettement
            if capitaux_propres and capitaux_propres[-1] > 0 and dette_nette:
                debt_equity = dette_nette[-1] / capitaux_propres[-1]
                analyse["ratios_calcules"]["debt_equity"] = round(debt_equity, 2)
        
        # Évaluation et recommandations
        score = 0
        if analyse["ratios_calcules"].get("croissance_ca", 0) > 5:
            analyse["points_forts"].append("Croissance du CA supérieure à 5%")
            score += 20
        
        if analyse["ratios_calcules"].get("marge_ebitda", 0) > 15:
            analyse["points_forts"].append("Marge EBITDA solide (>15%)")
            score += 20
        
        if analyse["ratios_calcules"].get("roe", 0) > 15:
            analyse["points_forts"].append("ROE attractif (>15%)")
            score += 20
            
        analyse["score_global"] = min(score, 100)
        
        return analyse

    def evaluer_opportunite_ma(self, cible: Dict[str, Any], acquireur: Dict[str, Any]) -> Dict[str, Any]:
        """Évalue une opportunité de M&A"""
        
        evaluation = {
            "rationale_strategique": {},
            "valorisation": {},
            "synergies": {},
            "risques": [],
            "structure_recommandee": {},
            "probabilite_succes": 0,
            "recommandation": ""
        }
        
        # Analyse du rationale stratégique
        secteur_cible = cible.get("secteur", "")
        secteur_acquireur = acquireur.get("secteur", "")
        
        if secteur_cible == secteur_acquireur:
            evaluation["rationale_strategique"]["type"] = "Consolidation horizontale"
            evaluation["rationale_strategique"]["avantages"] = [
                "Économies d'échelle", "Élimination concurrence", "Parts de marché"
            ]
        else:
            evaluation["rationale_strategique"]["type"] = "Diversification"
            evaluation["rationale_strategique"]["avantages"] = [
                "Diversification risques", "Nouveaux marchés", "Cross-selling"
            ]
        
        # Valorisation indicative
        ca_cible = cible.get("chiffre_affaires", 0)
        ebitda_cible = cible.get("ebitda", 0)
        
        if ca_cible > 0 and ebitda_cible > 0:
            # Multiples sectoriels (simplifiés)
            multiples_secteur = self._get_multiples_secteur(secteur_cible)
            
            valorisation_ev_ebitda = ebitda_cible * multiples_secteur.get("ev_ebitda", 8)
            valorisation_ev_sales = ca_cible * multiples_secteur.get("ev_sales", 2)
            
            evaluation["valorisation"]["ev_ebitda"] = valorisation_ev_ebitda
            evaluation["valorisation"]["ev_sales"] = valorisation_ev_sales
            evaluation["valorisation"]["fourchette"] = [
                min(valorisation_ev_ebitda, valorisation_ev_sales) * 0.9,
                max(valorisation_ev_ebitda, valorisation_ev_sales) * 1.1
            ]
        
        # Estimation des synergies
        ca_total = ca_cible + acquireur.get("chiffre_affaires", 0)
        synergies_revenus = ca_total * 0.02  # 2% du CA combiné
        synergies_couts = ca_cible * 0.05    # 5% du CA de la cible
        
        evaluation["synergies"]["revenus"] = synergies_revenus
        evaluation["synergies"]["couts"] = synergies_couts
        evaluation["synergies"]["total"] = synergies_revenus + synergies_couts
        
        # Évaluation des risques
        evaluation["risques"] = [
            "Risque d'intégration culturelle",
            "Risque de rétention des talents clés",
            "Risque réglementaire (antitrust)",
            "Risque de surévaluation",
            "Risque d'exécution des synergies"
        ]
        
        # Probabilité de succès (modèle simplifié)
        score_financier = min((ebitda_cible / ca_cible) * 100, 20) if ca_cible > 0 else 0
        score_strategique = 30 if secteur_cible == secteur_acquireur else 20
        score_taille = min(ca_cible / 1000000, 20)  # Bonus pour taille significative
        
        evaluation["probabilite_succes"] = min(score_financier + score_strategique + score_taille, 80)
        
        # Recommandation
        if evaluation["probabilite_succes"] > 60:
            evaluation["recommandation"] = "RECOMMANDÉ - Opportunité attractive"
        elif evaluation["probabilite_succes"] > 40:
            evaluation["recommandation"] = "À ÉTUDIER - Due diligence approfondie requise"
        else:
            evaluation["recommandation"] = "NON RECOMMANDÉ - Risques trop élevés"
        
        return evaluation

    def _get_multiples_secteur(self, secteur: str) -> Dict[str, float]:
        """Retourne les multiples de valorisation par secteur"""
        
        multiples_db = {
            "technologie": {"ev_ebitda": 15, "ev_sales": 4, "pe": 25},
            "industrie": {"ev_ebitda": 8, "ev_sales": 1.5, "pe": 15},
            "services_financiers": {"ev_ebitda": 10, "ev_sales": 3, "pe": 12},
            "sante_pharma": {"ev_ebitda": 12, "ev_sales": 5, "pe": 20},
            "energie": {"ev_ebitda": 6, "ev_sales": 1, "pe": 10},
            "biens_consommation": {"ev_ebitda": 10, "ev_sales": 2, "pe": 18}
        }
        
        return multiples_db.get(secteur.lower(), {"ev_ebitda": 8, "ev_sales": 2, "pe": 15})

    def analyser_structure_financiere(self, entreprise: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse la structure financière optimale d'une entreprise"""
        
        analyse = {
            "structure_actuelle": {},
            "structure_optimale": {},
            "recommandations": [],
            "impact_wacc": {},
            "flexibilite_financiere": ""
        }
        
        # Données actuelles
        dette_totale = entreprise.get("dette_totale", 0)
        capitaux_propres = entreprise.get("capitaux_propres", 0)
        ebitda = entreprise.get("ebitda", 0)
        
        if capitaux_propres > 0:
            ratio_endettement = dette_totale / (dette_totale + capitaux_propres)
            analyse["structure_actuelle"]["ratio_endettement"] = round(ratio_endettement, 3)
            
            if ebitda > 0:
                dette_ebitda = dette_totale / ebitda
                analyse["structure_actuelle"]["dette_ebitda"] = round(dette_ebitda, 2)
        
        # Structure optimale par secteur
        secteur = entreprise.get("secteur", "")
        if secteur in self.secteurs_prioritaires:
            if secteur == "technologie":
                ratio_optimal = 0.2  # 20% dette
                analyse["recommandations"].append("Secteur tech : privilégier financement par fonds propres")
            elif secteur == "industrie":
                ratio_optimal = 0.4  # 40% dette
                analyse["recommandations"].append("Secteur industriel : structure équilibrée avec dette modérée")
            else:
                ratio_optimal = 0.3  # 30% dette par défaut
        else:
            ratio_optimal = 0.3
            
        analyse["structure_optimale"]["ratio_endettement_cible"] = ratio_optimal
        
        # Recommandations d'ajustement
        ratio_actuel = analyse["structure_actuelle"].get("ratio_endettement", 0)
        if ratio_actuel > ratio_optimal + 0.1:
            analyse["recommandations"].append("Réduire l'endettement - Ratio trop élevé")
        elif ratio_actuel < ratio_optimal - 0.1:
            analyse["recommandations"].append("Opportunité d'optimisation fiscale via endettement")
        
        return analyse

    def effectuer_veille_financiere(self) -> Dict[str, Any]:
        """Effectue une veille financière automatique"""
        
        print(f"[{self.agent_id}] Démarrage de la veille financière...")
        
        veille_resultats = {
            "tendances_marches": [],
            "operations_ma_significatives": [],
            "nouvelles_reglementations": [],
            "innovations_fintech": [],
            "alertes_sectorielles": []
        }
        
        # Simulation de veille (en production, APIs financières)
        veille_resultats["tendances_marches"] = [
            "Taux d'intérêt : Stabilisation attendue BCE Q4 2024",
            "M&A Tech : Reprise activité avec valorisations ajustées",
            "IPO : Pipeline 2025 prometteur en Europe"
        ]
        
        veille_resultats["operations_ma_significatives"] = [
            "Acquisition Broadcom/VMware : $61Md - Impact consolidation tech",
            "Microsoft/Activision : Finalisation après approbations réglementaires",
            "Private Equity : Activité soutenue sur mid-market européen"
        ]
        
        veille_resultats["nouvelles_reglementations"] = [
            "CSRD : Nouvelles obligations reporting ESG 2024",
            "Basel III : Impact sur financement bancaire PME",
            "MiCA : Réglementation crypto-actifs UE"
        ]
        
        veille_resultats["innovations_fintech"] = [
            "IA générative : Applications en analyse financière",
            "Blockchain : Tokenisation d'actifs traditionnels",
            "Open Banking : Extension aux services d'investissement"
        ]
        
        print(f"[{self.agent_id}] Veille terminée. {len(veille_resultats['tendances_marches'])} tendances identifiées.")
        
        self.derniere_mise_a_jour = datetime.now().isoformat()
        return veille_resultats

    def generer_rapport_veille_quotidien(self) -> str:
        """Génère le rapport de veille quotidien"""
        
        veille = self.effectuer_veille_financiere()
        date_rapport = datetime.now().strftime("%d/%m/%Y")
        
        rapport = f"""# 📊 Veille Finance & Stratégie Financière - {date_rapport}

## 🎯 Synthèse Exécutive
Rapport quotidien des développements significatifs en finance d'entreprise, M&A et stratégie financière.

## 📈 Tendances des Marchés Financiers
"""
        
        for tendance in veille["tendances_marches"]:
            rapport += f"• **{tendance}**\n"
        
        rapport += f"""
## 🤝 Opérations M&A Significatives
"""
        
        for operation in veille["operations_ma_significatives"]:
            rapport += f"• **{operation}**\n"
        
        rapport += f"""
## ⚖️ Nouvelles Réglementations Financières
"""
        
        for reglementation in veille["nouvelles_reglementations"]:
            rapport += f"• **{reglementation}**\n"
        
        rapport += f"""
## 🚀 Innovations FinTech
"""
        
        for innovation in veille["innovations_fintech"]:
            rapport += f"• **{innovation}**\n"
        
        rapport += f"""
## 🎯 Implications Stratégiques

### Pour les Entreprises
- **Financement** : Conditions de crédit stables, opportunités de refinancement
- **M&A** : Fenêtre favorable pour acquisitions stratégiques
- **Valorisations** : Ajustement progressif vers fondamentaux

### Pour les Investisseurs
- **Private Equity** : Focus sur operational value creation
- **Venture Capital** : Sélectivité accrue, focus profitabilité
- **Corporate Venture** : Partenariats stratégiques privilégiés

## 📊 Métriques Clés à Surveiller
- **Spreads de crédit** : Stabilité relative
- **Multiples de valorisation** : Normalisation progressive
- **Volumes M&A** : Reprise sélective attendue

---
*Rapport généré par {self.nom} ({self.agent_id}) - {datetime.now().strftime("%H:%M")}*
*Sources : {', '.join(self.sources_veille[:3])} et autres*
"""
        
        return rapport

    def provide_expertise(self, mission_context: Dict[str, Any]) -> str:
        """Fournit une expertise financière pour une mission donnée"""
        
        mission_type = mission_context.get("type", "")
        secteur = mission_context.get("secteur", "")
        
        if "m&a" in mission_type.lower() or "acquisition" in mission_type.lower():
            return f"Expertise M&A pour {secteur} : Due diligence financière, valorisation, structuration"
        elif "financement" in mission_type.lower():
            return f"Expertise financement pour {secteur} : Structure optimale, sources de financement"
        elif "valorisation" in mission_type.lower():
            return f"Expertise valorisation pour {secteur} : Méthodes adaptées, benchmarks sectoriels"
        else:
            return f"Expertise finance d'entreprise pour {secteur} : Analyse financière, stratégie financière"

    def autonomous_watch(self):
        """Démarre la veille autonome de l'expert"""
        print(f"{self.agent_id}: Veille autonome sur finance d'entreprise, M&A et stratégie financière")
        if self.veille_active:
            rapport = self.generer_rapport_veille_quotidien()
            # Sauvegarde du rapport
            os.makedirs(self.knowledge_base_path, exist_ok=True)
            filename = f"veille_finance_{datetime.now().strftime('%Y%m%d')}.md"
            with open(os.path.join(self.knowledge_base_path, filename), 'w', encoding='utf-8') as f:
                f.write(rapport)

    def get_expertise_summary(self) -> Dict[str, Any]:
        """Retourne un résumé de l'expertise de l'agent"""
        
        return {
            "agent_id": self.agent_id,
            "nom": self.nom,
            "specialisation": self.specialisation,
            "domaines_expertise": list(self.domaines_expertise.keys()),
            "secteurs_prioritaires": list(self.secteurs_prioritaires.keys()),
            "services": [
                "Analyse de performance financière",
                "Évaluation d'opportunités M&A",
                "Optimisation structure financière",
                "Valorisation d'entreprises",
                "Due diligence financière",
                "Stratégie de financement",
                "Veille financière continue"
            ],
            "metriques_specialisees": sum(len(v) for v in self.metriques_cles.values()),
            "sources_veille": len(self.sources_veille),
            "derniere_mise_a_jour": self.derniere_mise_a_jour,
            "statut_veille": "ACTIVE" if self.veille_active else "INACTIVE"
        }

# Test de l'agent
if __name__ == '__main__':
    efs = ExpertFinanceStrategieFinanciere()
    
    print("=== Expert en Finance & Stratégie Financière ===")
    print(f"Agent: {efs.nom} ({efs.agent_id})")
    print(f"Spécialisation: {efs.specialisation}")
    
    # Test d'analyse financière
    donnees_test = {
        "chiffre_affaires": [1000, 1200, 1400],
        "ebitda": [200, 250, 300],
        "resultat_net": [80, 100, 120],
        "actif_total": [2000, 2200, 2400],
        "capitaux_propres": [800, 900, 1000],
        "dette_nette": [400, 450, 500]
    }
    
    print("\n--- Test d'Analyse Financière ---")
    analyse = efs.analyser_performance_financiere(donnees_test)
    print(f"Score global: {analyse['score_global']}/100")
    print(f"Croissance CA: {analyse['ratios_calcules'].get('croissance_ca', 'N/A')}%")
    
    # Test M&A
    print("\n--- Test Évaluation M&A ---")
    cible_test = {
        "secteur": "technologie",
        "chiffre_affaires": 500,
        "ebitda": 100
    }
    acquireur_test = {
        "secteur": "technologie", 
        "chiffre_affaires": 2000
    }
    
    evaluation_ma = efs.evaluer_opportunite_ma(cible_test, acquireur_test)
    print(f"Recommandation: {evaluation_ma['recommandation']}")
    print(f"Probabilité succès: {evaluation_ma['probabilite_succes']}%")
    
    # Test de veille
    print("\n--- Test de Veille Financière ---")
    rapport_veille = efs.generer_rapport_veille_quotidien()
    print(f"Rapport généré: {len(rapport_veille)} caractères")
    
    # Résumé de l'expertise
    print("\n--- Résumé de l'Expertise ---")
    expertise = efs.get_expertise_summary()
    print(f"Services: {len(expertise['services'])}")
    print(f"Domaines: {expertise['domaines_expertise']}")
    print(f"Secteurs prioritaires: {expertise['secteurs_prioritaires']}")

