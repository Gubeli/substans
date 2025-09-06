#!/usr/bin/env python3
"""
Senior Advisor Orchestrator - Point d'entrée unique pour toutes les interactions
Le Senior Advisor analyse chaque demande et active automatiquement les agents pertinents
"""

import json
import time
from datetime import datetime
from typing import List, Dict, Any

class SeniorAdvisorOrchestrator:
    def __init__(self):
        self.name = "Senior Advisor"
        self.role = "Orchestrateur Central - Point d'entrée unique"
        self.active_agents = []
        self.mission_context = {}
        self.interaction_history = []
        
        # Mapping des domaines vers les experts
        self.domain_experts = {
            "strategie": ["ESTRAT", "Senior Advisor"],
            "ia": ["EIA", "EDDI", "ESS"],
            "data": ["EDATA", "EDDI", "AAD"],
            "cloud": ["EC", "ETD"],
            "cybersecurite": ["ECYBER", "ELRD"],
            "finance": ["EBF", "ESTRAT"],
            "digital": ["EDDI", "ETD", "EIA"],
            "semiconducteurs": ["ESS", "ESTRAT", "ESN"],
            "reglementaire": ["ELRD", "ESN"],
            "souverainete": ["ESN", "ELRD", "ESS"],
            "transformation": ["ETD", "ESTRAT", "EDDI"],
            "business_plan": ["ESTRAT", "EBF", "AAD"],
            "proposition_commerciale": ["ARPC", "ESTRAT", "ASM"],
            "analyse_marche": ["AVS", "AAD", "ESTRAT"],
            "veille": ["AVS", "AGC"],
            "redaction": ["ARR", "ARPC"],
            "gestion_projet": ["ASM", "ADAMO"]
        }
        
        # Mapping des secteurs vers les experts métiers
        self.sector_experts = {
            "banque_finance": ["EBF"],
            "assurance": ["EA"],
            "retail": ["ER"],
            "manufacturing": ["EM"],
            "automobile": ["EAUTO"],
            "transport_logistique": ["ETL"],
            "services_publics": ["ESP"],
            "defense": ["ED"],
            "semiconducteurs": ["ESS"],
            "energie": ["EE"],
            "digital_data_ia": ["EDDI"]
        }

    def process_user_request(self, user_message: str, mission_context: Dict = None) -> Dict[str, Any]:
        """
        Point d'entrée unique pour toutes les demandes utilisateur
        Le Senior Advisor analyse et orchestre la réponse
        """
        print(f"\n🎯 Senior Advisor: Analyse de votre demande...")
        
        # Enregistrer l'interaction
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "mission_context": mission_context
        }
        self.interaction_history.append(interaction)
        
        # Analyse de la demande
        analysis = self._analyze_request(user_message, mission_context)
        
        # Activation des agents pertinents
        activated_agents = self._activate_relevant_agents(analysis)
        
        # Orchestration de la réponse
        response = self._orchestrate_response(analysis, activated_agents, mission_context)
        
        return {
            "senior_advisor_analysis": analysis,
            "activated_agents": activated_agents,
            "orchestrated_response": response,
            "interaction_id": len(self.interaction_history)
        }

    def _analyze_request(self, message: str, context: Dict = None) -> Dict[str, Any]:
        """Analyse intelligente de la demande utilisateur"""
        message_lower = message.lower()
        
        analysis = {
            "intent": self._detect_intent(message_lower),
            "domains": self._detect_domains(message_lower),
            "sectors": self._detect_sectors(message_lower, context),
            "deliverables": self._detect_deliverables(message_lower),
            "urgency": self._detect_urgency(message_lower),
            "complexity": self._assess_complexity(message_lower, context)
        }
        
        print(f"📊 Analyse: Intent={analysis['intent']}, Domaines={analysis['domains']}, Secteurs={analysis['sectors']}")
        return analysis

    def _detect_intent(self, message: str) -> str:
        """Détecte l'intention principale de la demande"""
        if any(word in message for word in ["livrable", "document", "rapport", "présentation"]):
            return "consultation_livrables"
        elif any(word in message for word in ["itération", "améliorer", "modifier", "corriger"]):
            return "iteration_livrable"
        elif any(word in message for word in ["nouvelle mission", "créer", "lancer"]):
            return "creation_mission"
        elif any(word in message for word in ["stratégie", "plan", "vision"]):
            return "conseil_strategique"
        elif any(word in message for word in ["analyse", "étude", "recherche"]):
            return "analyse_approfondie"
        elif any(word in message for word in ["proposition", "commercial", "offre"]):
            return "proposition_commerciale"
        else:
            return "conseil_general"

    def _detect_domains(self, message: str) -> List[str]:
        """Détecte les domaines d'expertise concernés"""
        domains = []
        domain_keywords = {
            "strategie": ["stratégie", "plan", "vision", "objectif"],
            "ia": ["ia", "intelligence artificielle", "machine learning", "ai"],
            "data": ["data", "données", "analytics", "big data"],
            "cloud": ["cloud", "infrastructure", "saas", "paas"],
            "cybersecurite": ["cybersécurité", "sécurité", "cyber", "protection"],
            "digital": ["digital", "numérique", "transformation"],
            "semiconducteurs": ["semiconducteur", "puce", "chip", "sequana"],
            "reglementaire": ["rgpd", "dma", "dsa", "réglementation", "compliance"],
            "finance": ["finance", "financier", "budget", "roi", "business plan"]
        }
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in message for keyword in keywords):
                domains.append(domain)
        
        return domains

    def _detect_sectors(self, message: str, context: Dict = None) -> List[str]:
        """Détecte les secteurs d'activité concernés"""
        sectors = []
        
        # Secteur depuis le contexte de mission
        if context and "secteur" in context:
            sector_mapping = {
                "Banque & Finance": "banque_finance",
                "Digital, Data, IA": "digital_data_ia",
                "Semi-conducteurs": "semiconducteurs"
            }
            if context["secteur"] in sector_mapping:
                sectors.append(sector_mapping[context["secteur"]])
        
        # Détection par mots-clés
        sector_keywords = {
            "banque_finance": ["banque", "finance", "bancaire"],
            "semiconducteurs": ["semiconducteur", "bull", "sequana", "hpc"],
            "digital_data_ia": ["digital", "data", "ia", "numérique"]
        }
        
        for sector, keywords in sector_keywords.items():
            if any(keyword in message for keyword in keywords):
                if sector not in sectors:
                    sectors.append(sector)
        
        return sectors

    def _detect_deliverables(self, message: str) -> List[str]:
        """Détecte les types de livrables demandés"""
        deliverables = []
        deliverable_keywords = {
            "proposition_commerciale": ["proposition", "commercial", "offre", "devis"],
            "business_plan": ["business plan", "plan d'affaires", "projections"],
            "analyse_strategique": ["analyse", "stratégique", "diagnostic"],
            "etude_marche": ["étude", "marché", "concurrence"],
            "presentation": ["présentation", "slides", "powerpoint"]
        }
        
        for deliverable, keywords in deliverable_keywords.items():
            if any(keyword in message for keyword in keywords):
                deliverables.append(deliverable)
        
        return deliverables

    def _detect_urgency(self, message: str) -> str:
        """Détecte le niveau d'urgence"""
        if any(word in message for word in ["urgent", "demain", "immédiat", "asap"]):
            return "haute"
        elif any(word in message for word in ["semaine", "rapide", "vite"]):
            return "moyenne"
        else:
            return "normale"

    def _assess_complexity(self, message: str, context: Dict = None) -> str:
        """Évalue la complexité de la demande"""
        complexity_indicators = 0
        
        # Indicateurs de complexité
        if len(message.split()) > 50:
            complexity_indicators += 1
        if context and len(context.get("domaines", [])) > 3:
            complexity_indicators += 1
        if any(word in message for word in ["complet", "détaillé", "approfondi"]):
            complexity_indicators += 1
        
        if complexity_indicators >= 2:
            return "elevee"
        elif complexity_indicators == 1:
            return "moyenne"
        else:
            return "faible"

    def _activate_relevant_agents(self, analysis: Dict[str, Any]) -> List[str]:
        """Active automatiquement les agents pertinents selon l'analyse"""
        activated = ["Senior Advisor"]  # Toujours inclus
        
        print(f"🔄 Activation des agents selon l'analyse...")
        
        # Activation par domaines
        for domain in analysis["domains"]:
            if domain in self.domain_experts:
                for agent in self.domain_experts[domain]:
                    if agent not in activated:
                        activated.append(agent)
                        print(f"  ✅ {agent} activé pour le domaine {domain}")
        
        # Activation par secteurs
        for sector in analysis["sectors"]:
            if sector in self.sector_experts:
                for agent in self.sector_experts[sector]:
                    if agent not in activated:
                        activated.append(agent)
                        print(f"  ✅ {agent} activé pour le secteur {sector}")
        
        # Activation par intent
        intent_agents = {
            "consultation_livrables": ["ARR", "AGC"],
            "iteration_livrable": ["ARR", "ADAMO"],
            "creation_mission": ["ASM", "ADAMO"],
            "conseil_strategique": ["ESTRAT", "AVS"],
            "analyse_approfondie": ["AAD", "AVS", "ARR"],
            "proposition_commerciale": ["ARPC", "ESTRAT"]
        }
        
        if analysis["intent"] in intent_agents:
            for agent in intent_agents[analysis["intent"]]:
                if agent not in activated:
                    activated.append(agent)
                    print(f"  ✅ {agent} activé pour l'intent {analysis['intent']}")
        
        # Activation selon complexité
        if analysis["complexity"] == "elevee":
            additional_agents = ["AGC", "ADAMO"]  # Gestion des connaissances et méthodes
            for agent in additional_agents:
                if agent not in activated:
                    activated.append(agent)
                    print(f"  ✅ {agent} activé pour complexité élevée")
        
        self.active_agents = activated
        print(f"🎯 Total: {len(activated)} agents activés")
        return activated

    def _orchestrate_response(self, analysis: Dict, agents: List[str], context: Dict = None) -> Dict[str, Any]:
        """Orchestre la réponse coordonnée de tous les agents"""
        print(f"\n🎼 Orchestration de la réponse avec {len(agents)} agents...")
        
        response = {
            "senior_advisor_message": self._generate_senior_advisor_response(analysis, context),
            "agents_contributions": {},
            "deliverables_available": [],
            "next_actions": [],
            "coordination_summary": ""
        }
        
        # Simulation des contributions des agents
        for agent in agents:
            if agent != "Senior Advisor":
                contribution = self._simulate_agent_contribution(agent, analysis, context)
                response["agents_contributions"][agent] = contribution
                print(f"  📝 {agent}: {contribution['summary']}")
        
        # Génération des livrables disponibles
        if analysis["intent"] == "consultation_livrables" and context:
            response["deliverables_available"] = self._get_available_deliverables(context)
        
        # Définition des prochaines actions
        response["next_actions"] = self._define_next_actions(analysis, context)
        
        # Résumé de coordination
        response["coordination_summary"] = f"Coordination de {len(agents)} agents pour répondre à votre demande {analysis['intent']}"
        
        return response

    def _generate_senior_advisor_response(self, analysis: Dict, context: Dict = None) -> str:
        """Génère la réponse principale du Senior Advisor"""
        intent = analysis["intent"]
        
        if intent == "consultation_livrables":
            return f"""🎯 **Senior Advisor - Consultation des Livrables**

J'ai analysé votre demande et coordonné avec les agents appropriés :

✅ **Agents mobilisés** : {', '.join(self.active_agents)}
📋 **Livrables disponibles** : Tous les documents de la mission sont prêts
🔄 **Actions possibles** : Consultation, téléchargement, itération

Les agents ARR et AGC ont préparé l'accès à tous vos documents. Souhaitez-vous consulter un livrable spécifique ?"""

        elif intent == "iteration_livrable":
            return f"""🔄 **Senior Advisor - Itération sur Livrable**

J'orchestre l'amélioration de votre livrable :

✅ **Agents mobilisés** : {', '.join(self.active_agents)}
🎯 **Processus d'itération** : Analyse → Amélioration → Validation
⏱️ **Délai estimé** : Nouvelle version dans quelques instants

Les agents ARR et ADAMO analysent vos commentaires pour produire une version améliorée."""

        elif intent == "conseil_strategique":
            return f"""🎯 **Senior Advisor - Conseil Stratégique**

J'ai activé l'équipe stratégique pour votre demande :

✅ **Experts mobilisés** : {', '.join(self.active_agents)}
📊 **Analyse en cours** : Diagnostic → Vision → Recommandations
🎯 **Livrables prévus** : Analyse stratégique, recommandations, roadmap

L'équipe ESTRAT et les experts sectoriels préparent une analyse complète."""

        else:
            return f"""🤖 **Senior Advisor à votre service**

J'ai analysé votre demande et coordonné la réponse :

✅ **{len(self.active_agents)} agents mobilisés** selon vos besoins
🎯 **Intent détecté** : {intent}
📋 **Domaines couverts** : {', '.join(analysis['domains']) if analysis['domains'] else 'Conseil général'}

Tous les agents pertinents sont maintenant actifs pour vous assister. Comment puis-je vous aider davantage ?"""

    def _simulate_agent_contribution(self, agent: str, analysis: Dict, context: Dict = None) -> Dict[str, str]:
        """Simule la contribution de chaque agent activé"""
        contributions = {
            "ARR": {
                "summary": "Préparation des documents et livrables pour consultation",
                "details": "Formatage des documents, vérification de la cohérence, préparation des exports multi-formats"
            },
            "ARPC": {
                "summary": "Optimisation de la proposition commerciale",
                "details": "Révision tarifaire, ajustement du positionnement, amélioration de la présentation"
            },
            "ESTRAT": {
                "summary": "Analyse stratégique et recommandations",
                "details": "Diagnostic approfondi, définition de la vision, élaboration des recommandations stratégiques"
            },
            "ESS": {
                "summary": "Expertise semi-conducteurs et technologies BullSequana",
                "details": "Analyse technique des gammes XH3000/X400, positionnement concurrentiel, roadmap technologique"
            },
            "EDDI": {
                "summary": "Expertise Digital, Data et IA",
                "details": "Analyse des enjeux de transformation digitale, stratégie data, opportunités IA"
            },
            "AAD": {
                "summary": "Analyse de données et benchmarks",
                "details": "Collecte et analyse des données marché, benchmarks concurrentiels, KPIs sectoriels"
            },
            "AVS": {
                "summary": "Veille stratégique et intelligence marché",
                "details": "Surveillance des tendances, analyse concurrentielle, identification des opportunités"
            }
        }
        
        return contributions.get(agent, {
            "summary": f"Contribution spécialisée de {agent}",
            "details": f"Expertise et analyse selon le domaine de {agent}"
        })

    def _get_available_deliverables(self, context: Dict) -> List[Dict]:
        """Récupère les livrables disponibles pour la mission"""
        if context and "livrables" in context:
            return context["livrables"]
        
        # Livrables par défaut pour mission Bull
        return [
            {
                "nom": "Proposition Commerciale Bull",
                "type": "document",
                "statut": "Terminé",
                "description": "Proposition commerciale complète (450k€, 13 semaines)"
            },
            {
                "nom": "Analyse Stratégique Bull", 
                "type": "document",
                "statut": "Terminé",
                "description": "Analyse des 4 piliers et positionnement concurrentiel"
            },
            {
                "nom": "Business Plan Bull 2025-2030",
                "type": "document", 
                "statut": "Terminé",
                "description": "Projections financières et plan d'exécution détaillé"
            }
        ]

    def _define_next_actions(self, analysis: Dict, context: Dict = None) -> List[Dict]:
        """Définit les prochaines actions recommandées"""
        actions = []
        
        if analysis["intent"] == "consultation_livrables":
            actions = [
                {"label": "Consulter un livrable spécifique", "priority": "haute"},
                {"label": "Télécharger tous les documents", "priority": "moyenne"},
                {"label": "Demander une itération", "priority": "faible"}
            ]
        elif analysis["intent"] == "iteration_livrable":
            actions = [
                {"label": "Attendre la nouvelle version", "priority": "haute"},
                {"label": "Préciser les modifications", "priority": "moyenne"},
                {"label": "Valider les changements", "priority": "faible"}
            ]
        else:
            actions = [
                {"label": "Préciser vos besoins", "priority": "haute"},
                {"label": "Consulter les livrables existants", "priority": "moyenne"},
                {"label": "Lancer une nouvelle analyse", "priority": "faible"}
            ]
        
        return actions

    def get_orchestration_status(self) -> Dict[str, Any]:
        """Retourne le statut de l'orchestration"""
        return {
            "senior_advisor": self.name,
            "active_agents": self.active_agents,
            "total_interactions": len(self.interaction_history),
            "last_interaction": self.interaction_history[-1] if self.interaction_history else None,
            "orchestration_mode": "centralized_through_senior_advisor"
        }

# Test du système d'orchestration
if __name__ == "__main__":
    orchestrator = SeniorAdvisorOrchestrator()
    
    # Test 1: Consultation des livrables
    print("=== TEST 1: Consultation des livrables ===")
    response1 = orchestrator.process_user_request(
        "Montrez-moi tous les livrables de la mission Bull",
        {"secteur": "Digital, Data, IA", "nom": "Vision & Plan Stratégique - Bull HPC/IA"}
    )
    print(f"Réponse Senior Advisor: {response1['orchestrated_response']['senior_advisor_message']}")
    
    # Test 2: Demande d'itération
    print("\n=== TEST 2: Demande d'itération ===")
    response2 = orchestrator.process_user_request(
        "Je veux améliorer la proposition commerciale Bull, ajouter plus de détails sur BullSequana XH3000"
    )
    print(f"Réponse Senior Advisor: {response2['orchestrated_response']['senior_advisor_message']}")
    
    # Test 3: Conseil stratégique
    print("\n=== TEST 3: Conseil stratégique ===")
    response3 = orchestrator.process_user_request(
        "Analysez la stratégie de souveraineté numérique pour Bull dans le contexte européen"
    )
    print(f"Réponse Senior Advisor: {response3['orchestrated_response']['senior_advisor_message']}")
    
    print(f"\n📊 Statut final: {orchestrator.get_orchestration_status()}")

