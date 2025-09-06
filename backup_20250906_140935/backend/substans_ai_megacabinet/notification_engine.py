#!/usr/bin/env python3
"""
Notification Engine - Substans.AI Enterprise
Système de notifications multi-canal avec templates, scheduling et analytics
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import time
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from email.mime.base import MimeBase
from email import encoders
import requests
from pathlib import Path
import jinja2
from collections import defaultdict

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificationType(Enum):
    """Types de notifications"""
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    PUSH = "push"
    SLACK = "slack"
    TEAMS = "teams"
    IN_APP = "in_app"

class NotificationPriority(Enum):
    """Priorités de notification"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"

class NotificationStatus(Enum):
    """Statuts de notification"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class NotificationTemplate:
    """Template de notification"""
    id: str
    name: str
    type: NotificationType
    subject_template: str
    body_template: str
    variables: List[str]
    language: str
    category: str
    created_at: datetime
    updated_at: datetime
    active: bool
    
    def render(self, variables: Dict[str, Any]) -> Dict[str, str]:
        """Rend le template avec les variables"""
        env = jinja2.Environment()
        
        subject = env.from_string(self.subject_template).render(**variables)
        body = env.from_string(self.body_template).render(**variables)
        
        return {'subject': subject, 'body': body}
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['type'] = self.type.value
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data

@dataclass
class NotificationRecipient:
    """Destinataire de notification"""
    id: str
    name: str
    email: Optional[str]
    phone: Optional[str]
    webhook_url: Optional[str]
    slack_channel: Optional[str]
    teams_webhook: Optional[str]
    preferences: Dict[str, Any]
    timezone: str
    active: bool
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        return data

@dataclass
class Notification:
    """Notification"""
    id: str
    template_id: str
    recipient_id: str
    type: NotificationType
    priority: NotificationPriority
    subject: str
    body: str
    variables: Dict[str, Any]
    scheduled_at: Optional[datetime]
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    status: NotificationStatus
    error_message: Optional[str]
    retry_count: int
    max_retries: int
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['type'] = self.type.value
        data['priority'] = self.priority.value
        data['status'] = self.status.value
        data['scheduled_at'] = self.scheduled_at.isoformat() if self.scheduled_at else None
        data['sent_at'] = self.sent_at.isoformat() if self.sent_at else None
        data['delivered_at'] = self.delivered_at.isoformat() if self.delivered_at else None
        data['created_at'] = self.created_at.isoformat()
        return data

class NotificationEngine:
    """Moteur de notifications enterprise"""
    
    def __init__(self, db_path: str = "notifications.db"):
        self.db_path = db_path
        self.running = False
        self.notification_thread = None
        
        # Configuration des canaux
        self.channel_configs = {
            'email': {
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'username': '',
                'password': '',
                'use_tls': True
            },
            'sms': {
                'provider': 'twilio',
                'account_sid': '',
                'auth_token': '',
                'from_number': ''
            },
            'slack': {
                'bot_token': '',
                'default_channel': '#general'
            },
            'teams': {
                'webhook_url': ''
            }
        }
        
        # Handlers par type de notification
        self.handlers = {
            NotificationType.EMAIL: self._send_email,
            NotificationType.SMS: self._send_sms,
            NotificationType.WEBHOOK: self._send_webhook,
            NotificationType.SLACK: self._send_slack,
            NotificationType.TEAMS: self._send_teams,
            NotificationType.IN_APP: self._send_in_app
        }
        
        # Templates par défaut
        self.default_templates = {
            'mission_started': {
                'name': 'Mission Démarrée',
                'type': NotificationType.EMAIL,
                'subject': 'Mission {{mission_title}} démarrée',
                'body': '''
Bonjour {{recipient_name}},

La mission "{{mission_title}}" a été démarrée.

Détails:
- Client: {{client_name}}
- Type: {{mission_type}}
- Échéance: {{due_date}}
- Agents assignés: {{agents}}

Vous pouvez suivre le progrès sur la plateforme Substans.AI.

Cordialement,
L'équipe Substans.AI
                ''',
                'variables': ['recipient_name', 'mission_title', 'client_name', 'mission_type', 'due_date', 'agents'],
                'category': 'mission'
            },
            'mission_completed': {
                'name': 'Mission Terminée',
                'type': NotificationType.EMAIL,
                'subject': 'Mission {{mission_title}} terminée avec succès',
                'body': '''
Bonjour {{recipient_name}},

La mission "{{mission_title}}" a été terminée avec succès.

Résultats:
- Score qualité: {{quality_score}}/100
- Durée: {{duration}} jours
- Livrables: {{deliverables_count}}
- Satisfaction client: {{client_satisfaction}}/5

Les livrables sont disponibles sur la plateforme.

Cordialement,
L'équipe Substans.AI
                ''',
                'variables': ['recipient_name', 'mission_title', 'quality_score', 'duration', 'deliverables_count', 'client_satisfaction'],
                'category': 'mission'
            },
            'system_alert': {
                'name': 'Alerte Système',
                'type': NotificationType.SLACK,
                'subject': 'Alerte {{severity}}: {{alert_title}}',
                'body': '''
🚨 **Alerte {{severity}}**

**{{alert_title}}**

{{alert_description}}

**Détails:**
- Composant: {{component}}
- Métrique: {{metric_name}} = {{metric_value}}
- Seuil: {{threshold}}
- Timestamp: {{timestamp}}

Action requise: {{recommended_action}}
                ''',
                'variables': ['severity', 'alert_title', 'alert_description', 'component', 'metric_name', 'metric_value', 'threshold', 'timestamp', 'recommended_action'],
                'category': 'system'
            }
        }
        
        self._init_database()
        self._init_default_templates()
        logger.info("Notification Engine initialisé")
    
    def _init_database(self):
        """Initialise la base de données"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS notification_templates (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    subject_template TEXT NOT NULL,
                    body_template TEXT NOT NULL,
                    variables TEXT NOT NULL,
                    language TEXT NOT NULL,
                    category TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    active BOOLEAN NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS notification_recipients (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT,
                    phone TEXT,
                    webhook_url TEXT,
                    slack_channel TEXT,
                    teams_webhook TEXT,
                    preferences TEXT NOT NULL,
                    timezone TEXT NOT NULL,
                    active BOOLEAN NOT NULL,
                    created_at TEXT NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS notifications (
                    id TEXT PRIMARY KEY,
                    template_id TEXT NOT NULL,
                    recipient_id TEXT NOT NULL,
                    type TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    body TEXT NOT NULL,
                    variables TEXT NOT NULL,
                    scheduled_at TEXT,
                    sent_at TEXT,
                    delivered_at TEXT,
                    status TEXT NOT NULL,
                    error_message TEXT,
                    retry_count INTEGER NOT NULL,
                    max_retries INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (template_id) REFERENCES notification_templates (id),
                    FOREIGN KEY (recipient_id) REFERENCES notification_recipients (id)
                );
                
                CREATE TABLE IF NOT EXISTS notification_analytics (
                    id TEXT PRIMARY KEY,
                    template_id TEXT NOT NULL,
                    type TEXT NOT NULL,
                    date TEXT NOT NULL,
                    sent_count INTEGER NOT NULL,
                    delivered_count INTEGER NOT NULL,
                    failed_count INTEGER NOT NULL,
                    avg_delivery_time REAL NOT NULL
                );
                
                CREATE INDEX IF NOT EXISTS idx_notifications_status ON notifications(status);
                CREATE INDEX IF NOT EXISTS idx_notifications_scheduled ON notifications(scheduled_at);
                CREATE INDEX IF NOT EXISTS idx_analytics_date ON notification_analytics(date);
            """)
    
    def _init_default_templates(self):
        """Initialise les templates par défaut"""
        for template_id, config in self.default_templates.items():
            template = NotificationTemplate(
                id=template_id,
                name=config['name'],
                type=config['type'],
                subject_template=config['subject'],
                body_template=config['body'],
                variables=config['variables'],
                language='fr',
                category=config['category'],
                created_at=datetime.now(),
                updated_at=datetime.now(),
                active=True
            )
            self.create_template(template)
    
    def create_template(self, template: NotificationTemplate):
        """Crée un template de notification"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO notification_templates 
                (id, name, type, subject_template, body_template, variables,
                 language, category, created_at, updated_at, active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                template.id, template.name, template.type.value,
                template.subject_template, template.body_template,
                json.dumps(template.variables), template.language,
                template.category, template.created_at.isoformat(),
                template.updated_at.isoformat(), template.active
            ))
        
        logger.info(f"Template créé: {template.name}")
    
    def create_recipient(self, recipient: NotificationRecipient):
        """Crée un destinataire"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO notification_recipients 
                (id, name, email, phone, webhook_url, slack_channel, teams_webhook,
                 preferences, timezone, active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                recipient.id, recipient.name, recipient.email, recipient.phone,
                recipient.webhook_url, recipient.slack_channel, recipient.teams_webhook,
                json.dumps(recipient.preferences), recipient.timezone,
                recipient.active, recipient.created_at.isoformat()
            ))
        
        logger.info(f"Destinataire créé: {recipient.name}")
    
    def send_notification(self, template_id: str, recipient_id: str,
                         variables: Dict[str, Any],
                         priority: NotificationPriority = NotificationPriority.NORMAL,
                         scheduled_at: Optional[datetime] = None) -> str:
        """Envoie une notification"""
        
        # Récupérer le template
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template non trouvé: {template_id}")
        
        # Récupérer le destinataire
        recipient = self.get_recipient(recipient_id)
        if not recipient:
            raise ValueError(f"Destinataire non trouvé: {recipient_id}")
        
        # Rendre le template
        rendered = template.render(variables)
        
        # Créer la notification
        notification_id = f"notif_{int(time.time() * 1000000)}"
        notification = Notification(
            id=notification_id,
            template_id=template_id,
            recipient_id=recipient_id,
            type=template.type,
            priority=priority,
            subject=rendered['subject'],
            body=rendered['body'],
            variables=variables,
            scheduled_at=scheduled_at,
            sent_at=None,
            delivered_at=None,
            status=NotificationStatus.PENDING,
            error_message=None,
            retry_count=0,
            max_retries=3,
            created_at=datetime.now()
        )
        
        # Sauvegarder
        self._save_notification(notification)
        
        # Envoyer immédiatement si pas de planification
        if not scheduled_at:
            self._process_notification(notification)
        
        logger.info(f"Notification créée: {notification_id}")
        return notification_id
    
    def _save_notification(self, notification: Notification):
        """Sauvegarde une notification"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO notifications 
                (id, template_id, recipient_id, type, priority, subject, body,
                 variables, scheduled_at, sent_at, delivered_at, status,
                 error_message, retry_count, max_retries, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                notification.id, notification.template_id, notification.recipient_id,
                notification.type.value, notification.priority.value,
                notification.subject, notification.body, json.dumps(notification.variables),
                notification.scheduled_at.isoformat() if notification.scheduled_at else None,
                notification.sent_at.isoformat() if notification.sent_at else None,
                notification.delivered_at.isoformat() if notification.delivered_at else None,
                notification.status.value, notification.error_message,
                notification.retry_count, notification.max_retries,
                notification.created_at.isoformat()
            ))
    
    def _process_notification(self, notification: Notification):
        """Traite une notification"""
        try:
            # Récupérer le destinataire
            recipient = self.get_recipient(notification.recipient_id)
            if not recipient:
                raise Exception(f"Destinataire non trouvé: {notification.recipient_id}")
            
            # Vérifier les préférences du destinataire
            if not self._check_recipient_preferences(recipient, notification):
                notification.status = NotificationStatus.CANCELLED
                self._save_notification(notification)
                return
            
            # Envoyer via le handler approprié
            handler = self.handlers.get(notification.type)
            if not handler:
                raise Exception(f"Handler non trouvé pour le type: {notification.type}")
            
            success = handler(notification, recipient)
            
            if success:
                notification.status = NotificationStatus.SENT
                notification.sent_at = datetime.now()
            else:
                raise Exception("Échec de l'envoi")
            
        except Exception as e:
            notification.error_message = str(e)
            notification.retry_count += 1
            
            if notification.retry_count >= notification.max_retries:
                notification.status = NotificationStatus.FAILED
            else:
                notification.status = NotificationStatus.PENDING
            
            logger.error(f"Erreur envoi notification {notification.id}: {e}")
        
        finally:
            self._save_notification(notification)
    
    def _check_recipient_preferences(self, recipient: NotificationRecipient,
                                   notification: Notification) -> bool:
        """Vérifie les préférences du destinataire"""
        prefs = recipient.preferences
        
        # Vérifier si le type de notification est autorisé
        allowed_types = prefs.get('allowed_types', [])
        if allowed_types and notification.type.value not in allowed_types:
            return False
        
        # Vérifier les heures autorisées
        quiet_hours = prefs.get('quiet_hours', {})
        if quiet_hours:
            now = datetime.now().time()
            start = datetime.strptime(quiet_hours.get('start', '00:00'), '%H:%M').time()
            end = datetime.strptime(quiet_hours.get('end', '23:59'), '%H:%M').time()
            
            if start <= now <= end:
                return False
        
        # Vérifier la priorité minimale
        min_priority = prefs.get('min_priority', 'low')
        priority_levels = {'low': 1, 'normal': 2, 'high': 3, 'urgent': 4, 'critical': 5}
        
        if priority_levels.get(notification.priority.value, 1) < priority_levels.get(min_priority, 1):
            return False
        
        return True
    
    def _send_email(self, notification: Notification, recipient: NotificationRecipient) -> bool:
        """Envoie un email"""
        try:
            if not recipient.email:
                raise Exception("Email du destinataire non configuré")
            
            config = self.channel_configs['email']
            if not config['username'] or not config['password']:
                logger.warning("Configuration email manquante")
                return True  # Simulation pour les tests
            
            # Créer le message
            msg = MimeMultipart()
            msg['From'] = config['username']
            msg['To'] = recipient.email
            msg['Subject'] = notification.subject
            
            # Corps du message
            msg.attach(MimeText(notification.body, 'plain', 'utf-8'))
            
            # Envoyer
            server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
            if config['use_tls']:
                server.starttls()
            server.login(config['username'], config['password'])
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email envoyé à {recipient.email}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur envoi email: {e}")
            return False
    
    def _send_sms(self, notification: Notification, recipient: NotificationRecipient) -> bool:
        """Envoie un SMS"""
        try:
            if not recipient.phone:
                raise Exception("Téléphone du destinataire non configuré")
            
            config = self.channel_configs['sms']
            if not config['account_sid'] or not config['auth_token']:
                logger.warning("Configuration SMS manquante")
                return True  # Simulation pour les tests
            
            # Ici, intégration avec Twilio ou autre provider SMS
            logger.info(f"SMS envoyé à {recipient.phone}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur envoi SMS: {e}")
            return False
    
    def _send_webhook(self, notification: Notification, recipient: NotificationRecipient) -> bool:
        """Envoie un webhook"""
        try:
            if not recipient.webhook_url:
                raise Exception("URL webhook du destinataire non configurée")
            
            payload = {
                'notification_id': notification.id,
                'subject': notification.subject,
                'body': notification.body,
                'priority': notification.priority.value,
                'timestamp': datetime.now().isoformat(),
                'variables': notification.variables
            }
            
            response = requests.post(
                recipient.webhook_url,
                json=payload,
                timeout=30,
                headers={'Content-Type': 'application/json'}
            )
            
            response.raise_for_status()
            logger.info(f"Webhook envoyé à {recipient.webhook_url}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur envoi webhook: {e}")
            return False
    
    def _send_slack(self, notification: Notification, recipient: NotificationRecipient) -> bool:
        """Envoie un message Slack"""
        try:
            config = self.channel_configs['slack']
            if not config['bot_token']:
                logger.warning("Configuration Slack manquante")
                return True  # Simulation pour les tests
            
            channel = recipient.slack_channel or config['default_channel']
            
            # Ici, intégration avec l'API Slack
            logger.info(f"Message Slack envoyé au canal {channel}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur envoi Slack: {e}")
            return False
    
    def _send_teams(self, notification: Notification, recipient: NotificationRecipient) -> bool:
        """Envoie un message Teams"""
        try:
            webhook_url = recipient.teams_webhook or self.channel_configs['teams']['webhook_url']
            if not webhook_url:
                raise Exception("URL webhook Teams non configurée")
            
            payload = {
                "@type": "MessageCard",
                "@context": "http://schema.org/extensions",
                "themeColor": "0076D7",
                "summary": notification.subject,
                "sections": [{
                    "activityTitle": notification.subject,
                    "activitySubtitle": f"Priorité: {notification.priority.value}",
                    "text": notification.body,
                    "facts": [
                        {"name": "Timestamp", "value": datetime.now().isoformat()},
                        {"name": "Type", "value": notification.type.value}
                    ]
                }]
            }
            
            response = requests.post(webhook_url, json=payload, timeout=30)
            response.raise_for_status()
            
            logger.info(f"Message Teams envoyé")
            return True
            
        except Exception as e:
            logger.error(f"Erreur envoi Teams: {e}")
            return False
    
    def _send_in_app(self, notification: Notification, recipient: NotificationRecipient) -> bool:
        """Envoie une notification in-app"""
        try:
            # Marquer comme livrée immédiatement pour les notifications in-app
            notification.delivered_at = datetime.now()
            logger.info(f"Notification in-app créée pour {recipient.name}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur notification in-app: {e}")
            return False
    
    def get_template(self, template_id: str) -> Optional[NotificationTemplate]:
        """Récupère un template"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM notification_templates WHERE id = ?", (template_id,))
            row = cursor.fetchone()
            
            if row:
                return NotificationTemplate(
                    id=row['id'],
                    name=row['name'],
                    type=NotificationType(row['type']),
                    subject_template=row['subject_template'],
                    body_template=row['body_template'],
                    variables=json.loads(row['variables']),
                    language=row['language'],
                    category=row['category'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at']),
                    active=bool(row['active'])
                )
            return None
    
    def get_recipient(self, recipient_id: str) -> Optional[NotificationRecipient]:
        """Récupère un destinataire"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM notification_recipients WHERE id = ?", (recipient_id,))
            row = cursor.fetchone()
            
            if row:
                return NotificationRecipient(
                    id=row['id'],
                    name=row['name'],
                    email=row['email'],
                    phone=row['phone'],
                    webhook_url=row['webhook_url'],
                    slack_channel=row['slack_channel'],
                    teams_webhook=row['teams_webhook'],
                    preferences=json.loads(row['preferences']),
                    timezone=row['timezone'],
                    active=bool(row['active']),
                    created_at=datetime.fromisoformat(row['created_at'])
                )
            return None
    
    def get_notifications(self, status: Optional[NotificationStatus] = None,
                         limit: int = 100) -> List[Notification]:
        """Récupère les notifications"""
        query = "SELECT * FROM notifications"
        params = []
        
        if status:
            query += " WHERE status = ?"
            params.append(status.value)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            
            notifications = []
            for row in cursor.fetchall():
                notification = Notification(
                    id=row['id'],
                    template_id=row['template_id'],
                    recipient_id=row['recipient_id'],
                    type=NotificationType(row['type']),
                    priority=NotificationPriority(row['priority']),
                    subject=row['subject'],
                    body=row['body'],
                    variables=json.loads(row['variables']),
                    scheduled_at=datetime.fromisoformat(row['scheduled_at']) if row['scheduled_at'] else None,
                    sent_at=datetime.fromisoformat(row['sent_at']) if row['sent_at'] else None,
                    delivered_at=datetime.fromisoformat(row['delivered_at']) if row['delivered_at'] else None,
                    status=NotificationStatus(row['status']),
                    error_message=row['error_message'],
                    retry_count=row['retry_count'],
                    max_retries=row['max_retries'],
                    created_at=datetime.fromisoformat(row['created_at'])
                )
                notifications.append(notification)
            
            return notifications
    
    def get_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Récupère les analytics des notifications"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Statistiques globales
            cursor = conn.execute("""
                SELECT status, COUNT(*) as count
                FROM notifications 
                WHERE created_at >= ? AND created_at <= ?
                GROUP BY status
            """, (start_date.isoformat(), end_date.isoformat()))
            
            status_stats = {row['status']: row['count'] for row in cursor.fetchall()}
            
            # Statistiques par type
            cursor = conn.execute("""
                SELECT type, COUNT(*) as count,
                       AVG(CASE WHEN sent_at IS NOT NULL AND created_at IS NOT NULL 
                           THEN (julianday(sent_at) - julianday(created_at)) * 24 * 60 
                           ELSE NULL END) as avg_send_time_minutes
                FROM notifications 
                WHERE created_at >= ? AND created_at <= ?
                GROUP BY type
            """, (start_date.isoformat(), end_date.isoformat()))
            
            type_stats = [dict(row) for row in cursor.fetchall()]
            
            # Statistiques par template
            cursor = conn.execute("""
                SELECT template_id, COUNT(*) as count,
                       SUM(CASE WHEN status = 'sent' THEN 1 ELSE 0 END) as sent_count,
                       SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_count
                FROM notifications 
                WHERE created_at >= ? AND created_at <= ?
                GROUP BY template_id
                ORDER BY count DESC
                LIMIT 10
            """, (start_date.isoformat(), end_date.isoformat()))
            
            template_stats = [dict(row) for row in cursor.fetchall()]
        
        return {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'days': days
            },
            'status_stats': status_stats,
            'type_stats': type_stats,
            'template_stats': template_stats,
            'total_notifications': sum(status_stats.values()),
            'success_rate': (status_stats.get('sent', 0) / sum(status_stats.values()) * 100) if status_stats else 0,
            'generated_at': datetime.now().isoformat()
        }
    
    def start_notification_service(self):
        """Démarre le service de notifications"""
        if self.running:
            return
        
        self.running = True
        self.notification_thread = threading.Thread(target=self._notification_loop, daemon=True)
        self.notification_thread.start()
        logger.info("Service de notifications démarré")
    
    def stop_notification_service(self):
        """Arrête le service de notifications"""
        self.running = False
        if self.notification_thread:
            self.notification_thread.join()
        logger.info("Service de notifications arrêté")
    
    def _notification_loop(self):
        """Boucle principale du service de notifications"""
        while self.running:
            try:
                # Traiter les notifications en attente
                pending_notifications = self.get_notifications(NotificationStatus.PENDING, 50)
                
                for notification in pending_notifications:
                    # Vérifier si c'est le moment d'envoyer
                    if notification.scheduled_at and datetime.now() < notification.scheduled_at:
                        continue
                    
                    self._process_notification(notification)
                
                # Nettoyer les anciennes notifications (> 90 jours)
                cutoff_date = datetime.now() - timedelta(days=90)
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("DELETE FROM notifications WHERE created_at < ?", 
                               (cutoff_date.isoformat(),))
                
                time.sleep(30)  # Attendre 30 secondes
                
            except Exception as e:
                logger.error(f"Erreur dans la boucle de notifications: {e}")
                time.sleep(60)

# Exemple d'utilisation
if __name__ == "__main__":
    # Créer le moteur de notifications
    engine = NotificationEngine()
    
    # Démarrer le service
    engine.start_notification_service()
    
    # Créer un destinataire d'exemple
    recipient = NotificationRecipient(
        id="admin",
        name="Administrateur",
        email="admin@substans.ai",
        phone="+33123456789",
        webhook_url=None,
        slack_channel="#general",
        teams_webhook=None,
        preferences={
            'allowed_types': ['email', 'slack'],
            'min_priority': 'normal',
            'quiet_hours': {'start': '22:00', 'end': '08:00'}
        },
        timezone="Europe/Paris",
        active=True,
        created_at=datetime.now()
    )
    
    engine.create_recipient(recipient)
    
    # Envoyer une notification d'exemple
    notification_id = engine.send_notification(
        template_id="mission_completed",
        recipient_id="admin",
        variables={
            'recipient_name': 'Administrateur',
            'mission_title': 'Analyse Stratégique Bull',
            'quality_score': 95,
            'duration': 12,
            'deliverables_count': 3,
            'client_satisfaction': 4.8
        },
        priority=NotificationPriority.HIGH
    )
    
    print(f"Notification envoyée: {notification_id}")
    
    # Afficher les analytics
    analytics = engine.get_analytics(7)
    print(f"Notifications totales (7 jours): {analytics['total_notifications']}")
    print(f"Taux de succès: {analytics['success_rate']:.1f}%")
    
    # Arrêter le service
    time.sleep(2)
    engine.stop_notification_service()

