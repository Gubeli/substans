#!/usr/bin/env python3
"""
Audit System - Substans.AI Enterprise
Système d'audit complet pour la traçabilité et la conformité
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import secrets
import threading
import time
from collections import defaultdict
import gzip
import os

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuditLevel(Enum):
    """Niveaux d'audit"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AuditCategory(Enum):
    """Catégories d'audit"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    SYSTEM_CHANGE = "system_change"
    SECURITY_EVENT = "security_event"
    BUSINESS_PROCESS = "business_process"
    COMPLIANCE = "compliance"
    PERFORMANCE = "performance"
    ERROR = "error"

class ComplianceStandard(Enum):
    """Standards de conformité"""
    GDPR = "gdpr"
    SOX = "sox"
    HIPAA = "hipaa"
    ISO27001 = "iso27001"
    PCI_DSS = "pci_dss"
    CUSTOM = "custom"

@dataclass
class AuditEvent:
    """Événement d'audit"""
    id: str
    timestamp: datetime
    level: AuditLevel
    category: AuditCategory
    event_type: str
    user_id: Optional[str]
    session_id: Optional[str]
    ip_address: str
    user_agent: str
    resource_type: Optional[str]
    resource_id: Optional[str]
    action: str
    description: str
    details: Dict[str, Any]
    before_state: Optional[Dict[str, Any]]
    after_state: Optional[Dict[str, Any]]
    success: bool
    error_message: Optional[str]
    compliance_tags: List[str]
    retention_policy: str
    checksum: str
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['level'] = self.level.value
        data['category'] = self.category.value
        return data

@dataclass
class ComplianceRule:
    """Règle de conformité"""
    id: str
    name: str
    description: str
    standard: ComplianceStandard
    category: AuditCategory
    conditions: Dict[str, Any]
    actions: List[str]
    severity: AuditLevel
    active: bool
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['standard'] = self.standard.value
        data['category'] = self.category.value
        data['severity'] = self.severity.value
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data

@dataclass
class AuditReport:
    """Rapport d'audit"""
    id: str
    name: str
    description: str
    report_type: str
    parameters: Dict[str, Any]
    generated_at: datetime
    generated_by: str
    period_start: datetime
    period_end: datetime
    events_count: int
    compliance_status: Dict[str, Any]
    findings: List[Dict[str, Any]]
    recommendations: List[str]
    file_path: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['generated_at'] = self.generated_at.isoformat()
        data['period_start'] = self.period_start.isoformat()
        data['period_end'] = self.period_end.isoformat()
        return data

class AuditSystem:
    """Système d'audit enterprise"""
    
    def __init__(self, db_path: str = "audit.db", archive_path: str = "audit_archive"):
        self.db_path = db_path
        self.archive_path = archive_path
        
        # Configuration d'audit
        self.config = {
            'retention_policies': {
                'security': 2555,  # 7 ans
                'financial': 2555,  # 7 ans
                'operational': 1095,  # 3 ans
                'system': 365,  # 1 an
                'debug': 30  # 30 jours
            },
            'archive_after_days': 90,
            'compression_enabled': True,
            'integrity_checks': True,
            'real_time_monitoring': True,
            'compliance_monitoring': True
        }
        
        # Statistiques d'audit
        self.audit_stats = defaultdict(int)
        self.performance_metrics = {
            'events_per_second': 0,
            'average_processing_time': 0,
            'storage_size_mb': 0,
            'archive_size_mb': 0
        }
        
        # Règles de conformité par défaut
        self.default_compliance_rules = {
            'gdpr_data_access': {
                'name': 'GDPR - Accès aux données personnelles',
                'description': 'Traçabilité des accès aux données personnelles',
                'standard': ComplianceStandard.GDPR,
                'category': AuditCategory.DATA_ACCESS,
                'conditions': {
                    'resource_type': 'user_data',
                    'action': ['read', 'export']
                },
                'actions': ['log_detailed', 'notify_dpo'],
                'severity': AuditLevel.INFO
            },
            'sox_financial_change': {
                'name': 'SOX - Modifications financières',
                'description': 'Traçabilité des modifications de données financières',
                'standard': ComplianceStandard.SOX,
                'category': AuditCategory.DATA_MODIFICATION,
                'conditions': {
                    'resource_type': 'financial_data',
                    'action': ['create', 'update', 'delete']
                },
                'actions': ['log_detailed', 'require_approval'],
                'severity': AuditLevel.WARNING
            },
            'security_admin_action': {
                'name': 'Actions administrateur sécurité',
                'description': 'Traçabilité des actions des administrateurs système',
                'standard': ComplianceStandard.ISO27001,
                'category': AuditCategory.SYSTEM_CHANGE,
                'conditions': {
                    'user_role': 'admin',
                    'category': 'system_change'
                },
                'actions': ['log_detailed', 'alert_security_team'],
                'severity': AuditLevel.WARNING
            }
        }
        
        # Templates de rapports
        self.report_templates = {
            'security_summary': {
                'name': 'Résumé Sécurité',
                'description': 'Rapport de synthèse des événements de sécurité',
                'categories': [AuditCategory.AUTHENTICATION, AuditCategory.AUTHORIZATION, AuditCategory.SECURITY_EVENT],
                'metrics': ['failed_logins', 'privilege_escalations', 'security_violations']
            },
            'compliance_gdpr': {
                'name': 'Conformité GDPR',
                'description': 'Rapport de conformité RGPD',
                'categories': [AuditCategory.DATA_ACCESS, AuditCategory.DATA_MODIFICATION],
                'metrics': ['data_access_requests', 'data_modifications', 'consent_changes']
            },
            'system_activity': {
                'name': 'Activité Système',
                'description': 'Rapport d\'activité système général',
                'categories': [AuditCategory.SYSTEM_CHANGE, AuditCategory.PERFORMANCE],
                'metrics': ['system_changes', 'performance_issues', 'error_rates']
            }
        }
        
        # Créer le répertoire d'archive
        os.makedirs(self.archive_path, exist_ok=True)
        
        self._init_database()
        self._init_compliance_rules()
        self._start_audit_services()
        
        logger.info("Audit System initialisé")
    
    def _init_database(self):
        """Initialise la base de données d'audit"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS audit_events (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    level TEXT NOT NULL,
                    category TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    user_id TEXT,
                    session_id TEXT,
                    ip_address TEXT NOT NULL,
                    user_agent TEXT NOT NULL,
                    resource_type TEXT,
                    resource_id TEXT,
                    action TEXT NOT NULL,
                    description TEXT NOT NULL,
                    details TEXT NOT NULL,
                    before_state TEXT,
                    after_state TEXT,
                    success BOOLEAN NOT NULL,
                    error_message TEXT,
                    compliance_tags TEXT NOT NULL,
                    retention_policy TEXT NOT NULL,
                    checksum TEXT NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS compliance_rules (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    standard TEXT NOT NULL,
                    category TEXT NOT NULL,
                    conditions TEXT NOT NULL,
                    actions TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    active BOOLEAN DEFAULT TRUE,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS audit_reports (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    report_type TEXT NOT NULL,
                    parameters TEXT NOT NULL,
                    generated_at TEXT NOT NULL,
                    generated_by TEXT NOT NULL,
                    period_start TEXT NOT NULL,
                    period_end TEXT NOT NULL,
                    events_count INTEGER NOT NULL,
                    compliance_status TEXT NOT NULL,
                    findings TEXT NOT NULL,
                    recommendations TEXT NOT NULL,
                    file_path TEXT
                );
                
                CREATE TABLE IF NOT EXISTS audit_archive (
                    id TEXT PRIMARY KEY,
                    original_event_id TEXT NOT NULL,
                    archived_at TEXT NOT NULL,
                    archive_file TEXT NOT NULL,
                    checksum TEXT NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS compliance_violations (
                    id TEXT PRIMARY KEY,
                    event_id TEXT NOT NULL,
                    rule_id TEXT NOT NULL,
                    violation_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    description TEXT NOT NULL,
                    detected_at TEXT NOT NULL,
                    resolved BOOLEAN DEFAULT FALSE,
                    resolution_notes TEXT,
                    resolved_at TEXT,
                    FOREIGN KEY (event_id) REFERENCES audit_events (id),
                    FOREIGN KEY (rule_id) REFERENCES compliance_rules (id)
                );
                
                CREATE TABLE IF NOT EXISTS audit_metrics (
                    id TEXT PRIMARY KEY,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    metric_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    context TEXT NOT NULL
                );
                
                CREATE INDEX IF NOT EXISTS idx_audit_events_timestamp ON audit_events(timestamp);
                CREATE INDEX IF NOT EXISTS idx_audit_events_category ON audit_events(category);
                CREATE INDEX IF NOT EXISTS idx_audit_events_user_id ON audit_events(user_id);
                CREATE INDEX IF NOT EXISTS idx_audit_events_level ON audit_events(level);
                CREATE INDEX IF NOT EXISTS idx_compliance_violations_detected_at ON compliance_violations(detected_at);
                CREATE INDEX IF NOT EXISTS idx_audit_metrics_timestamp ON audit_metrics(timestamp);
            """)
    
    def _init_compliance_rules(self):
        """Initialise les règles de conformité par défaut"""
        for rule_id, config in self.default_compliance_rules.items():
            # Vérifier si la règle existe déjà
            if self.get_compliance_rule(rule_id):
                continue
            
            rule = ComplianceRule(
                id=rule_id,
                name=config['name'],
                description=config['description'],
                standard=config['standard'],
                category=config['category'],
                conditions=config['conditions'],
                actions=config['actions'],
                severity=config['severity'],
                active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.create_compliance_rule(rule)
    
    def log_event(self, level: AuditLevel, category: AuditCategory, event_type: str,
                  action: str, description: str, user_id: Optional[str] = None,
                  session_id: Optional[str] = None, ip_address: str = "",
                  user_agent: str = "", resource_type: Optional[str] = None,
                  resource_id: Optional[str] = None, details: Dict[str, Any] = None,
                  before_state: Optional[Dict[str, Any]] = None,
                  after_state: Optional[Dict[str, Any]] = None,
                  success: bool = True, error_message: Optional[str] = None,
                  compliance_tags: List[str] = None) -> str:
        """Enregistre un événement d'audit"""
        
        event_id = f"audit_{int(time.time() * 1000000)}"
        timestamp = datetime.now()
        details = details or {}
        compliance_tags = compliance_tags or []
        
        # Déterminer la politique de rétention
        retention_policy = self._determine_retention_policy(category, compliance_tags)
        
        # Calculer le checksum pour l'intégrité
        checksum = self._calculate_checksum({
            'id': event_id,
            'timestamp': timestamp.isoformat(),
            'level': level.value,
            'category': category.value,
            'event_type': event_type,
            'user_id': user_id,
            'action': action,
            'description': description,
            'details': details,
            'success': success
        })
        
        # Créer l'événement d'audit
        event = AuditEvent(
            id=event_id,
            timestamp=timestamp,
            level=level,
            category=category,
            event_type=event_type,
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            description=description,
            details=details,
            before_state=before_state,
            after_state=after_state,
            success=success,
            error_message=error_message,
            compliance_tags=compliance_tags,
            retention_policy=retention_policy,
            checksum=checksum
        )
        
        # Sauvegarder en base
        self._save_event(event)
        
        # Vérifier les règles de conformité
        self._check_compliance_rules(event)
        
        # Mettre à jour les statistiques
        self.audit_stats[f"{level.value}_{category.value}"] += 1
        self.audit_stats['total_events'] += 1
        
        logger.debug(f"Événement d'audit enregistré: {event_id}")
        return event_id
    
    def _save_event(self, event: AuditEvent):
        """Sauvegarde un événement d'audit"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO audit_events 
                (id, timestamp, level, category, event_type, user_id, session_id,
                 ip_address, user_agent, resource_type, resource_id, action,
                 description, details, before_state, after_state, success,
                 error_message, compliance_tags, retention_policy, checksum)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.id, event.timestamp.isoformat(), event.level.value,
                event.category.value, event.event_type, event.user_id,
                event.session_id, event.ip_address, event.user_agent,
                event.resource_type, event.resource_id, event.action,
                event.description, json.dumps(event.details),
                json.dumps(event.before_state) if event.before_state else None,
                json.dumps(event.after_state) if event.after_state else None,
                event.success, event.error_message,
                json.dumps(event.compliance_tags), event.retention_policy,
                event.checksum
            ))
    
    def _determine_retention_policy(self, category: AuditCategory, 
                                  compliance_tags: List[str]) -> str:
        """Détermine la politique de rétention"""
        # Vérifier les tags de conformité
        if 'financial' in compliance_tags or 'sox' in compliance_tags:
            return 'financial'
        elif 'security' in compliance_tags or 'gdpr' in compliance_tags:
            return 'security'
        elif category in [AuditCategory.AUTHENTICATION, AuditCategory.AUTHORIZATION, 
                         AuditCategory.SECURITY_EVENT]:
            return 'security'
        elif category in [AuditCategory.SYSTEM_CHANGE, AuditCategory.PERFORMANCE]:
            return 'system'
        else:
            return 'operational'
    
    def _calculate_checksum(self, data: Dict[str, Any]) -> str:
        """Calcule le checksum d'un événement pour l'intégrité"""
        data_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def _check_compliance_rules(self, event: AuditEvent):
        """Vérifie les règles de conformité"""
        rules = self.get_active_compliance_rules()
        
        for rule in rules:
            if self._rule_matches_event(rule, event):
                # Enregistrer la violation si nécessaire
                if rule.severity in [AuditLevel.WARNING, AuditLevel.ERROR, AuditLevel.CRITICAL]:
                    self._record_compliance_violation(event, rule)
                
                # Exécuter les actions
                self._execute_compliance_actions(event, rule)
    
    def _rule_matches_event(self, rule: ComplianceRule, event: AuditEvent) -> bool:
        """Vérifie si une règle correspond à un événement"""
        conditions = rule.conditions
        
        # Vérifier la catégorie
        if 'category' in conditions:
            if event.category.value != conditions['category']:
                return False
        
        # Vérifier le type de ressource
        if 'resource_type' in conditions:
            if event.resource_type != conditions['resource_type']:
                return False
        
        # Vérifier l'action
        if 'action' in conditions:
            actions = conditions['action']
            if isinstance(actions, list):
                if event.action not in actions:
                    return False
            else:
                if event.action != actions:
                    return False
        
        # Vérifier le rôle utilisateur (si disponible dans les détails)
        if 'user_role' in conditions:
            user_role = event.details.get('user_role')
            if user_role != conditions['user_role']:
                return False
        
        return True
    
    def _record_compliance_violation(self, event: AuditEvent, rule: ComplianceRule):
        """Enregistre une violation de conformité"""
        violation_id = f"viol_{int(time.time() * 1000000)}"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO compliance_violations 
                (id, event_id, rule_id, violation_type, severity, description, detected_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                violation_id, event.id, rule.id, rule.standard.value,
                rule.severity.value, f"Violation de la règle: {rule.name}",
                datetime.now().isoformat()
            ))
        
        logger.warning(f"Violation de conformité détectée: {rule.name} - Événement: {event.id}")
    
    def _execute_compliance_actions(self, event: AuditEvent, rule: ComplianceRule):
        """Exécute les actions de conformité"""
        for action in rule.actions:
            try:
                if action == 'log_detailed':
                    # Log détaillé déjà fait
                    pass
                elif action == 'notify_dpo':
                    # Notifier le DPO (Data Protection Officer)
                    self._notify_dpo(event, rule)
                elif action == 'alert_security_team':
                    # Alerter l'équipe sécurité
                    self._alert_security_team(event, rule)
                elif action == 'require_approval':
                    # Marquer comme nécessitant une approbation
                    self._mark_for_approval(event, rule)
                
            except Exception as e:
                logger.error(f"Erreur exécution action {action}: {e}")
    
    def _notify_dpo(self, event: AuditEvent, rule: ComplianceRule):
        """Notifie le DPO"""
        # Implémentation de notification (email, webhook, etc.)
        logger.info(f"Notification DPO: {rule.name} - Événement: {event.id}")
    
    def _alert_security_team(self, event: AuditEvent, rule: ComplianceRule):
        """Alerte l'équipe sécurité"""
        # Implémentation d'alerte sécurité
        logger.warning(f"Alerte sécurité: {rule.name} - Événement: {event.id}")
    
    def _mark_for_approval(self, event: AuditEvent, rule: ComplianceRule):
        """Marque pour approbation"""
        # Implémentation du workflow d'approbation
        logger.info(f"Marqué pour approbation: {rule.name} - Événement: {event.id}")
    
    def create_compliance_rule(self, rule: ComplianceRule) -> bool:
        """Crée une règle de conformité"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO compliance_rules 
                    (id, name, description, standard, category, conditions, 
                     actions, severity, active, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    rule.id, rule.name, rule.description, rule.standard.value,
                    rule.category.value, json.dumps(rule.conditions),
                    json.dumps(rule.actions), rule.severity.value, rule.active,
                    rule.created_at.isoformat(), rule.updated_at.isoformat()
                ))
            
            logger.info(f"Règle de conformité créée: {rule.name}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur création règle conformité: {e}")
            return False
    
    def get_compliance_rule(self, rule_id: str) -> Optional[ComplianceRule]:
        """Récupère une règle de conformité"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM compliance_rules WHERE id = ?", (rule_id,))
            row = cursor.fetchone()
            
            if row:
                return ComplianceRule(
                    id=row['id'],
                    name=row['name'],
                    description=row['description'],
                    standard=ComplianceStandard(row['standard']),
                    category=AuditCategory(row['category']),
                    conditions=json.loads(row['conditions']),
                    actions=json.loads(row['actions']),
                    severity=AuditLevel(row['severity']),
                    active=bool(row['active']),
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at'])
                )
        
        return None
    
    def get_active_compliance_rules(self) -> List[ComplianceRule]:
        """Récupère toutes les règles de conformité actives"""
        rules = []
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM compliance_rules WHERE active = TRUE")
            
            for row in cursor.fetchall():
                rule = ComplianceRule(
                    id=row['id'],
                    name=row['name'],
                    description=row['description'],
                    standard=ComplianceStandard(row['standard']),
                    category=AuditCategory(row['category']),
                    conditions=json.loads(row['conditions']),
                    actions=json.loads(row['actions']),
                    severity=AuditLevel(row['severity']),
                    active=bool(row['active']),
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at'])
                )
                rules.append(rule)
        
        return rules
    
    def get_audit_events(self, start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None,
                        category: Optional[AuditCategory] = None,
                        level: Optional[AuditLevel] = None,
                        user_id: Optional[str] = None,
                        limit: int = 1000) -> List[AuditEvent]:
        """Récupère les événements d'audit"""
        query = "SELECT * FROM audit_events WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date.isoformat())
        
        if category:
            query += " AND category = ?"
            params.append(category.value)
        
        if level:
            query += " AND level = ?"
            params.append(level.value)
        
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        events = []
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            
            for row in cursor.fetchall():
                event = AuditEvent(
                    id=row['id'],
                    timestamp=datetime.fromisoformat(row['timestamp']),
                    level=AuditLevel(row['level']),
                    category=AuditCategory(row['category']),
                    event_type=row['event_type'],
                    user_id=row['user_id'],
                    session_id=row['session_id'],
                    ip_address=row['ip_address'],
                    user_agent=row['user_agent'],
                    resource_type=row['resource_type'],
                    resource_id=row['resource_id'],
                    action=row['action'],
                    description=row['description'],
                    details=json.loads(row['details']),
                    before_state=json.loads(row['before_state']) if row['before_state'] else None,
                    after_state=json.loads(row['after_state']) if row['after_state'] else None,
                    success=bool(row['success']),
                    error_message=row['error_message'],
                    compliance_tags=json.loads(row['compliance_tags']),
                    retention_policy=row['retention_policy'],
                    checksum=row['checksum']
                )
                events.append(event)
        
        return events
    
    def generate_report(self, report_type: str, start_date: datetime,
                       end_date: datetime, generated_by: str,
                       parameters: Dict[str, Any] = None) -> AuditReport:
        """Génère un rapport d'audit"""
        parameters = parameters or {}
        report_id = f"report_{int(time.time() * 1000000)}"
        
        # Récupérer les événements pour la période
        events = self.get_audit_events(start_date, end_date, limit=10000)
        
        # Analyser selon le type de rapport
        if report_type in self.report_templates:
            template = self.report_templates[report_type]
            findings = self._analyze_events_by_template(events, template)
        else:
            findings = self._analyze_events_generic(events)
        
        # Évaluer la conformité
        compliance_status = self._evaluate_compliance_status(events)
        
        # Générer des recommandations
        recommendations = self._generate_recommendations(events, findings)
        
        # Créer le rapport
        report = AuditReport(
            id=report_id,
            name=f"Rapport {report_type} - {start_date.strftime('%Y-%m-%d')} à {end_date.strftime('%Y-%m-%d')}",
            description=f"Rapport d'audit {report_type} généré automatiquement",
            report_type=report_type,
            parameters=parameters,
            generated_at=datetime.now(),
            generated_by=generated_by,
            period_start=start_date,
            period_end=end_date,
            events_count=len(events),
            compliance_status=compliance_status,
            findings=findings,
            recommendations=recommendations,
            file_path=None
        )
        
        # Sauvegarder le rapport
        self._save_report(report)
        
        logger.info(f"Rapport d'audit généré: {report_id}")
        return report
    
    def _analyze_events_by_template(self, events: List[AuditEvent], 
                                  template: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyse les événements selon un template"""
        findings = []
        
        # Filtrer par catégories
        relevant_events = [
            event for event in events 
            if event.category in template['categories']
        ]
        
        # Analyser les métriques
        for metric in template['metrics']:
            if metric == 'failed_logins':
                failed_logins = [
                    event for event in relevant_events
                    if event.category == AuditCategory.AUTHENTICATION and not event.success
                ]
                findings.append({
                    'type': 'metric',
                    'name': 'Échecs de connexion',
                    'value': len(failed_logins),
                    'severity': 'high' if len(failed_logins) > 10 else 'medium',
                    'details': f"{len(failed_logins)} tentatives de connexion échouées"
                })
            
            elif metric == 'security_violations':
                violations = [
                    event for event in relevant_events
                    if event.level in [AuditLevel.WARNING, AuditLevel.ERROR, AuditLevel.CRITICAL]
                ]
                findings.append({
                    'type': 'metric',
                    'name': 'Violations de sécurité',
                    'value': len(violations),
                    'severity': 'critical' if len(violations) > 5 else 'medium',
                    'details': f"{len(violations)} violations de sécurité détectées"
                })
        
        return findings
    
    def _analyze_events_generic(self, events: List[AuditEvent]) -> List[Dict[str, Any]]:
        """Analyse générique des événements"""
        findings = []
        
        # Statistiques par niveau
        level_stats = defaultdict(int)
        for event in events:
            level_stats[event.level.value] += 1
        
        findings.append({
            'type': 'statistics',
            'name': 'Répartition par niveau',
            'value': dict(level_stats),
            'severity': 'info',
            'details': f"Total: {len(events)} événements"
        })
        
        # Statistiques par catégorie
        category_stats = defaultdict(int)
        for event in events:
            category_stats[event.category.value] += 1
        
        findings.append({
            'type': 'statistics',
            'name': 'Répartition par catégorie',
            'value': dict(category_stats),
            'severity': 'info',
            'details': f"Répartition sur {len(category_stats)} catégories"
        })
        
        return findings
    
    def _evaluate_compliance_status(self, events: List[AuditEvent]) -> Dict[str, Any]:
        """Évalue le statut de conformité"""
        # Récupérer les violations de conformité
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT violation_type, COUNT(*) as count
                FROM compliance_violations 
                WHERE detected_at >= ? AND detected_at <= ?
                GROUP BY violation_type
            """, (
                events[0].timestamp.isoformat() if events else datetime.now().isoformat(),
                events[-1].timestamp.isoformat() if events else datetime.now().isoformat()
            ))
            
            violations = {row['violation_type']: row['count'] for row in cursor.fetchall()}
        
        # Calculer le score de conformité
        total_violations = sum(violations.values())
        compliance_score = max(0, 100 - (total_violations * 5))  # -5 points par violation
        
        return {
            'score': compliance_score,
            'violations': violations,
            'status': 'compliant' if compliance_score >= 90 else 'non_compliant',
            'total_violations': total_violations
        }
    
    def _generate_recommendations(self, events: List[AuditEvent], 
                                findings: List[Dict[str, Any]]) -> List[str]:
        """Génère des recommandations"""
        recommendations = []
        
        # Analyser les patterns d'erreur
        error_events = [event for event in events if not event.success]
        if len(error_events) > len(events) * 0.1:  # Plus de 10% d'erreurs
            recommendations.append(
                "Taux d'erreur élevé détecté. Investiguer les causes racines des échecs."
            )
        
        # Analyser les accès suspects
        auth_events = [event for event in events if event.category == AuditCategory.AUTHENTICATION]
        failed_auth = [event for event in auth_events if not event.success]
        if len(failed_auth) > 20:
            recommendations.append(
                "Nombre élevé d'échecs d'authentification. Renforcer les mesures de sécurité."
            )
        
        # Analyser les modifications système
        system_changes = [event for event in events if event.category == AuditCategory.SYSTEM_CHANGE]
        if len(system_changes) > 50:
            recommendations.append(
                "Activité de modification système élevée. Vérifier les processus de gestion des changements."
            )
        
        return recommendations
    
    def _save_report(self, report: AuditReport):
        """Sauvegarde un rapport d'audit"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO audit_reports 
                (id, name, description, report_type, parameters, generated_at,
                 generated_by, period_start, period_end, events_count,
                 compliance_status, findings, recommendations, file_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                report.id, report.name, report.description, report.report_type,
                json.dumps(report.parameters), report.generated_at.isoformat(),
                report.generated_by, report.period_start.isoformat(),
                report.period_end.isoformat(), report.events_count,
                json.dumps(report.compliance_status), json.dumps(report.findings),
                json.dumps(report.recommendations), report.file_path
            ))
    
    def get_audit_dashboard(self) -> Dict[str, Any]:
        """Récupère le tableau de bord d'audit"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Événements des dernières 24h
            cursor = conn.execute("""
                SELECT level, COUNT(*) as count
                FROM audit_events 
                WHERE timestamp >= datetime('now', '-24 hours')
                GROUP BY level
            """)
            
            events_24h = {row['level']: row['count'] for row in cursor.fetchall()}
            
            # Violations de conformité non résolues
            cursor = conn.execute("""
                SELECT COUNT(*) as count FROM compliance_violations 
                WHERE resolved = FALSE
            """)
            
            unresolved_violations = cursor.fetchone()['count']
            
            # Top catégories d'événements
            cursor = conn.execute("""
                SELECT category, COUNT(*) as count
                FROM audit_events 
                WHERE timestamp >= datetime('now', '-7 days')
                GROUP BY category
                ORDER BY count DESC
                LIMIT 10
            """)
            
            top_categories = [dict(row) for row in cursor.fetchall()]
            
            # Métriques de performance
            cursor = conn.execute("""
                SELECT COUNT(*) as total_events,
                       AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) as success_rate
                FROM audit_events 
                WHERE timestamp >= datetime('now', '-24 hours')
            """)
            
            perf_metrics = cursor.fetchone()
        
        return {
            'events_24h': events_24h,
            'total_events_24h': sum(events_24h.values()),
            'unresolved_violations': unresolved_violations,
            'success_rate_24h': round(perf_metrics['success_rate'] * 100, 2) if perf_metrics['success_rate'] else 0,
            'top_categories': top_categories,
            'audit_stats': dict(self.audit_stats),
            'performance_metrics': self.performance_metrics,
            'generated_at': datetime.now().isoformat()
        }
    
    def _start_audit_services(self):
        """Démarre les services d'audit"""
        def audit_maintenance():
            while True:
                try:
                    # Archiver les anciens événements
                    self._archive_old_events()
                    
                    # Nettoyer les événements expirés
                    self._cleanup_expired_events()
                    
                    # Mettre à jour les métriques de performance
                    self._update_performance_metrics()
                    
                    time.sleep(3600)  # 1 heure
                    
                except Exception as e:
                    logger.error(f"Erreur maintenance audit: {e}")
                    time.sleep(300)
        
        maintenance_thread = threading.Thread(target=audit_maintenance, daemon=True)
        maintenance_thread.start()
        logger.info("Services d'audit démarrés")
    
    def _archive_old_events(self):
        """Archive les anciens événements"""
        archive_date = datetime.now() - timedelta(days=self.config['archive_after_days'])
        
        with sqlite3.connect(self.db_path) as conn:
            # Récupérer les événements à archiver
            cursor = conn.execute("""
                SELECT * FROM audit_events 
                WHERE timestamp < ? 
                LIMIT 1000
            """, (archive_date.isoformat(),))
            
            events_to_archive = cursor.fetchall()
            
            if events_to_archive:
                # Créer le fichier d'archive
                archive_file = f"audit_archive_{int(time.time())}.json.gz"
                archive_path = os.path.join(self.archive_path, archive_file)
                
                # Compresser et sauvegarder
                with gzip.open(archive_path, 'wt') as f:
                    json.dump([dict(row) for row in events_to_archive], f)
                
                # Enregistrer dans la table d'archive
                for event in events_to_archive:
                    conn.execute("""
                        INSERT INTO audit_archive 
                        (id, original_event_id, archived_at, archive_file, checksum)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        f"arch_{int(time.time() * 1000000)}", event['id'],
                        datetime.now().isoformat(), archive_file, event['checksum']
                    ))
                
                # Supprimer les événements archivés
                event_ids = [event['id'] for event in events_to_archive]
                placeholders = ','.join(['?' for _ in event_ids])
                conn.execute(f"DELETE FROM audit_events WHERE id IN ({placeholders})", event_ids)
                
                logger.info(f"Archivé {len(events_to_archive)} événements dans {archive_file}")
    
    def _cleanup_expired_events(self):
        """Nettoie les événements expirés"""
        for policy, days in self.config['retention_policies'].items():
            cutoff_date = datetime.now() - timedelta(days=days)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    DELETE FROM audit_events 
                    WHERE retention_policy = ? AND timestamp < ?
                """, (policy, cutoff_date.isoformat()))
                
                if cursor.rowcount > 0:
                    logger.info(f"Supprimé {cursor.rowcount} événements expirés (politique: {policy})")
    
    def _update_performance_metrics(self):
        """Met à jour les métriques de performance"""
        # Calculer la taille de la base
        db_size = os.path.getsize(self.db_path) / (1024 * 1024)  # MB
        self.performance_metrics['storage_size_mb'] = round(db_size, 2)
        
        # Calculer la taille des archives
        archive_size = 0
        if os.path.exists(self.archive_path):
            for file in os.listdir(self.archive_path):
                file_path = os.path.join(self.archive_path, file)
                if os.path.isfile(file_path):
                    archive_size += os.path.getsize(file_path)
        
        self.performance_metrics['archive_size_mb'] = round(archive_size / (1024 * 1024), 2)

# Exemple d'utilisation
if __name__ == "__main__":
    # Créer le système d'audit
    audit_system = AuditSystem()
    
    # Enregistrer quelques événements de test
    audit_system.log_event(
        level=AuditLevel.INFO,
        category=AuditCategory.AUTHENTICATION,
        event_type="user_login",
        action="login",
        description="Connexion utilisateur réussie",
        user_id="admin_001",
        ip_address="127.0.0.1",
        user_agent="Test Client",
        success=True,
        compliance_tags=["security"]
    )
    
    audit_system.log_event(
        level=AuditLevel.WARNING,
        category=AuditCategory.DATA_MODIFICATION,
        event_type="data_update",
        action="update",
        description="Modification de données financières",
        user_id="admin_001",
        resource_type="financial_data",
        resource_id="budget_2024",
        details={"field": "amount", "old_value": 1000, "new_value": 1500},
        success=True,
        compliance_tags=["financial", "sox"]
    )
    
    # Générer un rapport
    report = audit_system.generate_report(
        report_type="security_summary",
        start_date=datetime.now() - timedelta(days=7),
        end_date=datetime.now(),
        generated_by="admin_001"
    )
    
    print(f"Rapport généré: {report.name}")
    print(f"Événements analysés: {report.events_count}")
    print(f"Score de conformité: {report.compliance_status['score']}%")
    
    # Afficher le tableau de bord
    dashboard = audit_system.get_audit_dashboard()
    print(f"\nTableau de bord audit:")
    print(f"- Événements 24h: {dashboard['total_events_24h']}")
    print(f"- Violations non résolues: {dashboard['unresolved_violations']}")
    print(f"- Taux de succès 24h: {dashboard['success_rate_24h']}%")
    print(f"- Taille base de données: {dashboard['performance_metrics']['storage_size_mb']} MB")

