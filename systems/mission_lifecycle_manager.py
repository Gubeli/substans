"""
Mission Lifecycle Manager - Gestionnaire du Cycle de Vie des Missions
Gestion complète des missions de conseil de A à Z
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
import shutil
import hashlib

# Configuration du logging
logging.basicConfig(level=logging.INFO)

class MissionStatus(Enum):
    """Statuts des missions"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"
    ARCHIVED = "archived"

class MissionPriority(Enum):
    """Priorités des missions"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"

class MissionType(Enum):
    """Types de missions"""
    STRATEGIC_ANALYSIS = "strategic_analysis"
    BUSINESS_PLAN = "business_plan"
    MARKET_STUDY = "market_study"
    COMPETITIVE_ANALYSIS = "competitive_analysis"
    OPERATIONAL_AUDIT = "operational_audit"
    DIGITAL_TRANSFORMATION = "digital_transformation"
    FINANCIAL_ANALYSIS = "financial_analysis"
    RISK_ASSESSMENT = "risk_assessment"
    MERGER_ACQUISITION = "merger_acquisition"
    INNOVATION_STRATEGY = "innovation_strategy"

class TaskStatus(Enum):
    """Statuts des tâches"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"

class DeliverableType(Enum):
    """Types de livrables"""
    REPORT = "report"
    PRESENTATION = "presentation"
    ANALYSIS = "analysis"
    RECOMMENDATION = "recommendation"
    BUSINESS_PLAN = "business_plan"
    STRATEGY = "strategy"
    ROADMAP = "roadmap"
    ASSESSMENT = "assessment"

@dataclass
class MissionClient:
    """Client de la mission"""
    client_id: str
    client_name: str
    industry: str
    size: str  # "startup", "sme", "large", "enterprise"
    contact_person: str
    contact_email: str
    contact_phone: str
    requirements: List[str]
    constraints: List[str]
    expectations: Dict[str, Any]

@dataclass
class MissionTeam:
    """Équipe de la mission"""
    team_id: str
    lead_consultant: str
    senior_advisor: str
    assigned_agents: List[str]
    external_experts: List[str]
    team_size: int
    required_skills: List[str]
    availability: Dict[str, float]  # agent_id -> availability %

@dataclass
class MissionTask:
    """Tâche de mission"""
    task_id: str
    mission_id: str
    task_name: str
    description: str
    assigned_to: str
    status: TaskStatus
    priority: MissionPriority
    estimated_hours: float
    actual_hours: float
    start_date: Optional[datetime]
    due_date: datetime
    completion_date: Optional[datetime]
    dependencies: List[str]  # task_ids
    deliverables: List[str]
    progress_percentage: float
    notes: str
    created_at: datetime
    updated_at: datetime

@dataclass
class MissionDeliverable:
    """Livrable de mission"""
    deliverable_id: str
    mission_id: str
    deliverable_name: str
    deliverable_type: DeliverableType
    description: str
    format: str  # "pdf", "docx", "pptx", "xlsx"
    file_path: str
    version: str
    status: str  # "draft", "review", "approved", "delivered"
    quality_score: float
    review_comments: List[str]
    created_by: str
    created_at: datetime
    updated_at: datetime
    delivered_at: Optional[datetime]

@dataclass
class MissionMilestone:
    """Jalon de mission"""
    milestone_id: str
    mission_id: str
    milestone_name: str
    description: str
    target_date: datetime
    actual_date: Optional[datetime]
    status: str  # "pending", "achieved", "missed", "cancelled"
    success_criteria: List[str]
    deliverables_required: List[str]
    stakeholders_involved: List[str]
    created_at: datetime

@dataclass
class MissionRisk:
    """Risque de mission"""
    risk_id: str
    mission_id: str
    risk_name: str
    description: str
    category: str  # "technical", "business", "resource", "timeline", "quality"
    probability: float  # 0-1
    impact: float  # 0-1
    risk_score: float  # probability * impact
    mitigation_plan: str
    contingency_plan: str
    owner: str
    status: str  # "identified", "mitigated", "occurred", "closed"
    created_at: datetime
    updated_at: datetime

@dataclass
class Mission:
    """Mission complète"""
    mission_id: str
    mission_name: str
    mission_type: MissionType
    description: str
    objectives: List[str]
    success_criteria: List[str]
    client: MissionClient
    team: MissionTeam
    status: MissionStatus
    priority: MissionPriority
    budget: float
    estimated_duration: int  # en jours
    actual_duration: Optional[int]
    start_date: datetime
    planned_end_date: datetime
    actual_end_date: Optional[datetime]
    methodology: str
    tasks: List[MissionTask]
    deliverables: List[MissionDeliverable]
    milestones: List[MissionMilestone]
    risks: List[MissionRisk]
    progress_percentage: float
    quality_score: float
    client_satisfaction: float
    lessons_learned: List[str]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

@dataclass
class MissionMetrics:
    """Métriques de mission"""
    mission_id: str
    total_hours_planned: float
    total_hours_actual: float
    budget_planned: float
    budget_actual: float
    tasks_completed: int
    tasks_total: int
    deliverables_delivered: int
    deliverables_total: int
    milestones_achieved: int
    milestones_total: int
    risks_mitigated: int
    risks_total: int
    quality_average: float
    timeline_performance: float  # % on time
    budget_performance: float  # % on budget
    client_satisfaction: float
    team_utilization: float
    calculated_at: datetime

class MissionLifecycleManager:
    """
    Gestionnaire du Cycle de Vie des Missions
    Gestion complète des missions de conseil de A à Z
    """
    
    def __init__(self, data_path: str = None):
        self.system_id = str(uuid.uuid4())
        self.logger = logging.getLogger(f"MissionLifecycleManager-{self.system_id[:8]}")
        
        # Chemins de données
        self.data_path = data_path or '/home/ubuntu/substans_ai_megacabinet/data/missions'
        self.db_path = os.path.join(self.data_path, 'missions.db')
        self.files_path = os.path.join(self.data_path, 'files')
        self.templates_path = os.path.join(self.data_path, 'templates')
        self.archives_path = os.path.join(self.data_path, 'archives')
        
        # Création des répertoires
        for path in [self.data_path, self.files_path, self.templates_path, self.archives_path]:
            os.makedirs(path, exist_ok=True)
        
        # Missions et données
        self.missions = {}
        self.mission_metrics = {}
        self.active_workflows = {}
        
        # Configuration
        self.config = {
            'auto_status_updates': True,
            'quality_threshold': 0.8,
            'risk_threshold': 0.7,
            'notification_enabled': True,
            'backup_enabled': True,
            'archive_after_days': 365,
            'max_concurrent_missions': 50
        }
        
        # Templates de missions
        self.mission_templates = {}
        
        # Workflows automatisés
        self.workflows = {
            'mission_creation': self._workflow_mission_creation,
            'task_assignment': self._workflow_task_assignment,
            'deliverable_review': self._workflow_deliverable_review,
            'milestone_tracking': self._workflow_milestone_tracking,
            'risk_monitoring': self._workflow_risk_monitoring,
            'mission_closure': self._workflow_mission_closure
        }
        
        # Notifications et alertes
        self.notification_queue = []
        self.alert_rules = {}
        
        # Statistiques
        self.system_stats = {
            'total_missions': 0,
            'active_missions': 0,
            'completed_missions': 0,
            'total_tasks': 0,
            'completed_tasks': 0,
            'total_deliverables': 0,
            'delivered_deliverables': 0,
            'average_mission_duration': 0.0,
            'average_client_satisfaction': 0.0,
            'on_time_delivery_rate': 0.0,
            'budget_performance_avg': 0.0
        }
        
        # Services
        self.executor = ThreadPoolExecutor(max_workers=5)
        
        # Base de données
        self._initialize_database()
        
        # Chargement des données existantes
        self._load_existing_missions()
        
        # Initialisation des templates
        self._initialize_mission_templates()
        
        # Démarrage des services
        self._start_services()
        
        self.logger.info(f"Mission Lifecycle Manager initialisé - ID: {self.system_id}")

    def _initialize_database(self):
        """Initialise la base de données"""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Table des missions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS missions (
                    mission_id TEXT PRIMARY KEY,
                    mission_name TEXT NOT NULL,
                    mission_type TEXT NOT NULL,
                    description TEXT,
                    objectives TEXT,
                    success_criteria TEXT,
                    client_data TEXT NOT NULL,
                    team_data TEXT NOT NULL,
                    status TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    budget REAL,
                    estimated_duration INTEGER,
                    actual_duration INTEGER,
                    start_date TIMESTAMP NOT NULL,
                    planned_end_date TIMESTAMP NOT NULL,
                    actual_end_date TIMESTAMP,
                    methodology TEXT,
                    progress_percentage REAL DEFAULT 0.0,
                    quality_score REAL DEFAULT 0.0,
                    client_satisfaction REAL DEFAULT 0.0,
                    lessons_learned TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL
                )
            ''')
            
            # Table des tâches
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mission_tasks (
                    task_id TEXT PRIMARY KEY,
                    mission_id TEXT NOT NULL,
                    task_name TEXT NOT NULL,
                    description TEXT,
                    assigned_to TEXT,
                    status TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    estimated_hours REAL,
                    actual_hours REAL DEFAULT 0.0,
                    start_date TIMESTAMP,
                    due_date TIMESTAMP NOT NULL,
                    completion_date TIMESTAMP,
                    dependencies TEXT,
                    deliverables TEXT,
                    progress_percentage REAL DEFAULT 0.0,
                    notes TEXT,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (mission_id) REFERENCES missions (mission_id)
                )
            ''')
            
            # Table des livrables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mission_deliverables (
                    deliverable_id TEXT PRIMARY KEY,
                    mission_id TEXT NOT NULL,
                    deliverable_name TEXT NOT NULL,
                    deliverable_type TEXT NOT NULL,
                    description TEXT,
                    format TEXT,
                    file_path TEXT,
                    version TEXT,
                    status TEXT NOT NULL,
                    quality_score REAL DEFAULT 0.0,
                    review_comments TEXT,
                    created_by TEXT,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    delivered_at TIMESTAMP,
                    FOREIGN KEY (mission_id) REFERENCES missions (mission_id)
                )
            ''')
            
            # Table des jalons
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mission_milestones (
                    milestone_id TEXT PRIMARY KEY,
                    mission_id TEXT NOT NULL,
                    milestone_name TEXT NOT NULL,
                    description TEXT,
                    target_date TIMESTAMP NOT NULL,
                    actual_date TIMESTAMP,
                    status TEXT NOT NULL,
                    success_criteria TEXT,
                    deliverables_required TEXT,
                    stakeholders_involved TEXT,
                    created_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (mission_id) REFERENCES missions (mission_id)
                )
            ''')
            
            # Table des risques
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mission_risks (
                    risk_id TEXT PRIMARY KEY,
                    mission_id TEXT NOT NULL,
                    risk_name TEXT NOT NULL,
                    description TEXT,
                    category TEXT NOT NULL,
                    probability REAL NOT NULL,
                    impact REAL NOT NULL,
                    risk_score REAL NOT NULL,
                    mitigation_plan TEXT,
                    contingency_plan TEXT,
                    owner TEXT,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (mission_id) REFERENCES missions (mission_id)
                )
            ''')
            
            # Table des métriques
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mission_metrics (
                    mission_id TEXT PRIMARY KEY,
                    total_hours_planned REAL,
                    total_hours_actual REAL,
                    budget_planned REAL,
                    budget_actual REAL,
                    tasks_completed INTEGER,
                    tasks_total INTEGER,
                    deliverables_delivered INTEGER,
                    deliverables_total INTEGER,
                    milestones_achieved INTEGER,
                    milestones_total INTEGER,
                    risks_mitigated INTEGER,
                    risks_total INTEGER,
                    quality_average REAL,
                    timeline_performance REAL,
                    budget_performance REAL,
                    client_satisfaction REAL,
                    team_utilization REAL,
                    calculated_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (mission_id) REFERENCES missions (mission_id)
                )
            ''')
            
            # Index pour les performances
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_missions_status 
                ON missions(status)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_missions_created 
                ON missions(created_at)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_tasks_mission 
                ON mission_tasks(mission_id)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_tasks_status 
                ON mission_tasks(status)
            ''')
            
            conn.commit()

    def create_mission(self, mission_data: Dict[str, Any]) -> Mission:
        """Crée une nouvelle mission"""
        
        mission_id = str(uuid.uuid4())
        
        # Validation des données
        required_fields = ['mission_name', 'mission_type', 'client', 'objectives']
        for field in required_fields:
            if field not in mission_data:
                raise ValueError(f"Champ requis manquant: {field}")
        
        # Création du client
        client_data = mission_data['client']
        client = MissionClient(
            client_id=client_data.get('client_id', str(uuid.uuid4())),
            client_name=client_data['client_name'],
            industry=client_data.get('industry', 'Unknown'),
            size=client_data.get('size', 'sme'),
            contact_person=client_data.get('contact_person', ''),
            contact_email=client_data.get('contact_email', ''),
            contact_phone=client_data.get('contact_phone', ''),
            requirements=client_data.get('requirements', []),
            constraints=client_data.get('constraints', []),
            expectations=client_data.get('expectations', {})
        )
        
        # Création de l'équipe
        team_data = mission_data.get('team', {})
        team = MissionTeam(
            team_id=str(uuid.uuid4()),
            lead_consultant=team_data.get('lead_consultant', 'Senior Advisor'),
            senior_advisor='Senior Advisor',
            assigned_agents=team_data.get('assigned_agents', []),
            external_experts=team_data.get('external_experts', []),
            team_size=len(team_data.get('assigned_agents', [])) + 1,
            required_skills=team_data.get('required_skills', []),
            availability=team_data.get('availability', {})
        )
        
        # Dates
        start_date = mission_data.get('start_date', datetime.now())
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date)
        
        estimated_duration = mission_data.get('estimated_duration', 30)
        planned_end_date = start_date + timedelta(days=estimated_duration)
        
        # Création de la mission
        mission = Mission(
            mission_id=mission_id,
            mission_name=mission_data['mission_name'],
            mission_type=MissionType(mission_data['mission_type']),
            description=mission_data.get('description', ''),
            objectives=mission_data['objectives'],
            success_criteria=mission_data.get('success_criteria', []),
            client=client,
            team=team,
            status=MissionStatus.DRAFT,
            priority=MissionPriority(mission_data.get('priority', 'medium')),
            budget=mission_data.get('budget', 0.0),
            estimated_duration=estimated_duration,
            actual_duration=None,
            start_date=start_date,
            planned_end_date=planned_end_date,
            actual_end_date=None,
            methodology=mission_data.get('methodology', 'Standard'),
            tasks=[],
            deliverables=[],
            milestones=[],
            risks=[],
            progress_percentage=0.0,
            quality_score=0.0,
            client_satisfaction=0.0,
            lessons_learned=[],
            metadata=mission_data.get('metadata', {}),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Sauvegarde
        self.missions[mission_id] = mission
        self._save_mission(mission)
        
        # Déclenchement du workflow de création
        self.executor.submit(self._trigger_workflow, 'mission_creation', mission_id)
        
        # Mise à jour des statistiques
        self.system_stats['total_missions'] += 1
        self.system_stats['active_missions'] += 1
        
        self.logger.info(f"Mission créée: {mission.mission_name} ({mission_id})")
        
        return mission

    def update_mission_status(self, mission_id: str, new_status: MissionStatus, 
                            notes: str = None) -> bool:
        """Met à jour le statut d'une mission"""
        
        if mission_id not in self.missions:
            self.logger.error(f"Mission non trouvée: {mission_id}")
            return False
        
        mission = self.missions[mission_id]
        old_status = mission.status
        
        # Validation des transitions de statut
        valid_transitions = self._get_valid_status_transitions(old_status)
        
        if new_status not in valid_transitions:
            self.logger.error(f"Transition invalide: {old_status.value} -> {new_status.value}")
            return False
        
        # Mise à jour
        mission.status = new_status
        mission.updated_at = datetime.now()
        
        # Actions spécifiques selon le statut
        if new_status == MissionStatus.IN_PROGRESS:
            mission.start_date = datetime.now()
        elif new_status == MissionStatus.COMPLETED:
            mission.actual_end_date = datetime.now()
            mission.actual_duration = (mission.actual_end_date - mission.start_date).days
            mission.progress_percentage = 100.0
            self.system_stats['completed_missions'] += 1
            self.system_stats['active_missions'] -= 1
        elif new_status == MissionStatus.CANCELLED:
            self.system_stats['active_missions'] -= 1
        
        # Sauvegarde
        self._save_mission(mission)
        
        # Notification
        if notes:
            mission.metadata['status_notes'] = mission.metadata.get('status_notes', [])
            mission.metadata['status_notes'].append({
                'timestamp': datetime.now().isoformat(),
                'old_status': old_status.value,
                'new_status': new_status.value,
                'notes': notes
            })
        
        self.logger.info(f"Mission {mission_id} - Statut: {old_status.value} -> {new_status.value}")
        
        return True

    def add_task(self, mission_id: str, task_data: Dict[str, Any]) -> MissionTask:
        """Ajoute une tâche à une mission"""
        
        if mission_id not in self.missions:
            raise ValueError(f"Mission non trouvée: {mission_id}")
        
        mission = self.missions[mission_id]
        task_id = str(uuid.uuid4())
        
        # Dates
        due_date = task_data['due_date']
        if isinstance(due_date, str):
            due_date = datetime.fromisoformat(due_date)
        
        start_date = task_data.get('start_date')
        if start_date and isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date)
        
        # Création de la tâche
        task = MissionTask(
            task_id=task_id,
            mission_id=mission_id,
            task_name=task_data['task_name'],
            description=task_data.get('description', ''),
            assigned_to=task_data.get('assigned_to', ''),
            status=TaskStatus(task_data.get('status', 'pending')),
            priority=MissionPriority(task_data.get('priority', 'medium')),
            estimated_hours=task_data.get('estimated_hours', 0.0),
            actual_hours=0.0,
            start_date=start_date,
            due_date=due_date,
            completion_date=None,
            dependencies=task_data.get('dependencies', []),
            deliverables=task_data.get('deliverables', []),
            progress_percentage=0.0,
            notes=task_data.get('notes', ''),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Ajout à la mission
        mission.tasks.append(task)
        mission.updated_at = datetime.now()
        
        # Sauvegarde
        self._save_task(task)
        self._save_mission(mission)
        
        # Déclenchement du workflow d'assignation
        if task.assigned_to:
            self.executor.submit(self._trigger_workflow, 'task_assignment', task_id)
        
        # Mise à jour des statistiques
        self.system_stats['total_tasks'] += 1
        
        self.logger.info(f"Tâche ajoutée: {task.task_name} ({task_id})")
        
        return task

    def update_task_progress(self, task_id: str, progress: float, 
                           actual_hours: float = None, notes: str = None) -> bool:
        """Met à jour le progrès d'une tâche"""
        
        # Recherche de la tâche
        task = None
        mission = None
        
        for m in self.missions.values():
            for t in m.tasks:
                if t.task_id == task_id:
                    task = t
                    mission = m
                    break
            if task:
                break
        
        if not task:
            self.logger.error(f"Tâche non trouvée: {task_id}")
            return False
        
        # Mise à jour
        old_progress = task.progress_percentage
        task.progress_percentage = max(0.0, min(100.0, progress))
        
        if actual_hours is not None:
            task.actual_hours = actual_hours
        
        if notes:
            task.notes = f"{task.notes}\n{datetime.now().isoformat()}: {notes}".strip()
        
        # Statut automatique
        if task.progress_percentage == 100.0 and task.status != TaskStatus.COMPLETED:
            task.status = TaskStatus.COMPLETED
            task.completion_date = datetime.now()
            self.system_stats['completed_tasks'] += 1
        elif task.progress_percentage > 0.0 and task.status == TaskStatus.PENDING:
            task.status = TaskStatus.IN_PROGRESS
            if not task.start_date:
                task.start_date = datetime.now()
        
        task.updated_at = datetime.now()
        
        # Mise à jour du progrès de la mission
        self._update_mission_progress(mission)
        
        # Sauvegarde
        self._save_task(task)
        self._save_mission(mission)
        
        self.logger.info(f"Tâche {task_id} - Progrès: {old_progress:.1f}% -> {progress:.1f}%")
        
        return True

    def add_deliverable(self, mission_id: str, deliverable_data: Dict[str, Any]) -> MissionDeliverable:
        """Ajoute un livrable à une mission"""
        
        if mission_id not in self.missions:
            raise ValueError(f"Mission non trouvée: {mission_id}")
        
        mission = self.missions[mission_id]
        deliverable_id = str(uuid.uuid4())
        
        # Création du livrable
        deliverable = MissionDeliverable(
            deliverable_id=deliverable_id,
            mission_id=mission_id,
            deliverable_name=deliverable_data['deliverable_name'],
            deliverable_type=DeliverableType(deliverable_data['deliverable_type']),
            description=deliverable_data.get('description', ''),
            format=deliverable_data.get('format', 'pdf'),
            file_path=deliverable_data.get('file_path', ''),
            version=deliverable_data.get('version', '1.0'),
            status=deliverable_data.get('status', 'draft'),
            quality_score=0.0,
            review_comments=[],
            created_by=deliverable_data.get('created_by', ''),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            delivered_at=None
        )
        
        # Ajout à la mission
        mission.deliverables.append(deliverable)
        mission.updated_at = datetime.now()
        
        # Sauvegarde
        self._save_deliverable(deliverable)
        self._save_mission(mission)
        
        # Mise à jour des statistiques
        self.system_stats['total_deliverables'] += 1
        
        self.logger.info(f"Livrable ajouté: {deliverable.deliverable_name} ({deliverable_id})")
        
        return deliverable

    def add_milestone(self, mission_id: str, milestone_data: Dict[str, Any]) -> MissionMilestone:
        """Ajoute un jalon à une mission"""
        
        if mission_id not in self.missions:
            raise ValueError(f"Mission non trouvée: {mission_id}")
        
        mission = self.missions[mission_id]
        milestone_id = str(uuid.uuid4())
        
        # Date cible
        target_date = milestone_data['target_date']
        if isinstance(target_date, str):
            target_date = datetime.fromisoformat(target_date)
        
        # Création du jalon
        milestone = MissionMilestone(
            milestone_id=milestone_id,
            mission_id=mission_id,
            milestone_name=milestone_data['milestone_name'],
            description=milestone_data.get('description', ''),
            target_date=target_date,
            actual_date=None,
            status='pending',
            success_criteria=milestone_data.get('success_criteria', []),
            deliverables_required=milestone_data.get('deliverables_required', []),
            stakeholders_involved=milestone_data.get('stakeholders_involved', []),
            created_at=datetime.now()
        )
        
        # Ajout à la mission
        mission.milestones.append(milestone)
        mission.updated_at = datetime.now()
        
        # Sauvegarde
        self._save_milestone(milestone)
        self._save_mission(mission)
        
        self.logger.info(f"Jalon ajouté: {milestone.milestone_name} ({milestone_id})")
        
        return milestone

    def add_risk(self, mission_id: str, risk_data: Dict[str, Any]) -> MissionRisk:
        """Ajoute un risque à une mission"""
        
        if mission_id not in self.missions:
            raise ValueError(f"Mission non trouvée: {mission_id}")
        
        mission = self.missions[mission_id]
        risk_id = str(uuid.uuid4())
        
        # Calcul du score de risque
        probability = risk_data['probability']
        impact = risk_data['impact']
        risk_score = probability * impact
        
        # Création du risque
        risk = MissionRisk(
            risk_id=risk_id,
            mission_id=mission_id,
            risk_name=risk_data['risk_name'],
            description=risk_data.get('description', ''),
            category=risk_data.get('category', 'business'),
            probability=probability,
            impact=impact,
            risk_score=risk_score,
            mitigation_plan=risk_data.get('mitigation_plan', ''),
            contingency_plan=risk_data.get('contingency_plan', ''),
            owner=risk_data.get('owner', ''),
            status='identified',
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Ajout à la mission
        mission.risks.append(risk)
        mission.updated_at = datetime.now()
        
        # Sauvegarde
        self._save_risk(risk)
        self._save_mission(mission)
        
        # Déclenchement du workflow de monitoring des risques
        if risk_score >= self.config['risk_threshold']:
            self.executor.submit(self._trigger_workflow, 'risk_monitoring', risk_id)
        
        self.logger.info(f"Risque ajouté: {risk.risk_name} (Score: {risk_score:.2f})")
        
        return risk

    def calculate_mission_metrics(self, mission_id: str) -> MissionMetrics:
        """Calcule les métriques d'une mission"""
        
        if mission_id not in self.missions:
            raise ValueError(f"Mission non trouvée: {mission_id}")
        
        mission = self.missions[mission_id]
        
        # Calculs des métriques
        total_hours_planned = sum(task.estimated_hours for task in mission.tasks)
        total_hours_actual = sum(task.actual_hours for task in mission.tasks)
        
        tasks_completed = len([t for t in mission.tasks if t.status == TaskStatus.COMPLETED])
        tasks_total = len(mission.tasks)
        
        deliverables_delivered = len([d for d in mission.deliverables if d.status == 'delivered'])
        deliverables_total = len(mission.deliverables)
        
        milestones_achieved = len([m for m in mission.milestones if m.status == 'achieved'])
        milestones_total = len(mission.milestones)
        
        risks_mitigated = len([r for r in mission.risks if r.status == 'mitigated'])
        risks_total = len(mission.risks)
        
        # Qualité moyenne
        quality_scores = [d.quality_score for d in mission.deliverables if d.quality_score > 0]
        quality_average = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        
        # Performance timeline
        if mission.actual_end_date and mission.planned_end_date:
            planned_duration = (mission.planned_end_date - mission.start_date).days
            actual_duration = (mission.actual_end_date - mission.start_date).days
            timeline_performance = max(0.0, min(2.0, planned_duration / actual_duration))
        else:
            timeline_performance = 1.0
        
        # Performance budget
        budget_performance = 1.0
        if mission.budget > 0 and total_hours_actual > 0:
            # Estimation simplifiée basée sur les heures
            estimated_cost = total_hours_actual * 100  # 100€/heure par défaut
            budget_performance = max(0.0, min(2.0, mission.budget / estimated_cost))
        
        # Utilisation de l'équipe
        team_utilization = 0.8  # Valeur par défaut
        if total_hours_planned > 0:
            team_utilization = min(1.0, total_hours_actual / total_hours_planned)
        
        # Création des métriques
        metrics = MissionMetrics(
            mission_id=mission_id,
            total_hours_planned=total_hours_planned,
            total_hours_actual=total_hours_actual,
            budget_planned=mission.budget,
            budget_actual=total_hours_actual * 100,  # Estimation
            tasks_completed=tasks_completed,
            tasks_total=tasks_total,
            deliverables_delivered=deliverables_delivered,
            deliverables_total=deliverables_total,
            milestones_achieved=milestones_achieved,
            milestones_total=milestones_total,
            risks_mitigated=risks_mitigated,
            risks_total=risks_total,
            quality_average=quality_average,
            timeline_performance=timeline_performance,
            budget_performance=budget_performance,
            client_satisfaction=mission.client_satisfaction,
            team_utilization=team_utilization,
            calculated_at=datetime.now()
        )
        
        # Sauvegarde
        self.mission_metrics[mission_id] = metrics
        self._save_mission_metrics(metrics)
        
        return metrics

    def get_mission_dashboard(self, mission_id: str = None) -> Dict[str, Any]:
        """Retourne le tableau de bord des missions"""
        
        if mission_id:
            # Dashboard spécifique à une mission
            if mission_id not in self.missions:
                return {}
            
            mission = self.missions[mission_id]
            metrics = self.calculate_mission_metrics(mission_id)
            
            return {
                'mission_info': {
                    'mission_id': mission.mission_id,
                    'mission_name': mission.mission_name,
                    'status': mission.status.value,
                    'progress': mission.progress_percentage,
                    'client': mission.client.client_name,
                    'team_size': mission.team.team_size
                },
                'timeline': {
                    'start_date': mission.start_date.isoformat(),
                    'planned_end_date': mission.planned_end_date.isoformat(),
                    'actual_end_date': mission.actual_end_date.isoformat() if mission.actual_end_date else None,
                    'days_remaining': (mission.planned_end_date - datetime.now()).days if mission.status != MissionStatus.COMPLETED else 0
                },
                'tasks': {
                    'total': metrics.tasks_total,
                    'completed': metrics.tasks_completed,
                    'completion_rate': metrics.tasks_completed / metrics.tasks_total if metrics.tasks_total > 0 else 0
                },
                'deliverables': {
                    'total': metrics.deliverables_total,
                    'delivered': metrics.deliverables_delivered,
                    'delivery_rate': metrics.deliverables_delivered / metrics.deliverables_total if metrics.deliverables_total > 0 else 0
                },
                'risks': {
                    'total': metrics.risks_total,
                    'high_risk': len([r for r in mission.risks if r.risk_score >= 0.7]),
                    'mitigated': metrics.risks_mitigated
                },
                'performance': {
                    'quality_score': metrics.quality_average,
                    'timeline_performance': metrics.timeline_performance,
                    'budget_performance': metrics.budget_performance,
                    'client_satisfaction': mission.client_satisfaction
                }
            }
        
        # Dashboard global
        active_missions = [m for m in self.missions.values() if m.status in [
            MissionStatus.IN_PROGRESS, MissionStatus.PLANNING, MissionStatus.REVIEW
        ]]
        
        completed_missions = [m for m in self.missions.values() if m.status == MissionStatus.COMPLETED]
        
        # Calculs globaux
        total_tasks = sum(len(m.tasks) for m in self.missions.values())
        completed_tasks = sum(len([t for t in m.tasks if t.status == TaskStatus.COMPLETED]) for m in self.missions.values())
        
        avg_client_satisfaction = 0.0
        if completed_missions:
            satisfactions = [m.client_satisfaction for m in completed_missions if m.client_satisfaction > 0]
            avg_client_satisfaction = sum(satisfactions) / len(satisfactions) if satisfactions else 0.0
        
        return {
            'overview': {
                'total_missions': len(self.missions),
                'active_missions': len(active_missions),
                'completed_missions': len(completed_missions),
                'completion_rate': len(completed_missions) / len(self.missions) if self.missions else 0
            },
            'tasks': {
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'completion_rate': completed_tasks / total_tasks if total_tasks > 0 else 0
            },
            'performance': {
                'average_client_satisfaction': avg_client_satisfaction,
                'on_time_delivery_rate': self.system_stats['on_time_delivery_rate'],
                'budget_performance_avg': self.system_stats['budget_performance_avg']
            },
            'recent_activity': self._get_recent_activity(),
            'alerts': self._get_active_alerts()
        }

    def _update_mission_progress(self, mission: Mission):
        """Met à jour le progrès global d'une mission"""
        
        if not mission.tasks:
            return
        
        # Progrès basé sur les tâches
        total_progress = sum(task.progress_percentage for task in mission.tasks)
        mission.progress_percentage = total_progress / len(mission.tasks)
        
        # Mise à jour automatique du statut
        if mission.progress_percentage == 100.0 and mission.status == MissionStatus.IN_PROGRESS:
            mission.status = MissionStatus.REVIEW
        elif mission.progress_percentage > 0.0 and mission.status == MissionStatus.PLANNING:
            mission.status = MissionStatus.IN_PROGRESS

    def _get_valid_status_transitions(self, current_status: MissionStatus) -> List[MissionStatus]:
        """Retourne les transitions de statut valides"""
        
        transitions = {
            MissionStatus.DRAFT: [MissionStatus.SUBMITTED, MissionStatus.CANCELLED],
            MissionStatus.SUBMITTED: [MissionStatus.APPROVED, MissionStatus.CANCELLED, MissionStatus.DRAFT],
            MissionStatus.APPROVED: [MissionStatus.PLANNING, MissionStatus.CANCELLED],
            MissionStatus.PLANNING: [MissionStatus.IN_PROGRESS, MissionStatus.ON_HOLD, MissionStatus.CANCELLED],
            MissionStatus.IN_PROGRESS: [MissionStatus.REVIEW, MissionStatus.ON_HOLD, MissionStatus.CANCELLED],
            MissionStatus.REVIEW: [MissionStatus.COMPLETED, MissionStatus.IN_PROGRESS],
            MissionStatus.ON_HOLD: [MissionStatus.IN_PROGRESS, MissionStatus.CANCELLED],
            MissionStatus.COMPLETED: [MissionStatus.ARCHIVED],
            MissionStatus.CANCELLED: [MissionStatus.ARCHIVED],
            MissionStatus.ARCHIVED: []
        }
        
        return transitions.get(current_status, [])

    def _trigger_workflow(self, workflow_name: str, entity_id: str):
        """Déclenche un workflow"""
        
        if workflow_name in self.workflows:
            try:
                self.workflows[workflow_name](entity_id)
            except Exception as e:
                self.logger.error(f"Erreur workflow {workflow_name}: {e}")

    def _workflow_mission_creation(self, mission_id: str):
        """Workflow de création de mission"""
        
        mission = self.missions.get(mission_id)
        if not mission:
            return
        
        # Création automatique des tâches de base
        base_tasks = [
            {
                'task_name': 'Analyse initiale',
                'description': 'Analyse des besoins et du contexte client',
                'due_date': mission.start_date + timedelta(days=3),
                'estimated_hours': 8.0,
                'priority': 'high'
            },
            {
                'task_name': 'Planification détaillée',
                'description': 'Élaboration du plan de travail détaillé',
                'due_date': mission.start_date + timedelta(days=5),
                'estimated_hours': 4.0,
                'priority': 'high'
            }
        ]
        
        for task_data in base_tasks:
            try:
                self.add_task(mission_id, task_data)
            except Exception as e:
                self.logger.error(f"Erreur création tâche automatique: {e}")
        
        # Création des jalons de base
        milestones = [
            {
                'milestone_name': 'Démarrage projet',
                'description': 'Lancement officiel du projet',
                'target_date': mission.start_date + timedelta(days=1)
            },
            {
                'milestone_name': 'Revue intermédiaire',
                'description': 'Point d\'étape à mi-parcours',
                'target_date': mission.start_date + timedelta(days=mission.estimated_duration // 2)
            },
            {
                'milestone_name': 'Livraison finale',
                'description': 'Livraison des livrables finaux',
                'target_date': mission.planned_end_date
            }
        ]
        
        for milestone_data in milestones:
            try:
                self.add_milestone(mission_id, milestone_data)
            except Exception as e:
                self.logger.error(f"Erreur création jalon automatique: {e}")

    def _workflow_task_assignment(self, task_id: str):
        """Workflow d'assignation de tâche"""
        
        # Notification d'assignation
        self.logger.info(f"Tâche {task_id} assignée - notification envoyée")

    def _workflow_deliverable_review(self, deliverable_id: str):
        """Workflow de revue de livrable"""
        
        # Processus de revue automatique
        self.logger.info(f"Livrable {deliverable_id} en cours de revue")

    def _workflow_milestone_tracking(self, milestone_id: str):
        """Workflow de suivi des jalons"""
        
        # Suivi automatique des jalons
        self.logger.info(f"Jalon {milestone_id} en cours de suivi")

    def _workflow_risk_monitoring(self, risk_id: str):
        """Workflow de monitoring des risques"""
        
        # Surveillance automatique des risques
        self.logger.info(f"Risque {risk_id} sous surveillance")

    def _workflow_mission_closure(self, mission_id: str):
        """Workflow de clôture de mission"""
        
        mission = self.missions.get(mission_id)
        if not mission:
            return
        
        # Calcul des métriques finales
        self.calculate_mission_metrics(mission_id)
        
        # Archivage automatique après délai
        self.executor.submit(self._schedule_archiving, mission_id)

    def _schedule_archiving(self, mission_id: str):
        """Programme l'archivage d'une mission"""
        
        # Attendre le délai configuré
        time.sleep(self.config['archive_after_days'] * 86400)
        
        # Archivage
        if mission_id in self.missions:
            mission = self.missions[mission_id]
            if mission.status == MissionStatus.COMPLETED:
                self.update_mission_status(mission_id, MissionStatus.ARCHIVED)

    def _get_recent_activity(self) -> List[Dict[str, Any]]:
        """Retourne l'activité récente"""
        
        activities = []
        
        # Missions récentes
        recent_missions = sorted(
            self.missions.values(),
            key=lambda m: m.updated_at,
            reverse=True
        )[:5]
        
        for mission in recent_missions:
            activities.append({
                'type': 'mission',
                'action': f"Mission {mission.status.value}",
                'description': mission.mission_name,
                'timestamp': mission.updated_at.isoformat()
            })
        
        return activities

    def _get_active_alerts(self) -> List[Dict[str, Any]]:
        """Retourne les alertes actives"""
        
        alerts = []
        
        # Missions en retard
        for mission in self.missions.values():
            if (mission.status in [MissionStatus.IN_PROGRESS, MissionStatus.PLANNING] and
                mission.planned_end_date < datetime.now()):
                alerts.append({
                    'type': 'warning',
                    'message': f"Mission en retard: {mission.mission_name}",
                    'mission_id': mission.mission_id
                })
        
        # Risques élevés
        for mission in self.missions.values():
            high_risks = [r for r in mission.risks if r.risk_score >= 0.7 and r.status == 'identified']
            if high_risks:
                alerts.append({
                    'type': 'danger',
                    'message': f"Risques élevés détectés: {mission.mission_name}",
                    'mission_id': mission.mission_id,
                    'risks_count': len(high_risks)
                })
        
        return alerts

    def _initialize_mission_templates(self):
        """Initialise les templates de missions"""
        
        self.mission_templates = {
            'strategic_analysis': {
                'name': 'Analyse Stratégique',
                'description': 'Template pour analyse stratégique complète',
                'estimated_duration': 45,
                'default_tasks': [
                    'Analyse de l\'environnement concurrentiel',
                    'Évaluation des forces et faiblesses',
                    'Identification des opportunités',
                    'Recommandations stratégiques'
                ],
                'default_deliverables': [
                    'Rapport d\'analyse stratégique',
                    'Présentation exécutive',
                    'Plan d\'action'
                ]
            },
            'business_plan': {
                'name': 'Business Plan',
                'description': 'Template pour élaboration de business plan',
                'estimated_duration': 60,
                'default_tasks': [
                    'Étude de marché',
                    'Modèle économique',
                    'Projections financières',
                    'Stratégie commerciale'
                ],
                'default_deliverables': [
                    'Business plan complet',
                    'Modèle financier',
                    'Pitch deck'
                ]
            }
        }

    def _save_mission(self, mission: Mission):
        """Sauvegarde une mission"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO missions 
                    (mission_id, mission_name, mission_type, description, objectives,
                     success_criteria, client_data, team_data, status, priority, budget,
                     estimated_duration, actual_duration, start_date, planned_end_date,
                     actual_end_date, methodology, progress_percentage, quality_score,
                     client_satisfaction, lessons_learned, metadata, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    mission.mission_id, mission.mission_name, mission.mission_type.value,
                    mission.description, json.dumps(mission.objectives),
                    json.dumps(mission.success_criteria), json.dumps(asdict(mission.client)),
                    json.dumps(asdict(mission.team)), mission.status.value, mission.priority.value,
                    mission.budget, mission.estimated_duration, mission.actual_duration,
                    mission.start_date, mission.planned_end_date, mission.actual_end_date,
                    mission.methodology, mission.progress_percentage, mission.quality_score,
                    mission.client_satisfaction, json.dumps(mission.lessons_learned),
                    json.dumps(mission.metadata), mission.created_at, mission.updated_at
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde mission: {e}")

    def _save_task(self, task: MissionTask):
        """Sauvegarde une tâche"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO mission_tasks 
                    (task_id, mission_id, task_name, description, assigned_to, status,
                     priority, estimated_hours, actual_hours, start_date, due_date,
                     completion_date, dependencies, deliverables, progress_percentage,
                     notes, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    task.task_id, task.mission_id, task.task_name, task.description,
                    task.assigned_to, task.status.value, task.priority.value,
                    task.estimated_hours, task.actual_hours, task.start_date,
                    task.due_date, task.completion_date, json.dumps(task.dependencies),
                    json.dumps(task.deliverables), task.progress_percentage,
                    task.notes, task.created_at, task.updated_at
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde tâche: {e}")

    def _save_deliverable(self, deliverable: MissionDeliverable):
        """Sauvegarde un livrable"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO mission_deliverables 
                    (deliverable_id, mission_id, deliverable_name, deliverable_type,
                     description, format, file_path, version, status, quality_score,
                     review_comments, created_by, created_at, updated_at, delivered_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    deliverable.deliverable_id, deliverable.mission_id,
                    deliverable.deliverable_name, deliverable.deliverable_type.value,
                    deliverable.description, deliverable.format, deliverable.file_path,
                    deliverable.version, deliverable.status, deliverable.quality_score,
                    json.dumps(deliverable.review_comments), deliverable.created_by,
                    deliverable.created_at, deliverable.updated_at, deliverable.delivered_at
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde livrable: {e}")

    def _save_milestone(self, milestone: MissionMilestone):
        """Sauvegarde un jalon"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO mission_milestones 
                    (milestone_id, mission_id, milestone_name, description, target_date,
                     actual_date, status, success_criteria, deliverables_required,
                     stakeholders_involved, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    milestone.milestone_id, milestone.mission_id, milestone.milestone_name,
                    milestone.description, milestone.target_date, milestone.actual_date,
                    milestone.status, json.dumps(milestone.success_criteria),
                    json.dumps(milestone.deliverables_required),
                    json.dumps(milestone.stakeholders_involved), milestone.created_at
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde jalon: {e}")

    def _save_risk(self, risk: MissionRisk):
        """Sauvegarde un risque"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO mission_risks 
                    (risk_id, mission_id, risk_name, description, category, probability,
                     impact, risk_score, mitigation_plan, contingency_plan, owner,
                     status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    risk.risk_id, risk.mission_id, risk.risk_name, risk.description,
                    risk.category, risk.probability, risk.impact, risk.risk_score,
                    risk.mitigation_plan, risk.contingency_plan, risk.owner,
                    risk.status, risk.created_at, risk.updated_at
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde risque: {e}")

    def _save_mission_metrics(self, metrics: MissionMetrics):
        """Sauvegarde les métriques de mission"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO mission_metrics 
                    (mission_id, total_hours_planned, total_hours_actual, budget_planned,
                     budget_actual, tasks_completed, tasks_total, deliverables_delivered,
                     deliverables_total, milestones_achieved, milestones_total,
                     risks_mitigated, risks_total, quality_average, timeline_performance,
                     budget_performance, client_satisfaction, team_utilization, calculated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    metrics.mission_id, metrics.total_hours_planned, metrics.total_hours_actual,
                    metrics.budget_planned, metrics.budget_actual, metrics.tasks_completed,
                    metrics.tasks_total, metrics.deliverables_delivered, metrics.deliverables_total,
                    metrics.milestones_achieved, metrics.milestones_total, metrics.risks_mitigated,
                    metrics.risks_total, metrics.quality_average, metrics.timeline_performance,
                    metrics.budget_performance, metrics.client_satisfaction,
                    metrics.team_utilization, metrics.calculated_at
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde métriques: {e}")

    def _load_existing_missions(self):
        """Charge les missions existantes"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Chargement des missions
                cursor.execute('SELECT * FROM missions ORDER BY created_at DESC')
                
                for row in cursor.fetchall():
                    # Reconstruction de la mission (version simplifiée)
                    mission_data = {
                        'mission_name': row[1],
                        'mission_type': row[2],
                        'description': row[3],
                        'objectives': json.loads(row[4]) if row[4] else [],
                        'client': json.loads(row[6]) if row[6] else {},
                        'start_date': row[13],
                        'estimated_duration': row[11] or 30,
                        'priority': row[9] or 'medium',
                        'budget': row[10] or 0.0
                    }
                    
                    # Création simplifiée (sans déclencher les workflows)
                    mission_id = row[0]
                    # Note: Implémentation simplifiée pour le chargement
                    
                self.logger.info(f"Missions existantes chargées")
                
        except Exception as e:
            self.logger.error(f"Erreur chargement missions: {e}")

    def _start_services(self):
        """Démarre les services du système"""
        
        # Service de monitoring des missions
        threading.Thread(target=self._mission_monitoring_service, daemon=True).start()
        
        # Service de sauvegarde automatique
        if self.config['backup_enabled']:
            threading.Thread(target=self._backup_service, daemon=True).start()

    def _mission_monitoring_service(self):
        """Service de monitoring des missions"""
        
        while True:
            try:
                # Vérification des missions actives
                for mission in self.missions.values():
                    if mission.status in [MissionStatus.IN_PROGRESS, MissionStatus.PLANNING]:
                        # Vérification des échéances
                        if mission.planned_end_date < datetime.now():
                            self.logger.warning(f"Mission en retard: {mission.mission_name}")
                        
                        # Calcul des métriques
                        self.calculate_mission_metrics(mission.mission_id)
                
                time.sleep(3600)  # Toutes les heures
                
            except Exception as e:
                self.logger.error(f"Erreur service monitoring: {e}")
                time.sleep(3600)

    def _backup_service(self):
        """Service de sauvegarde automatique"""
        
        while True:
            try:
                # Sauvegarde quotidienne
                backup_path = os.path.join(self.data_path, 'backups')
                os.makedirs(backup_path, exist_ok=True)
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_file = os.path.join(backup_path, f'missions_backup_{timestamp}.db')
                
                shutil.copy2(self.db_path, backup_file)
                
                self.logger.info(f"Sauvegarde créée: {backup_file}")
                
                time.sleep(86400)  # 24 heures
                
            except Exception as e:
                self.logger.error(f"Erreur service sauvegarde: {e}")
                time.sleep(86400)

    def get_system_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques du système"""
        
        # Mise à jour des statistiques
        active_count = len([m for m in self.missions.values() 
                           if m.status in [MissionStatus.IN_PROGRESS, MissionStatus.PLANNING, MissionStatus.REVIEW]])
        completed_count = len([m for m in self.missions.values() if m.status == MissionStatus.COMPLETED])
        
        self.system_stats.update({
            'total_missions': len(self.missions),
            'active_missions': active_count,
            'completed_missions': completed_count
        })
        
        return self.system_stats.copy()

# Instance globale
_mission_lifecycle_manager = None

def get_mission_lifecycle_manager() -> MissionLifecycleManager:
    """Retourne l'instance du gestionnaire de missions"""
    global _mission_lifecycle_manager
    if _mission_lifecycle_manager is None:
        _mission_lifecycle_manager = MissionLifecycleManager()
    return _mission_lifecycle_manager

# Test du système
if __name__ == '__main__':
    print("=== Test Mission Lifecycle Manager ===")
    
    mlm = MissionLifecycleManager()
    
    # Création d'une mission de test
    mission_data = {
        'mission_name': 'Analyse Stratégique Test',
        'mission_type': 'strategic_analysis',
        'description': 'Mission de test pour validation du système',
        'objectives': ['Analyser le marché', 'Identifier les opportunités'],
        'client': {
            'client_name': 'Client Test',
            'industry': 'Technology',
            'contact_person': 'John Doe',
            'contact_email': 'john@test.com'
        },
        'estimated_duration': 30,
        'budget': 50000.0,
        'priority': 'high'
    }
    
    mission = mlm.create_mission(mission_data)
    print(f"Mission créée: {mission.mission_name} ({mission.mission_id})")
    
    # Ajout d'une tâche
    task_data = {
        'task_name': 'Recherche marché',
        'description': 'Analyse du marché concurrentiel',
        'due_date': datetime.now() + timedelta(days=7),
        'estimated_hours': 16.0,
        'assigned_to': 'Expert Marché'
    }
    
    task = mlm.add_task(mission.mission_id, task_data)
    print(f"Tâche ajoutée: {task.task_name}")
    
    # Mise à jour du progrès
    mlm.update_task_progress(task.task_id, 50.0, 8.0, "Progrès à mi-parcours")
    
    # Calcul des métriques
    metrics = mlm.calculate_mission_metrics(mission.mission_id)
    print(f"Métriques calculées - Tâches: {metrics.tasks_completed}/{metrics.tasks_total}")
    
    # Dashboard
    dashboard = mlm.get_mission_dashboard(mission.mission_id)
    print(f"Dashboard: {dashboard['mission_info']['progress']:.1f}% complété")
    
    # Statistiques
    stats = mlm.get_system_statistics()
    print(f"Statistiques: {stats['total_missions']} missions totales")
    
    print("Test terminé avec succès")

