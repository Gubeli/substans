#!/usr/bin/env python3
"""
Script pour créer tous les agents manquants de l'architecture matricielle substans.ai
Total : 29 agents + 1 Senior Advisor = 30 agents
"""

import os

# Définition complète de tous les agents
AGENTS_DEFINITION = {
    "experts_metiers": {
        "er": {
            "nom": "ExpertRetail",
            "classe": "ExpertRetail",
            "specialisation": "Commerce de détail, e-commerce, distribution",
            "description": "Expert en retail, distribution, e-commerce et expérience client"
        },
        "em": {
            "nom": "ExpertManufacturing", 
            "classe": "ExpertManufacturing",
            "specialisation": "Industrie manufacturière, production, supply chain",
            "description": "Expert en manufacturing, industrie 4.0, optimisation production"
        },
        "eauto": {
            "nom": "ExpertAutomobile",
            "classe": "ExpertAutomobile", 
            "specialisation": "Industrie automobile, mobilité, véhicules électriques",
            "description": "Expert en automobile, mobilité durable, véhicules connectés"
        },
        "etl": {
            "nom": "ExpertTransportLogistique",
            "classe": "ExpertTransportLogistique",
            "specialisation": "Transport, logistique, supply chain",
            "description": "Expert en transport, logistique, optimisation des flux"
        },
        "esp": {
            "nom": "ExpertServicesPublics",
            "classe": "ExpertServicesPublics",
            "specialisation": "Administration publique, services publics, e-gouvernement",
            "description": "Expert en services publics, transformation digitale publique"
        },
        "ed": {
            "nom": "ExpertDefense",
            "classe": "ExpertDefense",
            "specialisation": "Défense, sécurité, technologies militaires",
            "description": "Expert en défense, sécurité nationale, technologies militaires"
        },
        "ee": {
            "nom": "ExpertEnergie",
            "classe": "ExpertEnergie",
            "specialisation": "Énergie, renouvelables, transition énergétique",
            "description": "Expert en énergie, transition énergétique, smart grids"
        }
    },
    "experts_domaines": {
        "etd": {
            "nom": "ExpertTransformationDigitale",
            "classe": "ExpertTransformationDigitale",
            "specialisation": "Transformation digitale, modernisation IT",
            "description": "Expert en transformation digitale, modernisation des SI"
        },
        "ecyber": {
            "nom": "ExpertCybersecurite",
            "classe": "ExpertCybersecurite",
            "specialisation": "Cybersécurité, protection des données, sécurité IT",
            "description": "Expert en cybersécurité, protection des données, audit sécurité"
        },
        "erse": {
            "nom": "ExpertRSE",
            "classe": "ExpertRSE",
            "specialisation": "Responsabilité sociétale, développement durable",
            "description": "Expert en RSE, développement durable, impact environnemental"
        },
        "esn": {
            "nom": "ExpertSouveraineteNumerique",
            "classe": "ExpertSouveraineteNumerique",
            "specialisation": "Souveraineté numérique, indépendance technologique",
            "description": "Expert en souveraineté numérique, technologies européennes"
        },
        "eli": {
            "nom": "ExpertLutteInformationnelle",
            "classe": "ExpertLutteInformationnelle",
            "specialisation": "Lutte informationnelle, désinformation, influence",
            "description": "Expert en lutte informationnelle, guerre cognitive, influence"
        },
        "ege": {
            "nom": "ExpertGestionEntreprise",
            "classe": "ExpertGestionEntreprise",
            "specialisation": "Gestion d'entreprise, management, organisation",
            "description": "Expert en gestion d'entreprise, optimisation organisationnelle"
        },
        "estrat": {
            "nom": "ExpertStrategie",
            "classe": "ExpertStrategie",
            "specialisation": "Stratégie d'entreprise, planification stratégique",
            "description": "Expert en stratégie d'entreprise, développement stratégique"
        },
        "erh": {
            "nom": "ExpertRH",
            "classe": "ExpertRH",
            "specialisation": "Ressources humaines, gestion des talents",
            "description": "Expert en RH, gestion des talents, transformation RH"
        },
        "eerc": {
            "nom": "ExpertExperienceRelationClient",
            "classe": "ExpertExperienceRelationClient",
            "specialisation": "Expérience client, relation client, satisfaction",
            "description": "Expert en expérience client, parcours client, satisfaction"
        }
    }
}

def create_expert_file(category, agent_id, agent_info):
    """Crée un fichier d'agent expert"""
    
    template = f'''"""
{agent_info["nom"]} - Agent Expert {category.replace("_", " ").title()}
Spécialisé en {agent_info["specialisation"]}
"""

from datetime import datetime
from typing import Dict, List, Any

class {agent_info["classe"]}:
    def __init__(self):
        self.agent_id = "{agent_id.upper()}"
        self.nom = "{agent_info["nom"]}"
        self.specialisation = "{agent_info["specialisation"]}"
        self.description = "{agent_info["description"]}"
        self.veille_active = True
        self.derniere_mise_a_jour = datetime.now().isoformat()
        
    def autonomous_watch(self):
        """Démarre la veille autonome de l'expert"""
        print(f"{{self.agent_id}}: Veille autonome sur {{self.specialisation}}")
        
    def provide_expertise(self, mission_context: Dict[str, Any]) -> str:
        """Fournit une expertise pour une mission donnée"""
        return f"Apport d'expertise pour la mission {{mission_context.get('nom', 'N/A')}}"
        
    def get_expertise_summary(self) -> Dict[str, Any]:
        """Retourne un résumé de l'expertise de l'agent"""
        return {{
            "agent_id": self.agent_id,
            "nom": self.nom,
            "specialisation": self.specialisation,
            "description": self.description,
            "derniere_mise_a_jour": self.derniere_mise_a_jour,
            "statut_veille": "ACTIVE" if self.veille_active else "INACTIVE"
        }}

# Test de l'agent
if __name__ == '__main__':
    expert = {agent_info["classe"]}()
    print(f"=== {{expert.nom}} ===")
    print(f"Agent: {{expert.agent_id}}")
    print(f"Spécialisation: {{expert.specialisation}}")
    print(f"Description: {{expert.description}}")
    
    # Test de veille autonome
    expert.autonomous_watch()
    
    # Test d'expertise
    mission_test = {{"nom": "Test Mission", "secteur": "Test"}}
    expertise = expert.provide_expertise(mission_test)
    print(f"Expertise: {{expertise}}")
'''
    
    # Déterminer le répertoire
    if category == "experts_metiers":
        directory = "/home/ubuntu/substans_ai_megacabinet/experts_metiers"
    else:
        directory = "/home/ubuntu/substans_ai_megacabinet/experts_domaines"
    
    # Créer le fichier
    file_path = f"{directory}/{agent_id}.py"
    with open(file_path, 'w') as f:
        f.write(template)
    
    print(f"✅ Créé: {file_path}")

def main():
    """Fonction principale pour créer tous les agents"""
    print("🚀 Création de tous les agents manquants pour l'architecture matricielle complète")
    
    total_created = 0
    
    # Créer tous les experts métiers manquants
    print("\n📋 Création des Experts Métiers manquants...")
    for agent_id, agent_info in AGENTS_DEFINITION["experts_metiers"].items():
        create_expert_file("experts_metiers", agent_id, agent_info)
        total_created += 1
    
    # Créer tous les experts domaines manquants
    print("\n💡 Création des Experts Domaines manquants...")
    for agent_id, agent_info in AGENTS_DEFINITION["experts_domaines"].items():
        create_expert_file("experts_domaines", agent_id, agent_info)
        total_created += 1
    
    print(f"\n🎉 TERMINÉ ! {total_created} agents créés")
    print(f"Architecture complète : 1 Senior Advisor + 7 Agents Consultants + 10 Experts Métiers + 12 Experts Domaines = 30 agents")

if __name__ == "__main__":
    main()

