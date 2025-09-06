#!/usr/bin/env python3
"""
Advanced Intelligence Collector - Système de Collecte d'Intelligence Quotidienne Avancé
Correction et amélioration du système de collecte d'intelligence
"""

import os
import json
import sqlite3
import datetime
import asyncio
import aiohttp
import hashlib
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
from pathlib import Path
import logging
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import schedule

# Configuration logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IntelligenceType(Enum):
    MARKET_TRENDS = "market_trends"
    TECHNOLOGY = "technology"
    REGULATORY = "regulatory"
    COMPETITIVE = "competitive"
    FINANCIAL = "financial"
    GEOPOLITICAL = "geopolitical"
    INNOVATION = "innovation"
    INDUSTRY_NEWS = "industry_news"

class SourceType(Enum):
    RSS_FEED = "rss_feed"
    API = "api"
    WEB_SCRAPING = "web_scraping"
    SOCIAL_MEDIA = "social_media"
    NEWSLETTER = "newsletter"
    RESEARCH_PAPER = "research_paper"

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    URGENT = 5

@dataclass
class IntelligenceSource:
    """Source d'intelligence"""
    id: str
    name: str
    url: str
    type: SourceType
    intelligence_types: List[IntelligenceType]
    agent_id: str
    priority: Priority
    frequency_hours: int
    active: bool = True
    last_collected: Optional[datetime.datetime] = None
    success_rate: float = 100.0
    avg_relevance: float = 0.0

@dataclass
class IntelligenceItem:
    """Item d'intelligence collecté"""
    id: str
    source_id: str
    agent_id: str
    title: str
    content: str
    url: str
    intelligence_type: IntelligenceType
    priority: Priority
    relevance_score: float
    sentiment: str
    keywords: List[str]
    collected_at: datetime.datetime
    processed: bool = False
    summary: Optional[str] = None

@dataclass
class DailyIntelligenceReport:
    """Rapport quotidien d'intelligence"""
    id: str
    agent_id: str
    date: datetime.date
    items_count: int
    avg_relevance: float
    top_keywords: List[str]
    summary: str
    recommendations: List[str]
    generated_at: datetime.datetime

class AdvancedIntelligenceCollector:
    """Collecteur d'intelligence quotidienne avancé"""
    
    def __init__(self, base_path: str = "/home/ubuntu/substans_ai_megacabinet"):
        self.base_path = Path(base_path)
        self.intelligence_path = self.base_path / "intelligence"
        self.reports_path = self.intelligence_path / "reports"
        self.db_path = self.base_path / "data" / "intelligence.db"
        
        # Créer les répertoires
        for path in [self.intelligence_path, self.reports_path, self.db_path.parent]:
            path.mkdir(parents=True, exist_ok=True)
        
        self._init_database()
        self._load_default_sources()
        
        # Configuration
        self.max_workers = 10
        self.collection_timeout = 30
        self.running = False
        self.scheduler_thread = None
        
        # Cache pour éviter les doublons
        self.content_hashes = set()
        
        # Statistiques
        self.stats = {
            "total_collected": 0,
            "today_collected": 0,
            "sources_active": 0,
            "avg_relevance": 0.0,
            "last_collection": None
        }
    
    def _init_database(self):
        """Initialise la base de données d'intelligence"""
        with sqlite3.connect(self.db_path) as conn:
            # Table des sources
            conn.execute("""
                CREATE TABLE IF NOT EXISTS intelligence_sources (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    url TEXT NOT NULL,
                    type TEXT NOT NULL,
                    intelligence_types TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    priority INTEGER NOT NULL,
                    frequency_hours INTEGER NOT NULL,
                    active BOOLEAN DEFAULT TRUE,
                    last_collected TIMESTAMP,
                    success_rate REAL DEFAULT 100.0,
                    avg_relevance REAL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table des items d'intelligence
            conn.execute("""
                CREATE TABLE IF NOT EXISTS intelligence_items (
                    id TEXT PRIMARY KEY,
                    source_id TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    url TEXT NOT NULL,
                    intelligence_type TEXT NOT NULL,
                    priority INTEGER NOT NULL,
                    relevance_score REAL NOT NULL,
                    sentiment TEXT,
                    keywords TEXT,
                    collected_at TIMESTAMP NOT NULL,
                    processed BOOLEAN DEFAULT FALSE,
                    summary TEXT,
                    content_hash TEXT UNIQUE,
                    FOREIGN KEY (source_id) REFERENCES intelligence_sources (id)
                )
            """)
            
            # Table des rapports quotidiens
            conn.execute("""
                CREATE TABLE IF NOT EXISTS daily_reports (
                    id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    date DATE NOT NULL,
                    items_count INTEGER NOT NULL,
                    avg_relevance REAL NOT NULL,
                    top_keywords TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    recommendations TEXT NOT NULL,
                    generated_at TIMESTAMP NOT NULL,
                    UNIQUE(agent_id, date)
                )
            """)
            
            # Index pour les performances
            conn.execute("CREATE INDEX IF NOT EXISTS idx_items_agent_date ON intelligence_items(agent_id, collected_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_items_type ON intelligence_items(intelligence_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sources_agent ON intelligence_sources(agent_id)")
            
            conn.commit()
    
    def _load_default_sources(self):
        """Charge les sources par défaut pour chaque agent"""
        default_sources = [
            # Expert Finance & M&A
            IntelligenceSource(
                id="source_finance_ft",
                name="Financial Times",
                url="https://www.ft.com/rss/home",
                type=SourceType.RSS_FEED,
                intelligence_types=[IntelligenceType.FINANCIAL, IntelligenceType.MARKET_TRENDS],
                agent_id="efs",
                priority=Priority.HIGH,
                frequency_hours=4
            ),
            IntelligenceSource(
                id="source_finance_wsj",
                name="Wall Street Journal",
                url="https://feeds.wsj.com/wsj/xml/rss/3_7085.xml",
                type=SourceType.RSS_FEED,
                intelligence_types=[IntelligenceType.FINANCIAL, IntelligenceType.COMPETITIVE],
                agent_id="efs",
                priority=Priority.HIGH,
                frequency_hours=4
            ),
            IntelligenceSource(
                id="source_finance_bloomberg",
                name="Bloomberg Markets",
                url="https://feeds.bloomberg.com/markets/news.rss",
                type=SourceType.RSS_FEED,
                intelligence_types=[IntelligenceType.FINANCIAL, IntelligenceType.MARKET_TRENDS],
                agent_id="efs",
                priority=Priority.CRITICAL,
                frequency_hours=2
            ),
            
            # Expert IA
            IntelligenceSource(
                id="source_ai_mit",
                name="MIT Technology Review AI",
                url="https://www.technologyreview.com/feed/",
                type=SourceType.RSS_FEED,
                intelligence_types=[IntelligenceType.TECHNOLOGY, IntelligenceType.INNOVATION],
                agent_id="eia",
                priority=Priority.HIGH,
                frequency_hours=6
            ),
            IntelligenceSource(
                id="source_ai_arxiv",
                name="ArXiv AI Papers",
                url="http://export.arxiv.org/rss/cs.AI",
                type=SourceType.RSS_FEED,
                intelligence_types=[IntelligenceType.TECHNOLOGY, IntelligenceType.RESEARCH_PAPER],
                agent_id="eia",
                priority=Priority.MEDIUM,
                frequency_hours=12
            ),
            
            # Expert Cybersécurité
            IntelligenceSource(
                id="source_cyber_krebs",
                name="Krebs on Security",
                url="https://krebsonsecurity.com/feed/",
                type=SourceType.RSS_FEED,
                intelligence_types=[IntelligenceType.TECHNOLOGY, IntelligenceType.REGULATORY],
                agent_id="ecyber",
                priority=Priority.HIGH,
                frequency_hours=6
            ),
            
            # Expert Semi-conducteurs
            IntelligenceSource(
                id="source_semi_eetimes",
                name="EE Times",
                url="https://www.eetimes.com/feed/",
                type=SourceType.RSS_FEED,
                intelligence_types=[IntelligenceType.TECHNOLOGY, IntelligenceType.INDUSTRY_NEWS],
                agent_id="ess",
                priority=Priority.HIGH,
                frequency_hours=8
            ),
            
            # Expert Banque Finance
            IntelligenceSource(
                id="source_bank_reuters",
                name="Reuters Banking",
                url="https://feeds.reuters.com/reuters/businessNews",
                type=SourceType.RSS_FEED,
                intelligence_types=[IntelligenceType.FINANCIAL, IntelligenceType.REGULATORY],
                agent_id="ebf",
                priority=Priority.HIGH,
                frequency_hours=6
            ),
            
            # Expert Cloud
            IntelligenceSource(
                id="source_cloud_aws",
                name="AWS News",
                url="https://aws.amazon.com/about-aws/whats-new/recent/feed/",
                type=SourceType.RSS_FEED,
                intelligence_types=[IntelligenceType.TECHNOLOGY, IntelligenceType.INNOVATION],
                agent_id="ec",
                priority=Priority.MEDIUM,
                frequency_hours=12
            ),
            
            # Sources générales pour tous les agents
            IntelligenceSource(
                id="source_general_techcrunch",
                name="TechCrunch",
                url="https://techcrunch.com/feed/",
                type=SourceType.RSS_FEED,
                intelligence_types=[IntelligenceType.TECHNOLOGY, IntelligenceType.INNOVATION, IntelligenceType.MARKET_TRENDS],
                agent_id="general",
                priority=Priority.MEDIUM,
                frequency_hours=8
            ),
            IntelligenceSource(
                id="source_general_wired",
                name="Wired",
                url="https://www.wired.com/feed/rss",
                type=SourceType.RSS_FEED,
                intelligence_types=[IntelligenceType.TECHNOLOGY, IntelligenceType.INNOVATION],
                agent_id="general",
                priority=Priority.MEDIUM,
                frequency_hours=12
            )
        ]
        
        for source in default_sources:
            self._save_source(source)
    
    def start_collection_service(self):
        """Démarre le service de collecte automatique"""
        if self.running:
            logger.warning("Service de collecte déjà en cours")
            return
        
        self.running = True
        logger.info("🚀 Démarrage du service de collecte d'intelligence")
        
        # Planifier les collectes
        schedule.every(2).hours.do(self._scheduled_collection_high_priority)
        schedule.every(6).hours.do(self._scheduled_collection_medium_priority)
        schedule.every(12).hours.do(self._scheduled_collection_low_priority)
        schedule.every().day.at("08:00").do(self._generate_daily_reports)
        
        # Thread pour le scheduler
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        # Collecte initiale
        self.collect_all_sources()
    
    def stop_collection_service(self):
        """Arrête le service de collecte"""
        self.running = False
        logger.info("🛑 Arrêt du service de collecte d'intelligence")
    
    def _run_scheduler(self):
        """Exécute le scheduler en boucle"""
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Vérifier toutes les minutes
    
    def _scheduled_collection_high_priority(self):
        """Collecte planifiée pour sources haute priorité"""
        logger.info("📊 Collecte planifiée - Haute priorité")
        self.collect_sources_by_priority(Priority.HIGH, Priority.CRITICAL, Priority.URGENT)
    
    def _scheduled_collection_medium_priority(self):
        """Collecte planifiée pour sources moyenne priorité"""
        logger.info("📊 Collecte planifiée - Moyenne priorité")
        self.collect_sources_by_priority(Priority.MEDIUM)
    
    def _scheduled_collection_low_priority(self):
        """Collecte planifiée pour sources basse priorité"""
        logger.info("📊 Collecte planifiée - Basse priorité")
        self.collect_sources_by_priority(Priority.LOW)
    
    def collect_all_sources(self) -> Dict[str, Any]:
        """Collecte toutes les sources actives"""
        logger.info("🔍 Démarrage collecte complète de toutes les sources")
        
        sources = self._get_active_sources()
        results = {
            "total_sources": len(sources),
            "collected_items": 0,
            "errors": 0,
            "sources_processed": [],
            "start_time": datetime.datetime.now()
        }
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_source = {
                executor.submit(self._collect_source, source): source 
                for source in sources
            }
            
            for future in as_completed(future_to_source):
                source = future_to_source[future]
                try:
                    items = future.result(timeout=self.collection_timeout)
                    results["collected_items"] += len(items)
                    results["sources_processed"].append({
                        "source_id": source.id,
                        "source_name": source.name,
                        "items_collected": len(items),
                        "status": "success"
                    })
                    logger.info(f"✅ {source.name}: {len(items)} items collectés")
                    
                except Exception as e:
                    results["errors"] += 1
                    results["sources_processed"].append({
                        "source_id": source.id,
                        "source_name": source.name,
                        "items_collected": 0,
                        "status": "error",
                        "error": str(e)
                    })
                    logger.error(f"❌ Erreur {source.name}: {e}")
        
        results["end_time"] = datetime.datetime.now()
        results["duration"] = (results["end_time"] - results["start_time"]).total_seconds()
        
        # Mettre à jour les statistiques
        self._update_stats(results)
        
        logger.info(f"📊 Collecte terminée: {results['collected_items']} items, {results['errors']} erreurs")
        return results
    
    def collect_sources_by_priority(self, *priorities: Priority) -> Dict[str, Any]:
        """Collecte les sources selon leur priorité"""
        sources = self._get_sources_by_priority(priorities)
        logger.info(f"🔍 Collecte {len(sources)} sources priorité {[p.name for p in priorities]}")
        
        results = {"collected_items": 0, "errors": 0, "sources_processed": []}
        
        for source in sources:
            try:
                items = self._collect_source(source)
                results["collected_items"] += len(items)
                results["sources_processed"].append({
                    "source_id": source.id,
                    "items_collected": len(items),
                    "status": "success"
                })
            except Exception as e:
                results["errors"] += 1
                results["sources_processed"].append({
                    "source_id": source.id,
                    "status": "error",
                    "error": str(e)
                })
        
        return results
    
    def _collect_source(self, source: IntelligenceSource) -> List[IntelligenceItem]:
        """Collecte une source spécifique"""
        items = []
        
        try:
            # Simuler la collecte (en production, utiliser des vraies APIs/RSS)
            simulated_items = self._simulate_source_collection(source)
            
            for item_data in simulated_items:
                # Vérifier les doublons
                content_hash = hashlib.md5(item_data["content"].encode()).hexdigest()
                if content_hash in self.content_hashes:
                    continue
                
                # Créer l'item d'intelligence
                item = IntelligenceItem(
                    id=f"intel_{uuid.uuid4().hex[:8]}",
                    source_id=source.id,
                    agent_id=source.agent_id,
                    title=item_data["title"],
                    content=item_data["content"],
                    url=item_data["url"],
                    intelligence_type=item_data["intelligence_type"],
                    priority=source.priority,
                    relevance_score=item_data["relevance_score"],
                    sentiment=item_data["sentiment"],
                    keywords=item_data["keywords"],
                    collected_at=datetime.datetime.now()
                )
                
                # Sauvegarder l'item
                self._save_intelligence_item(item, content_hash)
                items.append(item)
                self.content_hashes.add(content_hash)
            
            # Mettre à jour la source
            source.last_collected = datetime.datetime.now()
            source.success_rate = min(100.0, source.success_rate + 1.0)
            if items:
                source.avg_relevance = sum(item.relevance_score for item in items) / len(items)
            self._update_source(source)
            
        except Exception as e:
            # Diminuer le taux de succès en cas d'erreur
            source.success_rate = max(0.0, source.success_rate - 5.0)
            self._update_source(source)
            raise e
        
        return items
    
    def _simulate_source_collection(self, source: IntelligenceSource) -> List[Dict[str, Any]]:
        """Simule la collecte d'une source (remplacer par vraie collecte en production)"""
        import random
        
        # Données simulées selon le type de source
        sample_data = {
            "efs": [
                {
                    "title": "M&A Activity Surges in Tech Sector Q4 2024",
                    "content": "Merger and acquisition activity in the technology sector reached record highs in Q4 2024, with total deal value exceeding $150 billion. Key drivers include AI consolidation and cloud infrastructure expansion.",
                    "url": f"{source.url}/article-{random.randint(1000, 9999)}",
                    "intelligence_type": IntelligenceType.FINANCIAL,
                    "relevance_score": random.uniform(8.0, 9.5),
                    "sentiment": random.choice(["positive", "neutral", "negative"]),
                    "keywords": ["M&A", "technology", "AI", "cloud", "consolidation"]
                },
                {
                    "title": "European Banking Regulations Impact on FinTech",
                    "content": "New European banking regulations are reshaping the FinTech landscape, with increased compliance requirements affecting startup valuations and investment patterns.",
                    "url": f"{source.url}/article-{random.randint(1000, 9999)}",
                    "intelligence_type": IntelligenceType.REGULATORY,
                    "relevance_score": random.uniform(7.5, 9.0),
                    "sentiment": random.choice(["neutral", "negative"]),
                    "keywords": ["banking", "regulation", "FinTech", "compliance", "Europe"]
                }
            ],
            "eia": [
                {
                    "title": "Breakthrough in Quantum-AI Hybrid Computing",
                    "content": "Researchers demonstrate significant advances in quantum-AI hybrid systems, achieving 1000x speedup in specific machine learning tasks. Commercial applications expected by 2026.",
                    "url": f"{source.url}/article-{random.randint(1000, 9999)}",
                    "intelligence_type": IntelligenceType.TECHNOLOGY,
                    "relevance_score": random.uniform(9.0, 9.8),
                    "sentiment": "positive",
                    "keywords": ["quantum computing", "AI", "machine learning", "breakthrough", "speedup"]
                },
                {
                    "title": "Large Language Models Efficiency Improvements",
                    "content": "New training techniques reduce LLM computational requirements by 60% while maintaining performance, making AI more accessible to smaller organizations.",
                    "url": f"{source.url}/article-{random.randint(1000, 9999)}",
                    "intelligence_type": IntelligenceType.INNOVATION,
                    "relevance_score": random.uniform(8.5, 9.5),
                    "sentiment": "positive",
                    "keywords": ["LLM", "efficiency", "training", "computational", "accessibility"]
                }
            ],
            "ecyber": [
                {
                    "title": "Critical Zero-Day Vulnerability in Enterprise Software",
                    "content": "Security researchers discover critical zero-day vulnerability affecting major enterprise software platforms. Patches available, immediate update recommended.",
                    "url": f"{source.url}/article-{random.randint(1000, 9999)}",
                    "intelligence_type": IntelligenceType.TECHNOLOGY,
                    "relevance_score": random.uniform(9.5, 10.0),
                    "sentiment": "negative",
                    "keywords": ["zero-day", "vulnerability", "enterprise", "security", "patch"]
                }
            ],
            "general": [
                {
                    "title": "Global Tech Investment Trends 2025",
                    "content": "Analysis of global technology investment patterns shows shift towards sustainable tech and AI infrastructure, with $500B invested globally in 2024.",
                    "url": f"{source.url}/article-{random.randint(1000, 9999)}",
                    "intelligence_type": IntelligenceType.MARKET_TRENDS,
                    "relevance_score": random.uniform(7.0, 8.5),
                    "sentiment": "positive",
                    "keywords": ["investment", "technology", "sustainable", "AI", "infrastructure"]
                }
            ]
        }
        
        # Retourner des données selon l'agent
        agent_data = sample_data.get(source.agent_id, sample_data["general"])
        return random.sample(agent_data, min(len(agent_data), random.randint(1, 3)))
    
    def _generate_daily_reports(self):
        """Génère les rapports quotidiens pour tous les agents"""
        logger.info("📋 Génération des rapports quotidiens d'intelligence")
        
        agents = self._get_agents_with_intelligence()
        today = datetime.date.today()
        
        for agent_id in agents:
            try:
                report = self._generate_agent_daily_report(agent_id, today)
                self._save_daily_report(report)
                logger.info(f"✅ Rapport quotidien généré pour {agent_id}")
            except Exception as e:
                logger.error(f"❌ Erreur génération rapport {agent_id}: {e}")
    
    def _generate_agent_daily_report(self, agent_id: str, date: datetime.date) -> DailyIntelligenceReport:
        """Génère le rapport quotidien pour un agent"""
        # Récupérer les items du jour
        items = self._get_agent_items_by_date(agent_id, date)
        
        if not items:
            # Rapport vide si pas d'items
            return DailyIntelligenceReport(
                id=f"report_{agent_id}_{date.strftime('%Y%m%d')}",
                agent_id=agent_id,
                date=date,
                items_count=0,
                avg_relevance=0.0,
                top_keywords=[],
                summary="Aucune intelligence collectée aujourd'hui.",
                recommendations=["Vérifier les sources d'intelligence", "Ajuster la fréquence de collecte"],
                generated_at=datetime.datetime.now()
            )
        
        # Calculer les métriques
        avg_relevance = sum(item.relevance_score for item in items) / len(items)
        
        # Extraire les mots-clés les plus fréquents
        all_keywords = []
        for item in items:
            all_keywords.extend(item.keywords)
        
        keyword_counts = {}
        for keyword in all_keywords:
            keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
        
        top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        top_keywords = [kw[0] for kw in top_keywords]
        
        # Générer le résumé
        high_relevance_items = [item for item in items if item.relevance_score >= 8.0]
        summary = self._generate_intelligence_summary(items, high_relevance_items)
        
        # Générer les recommandations
        recommendations = self._generate_intelligence_recommendations(items, agent_id)
        
        return DailyIntelligenceReport(
            id=f"report_{agent_id}_{date.strftime('%Y%m%d')}",
            agent_id=agent_id,
            date=date,
            items_count=len(items),
            avg_relevance=avg_relevance,
            top_keywords=top_keywords,
            summary=summary,
            recommendations=recommendations,
            generated_at=datetime.datetime.now()
        )
    
    def _generate_intelligence_summary(self, items: List[IntelligenceItem], high_relevance_items: List[IntelligenceItem]) -> str:
        """Génère un résumé des items d'intelligence"""
        if not items:
            return "Aucune intelligence collectée."
        
        summary_parts = []
        
        # Statistiques générales
        summary_parts.append(f"Collecte de {len(items)} items d'intelligence")
        
        if high_relevance_items:
            summary_parts.append(f"dont {len(high_relevance_items)} à haute relevance (≥8.0)")
        
        # Types d'intelligence
        type_counts = {}
        for item in items:
            type_name = item.intelligence_type.value.replace('_', ' ').title()
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        if type_counts:
            top_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            types_str = ", ".join([f"{t[0]} ({t[1]})" for t in top_types])
            summary_parts.append(f"Principaux domaines: {types_str}")
        
        # Sentiment général
        sentiments = [item.sentiment for item in items if item.sentiment]
        if sentiments:
            positive_count = sentiments.count("positive")
            negative_count = sentiments.count("negative")
            if positive_count > negative_count:
                summary_parts.append("Tendance générale positive")
            elif negative_count > positive_count:
                summary_parts.append("Tendance générale négative")
            else:
                summary_parts.append("Tendance générale neutre")
        
        # Items les plus pertinents
        if high_relevance_items:
            top_item = max(high_relevance_items, key=lambda x: x.relevance_score)
            summary_parts.append(f"Item le plus pertinent: '{top_item.title}' (score: {top_item.relevance_score:.1f})")
        
        return ". ".join(summary_parts) + "."
    
    def _generate_intelligence_recommendations(self, items: List[IntelligenceItem], agent_id: str) -> List[str]:
        """Génère des recommandations basées sur l'intelligence collectée"""
        recommendations = []
        
        if not items:
            return [
                "Vérifier la configuration des sources d'intelligence",
                "Augmenter la fréquence de collecte",
                "Ajouter de nouvelles sources pertinentes"
            ]
        
        # Recommandations basées sur la relevance
        avg_relevance = sum(item.relevance_score for item in items) / len(items)
        if avg_relevance < 6.0:
            recommendations.append("Améliorer la qualité des sources - relevance moyenne faible")
        elif avg_relevance > 8.5:
            recommendations.append("Excellente qualité des sources - maintenir la configuration")
        
        # Recommandations basées sur les types d'intelligence
        type_counts = {}
        for item in items:
            type_counts[item.intelligence_type] = type_counts.get(item.intelligence_type, 0) + 1
        
        if len(type_counts) == 1:
            recommendations.append("Diversifier les types d'intelligence collectée")
        
        # Recommandations spécifiques par agent
        agent_recommendations = {
            "efs": [
                "Surveiller les tendances M&A dans le secteur tech",
                "Analyser l'impact des régulations financières",
                "Identifier les opportunités d'investissement"
            ],
            "eia": [
                "Suivre les avancées en IA générative",
                "Monitorer les innovations en quantum computing",
                "Analyser les tendances d'adoption enterprise"
            ],
            "ecyber": [
                "Surveiller les nouvelles vulnérabilités",
                "Analyser les tendances de cyberattaques",
                "Suivre l'évolution réglementaire cybersécurité"
            ]
        }
        
        if agent_id in agent_recommendations:
            recommendations.extend(agent_recommendations[agent_id][:2])
        
        return recommendations[:5]  # Limiter à 5 recommandations
    
    def get_daily_report(self, agent_id: str, date: datetime.date = None) -> Optional[DailyIntelligenceReport]:
        """Récupère le rapport quotidien d'un agent"""
        if date is None:
            date = datetime.date.today()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM daily_reports 
                WHERE agent_id = ? AND date = ?
            """, (agent_id, date.isoformat()))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return DailyIntelligenceReport(
                id=row['id'],
                agent_id=row['agent_id'],
                date=datetime.date.fromisoformat(row['date']),
                items_count=row['items_count'],
                avg_relevance=row['avg_relevance'],
                top_keywords=json.loads(row['top_keywords']),
                summary=row['summary'],
                recommendations=json.loads(row['recommendations']),
                generated_at=datetime.datetime.fromisoformat(row['generated_at'])
            )
    
    def get_intelligence_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques d'intelligence"""
        with sqlite3.connect(self.db_path) as conn:
            # Statistiques générales
            cursor = conn.execute("SELECT COUNT(*) FROM intelligence_items")
            total_items = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM intelligence_items WHERE DATE(collected_at) = DATE('now')")
            today_items = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM intelligence_sources WHERE active = 1")
            active_sources = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT AVG(relevance_score) FROM intelligence_items")
            avg_relevance = cursor.fetchone()[0] or 0.0
            
            cursor = conn.execute("SELECT MAX(collected_at) FROM intelligence_items")
            last_collection = cursor.fetchone()[0]
            
            # Statistiques par agent
            cursor = conn.execute("""
                SELECT agent_id, COUNT(*) as count, AVG(relevance_score) as avg_relevance
                FROM intelligence_items 
                GROUP BY agent_id
                ORDER BY count DESC
            """)
            agent_stats = [
                {"agent_id": row[0], "items_count": row[1], "avg_relevance": round(row[2], 2)}
                for row in cursor.fetchall()
            ]
            
            # Statistiques par type
            cursor = conn.execute("""
                SELECT intelligence_type, COUNT(*) as count
                FROM intelligence_items 
                GROUP BY intelligence_type
                ORDER BY count DESC
            """)
            type_stats = [
                {"type": row[0], "count": row[1]}
                for row in cursor.fetchall()
            ]
            
            return {
                "total_items": total_items,
                "today_items": today_items,
                "active_sources": active_sources,
                "avg_relevance": round(avg_relevance, 2),
                "last_collection": last_collection,
                "agent_stats": agent_stats,
                "type_stats": type_stats,
                "collection_status": "running" if self.running else "stopped"
            }
    
    def _get_active_sources(self) -> List[IntelligenceSource]:
        """Récupère toutes les sources actives"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM intelligence_sources WHERE active = 1")
            
            sources = []
            for row in cursor.fetchall():
                source = IntelligenceSource(
                    id=row['id'],
                    name=row['name'],
                    url=row['url'],
                    type=SourceType(row['type']),
                    intelligence_types=[IntelligenceType(t) for t in json.loads(row['intelligence_types'])],
                    agent_id=row['agent_id'],
                    priority=Priority(row['priority']),
                    frequency_hours=row['frequency_hours'],
                    active=bool(row['active']),
                    last_collected=datetime.datetime.fromisoformat(row['last_collected']) if row['last_collected'] else None,
                    success_rate=row['success_rate'],
                    avg_relevance=row['avg_relevance']
                )
                sources.append(source)
            
            return sources
    
    def _get_sources_by_priority(self, priorities: Tuple[Priority, ...]) -> List[IntelligenceSource]:
        """Récupère les sources par priorité"""
        priority_values = [p.value for p in priorities]
        placeholders = ','.join(['?'] * len(priority_values))
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(f"""
                SELECT * FROM intelligence_sources 
                WHERE active = 1 AND priority IN ({placeholders})
            """, priority_values)
            
            sources = []
            for row in cursor.fetchall():
                source = IntelligenceSource(
                    id=row['id'],
                    name=row['name'],
                    url=row['url'],
                    type=SourceType(row['type']),
                    intelligence_types=[IntelligenceType(t) for t in json.loads(row['intelligence_types'])],
                    agent_id=row['agent_id'],
                    priority=Priority(row['priority']),
                    frequency_hours=row['frequency_hours'],
                    active=bool(row['active']),
                    last_collected=datetime.datetime.fromisoformat(row['last_collected']) if row['last_collected'] else None,
                    success_rate=row['success_rate'],
                    avg_relevance=row['avg_relevance']
                )
                sources.append(source)
            
            return sources
    
    def _get_agents_with_intelligence(self) -> List[str]:
        """Récupère la liste des agents ayant de l'intelligence"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT DISTINCT agent_id FROM intelligence_sources WHERE active = 1")
            return [row[0] for row in cursor.fetchall()]
    
    def _get_agent_items_by_date(self, agent_id: str, date: datetime.date) -> List[IntelligenceItem]:
        """Récupère les items d'intelligence d'un agent pour une date"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM intelligence_items 
                WHERE agent_id = ? AND DATE(collected_at) = ?
                ORDER BY relevance_score DESC
            """, (agent_id, date.isoformat()))
            
            items = []
            for row in cursor.fetchall():
                item = IntelligenceItem(
                    id=row['id'],
                    source_id=row['source_id'],
                    agent_id=row['agent_id'],
                    title=row['title'],
                    content=row['content'],
                    url=row['url'],
                    intelligence_type=IntelligenceType(row['intelligence_type']),
                    priority=Priority(row['priority']),
                    relevance_score=row['relevance_score'],
                    sentiment=row['sentiment'],
                    keywords=json.loads(row['keywords']),
                    collected_at=datetime.datetime.fromisoformat(row['collected_at']),
                    processed=bool(row['processed']),
                    summary=row['summary']
                )
                items.append(item)
            
            return items
    
    def _save_source(self, source: IntelligenceSource):
        """Sauvegarde une source d'intelligence"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO intelligence_sources
                (id, name, url, type, intelligence_types, agent_id, priority, frequency_hours, 
                 active, last_collected, success_rate, avg_relevance)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                source.id, source.name, source.url, source.type.value,
                json.dumps([t.value for t in source.intelligence_types]),
                source.agent_id, source.priority.value, source.frequency_hours,
                source.active, 
                source.last_collected.isoformat() if source.last_collected else None,
                source.success_rate, source.avg_relevance
            ))
    
    def _update_source(self, source: IntelligenceSource):
        """Met à jour une source d'intelligence"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE intelligence_sources 
                SET last_collected = ?, success_rate = ?, avg_relevance = ?
                WHERE id = ?
            """, (
                source.last_collected.isoformat() if source.last_collected else None,
                source.success_rate, source.avg_relevance, source.id
            ))
    
    def _save_intelligence_item(self, item: IntelligenceItem, content_hash: str):
        """Sauvegarde un item d'intelligence"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR IGNORE INTO intelligence_items
                (id, source_id, agent_id, title, content, url, intelligence_type, priority,
                 relevance_score, sentiment, keywords, collected_at, processed, summary, content_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item.id, item.source_id, item.agent_id, item.title, item.content, item.url,
                item.intelligence_type.value, item.priority.value, item.relevance_score,
                item.sentiment, json.dumps(item.keywords), item.collected_at.isoformat(),
                item.processed, item.summary, content_hash
            ))
    
    def _save_daily_report(self, report: DailyIntelligenceReport):
        """Sauvegarde un rapport quotidien"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO daily_reports
                (id, agent_id, date, items_count, avg_relevance, top_keywords, summary, recommendations, generated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                report.id, report.agent_id, report.date.isoformat(), report.items_count,
                report.avg_relevance, json.dumps(report.top_keywords), report.summary,
                json.dumps(report.recommendations), report.generated_at.isoformat()
            ))
    
    def _update_stats(self, results: Dict[str, Any]):
        """Met à jour les statistiques"""
        self.stats["total_collected"] += results["collected_items"]
        self.stats["today_collected"] += results["collected_items"]
        self.stats["sources_active"] = results["total_sources"] - results["errors"]
        self.stats["last_collection"] = datetime.datetime.now().isoformat()

# Instance globale
advanced_intelligence_collector = AdvancedIntelligenceCollector()

if __name__ == "__main__":
    # Test du collecteur
    collector = AdvancedIntelligenceCollector()
    
    # Démarrer le service
    collector.start_collection_service()
    
    # Collecte immédiate
    results = collector.collect_all_sources()
    print(f"📊 Collecte terminée: {results}")
    
    # Statistiques
    stats = collector.get_intelligence_stats()
    print(f"📈 Statistiques: {stats}")
    
    # Générer rapport quotidien pour un agent
    today = datetime.date.today()
    report = collector._generate_agent_daily_report("efs", today)
    print(f"📋 Rapport EFS: {report.summary}")

