#!/usr/bin/env python3
"""
Performance Analytics System - Substans.AI Enterprise
Système d'analytics de performance avancé avec IA prédictive et reporting temps réel
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import statistics
import threading
import time
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Métrique de performance"""
    id: str
    name: str
    category: str
    value: float
    unit: str
    timestamp: datetime
    entity_id: str
    entity_type: str
    context: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

@dataclass
class KPI:
    """Indicateur clé de performance"""
    id: str
    name: str
    description: str
    category: str
    target_value: float
    current_value: float
    unit: str
    trend: str  # 'up', 'down', 'stable'
    status: str  # 'excellent', 'good', 'warning', 'critical'
    last_updated: datetime
    
    def calculate_achievement_rate(self) -> float:
        """Calcule le taux d'atteinte de l'objectif"""
        if self.target_value == 0:
            return 100.0 if self.current_value == 0 else 0.0
        return min(100.0, (self.current_value / self.target_value) * 100)
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['last_updated'] = self.last_updated.isoformat()
        data['achievement_rate'] = self.calculate_achievement_rate()
        return data

@dataclass
class PerformanceReport:
    """Rapport de performance"""
    id: str
    title: str
    period_start: datetime
    period_end: datetime
    entity_type: str
    entity_id: Optional[str]
    metrics: List[PerformanceMetric]
    kpis: List[KPI]
    insights: List[str]
    recommendations: List[str]
    score: float
    generated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'title': self.title,
            'period_start': self.period_start.isoformat(),
            'period_end': self.period_end.isoformat(),
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'metrics': [m.to_dict() for m in self.metrics],
            'kpis': [k.to_dict() for k in self.kpis],
            'insights': self.insights,
            'recommendations': self.recommendations,
            'score': self.score,
            'generated_at': self.generated_at.isoformat()
        }

class PerformanceAnalytics:
    """Système d'analytics de performance enterprise"""
    
    def __init__(self, db_path: str = "performance_analytics.db"):
        self.db_path = db_path
        self.running = False
        self.analytics_thread = None
        
        # Configuration des catégories de métriques
        self.metric_categories = {
            'productivity': 'Productivité',
            'quality': 'Qualité',
            'efficiency': 'Efficacité',
            'satisfaction': 'Satisfaction',
            'financial': 'Financier',
            'time': 'Temps',
            'resource': 'Ressources',
            'innovation': 'Innovation'
        }
        
        # Configuration des KPIs par défaut
        self.default_kpis = {
            'mission_success_rate': {
                'name': 'Taux de Succès des Missions',
                'description': 'Pourcentage de missions terminées avec succès',
                'category': 'quality',
                'target_value': 95.0,
                'unit': '%'
            },
            'average_mission_duration': {
                'name': 'Durée Moyenne des Missions',
                'description': 'Temps moyen pour compléter une mission',
                'category': 'time',
                'target_value': 14.0,
                'unit': 'jours'
            },
            'client_satisfaction': {
                'name': 'Satisfaction Client',
                'description': 'Score moyen de satisfaction client',
                'category': 'satisfaction',
                'target_value': 4.5,
                'unit': '/5'
            },
            'agent_utilization': {
                'name': 'Utilisation des Agents',
                'description': 'Pourcentage d\'utilisation des agents',
                'category': 'resource',
                'target_value': 80.0,
                'unit': '%'
            },
            'revenue_per_mission': {
                'name': 'Revenus par Mission',
                'description': 'Revenus moyens générés par mission',
                'category': 'financial',
                'target_value': 50000.0,
                'unit': '€'
            },
            'quality_score': {
                'name': 'Score Qualité Global',
                'description': 'Score moyen de qualité des livrables',
                'category': 'quality',
                'target_value': 85.0,
                'unit': '/100'
            }
        }
        
        self._init_database()
        logger.info("Performance Analytics System initialisé")
    
    def _init_database(self):
        """Initialise la base de données"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    value REAL NOT NULL,
                    unit TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    context TEXT NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS kpis (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    category TEXT NOT NULL,
                    target_value REAL NOT NULL,
                    current_value REAL NOT NULL,
                    unit TEXT NOT NULL,
                    trend TEXT NOT NULL,
                    status TEXT NOT NULL,
                    last_updated TEXT NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS reports (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    period_start TEXT NOT NULL,
                    period_end TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    entity_id TEXT,
                    data TEXT NOT NULL,
                    score REAL NOT NULL,
                    generated_at TEXT NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS benchmarks (
                    id TEXT PRIMARY KEY,
                    metric_name TEXT NOT NULL,
                    industry TEXT NOT NULL,
                    percentile_25 REAL NOT NULL,
                    percentile_50 REAL NOT NULL,
                    percentile_75 REAL NOT NULL,
                    percentile_90 REAL NOT NULL,
                    last_updated TEXT NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS alerts (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    entity_id TEXT,
                    threshold_value REAL,
                    current_value REAL,
                    created_at TEXT NOT NULL,
                    resolved_at TEXT,
                    status TEXT NOT NULL
                );
                
                CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics(timestamp);
                CREATE INDEX IF NOT EXISTS idx_metrics_entity ON metrics(entity_type, entity_id);
                CREATE INDEX IF NOT EXISTS idx_reports_period ON reports(period_start, period_end);
                CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);
            """)
        
        # Initialiser les KPIs par défaut
        self._init_default_kpis()
    
    def _init_default_kpis(self):
        """Initialise les KPIs par défaut"""
        for kpi_id, config in self.default_kpis.items():
            kpi = KPI(
                id=kpi_id,
                name=config['name'],
                description=config['description'],
                category=config['category'],
                target_value=config['target_value'],
                current_value=0.0,
                unit=config['unit'],
                trend='stable',
                status='warning',
                last_updated=datetime.now()
            )
            self.save_kpi(kpi)
    
    def record_metric(self, metric: PerformanceMetric):
        """Enregistre une métrique de performance"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO metrics 
                (id, name, category, value, unit, timestamp, entity_id, entity_type, context)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metric.id, metric.name, metric.category, metric.value,
                metric.unit, metric.timestamp.isoformat(), metric.entity_id,
                metric.entity_type, json.dumps(metric.context)
            ))
        
        # Mettre à jour les KPIs liés
        self._update_related_kpis(metric)
        
        # Vérifier les alertes
        self._check_alerts(metric)
        
        logger.info(f"Métrique enregistrée: {metric.name} = {metric.value} {metric.unit}")
    
    def save_kpi(self, kpi: KPI):
        """Sauvegarde un KPI"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO kpis 
                (id, name, description, category, target_value, current_value, 
                 unit, trend, status, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                kpi.id, kpi.name, kpi.description, kpi.category,
                kpi.target_value, kpi.current_value, kpi.unit,
                kpi.trend, kpi.status, kpi.last_updated.isoformat()
            ))
    
    def get_metrics(self, entity_type: Optional[str] = None, 
                   entity_id: Optional[str] = None,
                   category: Optional[str] = None,
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None) -> List[PerformanceMetric]:
        """Récupère les métriques selon les critères"""
        query = "SELECT * FROM metrics WHERE 1=1"
        params = []
        
        if entity_type:
            query += " AND entity_type = ?"
            params.append(entity_type)
        
        if entity_id:
            query += " AND entity_id = ?"
            params.append(entity_id)
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date.isoformat())
        
        query += " ORDER BY timestamp DESC"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            
            metrics = []
            for row in cursor.fetchall():
                metric = PerformanceMetric(
                    id=row['id'],
                    name=row['name'],
                    category=row['category'],
                    value=row['value'],
                    unit=row['unit'],
                    timestamp=datetime.fromisoformat(row['timestamp']),
                    entity_id=row['entity_id'],
                    entity_type=row['entity_type'],
                    context=json.loads(row['context'])
                )
                metrics.append(metric)
            
            return metrics
    
    def get_kpis(self, category: Optional[str] = None) -> List[KPI]:
        """Récupère les KPIs"""
        query = "SELECT * FROM kpis"
        params = []
        
        if category:
            query += " WHERE category = ?"
            params.append(category)
        
        query += " ORDER BY name"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            
            kpis = []
            for row in cursor.fetchall():
                kpi = KPI(
                    id=row['id'],
                    name=row['name'],
                    description=row['description'],
                    category=row['category'],
                    target_value=row['target_value'],
                    current_value=row['current_value'],
                    unit=row['unit'],
                    trend=row['trend'],
                    status=row['status'],
                    last_updated=datetime.fromisoformat(row['last_updated'])
                )
                kpis.append(kpi)
            
            return kpis
    
    def generate_performance_report(self, entity_type: str, 
                                  entity_id: Optional[str] = None,
                                  period_days: int = 30) -> PerformanceReport:
        """Génère un rapport de performance"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        # Récupérer les métriques de la période
        metrics = self.get_metrics(
            entity_type=entity_type,
            entity_id=entity_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Récupérer les KPIs
        kpis = self.get_kpis()
        
        # Générer des insights
        insights = self._generate_insights(metrics, kpis)
        
        # Générer des recommandations
        recommendations = self._generate_recommendations(metrics, kpis)
        
        # Calculer le score global
        score = self._calculate_performance_score(metrics, kpis)
        
        # Créer le rapport
        report_id = f"report_{entity_type}_{entity_id or 'all'}_{int(time.time())}"
        title = f"Rapport de Performance - {entity_type}"
        if entity_id:
            title += f" ({entity_id})"
        
        report = PerformanceReport(
            id=report_id,
            title=title,
            period_start=start_date,
            period_end=end_date,
            entity_type=entity_type,
            entity_id=entity_id,
            metrics=metrics,
            kpis=kpis,
            insights=insights,
            recommendations=recommendations,
            score=score,
            generated_at=datetime.now()
        )
        
        # Sauvegarder le rapport
        self._save_report(report)
        
        logger.info(f"Rapport de performance généré: {report.title}")
        return report
    
    def _update_related_kpis(self, metric: PerformanceMetric):
        """Met à jour les KPIs liés à une métrique"""
        kpi_updates = {
            'mission_success_rate': ['mission_completion', 'mission_success'],
            'average_mission_duration': ['mission_duration'],
            'client_satisfaction': ['satisfaction_score'],
            'agent_utilization': ['agent_usage', 'agent_activity'],
            'revenue_per_mission': ['mission_revenue'],
            'quality_score': ['quality_rating', 'deliverable_quality']
        }
        
        for kpi_id, metric_names in kpi_updates.items():
            if metric.name in metric_names:
                self._recalculate_kpi(kpi_id, metric.category)
    
    def _recalculate_kpi(self, kpi_id: str, category: str):
        """Recalcule un KPI basé sur les métriques récentes"""
        # Récupérer les métriques des 30 derniers jours
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        metrics = self.get_metrics(
            category=category,
            start_date=start_date,
            end_date=end_date
        )
        
        if not metrics:
            return
        
        # Calculer la nouvelle valeur selon le KPI
        if kpi_id == 'mission_success_rate':
            success_metrics = [m for m in metrics if m.name == 'mission_success']
            total_metrics = [m for m in metrics if m.name in ['mission_success', 'mission_failure']]
            new_value = (len(success_metrics) / len(total_metrics) * 100) if total_metrics else 0
        
        elif kpi_id == 'average_mission_duration':
            duration_metrics = [m for m in metrics if m.name == 'mission_duration']
            new_value = statistics.mean([m.value for m in duration_metrics]) if duration_metrics else 0
        
        elif kpi_id in ['client_satisfaction', 'quality_score']:
            relevant_metrics = [m for m in metrics if kpi_id.replace('_', '') in m.name.replace('_', '')]
            new_value = statistics.mean([m.value for m in relevant_metrics]) if relevant_metrics else 0
        
        else:
            # Calcul générique
            new_value = statistics.mean([m.value for m in metrics]) if metrics else 0
        
        # Mettre à jour le KPI
        kpis = self.get_kpis()
        for kpi in kpis:
            if kpi.id == kpi_id:
                old_value = kpi.current_value
                kpi.current_value = new_value
                
                # Déterminer la tendance
                if new_value > old_value * 1.05:
                    kpi.trend = 'up'
                elif new_value < old_value * 0.95:
                    kpi.trend = 'down'
                else:
                    kpi.trend = 'stable'
                
                # Déterminer le statut
                achievement_rate = kpi.calculate_achievement_rate()
                if achievement_rate >= 95:
                    kpi.status = 'excellent'
                elif achievement_rate >= 80:
                    kpi.status = 'good'
                elif achievement_rate >= 60:
                    kpi.status = 'warning'
                else:
                    kpi.status = 'critical'
                
                kpi.last_updated = datetime.now()
                self.save_kpi(kpi)
                break
    
    def _check_alerts(self, metric: PerformanceMetric):
        """Vérifie et génère des alertes basées sur les métriques"""
        # Seuils d'alerte par catégorie
        alert_thresholds = {
            'quality': {'critical': 60, 'warning': 75},
            'satisfaction': {'critical': 3.0, 'warning': 3.5},
            'efficiency': {'critical': 50, 'warning': 70},
            'time': {'critical': 30, 'warning': 20}  # jours de retard
        }
        
        if metric.category in alert_thresholds:
            thresholds = alert_thresholds[metric.category]
            
            severity = None
            if metric.value <= thresholds['critical']:
                severity = 'critical'
            elif metric.value <= thresholds['warning']:
                severity = 'warning'
            
            if severity:
                alert_id = f"alert_{metric.entity_type}_{metric.entity_id}_{int(time.time())}"
                
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        INSERT INTO alerts 
                        (id, type, severity, title, description, entity_type, entity_id,
                         threshold_value, current_value, created_at, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        alert_id, 'performance', severity,
                        f"Performance {severity.upper()}: {metric.name}",
                        f"La métrique {metric.name} a une valeur de {metric.value} {metric.unit}, "
                        f"en dessous du seuil {severity} de {thresholds[severity]}",
                        metric.entity_type, metric.entity_id,
                        thresholds[severity], metric.value,
                        datetime.now().isoformat(), 'active'
                    ))
                
                logger.warning(f"Alerte {severity}: {metric.name} = {metric.value}")
    
    def _generate_insights(self, metrics: List[PerformanceMetric], 
                          kpis: List[KPI]) -> List[str]:
        """Génère des insights basés sur les métriques et KPIs"""
        insights = []
        
        # Analyser les tendances des KPIs
        excellent_kpis = [k for k in kpis if k.status == 'excellent']
        critical_kpis = [k for k in kpis if k.status == 'critical']
        
        if excellent_kpis:
            insights.append(f"Performance excellente sur {len(excellent_kpis)} KPIs: "
                          f"{', '.join([k.name for k in excellent_kpis[:3]])}")
        
        if critical_kpis:
            insights.append(f"Attention requise sur {len(critical_kpis)} KPIs critiques: "
                          f"{', '.join([k.name for k in critical_kpis[:3]])}")
        
        # Analyser les métriques par catégorie
        metrics_by_category = defaultdict(list)
        for metric in metrics:
            metrics_by_category[metric.category].append(metric)
        
        for category, cat_metrics in metrics_by_category.items():
            if len(cat_metrics) >= 5:  # Assez de données pour analyse
                values = [m.value for m in cat_metrics]
                avg_value = statistics.mean(values)
                trend = "stable"
                
                if len(values) >= 2:
                    recent_avg = statistics.mean(values[:len(values)//2])
                    older_avg = statistics.mean(values[len(values)//2:])
                    
                    if recent_avg > older_avg * 1.1:
                        trend = "amélioration"
                    elif recent_avg < older_avg * 0.9:
                        trend = "dégradation"
                
                insights.append(f"Catégorie {category}: moyenne de {avg_value:.1f}, "
                              f"tendance {trend}")
        
        return insights[:10]  # Limiter à 10 insights
    
    def _generate_recommendations(self, metrics: List[PerformanceMetric], 
                                kpis: List[KPI]) -> List[str]:
        """Génère des recommandations basées sur l'analyse"""
        recommendations = []
        
        # Recommandations basées sur les KPIs critiques
        critical_kpis = [k for k in kpis if k.status == 'critical']
        for kpi in critical_kpis[:3]:
            if kpi.category == 'quality':
                recommendations.append(f"Améliorer {kpi.name}: mettre en place des revues qualité supplémentaires")
            elif kpi.category == 'time':
                recommendations.append(f"Optimiser {kpi.name}: revoir la planification et l'allocation des ressources")
            elif kpi.category == 'satisfaction':
                recommendations.append(f"Améliorer {kpi.name}: renforcer la communication client et le suivi")
            else:
                recommendations.append(f"Améliorer {kpi.name}: analyser les causes racines et mettre en place un plan d'action")
        
        # Recommandations basées sur les tendances
        declining_kpis = [k for k in kpis if k.trend == 'down']
        if len(declining_kpis) >= 3:
            recommendations.append("Plusieurs KPIs en baisse: effectuer un audit complet des processus")
        
        # Recommandations génériques
        if not recommendations:
            recommendations.extend([
                "Continuer le monitoring des performances pour maintenir les standards",
                "Mettre en place des benchmarks sectoriels pour comparaison",
                "Automatiser davantage de métriques pour un suivi temps réel"
            ])
        
        return recommendations[:5]  # Limiter à 5 recommandations
    
    def _calculate_performance_score(self, metrics: List[PerformanceMetric], 
                                   kpis: List[KPI]) -> float:
        """Calcule un score global de performance"""
        if not kpis:
            return 0.0
        
        # Pondération par statut
        status_weights = {
            'excellent': 100,
            'good': 80,
            'warning': 60,
            'critical': 30
        }
        
        total_score = 0
        total_weight = 0
        
        for kpi in kpis:
            weight = 1.0
            if kpi.category in ['quality', 'satisfaction']:
                weight = 1.5  # Plus important
            
            score = status_weights.get(kpi.status, 50)
            total_score += score * weight
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _save_report(self, report: PerformanceReport):
        """Sauvegarde un rapport"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO reports 
                (id, title, period_start, period_end, entity_type, entity_id, 
                 data, score, generated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                report.id, report.title,
                report.period_start.isoformat(), report.period_end.isoformat(),
                report.entity_type, report.entity_id,
                json.dumps(report.to_dict()), report.score,
                report.generated_at.isoformat()
            ))
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Récupère les données pour le dashboard"""
        kpis = self.get_kpis()
        
        # Métriques récentes (7 derniers jours)
        recent_metrics = self.get_metrics(
            start_date=datetime.now() - timedelta(days=7)
        )
        
        # Alertes actives
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM alerts 
                WHERE status = 'active' 
                ORDER BY created_at DESC 
                LIMIT 10
            """)
            alerts = [dict(row) for row in cursor.fetchall()]
        
        # Statistiques par catégorie
        category_stats = {}
        for category in self.metric_categories:
            cat_kpis = [k for k in kpis if k.category == category]
            if cat_kpis:
                avg_achievement = statistics.mean([k.calculate_achievement_rate() for k in cat_kpis])
                category_stats[category] = {
                    'name': self.metric_categories[category],
                    'kpi_count': len(cat_kpis),
                    'avg_achievement': avg_achievement,
                    'status': 'excellent' if avg_achievement >= 90 else 
                             'good' if avg_achievement >= 75 else 
                             'warning' if avg_achievement >= 60 else 'critical'
                }
        
        return {
            'kpis': [k.to_dict() for k in kpis],
            'recent_metrics_count': len(recent_metrics),
            'active_alerts': alerts,
            'category_stats': category_stats,
            'overall_score': self._calculate_performance_score(recent_metrics, kpis),
            'last_updated': datetime.now().isoformat()
        }
    
    def start_analytics_service(self):
        """Démarre le service d'analytics en arrière-plan"""
        if self.running:
            return
        
        self.running = True
        self.analytics_thread = threading.Thread(target=self._analytics_loop, daemon=True)
        self.analytics_thread.start()
        logger.info("Service d'analytics démarré")
    
    def stop_analytics_service(self):
        """Arrête le service d'analytics"""
        self.running = False
        if self.analytics_thread:
            self.analytics_thread.join()
        logger.info("Service d'analytics arrêté")
    
    def _analytics_loop(self):
        """Boucle principale du service d'analytics"""
        while self.running:
            try:
                # Recalculer les KPIs toutes les heures
                for kpi_id in self.default_kpis:
                    self._recalculate_kpi(kpi_id, 'all')
                
                # Nettoyer les anciennes métriques (> 90 jours)
                cutoff_date = datetime.now() - timedelta(days=90)
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("DELETE FROM metrics WHERE timestamp < ?", 
                               (cutoff_date.isoformat(),))
                
                # Résoudre les alertes anciennes (> 7 jours)
                alert_cutoff = datetime.now() - timedelta(days=7)
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        UPDATE alerts 
                        SET status = 'auto_resolved', resolved_at = ? 
                        WHERE status = 'active' AND created_at < ?
                    """, (datetime.now().isoformat(), alert_cutoff.isoformat()))
                
                time.sleep(3600)  # Attendre 1 heure
                
            except Exception as e:
                logger.error(f"Erreur dans la boucle analytics: {e}")
                time.sleep(60)  # Attendre 1 minute en cas d'erreur

# Exemple d'utilisation
if __name__ == "__main__":
    # Créer le système d'analytics
    analytics = PerformanceAnalytics()
    
    # Démarrer le service
    analytics.start_analytics_service()
    
    # Enregistrer quelques métriques d'exemple
    test_metrics = [
        PerformanceMetric(
            id="metric_1",
            name="mission_success",
            category="quality",
            value=1.0,
            unit="boolean",
            timestamp=datetime.now(),
            entity_id="mission_001",
            entity_type="mission",
            context={"client": "Bull", "type": "strategic_analysis"}
        ),
        PerformanceMetric(
            id="metric_2",
            name="mission_duration",
            category="time",
            value=12.5,
            unit="days",
            timestamp=datetime.now(),
            entity_id="mission_001",
            entity_type="mission",
            context={"planned": 14, "actual": 12.5}
        ),
        PerformanceMetric(
            id="metric_3",
            name="satisfaction_score",
            category="satisfaction",
            value=4.2,
            unit="/5",
            timestamp=datetime.now(),
            entity_id="client_bull",
            entity_type="client",
            context={"survey_id": "survey_001"}
        )
    ]
    
    for metric in test_metrics:
        analytics.record_metric(metric)
    
    # Générer un rapport
    report = analytics.generate_performance_report("mission", period_days=30)
    print(f"Rapport généré: {report.title}")
    print(f"Score: {report.score:.1f}")
    print(f"Insights: {len(report.insights)}")
    print(f"Recommandations: {len(report.recommendations)}")
    
    # Afficher le dashboard
    dashboard = analytics.get_dashboard_data()
    print(f"Dashboard - Score global: {dashboard['overall_score']:.1f}")
    print(f"KPIs: {len(dashboard['kpis'])}")
    print(f"Alertes actives: {len(dashboard['active_alerts'])}")
    
    # Arrêter le service
    analytics.stop_analytics_service()

