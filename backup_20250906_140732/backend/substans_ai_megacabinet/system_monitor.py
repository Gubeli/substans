"""
System Monitor - Moniteur Système
Surveillance et monitoring enterprise-grade pour substans.ai
"""

import json
import logging
import os
import psutil
import time
import threading
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
from concurrent.futures import ThreadPoolExecutor
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import requests

# Configuration du logging
logging.basicConfig(level=logging.INFO)

class AlertLevel(Enum):
    """Niveaux d'alerte"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class MetricType(Enum):
    """Types de métriques"""
    SYSTEM = "system"
    APPLICATION = "application"
    BUSINESS = "business"
    PERFORMANCE = "performance"
    SECURITY = "security"

class MonitorStatus(Enum):
    """États du monitoring"""
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"

@dataclass
class Alert:
    """Alerte système"""
    alert_id: str
    level: AlertLevel
    title: str
    message: str
    metric_name: str
    current_value: float
    threshold_value: float
    created_at: datetime
    resolved_at: Optional[datetime]
    resolved: bool
    metadata: Dict[str, Any]

@dataclass
class Metric:
    """Métrique système"""
    metric_id: str
    name: str
    metric_type: MetricType
    value: float
    unit: str
    timestamp: datetime
    tags: Dict[str, str]
    metadata: Dict[str, Any]

@dataclass
class Threshold:
    """Seuil d'alerte"""
    threshold_id: str
    metric_name: str
    operator: str  # >, <, >=, <=, ==, !=
    value: float
    alert_level: AlertLevel
    enabled: bool
    created_at: datetime

class SystemMonitor:
    """
    Moniteur système pour surveillance enterprise-grade
    Collecte des métriques, génère des alertes, et assure la supervision
    """
    
    def __init__(self, core_engine=None):
        self.monitor_id = str(uuid.uuid4())
        self.logger = logging.getLogger(f"SystemMonitor-{self.monitor_id[:8]}")
        
        # Référence au moteur principal
        self.core_engine = core_engine
        
        # État du monitoring
        self.status = MonitorStatus.ACTIVE
        self.start_time = datetime.now()
        
        # Métriques et alertes
        self.current_metrics = {}
        self.active_alerts = {}
        self.resolved_alerts = {}
        self.thresholds = {}
        
        # Configuration
        self.collection_interval = 30  # secondes
        self.retention_days = 30
        self.max_alerts = 1000
        
        # Callbacks d'alerte
        self.alert_callbacks = []
        
        # Services
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.collection_thread = None
        self.cleanup_thread = None
        
        # Base de données
        self.db_path = '/home/ubuntu/substans_ai_megacabinet/data/monitor.db'
        self._initialize_database()
        
        # Chargement des seuils
        self._load_thresholds()
        
        # Démarrage du monitoring
        self._start_monitoring()
        
        self.logger.info(f"System Monitor initialisé - ID: {self.monitor_id}")

    def _initialize_database(self):
        """Initialise la base de données de monitoring"""
        
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Table des métriques
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS metrics (
                    metric_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    metric_type TEXT NOT NULL,
                    value REAL NOT NULL,
                    unit TEXT,
                    timestamp TIMESTAMP NOT NULL,
                    tags TEXT,
                    metadata TEXT
                )
            ''')
            
            # Index sur timestamp pour les requêtes temporelles
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_metrics_timestamp 
                ON metrics(timestamp)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_metrics_name 
                ON metrics(name)
            ''')
            
            # Table des alertes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    alert_id TEXT PRIMARY KEY,
                    level TEXT NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    current_value REAL,
                    threshold_value REAL,
                    created_at TIMESTAMP NOT NULL,
                    resolved_at TIMESTAMP,
                    resolved BOOLEAN DEFAULT FALSE,
                    metadata TEXT
                )
            ''')
            
            # Table des seuils
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS thresholds (
                    threshold_id TEXT PRIMARY KEY,
                    metric_name TEXT NOT NULL,
                    operator TEXT NOT NULL,
                    value REAL NOT NULL,
                    alert_level TEXT NOT NULL,
                    enabled BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP NOT NULL
                )
            ''')
            
            # Table des événements système
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_events (
                    event_id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    severity TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    metadata TEXT
                )
            ''')
            
            conn.commit()

    def _load_thresholds(self):
        """Charge les seuils depuis la base de données"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM thresholds WHERE enabled = TRUE')
                
                for row in cursor.fetchall():
                    threshold_data = dict(zip([col[0] for col in cursor.description], row))
                    
                    threshold = Threshold(
                        threshold_id=threshold_data['threshold_id'],
                        metric_name=threshold_data['metric_name'],
                        operator=threshold_data['operator'],
                        value=threshold_data['value'],
                        alert_level=AlertLevel(threshold_data['alert_level']),
                        enabled=threshold_data['enabled'],
                        created_at=datetime.fromisoformat(threshold_data['created_at'])
                    )
                    
                    self.thresholds[threshold.threshold_id] = threshold
            
            self.logger.info(f"{len(self.thresholds)} seuils chargés")
            
        except Exception as e:
            self.logger.error(f"Erreur chargement seuils: {e}")

    def _start_monitoring(self):
        """Démarre les services de monitoring"""
        
        # Service de collecte des métriques
        self.collection_thread = threading.Thread(
            target=self._metrics_collection_service, daemon=True
        )
        self.collection_thread.start()
        
        # Service de nettoyage
        self.cleanup_thread = threading.Thread(
            target=self._cleanup_service, daemon=True
        )
        self.cleanup_thread.start()
        
        # Initialisation des seuils par défaut
        self._setup_default_thresholds()

    def _setup_default_thresholds(self):
        """Configure les seuils par défaut"""
        
        default_thresholds = [
            # Métriques système
            ('cpu_usage', '>', 80.0, AlertLevel.WARNING),
            ('cpu_usage', '>', 95.0, AlertLevel.CRITICAL),
            ('memory_usage', '>', 85.0, AlertLevel.WARNING),
            ('memory_usage', '>', 95.0, AlertLevel.CRITICAL),
            ('disk_usage', '>', 90.0, AlertLevel.WARNING),
            ('disk_usage', '>', 98.0, AlertLevel.CRITICAL),
            
            # Métriques application
            ('active_tasks', '>', 100, AlertLevel.WARNING),
            ('failed_tasks', '>', 10, AlertLevel.ERROR),
            ('response_time', '>', 5000, AlertLevel.WARNING),  # ms
            ('error_rate', '>', 5.0, AlertLevel.WARNING),  # %
            
            # Métriques business
            ('mission_success_rate', '<', 80.0, AlertLevel.WARNING),
            ('agent_availability', '<', 90.0, AlertLevel.ERROR),
        ]
        
        for metric_name, operator, value, level in default_thresholds:
            if not any(t.metric_name == metric_name and t.operator == operator 
                      for t in self.thresholds.values()):
                self.add_threshold(metric_name, operator, value, level)

    def collect_metric(self, name: str, value: float, metric_type: MetricType = MetricType.APPLICATION,
                      unit: str = '', tags: Dict[str, str] = None, 
                      metadata: Dict[str, Any] = None) -> str:
        """Collecte une métrique"""
        
        metric_id = str(uuid.uuid4())
        
        metric = Metric(
            metric_id=metric_id,
            name=name,
            metric_type=metric_type,
            value=value,
            unit=unit,
            timestamp=datetime.now(),
            tags=tags or {},
            metadata=metadata or {}
        )
        
        # Stockage en mémoire
        self.current_metrics[name] = metric
        
        # Sauvegarde en base
        self._save_metric(metric)
        
        # Vérification des seuils
        self._check_thresholds(metric)
        
        return metric_id

    def _collect_system_metrics(self):
        """Collecte les métriques système"""
        
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            self.collect_metric('cpu_usage', cpu_percent, MetricType.SYSTEM, '%')
            
            # Mémoire
            memory = psutil.virtual_memory()
            self.collect_metric('memory_usage', memory.percent, MetricType.SYSTEM, '%')
            self.collect_metric('memory_available', memory.available / (1024**3), MetricType.SYSTEM, 'GB')
            
            # Disque
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.collect_metric('disk_usage', disk_percent, MetricType.SYSTEM, '%')
            self.collect_metric('disk_free', disk.free / (1024**3), MetricType.SYSTEM, 'GB')
            
            # Réseau
            network = psutil.net_io_counters()
            self.collect_metric('network_bytes_sent', network.bytes_sent, MetricType.SYSTEM, 'bytes')
            self.collect_metric('network_bytes_recv', network.bytes_recv, MetricType.SYSTEM, 'bytes')
            
            # Processus
            process_count = len(psutil.pids())
            self.collect_metric('process_count', process_count, MetricType.SYSTEM, 'count')
            
            # Load average (Linux/Unix)
            try:
                load_avg = os.getloadavg()
                self.collect_metric('load_average_1m', load_avg[0], MetricType.SYSTEM)
                self.collect_metric('load_average_5m', load_avg[1], MetricType.SYSTEM)
                self.collect_metric('load_average_15m', load_avg[2], MetricType.SYSTEM)
            except:
                pass  # Windows n'a pas getloadavg
            
        except Exception as e:
            self.logger.error(f"Erreur collecte métriques système: {e}")

    def _collect_application_metrics(self):
        """Collecte les métriques applicatives"""
        
        try:
            if self.core_engine:
                # Métriques du moteur principal
                engine_metrics = self.core_engine.get_system_metrics()
                
                for metric_name, value in engine_metrics.items():
                    if isinstance(value, (int, float)):
                        self.collect_metric(
                            f"engine_{metric_name}", 
                            value, 
                            MetricType.APPLICATION
                        )
                
                # Métriques des tâches
                task_stats = self.core_engine.get_task_statistics()
                
                self.collect_metric('active_tasks', task_stats.get('active', 0), MetricType.APPLICATION)
                self.collect_metric('completed_tasks', task_stats.get('completed', 0), MetricType.APPLICATION)
                self.collect_metric('failed_tasks', task_stats.get('failed', 0), MetricType.APPLICATION)
                
                # Taux de succès
                total_tasks = task_stats.get('completed', 0) + task_stats.get('failed', 0)
                if total_tasks > 0:
                    success_rate = (task_stats.get('completed', 0) / total_tasks) * 100
                    self.collect_metric('task_success_rate', success_rate, MetricType.BUSINESS, '%')
                
                # Temps de réponse moyen
                avg_response_time = task_stats.get('average_execution_time', 0) * 1000  # ms
                self.collect_metric('response_time', avg_response_time, MetricType.PERFORMANCE, 'ms')
            
            # Métriques de l'application
            uptime = (datetime.now() - self.start_time).total_seconds()
            self.collect_metric('uptime', uptime, MetricType.APPLICATION, 'seconds')
            
            # Métriques des alertes
            self.collect_metric('active_alerts_count', len(self.active_alerts), MetricType.APPLICATION)
            
        except Exception as e:
            self.logger.error(f"Erreur collecte métriques application: {e}")

    def _check_thresholds(self, metric: Metric):
        """Vérifie les seuils pour une métrique"""
        
        for threshold in self.thresholds.values():
            if threshold.metric_name == metric.name and threshold.enabled:
                
                # Évaluation du seuil
                triggered = self._evaluate_threshold(metric.value, threshold)
                
                if triggered:
                    # Vérification si l'alerte existe déjà
                    existing_alert = None
                    for alert in self.active_alerts.values():
                        if (alert.metric_name == metric.name and 
                            alert.level == threshold.alert_level and
                            not alert.resolved):
                            existing_alert = alert
                            break
                    
                    if not existing_alert:
                        # Création d'une nouvelle alerte
                        self._create_alert(metric, threshold)

    def _evaluate_threshold(self, value: float, threshold: Threshold) -> bool:
        """Évalue si un seuil est dépassé"""
        
        if threshold.operator == '>':
            return value > threshold.value
        elif threshold.operator == '<':
            return value < threshold.value
        elif threshold.operator == '>=':
            return value >= threshold.value
        elif threshold.operator == '<=':
            return value <= threshold.value
        elif threshold.operator == '==':
            return value == threshold.value
        elif threshold.operator == '!=':
            return value != threshold.value
        else:
            return False

    def _create_alert(self, metric: Metric, threshold: Threshold):
        """Crée une nouvelle alerte"""
        
        alert_id = str(uuid.uuid4())
        
        alert = Alert(
            alert_id=alert_id,
            level=threshold.alert_level,
            title=f"Seuil dépassé: {metric.name}",
            message=f"La métrique {metric.name} ({metric.value} {metric.unit}) "
                   f"a dépassé le seuil {threshold.operator} {threshold.value}",
            metric_name=metric.name,
            current_value=metric.value,
            threshold_value=threshold.value,
            created_at=datetime.now(),
            resolved_at=None,
            resolved=False,
            metadata={
                'threshold_id': threshold.threshold_id,
                'metric_type': metric.metric_type.value,
                'tags': metric.tags
            }
        )
        
        # Stockage
        self.active_alerts[alert_id] = alert
        
        # Sauvegarde en base
        self._save_alert(alert)
        
        # Notification
        self._notify_alert(alert)
        
        self.logger.warning(f"Alerte créée: {alert.title}")

    def _notify_alert(self, alert: Alert):
        """Notifie une alerte"""
        
        # Appel des callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                self.logger.error(f"Erreur callback alerte: {e}")
        
        # Log selon le niveau
        if alert.level == AlertLevel.CRITICAL:
            self.logger.critical(alert.message)
        elif alert.level == AlertLevel.ERROR:
            self.logger.error(alert.message)
        elif alert.level == AlertLevel.WARNING:
            self.logger.warning(alert.message)
        else:
            self.logger.info(alert.message)

    def add_threshold(self, metric_name: str, operator: str, value: float,
                     alert_level: AlertLevel) -> str:
        """Ajoute un seuil d'alerte"""
        
        threshold_id = str(uuid.uuid4())
        
        threshold = Threshold(
            threshold_id=threshold_id,
            metric_name=metric_name,
            operator=operator,
            value=value,
            alert_level=alert_level,
            enabled=True,
            created_at=datetime.now()
        )
        
        self.thresholds[threshold_id] = threshold
        
        # Sauvegarde en base
        self._save_threshold(threshold)
        
        self.logger.info(f"Seuil ajouté: {metric_name} {operator} {value}")
        
        return threshold_id

    def remove_threshold(self, threshold_id: str) -> bool:
        """Supprime un seuil"""
        
        if threshold_id not in self.thresholds:
            return False
        
        del self.thresholds[threshold_id]
        
        # Suppression en base
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM thresholds WHERE threshold_id = ?', (threshold_id,))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Erreur suppression seuil: {e}")
        
        return True

    def resolve_alert(self, alert_id: str, resolution_note: str = '') -> bool:
        """Résout une alerte"""
        
        if alert_id not in self.active_alerts:
            return False
        
        alert = self.active_alerts[alert_id]
        alert.resolved = True
        alert.resolved_at = datetime.now()
        alert.metadata['resolution_note'] = resolution_note
        
        # Déplacement vers les alertes résolues
        self.resolved_alerts[alert_id] = alert
        del self.active_alerts[alert_id]
        
        # Mise à jour en base
        self._save_alert(alert)
        
        self.logger.info(f"Alerte résolue: {alert.title}")
        
        return True

    def add_alert_callback(self, callback: Callable[[Alert], None]):
        """Ajoute un callback d'alerte"""
        
        self.alert_callbacks.append(callback)

    def get_metrics(self, metric_name: str = None, start_time: datetime = None,
                   end_time: datetime = None, limit: int = 1000) -> List[Dict[str, Any]]:
        """Récupère les métriques"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = 'SELECT * FROM metrics WHERE 1=1'
                params = []
                
                if metric_name:
                    query += ' AND name = ?'
                    params.append(metric_name)
                
                if start_time:
                    query += ' AND timestamp >= ?'
                    params.append(start_time)
                
                if end_time:
                    query += ' AND timestamp <= ?'
                    params.append(end_time)
                
                query += ' ORDER BY timestamp DESC LIMIT ?'
                params.append(limit)
                
                cursor.execute(query, params)
                
                metrics = []
                for row in cursor.fetchall():
                    metric_data = dict(zip([col[0] for col in cursor.description], row))
                    metric_data['tags'] = json.loads(metric_data['tags']) if metric_data['tags'] else {}
                    metric_data['metadata'] = json.loads(metric_data['metadata']) if metric_data['metadata'] else {}
                    metrics.append(metric_data)
                
                return metrics
                
        except Exception as e:
            self.logger.error(f"Erreur récupération métriques: {e}")
            return []

    def get_alerts(self, resolved: bool = None, level: AlertLevel = None,
                  limit: int = 100) -> List[Dict[str, Any]]:
        """Récupère les alertes"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = 'SELECT * FROM alerts WHERE 1=1'
                params = []
                
                if resolved is not None:
                    query += ' AND resolved = ?'
                    params.append(resolved)
                
                if level:
                    query += ' AND level = ?'
                    params.append(level.value)
                
                query += ' ORDER BY created_at DESC LIMIT ?'
                params.append(limit)
                
                cursor.execute(query, params)
                
                alerts = []
                for row in cursor.fetchall():
                    alert_data = dict(zip([col[0] for col in cursor.description], row))
                    alert_data['metadata'] = json.loads(alert_data['metadata']) if alert_data['metadata'] else {}
                    alerts.append(alert_data)
                
                return alerts
                
        except Exception as e:
            self.logger.error(f"Erreur récupération alertes: {e}")
            return []

    def get_system_health(self) -> Dict[str, Any]:
        """Retourne l'état de santé du système"""
        
        health = {
            'status': 'healthy',
            'uptime': (datetime.now() - self.start_time).total_seconds(),
            'active_alerts': len(self.active_alerts),
            'critical_alerts': len([a for a in self.active_alerts.values() 
                                  if a.level == AlertLevel.CRITICAL]),
            'metrics_collected': len(self.current_metrics),
            'last_collection': None
        }
        
        # Dernière collecte
        if self.current_metrics:
            latest_metric = max(self.current_metrics.values(), key=lambda m: m.timestamp)
            health['last_collection'] = latest_metric.timestamp.isoformat()
        
        # Détermination du statut global
        if health['critical_alerts'] > 0:
            health['status'] = 'critical'
        elif health['active_alerts'] > 0:
            health['status'] = 'warning'
        elif (datetime.now() - self.start_time).total_seconds() < 300:  # 5 minutes
            health['status'] = 'starting'
        
        # Métriques système actuelles
        system_metrics = {}
        for name, metric in self.current_metrics.items():
            if metric.metric_type == MetricType.SYSTEM:
                system_metrics[name] = {
                    'value': metric.value,
                    'unit': metric.unit,
                    'timestamp': metric.timestamp.isoformat()
                }
        
        health['system_metrics'] = system_metrics
        
        return health

    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Retourne un résumé des performances"""
        
        start_time = datetime.now() - timedelta(hours=hours)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Métriques moyennes
                cursor.execute('''
                    SELECT name, AVG(value) as avg_value, MIN(value) as min_value, 
                           MAX(value) as max_value, COUNT(*) as count
                    FROM metrics 
                    WHERE timestamp >= ? AND metric_type = 'performance'
                    GROUP BY name
                ''', (start_time,))
                
                performance_metrics = {}
                for row in cursor.fetchall():
                    name, avg_val, min_val, max_val, count = row
                    performance_metrics[name] = {
                        'average': avg_val,
                        'minimum': min_val,
                        'maximum': max_val,
                        'samples': count
                    }
                
                # Alertes dans la période
                cursor.execute('''
                    SELECT level, COUNT(*) as count
                    FROM alerts 
                    WHERE created_at >= ?
                    GROUP BY level
                ''', (start_time,))
                
                alert_summary = {}
                for row in cursor.fetchall():
                    level, count = row
                    alert_summary[level] = count
                
                return {
                    'period_hours': hours,
                    'performance_metrics': performance_metrics,
                    'alert_summary': alert_summary,
                    'generated_at': datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Erreur résumé performances: {e}")
            return {}

    def _save_metric(self, metric: Metric):
        """Sauvegarde une métrique en base"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO metrics 
                    (metric_id, name, metric_type, value, unit, timestamp, tags, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    metric.metric_id, metric.name, metric.metric_type.value,
                    metric.value, metric.unit, metric.timestamp,
                    json.dumps(metric.tags), json.dumps(metric.metadata)
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde métrique: {e}")

    def _save_alert(self, alert: Alert):
        """Sauvegarde une alerte en base"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO alerts 
                    (alert_id, level, title, message, metric_name, current_value,
                     threshold_value, created_at, resolved_at, resolved, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    alert.alert_id, alert.level.value, alert.title, alert.message,
                    alert.metric_name, alert.current_value, alert.threshold_value,
                    alert.created_at, alert.resolved_at, alert.resolved,
                    json.dumps(alert.metadata)
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde alerte: {e}")

    def _save_threshold(self, threshold: Threshold):
        """Sauvegarde un seuil en base"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO thresholds 
                    (threshold_id, metric_name, operator, value, alert_level, enabled, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    threshold.threshold_id, threshold.metric_name, threshold.operator,
                    threshold.value, threshold.alert_level.value, threshold.enabled,
                    threshold.created_at
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde seuil: {e}")

    def _metrics_collection_service(self):
        """Service de collecte des métriques"""
        
        while self.status == MonitorStatus.ACTIVE:
            try:
                # Collecte des métriques système
                self._collect_system_metrics()
                
                # Collecte des métriques applicatives
                self._collect_application_metrics()
                
                time.sleep(self.collection_interval)
                
            except Exception as e:
                self.logger.error(f"Erreur service collecte: {e}")
                time.sleep(self.collection_interval)

    def _cleanup_service(self):
        """Service de nettoyage des données anciennes"""
        
        while self.status == MonitorStatus.ACTIVE:
            try:
                cutoff_date = datetime.now() - timedelta(days=self.retention_days)
                
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Nettoyage des métriques anciennes
                    cursor.execute('DELETE FROM metrics WHERE timestamp < ?', (cutoff_date,))
                    metrics_deleted = cursor.rowcount
                    
                    # Nettoyage des alertes résolues anciennes
                    cursor.execute('''
                        DELETE FROM alerts 
                        WHERE resolved = TRUE AND resolved_at < ?
                    ''', (cutoff_date,))
                    alerts_deleted = cursor.rowcount
                    
                    conn.commit()
                
                if metrics_deleted > 0 or alerts_deleted > 0:
                    self.logger.info(f"Nettoyage: {metrics_deleted} métriques, {alerts_deleted} alertes supprimées")
                
                # Nettoyage toutes les heures
                time.sleep(3600)
                
            except Exception as e:
                self.logger.error(f"Erreur service nettoyage: {e}")
                time.sleep(3600)

    def stop_monitoring(self):
        """Arrête le monitoring"""
        
        self.status = MonitorStatus.STOPPED
        self.logger.info("Monitoring arrêté")

    def pause_monitoring(self):
        """Met en pause le monitoring"""
        
        self.status = MonitorStatus.PAUSED
        self.logger.info("Monitoring en pause")

    def resume_monitoring(self):
        """Reprend le monitoring"""
        
        self.status = MonitorStatus.ACTIVE
        self.logger.info("Monitoring repris")

# Instance globale
_system_monitor = None

def get_system_monitor() -> SystemMonitor:
    """Retourne l'instance du moniteur système"""
    global _system_monitor
    if _system_monitor is None:
        _system_monitor = SystemMonitor()
    return _system_monitor

# Test du moniteur
if __name__ == '__main__':
    print("=== Test System Monitor ===")
    
    monitor = SystemMonitor()
    
    # Test de collecte de métrique
    monitor.collect_metric('test_metric', 75.5, MetricType.APPLICATION, '%')
    print("Métrique collectée")
    
    # Test d'ajout de seuil
    threshold_id = monitor.add_threshold('test_metric', '>', 70.0, AlertLevel.WARNING)
    print(f"Seuil ajouté: {threshold_id}")
    
    # Attente pour voir l'alerte
    time.sleep(2)
    
    # Vérification des alertes
    alerts = monitor.get_alerts(resolved=False)
    print(f"Alertes actives: {len(alerts)}")
    
    # État de santé
    health = monitor.get_system_health()
    print(f"État système: {health['status']}")
    
    print("Test terminé")

