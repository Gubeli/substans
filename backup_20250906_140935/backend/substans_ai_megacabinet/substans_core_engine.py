"""
Substans Core Engine - Système Principal Unifié
Architecture enterprise-grade pour la plateforme substans.ai
"""

import asyncio
import json
import logging
import os
import sys
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from queue import Queue, PriorityQueue
import sqlite3
import hashlib
import pickle
from pathlib import Path

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/substans_ai_megacabinet/logs/core_engine.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class SystemStatus(Enum):
    """États du système"""
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    SHUTDOWN = "shutdown"

class TaskPriority(Enum):
    """Priorités des tâches"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5

class TaskStatus(Enum):
    """États des tâches"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class SystemMetrics:
    """Métriques système"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    active_tasks: int
    completed_tasks: int
    failed_tasks: int
    uptime: float
    response_time_avg: float
    throughput: float
    error_rate: float
    timestamp: datetime

@dataclass
class Task:
    """Tâche système"""
    task_id: str
    name: str
    priority: TaskPriority
    status: TaskStatus
    agent_id: str
    mission_id: Optional[str]
    parameters: Dict[str, Any]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    result: Optional[Any]
    error: Optional[str]
    retry_count: int
    max_retries: int
    timeout: int
    dependencies: List[str]
    
    def __lt__(self, other):
        return self.priority.value < other.priority.value

class SubstansCoreEngine:
    """
    Moteur principal de la plateforme Substans.AI
    Architecture enterprise-grade avec orchestration avancée
    """
    
    def __init__(self, config_path: str = None):
        self.engine_id = str(uuid.uuid4())
        self.status = SystemStatus.INITIALIZING
        self.start_time = datetime.now()
        self.logger = logging.getLogger(f"SubstansCoreEngine-{self.engine_id[:8]}")
        
        # Configuration
        self.config = self._load_configuration(config_path)
        
        # Base de données
        self.db_path = self.config.get('database_path', '/home/ubuntu/substans_ai_megacabinet/data/substans.db')
        self._initialize_database()
        
        # Gestionnaires de tâches
        self.task_queue = PriorityQueue()
        self.active_tasks = {}
        self.completed_tasks = {}
        self.failed_tasks = {}
        
        # Pool de threads
        self.max_workers = self.config.get('max_workers', 20)
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        
        # Agents disponibles
        self.agents = {}
        self.agent_status = {}
        
        # Métriques
        self.metrics = SystemMetrics(
            cpu_usage=0.0, memory_usage=0.0, disk_usage=0.0,
            active_tasks=0, completed_tasks=0, failed_tasks=0,
            uptime=0.0, response_time_avg=0.0, throughput=0.0,
            error_rate=0.0, timestamp=datetime.now()
        )
        
        # Événements système
        self.event_handlers = {}
        self.shutdown_event = threading.Event()
        
        # Cache système
        self.cache = {}
        self.cache_ttl = {}
        
        # Sécurité
        self.security_manager = None
        self.access_control = None
        
        self.logger.info(f"Substans Core Engine initialisé - ID: {self.engine_id}")

    def _load_configuration(self, config_path: str) -> Dict[str, Any]:
        """Charge la configuration système"""
        default_config = {
            'max_workers': 20,
            'task_timeout': 3600,
            'max_retries': 3,
            'database_path': '/home/ubuntu/substans_ai_megacabinet/data/substans.db',
            'log_level': 'INFO',
            'cache_ttl': 3600,
            'metrics_interval': 60,
            'backup_interval': 86400,
            'security_enabled': True,
            'monitoring_enabled': True
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                self.logger.warning(f"Erreur chargement configuration: {e}")
        
        return default_config

    def _initialize_database(self):
        """Initialise la base de données système"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Table des tâches
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    priority INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    mission_id TEXT,
                    parameters TEXT,
                    created_at TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    result TEXT,
                    error TEXT,
                    retry_count INTEGER DEFAULT 0,
                    max_retries INTEGER DEFAULT 3
                )
            ''')
            
            # Table des métriques
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP,
                    cpu_usage REAL,
                    memory_usage REAL,
                    disk_usage REAL,
                    active_tasks INTEGER,
                    completed_tasks INTEGER,
                    failed_tasks INTEGER,
                    uptime REAL,
                    response_time_avg REAL,
                    throughput REAL,
                    error_rate REAL
                )
            ''')
            
            # Table des événements
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP,
                    event_type TEXT,
                    source TEXT,
                    data TEXT,
                    severity TEXT
                )
            ''')
            
            # Table des agents
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agents (
                    agent_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    last_activity TIMESTAMP,
                    performance_score REAL,
                    total_tasks INTEGER DEFAULT 0,
                    successful_tasks INTEGER DEFAULT 0,
                    failed_tasks INTEGER DEFAULT 0
                )
            ''')
            
            conn.commit()

    def start(self):
        """Démarre le moteur principal"""
        try:
            self.logger.info("Démarrage du Substans Core Engine")
            self.status = SystemStatus.RUNNING
            
            # Chargement des agents
            self._load_agents()
            
            # Démarrage des services
            self._start_services()
            
            # Boucle principale
            self._main_loop()
            
        except Exception as e:
            self.logger.error(f"Erreur démarrage moteur: {e}")
            self.status = SystemStatus.ERROR
            raise

    def _load_agents(self):
        """Charge tous les agents disponibles"""
        self.logger.info("Chargement des agents")
        
        # Agents Consultants
        agents_consultants = [
            'avs', 'aad', 'arr', 'agc', 'asm', 'arpc', 'adamo'
        ]
        
        # Experts Métiers
        experts_metiers = [
            'ess', 'ebf', 'ea', 'er', 'em', 'eauto', 'etl', 'esp', 'ed', 'ee', 'eddi'
        ]
        
        # Experts Domaines
        experts_domaines = [
            'eia', 'ec', 'edata', 'elrd', 'efs', 'etd', 'ecyber', 'erse', 'esn', 
            'eli', 'ege', 'estrat', 'erh', 'eerc'
        ]
        
        # Chargement dynamique des agents
        for agent_type, agent_list in [
            ('consultant', agents_consultants),
            ('metier', experts_metiers),
            ('domaine', experts_domaines)
        ]:
            for agent_id in agent_list:
                try:
                    agent = self._load_agent(agent_id, agent_type)
                    if agent:
                        self.agents[agent_id] = agent
                        self.agent_status[agent_id] = 'active'
                        self.logger.info(f"Agent {agent_id} chargé avec succès")
                except Exception as e:
                    self.logger.error(f"Erreur chargement agent {agent_id}: {e}")
        
        self.logger.info(f"{len(self.agents)} agents chargés")

    def _load_agent(self, agent_id: str, agent_type: str):
        """Charge un agent spécifique"""
        try:
            if agent_type == 'consultant':
                module_path = f'agents_consultants.{agent_id}'
            elif agent_type == 'metier':
                module_path = f'experts_metiers.{agent_id}'
            else:
                module_path = f'experts_domaines.{agent_id}'
            
            # Import dynamique
            module = __import__(module_path, fromlist=[agent_id])
            
            # Recherche de la classe agent
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    hasattr(attr, 'agent_id') and 
                    hasattr(attr, 'provide_expertise')):
                    return attr()
            
            return None
            
        except Exception as e:
            self.logger.error(f"Erreur import agent {agent_id}: {e}")
            return None

    def _start_services(self):
        """Démarre les services système"""
        self.logger.info("Démarrage des services système")
        
        # Service de métriques
        threading.Thread(target=self._metrics_service, daemon=True).start()
        
        # Service de nettoyage
        threading.Thread(target=self._cleanup_service, daemon=True).start()
        
        # Service de sauvegarde
        threading.Thread(target=self._backup_service, daemon=True).start()
        
        # Service de monitoring
        if self.config.get('monitoring_enabled', True):
            threading.Thread(target=self._monitoring_service, daemon=True).start()

    def _main_loop(self):
        """Boucle principale du moteur"""
        self.logger.info("Boucle principale démarrée")
        
        while not self.shutdown_event.is_set():
            try:
                # Traitement des tâches
                self._process_tasks()
                
                # Mise à jour des métriques
                self._update_metrics()
                
                # Gestion des événements
                self._handle_events()
                
                # Pause courte
                time.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Erreur boucle principale: {e}")
                time.sleep(1)

    def submit_task(self, name: str, agent_id: str, parameters: Dict[str, Any], 
                   priority: TaskPriority = TaskPriority.MEDIUM,
                   mission_id: str = None, timeout: int = None,
                   max_retries: int = None) -> str:
        """Soumet une nouvelle tâche"""
        
        task_id = str(uuid.uuid4())
        
        task = Task(
            task_id=task_id,
            name=name,
            priority=priority,
            status=TaskStatus.PENDING,
            agent_id=agent_id,
            mission_id=mission_id,
            parameters=parameters,
            created_at=datetime.now(),
            started_at=None,
            completed_at=None,
            result=None,
            error=None,
            retry_count=0,
            max_retries=max_retries or self.config.get('max_retries', 3),
            timeout=timeout or self.config.get('task_timeout', 3600),
            dependencies=[]
        )
        
        # Sauvegarde en base
        self._save_task(task)
        
        # Ajout à la queue
        self.task_queue.put(task)
        
        self.logger.info(f"Tâche {task_id} soumise - Agent: {agent_id}, Priorité: {priority.name}")
        
        return task_id

    def _process_tasks(self):
        """Traite les tâches en attente"""
        while not self.task_queue.empty() and len(self.active_tasks) < self.max_workers:
            try:
                task = self.task_queue.get_nowait()
                
                # Vérification des dépendances
                if self._check_dependencies(task):
                    # Soumission à l'executor
                    future = self.executor.submit(self._execute_task, task)
                    self.active_tasks[task.task_id] = (task, future)
                    
                    task.status = TaskStatus.RUNNING
                    task.started_at = datetime.now()
                    self._save_task(task)
                else:
                    # Remise en queue si dépendances non satisfaites
                    self.task_queue.put(task)
                    
            except Exception as e:
                self.logger.error(f"Erreur traitement tâche: {e}")
        
        # Vérification des tâches actives
        completed_tasks = []
        for task_id, (task, future) in self.active_tasks.items():
            if future.done():
                completed_tasks.append(task_id)
                try:
                    result = future.result()
                    task.result = result
                    task.status = TaskStatus.COMPLETED
                    task.completed_at = datetime.now()
                    self.completed_tasks[task_id] = task
                    
                    self.logger.info(f"Tâche {task_id} terminée avec succès")
                    
                except Exception as e:
                    task.error = str(e)
                    task.status = TaskStatus.FAILED
                    task.completed_at = datetime.now()
                    
                    # Retry si possible
                    if task.retry_count < task.max_retries:
                        task.retry_count += 1
                        task.status = TaskStatus.PENDING
                        task.started_at = None
                        task.completed_at = None
                        task.error = None
                        self.task_queue.put(task)
                        self.logger.info(f"Tâche {task_id} en retry ({task.retry_count}/{task.max_retries})")
                    else:
                        self.failed_tasks[task_id] = task
                        self.logger.error(f"Tâche {task_id} échouée définitivement: {e}")
                
                self._save_task(task)
        
        # Nettoyage des tâches terminées
        for task_id in completed_tasks:
            del self.active_tasks[task_id]

    def _execute_task(self, task: Task) -> Any:
        """Exécute une tâche"""
        self.logger.info(f"Exécution tâche {task.task_id} - Agent: {task.agent_id}")
        
        start_time = time.time()
        
        try:
            # Récupération de l'agent
            agent = self.agents.get(task.agent_id)
            if not agent:
                raise Exception(f"Agent {task.agent_id} non trouvé")
            
            # Exécution selon le type de tâche
            if task.name == 'provide_expertise':
                result = agent.provide_expertise(task.parameters)
            elif task.name == 'autonomous_watch':
                result = agent.autonomous_watch()
            elif hasattr(agent, task.name):
                method = getattr(agent, task.name)
                result = method(**task.parameters)
            else:
                raise Exception(f"Méthode {task.name} non trouvée sur agent {task.agent_id}")
            
            execution_time = time.time() - start_time
            self.logger.info(f"Tâche {task.task_id} exécutée en {execution_time:.2f}s")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Erreur exécution tâche {task.task_id} après {execution_time:.2f}s: {e}")
            raise

    def _check_dependencies(self, task: Task) -> bool:
        """Vérifie si les dépendances d'une tâche sont satisfaites"""
        for dep_id in task.dependencies:
            if dep_id not in self.completed_tasks:
                return False
        return True

    def _save_task(self, task: Task):
        """Sauvegarde une tâche en base"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO tasks 
                    (task_id, name, priority, status, agent_id, mission_id, parameters,
                     created_at, started_at, completed_at, result, error, retry_count, max_retries)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    task.task_id, task.name, task.priority.value, task.status.value,
                    task.agent_id, task.mission_id, json.dumps(task.parameters),
                    task.created_at, task.started_at, task.completed_at,
                    json.dumps(task.result) if task.result else None,
                    task.error, task.retry_count, task.max_retries
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde tâche: {e}")

    def _update_metrics(self):
        """Met à jour les métriques système"""
        try:
            import psutil
            
            self.metrics.cpu_usage = psutil.cpu_percent()
            self.metrics.memory_usage = psutil.virtual_memory().percent
            self.metrics.disk_usage = psutil.disk_usage('/').percent
            self.metrics.active_tasks = len(self.active_tasks)
            self.metrics.completed_tasks = len(self.completed_tasks)
            self.metrics.failed_tasks = len(self.failed_tasks)
            self.metrics.uptime = (datetime.now() - self.start_time).total_seconds()
            self.metrics.timestamp = datetime.now()
            
            # Calcul du taux d'erreur
            total_tasks = self.metrics.completed_tasks + self.metrics.failed_tasks
            if total_tasks > 0:
                self.metrics.error_rate = self.metrics.failed_tasks / total_tasks * 100
            
        except ImportError:
            # Métriques basiques si psutil non disponible
            self.metrics.active_tasks = len(self.active_tasks)
            self.metrics.completed_tasks = len(self.completed_tasks)
            self.metrics.failed_tasks = len(self.failed_tasks)
            self.metrics.uptime = (datetime.now() - self.start_time).total_seconds()
            self.metrics.timestamp = datetime.now()

    def _metrics_service(self):
        """Service de collecte des métriques"""
        while not self.shutdown_event.is_set():
            try:
                self._update_metrics()
                self._save_metrics()
                time.sleep(self.config.get('metrics_interval', 60))
            except Exception as e:
                self.logger.error(f"Erreur service métriques: {e}")
                time.sleep(60)

    def _save_metrics(self):
        """Sauvegarde les métriques en base"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO metrics 
                    (timestamp, cpu_usage, memory_usage, disk_usage, active_tasks,
                     completed_tasks, failed_tasks, uptime, response_time_avg, throughput, error_rate)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    self.metrics.timestamp, self.metrics.cpu_usage, self.metrics.memory_usage,
                    self.metrics.disk_usage, self.metrics.active_tasks, self.metrics.completed_tasks,
                    self.metrics.failed_tasks, self.metrics.uptime, self.metrics.response_time_avg,
                    self.metrics.throughput, self.metrics.error_rate
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde métriques: {e}")

    def _cleanup_service(self):
        """Service de nettoyage"""
        while not self.shutdown_event.is_set():
            try:
                # Nettoyage des tâches anciennes
                cutoff_date = datetime.now() - timedelta(days=7)
                
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        DELETE FROM tasks 
                        WHERE completed_at < ? AND status IN ('completed', 'failed')
                    ''', (cutoff_date,))
                    
                    cursor.execute('''
                        DELETE FROM metrics 
                        WHERE timestamp < ?
                    ''', (cutoff_date,))
                    
                    conn.commit()
                
                # Nettoyage du cache
                current_time = time.time()
                expired_keys = [
                    key for key, ttl in self.cache_ttl.items()
                    if current_time > ttl
                ]
                
                for key in expired_keys:
                    del self.cache[key]
                    del self.cache_ttl[key]
                
                time.sleep(3600)  # Nettoyage toutes les heures
                
            except Exception as e:
                self.logger.error(f"Erreur service nettoyage: {e}")
                time.sleep(3600)

    def _backup_service(self):
        """Service de sauvegarde"""
        while not self.shutdown_event.is_set():
            try:
                backup_path = f"/home/ubuntu/substans_ai_megacabinet/backups/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                os.makedirs(os.path.dirname(backup_path), exist_ok=True)
                
                # Copie de la base de données
                import shutil
                shutil.copy2(self.db_path, backup_path)
                
                self.logger.info(f"Sauvegarde créée: {backup_path}")
                
                time.sleep(self.config.get('backup_interval', 86400))
                
            except Exception as e:
                self.logger.error(f"Erreur service sauvegarde: {e}")
                time.sleep(86400)

    def _monitoring_service(self):
        """Service de monitoring"""
        while not self.shutdown_event.is_set():
            try:
                # Vérification de la santé du système
                if self.metrics.cpu_usage > 90:
                    self._emit_event('high_cpu_usage', 'system', {'cpu_usage': self.metrics.cpu_usage}, 'warning')
                
                if self.metrics.memory_usage > 90:
                    self._emit_event('high_memory_usage', 'system', {'memory_usage': self.metrics.memory_usage}, 'warning')
                
                if self.metrics.error_rate > 10:
                    self._emit_event('high_error_rate', 'system', {'error_rate': self.metrics.error_rate}, 'error')
                
                time.sleep(60)
                
            except Exception as e:
                self.logger.error(f"Erreur service monitoring: {e}")
                time.sleep(60)

    def _emit_event(self, event_type: str, source: str, data: Dict[str, Any], severity: str = 'info'):
        """Émet un événement système"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO events (timestamp, event_type, source, data, severity)
                    VALUES (?, ?, ?, ?, ?)
                ''', (datetime.now(), event_type, source, json.dumps(data), severity))
                conn.commit()
            
            self.logger.info(f"Événement émis: {event_type} - {severity}")
            
        except Exception as e:
            self.logger.error(f"Erreur émission événement: {e}")

    def _handle_events(self):
        """Gère les événements système"""
        # Traitement des événements en attente
        pass

    def get_status(self) -> Dict[str, Any]:
        """Retourne le statut du système"""
        return {
            'engine_id': self.engine_id,
            'status': self.status.value,
            'uptime': (datetime.now() - self.start_time).total_seconds(),
            'agents_loaded': len(self.agents),
            'active_tasks': len(self.active_tasks),
            'completed_tasks': len(self.completed_tasks),
            'failed_tasks': len(self.failed_tasks),
            'metrics': asdict(self.metrics)
        }

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Retourne le statut d'une tâche"""
        # Recherche dans les tâches actives
        if task_id in self.active_tasks:
            task, _ = self.active_tasks[task_id]
            return asdict(task)
        
        # Recherche dans les tâches terminées
        if task_id in self.completed_tasks:
            return asdict(self.completed_tasks[task_id])
        
        # Recherche dans les tâches échouées
        if task_id in self.failed_tasks:
            return asdict(self.failed_tasks[task_id])
        
        # Recherche en base
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM tasks WHERE task_id = ?', (task_id,))
                row = cursor.fetchone()
                if row:
                    columns = [desc[0] for desc in cursor.description]
                    return dict(zip(columns, row))
        except Exception as e:
            self.logger.error(f"Erreur recherche tâche: {e}")
        
        return None

    def cancel_task(self, task_id: str) -> bool:
        """Annule une tâche"""
        try:
            if task_id in self.active_tasks:
                task, future = self.active_tasks[task_id]
                future.cancel()
                task.status = TaskStatus.CANCELLED
                task.completed_at = datetime.now()
                self._save_task(task)
                del self.active_tasks[task_id]
                self.logger.info(f"Tâche {task_id} annulée")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Erreur annulation tâche: {e}")
            return False

    def shutdown(self):
        """Arrêt propre du moteur"""
        self.logger.info("Arrêt du Substans Core Engine")
        self.status = SystemStatus.SHUTDOWN
        
        # Signal d'arrêt
        self.shutdown_event.set()
        
        # Attente des tâches actives
        for task_id, (task, future) in self.active_tasks.items():
            try:
                future.result(timeout=30)
            except Exception:
                future.cancel()
        
        # Arrêt de l'executor
        self.executor.shutdown(wait=True)
        
        self.logger.info("Substans Core Engine arrêté")

# Instance globale
_core_engine = None

def get_core_engine(config_path: str = None) -> SubstansCoreEngine:
    """Retourne l'instance du moteur principal"""
    global _core_engine
    if _core_engine is None:
        _core_engine = SubstansCoreEngine(config_path)
    return _core_engine

def start_core_engine(config_path: str = None):
    """Démarre le moteur principal"""
    engine = get_core_engine(config_path)
    engine.start()

# Test du moteur
if __name__ == '__main__':
    # Configuration de test
    os.makedirs('/home/ubuntu/substans_ai_megacabinet/logs', exist_ok=True)
    os.makedirs('/home/ubuntu/substans_ai_megacabinet/data', exist_ok=True)
    
    # Démarrage du moteur
    engine = SubstansCoreEngine()
    
    try:
        print("=== Test Substans Core Engine ===")
        print(f"Engine ID: {engine.engine_id}")
        print(f"Status: {engine.status.value}")
        
        # Test de soumission de tâche
        task_id = engine.submit_task(
            name='provide_expertise',
            agent_id='efs',
            parameters={'mission_context': {'nom': 'Test Mission'}},
            priority=TaskPriority.HIGH
        )
        
        print(f"Tâche soumise: {task_id}")
        
        # Simulation courte
        time.sleep(2)
        
        # Vérification du statut
        status = engine.get_status()
        print(f"Agents chargés: {status['agents_loaded']}")
        print(f"Tâches actives: {status['active_tasks']}")
        
        print("Test terminé avec succès")
        
    except Exception as e:
        print(f"Erreur test: {e}")
    finally:
        engine.shutdown()

