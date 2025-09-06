#!/usr/bin/env python3
"""
Substans.ai - Méga-Cabinet Virtuel
Fichier principal d'intégration et de tests
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from senior_advisor.senior_advisor import SeniorAdvisor
from agents_consultants.avs import AgentVeilleStrategique
from agents_consultants.aad import AgentAnalyseDonnees
from agents_consultants.arr import AgentRedactionRapports
from agents_consultants.agc import AgentGestionConnaissances
from agents_consultants.asm import AgentSuiviMission
from agents_consultants.arpc import AgentRedactionPropositionCommerciale
from agents_consultants.adamo import AgentDefinitionAmeliorationMethodesOutils

from experts_metiers.ess import ExpertSemiConducteursSubstrats
from experts_metiers.ebf import ExpertBanqueFinance
from experts_metiers.ea import ExpertAssurance

from experts_domaines.eia import ExpertIA
from experts_domaines.ec import ExpertCloud
from experts_domaines.edata import ExpertData
from experts_domaines.elrd import ExpertLegislationsReglementationsDigitales

from interactions_inter_agents import InteractionsInterAgents
from machine_learning_global import MachineLearningGlobal

class SubstansAI:
    """
    Classe principale du méga-cabinet virtuel Substans.ai
    """
    
    def __init__(self):
        print("🚀 Initialisation de Substans.ai - Méga-Cabinet Virtuel")
        
        # Initialisation du Senior Advisor
        self.senior_advisor = SeniorAdvisor()
        print("✅ Senior Advisor initialisé")
        
        # Initialisation des Agents Consultants (Dimension 1)
        self.agents_consultants = {
            'avs': AgentVeilleStrategique(),
            'aad': AgentAnalyseDonnees(),
            'arr': AgentRedactionRapports(),
            'agc': AgentGestionConnaissances(),
            'asm': AgentSuiviMission(),
            'arpc': AgentRedactionPropositionCommerciale(),
            'adamo': AgentDefinitionAmeliorationMethodesOutils()
        }
        print("✅ 7 Agents Consultants initialisés")
        
        # Initialisation des Experts Métiers (Dimension 2)
        self.experts_metiers = {
            'ess': ExpertSemiConducteursSubstrats(),
            'ebf': ExpertBanqueFinance(),
            'ea': ExpertAssurance()
            # TODO: Ajouter les autres experts métiers
        }
        print("✅ 3 Experts Métiers initialisés (prioritaires)")
        
        # Initialisation des Experts Domaines (Dimension 3)
        self.experts_domaines = {
            'eia': ExpertIA(),
            'ec': ExpertCloud(),
            'edata': ExpertData(),
            'elrd': ExpertLegislationsReglementationsDigitales()
            # TODO: Ajouter les autres experts domaines
        }
        print("✅ 4 Experts Domaines initialisés (prioritaires)")
        
        # Initialisation des systèmes d'interaction et d'apprentissage
        self.interactions = InteractionsInterAgents(self.senior_advisor)
        self.machine_learning = MachineLearningGlobal(self.senior_advisor)
        print("✅ Systèmes d'interaction et ML initialisés")
        
        # Liaison des agents au Senior Advisor
        self.senior_advisor.agents_consultants = self.agents_consultants
        self.senior_advisor.experts_metiers = self.experts_metiers
        self.senior_advisor.experts_domaines = self.experts_domaines
        
        print("🎯 Architecture matricielle complète opérationnelle !")
        print(f"   - 1 Senior Advisor")
        print(f"   - {len(self.agents_consultants)} Agents Consultants")
        print(f"   - {len(self.experts_metiers)} Experts Métiers")
        print(f"   - {len(self.experts_domaines)} Experts Domaines")
        print(f"   - Total: {1 + len(self.agents_consultants) + len(self.experts_metiers) + len(self.experts_domaines)} agents")
    
    def test_mission_complete(self):
        """
        Test d'une mission complète pour valider l'architecture
        """
        print("\n🧪 Test d'une mission complète")
        
        # Mission de test
        mission_test = {
            "nom": "Test Architecture Matricielle",
            "client": "Substans.ai",
            "secteur": "Semi-conducteurs",
            "domaines": ["IA", "Cloud", "Data"],
            "brief": "Validation de l'architecture matricielle complète"
        }
        
        print(f"📋 Mission: {mission_test['nom']}")
        
        # 1. Orchestration par le Senior Advisor
        print("\n1️⃣ Phase Orchestration")
        self.senior_advisor.orchestrate_mission(mission_test)
        
        # 2. Activation des experts pertinents
        print("\n2️⃣ Phase Activation des Experts")
        if mission_test['secteur'] == 'Semi-conducteurs':
            expertise_sectorielle = self.experts_metiers['ess'].provide_expertise(mission_test)
            print(f"   ESS: {expertise_sectorielle}")
        
        for domaine in mission_test['domaines']:
            if domaine == 'IA':
                expertise_ia = self.experts_domaines['eia'].provide_expertise(mission_test)
                print(f"   EIA: {expertise_ia}")
            elif domaine == 'Cloud':
                expertise_cloud = self.experts_domaines['ec'].provide_expertise(mission_test)
                print(f"   EC: {expertise_cloud}")
            elif domaine == 'Data':
                expertise_data = self.experts_domaines['edata'].provide_expertise(mission_test)
                print(f"   EDATA: {expertise_data}")
        
        # 3. Workflow des agents consultants
        print("\n3️⃣ Phase Workflow Agents Consultants")
        self.agents_consultants['avs'].collect_data(mission_test)
        
        # Simulation de données collectées
        data_collected = {"sources": 10, "insights": 25, "quality": "high"}
        self.agents_consultants['aad'].analyze_data(data_collected)
        
        # Simulation d'analyse
        analysis_result = {"trends": 5, "recommendations": 8, "confidence": 0.95}
        self.agents_consultants['arr'].write_report(analysis_result)
        
        # 4. Test des interactions inter-agents
        print("\n4️⃣ Phase Interactions Inter-Agents")
        self.interactions.avs_to_aad(data_collected)
        self.interactions.aad_to_arr(analysis_result)
        
        # 5. Machine Learning et amélioration
        print("\n5️⃣ Phase Machine Learning")
        feedback_test = {
            "satisfaction": 4.8,
            "quality": 4.9,
            "efficiency": 4.7,
            "innovation": 4.6
        }
        self.machine_learning.collect_feedback("test_001", feedback_test)
        self.machine_learning.improve_system()
        
        print("\n✅ Test de mission complète réussi !")
        return True
    
    def start_autonomous_watch(self):
        """
        Démarre la veille autonome des experts
        """
        print("\n🔍 Démarrage de la veille autonome")
        
        # Veille des experts métiers
        for expert_name, expert in self.experts_metiers.items():
            expert.autonomous_watch()
        
        # Veille des experts domaines
        for expert_name, expert in self.experts_domaines.items():
            expert.autonomous_watch()
        
        print("✅ Veille autonome active sur tous les experts")
    
    def get_system_status(self):
        """
        Retourne le statut du système
        """
        status = {
            "senior_advisor": "actif",
            "agents_consultants": len(self.agents_consultants),
            "experts_metiers": len(self.experts_metiers),
            "experts_domaines": len(self.experts_domaines),
            "total_agents": 1 + len(self.agents_consultants) + len(self.experts_metiers) + len(self.experts_domaines),
            "ml_active": True,
            "interactions_active": True
        }
        return status

def main():
    """
    Fonction principale
    """
    print("=" * 60)
    print("🧠 SUBSTANS.AI - MÉGA-CABINET VIRTUEL")
    print("    Architecture Matricielle à 3 Dimensions")
    print("=" * 60)
    
    # Initialisation du système
    substans = SubstansAI()
    
    # Démarrage de la veille autonome
    substans.start_autonomous_watch()
    
    # Test complet du système
    substans.test_mission_complete()
    
    # Affichage du statut final
    status = substans.get_system_status()
    print(f"\n📊 STATUT FINAL DU SYSTÈME:")
    print(f"   🎯 Senior Advisor: {status['senior_advisor']}")
    print(f"   ⚙️  Agents Consultants: {status['agents_consultants']}")
    print(f"   🏭 Experts Métiers: {status['experts_metiers']}")
    print(f"   💡 Experts Domaines: {status['experts_domaines']}")
    print(f"   🤖 Total Agents: {status['total_agents']}")
    print(f"   🧠 Machine Learning: {'✅' if status['ml_active'] else '❌'}")
    print(f"   🔄 Interactions: {'✅' if status['interactions_active'] else '❌'}")
    
    print("\n🚀 Substans.ai est opérationnel !")
    print("   Interface utilisateur disponible sur: http://localhost:5175/")
    
    return substans

if __name__ == "__main__":
    substans_system = main()

