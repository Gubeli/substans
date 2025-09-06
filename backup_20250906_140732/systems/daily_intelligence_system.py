#!/usr/bin/env python3
"""
Daily Intelligence System - Système de Veille Quotidienne Automatisée
Chaque agent expert exécute quotidiennement une session de veille dans son domaine
Génère des rapports d'enrichissement intégrés à la base de connaissances
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import hashlib
import os

class DailyIntelligenceSystem:
    def __init__(self):
        self.name = "Daily Intelligence System"
        self.version = "1.0"
        self.intelligence_reports = []
        self.knowledge_enrichment_log = []
        
        # Configuration des agents experts et leurs domaines de veille
        self.expert_agents = {
            "ESS": {
                "name": "Expert Semi-conducteurs & Substrats",
                "domains": ["semi-conducteurs", "HPC", "supercalcul", "BullSequana", "BXI"],
                "sources": [
                    "IEEE Spectrum", "EE Times", "AnandTech", "HPCwire", 
                    "Top500.org", "Eviden.com", "Nvidia.com", "Intel.com"
                ],
                "keywords": [
                    "BullSequana", "exascale", "HPC", "supercalculateur", "BXI",
                    "interconnect", "Nvidia H100", "Intel Ponte Vecchio", "AMD MI300"
                ],
                "expertise_level": "senior_engineer_15_years"
            },
            
            "EDDI": {
                "name": "Expert Digital, Data, IA",
                "domains": ["intelligence artificielle", "data", "transformation digitale"],
                "sources": [
                    "MIT Technology Review", "VentureBeat AI", "TechCrunch", "Wired",
                    "OpenAI.com", "Google AI", "Microsoft AI", "Anthropic.com"
                ],
                "keywords": [
                    "GPT", "LLM", "IA générative", "machine learning", "MLOps",
                    "DataOps", "transformation digitale", "cloud native", "edge computing"
                ],
                "expertise_level": "chief_digital_officer"
            },
            
            "EIA": {
                "name": "Expert Intelligence Artificielle",
                "domains": ["IA", "machine learning", "deep learning", "AGI"],
                "sources": [
                    "ArXiv.org", "Papers With Code", "Towards Data Science", "AI Research",
                    "OpenAI Research", "DeepMind", "Anthropic Research", "Hugging Face"
                ],
                "keywords": [
                    "transformer", "attention", "RLHF", "fine-tuning", "RAG",
                    "multimodal", "AGI", "alignment", "safety", "reasoning"
                ],
                "expertise_level": "ai_research_scientist"
            },
            
            "EC": {
                "name": "Expert Cloud",
                "domains": ["cloud computing", "infrastructure", "DevOps"],
                "sources": [
                    "AWS Blog", "Google Cloud Blog", "Azure Blog", "CNCF",
                    "Kubernetes.io", "Docker.com", "RedHat", "VMware"
                ],
                "keywords": [
                    "kubernetes", "serverless", "microservices", "containers",
                    "multi-cloud", "edge computing", "DevOps", "GitOps", "observability"
                ],
                "expertise_level": "cloud_architect_senior"
            },
            
            "EDATA": {
                "name": "Expert Data",
                "domains": ["data engineering", "analytics", "big data"],
                "sources": [
                    "Databricks Blog", "Snowflake Blog", "Apache Foundation", "Confluent",
                    "dbt Labs", "Fivetran", "Looker", "Tableau"
                ],
                "keywords": [
                    "data lakehouse", "data mesh", "real-time analytics", "streaming",
                    "dbt", "Apache Spark", "Kafka", "data governance", "data quality"
                ],
                "expertise_level": "chief_data_officer"
            },
            
            "ELRD": {
                "name": "Expert Législations & Réglementations Digitales",
                "domains": ["réglementation", "compliance", "RGPD", "DMA", "DSA"],
                "sources": [
                    "EUR-Lex", "CNIL", "Commission Européenne", "FTC", "DOJ",
                    "Privacy International", "IAPP", "TechPolicy"
                ],
                "keywords": [
                    "RGPD", "DMA", "DSA", "AI Act", "GDPR", "privacy",
                    "data protection", "antitrust", "competition", "sovereignty"
                ],
                "expertise_level": "regulatory_affairs_director"
            },
            
            "ESTRAT": {
                "name": "Expert Stratégie",
                "domains": ["stratégie", "business", "consulting", "M&A"],
                "sources": [
                    "McKinsey Insights", "BCG Insights", "Bain Insights", "Deloitte",
                    "Harvard Business Review", "MIT Sloan", "Strategy+Business"
                ],
                "keywords": [
                    "digital transformation", "business model", "competitive advantage",
                    "innovation strategy", "M&A", "corporate strategy", "disruption"
                ],
                "expertise_level": "partner_strategy_consulting"
            },
            
            "ECYBER": {
                "name": "Expert Cybersécurité",
                "domains": ["cybersécurité", "sécurité", "cyber threats"],
                "sources": [
                    "CISA", "NIST", "ANSSI", "Krebs on Security", "Dark Reading",
                    "Security Week", "Threatpost", "SANS"
                ],
                "keywords": [
                    "zero trust", "ransomware", "APT", "threat intelligence",
                    "SIEM", "SOC", "incident response", "vulnerability", "penetration testing"
                ],
                "expertise_level": "chief_security_officer"
            }
        }

    def execute_daily_intelligence_cycle(self) -> Dict[str, Any]:
        """
        Exécute le cycle quotidien de veille pour tous les agents experts
        """
        print(f"🌅 Démarrage du cycle de veille quotidienne - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        daily_reports = {}
        enrichment_summary = {
            "date": datetime.now().strftime('%Y-%m-%d'),
            "total_agents": len(self.expert_agents),
            "reports_generated": 0,
            "knowledge_items_added": 0,
            "intelligence_score": 0.0
        }
        
        for agent_id, agent_config in self.expert_agents.items():
            print(f"\n🔍 {agent_config['name']} - Début de la veille...")
            
            # Exécution de la veille pour cet agent
            agent_report = self._execute_agent_intelligence(agent_id, agent_config)
            daily_reports[agent_id] = agent_report
            
            # Intégration à la base de connaissances
            knowledge_integration = self._integrate_to_knowledge_base(agent_id, agent_report)
            
            enrichment_summary["reports_generated"] += 1
            enrichment_summary["knowledge_items_added"] += knowledge_integration["items_added"]
            
            print(f"✅ {agent_config['name']} - Veille terminée: {agent_report['findings_count']} découvertes")
        
        # Calcul du score d'intelligence global
        enrichment_summary["intelligence_score"] = self._calculate_intelligence_score(daily_reports)
        
        # Sauvegarde du cycle quotidien
        cycle_result = {
            "cycle_id": self._generate_cycle_id(),
            "date": datetime.now().isoformat(),
            "summary": enrichment_summary,
            "agent_reports": daily_reports,
            "knowledge_enrichment": self.knowledge_enrichment_log[-len(self.expert_agents):]
        }
        
        self.intelligence_reports.append(cycle_result)
        
        print(f"\n🎯 Cycle quotidien terminé: {enrichment_summary['reports_generated']} rapports, {enrichment_summary['knowledge_items_added']} enrichissements")
        
        return cycle_result

    def _execute_agent_intelligence(self, agent_id: str, agent_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Exécute la session de veille pour un agent spécifique
        """
        # Simulation de la veille (en production, ceci ferait de vraies recherches)
        intelligence_findings = self._simulate_intelligence_gathering(agent_id, agent_config)
        
        # Analyse et synthèse des découvertes
        analysis = self._analyze_findings(agent_id, intelligence_findings, agent_config)
        
        # Génération du rapport quotidien
        daily_report = {
            "agent_id": agent_id,
            "agent_name": agent_config["name"],
            "date": datetime.now().strftime('%Y-%m-%d'),
            "veille_duration": "2 heures",
            "sources_consulted": len(agent_config["sources"]),
            "keywords_monitored": len(agent_config["keywords"]),
            "findings_count": len(intelligence_findings),
            "intelligence_findings": intelligence_findings,
            "analysis": analysis,
            "learning_summary": self._generate_learning_summary(agent_id, intelligence_findings),
            "performance_enhancement": self._assess_performance_enhancement(agent_id, intelligence_findings),
            "next_focus_areas": self._identify_next_focus_areas(agent_id, intelligence_findings)
        }
        
        return daily_report

    def _simulate_intelligence_gathering(self, agent_id: str, agent_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Simule la collecte d'intelligence (en production: vraies recherches web/API)
        """
        # Simulation de découvertes selon le domaine de l'agent
        simulated_findings = {
            "ESS": [
                {
                    "title": "Nvidia annonce la nouvelle architecture Blackwell pour l'IA",
                    "source": "Nvidia Blog",
                    "date": datetime.now().strftime('%Y-%m-%d'),
                    "relevance": 0.95,
                    "summary": "Nouvelle architecture GPU Blackwell avec performance 4x supérieure pour l'IA générative",
                    "impact": "Concurrence directe avec BullSequana XH3000",
                    "keywords": ["Nvidia", "Blackwell", "GPU", "IA", "performance"]
                },
                {
                    "title": "Intel dévoile sa roadmap HPC 2025-2027",
                    "source": "Intel Newsroom",
                    "date": datetime.now().strftime('%Y-%m-%d'),
                    "relevance": 0.88,
                    "summary": "Intel présente sa stratégie HPC avec focus sur l'efficacité énergétique",
                    "impact": "Positionnement concurrentiel à analyser vs BullSequana",
                    "keywords": ["Intel", "HPC", "roadmap", "efficacité énergétique"]
                },
                {
                    "title": "JUPITER atteint 1 exaflop - Premier supercalculateur exascale européen",
                    "source": "HPCwire",
                    "date": datetime.now().strftime('%Y-%m-%d'),
                    "relevance": 0.92,
                    "summary": "Le supercalculateur JUPITER basé sur BullSequana XH3000 atteint l'exascale",
                    "impact": "Validation technologique majeure pour Bull/Eviden",
                    "keywords": ["JUPITER", "exascale", "BullSequana", "Europe", "souveraineté"]
                }
            ],
            
            "EDDI": [
                {
                    "title": "OpenAI lance GPT-5 avec capacités de raisonnement avancées",
                    "source": "OpenAI Blog",
                    "date": datetime.now().strftime('%Y-%m-%d'),
                    "relevance": 0.96,
                    "summary": "GPT-5 introduit des capacités de raisonnement multi-étapes et planification",
                    "impact": "Révolution pour les applications IA d'entreprise",
                    "keywords": ["GPT-5", "raisonnement", "IA générative", "entreprise"]
                },
                {
                    "title": "Microsoft annonce Copilot Enterprise avec RAG avancé",
                    "source": "Microsoft Blog",
                    "date": datetime.now().strftime('%Y-%m-%d'),
                    "relevance": 0.89,
                    "summary": "Nouvelle version de Copilot intégrant RAG pour données d'entreprise",
                    "impact": "Accélération de l'adoption IA en entreprise",
                    "keywords": ["Microsoft", "Copilot", "RAG", "entreprise", "productivité"]
                }
            ],
            
            "ELRD": [
                {
                    "title": "L'UE finalise l'AI Act - Entrée en vigueur février 2025",
                    "source": "Commission Européenne",
                    "date": datetime.now().strftime('%Y-%m-%d'),
                    "relevance": 0.94,
                    "summary": "L'AI Act européen entre en vigueur avec obligations pour les systèmes IA à haut risque",
                    "impact": "Impact majeur sur le développement et déploiement d'IA",
                    "keywords": ["AI Act", "UE", "réglementation", "IA", "compliance"]
                }
            ]
        }
        
        return simulated_findings.get(agent_id, [
            {
                "title": f"Développement dans le domaine de {agent_config['name']}",
                "source": "Source spécialisée",
                "date": datetime.now().strftime('%Y-%m-%d'),
                "relevance": 0.75,
                "summary": f"Nouvelle évolution dans {agent_config['domains'][0]}",
                "impact": "À analyser selon expertise sectorielle",
                "keywords": agent_config['keywords'][:3]
            }
        ])

    def _analyze_findings(self, agent_id: str, findings: List[Dict], agent_config: Dict) -> Dict[str, Any]:
        """
        Analyse les découvertes avec l'expertise de l'agent
        """
        analysis = {
            "key_trends": [],
            "competitive_intelligence": [],
            "technology_shifts": [],
            "regulatory_changes": [],
            "market_opportunities": [],
            "strategic_implications": [],
            "risk_assessment": []
        }
        
        for finding in findings:
            relevance = finding.get("relevance", 0.5)
            
            if relevance > 0.9:
                analysis["key_trends"].append({
                    "trend": finding["title"],
                    "impact": finding["impact"],
                    "confidence": "high"
                })
            
            if any(keyword in finding["title"].lower() for keyword in ["concurrent", "competitor", "vs", "against"]):
                analysis["competitive_intelligence"].append({
                    "intelligence": finding["summary"],
                    "competitive_impact": finding["impact"]
                })
            
            if any(keyword in finding["title"].lower() for keyword in ["nouveau", "innovation", "breakthrough", "révolution"]):
                analysis["technology_shifts"].append({
                    "technology": finding["title"],
                    "disruption_potential": "high" if relevance > 0.9 else "medium"
                })
        
        # Implications stratégiques spécifiques à l'agent
        if agent_id == "ESS":
            analysis["strategic_implications"] = [
                "Renforcement nécessaire de la roadmap BullSequana face à Nvidia Blackwell",
                "Opportunité de valoriser les succès JUPITER pour le positionnement européen",
                "Surveillance accrue des développements Intel HPC"
            ]
        elif agent_id == "EDDI":
            analysis["strategic_implications"] = [
                "Intégration des capacités GPT-5 dans les solutions Bull",
                "Développement d'une stratégie Copilot Enterprise concurrente",
                "Positionnement sur l'IA d'entreprise avec souveraineté européenne"
            ]
        
        return analysis

    def _generate_learning_summary(self, agent_id: str, findings: List[Dict]) -> Dict[str, Any]:
        """
        Génère un résumé des apprentissages pour l'agent
        """
        learning_summary = {
            "new_knowledge_areas": [],
            "expertise_enhancement": [],
            "capability_expansion": [],
            "performance_improvement_potential": 0.0
        }
        
        # Analyse des nouveaux domaines de connaissance
        for finding in findings:
            if finding.get("relevance", 0) > 0.8:
                learning_summary["new_knowledge_areas"].append({
                    "area": finding["title"],
                    "knowledge_depth": "high" if finding.get("relevance", 0) > 0.9 else "medium",
                    "application_potential": finding["impact"]
                })
        
        # Évaluation de l'amélioration des performances
        high_relevance_count = sum(1 for f in findings if f.get("relevance", 0) > 0.8)
        learning_summary["performance_improvement_potential"] = min(1.0, high_relevance_count * 0.1)
        
        return learning_summary

    def _assess_performance_enhancement(self, agent_id: str, findings: List[Dict]) -> Dict[str, Any]:
        """
        Évalue l'amélioration des performances de l'agent
        """
        enhancement = {
            "knowledge_base_expansion": len(findings),
            "expertise_deepening": sum(f.get("relevance", 0) for f in findings) / len(findings) if findings else 0,
            "competitive_awareness": len([f for f in findings if "concurren" in f.get("impact", "").lower()]),
            "innovation_tracking": len([f for f in findings if f.get("relevance", 0) > 0.9]),
            "overall_enhancement_score": 0.0
        }
        
        # Calcul du score global d'amélioration
        base_score = enhancement["expertise_deepening"]
        innovation_bonus = enhancement["innovation_tracking"] * 0.1
        competitive_bonus = enhancement["competitive_awareness"] * 0.05
        
        enhancement["overall_enhancement_score"] = min(1.0, base_score + innovation_bonus + competitive_bonus)
        
        return enhancement

    def _identify_next_focus_areas(self, agent_id: str, findings: List[Dict]) -> List[str]:
        """
        Identifie les prochaines zones de focus pour l'agent
        """
        focus_areas = []
        
        # Analyse des gaps et opportunités
        high_impact_findings = [f for f in findings if f.get("relevance", 0) > 0.85]
        
        for finding in high_impact_findings:
            if "opportunité" in finding.get("impact", "").lower():
                focus_areas.append(f"Approfondir: {finding['title']}")
            elif "concurrence" in finding.get("impact", "").lower():
                focus_areas.append(f"Surveiller: {finding['title']}")
        
        # Focus spécifiques par agent
        agent_specific_focus = {
            "ESS": ["Évolution architectures GPU", "Roadmaps concurrents HPC", "Technologies interconnect"],
            "EDDI": ["IA générative entreprise", "Plateformes no-code/low-code", "Edge AI"],
            "ELRD": ["Évolutions réglementaires IA", "Compliance multi-juridictionnelle", "Privacy tech"]
        }
        
        focus_areas.extend(agent_specific_focus.get(agent_id, ["Veille sectorielle continue"]))
        
        return focus_areas[:5]  # Limiter à 5 focus areas

    def _integrate_to_knowledge_base(self, agent_id: str, agent_report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Intègre le rapport de veille à la base de connaissances substans.ai
        """
        integration_result = {
            "agent_id": agent_id,
            "integration_date": datetime.now().isoformat(),
            "items_added": 0,
            "knowledge_categories": [],
            "integration_success": True
        }
        
        # Simulation de l'intégration (en production: vraie base de données)
        findings = agent_report.get("intelligence_findings", [])
        
        for finding in findings:
            if finding.get("relevance", 0) > 0.7:  # Seuil de qualité
                knowledge_item = {
                    "id": self._generate_knowledge_id(agent_id, finding),
                    "agent_source": agent_id,
                    "title": finding["title"],
                    "content": finding["summary"],
                    "category": self._categorize_knowledge(finding),
                    "relevance_score": finding.get("relevance", 0),
                    "date_added": datetime.now().isoformat(),
                    "keywords": finding.get("keywords", []),
                    "impact_assessment": finding.get("impact", "")
                }
                
                integration_result["items_added"] += 1
                category = knowledge_item["category"]
                if category not in integration_result["knowledge_categories"]:
                    integration_result["knowledge_categories"].append(category)
        
        # Log de l'enrichissement
        enrichment_log = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": agent_id,
            "items_integrated": integration_result["items_added"],
            "categories": integration_result["knowledge_categories"],
            "quality_score": sum(f.get("relevance", 0) for f in findings) / len(findings) if findings else 0
        }
        
        self.knowledge_enrichment_log.append(enrichment_log)
        
        return integration_result

    def _categorize_knowledge(self, finding: Dict[str, Any]) -> str:
        """
        Catégorise automatiquement les connaissances
        """
        title_lower = finding["title"].lower()
        
        if any(word in title_lower for word in ["concurrent", "competitor", "vs", "market share"]):
            return "competitive_intelligence"
        elif any(word in title_lower for word in ["innovation", "breakthrough", "nouveau", "révolution"]):
            return "technology_innovation"
        elif any(word in title_lower for word in ["réglementation", "loi", "compliance", "régulation"]):
            return "regulatory_updates"
        elif any(word in title_lower for word in ["marché", "market", "industrie", "secteur"]):
            return "market_intelligence"
        elif any(word in title_lower for word in ["stratégie", "strategy", "business model"]):
            return "strategic_intelligence"
        else:
            return "general_intelligence"

    def _calculate_intelligence_score(self, daily_reports: Dict[str, Any]) -> float:
        """
        Calcule le score d'intelligence global du cycle quotidien
        """
        total_findings = sum(report.get("findings_count", 0) for report in daily_reports.values())
        total_relevance = sum(
            sum(f.get("relevance", 0) for f in report.get("intelligence_findings", []))
            for report in daily_reports.values()
        )
        
        if total_findings == 0:
            return 0.0
        
        avg_relevance = total_relevance / total_findings
        coverage_score = len(daily_reports) / len(self.expert_agents)
        
        intelligence_score = (avg_relevance * 0.7 + coverage_score * 0.3)
        
        return min(1.0, intelligence_score)

    def _generate_cycle_id(self) -> str:
        """Génère un ID unique pour le cycle quotidien"""
        date_str = datetime.now().strftime('%Y%m%d')
        hash_input = f"{date_str}_{len(self.intelligence_reports)}"
        return f"CYCLE_{date_str}_{hashlib.md5(hash_input.encode()).hexdigest()[:8]}"

    def _generate_knowledge_id(self, agent_id: str, finding: Dict[str, Any]) -> str:
        """Génère un ID unique pour un élément de connaissance"""
        hash_input = f"{agent_id}_{finding['title']}_{finding.get('date', '')}"
        return f"KB_{hashlib.md5(hash_input.encode()).hexdigest()[:12]}"

    def generate_daily_intelligence_report(self) -> str:
        """
        Génère le rapport quotidien consolidé de veille
        """
        if not self.intelligence_reports:
            return "Aucun cycle de veille exécuté aujourd'hui."
        
        latest_cycle = self.intelligence_reports[-1]
        summary = latest_cycle["summary"]
        
        report = f"""# 📊 RAPPORT QUOTIDIEN DE VEILLE INTELLIGENCE - {summary['date']}

## 🎯 RÉSUMÉ EXÉCUTIF
- **Agents mobilisés** : {summary['total_agents']} experts
- **Rapports générés** : {summary['reports_generated']}
- **Enrichissements KB** : {summary['knowledge_items_added']} nouveaux éléments
- **Score d'intelligence** : {summary['intelligence_score']:.2f}/1.0

## 📋 DÉCOUVERTES MAJEURES PAR EXPERT

"""
        
        for agent_id, report_data in latest_cycle["agent_reports"].items():
            agent_name = report_data["agent_name"]
            findings_count = report_data["findings_count"]
            
            report += f"### {agent_name}\n"
            report += f"- **Découvertes** : {findings_count}\n"
            report += f"- **Sources consultées** : {report_data['sources_consulted']}\n"
            
            # Top découvertes
            top_findings = sorted(
                report_data.get("intelligence_findings", []),
                key=lambda x: x.get("relevance", 0),
                reverse=True
            )[:2]
            
            for finding in top_findings:
                report += f"  - 🔍 **{finding['title']}** (Relevance: {finding.get('relevance', 0):.2f})\n"
                report += f"    - {finding['summary']}\n"
                report += f"    - Impact: {finding['impact']}\n"
            
            report += "\n"
        
        report += f"""## 🧠 ENRICHISSEMENT DE LA BASE DE CONNAISSANCES

"""
        
        for enrichment in latest_cycle["knowledge_enrichment"]:
            agent_id = enrichment["agent_id"]
            items = enrichment["items_integrated"]
            quality = enrichment["quality_score"]
            
            report += f"- **{agent_id}** : {items} éléments ajoutés (Qualité: {quality:.2f})\n"
        
        report += f"""
## 📈 MÉTRIQUES DE PERFORMANCE
- **Couverture sectorielle** : {len(latest_cycle['agent_reports'])}/{len(self.expert_agents)} domaines
- **Qualité moyenne** : {summary['intelligence_score']:.2f}/1.0
- **Enrichissement KB** : +{summary['knowledge_items_added']} éléments

---
*Rapport généré automatiquement par le Daily Intelligence System v{self.version}*
"""
        
        return report

    def get_intelligence_metrics(self) -> Dict[str, Any]:
        """Retourne les métriques du système de veille"""
        if not self.intelligence_reports:
            return {"status": "no_data", "cycles_executed": 0}
        
        latest_cycle = self.intelligence_reports[-1]
        
        return {
            "system_name": self.name,
            "version": self.version,
            "cycles_executed": len(self.intelligence_reports),
            "agents_monitored": len(self.expert_agents),
            "latest_cycle": latest_cycle["summary"],
            "knowledge_enrichment_trend": self._calculate_enrichment_trend(),
            "intelligence_quality_trend": self._calculate_quality_trend()
        }

    def _calculate_enrichment_trend(self) -> Dict[str, float]:
        """Calcule la tendance d'enrichissement des connaissances"""
        if len(self.intelligence_reports) < 2:
            return {"trend": 0.0, "acceleration": False}
        
        recent_enrichments = [
            cycle["summary"]["knowledge_items_added"] 
            for cycle in self.intelligence_reports[-5:]
        ]
        
        avg_recent = sum(recent_enrichments) / len(recent_enrichments)
        
        older_enrichments = [
            cycle["summary"]["knowledge_items_added"] 
            for cycle in self.intelligence_reports[-10:-5]
        ]
        
        if older_enrichments:
            avg_older = sum(older_enrichments) / len(older_enrichments)
            trend = (avg_recent - avg_older) / avg_older if avg_older > 0 else 0
        else:
            trend = 0.0
        
        return {
            "trend": trend,
            "acceleration": trend > 0.1,
            "avg_daily_enrichment": avg_recent
        }

    def _calculate_quality_trend(self) -> Dict[str, float]:
        """Calcule la tendance de qualité de l'intelligence"""
        if len(self.intelligence_reports) < 2:
            return {"trend": 0.0, "improvement": False}
        
        recent_scores = [
            cycle["summary"]["intelligence_score"] 
            for cycle in self.intelligence_reports[-5:]
        ]
        
        avg_recent = sum(recent_scores) / len(recent_scores)
        
        return {
            "current_quality": avg_recent,
            "improvement": avg_recent > 0.8,
            "excellence_threshold": avg_recent > 0.9
        }

# Test du système de veille quotidienne
if __name__ == "__main__":
    intelligence_system = DailyIntelligenceSystem()
    
    print("=== TEST SYSTÈME DE VEILLE QUOTIDIENNE ===")
    
    # Exécution d'un cycle de veille
    cycle_result = intelligence_system.execute_daily_intelligence_cycle()
    
    print(f"\n📊 Résultats du cycle:")
    print(f"- Agents: {cycle_result['summary']['total_agents']}")
    print(f"- Rapports: {cycle_result['summary']['reports_generated']}")
    print(f"- Enrichissements: {cycle_result['summary']['knowledge_items_added']}")
    print(f"- Score: {cycle_result['summary']['intelligence_score']:.2f}")
    
    # Génération du rapport quotidien
    print(f"\n📋 Rapport quotidien:")
    daily_report = intelligence_system.generate_daily_intelligence_report()
    print(daily_report[:1000] + "..." if len(daily_report) > 1000 else daily_report)
    
    print(f"\n📈 Métriques système:")
    metrics = intelligence_system.get_intelligence_metrics()
    print(json.dumps(metrics, indent=2, default=str))

