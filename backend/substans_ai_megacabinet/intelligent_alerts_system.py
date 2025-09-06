#!/usr/bin/env python3
"""
Intelligent Alerts System - Système d'Alertes Intelligentes
Système complet d'alertes avec IA prédictive, multi-canal et escalation automatique
"""

import os
import json
import sqlite3
import datetime
import threading
import time
import smtplib
import requests
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
from pathlib import Path
import logging
import asyncio
import concurrent.futures
from collections import defaultdict, deque
import statistics
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pickle

# Configuration logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class AlertStatus(Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    SUPPRESSED = "suppressed"

class AlertChannel(Enum):
    EMAIL = "email"
    SMS = "sms"
    SLACK = "slack"
    WEBHOOK = "webhook"
    IN_APP = "in_app"
    TEAMS = "teams"
    DISCORD = "discord"

class AlertType(Enum):
    PERFORMANCE = "performance"
    SECURITY = "security"
    SYSTEM = "system"
    BUSINESS = "business"
    PREDICTIVE = "predictive"
    ANOMALY = "anomaly"

@dataclass
class AlertRule:
    """Règle d'alerte"""
    id: str
    name: str
    description: str
    alert_type: AlertType
    severity: AlertSeverity
    condition: str  # Expression Python évaluable
    threshold: float
    duration_minutes: int
    channels: List[AlertChannel]
    enabled: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime
    tags: List[str]
    escalation_rules: List[Dict[str, Any]]

@dataclass
class Alert:
    """Alerte"""
    id: str
    rule_id: str
    title: str
    description: str
    severity: AlertSeverity
    status: AlertStatus
    alert_type: AlertType
    source: str
    value: float
    threshold: float
    created_at: datetime.datetime
    updated_at: datetime.datetime
    acknowledged_at: Optional[datetime.datetime]
    resolved_at: Optional[datetime.datetime]
    acknowledged_by: Optional[str]
    resolved_by: Optional[str]
    metadata: Dict[str, Any]
    escalation_level: int
    notification_count: int

@dataclass
class NotificationChannel:
    """Canal de notification"""
    channel_type: AlertChannel
    name: str
    config: Dict[str, Any]
    enabled: bool
    rate_limit: int  # Messages par heure
    retry_count: int
    timeout_seconds: int

class AnomalyDetector:
    """Détecteur d'anomalies avec IA"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.training_data = defaultdict(list)
        self.min_samples = 50
        self.contamination = 0.1
        
    def add_data_point(self, metric_name: str, value: float, timestamp: datetime.datetime):
        """Ajoute un point de données pour l'entraînement"""
        self.training_data[metric_name].append({
            'value': value,
            'timestamp': timestamp,
            'hour': timestamp.hour,
            'day_of_week': timestamp.weekday(),
            'day_of_month': timestamp.day
        })
        
        # Garder seulement les 1000 derniers points
        if len(self.training_data[metric_name]) > 1000:
            self.training_data[metric_name] = self.training_data[metric_name][-1000:]
    
    def train_model(self, metric_name: str) -> bool:
        """Entraîne le modèle pour une métrique"""
        if len(self.training_data[metric_name]) < self.min_samples:
            return False
        
        try:
            # Préparer les données
            data = self.training_data[metric_name]
            features = []
            
            for point in data:
                features.append([
                    point['value'],
                    point['hour'],
                    point['day_of_week'],
                    point['day_of_month']
                ])
            
            X = np.array(features)
            
            # Normaliser les données
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Entraîner le modèle d'isolation forest
            model = IsolationForest(
                contamination=self.contamination,
                random_state=42,
                n_estimators=100
            )
            model.fit(X_scaled)
            
            # Sauvegarder le modèle et le scaler
            self.models[metric_name] = model
            self.scalers[metric_name] = scaler
            
            logger.info(f"🤖 Modèle d'anomalie entraîné pour {metric_name}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur entraînement modèle {metric_name}: {e}")
            return False
    
    def detect_anomaly(self, metric_name: str, value: float, timestamp: datetime.datetime) -> Dict[str, Any]:
        """Détecte une anomalie"""
        if metric_name not in self.models:
            return {"is_anomaly": False, "confidence": 0.0, "reason": "Modèle non entraîné"}
        
        try:
            # Préparer les données
            features = np.array([[
                value,
                timestamp.hour,
                timestamp.weekday(),
                timestamp.day
            ]])
            
            # Normaliser
            scaler = self.scalers[metric_name]
            features_scaled = scaler.transform(features)
            
            # Prédire
            model = self.models[metric_name]
            prediction = model.predict(features_scaled)[0]
            anomaly_score = model.decision_function(features_scaled)[0]
            
            is_anomaly = prediction == -1
            confidence = abs(anomaly_score)
            
            # Analyser le type d'anomalie
            reason = self._analyze_anomaly_reason(metric_name, value, timestamp)
            
            return {
                "is_anomaly": is_anomaly,
                "confidence": confidence,
                "anomaly_score": anomaly_score,
                "reason": reason
            }
            
        except Exception as e:
            logger.error(f"Erreur détection anomalie {metric_name}: {e}")
            return {"is_anomaly": False, "confidence": 0.0, "reason": f"Erreur: {e}"}
    
    def _analyze_anomaly_reason(self, metric_name: str, value: float, timestamp: datetime.datetime) -> str:
        """Analyse la raison de l'anomalie"""
        if not self.training_data[metric_name]:
            return "Données insuffisantes"
        
        recent_data = [p['value'] for p in self.training_data[metric_name][-100:]]
        avg_value = statistics.mean(recent_data)
        std_value = statistics.stdev(recent_data) if len(recent_data) > 1 else 0
        
        if value > avg_value + 2 * std_value:
            return f"Valeur anormalement élevée ({value:.2f} vs moyenne {avg_value:.2f})"
        elif value < avg_value - 2 * std_value:
            return f"Valeur anormalement faible ({value:.2f} vs moyenne {avg_value:.2f})"
        else:
            return "Anomalie de pattern temporel"

class IntelligentAlertsSystem:
    """Système d'alertes intelligentes"""
    
    def __init__(self, base_path: str = "/home/ubuntu/substans_ai_megacabinet"):
        self.base_path = Path(base_path)
        self.db_path = self.base_path / "data" / "alerts.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Composants
        self.anomaly_detector = AnomalyDetector()
        self.notification_channels = {}
        self.alert_rules = {}
        self.active_alerts = {}
        
        # Configuration
        self.check_interval = 30  # secondes
        self.escalation_enabled = True
        self.rate_limiting_enabled = True
        
        # Threads et services
        self.monitoring_thread = None
        self.escalation_thread = None
        self.running = False
        
        # Métriques
        self.metrics_buffer = defaultdict(deque)
        self.notification_stats = defaultdict(int)
        
        self._init_database()
        self._init_default_channels()
        self._init_default_rules()
        self._start_services()
    
    def _init_database(self):
        """Initialise la base de données"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS alert_rules (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    condition_expr TEXT NOT NULL,
                    threshold REAL NOT NULL,
                    duration_minutes INTEGER NOT NULL,
                    channels TEXT NOT NULL,
                    enabled BOOLEAN NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    tags TEXT,
                    escalation_rules TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id TEXT PRIMARY KEY,
                    rule_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    severity TEXT NOT NULL,
                    status TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    source TEXT NOT NULL,
                    value REAL NOT NULL,
                    threshold REAL NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    acknowledged_at TIMESTAMP,
                    resolved_at TIMESTAMP,
                    acknowledged_by TEXT,
                    resolved_by TEXT,
                    metadata TEXT,
                    escalation_level INTEGER DEFAULT 0,
                    notification_count INTEGER DEFAULT 0
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS notification_log (
                    id TEXT PRIMARY KEY,
                    alert_id TEXT NOT NULL,
                    channel_type TEXT NOT NULL,
                    recipient TEXT NOT NULL,
                    status TEXT NOT NULL,
                    sent_at TIMESTAMP NOT NULL,
                    error_message TEXT,
                    retry_count INTEGER DEFAULT 0
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS metrics_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT NOT NULL,
                    value REAL NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    source TEXT NOT NULL
                )
            """)
            
            # Index pour les performances
            conn.execute("CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_alerts_created ON alerts(created_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_metrics_name_time ON metrics_history(metric_name, timestamp)")
            
            conn.commit()
    
    def _init_default_channels(self):
        """Initialise les canaux par défaut"""
        self.notification_channels = {
            "email_admin": NotificationChannel(
                channel_type=AlertChannel.EMAIL,
                name="Email Admin",
                config={
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "username": "admin@substans.ai",
                    "password": "app_password",
                    "recipients": ["admin@substans.ai"]
                },
                enabled=True,
                rate_limit=60,
                retry_count=3,
                timeout_seconds=30
            ),
            "slack_alerts": NotificationChannel(
                channel_type=AlertChannel.SLACK,
                name="Slack Alerts",
                config={
                    "webhook_url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
                    "channel": "#alerts",
                    "username": "Substans.AI"
                },
                enabled=True,
                rate_limit=120,
                retry_count=2,
                timeout_seconds=15
            ),
            "webhook_general": NotificationChannel(
                channel_type=AlertChannel.WEBHOOK,
                name="Webhook General",
                config={
                    "url": "https://api.substans.ai/webhooks/alerts",
                    "method": "POST",
                    "headers": {"Authorization": "Bearer token"}
                },
                enabled=True,
                rate_limit=300,
                retry_count=3,
                timeout_seconds=10
            )
        }
    
    def _init_default_rules(self):
        """Initialise les règles par défaut"""
        default_rules = [
            {
                "name": "CPU Élevé",
                "description": "CPU supérieur à 85% pendant 5 minutes",
                "alert_type": AlertType.PERFORMANCE,
                "severity": AlertSeverity.HIGH,
                "condition": "cpu_percent > threshold",
                "threshold": 85.0,
                "duration_minutes": 5,
                "channels": [AlertChannel.EMAIL, AlertChannel.SLACK],
                "tags": ["performance", "cpu"]
            },
            {
                "name": "Mémoire Critique",
                "description": "Utilisation mémoire supérieure à 90%",
                "alert_type": AlertType.PERFORMANCE,
                "severity": AlertSeverity.CRITICAL,
                "condition": "memory_percent > threshold",
                "threshold": 90.0,
                "duration_minutes": 2,
                "channels": [AlertChannel.EMAIL, AlertChannel.SLACK, AlertChannel.WEBHOOK],
                "tags": ["performance", "memory"]
            },
            {
                "name": "Anomalie Détectée",
                "description": "Anomalie détectée par l'IA",
                "alert_type": AlertType.ANOMALY,
                "severity": AlertSeverity.MEDIUM,
                "condition": "anomaly_confidence > threshold",
                "threshold": 0.7,
                "duration_minutes": 1,
                "channels": [AlertChannel.SLACK],
                "tags": ["ai", "anomaly"]
            },
            {
                "name": "Échec Mission",
                "description": "Mission échouée ou bloquée",
                "alert_type": AlertType.BUSINESS,
                "severity": AlertSeverity.HIGH,
                "condition": "mission_failure_rate > threshold",
                "threshold": 0.1,
                "duration_minutes": 10,
                "channels": [AlertChannel.EMAIL, AlertChannel.WEBHOOK],
                "tags": ["business", "mission"]
            },
            {
                "name": "Sécurité Compromise",
                "description": "Tentative d'accès non autorisé",
                "alert_type": AlertType.SECURITY,
                "severity": AlertSeverity.EMERGENCY,
                "condition": "security_breach_detected == True",
                "threshold": 1.0,
                "duration_minutes": 0,
                "channels": [AlertChannel.EMAIL, AlertChannel.SLACK, AlertChannel.WEBHOOK],
                "tags": ["security", "breach"]
            }
        ]
        
        for rule_data in default_rules:
            rule = AlertRule(
                id=str(uuid.uuid4()),
                name=rule_data["name"],
                description=rule_data["description"],
                alert_type=rule_data["alert_type"],
                severity=rule_data["severity"],
                condition=rule_data["condition"],
                threshold=rule_data["threshold"],
                duration_minutes=rule_data["duration_minutes"],
                channels=rule_data["channels"],
                enabled=True,
                created_at=datetime.datetime.now(),
                updated_at=datetime.datetime.now(),
                tags=rule_data["tags"],
                escalation_rules=[
                    {"level": 1, "delay_minutes": 15, "channels": [AlertChannel.EMAIL]},
                    {"level": 2, "delay_minutes": 30, "channels": [AlertChannel.EMAIL, AlertChannel.SLACK]},
                    {"level": 3, "delay_minutes": 60, "channels": [AlertChannel.EMAIL, AlertChannel.SLACK, AlertChannel.WEBHOOK]}
                ]
            )
            self.alert_rules[rule.id] = rule
    
    def _start_services(self):
        """Démarre les services d'arrière-plan"""
        if self.running:
            return
        
        self.running = True
        
        # Thread de monitoring
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        # Thread d'escalation
        if self.escalation_enabled:
            self.escalation_thread = threading.Thread(target=self._escalation_loop, daemon=True)
            self.escalation_thread.start()
        
        logger.info("🚀 Services d'alertes démarrés")
    
    def stop_services(self):
        """Arrête les services"""
        self.running = False
        logger.info("🛑 Services d'alertes arrêtés")
    
    def _monitoring_loop(self):
        """Boucle de monitoring des alertes"""
        while self.running:
            try:
                # Vérifier les règles d'alerte
                self._check_alert_rules()
                
                # Entraîner les modèles d'anomalie
                self._train_anomaly_models()
                
                # Nettoyer les anciennes données
                self._cleanup_old_data()
                
            except Exception as e:
                logger.error(f"Erreur monitoring alertes: {e}")
            
            time.sleep(self.check_interval)
    
    def _escalation_loop(self):
        """Boucle d'escalation des alertes"""
        while self.running:
            try:
                self._process_escalations()
            except Exception as e:
                logger.error(f"Erreur escalation: {e}")
            
            time.sleep(60)  # Vérifier les escalations chaque minute
    
    def add_metric(self, metric_name: str, value: float, source: str = "system"):
        """Ajoute une métrique pour monitoring"""
        timestamp = datetime.datetime.now()
        
        # Ajouter au buffer
        self.metrics_buffer[metric_name].append({
            'value': value,
            'timestamp': timestamp,
            'source': source
        })
        
        # Garder seulement les 1000 derniers points
        if len(self.metrics_buffer[metric_name]) > 1000:
            self.metrics_buffer[metric_name].popleft()
        
        # Ajouter aux données d'entraînement d'anomalie
        self.anomaly_detector.add_data_point(metric_name, value, timestamp)
        
        # Sauvegarder en base de données
        self._save_metric(metric_name, value, timestamp, source)
    
    def _save_metric(self, metric_name: str, value: float, timestamp: datetime.datetime, source: str):
        """Sauvegarde une métrique en base"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO metrics_history (metric_name, value, timestamp, source)
                    VALUES (?, ?, ?, ?)
                """, (metric_name, value, timestamp.isoformat(), source))
        except Exception as e:
            logger.error(f"Erreur sauvegarde métrique: {e}")
    
    def _check_alert_rules(self):
        """Vérifie les règles d'alerte"""
        current_time = datetime.datetime.now()
        
        for rule in self.alert_rules.values():
            if not rule.enabled:
                continue
            
            try:
                # Évaluer la condition
                should_alert = self._evaluate_rule_condition(rule)
                
                if should_alert:
                    # Vérifier si l'alerte existe déjà
                    existing_alert = self._get_active_alert_for_rule(rule.id)
                    
                    if existing_alert:
                        # Mettre à jour l'alerte existante
                        self._update_alert(existing_alert)
                    else:
                        # Créer une nouvelle alerte
                        self._create_alert(rule)
                
            except Exception as e:
                logger.error(f"Erreur évaluation règle {rule.name}: {e}")
    
    def _evaluate_rule_condition(self, rule: AlertRule) -> bool:
        """Évalue la condition d'une règle"""
        try:
            # Préparer le contexte d'évaluation
            context = self._build_evaluation_context(rule)
            
            # Évaluer l'expression
            result = eval(rule.condition, {"__builtins__": {}}, context)
            
            return bool(result)
            
        except Exception as e:
            logger.error(f"Erreur évaluation condition '{rule.condition}': {e}")
            return False
    
    def _build_evaluation_context(self, rule: AlertRule) -> Dict[str, Any]:
        """Construit le contexte d'évaluation pour une règle"""
        context = {"threshold": rule.threshold}
        
        # Ajouter les métriques récentes
        for metric_name, data_points in self.metrics_buffer.items():
            if data_points:
                latest_point = data_points[-1]
                context[metric_name] = latest_point['value']
                
                # Ajouter des statistiques
                recent_values = [p['value'] for p in list(data_points)[-10:]]
                context[f"{metric_name}_avg"] = statistics.mean(recent_values)
                context[f"{metric_name}_max"] = max(recent_values)
                context[f"{metric_name}_min"] = min(recent_values)
        
        # Ajouter des métriques d'anomalie
        for metric_name in self.metrics_buffer.keys():
            if metric_name in self.anomaly_detector.models:
                latest_data = self.metrics_buffer[metric_name]
                if latest_data:
                    latest_point = latest_data[-1]
                    anomaly_result = self.anomaly_detector.detect_anomaly(
                        metric_name, 
                        latest_point['value'], 
                        latest_point['timestamp']
                    )
                    context[f"{metric_name}_anomaly"] = anomaly_result['is_anomaly']
                    context[f"{metric_name}_anomaly_confidence"] = anomaly_result['confidence']
        
        # Ajouter des métriques système
        context.update({
            "current_time": datetime.datetime.now(),
            "hour": datetime.datetime.now().hour,
            "day_of_week": datetime.datetime.now().weekday(),
            "active_alerts_count": len(self.active_alerts),
            "security_breach_detected": False,  # À implémenter
            "mission_failure_rate": 0.0  # À implémenter
        })
        
        return context
    
    def _get_active_alert_for_rule(self, rule_id: str) -> Optional[Alert]:
        """Récupère l'alerte active pour une règle"""
        for alert in self.active_alerts.values():
            if alert.rule_id == rule_id and alert.status == AlertStatus.ACTIVE:
                return alert
        return None
    
    def _create_alert(self, rule: AlertRule):
        """Crée une nouvelle alerte"""
        alert_id = str(uuid.uuid4())
        current_time = datetime.datetime.now()
        
        # Récupérer la valeur actuelle
        context = self._build_evaluation_context(rule)
        current_value = 0.0
        
        # Essayer de trouver la métrique principale
        for key, value in context.items():
            if isinstance(value, (int, float)) and key != "threshold":
                current_value = value
                break
        
        alert = Alert(
            id=alert_id,
            rule_id=rule.id,
            title=f"🚨 {rule.name}",
            description=rule.description,
            severity=rule.severity,
            status=AlertStatus.ACTIVE,
            alert_type=rule.alert_type,
            source="intelligent_alerts_system",
            value=current_value,
            threshold=rule.threshold,
            created_at=current_time,
            updated_at=current_time,
            acknowledged_at=None,
            resolved_at=None,
            acknowledged_by=None,
            resolved_by=None,
            metadata={
                "rule_name": rule.name,
                "tags": rule.tags,
                "context": context
            },
            escalation_level=0,
            notification_count=0
        )
        
        # Ajouter à la liste des alertes actives
        self.active_alerts[alert_id] = alert
        
        # Sauvegarder en base
        self._save_alert(alert)
        
        # Envoyer les notifications
        self._send_notifications(alert, rule.channels)
        
        logger.warning(f"🚨 Nouvelle alerte créée: {alert.title}")
    
    def _update_alert(self, alert: Alert):
        """Met à jour une alerte existante"""
        alert.updated_at = datetime.datetime.now()
        alert.notification_count += 1
        
        # Sauvegarder en base
        self._save_alert(alert)
    
    def _save_alert(self, alert: Alert):
        """Sauvegarde une alerte en base"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO alerts
                    (id, rule_id, title, description, severity, status, alert_type, source,
                     value, threshold, created_at, updated_at, acknowledged_at, resolved_at,
                     acknowledged_by, resolved_by, metadata, escalation_level, notification_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    alert.id, alert.rule_id, alert.title, alert.description,
                    alert.severity.value, alert.status.value, alert.alert_type.value,
                    alert.source, alert.value, alert.threshold,
                    alert.created_at.isoformat(), alert.updated_at.isoformat(),
                    alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
                    alert.resolved_at.isoformat() if alert.resolved_at else None,
                    alert.acknowledged_by, alert.resolved_by,
                    json.dumps(alert.metadata), alert.escalation_level, alert.notification_count
                ))
        except Exception as e:
            logger.error(f"Erreur sauvegarde alerte: {e}")
    
    def _send_notifications(self, alert: Alert, channels: List[AlertChannel]):
        """Envoie les notifications pour une alerte"""
        for channel in channels:
            try:
                # Trouver le canal de notification configuré
                channel_config = None
                for config in self.notification_channels.values():
                    if config.channel_type == channel and config.enabled:
                        channel_config = config
                        break
                
                if not channel_config:
                    continue
                
                # Vérifier le rate limiting
                if self.rate_limiting_enabled:
                    if not self._check_rate_limit(channel_config):
                        continue
                
                # Envoyer la notification
                success = self._send_notification(alert, channel_config)
                
                # Enregistrer le log
                self._log_notification(alert.id, channel, "success" if success else "failed")
                
                if success:
                    self.notification_stats[f"{channel.value}_sent"] += 1
                else:
                    self.notification_stats[f"{channel.value}_failed"] += 1
                    
            except Exception as e:
                logger.error(f"Erreur envoi notification {channel.value}: {e}")
                self.notification_stats[f"{channel.value}_failed"] += 1
    
    def _check_rate_limit(self, channel_config: NotificationChannel) -> bool:
        """Vérifie le rate limiting pour un canal"""
        # Implémentation simplifiée - en production, utiliser Redis ou une base de données
        return True
    
    def _send_notification(self, alert: Alert, channel_config: NotificationChannel) -> bool:
        """Envoie une notification via un canal spécifique"""
        try:
            if channel_config.channel_type == AlertChannel.EMAIL:
                return self._send_email_notification(alert, channel_config)
            elif channel_config.channel_type == AlertChannel.SLACK:
                return self._send_slack_notification(alert, channel_config)
            elif channel_config.channel_type == AlertChannel.WEBHOOK:
                return self._send_webhook_notification(alert, channel_config)
            else:
                logger.warning(f"Canal non supporté: {channel_config.channel_type}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur envoi notification {channel_config.channel_type.value}: {e}")
            return False
    
    def _send_email_notification(self, alert: Alert, channel_config: NotificationChannel) -> bool:
        """Envoie une notification par email"""
        try:
            config = channel_config.config
            
            # Créer le message
            msg = MimeMultipart()
            msg['From'] = config['username']
            msg['To'] = ', '.join(config['recipients'])
            msg['Subject'] = f"[{alert.severity.value.upper()}] {alert.title}"
            
            # Corps du message
            body = f"""
Alerte Substans.AI

Titre: {alert.title}
Sévérité: {alert.severity.value.upper()}
Type: {alert.alert_type.value}
Description: {alert.description}

Valeur actuelle: {alert.value}
Seuil: {alert.threshold}
Créée le: {alert.created_at.strftime('%Y-%m-%d %H:%M:%S')}

Métadonnées:
{json.dumps(alert.metadata, indent=2)}

---
Substans.AI Intelligent Alerts System
            """
            
            msg.attach(MimeText(body, 'plain'))
            
            # Envoyer l'email
            server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
            server.starttls()
            server.login(config['username'], config['password'])
            server.send_message(msg)
            server.quit()
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur envoi email: {e}")
            return False
    
    def _send_slack_notification(self, alert: Alert, channel_config: NotificationChannel) -> bool:
        """Envoie une notification Slack"""
        try:
            config = channel_config.config
            
            # Couleur selon la sévérité
            color_map = {
                AlertSeverity.LOW: "#36a64f",
                AlertSeverity.MEDIUM: "#ff9500", 
                AlertSeverity.HIGH: "#ff0000",
                AlertSeverity.CRITICAL: "#8b0000",
                AlertSeverity.EMERGENCY: "#4b0082"
            }
            
            payload = {
                "channel": config['channel'],
                "username": config['username'],
                "attachments": [{
                    "color": color_map.get(alert.severity, "#ff0000"),
                    "title": alert.title,
                    "text": alert.description,
                    "fields": [
                        {"title": "Sévérité", "value": alert.severity.value.upper(), "short": True},
                        {"title": "Type", "value": alert.alert_type.value, "short": True},
                        {"title": "Valeur", "value": str(alert.value), "short": True},
                        {"title": "Seuil", "value": str(alert.threshold), "short": True}
                    ],
                    "footer": "Substans.AI",
                    "ts": int(alert.created_at.timestamp())
                }]
            }
            
            response = requests.post(
                config['webhook_url'],
                json=payload,
                timeout=channel_config.timeout_seconds
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Erreur envoi Slack: {e}")
            return False
    
    def _send_webhook_notification(self, alert: Alert, channel_config: NotificationChannel) -> bool:
        """Envoie une notification webhook"""
        try:
            config = channel_config.config
            
            payload = {
                "alert": asdict(alert),
                "timestamp": datetime.datetime.now().isoformat(),
                "source": "substans_ai_alerts"
            }
            
            headers = config.get('headers', {})
            headers['Content-Type'] = 'application/json'
            
            response = requests.request(
                method=config.get('method', 'POST'),
                url=config['url'],
                json=payload,
                headers=headers,
                timeout=channel_config.timeout_seconds
            )
            
            return response.status_code < 400
            
        except Exception as e:
            logger.error(f"Erreur envoi webhook: {e}")
            return False
    
    def _log_notification(self, alert_id: str, channel: AlertChannel, status: str):
        """Enregistre le log de notification"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO notification_log
                    (id, alert_id, channel_type, recipient, status, sent_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    str(uuid.uuid4()),
                    alert_id,
                    channel.value,
                    "system",
                    status,
                    datetime.datetime.now().isoformat()
                ))
        except Exception as e:
            logger.error(f"Erreur log notification: {e}")
    
    def _process_escalations(self):
        """Traite les escalations d'alertes"""
        current_time = datetime.datetime.now()
        
        for alert in list(self.active_alerts.values()):
            if alert.status != AlertStatus.ACTIVE:
                continue
            
            # Récupérer la règle
            rule = self.alert_rules.get(alert.rule_id)
            if not rule or not rule.escalation_rules:
                continue
            
            # Vérifier si une escalation est nécessaire
            for escalation_rule in rule.escalation_rules:
                level = escalation_rule['level']
                delay_minutes = escalation_rule['delay_minutes']
                
                if alert.escalation_level >= level:
                    continue
                
                # Vérifier le délai
                time_since_creation = (current_time - alert.created_at).total_seconds() / 60
                
                if time_since_creation >= delay_minutes:
                    # Escalader l'alerte
                    alert.escalation_level = level
                    alert.updated_at = current_time
                    
                    # Envoyer les notifications d'escalation
                    self._send_notifications(alert, escalation_rule['channels'])
                    
                    # Sauvegarder
                    self._save_alert(alert)
                    
                    logger.warning(f"🔺 Escalation niveau {level} pour alerte {alert.title}")
    
    def _train_anomaly_models(self):
        """Entraîne les modèles d'anomalie"""
        for metric_name in self.metrics_buffer.keys():
            if metric_name not in self.anomaly_detector.models:
                self.anomaly_detector.train_model(metric_name)
    
    def _cleanup_old_data(self):
        """Nettoie les anciennes données"""
        try:
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=30)
            
            with sqlite3.connect(self.db_path) as conn:
                # Nettoyer les anciennes métriques
                conn.execute("""
                    DELETE FROM metrics_history 
                    WHERE timestamp < ?
                """, (cutoff_date.isoformat(),))
                
                # Nettoyer les anciens logs de notification
                conn.execute("""
                    DELETE FROM notification_log 
                    WHERE sent_at < ?
                """, (cutoff_date.isoformat(),))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Erreur nettoyage données: {e}")
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acquitte une alerte"""
        if alert_id not in self.active_alerts:
            return False
        
        alert = self.active_alerts[alert_id]
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_at = datetime.datetime.now()
        alert.acknowledged_by = acknowledged_by
        alert.updated_at = datetime.datetime.now()
        
        self._save_alert(alert)
        logger.info(f"✅ Alerte acquittée: {alert.title} par {acknowledged_by}")
        return True
    
    def resolve_alert(self, alert_id: str, resolved_by: str) -> bool:
        """Résout une alerte"""
        if alert_id not in self.active_alerts:
            return False
        
        alert = self.active_alerts[alert_id]
        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = datetime.datetime.now()
        alert.resolved_by = resolved_by
        alert.updated_at = datetime.datetime.now()
        
        self._save_alert(alert)
        
        # Retirer de la liste des alertes actives
        del self.active_alerts[alert_id]
        
        logger.info(f"✅ Alerte résolue: {alert.title} par {resolved_by}")
        return True
    
    def get_alerts_dashboard(self) -> Dict[str, Any]:
        """Récupère le tableau de bord des alertes"""
        active_alerts = list(self.active_alerts.values())
        
        # Statistiques par sévérité
        severity_stats = defaultdict(int)
        for alert in active_alerts:
            severity_stats[alert.severity.value] += 1
        
        # Statistiques par type
        type_stats = defaultdict(int)
        for alert in active_alerts:
            type_stats[alert.alert_type.value] += 1
        
        # Alertes récentes (24h)
        recent_cutoff = datetime.datetime.now() - datetime.timedelta(hours=24)
        recent_alerts = [
            asdict(alert) for alert in active_alerts 
            if alert.created_at >= recent_cutoff
        ]
        
        return {
            "active_alerts_count": len(active_alerts),
            "severity_breakdown": dict(severity_stats),
            "type_breakdown": dict(type_stats),
            "recent_alerts": recent_alerts,
            "notification_stats": dict(self.notification_stats),
            "rules_count": len(self.alert_rules),
            "channels_count": len(self.notification_channels),
            "anomaly_models_trained": len(self.anomaly_detector.models),
            "system_status": "running" if self.running else "stopped"
        }

# Instance globale
intelligent_alerts = IntelligentAlertsSystem()

if __name__ == "__main__":
    # Test du système d'alertes
    alerts_system = IntelligentAlertsSystem()
    
    # Ajouter des métriques de test
    alerts_system.add_metric("cpu_percent", 88.5)
    alerts_system.add_metric("memory_percent", 92.3)
    alerts_system.add_metric("response_time_ms", 1250.0)
    
    # Attendre un peu pour que les alertes se déclenchent
    time.sleep(2)
    
    # Récupérer le tableau de bord
    dashboard = alerts_system.get_alerts_dashboard()
    print(f"🚨 Alertes actives: {dashboard['active_alerts_count']}")
    print(f"📊 Répartition sévérité: {dashboard['severity_breakdown']}")
    
    # Arrêter les services
    alerts_system.stop_services()

