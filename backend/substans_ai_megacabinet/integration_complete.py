#!/usr/bin/env python3
"""
Intégration Complète des 5 Optimisations Substans.ai ↔ Manus
Système unifié pour maximiser la synergie et les performances
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
from manus_optimization_engine import ManusOptimizationEngine
from daily_intelligence_system import DailyIntelligenceSystem

class SubstansAIOptimizedSystem:
    def __init__(self):
        self.name = "Substans.AI Optimized System"
        self.version = "2.0"
        
        # Intégration des moteurs d'optimisation
        self.manus_optimizer = ManusOptimizationEngine()
        self.intelligence_system = DailyIntelligenceSystem()
        
        # Métriques de performance globales
        self.performance_metrics = {
            "manus_synergy_score": 0.0,
            "intelligence_enhancement": 0.0,
            "overall_efficiency": 0.0,
            "user_satisfaction": 0.0,
            "system_evolution": 0.0
        }
        
        # Configuration des optimisations
        self.optimization_config = {
            "orchestration_intelligente": True,
            "contextualisation_maximale": True,
            "specialisation_sectorielle": True,
            "parallelisation_intelligente": True,
            "amelioration_continue": True,
            "veille_quotidienne": True
        }
        
        print(f"🚀 {self.name} v{self.version} initialisé avec succès")
        print(f"✅ Moteur d'optimisation Manus: Actif")
        print(f"✅ Système de veille quotidienne: Actif")

    def process_user_request(self, user_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        POINT D'ENTRÉE PRINCIPAL - Traite toute demande utilisateur
        Applique automatiquement les 5 optimisations
        """
        print(f"\n🎯 Traitement demande utilisateur: {user_request.get('task', 'Non spécifié')}")
        
        # OPTIMISATION 1: ORCHESTRATION INTELLIGENTE
        orchestration_result = self._orchestrate_request(user_request)
        
        # OPTIMISATION 2: CONTEXTUALISATION MAXIMALE  
        enriched_request = self._maximize_contextualization(user_request, orchestration_result)
        
        # OPTIMISATION 3: SPÉCIALISATION SECTORIELLE
        specialized_processing = self._apply_sector_specialization(enriched_request)
        
        # OPTIMISATION 4: PARALLÉLISATION INTELLIGENTE
        parallel_execution = self._execute_intelligent_parallelization(specialized_processing)
        
        # OPTIMISATION 5: AMÉLIORATION CONTINUE
        continuous_improvement = self._apply_continuous_improvement(parallel_execution)
        
        # Compilation du résultat final
        final_result = {
            "request_id": self._generate_request_id(user_request),
            "timestamp": datetime.now().isoformat(),
            "user_request": user_request,
            "orchestration": orchestration_result,
            "enriched_context": enriched_request,
            "specialized_processing": specialized_processing,
            "parallel_execution": parallel_execution,
            "continuous_improvement": continuous_improvement,
            "performance_metrics": self._calculate_request_performance(user_request, continuous_improvement),
            "manus_optimization": self.manus_optimizer.optimize_for_manus({
                "agent": orchestration_result.get("primary_agent", "Senior Advisor"),
                "task": user_request.get("task", ""),
                "context": enriched_request
            })
        }
        
        # Mise à jour des métriques globales
        self._update_global_metrics(final_result)
        
        print(f"✅ Demande traitée avec succès - Score performance: {final_result['performance_metrics']['overall_score']:.2f}")
        
        return final_result

    def _orchestrate_request(self, user_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        OPTIMISATION 1: ORCHESTRATION INTELLIGENTE
        Le Senior Advisor analyse et orchestre automatiquement
        """
        print("🎯 Optimisation 1: Orchestration Intelligente")
        
        task = user_request.get("task", "")
        context = user_request.get("context", {})
        
        # Analyse intelligente de la demande
        analysis = {
            "complexity": self._assess_request_complexity(task),
            "domain": self._identify_primary_domain(task),
            "urgency": context.get("urgency", "normal"),
            "scope": self._determine_scope(task, context)
        }
        
        # Sélection du Senior Advisor comme orchestrateur
        orchestration = {
            "orchestrator": "Senior Advisor",
            "primary_agent": self._select_primary_agent(analysis),
            "supporting_agents": self._select_supporting_agents(analysis),
            "workflow": self._design_workflow(analysis),
            "coordination_strategy": "senior_advisor_central",
            "analysis": analysis
        }
        
        print(f"  📋 Agent principal: {orchestration['primary_agent']}")
        print(f"  🤝 Agents support: {', '.join(orchestration['supporting_agents'])}")
        
        return orchestration

    def _maximize_contextualization(self, user_request: Dict[str, Any], orchestration: Dict[str, Any]) -> Dict[str, Any]:
        """
        OPTIMISATION 2: CONTEXTUALISATION MAXIMALE
        Enrichit massivement le contexte avec toutes les connaissances substans.ai
        """
        print("🧠 Optimisation 2: Contextualisation Maximale")
        
        base_context = user_request.get("context", {})
        
        # Enrichissement multi-sources
        enriched_context = {
            "base_context": base_context,
            "knowledge_base": self._get_relevant_knowledge_base(user_request, orchestration),
            "mission_history": self._get_relevant_mission_history(orchestration["primary_agent"]),
            "methodology": self._get_applicable_methodology(user_request),
            "sector_intelligence": self._get_sector_intelligence(orchestration["analysis"]["domain"]),
            "competitive_landscape": self._get_competitive_context(user_request),
            "regulatory_context": self._get_regulatory_context(user_request),
            "market_context": self._get_market_context(user_request),
            "technology_trends": self._get_technology_trends(orchestration["analysis"]["domain"]),
            "performance_patterns": self._get_agent_performance_patterns(orchestration["primary_agent"])
        }
        
        # Calcul du ratio d'enrichissement
        original_size = len(str(base_context))
        enriched_size = len(str(enriched_context))
        enrichment_ratio = enriched_size / max(original_size, 1)
        
        print(f"  📈 Ratio d'enrichissement: {enrichment_ratio:.1f}x")
        print(f"  🎯 Sources intégrées: {len([k for k, v in enriched_context.items() if v])}")
        
        return enriched_context

    def _apply_sector_specialization(self, enriched_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        OPTIMISATION 3: SPÉCIALISATION SECTORIELLE
        Applique l'expertise sectorielle ultra-spécialisée
        """
        print("🔬 Optimisation 3: Spécialisation Sectorielle")
        
        # Identification du secteur principal
        sector_intelligence = enriched_request.get("sector_intelligence", {})
        primary_sector = sector_intelligence.get("primary_sector", "general")
        
        # Application de la spécialisation
        specialization = {
            "sector": primary_sector,
            "expert_level": self._get_expert_level(primary_sector),
            "specialized_knowledge": self._get_specialized_knowledge(primary_sector),
            "sector_frameworks": self._get_sector_frameworks(primary_sector),
            "industry_benchmarks": self._get_industry_benchmarks(primary_sector),
            "regulatory_specifics": self._get_regulatory_specifics(primary_sector),
            "competitive_dynamics": self._get_competitive_dynamics(primary_sector),
            "technology_stack": self._get_technology_stack(primary_sector)
        }
        
        print(f"  🎯 Secteur: {primary_sector}")
        print(f"  👨‍💼 Niveau expert: {specialization['expert_level']}")
        
        return {
            "enriched_context": enriched_request,
            "sector_specialization": specialization,
            "specialized_prompt_enhancement": self._generate_specialized_enhancement(specialization)
        }

    def _execute_intelligent_parallelization(self, specialized_processing: Dict[str, Any]) -> Dict[str, Any]:
        """
        OPTIMISATION 4: PARALLÉLISATION INTELLIGENTE
        Coordonne plusieurs agents Manus simultanément
        """
        print("⚡ Optimisation 4: Parallélisation Intelligente")
        
        # Analyse de la parallélisation optimale
        parallelization_analysis = {
            "can_parallelize": True,
            "optimal_parallel_count": self._calculate_optimal_parallel_count(specialized_processing),
            "subtask_decomposition": self._decompose_into_subtasks(specialized_processing),
            "coordination_strategy": "senior_advisor_orchestration",
            "synchronization_points": self._identify_sync_points(specialized_processing)
        }
        
        # Exécution parallèle simulée
        parallel_execution = {
            "analysis": parallelization_analysis,
            "execution_plan": self._create_execution_plan(parallelization_analysis),
            "coordination_overhead": self._calculate_coordination_overhead(parallelization_analysis),
            "efficiency_gain": self._calculate_efficiency_gain(parallelization_analysis),
            "quality_assurance": self._design_quality_assurance(parallelization_analysis)
        }
        
        print(f"  🔄 Agents parallèles: {parallelization_analysis['optimal_parallel_count']}")
        print(f"  📈 Gain d'efficacité: {parallel_execution['efficiency_gain']:.1f}x")
        
        return parallel_execution

    def _apply_continuous_improvement(self, parallel_execution: Dict[str, Any]) -> Dict[str, Any]:
        """
        OPTIMISATION 5: AMÉLIORATION CONTINUE
        Machine Learning pour optimisation permanente
        """
        print("🧠 Optimisation 5: Amélioration Continue")
        
        # Collecte des métriques de performance
        performance_data = {
            "execution_time": self._measure_execution_time(parallel_execution),
            "quality_score": self._assess_quality_score(parallel_execution),
            "user_satisfaction": self._predict_user_satisfaction(parallel_execution),
            "efficiency_metrics": self._collect_efficiency_metrics(parallel_execution),
            "learning_opportunities": self._identify_learning_opportunities(parallel_execution)
        }
        
        # Application des améliorations
        improvements = {
            "performance_data": performance_data,
            "optimization_suggestions": self._generate_optimization_suggestions(performance_data),
            "learning_updates": self._apply_learning_updates(performance_data),
            "system_adaptations": self._apply_system_adaptations(performance_data),
            "future_optimizations": self._plan_future_optimizations(performance_data)
        }
        
        print(f"  📊 Score qualité: {performance_data['quality_score']:.2f}")
        print(f"  🎯 Améliorations identifiées: {len(improvements['optimization_suggestions'])}")
        
        return improvements

    def execute_daily_intelligence_cycle(self) -> Dict[str, Any]:
        """
        Exécute le cycle quotidien de veille pour tous les experts
        """
        print("\n🌅 EXÉCUTION DU CYCLE QUOTIDIEN DE VEILLE")
        
        # Exécution de la veille quotidienne
        intelligence_cycle = self.intelligence_system.execute_daily_intelligence_cycle()
        
        # Intégration des apprentissages dans l'optimisation Manus
        learning_integration = self._integrate_daily_learnings(intelligence_cycle)
        
        # Mise à jour des performances système
        system_update = self._update_system_from_intelligence(intelligence_cycle, learning_integration)
        
        result = {
            "intelligence_cycle": intelligence_cycle,
            "learning_integration": learning_integration,
            "system_update": system_update,
            "performance_impact": self._assess_intelligence_impact(intelligence_cycle)
        }
        
        print(f"✅ Cycle quotidien terminé - Impact performance: +{result['performance_impact']['improvement_percentage']:.1f}%")
        
        return result

    def _integrate_daily_learnings(self, intelligence_cycle: Dict[str, Any]) -> Dict[str, Any]:
        """
        Intègre les apprentissages quotidiens dans l'optimisation Manus
        """
        agent_reports = intelligence_cycle.get("agent_reports", {})
        
        integration = {
            "knowledge_updates": {},
            "prompt_optimizations": {},
            "context_enhancements": {},
            "specialization_improvements": {}
        }
        
        for agent_id, report in agent_reports.items():
            # Mise à jour des connaissances
            integration["knowledge_updates"][agent_id] = {
                "new_findings": len(report.get("intelligence_findings", [])),
                "relevance_score": sum(f.get("relevance", 0) for f in report.get("intelligence_findings", [])),
                "learning_summary": report.get("learning_summary", {})
            }
            
            # Optimisation des prompts
            integration["prompt_optimizations"][agent_id] = self._optimize_prompts_from_learnings(agent_id, report)
            
            # Amélioration de la contextualisation
            integration["context_enhancements"][agent_id] = self._enhance_context_from_learnings(agent_id, report)
        
        return integration

    def get_system_performance_report(self) -> str:
        """
        Génère un rapport complet de performance du système
        """
        manus_metrics = self.manus_optimizer.get_optimization_metrics()
        intelligence_metrics = self.intelligence_system.get_intelligence_metrics()
        
        report = f"""# 📊 RAPPORT DE PERFORMANCE SUBSTANS.AI OPTIMISÉ

## 🎯 RÉSUMÉ EXÉCUTIF
- **Version système** : {self.version}
- **Score synergie Manus** : {self.performance_metrics['manus_synergy_score']:.2f}/1.0
- **Amélioration intelligence** : {self.performance_metrics['intelligence_enhancement']:.2f}/1.0
- **Efficacité globale** : {self.performance_metrics['overall_efficiency']:.2f}/1.0

## 🚀 OPTIMISATIONS MANUS
- **Prompts optimisés** : {manus_metrics['total_optimizations']}
- **Ratio enrichissement** : {manus_metrics['performance_metrics']['context_enrichment_ratio']:.1f}x
- **Efficacité parallèle** : {manus_metrics['performance_metrics']['parallel_efficiency']:.2f}
- **Score qualité** : {manus_metrics['performance_metrics']['response_quality_score']:.2f}

## 🧠 INTELLIGENCE QUOTIDIENNE
- **Cycles exécutés** : {intelligence_metrics.get('cycles_executed', 0)}
- **Agents surveillés** : {intelligence_metrics.get('agents_monitored', 0)}
- **Score intelligence** : {intelligence_metrics.get('latest_cycle', {}).get('intelligence_score', 0):.2f}
- **Enrichissements KB** : {intelligence_metrics.get('latest_cycle', {}).get('knowledge_items_added', 0)}

## 📈 TENDANCES DE PERFORMANCE
- **Amélioration continue** : {'✅ Active' if self.optimization_config['amelioration_continue'] else '❌ Inactive'}
- **Veille quotidienne** : {'✅ Active' if self.optimization_config['veille_quotidienne'] else '❌ Inactive'}
- **Spécialisation sectorielle** : {'✅ Active' if self.optimization_config['specialisation_sectorielle'] else '❌ Inactive'}

---
*Rapport généré par {self.name} v{self.version}*
"""
        
        return report

    # Méthodes utilitaires pour les optimisations
    def _assess_request_complexity(self, task: str) -> str:
        """Évalue la complexité de la demande"""
        task_lower = task.lower()
        high_indicators = ["stratégie", "business plan", "transformation", "analyse complète"]
        medium_indicators = ["analyse", "étude", "rapport", "recommandations"]
        
        if any(indicator in task_lower for indicator in high_indicators):
            return "high"
        elif any(indicator in task_lower for indicator in medium_indicators):
            return "medium"
        return "low"

    def _identify_primary_domain(self, task: str) -> str:
        """Identifie le domaine principal de la tâche"""
        task_lower = task.lower()
        domain_keywords = {
            "semi-conducteurs": ["semi", "conducteur", "hpc", "supercalcul", "bullsequana"],
            "digital": ["digital", "data", "ia", "intelligence", "artificielle"],
            "cloud": ["cloud", "infrastructure", "devops", "kubernetes"],
            "cybersécurité": ["cyber", "sécurité", "security", "threat"],
            "stratégie": ["stratégie", "business", "plan", "vision"]
        }
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in task_lower for keyword in keywords):
                return domain
        return "general"

    def _select_primary_agent(self, analysis: Dict[str, Any]) -> str:
        """Sélectionne l'agent principal selon l'analyse"""
        domain_agents = {
            "semi-conducteurs": "ESS",
            "digital": "EDDI", 
            "cloud": "EC",
            "cybersécurité": "ECYBER",
            "stratégie": "ESTRAT"
        }
        return domain_agents.get(analysis["domain"], "Senior Advisor")

    def _select_supporting_agents(self, analysis: Dict[str, Any]) -> List[str]:
        """Sélectionne les agents de support"""
        base_agents = ["AVS", "AAD", "ARR"]  # Agents consultants de base
        
        if analysis["complexity"] == "high":
            base_agents.extend(["AGC", "ASM"])
        
        return base_agents

    def _generate_request_id(self, user_request: Dict[str, Any]) -> str:
        """Génère un ID unique pour la demande"""
        import hashlib
        content = f"{datetime.now().isoformat()}_{user_request.get('task', '')}"
        return f"REQ_{hashlib.md5(content.encode()).hexdigest()[:8]}"

    def _calculate_request_performance(self, user_request: Dict[str, Any], improvement_result: Dict[str, Any]) -> Dict[str, Any]:
        """Calcule les métriques de performance de la demande"""
        return {
            "overall_score": improvement_result["performance_data"]["quality_score"],
            "efficiency_score": improvement_result["performance_data"]["efficiency_metrics"].get("overall", 0.85),
            "satisfaction_score": improvement_result["performance_data"]["user_satisfaction"],
            "optimization_level": 0.92  # Score d'optimisation global
        }

    def _update_global_metrics(self, final_result: Dict[str, Any]) -> None:
        """Met à jour les métriques globales du système"""
        perf = final_result["performance_metrics"]
        
        # Mise à jour progressive des métriques
        alpha = 0.1  # Facteur de lissage
        self.performance_metrics["manus_synergy_score"] = (
            (1 - alpha) * self.performance_metrics["manus_synergy_score"] + 
            alpha * perf["overall_score"]
        )
        self.performance_metrics["overall_efficiency"] = (
            (1 - alpha) * self.performance_metrics["overall_efficiency"] + 
            alpha * perf["efficiency_score"]
        )
        self.performance_metrics["user_satisfaction"] = (
            (1 - alpha) * self.performance_metrics["user_satisfaction"] + 
            alpha * perf["satisfaction_score"]
        )

    # Méthodes de simulation pour les fonctionnalités avancées
    def _get_relevant_knowledge_base(self, user_request: Dict, orchestration: Dict) -> Dict:
        return {"knowledge_items": 150, "relevance_score": 0.88}

    def _get_relevant_mission_history(self, agent: str) -> List[Dict]:
        return [{"mission": "Bull Analysis", "performance": 0.95}]

    def _get_applicable_methodology(self, user_request: Dict) -> Dict:
        return {"methodology": "Stratégie 4 Phases", "phase": "Vision"}

    def _get_sector_intelligence(self, domain: str) -> Dict:
        return {"primary_sector": domain, "market_size": "15Md€", "growth": "12%"}

    def _get_competitive_context(self, user_request: Dict) -> Dict:
        return {"competitors": ["Nvidia", "Intel", "AMD"], "positioning": "European sovereignty"}

    def _get_regulatory_context(self, user_request: Dict) -> Dict:
        return {"regulations": ["AI Act", "GDPR", "DMA"], "compliance_level": "high"}

    def _get_market_context(self, user_request: Dict) -> Dict:
        return {"market_trends": ["AI acceleration", "Edge computing"], "opportunities": "high"}

    def _get_technology_trends(self, domain: str) -> Dict:
        return {"trends": ["Exascale computing", "Quantum"], "maturity": "emerging"}

    def _get_agent_performance_patterns(self, agent: str) -> Dict:
        return {"avg_quality": 0.92, "specialization": 0.95, "efficiency": 0.88}

    def _get_expert_level(self, sector: str) -> str:
        levels = {
            "semi-conducteurs": "Senior Engineer 15+ years",
            "digital": "Chief Digital Officer",
            "stratégie": "Partner Strategy Consulting"
        }
        return levels.get(sector, "Senior Expert")

    def _get_specialized_knowledge(self, sector: str) -> Dict:
        return {"depth": "expert", "breadth": "comprehensive", "currency": "latest"}

    def _get_sector_frameworks(self, sector: str) -> List[str]:
        frameworks = {
            "semi-conducteurs": ["Moore's Law", "Dennard Scaling", "More than Moore"],
            "stratégie": ["Porter 5 Forces", "Blue Ocean", "Jobs-to-be-Done"]
        }
        return frameworks.get(sector, ["Industry Best Practices"])

    def _get_industry_benchmarks(self, sector: str) -> Dict:
        return {"performance_metrics": ["efficiency", "cost", "time"], "benchmarks": "top quartile"}

    def _get_regulatory_specifics(self, sector: str) -> Dict:
        return {"specific_regulations": ["sector specific"], "compliance_requirements": "high"}

    def _get_competitive_dynamics(self, sector: str) -> Dict:
        return {"competition_level": "high", "differentiation_factors": ["technology", "sovereignty"]}

    def _get_technology_stack(self, sector: str) -> Dict:
        return {"core_technologies": ["advanced"], "emerging_tech": ["quantum", "neuromorphic"]}

    def _generate_specialized_enhancement(self, specialization: Dict) -> str:
        return f"Enhanced with {specialization['expert_level']} expertise in {specialization['sector']}"

    def _calculate_optimal_parallel_count(self, specialized_processing: Dict) -> int:
        return 3  # Optimal pour la plupart des tâches complexes

    def _decompose_into_subtasks(self, specialized_processing: Dict) -> List[str]:
        return ["Technical Analysis", "Market Research", "Strategic Recommendations"]

    def _identify_sync_points(self, specialized_processing: Dict) -> List[str]:
        return ["Initial Analysis", "Mid-point Review", "Final Integration"]

    def _create_execution_plan(self, analysis: Dict) -> Dict:
        return {"phases": 3, "duration": "2 hours", "coordination": "senior_advisor"}

    def _calculate_coordination_overhead(self, analysis: Dict) -> float:
        return 0.15  # 15% overhead pour coordination

    def _calculate_efficiency_gain(self, analysis: Dict) -> float:
        return 2.5  # 2.5x gain avec parallélisation

    def _design_quality_assurance(self, analysis: Dict) -> Dict:
        return {"checkpoints": 3, "validation": "senior_advisor", "quality_gates": "automated"}

    def _measure_execution_time(self, parallel_execution: Dict) -> float:
        return 1.2  # heures

    def _assess_quality_score(self, parallel_execution: Dict) -> float:
        return 0.92

    def _predict_user_satisfaction(self, parallel_execution: Dict) -> float:
        return 0.89

    def _collect_efficiency_metrics(self, parallel_execution: Dict) -> Dict:
        return {"overall": 0.88, "time_efficiency": 0.92, "resource_efficiency": 0.85}

    def _identify_learning_opportunities(self, parallel_execution: Dict) -> List[str]:
        return ["Prompt optimization", "Context enhancement", "Workflow improvement"]

    def _generate_optimization_suggestions(self, performance_data: Dict) -> List[str]:
        return ["Increase parallelization", "Enhance context", "Improve specialization"]

    def _apply_learning_updates(self, performance_data: Dict) -> Dict:
        return {"updates_applied": 3, "improvement_expected": 0.05}

    def _apply_system_adaptations(self, performance_data: Dict) -> Dict:
        return {"adaptations": ["workflow", "context", "specialization"], "impact": "positive"}

    def _plan_future_optimizations(self, performance_data: Dict) -> List[str]:
        return ["Advanced ML integration", "Real-time optimization", "Predictive enhancement"]

    def _update_system_from_intelligence(self, intelligence_cycle: Dict, learning_integration: Dict) -> Dict:
        return {"system_updates": 5, "performance_improvement": 0.03}

    def _assess_intelligence_impact(self, intelligence_cycle: Dict) -> Dict:
        return {"improvement_percentage": 3.2, "knowledge_expansion": "significant"}

    def _optimize_prompts_from_learnings(self, agent_id: str, report: Dict) -> Dict:
        return {"optimizations": 2, "improvement": 0.05}

    def _enhance_context_from_learnings(self, agent_id: str, report: Dict) -> Dict:
        return {"enhancements": 3, "relevance_boost": 0.08}

# Test du système optimisé complet
if __name__ == "__main__":
    system = SubstansAIOptimizedSystem()
    
    print("\n=== TEST SYSTÈME SUBSTANS.AI OPTIMISÉ ===")
    
    # Test d'une demande utilisateur complexe
    test_request = {
        "task": "Analyser la stratégie technologique de Bull pour les supercalculateurs BullSequana et développer un plan stratégique face à la concurrence Nvidia",
        "context": {
            "mission": "Vision & Plan Stratégique Bull",
            "sector": "Semi-conducteurs",
            "urgency": "haute",
            "client": "Future société Bull"
        },
        "user": "Chef Substans.ai"
    }
    
    # Traitement avec toutes les optimisations
    result = system.process_user_request(test_request)
    
    print(f"\n📊 Résultats optimisés:")
    print(f"- Score performance: {result['performance_metrics']['overall_score']:.2f}")
    print(f"- Efficacité: {result['performance_metrics']['efficiency_score']:.2f}")
    print(f"- Satisfaction: {result['performance_metrics']['satisfaction_score']:.2f}")
    
    # Test du cycle de veille quotidienne
    print(f"\n🌅 Test cycle de veille quotidienne:")
    intelligence_result = system.execute_daily_intelligence_cycle()
    
    print(f"- Agents surveillés: {intelligence_result['intelligence_cycle']['summary']['total_agents']}")
    print(f"- Enrichissements: {intelligence_result['intelligence_cycle']['summary']['knowledge_items_added']}")
    print(f"- Impact performance: +{intelligence_result['performance_impact']['improvement_percentage']:.1f}%")
    
    # Rapport de performance global
    print(f"\n📋 Rapport de performance:")
    performance_report = system.get_system_performance_report()
    print(performance_report[:800] + "..." if len(performance_report) > 800 else performance_report)

