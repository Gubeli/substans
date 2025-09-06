import json
import os
from methodology_manager import MethodologyManager

class AgentMethodologyIntegration:
    def __init__(self):
        self.methodology_manager = MethodologyManager()
        self.agents_config = self.load_agents_config()
        
    def load_agents_config(self):
        # Configuration des agents existants
        return {
            "senior_advisor": {
                "nom": "Senior Advisor",
                "role": "Orchestration et supervision générale",
                "phases_actives": [1, 4, 6],
                "competences": ["stratégie", "gestion_projet", "client_relation"]
            },
            "avs": {
                "nom": "Agent de Veille Stratégique",
                "role": "Veille et identification d'opportunités",
                "phases_actives": [1, 2],
                "competences": ["veille", "analyse_tendances", "signaux_faibles"]
            },
            "aad": {
                "nom": "Agent d'Analyse de Données",
                "role": "Collecte et analyse quantitative",
                "phases_actives": [2, 3],
                "competences": ["data_analysis", "modélisation", "validation"]
            },
            "arr": {
                "nom": "Agent de Rédaction de Rapports",
                "role": "Production de livrables",
                "phases_actives": [3, 4, 5],
                "competences": ["rédaction", "storytelling", "visualisation"]
            },
            "agc": {
                "nom": "Agent de Gestion des Connaissances",
                "role": "Capitalisation et partage",
                "phases_actives": [5, 6],
                "competences": ["knowledge_management", "documentation", "archivage"]
            },
            "asm": {
                "nom": "Agent de Suivi de Mission",
                "role": "Suivi et amélioration continue",
                "phases_actives": [6],
                "competences": ["suivi_projet", "feedback", "amélioration_continue"]
            }
        }
    
    def integrate_methodology_in_agent(self, agent_id):
        """Intègre la méthodologie dans un agent spécifique"""
        if agent_id not in self.agents_config:
            return False
            
        agent = self.agents_config[agent_id]
        methodology = self.methodology_manager.methodology
        
        # Créer le contexte méthodologique pour l'agent
        agent_methodology_context = {
            "agent_info": agent,
            "phases_responsables": [],
            "workflow_complet": methodology["phases"]
        }
        
        # Identifier les phases où l'agent est actif
        for phase in methodology["phases"]:
            if phase["id"] in agent["phases_actives"]:
                agent_methodology_context["phases_responsables"].append({
                    "phase_id": phase["id"],
                    "nom": phase["nom"],
                    "taches": phase["taches"],
                    "livrables": phase["livrables"],
                    "duree_estimee": phase["duree_estimee_pct"]
                })
        
        # Sauvegarder le contexte méthodologique de l'agent
        context_path = f"/home/ubuntu/substans_ai_megacabinet/{agent_id}/{agent_id}_methodology_context.json"
        os.makedirs(os.path.dirname(context_path), exist_ok=True)
        
        with open(context_path, 'w') as f:
            json.dump(agent_methodology_context, f, indent=2)
            
        return True
    
    def integrate_methodology_in_all_agents(self):
        """Intègre la méthodologie dans tous les agents"""
        results = {}
        
        for agent_id in self.agents_config.keys():
            results[agent_id] = self.integrate_methodology_in_agent(agent_id)
            
        # Intégrer aussi dans les experts métiers et domaines
        experts_metiers = ["ess", "ebf", "ea"]  # Semi-conducteurs, Banque, Assurance
        experts_domaines = ["eia", "ec", "edata"]  # IA, Cloud, Data
        
        for expert_id in experts_metiers + experts_domaines:
            expert_context = {
                "agent_info": {
                    "nom": f"Expert {expert_id.upper()}",
                    "role": "Expertise sectorielle/domaine",
                    "phases_actives": [2, 3],  # Collecte et Analyse
                    "competences": ["expertise_sectorielle", "veille_continue", "validation"]
                },
                "phases_responsables": [
                    {
                        "phase_id": 2,
                        "nom": "Collecte et Validation des Données",
                        "role_expert": "Validation et enrichissement des données sectorielles",
                        "taches": ["Validation des données", "Apport d'expertise", "Identification des sources spécialisées"]
                    },
                    {
                        "phase_id": 3,
                        "nom": "Analyse Approfondie et Synthèse",
                        "role_expert": "Interprétation experte et insights sectoriels",
                        "taches": ["Analyse qualitative", "Insights sectoriels", "Validation des conclusions"]
                    }
                ],
                "workflow_complet": self.methodology_manager.methodology["phases"]
            }
            
            context_path = f"/home/ubuntu/substans_ai_megacabinet/experts_metiers/{expert_id}/{expert_id}_methodology_context.json"
            if expert_id in experts_domaines:
                context_path = f"/home/ubuntu/substans_ai_megacabinet/experts_domaines/{expert_id}/{expert_id}_methodology_context.json"
                
            os.makedirs(os.path.dirname(context_path), exist_ok=True)
            
            with open(context_path, 'w') as f:
                json.dump(expert_context, f, indent=2)
                
            results[expert_id] = True
            
        return results
    
    def get_phase_agents(self, phase_id):
        """Retourne la liste des agents actifs pour une phase donnée"""
        phase = self.methodology_manager.get_phase(phase_id)
        if not phase:
            return []
            
        active_agents = []
        
        # Agents consultants
        for agent_id, agent_config in self.agents_config.items():
            if phase_id in agent_config["phases_actives"]:
                active_agents.append({
                    "id": agent_id,
                    "nom": agent_config["nom"],
                    "role": agent_config["role"]
                })
        
        # Ajouter les experts si phase 2 ou 3
        if phase_id in [2, 3]:
            experts = ["ess", "ebf", "ea", "eia", "ec", "edata"]
            for expert_id in experts:
                active_agents.append({
                    "id": expert_id,
                    "nom": f"Expert {expert_id.upper()}",
                    "role": "Expertise sectorielle/domaine"
                })
                
        return active_agents
    
    def create_mission_orchestration_plan(self, mission_data):
        """Crée un plan d'orchestration pour une mission spécifique"""
        orchestration_plan = {
            "mission_id": mission_data.get("id", "unknown"),
            "mission_name": mission_data.get("nom", "Mission sans nom"),
            "phases_execution": []
        }
        
        for phase in self.methodology_manager.methodology["phases"]:
            phase_plan = {
                "phase_id": phase["id"],
                "phase_nom": phase["nom"],
                "agents_assignes": self.get_phase_agents(phase["id"]),
                "livrables_attendus": phase["livrables"],
                "taches": phase["taches"],
                "duree_estimee_pct": phase["duree_estimee_pct"],
                "statut": "en_attente"
            }
            orchestration_plan["phases_execution"].append(phase_plan)
            
        return orchestration_plan

# Test du système d'intégration
if __name__ == '__main__':
    integrator = AgentMethodologyIntegration()
    
    print("=== Intégration de la méthodologie dans tous les agents ===")
    results = integrator.integrate_methodology_in_all_agents()
    
    for agent_id, success in results.items():
        status = "✓ Succès" if success else "✗ Échec"
        print(f"{agent_id}: {status}")
    
    print("\n=== Agents actifs pour la Phase 2 (Collecte et Validation) ===")
    phase2_agents = integrator.get_phase_agents(2)
    for agent in phase2_agents:
        print(f"- {agent['nom']} ({agent['id']}): {agent['role']}")
    
    print("\n=== Plan d'orchestration pour une mission test ===")
    mission_test = {"id": "mission_001", "nom": "Analyse Marché FinTech"}
    plan = integrator.create_mission_orchestration_plan(mission_test)
    
    print(f"Mission: {plan['mission_name']}")
    for phase_plan in plan["phases_execution"]:
        print(f"\nPhase {phase_plan['phase_id']}: {phase_plan['phase_nom']}")
        print(f"  Agents: {', '.join([a['nom'] for a in phase_plan['agents_assignes']])}")
        print(f"  Livrables: {', '.join(phase_plan['livrables_attendus'])}")

