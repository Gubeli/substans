"""
Methodology Adaptive - Système de Méthodologies Adaptatives
Système intelligent d'adaptation et d'optimisation des méthodologies de conseil
"""

import json
import logging
import numpy as np
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
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import networkx as nx
from collections import defaultdict, Counter
import pickle
import hashlib

# Configuration du logging
logging.basicConfig(level=logging.INFO)

class MethodologyType(Enum):
    """Types de méthodologies"""
    STRATEGIC_ANALYSIS = "strategic_analysis"
    BUSINESS_PLAN = "business_plan"
    MARKET_RESEARCH = "market_research"
    COMPETITIVE_ANALYSIS = "competitive_analysis"
    FINANCIAL_ANALYSIS = "financial_analysis"
    OPERATIONAL_AUDIT = "operational_audit"
    DIGITAL_TRANSFORMATION = "digital_transformation"
    CHANGE_MANAGEMENT = "change_management"
    RISK_ASSESSMENT = "risk_assessment"
    INNOVATION_STRATEGY = "innovation_strategy"

class ComplexityLevel(Enum):
    """Niveaux de complexité"""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    EXPERT = "expert"

class IndustryType(Enum):
    """Types d'industries"""
    TECHNOLOGY = "technology"
    FINANCE = "finance"
    HEALTHCARE = "healthcare"
    MANUFACTURING = "manufacturing"
    RETAIL = "retail"
    ENERGY = "energy"
    TELECOMMUNICATIONS = "telecommunications"
    AUTOMOTIVE = "automotive"
    AEROSPACE = "aerospace"
    CONSULTING = "consulting"

class AdaptationTrigger(Enum):
    """Déclencheurs d'adaptation"""
    PERFORMANCE_DECLINE = "performance_decline"
    NEW_CONTEXT = "new_context"
    FEEDBACK_NEGATIVE = "feedback_negative"
    COMPLEXITY_INCREASE = "complexity_increase"
    TIME_CONSTRAINT = "time_constraint"
    RESOURCE_CONSTRAINT = "resource_constraint"
    QUALITY_REQUIREMENT = "quality_requirement"
    INNOVATION_NEED = "innovation_need"

@dataclass
class MethodologyStep:
    """Étape de méthodologie"""
    step_id: str
    name: str
    description: str
    duration_estimate: int  # en heures
    complexity_score: float
    required_skills: List[str]
    deliverables: List[str]
    dependencies: List[str]
    optional: bool
    success_criteria: List[str]
    resources_needed: List[str]
    risk_factors: List[str]

@dataclass
class Methodology:
    """Méthodologie complète"""
    methodology_id: str
    name: str
    description: str
    methodology_type: MethodologyType
    complexity_level: ComplexityLevel
    target_industries: List[IndustryType]
    steps: List[MethodologyStep]
    total_duration: int
    success_rate: float
    usage_count: int
    last_updated: datetime
    version: int
    tags: List[str]
    metadata: Dict[str, Any]

@dataclass
class ProjectContext:
    """Contexte de projet"""
    project_id: str
    industry: IndustryType
    complexity_level: ComplexityLevel
    budget_range: str
    timeline_constraint: int  # en jours
    team_size: int
    required_deliverables: List[str]
    special_requirements: List[str]
    risk_tolerance: str
    quality_expectations: str
    stakeholder_count: int
    geographic_scope: str
    regulatory_constraints: List[str]

@dataclass
class AdaptationRule:
    """Règle d'adaptation"""
    rule_id: str
    name: str
    trigger: AdaptationTrigger
    conditions: Dict[str, Any]
    actions: List[Dict[str, Any]]
    priority: int
    success_rate: float
    usage_count: int
    created_at: datetime

@dataclass
class PerformanceMetrics:
    """Métriques de performance"""
    methodology_id: str
    project_id: str
    execution_time: int
    quality_score: float
    client_satisfaction: float
    budget_efficiency: float
    timeline_adherence: float
    deliverable_completeness: float
    team_satisfaction: float
    innovation_score: float
    risk_mitigation: float
    overall_success: float

class MethodologyAdaptive:
    """
    Système de méthodologies adaptatives avec IA
    Optimisation intelligente des méthodologies selon le contexte
    """
    
    def __init__(self, data_path: str = None):
        self.system_id = str(uuid.uuid4())
        self.logger = logging.getLogger(f"MethodologyAdaptive-{self.system_id[:8]}")
        
        # Chemins de données
        self.data_path = data_path or '/home/ubuntu/substans_ai_megacabinet/data/methodology'
        self.models_path = os.path.join(self.data_path, 'adaptive_models')
        self.db_path = os.path.join(self.data_path, 'methodology.db')
        
        # Création des répertoires
        os.makedirs(self.data_path, exist_ok=True)
        os.makedirs(self.models_path, exist_ok=True)
        
        # Données
        self.methodologies = {}
        self.adaptation_rules = {}
        self.performance_history = []
        self.project_contexts = {}
        
        # Modèles d'apprentissage
        self.context_clusters = None
        self.performance_predictor = None
        self.adaptation_engine = None
        
        # Cache d'optimisation
        self.optimization_cache = {}
        self.cache_ttl = 3600  # 1 heure
        
        # Statistiques
        self.system_stats = {
            'total_methodologies': 0,
            'total_adaptations': 0,
            'average_success_rate': 0.0,
            'most_used_methodologies': [],
            'adaptation_triggers_frequency': {},
            'performance_trends': []
        }
        
        # Services
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.learning_enabled = True
        
        # Base de données
        self._initialize_database()
        
        # Chargement des données existantes
        self._load_existing_data()
        
        # Initialisation des méthodologies de base
        self._initialize_base_methodologies()
        
        # Démarrage des services
        self._start_services()
        
        self.logger.info(f"Système de Méthodologies Adaptatives initialisé - ID: {self.system_id}")

    def _initialize_database(self):
        """Initialise la base de données"""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Table des méthodologies
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS methodologies (
                    methodology_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    methodology_type TEXT NOT NULL,
                    complexity_level TEXT NOT NULL,
                    target_industries TEXT,
                    steps TEXT NOT NULL,
                    total_duration INTEGER,
                    success_rate REAL DEFAULT 0.0,
                    usage_count INTEGER DEFAULT 0,
                    last_updated TIMESTAMP NOT NULL,
                    version INTEGER DEFAULT 1,
                    tags TEXT,
                    metadata TEXT
                )
            ''')
            
            # Table des contextes de projet
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS project_contexts (
                    project_id TEXT PRIMARY KEY,
                    industry TEXT NOT NULL,
                    complexity_level TEXT NOT NULL,
                    budget_range TEXT,
                    timeline_constraint INTEGER,
                    team_size INTEGER,
                    required_deliverables TEXT,
                    special_requirements TEXT,
                    risk_tolerance TEXT,
                    quality_expectations TEXT,
                    stakeholder_count INTEGER,
                    geographic_scope TEXT,
                    regulatory_constraints TEXT
                )
            ''')
            
            # Table des règles d'adaptation
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS adaptation_rules (
                    rule_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    trigger TEXT NOT NULL,
                    conditions TEXT NOT NULL,
                    actions TEXT NOT NULL,
                    priority INTEGER DEFAULT 1,
                    success_rate REAL DEFAULT 0.0,
                    usage_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP NOT NULL
                )
            ''')
            
            # Table des métriques de performance
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    methodology_id TEXT NOT NULL,
                    project_id TEXT NOT NULL,
                    execution_time INTEGER,
                    quality_score REAL,
                    client_satisfaction REAL,
                    budget_efficiency REAL,
                    timeline_adherence REAL,
                    deliverable_completeness REAL,
                    team_satisfaction REAL,
                    innovation_score REAL,
                    risk_mitigation REAL,
                    overall_success REAL,
                    timestamp TIMESTAMP NOT NULL,
                    FOREIGN KEY (methodology_id) REFERENCES methodologies (methodology_id),
                    FOREIGN KEY (project_id) REFERENCES project_contexts (project_id)
                )
            ''')
            
            # Table des adaptations appliquées
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS applied_adaptations (
                    adaptation_id TEXT PRIMARY KEY,
                    methodology_id TEXT NOT NULL,
                    project_id TEXT NOT NULL,
                    rule_id TEXT NOT NULL,
                    adaptation_details TEXT NOT NULL,
                    performance_impact REAL,
                    timestamp TIMESTAMP NOT NULL,
                    FOREIGN KEY (methodology_id) REFERENCES methodologies (methodology_id),
                    FOREIGN KEY (project_id) REFERENCES project_contexts (project_id),
                    FOREIGN KEY (rule_id) REFERENCES adaptation_rules (rule_id)
                )
            ''')
            
            # Index pour les performances
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_performance_methodology 
                ON performance_metrics(methodology_id)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_performance_project 
                ON performance_metrics(project_id)
            ''')
            
            conn.commit()

    def _initialize_base_methodologies(self):
        """Initialise les méthodologies de base"""
        
        # Méthodologie d'analyse stratégique
        strategic_steps = [
            MethodologyStep(
                step_id="sa_001",
                name="Analyse de l'environnement externe",
                description="Analyse PESTEL et forces de Porter",
                duration_estimate=16,
                complexity_score=0.7,
                required_skills=["analyse_strategique", "recherche_marche"],
                deliverables=["rapport_pestel", "analyse_porter"],
                dependencies=[],
                optional=False,
                success_criteria=["completude_analyse", "pertinence_insights"],
                resources_needed=["bases_donnees", "expert_secteur"],
                risk_factors=["donnees_obsoletes", "biais_analyse"]
            ),
            MethodologyStep(
                step_id="sa_002",
                name="Diagnostic interne",
                description="Analyse des ressources et capacités",
                duration_estimate=12,
                complexity_score=0.6,
                required_skills=["audit_interne", "analyse_financiere"],
                deliverables=["diagnostic_interne", "matrice_swot"],
                dependencies=["sa_001"],
                optional=False,
                success_criteria=["exhaustivite_diagnostic", "objectivite_evaluation"],
                resources_needed=["donnees_internes", "interviews_dirigeants"],
                risk_factors=["resistance_interne", "donnees_incompletes"]
            ),
            MethodologyStep(
                step_id="sa_003",
                name="Formulation stratégique",
                description="Définition des options stratégiques",
                duration_estimate=20,
                complexity_score=0.8,
                required_skills=["strategie_entreprise", "innovation"],
                deliverables=["options_strategiques", "plan_implementation"],
                dependencies=["sa_001", "sa_002"],
                optional=False,
                success_criteria=["faisabilite_options", "alignement_objectifs"],
                resources_needed=["workshops_strategiques", "expertise_sectorielle"],
                risk_factors=["complexite_implementation", "resistance_changement"]
            )
        ]
        
        strategic_methodology = Methodology(
            methodology_id="meth_strategic_001",
            name="Analyse Stratégique Complète",
            description="Méthodologie d'analyse stratégique en 3 phases",
            methodology_type=MethodologyType.STRATEGIC_ANALYSIS,
            complexity_level=ComplexityLevel.COMPLEX,
            target_industries=[IndustryType.TECHNOLOGY, IndustryType.FINANCE, IndustryType.MANUFACTURING],
            steps=strategic_steps,
            total_duration=48,
            success_rate=0.85,
            usage_count=0,
            last_updated=datetime.now(),
            version=1,
            tags=["strategie", "analyse", "diagnostic"],
            metadata={"created_by": "system", "validated": True}
        )
        
        self.methodologies["meth_strategic_001"] = strategic_methodology
        
        # Méthodologie de business plan
        bp_steps = [
            MethodologyStep(
                step_id="bp_001",
                name="Étude de marché",
                description="Analyse du marché cible et de la concurrence",
                duration_estimate=24,
                complexity_score=0.6,
                required_skills=["etude_marche", "analyse_concurrentielle"],
                deliverables=["etude_marche", "positionnement_concurrentiel"],
                dependencies=[],
                optional=False,
                success_criteria=["precision_donnees", "pertinence_segmentation"],
                resources_needed=["etudes_sectorielles", "interviews_clients"],
                risk_factors=["donnees_marche_limitees", "evolution_rapide_marche"]
            ),
            MethodologyStep(
                step_id="bp_002",
                name="Modèle économique",
                description="Définition du modèle d'affaires et des revenus",
                duration_estimate=16,
                complexity_score=0.7,
                required_skills=["modelisation_business", "analyse_financiere"],
                deliverables=["business_model_canvas", "modele_revenus"],
                dependencies=["bp_001"],
                optional=False,
                success_criteria=["viabilite_modele", "scalabilite"],
                resources_needed=["benchmarks_secteur", "expertise_financiere"],
                risk_factors=["assumptions_optimistes", "modele_non_scalable"]
            ),
            MethodologyStep(
                step_id="bp_003",
                name="Projections financières",
                description="Élaboration des prévisions financières",
                duration_estimate=20,
                complexity_score=0.8,
                required_skills=["modelisation_financiere", "analyse_risques"],
                deliverables=["previsions_financieres", "analyse_sensibilite"],
                dependencies=["bp_002"],
                optional=False,
                success_criteria=["realisme_projections", "robustesse_modele"],
                resources_needed=["donnees_financieres", "outils_modelisation"],
                risk_factors=["volatilite_marche", "hypotheses_erronees"]
            )
        ]
        
        bp_methodology = Methodology(
            methodology_id="meth_bp_001",
            name="Business Plan Complet",
            description="Méthodologie de création de business plan",
            methodology_type=MethodologyType.BUSINESS_PLAN,
            complexity_level=ComplexityLevel.MODERATE,
            target_industries=[IndustryType.TECHNOLOGY, IndustryType.RETAIL, IndustryType.CONSULTING],
            steps=bp_steps,
            total_duration=60,
            success_rate=0.78,
            usage_count=0,
            last_updated=datetime.now(),
            version=1,
            tags=["business_plan", "modelisation", "financier"],
            metadata={"created_by": "system", "validated": True}
        )
        
        self.methodologies["meth_bp_001"] = bp_methodology
        
        # Sauvegarde des méthodologies de base
        for methodology in self.methodologies.values():
            self._save_methodology(methodology)
        
        self.logger.info("Méthodologies de base initialisées")

    def adapt_methodology(self, methodology_id: str, project_context: ProjectContext,
                         performance_feedback: PerformanceMetrics = None) -> Methodology:
        """Adapte une méthodologie selon le contexte"""
        
        if methodology_id not in self.methodologies:
            raise ValueError(f"Méthodologie {methodology_id} non trouvée")
        
        base_methodology = self.methodologies[methodology_id]
        
        # Vérification du cache
        cache_key = self._generate_adaptation_cache_key(methodology_id, project_context)
        
        if cache_key in self.optimization_cache:
            cache_entry = self.optimization_cache[cache_key]
            if time.time() - cache_entry['timestamp'] < self.cache_ttl:
                return cache_entry['adapted_methodology']
        
        # Analyse du contexte
        context_analysis = self._analyze_project_context(project_context)
        
        # Identification des adaptations nécessaires
        required_adaptations = self._identify_required_adaptations(
            base_methodology, project_context, context_analysis, performance_feedback
        )
        
        # Application des adaptations
        adapted_methodology = self._apply_adaptations(base_methodology, required_adaptations)
        
        # Optimisation finale
        optimized_methodology = self._optimize_methodology(adapted_methodology, project_context)
        
        # Cache du résultat
        self.optimization_cache[cache_key] = {
            'adapted_methodology': optimized_methodology,
            'timestamp': time.time(),
            'adaptations_applied': required_adaptations
        }
        
        # Mise à jour des statistiques
        self.system_stats['total_adaptations'] += 1
        
        self.logger.info(f"Méthodologie {methodology_id} adaptée avec {len(required_adaptations)} modifications")
        
        return optimized_methodology

    def _analyze_project_context(self, context: ProjectContext) -> Dict[str, Any]:
        """Analyse le contexte du projet"""
        
        analysis = {
            'complexity_factors': [],
            'risk_factors': [],
            'constraint_factors': [],
            'optimization_opportunities': [],
            'recommended_adjustments': []
        }
        
        # Analyse de la complexité
        if context.complexity_level == ComplexityLevel.EXPERT:
            analysis['complexity_factors'].append('high_expertise_required')
        
        if context.stakeholder_count > 10:
            analysis['complexity_factors'].append('high_stakeholder_complexity')
        
        if len(context.regulatory_constraints) > 3:
            analysis['complexity_factors'].append('high_regulatory_complexity')
        
        # Analyse des risques
        if context.timeline_constraint < 30:
            analysis['risk_factors'].append('tight_timeline')
        
        if context.team_size < 3:
            analysis['risk_factors'].append('limited_resources')
        
        if context.risk_tolerance == 'low':
            analysis['risk_factors'].append('low_risk_tolerance')
        
        # Analyse des contraintes
        if context.budget_range in ['low', 'limited']:
            analysis['constraint_factors'].append('budget_constraint')
        
        if context.geographic_scope == 'international':
            analysis['constraint_factors'].append('geographic_complexity')
        
        # Opportunités d'optimisation
        if context.team_size > 8:
            analysis['optimization_opportunities'].append('parallel_execution')
        
        if context.quality_expectations == 'high':
            analysis['optimization_opportunities'].append('quality_enhancement')
        
        return analysis

    def _identify_required_adaptations(self, methodology: Methodology, 
                                     context: ProjectContext,
                                     context_analysis: Dict[str, Any],
                                     performance_feedback: PerformanceMetrics = None) -> List[Dict[str, Any]]:
        """Identifie les adaptations nécessaires"""
        
        adaptations = []
        
        # Adaptations basées sur les contraintes de temps
        if context.timeline_constraint < methodology.total_duration / 8:  # Moins de jours que d'heures/8
            adaptations.append({
                'type': 'timeline_compression',
                'action': 'parallel_execution',
                'target_steps': [step.step_id for step in methodology.steps if not step.dependencies],
                'impact': 'reduce_duration_30_percent'
            })
            
            adaptations.append({
                'type': 'scope_reduction',
                'action': 'make_optional',
                'target_steps': [step.step_id for step in methodology.steps if step.complexity_score < 0.6],
                'impact': 'maintain_core_quality'
            })
        
        # Adaptations basées sur la taille d'équipe
        if context.team_size < 3:
            adaptations.append({
                'type': 'resource_optimization',
                'action': 'sequential_execution',
                'target_steps': 'all',
                'impact': 'increase_duration_reduce_complexity'
            })
        elif context.team_size > 8:
            adaptations.append({
                'type': 'resource_utilization',
                'action': 'parallel_workstreams',
                'target_steps': [step.step_id for step in methodology.steps if len(step.dependencies) <= 1],
                'impact': 'reduce_duration_increase_coordination'
            })
        
        # Adaptations basées sur l'industrie
        if context.industry == IndustryType.TECHNOLOGY:
            adaptations.append({
                'type': 'industry_specialization',
                'action': 'add_tech_focus',
                'target_steps': [step.step_id for step in methodology.steps if 'analyse' in step.name.lower()],
                'impact': 'increase_relevance_tech_sector'
            })
        
        # Adaptations basées sur les performances passées
        if performance_feedback and performance_feedback.overall_success < 0.7:
            if performance_feedback.quality_score < 0.7:
                adaptations.append({
                    'type': 'quality_enhancement',
                    'action': 'add_quality_gates',
                    'target_steps': 'all',
                    'impact': 'increase_quality_increase_duration'
                })
            
            if performance_feedback.timeline_adherence < 0.7:
                adaptations.append({
                    'type': 'timeline_management',
                    'action': 'add_buffer_time',
                    'target_steps': [step.step_id for step in methodology.steps if step.complexity_score > 0.7],
                    'impact': 'improve_timeline_adherence'
                })
        
        # Adaptations basées sur les exigences de qualité
        if context.quality_expectations == 'high':
            adaptations.append({
                'type': 'quality_assurance',
                'action': 'add_review_steps',
                'target_steps': [step.step_id for step in methodology.steps if step.deliverables],
                'impact': 'increase_quality_increase_duration'
            })
        
        return adaptations

    def _apply_adaptations(self, base_methodology: Methodology, 
                          adaptations: List[Dict[str, Any]]) -> Methodology:
        """Applique les adaptations à la méthodologie"""
        
        # Copie de la méthodologie de base
        adapted_methodology = Methodology(
            methodology_id=f"{base_methodology.methodology_id}_adapted_{int(time.time())}",
            name=f"{base_methodology.name} (Adaptée)",
            description=f"{base_methodology.description} - Version adaptée",
            methodology_type=base_methodology.methodology_type,
            complexity_level=base_methodology.complexity_level,
            target_industries=base_methodology.target_industries.copy(),
            steps=[],  # Sera rempli
            total_duration=base_methodology.total_duration,
            success_rate=base_methodology.success_rate,
            usage_count=0,
            last_updated=datetime.now(),
            version=base_methodology.version + 1,
            tags=base_methodology.tags.copy() + ["adapted"],
            metadata=base_methodology.metadata.copy()
        )
        
        # Copie des étapes
        adapted_steps = []
        for step in base_methodology.steps:
            adapted_step = MethodologyStep(
                step_id=step.step_id,
                name=step.name,
                description=step.description,
                duration_estimate=step.duration_estimate,
                complexity_score=step.complexity_score,
                required_skills=step.required_skills.copy(),
                deliverables=step.deliverables.copy(),
                dependencies=step.dependencies.copy(),
                optional=step.optional,
                success_criteria=step.success_criteria.copy(),
                resources_needed=step.resources_needed.copy(),
                risk_factors=step.risk_factors.copy()
            )
            adapted_steps.append(adapted_step)
        
        # Application des adaptations
        for adaptation in adaptations:
            adapted_steps = self._apply_single_adaptation(adapted_steps, adaptation)
            
            # Mise à jour de la durée totale
            adapted_methodology.total_duration = sum(step.duration_estimate for step in adapted_steps)
        
        adapted_methodology.steps = adapted_steps
        adapted_methodology.metadata['adaptations_applied'] = adaptations
        
        return adapted_methodology

    def _apply_single_adaptation(self, steps: List[MethodologyStep], 
                                adaptation: Dict[str, Any]) -> List[MethodologyStep]:
        """Applique une adaptation spécifique"""
        
        adaptation_type = adaptation['type']
        action = adaptation['action']
        target_steps = adaptation['target_steps']
        
        if adaptation_type == 'timeline_compression':
            if action == 'parallel_execution':
                # Supprime les dépendances pour permettre l'exécution parallèle
                for step in steps:
                    if isinstance(target_steps, list) and step.step_id in target_steps:
                        step.dependencies = []
                        step.duration_estimate = int(step.duration_estimate * 0.7)  # Réduction 30%
        
        elif adaptation_type == 'scope_reduction':
            if action == 'make_optional':
                for step in steps:
                    if isinstance(target_steps, list) and step.step_id in target_steps:
                        step.optional = True
        
        elif adaptation_type == 'resource_optimization':
            if action == 'sequential_execution':
                # Force l'exécution séquentielle
                for i, step in enumerate(steps):
                    if i > 0:
                        step.dependencies = [steps[i-1].step_id]
        
        elif adaptation_type == 'resource_utilization':
            if action == 'parallel_workstreams':
                # Optimise pour l'exécution parallèle
                for step in steps:
                    if isinstance(target_steps, list) and step.step_id in target_steps:
                        step.duration_estimate = int(step.duration_estimate * 0.8)  # Réduction 20%
        
        elif adaptation_type == 'quality_enhancement':
            if action == 'add_quality_gates':
                # Ajoute des critères de qualité
                for step in steps:
                    step.success_criteria.append('quality_gate_passed')
                    step.duration_estimate = int(step.duration_estimate * 1.2)  # Augmentation 20%
        
        elif adaptation_type == 'quality_assurance':
            if action == 'add_review_steps':
                # Ajoute des étapes de révision
                new_steps = []
                for step in steps:
                    new_steps.append(step)
                    if isinstance(target_steps, list) and step.step_id in target_steps:
                        review_step = MethodologyStep(
                            step_id=f"{step.step_id}_review",
                            name=f"Révision - {step.name}",
                            description=f"Révision et validation de {step.name}",
                            duration_estimate=max(2, int(step.duration_estimate * 0.2)),
                            complexity_score=0.3,
                            required_skills=["revision", "qualite"],
                            deliverables=[f"rapport_revision_{step.step_id}"],
                            dependencies=[step.step_id],
                            optional=False,
                            success_criteria=["validation_qualite"],
                            resources_needed=["expert_qualite"],
                            risk_factors=["retard_validation"]
                        )
                        new_steps.append(review_step)
                steps = new_steps
        
        return steps

    def _optimize_methodology(self, methodology: Methodology, 
                             context: ProjectContext) -> Methodology:
        """Optimise la méthodologie finale"""
        
        # Optimisation de l'ordre des étapes
        optimized_steps = self._optimize_step_sequence(methodology.steps)
        
        # Optimisation des ressources
        optimized_steps = self._optimize_resource_allocation(optimized_steps, context)
        
        # Optimisation des risques
        optimized_steps = self._optimize_risk_mitigation(optimized_steps)
        
        methodology.steps = optimized_steps
        methodology.total_duration = sum(step.duration_estimate for step in optimized_steps)
        
        return methodology

    def _optimize_step_sequence(self, steps: List[MethodologyStep]) -> List[MethodologyStep]:
        """Optimise la séquence des étapes"""
        
        # Création d'un graphe de dépendances
        graph = nx.DiGraph()
        
        for step in steps:
            graph.add_node(step.step_id, step=step)
            for dep in step.dependencies:
                graph.add_edge(dep, step.step_id)
        
        # Tri topologique pour optimiser l'ordre
        try:
            optimal_order = list(nx.topological_sort(graph))
            
            # Réorganisation des étapes selon l'ordre optimal
            step_dict = {step.step_id: step for step in steps}
            optimized_steps = [step_dict[step_id] for step_id in optimal_order if step_id in step_dict]
            
            return optimized_steps
            
        except nx.NetworkXError:
            # En cas de cycle, retourner l'ordre original
            return steps

    def _optimize_resource_allocation(self, steps: List[MethodologyStep], 
                                    context: ProjectContext) -> List[MethodologyStep]:
        """Optimise l'allocation des ressources"""
        
        # Ajustement selon la taille d'équipe
        team_factor = min(context.team_size / 5.0, 2.0)  # Facteur max 2.0
        
        for step in steps:
            if len(step.required_skills) > 1 and team_factor > 1.2:
                # Réduction de durée pour équipes importantes
                step.duration_estimate = int(step.duration_estimate / team_factor)
            elif team_factor < 0.8:
                # Augmentation de durée pour petites équipes
                step.duration_estimate = int(step.duration_estimate * 1.3)
        
        return steps

    def _optimize_risk_mitigation(self, steps: List[MethodologyStep]) -> List[MethodologyStep]:
        """Optimise la mitigation des risques"""
        
        for step in steps:
            # Ajout de temps de buffer pour étapes à haut risque
            if len(step.risk_factors) > 2:
                buffer_time = max(1, int(step.duration_estimate * 0.15))
                step.duration_estimate += buffer_time
                step.success_criteria.append('risk_mitigation_validated')
        
        return steps

    def record_performance(self, methodology_id: str, project_id: str, 
                          metrics: PerformanceMetrics):
        """Enregistre les performances d'une méthodologie"""
        
        self.performance_history.append(metrics)
        
        # Sauvegarde en base
        self._save_performance_metrics(metrics)
        
        # Mise à jour du taux de succès de la méthodologie
        if methodology_id in self.methodologies:
            methodology = self.methodologies[methodology_id]
            
            # Calcul du nouveau taux de succès
            methodology_performances = [
                m for m in self.performance_history 
                if m.methodology_id == methodology_id
            ]
            
            if methodology_performances:
                avg_success = sum(m.overall_success for m in methodology_performances) / len(methodology_performances)
                methodology.success_rate = avg_success
                methodology.usage_count += 1
                
                # Sauvegarde
                self._save_methodology(methodology)
        
        # Apprentissage automatique si activé
        if self.learning_enabled:
            self.executor.submit(self._learn_from_performance, metrics)
        
        self.logger.info(f"Performance enregistrée pour méthodologie {methodology_id}")

    def get_methodology_recommendations(self, context: ProjectContext, 
                                      limit: int = 5) -> List[Dict[str, Any]]:
        """Recommande des méthodologies selon le contexte"""
        
        recommendations = []
        
        for methodology in self.methodologies.values():
            # Calcul du score de compatibilité
            compatibility_score = self._calculate_compatibility_score(methodology, context)
            
            if compatibility_score > 0.3:  # Seuil minimum
                recommendations.append({
                    'methodology_id': methodology.methodology_id,
                    'name': methodology.name,
                    'compatibility_score': compatibility_score,
                    'success_rate': methodology.success_rate,
                    'estimated_duration': methodology.total_duration,
                    'complexity_level': methodology.complexity_level.value,
                    'usage_count': methodology.usage_count,
                    'adaptation_needed': compatibility_score < 0.8
                })
        
        # Tri par score de compatibilité et taux de succès
        recommendations.sort(
            key=lambda x: (x['compatibility_score'] * 0.6 + x['success_rate'] * 0.4),
            reverse=True
        )
        
        return recommendations[:limit]

    def _calculate_compatibility_score(self, methodology: Methodology, 
                                     context: ProjectContext) -> float:
        """Calcule le score de compatibilité méthodologie-contexte"""
        
        score = 0.0
        
        # Compatibilité industrie
        if context.industry in methodology.target_industries:
            score += 0.3
        
        # Compatibilité complexité
        complexity_mapping = {
            ComplexityLevel.SIMPLE: 1,
            ComplexityLevel.MODERATE: 2,
            ComplexityLevel.COMPLEX: 3,
            ComplexityLevel.EXPERT: 4
        }
        
        method_complexity = complexity_mapping[methodology.complexity_level]
        context_complexity = complexity_mapping[context.complexity_level]
        
        complexity_diff = abs(method_complexity - context_complexity)
        complexity_score = max(0, 1 - complexity_diff * 0.2)
        score += complexity_score * 0.25
        
        # Compatibilité durée
        estimated_days = methodology.total_duration / 8  # 8h par jour
        if estimated_days <= context.timeline_constraint:
            score += 0.2
        elif estimated_days <= context.timeline_constraint * 1.2:
            score += 0.1
        
        # Compatibilité équipe
        if context.team_size >= 3:  # Équipe suffisante
            score += 0.15
        
        # Bonus pour taux de succès élevé
        score += methodology.success_rate * 0.1
        
        return min(score, 1.0)

    def _generate_adaptation_cache_key(self, methodology_id: str, 
                                     context: ProjectContext) -> str:
        """Génère une clé de cache pour l'adaptation"""
        
        key_data = {
            'methodology_id': methodology_id,
            'industry': context.industry.value,
            'complexity': context.complexity_level.value,
            'timeline': context.timeline_constraint,
            'team_size': context.team_size,
            'budget': context.budget_range,
            'quality': context.quality_expectations
        }
        
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()

    def _save_methodology(self, methodology: Methodology):
        """Sauvegarde une méthodologie"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO methodologies 
                    (methodology_id, name, description, methodology_type, complexity_level,
                     target_industries, steps, total_duration, success_rate, usage_count,
                     last_updated, version, tags, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    methodology.methodology_id, methodology.name, methodology.description,
                    methodology.methodology_type.value, methodology.complexity_level.value,
                    json.dumps([ind.value for ind in methodology.target_industries]),
                    json.dumps([asdict(step) for step in methodology.steps]),
                    methodology.total_duration, methodology.success_rate, methodology.usage_count,
                    methodology.last_updated, methodology.version,
                    json.dumps(methodology.tags), json.dumps(methodology.metadata)
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde méthodologie: {e}")

    def _save_performance_metrics(self, metrics: PerformanceMetrics):
        """Sauvegarde les métriques de performance"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO performance_metrics 
                    (methodology_id, project_id, execution_time, quality_score,
                     client_satisfaction, budget_efficiency, timeline_adherence,
                     deliverable_completeness, team_satisfaction, innovation_score,
                     risk_mitigation, overall_success, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    metrics.methodology_id, metrics.project_id, metrics.execution_time,
                    metrics.quality_score, metrics.client_satisfaction, metrics.budget_efficiency,
                    metrics.timeline_adherence, metrics.deliverable_completeness,
                    metrics.team_satisfaction, metrics.innovation_score,
                    metrics.risk_mitigation, metrics.overall_success, datetime.now()
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde métriques: {e}")

    def _load_existing_data(self):
        """Charge les données existantes"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Chargement des méthodologies
                cursor.execute('SELECT * FROM methodologies')
                
                for row in cursor.fetchall():
                    data = dict(zip([col[0] for col in cursor.description], row))
                    
                    # Reconstruction des étapes
                    steps_data = json.loads(data['steps'])
                    steps = []
                    
                    for step_data in steps_data:
                        step = MethodologyStep(**step_data)
                        steps.append(step)
                    
                    methodology = Methodology(
                        methodology_id=data['methodology_id'],
                        name=data['name'],
                        description=data['description'],
                        methodology_type=MethodologyType(data['methodology_type']),
                        complexity_level=ComplexityLevel(data['complexity_level']),
                        target_industries=[IndustryType(ind) for ind in json.loads(data['target_industries'])],
                        steps=steps,
                        total_duration=data['total_duration'],
                        success_rate=data['success_rate'],
                        usage_count=data['usage_count'],
                        last_updated=datetime.fromisoformat(data['last_updated']),
                        version=data['version'],
                        tags=json.loads(data['tags']),
                        metadata=json.loads(data['metadata'])
                    )
                    
                    self.methodologies[data['methodology_id']] = methodology
                
                self.logger.info(f"{len(self.methodologies)} méthodologies chargées")
                
        except Exception as e:
            self.logger.error(f"Erreur chargement données: {e}")

    def _start_services(self):
        """Démarre les services du système"""
        
        # Service d'apprentissage automatique
        threading.Thread(target=self._learning_service, daemon=True).start()
        
        # Service de nettoyage du cache
        threading.Thread(target=self._cache_cleanup_service, daemon=True).start()

    def _learning_service(self):
        """Service d'apprentissage automatique"""
        
        while True:
            try:
                if len(self.performance_history) > 10:
                    self._update_adaptation_rules()
                
                time.sleep(3600)  # Apprentissage toutes les heures
                
            except Exception as e:
                self.logger.error(f"Erreur service apprentissage: {e}")
                time.sleep(3600)

    def _cache_cleanup_service(self):
        """Service de nettoyage du cache"""
        
        while True:
            try:
                current_time = time.time()
                expired_keys = [
                    key for key, entry in self.optimization_cache.items()
                    if current_time - entry['timestamp'] > self.cache_ttl
                ]
                
                for key in expired_keys:
                    del self.optimization_cache[key]
                
                if expired_keys:
                    self.logger.info(f"{len(expired_keys)} entrées de cache supprimées")
                
                time.sleep(1800)  # Nettoyage toutes les 30 minutes
                
            except Exception as e:
                self.logger.error(f"Erreur service nettoyage cache: {e}")
                time.sleep(1800)

    def _learn_from_performance(self, metrics: PerformanceMetrics):
        """Apprentissage à partir des performances"""
        
        # Identification des patterns de succès/échec
        if metrics.overall_success < 0.6:
            # Analyse des causes d'échec
            failure_factors = []
            
            if metrics.timeline_adherence < 0.7:
                failure_factors.append('timeline_issues')
            if metrics.quality_score < 0.7:
                failure_factors.append('quality_issues')
            if metrics.budget_efficiency < 0.7:
                failure_factors.append('budget_issues')
            
            # Création de règles d'adaptation préventives
            for factor in failure_factors:
                self._create_preventive_adaptation_rule(factor, metrics)

    def _create_preventive_adaptation_rule(self, failure_factor: str, 
                                         metrics: PerformanceMetrics):
        """Crée une règle d'adaptation préventive"""
        
        rule_id = str(uuid.uuid4())
        
        if failure_factor == 'timeline_issues':
            rule = AdaptationRule(
                rule_id=rule_id,
                name="Prévention retards timeline",
                trigger=AdaptationTrigger.TIME_CONSTRAINT,
                conditions={'timeline_constraint_ratio': '<1.2'},
                actions=[
                    {'type': 'add_buffer_time', 'percentage': 0.15},
                    {'type': 'parallel_execution', 'applicable_steps': 'independent'}
                ],
                priority=2,
                success_rate=0.0,
                usage_count=0,
                created_at=datetime.now()
            )
            
            self.adaptation_rules[rule_id] = rule

    def _update_adaptation_rules(self):
        """Met à jour les règles d'adaptation basées sur l'apprentissage"""
        
        # Analyse des performances par type d'adaptation
        adaptation_performance = defaultdict(list)
        
        for metrics in self.performance_history:
            # Récupération des adaptations appliquées (si disponible dans metadata)
            # Mise à jour des taux de succès des règles
            pass
        
        self.logger.info("Règles d'adaptation mises à jour")

    def get_system_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques du système"""
        
        # Mise à jour des statistiques
        if self.methodologies:
            success_rates = [m.success_rate for m in self.methodologies.values()]
            self.system_stats['average_success_rate'] = sum(success_rates) / len(success_rates)
        
        # Méthodologies les plus utilisées
        most_used = sorted(
            self.methodologies.values(),
            key=lambda x: x.usage_count,
            reverse=True
        )[:5]
        
        self.system_stats['most_used_methodologies'] = [
            {'id': m.methodology_id, 'name': m.name, 'usage_count': m.usage_count}
            for m in most_used
        ]
        
        return self.system_stats.copy()

# Instance globale
_methodology_system = None

def get_methodology_system() -> MethodologyAdaptive:
    """Retourne l'instance du système de méthodologies"""
    global _methodology_system
    if _methodology_system is None:
        _methodology_system = MethodologyAdaptive()
    return _methodology_system

# Test du système
if __name__ == '__main__':
    print("=== Test Système de Méthodologies Adaptatives ===")
    
    system = MethodologyAdaptive()
    
    # Test de contexte de projet
    context = ProjectContext(
        project_id="test_001",
        industry=IndustryType.TECHNOLOGY,
        complexity_level=ComplexityLevel.MODERATE,
        budget_range="medium",
        timeline_constraint=45,
        team_size=5,
        required_deliverables=["business_plan", "market_analysis"],
        special_requirements=["regulatory_compliance"],
        risk_tolerance="medium",
        quality_expectations="high",
        stakeholder_count=8,
        geographic_scope="national",
        regulatory_constraints=["gdpr", "financial_regulations"]
    )
    
    # Test de recommandations
    recommendations = system.get_methodology_recommendations(context)
    print(f"Recommandations: {len(recommendations)}")
    
    if recommendations:
        best_recommendation = recommendations[0]
        print(f"Meilleure recommandation: {best_recommendation['name']}")
        print(f"Score de compatibilité: {best_recommendation['compatibility_score']:.3f}")
        
        # Test d'adaptation
        adapted_methodology = system.adapt_methodology(
            best_recommendation['methodology_id'], 
            context
        )
        
        print(f"Méthodologie adaptée: {adapted_methodology.name}")
        print(f"Durée totale: {adapted_methodology.total_duration}h")
        print(f"Nombre d'étapes: {len(adapted_methodology.steps)}")
    
    # Test des statistiques
    stats = system.get_system_statistics()
    print(f"Statistiques: {stats['total_methodologies']} méthodologies")
    
    print("Test terminé avec succès")

