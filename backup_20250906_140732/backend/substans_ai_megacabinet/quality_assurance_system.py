"""
Quality Assurance System - Système d'Assurance Qualité Enterprise
Garantit la qualité des livrables et processus de conseil
"""

import json
import logging
import os
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor
import re
import hashlib
import statistics
from collections import defaultdict

# Configuration du logging
logging.basicConfig(level=logging.INFO)

class QualityLevel(Enum):
    """Niveaux de qualité"""
    EXCELLENT = "excellent"  # 90-100%
    GOOD = "good"           # 75-89%
    ACCEPTABLE = "acceptable"  # 60-74%
    POOR = "poor"           # 40-59%
    UNACCEPTABLE = "unacceptable"  # 0-39%

class ReviewStatus(Enum):
    """Statuts de revue"""
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"
    ESCALATED = "escalated"

class QualityDimension(Enum):
    """Dimensions de qualité"""
    CONTENT_ACCURACY = "content_accuracy"
    METHODOLOGY_COMPLIANCE = "methodology_compliance"
    PRESENTATION_QUALITY = "presentation_quality"
    COMPLETENESS = "completeness"
    RELEVANCE = "relevance"
    CLARITY = "clarity"
    INNOVATION = "innovation"
    CLIENT_ALIGNMENT = "client_alignment"
    TECHNICAL_RIGOR = "technical_rigor"
    ACTIONABILITY = "actionability"

class QualityCheckType(Enum):
    """Types de contrôles qualité"""
    AUTOMATED = "automated"
    PEER_REVIEW = "peer_review"
    EXPERT_REVIEW = "expert_review"
    CLIENT_REVIEW = "client_review"
    FINAL_VALIDATION = "final_validation"

@dataclass
class QualityMetric:
    """Métrique de qualité"""
    metric_id: str
    name: str
    description: str
    dimension: QualityDimension
    weight: float  # Poids dans le calcul global (0-1)
    min_threshold: float  # Seuil minimum acceptable
    target_threshold: float  # Seuil cible
    calculation_method: str  # Méthode de calcul
    automated: bool  # Calculable automatiquement
    created_at: datetime

@dataclass
class QualityCheck:
    """Contrôle qualité"""
    check_id: str
    deliverable_id: str
    mission_id: str
    check_type: QualityCheckType
    reviewer_id: str
    reviewer_name: str
    status: ReviewStatus
    overall_score: float
    dimension_scores: Dict[QualityDimension, float]
    comments: List[str]
    recommendations: List[str]
    issues_found: List[str]
    approval_conditions: List[str]
    review_duration_minutes: int
    started_at: datetime
    completed_at: Optional[datetime]
    escalated_to: Optional[str]
    escalation_reason: Optional[str]

@dataclass
class QualityStandard:
    """Standard de qualité"""
    standard_id: str
    name: str
    description: str
    deliverable_type: str
    industry: str
    complexity_level: str  # "simple", "medium", "complex", "expert"
    required_metrics: List[str]  # metric_ids
    min_overall_score: float
    review_stages: List[QualityCheckType]
    mandatory_reviewers: List[str]  # Rôles requis
    approval_threshold: int  # Nombre d'approbations requises
    created_at: datetime
    updated_at: datetime

@dataclass
class QualityReport:
    """Rapport de qualité"""
    report_id: str
    deliverable_id: str
    mission_id: str
    overall_quality_score: float
    quality_level: QualityLevel
    dimension_breakdown: Dict[QualityDimension, float]
    checks_summary: Dict[QualityCheckType, Dict[str, Any]]
    improvement_recommendations: List[str]
    compliance_status: Dict[str, bool]
    risk_indicators: List[str]
    benchmark_comparison: Dict[str, float]
    generated_at: datetime
    valid_until: datetime

@dataclass
class QualityTrend:
    """Tendance qualité"""
    trend_id: str
    entity_type: str  # "mission", "agent", "client", "deliverable_type"
    entity_id: str
    time_period: str  # "week", "month", "quarter", "year"
    quality_evolution: List[Tuple[datetime, float]]
    trend_direction: str  # "improving", "stable", "declining"
    trend_strength: float  # 0-1
    key_factors: List[str]
    predictions: Dict[str, float]
    calculated_at: datetime

@dataclass
class QualityAlert:
    """Alerte qualité"""
    alert_id: str
    alert_type: str  # "threshold_breach", "trend_decline", "compliance_issue"
    severity: str  # "low", "medium", "high", "critical"
    entity_type: str
    entity_id: str
    message: str
    details: Dict[str, Any]
    triggered_at: datetime
    acknowledged_at: Optional[datetime]
    resolved_at: Optional[datetime]
    actions_taken: List[str]

class QualityAssuranceSystem:
    """
    Système d'Assurance Qualité Enterprise
    Garantit la qualité des livrables et processus de conseil
    """
    
    def __init__(self, data_path: str = None):
        self.system_id = str(uuid.uuid4())
        self.logger = logging.getLogger(f"QualityAssuranceSystem-{self.system_id[:8]}")
        
        # Chemins de données
        self.data_path = data_path or '/home/ubuntu/substans_ai_megacabinet/data/quality'
        self.db_path = os.path.join(self.data_path, 'quality.db')
        self.reports_path = os.path.join(self.data_path, 'reports')
        self.templates_path = os.path.join(self.data_path, 'templates')
        
        # Création des répertoires
        for path in [self.data_path, self.reports_path, self.templates_path]:
            os.makedirs(path, exist_ok=True)
        
        # Données du système
        self.quality_metrics = {}
        self.quality_standards = {}
        self.quality_checks = {}
        self.quality_reports = {}
        self.quality_trends = {}
        self.quality_alerts = {}
        
        # Configuration
        self.config = {
            'auto_quality_checks': True,
            'min_review_duration': 30,  # minutes
            'escalation_threshold': 0.6,  # Score en dessous duquel escalader
            'trend_analysis_enabled': True,
            'alert_notifications': True,
            'benchmark_enabled': True,
            'continuous_monitoring': True
        }
        
        # Reviewers et leurs compétences
        self.reviewers = {
            'Senior Advisor': {
                'expertise': ['strategic_analysis', 'business_plan', 'all'],
                'max_concurrent_reviews': 5,
                'average_review_time': 60
            },
            'Expert Finance': {
                'expertise': ['financial_analysis', 'business_plan', 'merger_acquisition'],
                'max_concurrent_reviews': 3,
                'average_review_time': 90
            },
            'Expert Stratégie': {
                'expertise': ['strategic_analysis', 'competitive_analysis'],
                'max_concurrent_reviews': 4,
                'average_review_time': 75
            }
        }
        
        # Métriques de qualité par défaut
        self.default_metrics = {}
        
        # Standards de qualité par défaut
        self.default_standards = {}
        
        # Benchmarks industriels
        self.industry_benchmarks = {}
        
        # Statistiques système
        self.system_stats = {
            'total_checks': 0,
            'approved_checks': 0,
            'rejected_checks': 0,
            'average_quality_score': 0.0,
            'average_review_time': 0.0,
            'escalation_rate': 0.0,
            'compliance_rate': 0.0,
            'improvement_rate': 0.0
        }
        
        # Services
        self.executor = ThreadPoolExecutor(max_workers=3)
        
        # Base de données
        self._initialize_database()
        
        # Initialisation des métriques et standards
        self._initialize_default_metrics()
        self._initialize_default_standards()
        self._initialize_industry_benchmarks()
        
        # Chargement des données existantes
        self._load_existing_data()
        
        # Démarrage des services
        self._start_services()
        
        self.logger.info(f"Quality Assurance System initialisé - ID: {self.system_id}")

    def _initialize_database(self):
        """Initialise la base de données"""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Table des métriques de qualité
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quality_metrics (
                    metric_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    dimension TEXT NOT NULL,
                    weight REAL NOT NULL,
                    min_threshold REAL NOT NULL,
                    target_threshold REAL NOT NULL,
                    calculation_method TEXT,
                    automated BOOLEAN NOT NULL,
                    created_at TIMESTAMP NOT NULL
                )
            ''')
            
            # Table des contrôles qualité
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quality_checks (
                    check_id TEXT PRIMARY KEY,
                    deliverable_id TEXT NOT NULL,
                    mission_id TEXT NOT NULL,
                    check_type TEXT NOT NULL,
                    reviewer_id TEXT NOT NULL,
                    reviewer_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    overall_score REAL,
                    dimension_scores TEXT,
                    comments TEXT,
                    recommendations TEXT,
                    issues_found TEXT,
                    approval_conditions TEXT,
                    review_duration_minutes INTEGER,
                    started_at TIMESTAMP NOT NULL,
                    completed_at TIMESTAMP,
                    escalated_to TEXT,
                    escalation_reason TEXT
                )
            ''')
            
            # Table des standards de qualité
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quality_standards (
                    standard_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    deliverable_type TEXT NOT NULL,
                    industry TEXT NOT NULL,
                    complexity_level TEXT NOT NULL,
                    required_metrics TEXT,
                    min_overall_score REAL NOT NULL,
                    review_stages TEXT,
                    mandatory_reviewers TEXT,
                    approval_threshold INTEGER NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL
                )
            ''')
            
            # Table des rapports de qualité
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quality_reports (
                    report_id TEXT PRIMARY KEY,
                    deliverable_id TEXT NOT NULL,
                    mission_id TEXT NOT NULL,
                    overall_quality_score REAL NOT NULL,
                    quality_level TEXT NOT NULL,
                    dimension_breakdown TEXT,
                    checks_summary TEXT,
                    improvement_recommendations TEXT,
                    compliance_status TEXT,
                    risk_indicators TEXT,
                    benchmark_comparison TEXT,
                    generated_at TIMESTAMP NOT NULL,
                    valid_until TIMESTAMP NOT NULL
                )
            ''')
            
            # Table des tendances qualité
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quality_trends (
                    trend_id TEXT PRIMARY KEY,
                    entity_type TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    time_period TEXT NOT NULL,
                    quality_evolution TEXT,
                    trend_direction TEXT NOT NULL,
                    trend_strength REAL NOT NULL,
                    key_factors TEXT,
                    predictions TEXT,
                    calculated_at TIMESTAMP NOT NULL
                )
            ''')
            
            # Table des alertes qualité
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quality_alerts (
                    alert_id TEXT PRIMARY KEY,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    message TEXT NOT NULL,
                    details TEXT,
                    triggered_at TIMESTAMP NOT NULL,
                    acknowledged_at TIMESTAMP,
                    resolved_at TIMESTAMP,
                    actions_taken TEXT
                )
            ''')
            
            # Index pour les performances
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_checks_deliverable 
                ON quality_checks(deliverable_id)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_checks_status 
                ON quality_checks(status)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_reports_mission 
                ON quality_reports(mission_id)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_alerts_severity 
                ON quality_alerts(severity)
            ''')
            
            conn.commit()

    def _initialize_default_metrics(self):
        """Initialise les métriques de qualité par défaut"""
        
        metrics_data = [
            {
                'name': 'Précision du contenu',
                'description': 'Exactitude et fiabilité des informations présentées',
                'dimension': QualityDimension.CONTENT_ACCURACY,
                'weight': 0.15,
                'min_threshold': 0.8,
                'target_threshold': 0.95,
                'calculation_method': 'expert_review',
                'automated': False
            },
            {
                'name': 'Conformité méthodologique',
                'description': 'Respect des méthodologies et frameworks établis',
                'dimension': QualityDimension.METHODOLOGY_COMPLIANCE,
                'weight': 0.12,
                'min_threshold': 0.75,
                'target_threshold': 0.9,
                'calculation_method': 'checklist_validation',
                'automated': True
            },
            {
                'name': 'Qualité de présentation',
                'description': 'Clarté visuelle, structure et lisibilité',
                'dimension': QualityDimension.PRESENTATION_QUALITY,
                'weight': 0.10,
                'min_threshold': 0.7,
                'target_threshold': 0.85,
                'calculation_method': 'automated_analysis',
                'automated': True
            },
            {
                'name': 'Complétude',
                'description': 'Couverture complète des objectifs et exigences',
                'dimension': QualityDimension.COMPLETENESS,
                'weight': 0.13,
                'min_threshold': 0.8,
                'target_threshold': 0.95,
                'calculation_method': 'requirement_mapping',
                'automated': True
            },
            {
                'name': 'Pertinence',
                'description': 'Adéquation avec les besoins et contexte client',
                'dimension': QualityDimension.RELEVANCE,
                'weight': 0.14,
                'min_threshold': 0.75,
                'target_threshold': 0.9,
                'calculation_method': 'expert_review',
                'automated': False
            },
            {
                'name': 'Clarté',
                'description': 'Facilité de compréhension et communication',
                'dimension': QualityDimension.CLARITY,
                'weight': 0.11,
                'min_threshold': 0.7,
                'target_threshold': 0.85,
                'calculation_method': 'readability_analysis',
                'automated': True
            },
            {
                'name': 'Innovation',
                'description': 'Originalité et créativité des approches proposées',
                'dimension': QualityDimension.INNOVATION,
                'weight': 0.08,
                'min_threshold': 0.6,
                'target_threshold': 0.8,
                'calculation_method': 'expert_review',
                'automated': False
            },
            {
                'name': 'Alignement client',
                'description': 'Correspondance avec les attentes et objectifs client',
                'dimension': QualityDimension.CLIENT_ALIGNMENT,
                'weight': 0.12,
                'min_threshold': 0.8,
                'target_threshold': 0.95,
                'calculation_method': 'requirement_validation',
                'automated': True
            },
            {
                'name': 'Rigueur technique',
                'description': 'Solidité des analyses et recommandations',
                'dimension': QualityDimension.TECHNICAL_RIGOR,
                'weight': 0.10,
                'min_threshold': 0.75,
                'target_threshold': 0.9,
                'calculation_method': 'expert_review',
                'automated': False
            },
            {
                'name': 'Actionnabilité',
                'description': 'Facilité de mise en œuvre des recommandations',
                'dimension': QualityDimension.ACTIONABILITY,
                'weight': 0.05,
                'min_threshold': 0.7,
                'target_threshold': 0.85,
                'calculation_method': 'implementation_analysis',
                'automated': True
            }
        ]
        
        for metric_data in metrics_data:
            metric_id = str(uuid.uuid4())
            metric = QualityMetric(
                metric_id=metric_id,
                name=metric_data['name'],
                description=metric_data['description'],
                dimension=metric_data['dimension'],
                weight=metric_data['weight'],
                min_threshold=metric_data['min_threshold'],
                target_threshold=metric_data['target_threshold'],
                calculation_method=metric_data['calculation_method'],
                automated=metric_data['automated'],
                created_at=datetime.now()
            )
            
            self.quality_metrics[metric_id] = metric

    def _initialize_default_standards(self):
        """Initialise les standards de qualité par défaut"""
        
        standards_data = [
            {
                'name': 'Standard Analyse Stratégique',
                'description': 'Standard de qualité pour les analyses stratégiques',
                'deliverable_type': 'strategic_analysis',
                'industry': 'all',
                'complexity_level': 'medium',
                'min_overall_score': 0.8,
                'review_stages': [QualityCheckType.AUTOMATED, QualityCheckType.PEER_REVIEW, QualityCheckType.EXPERT_REVIEW],
                'mandatory_reviewers': ['Senior Advisor'],
                'approval_threshold': 2
            },
            {
                'name': 'Standard Business Plan',
                'description': 'Standard de qualité pour les business plans',
                'deliverable_type': 'business_plan',
                'industry': 'all',
                'complexity_level': 'complex',
                'min_overall_score': 0.85,
                'review_stages': [QualityCheckType.AUTOMATED, QualityCheckType.EXPERT_REVIEW, QualityCheckType.FINAL_VALIDATION],
                'mandatory_reviewers': ['Senior Advisor', 'Expert Finance'],
                'approval_threshold': 2
            },
            {
                'name': 'Standard Analyse Financière',
                'description': 'Standard de qualité pour les analyses financières',
                'deliverable_type': 'financial_analysis',
                'industry': 'finance',
                'complexity_level': 'complex',
                'min_overall_score': 0.9,
                'review_stages': [QualityCheckType.AUTOMATED, QualityCheckType.EXPERT_REVIEW, QualityCheckType.FINAL_VALIDATION],
                'mandatory_reviewers': ['Expert Finance'],
                'approval_threshold': 2
            }
        ]
        
        for standard_data in standards_data:
            standard_id = str(uuid.uuid4())
            standard = QualityStandard(
                standard_id=standard_id,
                name=standard_data['name'],
                description=standard_data['description'],
                deliverable_type=standard_data['deliverable_type'],
                industry=standard_data['industry'],
                complexity_level=standard_data['complexity_level'],
                required_metrics=list(self.quality_metrics.keys()),
                min_overall_score=standard_data['min_overall_score'],
                review_stages=standard_data['review_stages'],
                mandatory_reviewers=standard_data['mandatory_reviewers'],
                approval_threshold=standard_data['approval_threshold'],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.quality_standards[standard_id] = standard

    def _initialize_industry_benchmarks(self):
        """Initialise les benchmarks industriels"""
        
        self.industry_benchmarks = {
            'technology': {
                'average_quality_score': 0.82,
                'top_quartile_threshold': 0.9,
                'dimension_averages': {
                    QualityDimension.CONTENT_ACCURACY: 0.85,
                    QualityDimension.METHODOLOGY_COMPLIANCE: 0.8,
                    QualityDimension.INNOVATION: 0.9,
                    QualityDimension.TECHNICAL_RIGOR: 0.88
                }
            },
            'finance': {
                'average_quality_score': 0.88,
                'top_quartile_threshold': 0.95,
                'dimension_averages': {
                    QualityDimension.CONTENT_ACCURACY: 0.92,
                    QualityDimension.METHODOLOGY_COMPLIANCE: 0.9,
                    QualityDimension.TECHNICAL_RIGOR: 0.95,
                    QualityDimension.CLARITY: 0.85
                }
            },
            'healthcare': {
                'average_quality_score': 0.85,
                'top_quartile_threshold': 0.92,
                'dimension_averages': {
                    QualityDimension.CONTENT_ACCURACY: 0.95,
                    QualityDimension.METHODOLOGY_COMPLIANCE: 0.88,
                    QualityDimension.TECHNICAL_RIGOR: 0.9,
                    QualityDimension.ACTIONABILITY: 0.8
                }
            }
        }

    def create_quality_check(self, deliverable_id: str, mission_id: str, 
                           check_type: QualityCheckType, reviewer_id: str = None) -> QualityCheck:
        """Crée un nouveau contrôle qualité"""
        
        check_id = str(uuid.uuid4())
        
        # Sélection automatique du reviewer si non spécifié
        if not reviewer_id:
            reviewer_id = self._select_best_reviewer(deliverable_id, check_type)
        
        reviewer_name = reviewer_id  # Simplification
        
        # Création du contrôle
        quality_check = QualityCheck(
            check_id=check_id,
            deliverable_id=deliverable_id,
            mission_id=mission_id,
            check_type=check_type,
            reviewer_id=reviewer_id,
            reviewer_name=reviewer_name,
            status=ReviewStatus.PENDING,
            overall_score=0.0,
            dimension_scores={},
            comments=[],
            recommendations=[],
            issues_found=[],
            approval_conditions=[],
            review_duration_minutes=0,
            started_at=datetime.now(),
            completed_at=None,
            escalated_to=None,
            escalation_reason=None
        )
        
        # Sauvegarde
        self.quality_checks[check_id] = quality_check
        self._save_quality_check(quality_check)
        
        # Démarrage automatique si contrôle automatisé
        if check_type == QualityCheckType.AUTOMATED:
            self.executor.submit(self._perform_automated_check, check_id)
        
        self.logger.info(f"Contrôle qualité créé: {check_id} ({check_type.value})")
        
        return quality_check

    def perform_quality_check(self, check_id: str, scores: Dict[QualityDimension, float],
                            comments: List[str] = None, recommendations: List[str] = None,
                            issues: List[str] = None) -> bool:
        """Effectue un contrôle qualité"""
        
        if check_id not in self.quality_checks:
            self.logger.error(f"Contrôle qualité non trouvé: {check_id}")
            return False
        
        quality_check = self.quality_checks[check_id]
        
        # Mise à jour du statut
        quality_check.status = ReviewStatus.IN_REVIEW
        quality_check.dimension_scores = scores
        quality_check.comments = comments or []
        quality_check.recommendations = recommendations or []
        quality_check.issues_found = issues or []
        
        # Calcul du score global
        overall_score = self._calculate_overall_score(scores)
        quality_check.overall_score = overall_score
        
        # Détermination du statut final
        standard = self._get_applicable_standard(quality_check.deliverable_id)
        
        if overall_score >= (standard.min_overall_score if standard else 0.8):
            if not quality_check.issues_found:
                quality_check.status = ReviewStatus.APPROVED
            else:
                quality_check.status = ReviewStatus.NEEDS_REVISION
                quality_check.approval_conditions = [
                    f"Corriger: {issue}" for issue in quality_check.issues_found
                ]
        else:
            if overall_score < self.config['escalation_threshold']:
                quality_check.status = ReviewStatus.ESCALATED
                quality_check.escalated_to = 'Senior Advisor'
                quality_check.escalation_reason = f"Score trop faible: {overall_score:.2f}"
            else:
                quality_check.status = ReviewStatus.REJECTED
        
        # Finalisation
        quality_check.completed_at = datetime.now()
        quality_check.review_duration_minutes = int(
            (quality_check.completed_at - quality_check.started_at).total_seconds() / 60
        )
        
        # Sauvegarde
        self._save_quality_check(quality_check)
        
        # Mise à jour des statistiques
        self._update_system_stats()
        
        # Génération d'alertes si nécessaire
        if quality_check.status in [ReviewStatus.REJECTED, ReviewStatus.ESCALATED]:
            self._generate_quality_alert(quality_check)
        
        self.logger.info(f"Contrôle qualité terminé: {check_id} - Score: {overall_score:.2f}")
        
        return True

    def generate_quality_report(self, deliverable_id: str, mission_id: str) -> QualityReport:
        """Génère un rapport de qualité pour un livrable"""
        
        report_id = str(uuid.uuid4())
        
        # Récupération des contrôles qualité pour ce livrable
        deliverable_checks = [
            check for check in self.quality_checks.values()
            if check.deliverable_id == deliverable_id
        ]
        
        if not deliverable_checks:
            self.logger.warning(f"Aucun contrôle qualité trouvé pour le livrable: {deliverable_id}")
            # Création d'un rapport par défaut
            return self._create_default_quality_report(report_id, deliverable_id, mission_id)
        
        # Calcul du score global
        completed_checks = [c for c in deliverable_checks if c.status in [
            ReviewStatus.APPROVED, ReviewStatus.REJECTED, ReviewStatus.NEEDS_REVISION
        ]]
        
        if not completed_checks:
            overall_score = 0.0
        else:
            overall_score = statistics.mean([c.overall_score for c in completed_checks])
        
        # Détermination du niveau de qualité
        quality_level = self._determine_quality_level(overall_score)
        
        # Analyse des dimensions
        dimension_breakdown = {}
        for dimension in QualityDimension:
            dimension_scores = []
            for check in completed_checks:
                if dimension in check.dimension_scores:
                    dimension_scores.append(check.dimension_scores[dimension])
            
            if dimension_scores:
                dimension_breakdown[dimension] = statistics.mean(dimension_scores)
            else:
                dimension_breakdown[dimension] = 0.0
        
        # Résumé des contrôles
        checks_summary = {}
        for check_type in QualityCheckType:
            type_checks = [c for c in deliverable_checks if c.check_type == check_type]
            if type_checks:
                checks_summary[check_type] = {
                    'count': len(type_checks),
                    'completed': len([c for c in type_checks if c.completed_at]),
                    'approved': len([c for c in type_checks if c.status == ReviewStatus.APPROVED]),
                    'average_score': statistics.mean([c.overall_score for c in type_checks if c.overall_score > 0])
                }
        
        # Recommandations d'amélioration
        improvement_recommendations = []
        for check in completed_checks:
            improvement_recommendations.extend(check.recommendations)
        
        # Suppression des doublons
        improvement_recommendations = list(set(improvement_recommendations))
        
        # Statut de conformité
        standard = self._get_applicable_standard(deliverable_id)
        compliance_status = {}
        
        if standard:
            compliance_status = {
                'overall_score_compliant': overall_score >= standard.min_overall_score,
                'required_reviews_completed': len(completed_checks) >= len(standard.review_stages),
                'mandatory_reviewers_involved': self._check_mandatory_reviewers(deliverable_checks, standard),
                'approval_threshold_met': len([c for c in completed_checks if c.status == ReviewStatus.APPROVED]) >= standard.approval_threshold
            }
        
        # Indicateurs de risque
        risk_indicators = []
        if overall_score < 0.7:
            risk_indicators.append("Score de qualité faible")
        if len([c for c in completed_checks if c.status == ReviewStatus.REJECTED]) > 0:
            risk_indicators.append("Contrôles rejetés")
        if len([c for c in completed_checks if c.status == ReviewStatus.ESCALATED]) > 0:
            risk_indicators.append("Escalations requises")
        
        # Comparaison avec les benchmarks
        benchmark_comparison = self._get_benchmark_comparison(deliverable_id, overall_score, dimension_breakdown)
        
        # Création du rapport
        quality_report = QualityReport(
            report_id=report_id,
            deliverable_id=deliverable_id,
            mission_id=mission_id,
            overall_quality_score=overall_score,
            quality_level=quality_level,
            dimension_breakdown=dimension_breakdown,
            checks_summary=checks_summary,
            improvement_recommendations=improvement_recommendations,
            compliance_status=compliance_status,
            risk_indicators=risk_indicators,
            benchmark_comparison=benchmark_comparison,
            generated_at=datetime.now(),
            valid_until=datetime.now() + timedelta(days=30)
        )
        
        # Sauvegarde
        self.quality_reports[report_id] = quality_report
        self._save_quality_report(quality_report)
        
        self.logger.info(f"Rapport de qualité généré: {report_id} - Score: {overall_score:.2f}")
        
        return quality_report

    def analyze_quality_trends(self, entity_type: str, entity_id: str, 
                             time_period: str = "month") -> QualityTrend:
        """Analyse les tendances qualité"""
        
        trend_id = str(uuid.uuid4())
        
        # Récupération des données historiques
        historical_data = self._get_historical_quality_data(entity_type, entity_id, time_period)
        
        if len(historical_data) < 2:
            self.logger.warning(f"Données insuffisantes pour l'analyse de tendance: {entity_id}")
            return self._create_default_trend(trend_id, entity_type, entity_id, time_period)
        
        # Calcul de la tendance
        quality_evolution = [(datetime.fromisoformat(date), score) for date, score in historical_data]
        quality_evolution.sort(key=lambda x: x[0])
        
        # Analyse de la direction
        scores = [score for _, score in quality_evolution]
        
        if len(scores) >= 3:
            # Régression linéaire simple
            x_values = list(range(len(scores)))
            slope = self._calculate_slope(x_values, scores)
            
            if slope > 0.01:
                trend_direction = "improving"
                trend_strength = min(1.0, abs(slope) * 10)
            elif slope < -0.01:
                trend_direction = "declining"
                trend_strength = min(1.0, abs(slope) * 10)
            else:
                trend_direction = "stable"
                trend_strength = 0.1
        else:
            trend_direction = "stable"
            trend_strength = 0.1
        
        # Facteurs clés
        key_factors = self._identify_key_factors(entity_type, entity_id, quality_evolution)
        
        # Prédictions
        predictions = {}
        if len(scores) >= 3:
            next_month_prediction = scores[-1] + slope
            predictions = {
                'next_month': max(0.0, min(1.0, next_month_prediction)),
                'confidence': trend_strength
            }
        
        # Création de la tendance
        quality_trend = QualityTrend(
            trend_id=trend_id,
            entity_type=entity_type,
            entity_id=entity_id,
            time_period=time_period,
            quality_evolution=quality_evolution,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            key_factors=key_factors,
            predictions=predictions,
            calculated_at=datetime.now()
        )
        
        # Sauvegarde
        self.quality_trends[trend_id] = quality_trend
        self._save_quality_trend(quality_trend)
        
        self.logger.info(f"Tendance qualité analysée: {entity_id} - Direction: {trend_direction}")
        
        return quality_trend

    def get_quality_dashboard(self, entity_type: str = None, entity_id: str = None) -> Dict[str, Any]:
        """Retourne le tableau de bord qualité"""
        
        if entity_type and entity_id:
            # Dashboard spécifique
            return self._get_entity_quality_dashboard(entity_type, entity_id)
        
        # Dashboard global
        total_checks = len(self.quality_checks)
        completed_checks = len([c for c in self.quality_checks.values() if c.completed_at])
        approved_checks = len([c for c in self.quality_checks.values() if c.status == ReviewStatus.APPROVED])
        
        # Scores moyens
        completed_checks_list = [c for c in self.quality_checks.values() if c.overall_score > 0]
        avg_score = statistics.mean([c.overall_score for c in completed_checks_list]) if completed_checks_list else 0.0
        
        # Distribution des niveaux de qualité
        quality_distribution = defaultdict(int)
        for check in completed_checks_list:
            level = self._determine_quality_level(check.overall_score)
            quality_distribution[level.value] += 1
        
        # Tendances récentes
        recent_trends = self._get_recent_quality_trends()
        
        # Alertes actives
        active_alerts = [alert for alert in self.quality_alerts.values() if not alert.resolved_at]
        
        return {
            'overview': {
                'total_checks': total_checks,
                'completed_checks': completed_checks,
                'approval_rate': approved_checks / completed_checks if completed_checks > 0 else 0,
                'average_quality_score': avg_score
            },
            'quality_distribution': dict(quality_distribution),
            'performance_metrics': {
                'average_review_time': self.system_stats['average_review_time'],
                'escalation_rate': self.system_stats['escalation_rate'],
                'compliance_rate': self.system_stats['compliance_rate']
            },
            'trends': recent_trends,
            'active_alerts': len(active_alerts),
            'top_issues': self._get_top_quality_issues(),
            'improvement_opportunities': self._get_improvement_opportunities()
        }

    def _perform_automated_check(self, check_id: str):
        """Effectue un contrôle qualité automatisé"""
        
        quality_check = self.quality_checks.get(check_id)
        if not quality_check:
            return
        
        # Simulation d'un contrôle automatisé
        dimension_scores = {}
        
        # Contrôles automatisés basiques
        for dimension in QualityDimension:
            metric = self._get_metric_for_dimension(dimension)
            if metric and metric.automated:
                # Simulation de calcul automatique
                score = self._simulate_automated_score(dimension)
                dimension_scores[dimension] = score
        
        # Finalisation du contrôle
        self.perform_quality_check(
            check_id=check_id,
            scores=dimension_scores,
            comments=["Contrôle automatisé effectué"],
            recommendations=self._generate_automated_recommendations(dimension_scores)
        )

    def _simulate_automated_score(self, dimension: QualityDimension) -> float:
        """Simule un score automatisé pour une dimension"""
        
        # Simulation basée sur la dimension
        base_scores = {
            QualityDimension.METHODOLOGY_COMPLIANCE: 0.85,
            QualityDimension.PRESENTATION_QUALITY: 0.8,
            QualityDimension.COMPLETENESS: 0.9,
            QualityDimension.CLARITY: 0.75,
            QualityDimension.CLIENT_ALIGNMENT: 0.88,
            QualityDimension.ACTIONABILITY: 0.82
        }
        
        base_score = base_scores.get(dimension, 0.8)
        
        # Ajout de variabilité
        import random
        variation = random.uniform(-0.1, 0.1)
        
        return max(0.0, min(1.0, base_score + variation))

    def _generate_automated_recommendations(self, scores: Dict[QualityDimension, float]) -> List[str]:
        """Génère des recommandations automatiques"""
        
        recommendations = []
        
        for dimension, score in scores.items():
            if score < 0.7:
                if dimension == QualityDimension.PRESENTATION_QUALITY:
                    recommendations.append("Améliorer la mise en forme et la structure du document")
                elif dimension == QualityDimension.CLARITY:
                    recommendations.append("Simplifier le langage et améliorer la lisibilité")
                elif dimension == QualityDimension.COMPLETENESS:
                    recommendations.append("Vérifier que tous les objectifs sont couverts")
                elif dimension == QualityDimension.METHODOLOGY_COMPLIANCE:
                    recommendations.append("Revoir la conformité aux méthodologies établies")
        
        return recommendations

    def _calculate_overall_score(self, dimension_scores: Dict[QualityDimension, float]) -> float:
        """Calcule le score global pondéré"""
        
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for dimension, score in dimension_scores.items():
            metric = self._get_metric_for_dimension(dimension)
            weight = metric.weight if metric else 0.1
            
            total_weighted_score += score * weight
            total_weight += weight
        
        return total_weighted_score / total_weight if total_weight > 0 else 0.0

    def _determine_quality_level(self, score: float) -> QualityLevel:
        """Détermine le niveau de qualité basé sur le score"""
        
        if score >= 0.9:
            return QualityLevel.EXCELLENT
        elif score >= 0.75:
            return QualityLevel.GOOD
        elif score >= 0.6:
            return QualityLevel.ACCEPTABLE
        elif score >= 0.4:
            return QualityLevel.POOR
        else:
            return QualityLevel.UNACCEPTABLE

    def _get_metric_for_dimension(self, dimension: QualityDimension) -> Optional[QualityMetric]:
        """Retourne la métrique pour une dimension"""
        
        for metric in self.quality_metrics.values():
            if metric.dimension == dimension:
                return metric
        return None

    def _get_applicable_standard(self, deliverable_id: str) -> Optional[QualityStandard]:
        """Retourne le standard applicable pour un livrable"""
        
        # Simulation - en réalité, on récupérerait le type de livrable
        # et l'industrie depuis la base de données
        for standard in self.quality_standards.values():
            if standard.deliverable_type in ['strategic_analysis', 'business_plan']:
                return standard
        
        return None

    def _select_best_reviewer(self, deliverable_id: str, check_type: QualityCheckType) -> str:
        """Sélectionne le meilleur reviewer pour un contrôle"""
        
        # Logique de sélection basée sur l'expertise et la disponibilité
        if check_type == QualityCheckType.AUTOMATED:
            return 'System'
        
        # Sélection basée sur l'expertise
        available_reviewers = []
        for reviewer_id, reviewer_info in self.reviewers.items():
            if 'all' in reviewer_info['expertise']:
                available_reviewers.append(reviewer_id)
        
        return available_reviewers[0] if available_reviewers else 'Senior Advisor'

    def _check_mandatory_reviewers(self, checks: List[QualityCheck], standard: QualityStandard) -> bool:
        """Vérifie si tous les reviewers obligatoires ont participé"""
        
        involved_reviewers = set(check.reviewer_id for check in checks)
        mandatory_reviewers = set(standard.mandatory_reviewers)
        
        return mandatory_reviewers.issubset(involved_reviewers)

    def _get_benchmark_comparison(self, deliverable_id: str, overall_score: float, 
                                dimension_breakdown: Dict[QualityDimension, float]) -> Dict[str, float]:
        """Retourne la comparaison avec les benchmarks"""
        
        # Simulation - en réalité, on déterminerait l'industrie du client
        industry = 'technology'  # Par défaut
        
        if industry in self.industry_benchmarks:
            benchmark = self.industry_benchmarks[industry]
            
            return {
                'industry_average_delta': overall_score - benchmark['average_quality_score'],
                'top_quartile_delta': overall_score - benchmark['top_quartile_threshold'],
                'percentile_rank': min(100, max(0, (overall_score - 0.5) * 200))  # Approximation
            }
        
        return {}

    def _generate_quality_alert(self, quality_check: QualityCheck):
        """Génère une alerte qualité"""
        
        alert_id = str(uuid.uuid4())
        
        if quality_check.status == ReviewStatus.ESCALATED:
            severity = "high"
            message = f"Contrôle qualité escaladé - Score: {quality_check.overall_score:.2f}"
        else:
            severity = "medium"
            message = f"Contrôle qualité rejeté - Score: {quality_check.overall_score:.2f}"
        
        alert = QualityAlert(
            alert_id=alert_id,
            alert_type="quality_issue",
            severity=severity,
            entity_type="deliverable",
            entity_id=quality_check.deliverable_id,
            message=message,
            details={
                'check_id': quality_check.check_id,
                'reviewer': quality_check.reviewer_name,
                'issues': quality_check.issues_found
            },
            triggered_at=datetime.now(),
            acknowledged_at=None,
            resolved_at=None,
            actions_taken=[]
        )
        
        self.quality_alerts[alert_id] = alert
        self._save_quality_alert(alert)

    def _update_system_stats(self):
        """Met à jour les statistiques système"""
        
        completed_checks = [c for c in self.quality_checks.values() if c.completed_at]
        
        if completed_checks:
            self.system_stats.update({
                'total_checks': len(self.quality_checks),
                'approved_checks': len([c for c in completed_checks if c.status == ReviewStatus.APPROVED]),
                'rejected_checks': len([c for c in completed_checks if c.status == ReviewStatus.REJECTED]),
                'average_quality_score': statistics.mean([c.overall_score for c in completed_checks if c.overall_score > 0]),
                'average_review_time': statistics.mean([c.review_duration_minutes for c in completed_checks if c.review_duration_minutes > 0]),
                'escalation_rate': len([c for c in completed_checks if c.status == ReviewStatus.ESCALATED]) / len(completed_checks)
            })

    def _get_historical_quality_data(self, entity_type: str, entity_id: str, time_period: str) -> List[Tuple[str, float]]:
        """Récupère les données historiques de qualité"""
        
        # Simulation de données historiques
        historical_data = []
        
        base_date = datetime.now() - timedelta(days=90)
        for i in range(12):  # 12 points de données
            date = base_date + timedelta(days=i * 7)
            score = 0.8 + (i * 0.01) + ((-1) ** i * 0.02)  # Tendance légèrement croissante avec variations
            historical_data.append((date.isoformat(), max(0.0, min(1.0, score))))
        
        return historical_data

    def _calculate_slope(self, x_values: List[int], y_values: List[float]) -> float:
        """Calcule la pente d'une régression linéaire simple"""
        
        n = len(x_values)
        if n < 2:
            return 0.0
        
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x * x for x in x_values)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        return slope

    def _identify_key_factors(self, entity_type: str, entity_id: str, 
                            quality_evolution: List[Tuple[datetime, float]]) -> List[str]:
        """Identifie les facteurs clés influençant la qualité"""
        
        factors = []
        
        # Analyse des variations
        scores = [score for _, score in quality_evolution]
        
        if len(scores) >= 3:
            recent_trend = scores[-3:]
            if all(recent_trend[i] > recent_trend[i-1] for i in range(1, len(recent_trend))):
                factors.append("Amélioration continue récente")
            elif all(recent_trend[i] < recent_trend[i-1] for i in range(1, len(recent_trend))):
                factors.append("Dégradation récente")
        
        # Facteurs génériques basés sur le type d'entité
        if entity_type == "mission":
            factors.extend(["Complexité du projet", "Expérience de l'équipe"])
        elif entity_type == "agent":
            factors.extend(["Charge de travail", "Formation récente"])
        
        return factors

    def _create_default_quality_report(self, report_id: str, deliverable_id: str, mission_id: str) -> QualityReport:
        """Crée un rapport de qualité par défaut"""
        
        return QualityReport(
            report_id=report_id,
            deliverable_id=deliverable_id,
            mission_id=mission_id,
            overall_quality_score=0.0,
            quality_level=QualityLevel.UNACCEPTABLE,
            dimension_breakdown={dim: 0.0 for dim in QualityDimension},
            checks_summary={},
            improvement_recommendations=["Effectuer des contrôles qualité"],
            compliance_status={'no_checks_performed': True},
            risk_indicators=["Aucun contrôle qualité effectué"],
            benchmark_comparison={},
            generated_at=datetime.now(),
            valid_until=datetime.now() + timedelta(days=30)
        )

    def _create_default_trend(self, trend_id: str, entity_type: str, entity_id: str, time_period: str) -> QualityTrend:
        """Crée une tendance par défaut"""
        
        return QualityTrend(
            trend_id=trend_id,
            entity_type=entity_type,
            entity_id=entity_id,
            time_period=time_period,
            quality_evolution=[(datetime.now(), 0.0)],
            trend_direction="stable",
            trend_strength=0.0,
            key_factors=["Données insuffisantes"],
            predictions={},
            calculated_at=datetime.now()
        )

    def _get_entity_quality_dashboard(self, entity_type: str, entity_id: str) -> Dict[str, Any]:
        """Retourne le dashboard qualité pour une entité spécifique"""
        
        # Récupération des contrôles pour cette entité
        entity_checks = []
        if entity_type == "mission":
            entity_checks = [c for c in self.quality_checks.values() if c.mission_id == entity_id]
        elif entity_type == "deliverable":
            entity_checks = [c for c in self.quality_checks.values() if c.deliverable_id == entity_id]
        
        completed_checks = [c for c in entity_checks if c.completed_at]
        
        # Calculs
        avg_score = statistics.mean([c.overall_score for c in completed_checks]) if completed_checks else 0.0
        
        return {
            'entity_info': {
                'entity_type': entity_type,
                'entity_id': entity_id,
                'total_checks': len(entity_checks),
                'completed_checks': len(completed_checks)
            },
            'quality_metrics': {
                'average_score': avg_score,
                'quality_level': self._determine_quality_level(avg_score).value,
                'approval_rate': len([c for c in completed_checks if c.status == ReviewStatus.APPROVED]) / len(completed_checks) if completed_checks else 0
            },
            'recent_checks': [
                {
                    'check_id': c.check_id,
                    'type': c.check_type.value,
                    'score': c.overall_score,
                    'status': c.status.value,
                    'completed_at': c.completed_at.isoformat() if c.completed_at else None
                }
                for c in sorted(entity_checks, key=lambda x: x.started_at, reverse=True)[:5]
            ]
        }

    def _get_recent_quality_trends(self) -> List[Dict[str, Any]]:
        """Retourne les tendances qualité récentes"""
        
        recent_trends = sorted(
            self.quality_trends.values(),
            key=lambda t: t.calculated_at,
            reverse=True
        )[:5]
        
        return [
            {
                'entity_type': t.entity_type,
                'entity_id': t.entity_id,
                'direction': t.trend_direction,
                'strength': t.trend_strength,
                'calculated_at': t.calculated_at.isoformat()
            }
            for t in recent_trends
        ]

    def _get_top_quality_issues(self) -> List[str]:
        """Retourne les principaux problèmes de qualité"""
        
        issues = []
        for check in self.quality_checks.values():
            issues.extend(check.issues_found)
        
        # Comptage des occurrences
        issue_counts = defaultdict(int)
        for issue in issues:
            issue_counts[issue] += 1
        
        # Top 5
        top_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return [f"{issue} ({count} occurrences)" for issue, count in top_issues]

    def _get_improvement_opportunities(self) -> List[str]:
        """Retourne les opportunités d'amélioration"""
        
        opportunities = []
        
        # Analyse des dimensions faibles
        dimension_scores = defaultdict(list)
        for check in self.quality_checks.values():
            if check.overall_score > 0:
                for dim, score in check.dimension_scores.items():
                    dimension_scores[dim].append(score)
        
        for dim, scores in dimension_scores.items():
            if scores:
                avg_score = statistics.mean(scores)
                if avg_score < 0.75:
                    opportunities.append(f"Améliorer {dim.value} (score moyen: {avg_score:.2f})")
        
        return opportunities[:5]

    def _save_quality_check(self, quality_check: QualityCheck):
        """Sauvegarde un contrôle qualité"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO quality_checks 
                    (check_id, deliverable_id, mission_id, check_type, reviewer_id,
                     reviewer_name, status, overall_score, dimension_scores, comments,
                     recommendations, issues_found, approval_conditions, review_duration_minutes,
                     started_at, completed_at, escalated_to, escalation_reason)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    quality_check.check_id, quality_check.deliverable_id, quality_check.mission_id,
                    quality_check.check_type.value, quality_check.reviewer_id, quality_check.reviewer_name,
                    quality_check.status.value, quality_check.overall_score,
                    json.dumps({dim.value: score for dim, score in quality_check.dimension_scores.items()}),
                    json.dumps(quality_check.comments), json.dumps(quality_check.recommendations),
                    json.dumps(quality_check.issues_found), json.dumps(quality_check.approval_conditions),
                    quality_check.review_duration_minutes, quality_check.started_at, quality_check.completed_at,
                    quality_check.escalated_to, quality_check.escalation_reason
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde contrôle qualité: {e}")

    def _save_quality_report(self, quality_report: QualityReport):
        """Sauvegarde un rapport de qualité"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO quality_reports 
                    (report_id, deliverable_id, mission_id, overall_quality_score, quality_level,
                     dimension_breakdown, checks_summary, improvement_recommendations, compliance_status,
                     risk_indicators, benchmark_comparison, generated_at, valid_until)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    quality_report.report_id, quality_report.deliverable_id, quality_report.mission_id,
                    quality_report.overall_quality_score, quality_report.quality_level.value,
                    json.dumps({dim.value: score for dim, score in quality_report.dimension_breakdown.items()}),
                    json.dumps({ct.value: summary for ct, summary in quality_report.checks_summary.items()}),
                    json.dumps(quality_report.improvement_recommendations),
                    json.dumps(quality_report.compliance_status), json.dumps(quality_report.risk_indicators),
                    json.dumps(quality_report.benchmark_comparison), quality_report.generated_at,
                    quality_report.valid_until
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde rapport qualité: {e}")

    def _save_quality_trend(self, quality_trend: QualityTrend):
        """Sauvegarde une tendance qualité"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO quality_trends 
                    (trend_id, entity_type, entity_id, time_period, quality_evolution,
                     trend_direction, trend_strength, key_factors, predictions, calculated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    quality_trend.trend_id, quality_trend.entity_type, quality_trend.entity_id,
                    quality_trend.time_period,
                    json.dumps([(dt.isoformat(), score) for dt, score in quality_trend.quality_evolution]),
                    quality_trend.trend_direction, quality_trend.trend_strength,
                    json.dumps(quality_trend.key_factors), json.dumps(quality_trend.predictions),
                    quality_trend.calculated_at
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde tendance qualité: {e}")

    def _save_quality_alert(self, quality_alert: QualityAlert):
        """Sauvegarde une alerte qualité"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO quality_alerts 
                    (alert_id, alert_type, severity, entity_type, entity_id, message,
                     details, triggered_at, acknowledged_at, resolved_at, actions_taken)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    quality_alert.alert_id, quality_alert.alert_type, quality_alert.severity,
                    quality_alert.entity_type, quality_alert.entity_id, quality_alert.message,
                    json.dumps(quality_alert.details), quality_alert.triggered_at,
                    quality_alert.acknowledged_at, quality_alert.resolved_at,
                    json.dumps(quality_alert.actions_taken)
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde alerte qualité: {e}")

    def _load_existing_data(self):
        """Charge les données existantes"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Chargement des contrôles qualité
                cursor.execute('SELECT * FROM quality_checks ORDER BY started_at DESC LIMIT 100')
                
                for row in cursor.fetchall():
                    # Reconstruction simplifiée
                    check_id = row[0]
                    # Note: Implémentation simplifiée pour le chargement
                
                self.logger.info("Données qualité existantes chargées")
                
        except Exception as e:
            self.logger.error(f"Erreur chargement données qualité: {e}")

    def _start_services(self):
        """Démarre les services du système"""
        
        # Service de monitoring qualité
        if self.config['continuous_monitoring']:
            threading.Thread(target=self._quality_monitoring_service, daemon=True).start()
        
        # Service d'analyse des tendances
        if self.config['trend_analysis_enabled']:
            threading.Thread(target=self._trend_analysis_service, daemon=True).start()

    def _quality_monitoring_service(self):
        """Service de monitoring qualité continu"""
        
        while True:
            try:
                # Vérification des contrôles en cours
                pending_checks = [c for c in self.quality_checks.values() 
                                if c.status == ReviewStatus.PENDING]
                
                for check in pending_checks:
                    # Vérification des timeouts
                    elapsed_time = (datetime.now() - check.started_at).total_seconds() / 60
                    if elapsed_time > 120:  # 2 heures
                        self.logger.warning(f"Contrôle qualité en timeout: {check.check_id}")
                
                # Mise à jour des statistiques
                self._update_system_stats()
                
                time.sleep(1800)  # Toutes les 30 minutes
                
            except Exception as e:
                self.logger.error(f"Erreur service monitoring qualité: {e}")
                time.sleep(1800)

    def _trend_analysis_service(self):
        """Service d'analyse des tendances"""
        
        while True:
            try:
                # Analyse des tendances pour les entités actives
                active_entities = set()
                
                # Collecte des entités actives
                for check in self.quality_checks.values():
                    active_entities.add(('mission', check.mission_id))
                    active_entities.add(('deliverable', check.deliverable_id))
                
                # Analyse des tendances
                for entity_type, entity_id in list(active_entities)[:10]:  # Limite pour éviter la surcharge
                    try:
                        self.analyze_quality_trends(entity_type, entity_id)
                    except Exception as e:
                        self.logger.error(f"Erreur analyse tendance {entity_id}: {e}")
                
                time.sleep(86400)  # Une fois par jour
                
            except Exception as e:
                self.logger.error(f"Erreur service analyse tendances: {e}")
                time.sleep(86400)

    def get_system_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques du système"""
        
        self._update_system_stats()
        return self.system_stats.copy()

# Instance globale
_quality_assurance_system = None

def get_quality_assurance_system() -> QualityAssuranceSystem:
    """Retourne l'instance du système d'assurance qualité"""
    global _quality_assurance_system
    if _quality_assurance_system is None:
        _quality_assurance_system = QualityAssuranceSystem()
    return _quality_assurance_system

# Test du système
if __name__ == '__main__':
    print("=== Test Quality Assurance System ===")
    
    qas = QualityAssuranceSystem()
    
    # Création d'un contrôle qualité de test
    check = qas.create_quality_check(
        deliverable_id="test_deliverable_001",
        mission_id="test_mission_001",
        check_type=QualityCheckType.EXPERT_REVIEW,
        reviewer_id="Senior Advisor"
    )
    
    print(f"Contrôle qualité créé: {check.check_id}")
    
    # Simulation d'un contrôle
    dimension_scores = {
        QualityDimension.CONTENT_ACCURACY: 0.85,
        QualityDimension.METHODOLOGY_COMPLIANCE: 0.9,
        QualityDimension.PRESENTATION_QUALITY: 0.75,
        QualityDimension.COMPLETENESS: 0.88,
        QualityDimension.RELEVANCE: 0.82
    }
    
    success = qas.perform_quality_check(
        check_id=check.check_id,
        scores=dimension_scores,
        comments=["Bon travail global", "Quelques améliorations possibles"],
        recommendations=["Améliorer la présentation", "Ajouter plus d'exemples"]
    )
    
    print(f"Contrôle effectué: {success} - Score: {check.overall_score:.2f}")
    
    # Génération d'un rapport
    report = qas.generate_quality_report("test_deliverable_001", "test_mission_001")
    print(f"Rapport généré: {report.quality_level.value} ({report.overall_quality_score:.2f})")
    
    # Analyse des tendances
    trend = qas.analyze_quality_trends("mission", "test_mission_001")
    print(f"Tendance analysée: {trend.trend_direction} (force: {trend.trend_strength:.2f})")
    
    # Dashboard
    dashboard = qas.get_quality_dashboard()
    print(f"Dashboard: {dashboard['overview']['total_checks']} contrôles totaux")
    
    # Statistiques
    stats = qas.get_system_statistics()
    print(f"Statistiques: Score moyen {stats['average_quality_score']:.2f}")
    
    print("Test terminé avec succès")

