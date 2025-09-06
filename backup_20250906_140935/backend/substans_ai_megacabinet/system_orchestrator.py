"""
System Orchestrator - Orchestrateur Système
Coordination enterprise-grade des agents et workflows
"""

import asyncio
import json
import logging
import os
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from queue import Queue, PriorityQueue
import networkx as nx
from concurrent.futures import ThreadPoolExecutor, as_completed
import sqlite3

# Configuration du logging
logging.basicConfig(level=logging.INFO)

class WorkflowStatus(Enum):
    """États des workflows"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class NodeType(Enum):
    """Types de nœuds dans un workflow"""
    AGENT = "agent"
    CONDITION = "condition"
    PARALLEL = "parallel"
    SEQUENTIAL = "sequential"
    MERGE = "merge"
    SPLIT = "split"

class ExecutionMode(Enum):
    """Modes d'exécution"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    PIPELINE = "pipeline"

@dataclass
class WorkflowNode:
    """Nœud de workflow"""
    node_id: str
    name: str
    node_type: NodeType
    agent_id: Optional[str]
    method: Optional[str]
    parameters: Dict[str, Any]
    conditions: List[str]
    dependencies: List[str]
    timeout: int
    retry_count: int
    max_retries: int
    status: str
    result: Optional[Any]
    error: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

@dataclass
class Workflow:
    """Workflow complet"""
    workflow_id: str
    name: str
    description: str
    status: WorkflowStatus
    execution_mode: ExecutionMode
    nodes: Dict[str, WorkflowNode]
    edges: List[Tuple[str, str]]
    variables: Dict[str, Any]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_by: str
    priority: int
    timeout: int
    result: Optional[Any]
    error: Optional[str]

class SystemOrchestrator:
    """
    Orchestrateur système pour la coordination des agents et workflows
    """
    
    def __init__(self, core_engine=None):
        self.orchestrator_id = str(uuid.uuid4())
        self.logger = logging.getLogger(f"SystemOrchestrator-{self.orchestrator_id[:8]}")
        
        # Référence au moteur principal
        self.core_engine = core_engine
        
        # Workflows
        self.workflows = {}
        self.active_workflows = {}
        self.completed_workflows = {}
        self.failed_workflows = {}
        
        # Graphes de workflows
        self.workflow_graphs = {}
        
        # Exécuteurs
        self.workflow_executor = ThreadPoolExecutor(max_workers=10)
        self.node_executor = ThreadPoolExecutor(max_workers=50)
        
        # Patterns de workflows prédéfinis
        self.workflow_patterns = self._initialize_patterns()
        
        # Métriques d'orchestration
        self.orchestration_metrics = {
            'workflows_executed': 0,
            'nodes_executed': 0,
            'average_execution_time': 0.0,
            'success_rate': 0.0,
            'parallel_efficiency': 0.0
        }
        
        # Base de données
        self.db_path = '/home/ubuntu/substans_ai_megacabinet/data/orchestrator.db'
        self._initialize_database()
        
        self.logger.info(f"System Orchestrator initialisé - ID: {self.orchestrator_id}")

    def _initialize_database(self):
        """Initialise la base de données de l'orchestrateur"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Table des workflows
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS workflows (
                    workflow_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    status TEXT NOT NULL,
                    execution_mode TEXT NOT NULL,
                    created_at TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    created_by TEXT,
                    priority INTEGER,
                    timeout INTEGER,
                    result TEXT,
                    error TEXT
                )
            ''')
            
            # Table des nœuds
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS workflow_nodes (
                    node_id TEXT PRIMARY KEY,
                    workflow_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    node_type TEXT NOT NULL,
                    agent_id TEXT,
                    method TEXT,
                    parameters TEXT,
                    conditions TEXT,
                    dependencies TEXT,
                    timeout INTEGER,
                    retry_count INTEGER,
                    max_retries INTEGER,
                    status TEXT,
                    result TEXT,
                    error TEXT,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (workflow_id) REFERENCES workflows (workflow_id)
                )
            ''')
            
            # Table des métriques
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS orchestration_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP,
                    workflows_executed INTEGER,
                    nodes_executed INTEGER,
                    average_execution_time REAL,
                    success_rate REAL,
                    parallel_efficiency REAL
                )
            ''')
            
            conn.commit()

    def _initialize_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialise les patterns de workflows prédéfinis"""
        return {
            'mission_analysis': {
                'name': 'Analyse de Mission',
                'description': 'Workflow standard pour l\'analyse d\'une mission',
                'nodes': [
                    {'id': 'brief_analysis', 'agent': 'senior_advisor', 'method': 'analyze_brief'},
                    {'id': 'expert_selection', 'agent': 'senior_advisor', 'method': 'select_experts'},
                    {'id': 'parallel_analysis', 'type': 'parallel', 'agents': ['multiple']},
                    {'id': 'synthesis', 'agent': 'senior_advisor', 'method': 'synthesize_results'},
                    {'id': 'deliverable_generation', 'agent': 'arr', 'method': 'generate_deliverable'}
                ],
                'execution_mode': ExecutionMode.PIPELINE
            },
            'intelligence_gathering': {
                'name': 'Collecte d\'Intelligence',
                'description': 'Workflow pour la collecte d\'intelligence sectorielle',
                'nodes': [
                    {'id': 'source_identification', 'agent': 'avs', 'method': 'identify_sources'},
                    {'id': 'parallel_collection', 'type': 'parallel', 'agents': ['multiple']},
                    {'id': 'data_analysis', 'agent': 'aad', 'method': 'analyze_data'},
                    {'id': 'trend_detection', 'agent': 'aad', 'method': 'detect_trends'},
                    {'id': 'report_generation', 'agent': 'arr', 'method': 'generate_report'}
                ],
                'execution_mode': ExecutionMode.PIPELINE
            },
            'competitive_analysis': {
                'name': 'Analyse Concurrentielle',
                'description': 'Workflow pour l\'analyse concurrentielle approfondie',
                'nodes': [
                    {'id': 'competitor_identification', 'agent': 'avs', 'method': 'identify_competitors'},
                    {'id': 'market_analysis', 'agent': 'multiple', 'method': 'analyze_market'},
                    {'id': 'swot_analysis', 'agent': 'multiple', 'method': 'perform_swot'},
                    {'id': 'positioning_analysis', 'agent': 'multiple', 'method': 'analyze_positioning'},
                    {'id': 'recommendations', 'agent': 'senior_advisor', 'method': 'generate_recommendations'}
                ],
                'execution_mode': ExecutionMode.SEQUENTIAL
            },
            'financial_analysis': {
                'name': 'Analyse Financière',
                'description': 'Workflow pour l\'analyse financière complète',
                'nodes': [
                    {'id': 'data_collection', 'agent': 'efs', 'method': 'collect_financial_data'},
                    {'id': 'ratio_analysis', 'agent': 'efs', 'method': 'calculate_ratios'},
                    {'id': 'valuation', 'agent': 'efs', 'method': 'perform_valuation'},
                    {'id': 'risk_assessment', 'agent': 'efs', 'method': 'assess_risks'},
                    {'id': 'recommendations', 'agent': 'efs', 'method': 'generate_recommendations'}
                ],
                'execution_mode': ExecutionMode.SEQUENTIAL
            },
            'digital_transformation': {
                'name': 'Transformation Digitale',
                'description': 'Workflow pour l\'analyse de transformation digitale',
                'nodes': [
                    {'id': 'current_state', 'agent': 'eia', 'method': 'assess_current_state'},
                    {'id': 'technology_audit', 'agent': 'ec', 'method': 'audit_technology'},
                    {'id': 'data_strategy', 'agent': 'edata', 'method': 'design_data_strategy'},
                    {'id': 'security_assessment', 'agent': 'ecyber', 'method': 'assess_security'},
                    {'id': 'roadmap', 'agent': 'senior_advisor', 'method': 'create_roadmap'}
                ],
                'execution_mode': ExecutionMode.PIPELINE
            }
        }

    def create_workflow(self, name: str, description: str, 
                       execution_mode: ExecutionMode = ExecutionMode.SEQUENTIAL,
                       created_by: str = 'system', priority: int = 5,
                       timeout: int = 3600) -> str:
        """Crée un nouveau workflow"""
        
        workflow_id = str(uuid.uuid4())
        
        workflow = Workflow(
            workflow_id=workflow_id,
            name=name,
            description=description,
            status=WorkflowStatus.PENDING,
            execution_mode=execution_mode,
            nodes={},
            edges=[],
            variables={},
            created_at=datetime.now(),
            started_at=None,
            completed_at=None,
            created_by=created_by,
            priority=priority,
            timeout=timeout,
            result=None,
            error=None
        )
        
        self.workflows[workflow_id] = workflow
        self.workflow_graphs[workflow_id] = nx.DiGraph()
        
        # Sauvegarde en base
        self._save_workflow(workflow)
        
        self.logger.info(f"Workflow {workflow_id} créé: {name}")
        
        return workflow_id

    def add_node(self, workflow_id: str, node_id: str, name: str,
                node_type: NodeType, agent_id: str = None, method: str = None,
                parameters: Dict[str, Any] = None, conditions: List[str] = None,
                dependencies: List[str] = None, timeout: int = 300,
                max_retries: int = 3) -> bool:
        """Ajoute un nœud au workflow"""
        
        if workflow_id not in self.workflows:
            self.logger.error(f"Workflow {workflow_id} non trouvé")
            return False
        
        node = WorkflowNode(
            node_id=node_id,
            name=name,
            node_type=node_type,
            agent_id=agent_id,
            method=method,
            parameters=parameters or {},
            conditions=conditions or [],
            dependencies=dependencies or [],
            timeout=timeout,
            retry_count=0,
            max_retries=max_retries,
            status='pending',
            result=None,
            error=None,
            started_at=None,
            completed_at=None
        )
        
        workflow = self.workflows[workflow_id]
        workflow.nodes[node_id] = node
        
        # Ajout au graphe
        self.workflow_graphs[workflow_id].add_node(node_id, **asdict(node))
        
        # Sauvegarde en base
        self._save_node(workflow_id, node)
        
        self.logger.info(f"Nœud {node_id} ajouté au workflow {workflow_id}")
        
        return True

    def add_edge(self, workflow_id: str, from_node: str, to_node: str,
                condition: str = None) -> bool:
        """Ajoute une arête entre deux nœuds"""
        
        if workflow_id not in self.workflows:
            return False
        
        workflow = self.workflows[workflow_id]
        
        if from_node not in workflow.nodes or to_node not in workflow.nodes:
            return False
        
        workflow.edges.append((from_node, to_node))
        
        # Ajout au graphe
        edge_data = {'condition': condition} if condition else {}
        self.workflow_graphs[workflow_id].add_edge(from_node, to_node, **edge_data)
        
        self.logger.info(f"Arête ajoutée: {from_node} -> {to_node}")
        
        return True

    def create_from_pattern(self, pattern_name: str, parameters: Dict[str, Any] = None,
                          created_by: str = 'system') -> Optional[str]:
        """Crée un workflow à partir d'un pattern prédéfini"""
        
        if pattern_name not in self.workflow_patterns:
            self.logger.error(f"Pattern {pattern_name} non trouvé")
            return None
        
        pattern = self.workflow_patterns[pattern_name]
        
        # Création du workflow
        workflow_id = self.create_workflow(
            name=pattern['name'],
            description=pattern['description'],
            execution_mode=pattern['execution_mode'],
            created_by=created_by
        )
        
        # Ajout des nœuds
        for i, node_config in enumerate(pattern['nodes']):
            node_id = node_config.get('id', f"node_{i}")
            
            self.add_node(
                workflow_id=workflow_id,
                node_id=node_id,
                name=node_config.get('name', node_id),
                node_type=NodeType.AGENT if 'agent' in node_config else NodeType.PARALLEL,
                agent_id=node_config.get('agent'),
                method=node_config.get('method'),
                parameters=parameters or {}
            )
            
            # Ajout des dépendances séquentielles
            if i > 0:
                prev_node = pattern['nodes'][i-1].get('id', f"node_{i-1}")
                self.add_edge(workflow_id, prev_node, node_id)
        
        self.logger.info(f"Workflow créé à partir du pattern {pattern_name}: {workflow_id}")
        
        return workflow_id

    def execute_workflow(self, workflow_id: str, input_data: Dict[str, Any] = None) -> bool:
        """Exécute un workflow"""
        
        if workflow_id not in self.workflows:
            self.logger.error(f"Workflow {workflow_id} non trouvé")
            return False
        
        workflow = self.workflows[workflow_id]
        
        if workflow.status != WorkflowStatus.PENDING:
            self.logger.error(f"Workflow {workflow_id} ne peut pas être exécuté (statut: {workflow.status})")
            return False
        
        # Initialisation des variables
        if input_data:
            workflow.variables.update(input_data)
        
        # Démarrage de l'exécution
        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.now()
        
        self.active_workflows[workflow_id] = workflow
        
        # Soumission à l'exécuteur
        future = self.workflow_executor.submit(self._execute_workflow_internal, workflow_id)
        
        self.logger.info(f"Exécution du workflow {workflow_id} démarrée")
        
        return True

    def _execute_workflow_internal(self, workflow_id: str):
        """Exécution interne d'un workflow"""
        
        try:
            workflow = self.workflows[workflow_id]
            graph = self.workflow_graphs[workflow_id]
            
            if workflow.execution_mode == ExecutionMode.SEQUENTIAL:
                self._execute_sequential(workflow_id, graph)
            elif workflow.execution_mode == ExecutionMode.PARALLEL:
                self._execute_parallel(workflow_id, graph)
            elif workflow.execution_mode == ExecutionMode.PIPELINE:
                self._execute_pipeline(workflow_id, graph)
            else:
                self._execute_conditional(workflow_id, graph)
            
            # Finalisation
            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = datetime.now()
            
            # Déplacement vers les workflows terminés
            self.completed_workflows[workflow_id] = workflow
            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]
            
            self.logger.info(f"Workflow {workflow_id} terminé avec succès")
            
        except Exception as e:
            workflow = self.workflows[workflow_id]
            workflow.status = WorkflowStatus.FAILED
            workflow.error = str(e)
            workflow.completed_at = datetime.now()
            
            # Déplacement vers les workflows échoués
            self.failed_workflows[workflow_id] = workflow
            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]
            
            self.logger.error(f"Workflow {workflow_id} échoué: {e}")

    def _execute_sequential(self, workflow_id: str, graph: nx.DiGraph):
        """Exécution séquentielle"""
        
        # Tri topologique pour l'ordre d'exécution
        try:
            execution_order = list(nx.topological_sort(graph))
        except nx.NetworkXError:
            raise Exception("Cycle détecté dans le workflow")
        
        workflow = self.workflows[workflow_id]
        
        for node_id in execution_order:
            if workflow.status != WorkflowStatus.RUNNING:
                break
            
            node = workflow.nodes[node_id]
            
            # Vérification des dépendances
            if not self._check_node_dependencies(workflow_id, node_id):
                continue
            
            # Exécution du nœud
            self._execute_node(workflow_id, node_id)

    def _execute_parallel(self, workflow_id: str, graph: nx.DiGraph):
        """Exécution parallèle"""
        
        workflow = self.workflows[workflow_id]
        
        # Identification des nœuds sans dépendances
        ready_nodes = [node_id for node_id in graph.nodes() 
                      if graph.in_degree(node_id) == 0]
        
        futures = {}
        
        # Soumission des nœuds prêts
        for node_id in ready_nodes:
            future = self.node_executor.submit(self._execute_node, workflow_id, node_id)
            futures[future] = node_id
        
        # Traitement des résultats
        while futures and workflow.status == WorkflowStatus.RUNNING:
            for future in as_completed(futures, timeout=1):
                node_id = futures[future]
                del futures[future]
                
                try:
                    future.result()
                    
                    # Identification des nouveaux nœuds prêts
                    for successor in graph.successors(node_id):
                        if (self._check_node_dependencies(workflow_id, successor) and
                            successor not in [futures[f] for f in futures]):
                            
                            new_future = self.node_executor.submit(
                                self._execute_node, workflow_id, successor
                            )
                            futures[new_future] = successor
                
                except Exception as e:
                    self.logger.error(f"Erreur exécution nœud {node_id}: {e}")
                    workflow.nodes[node_id].error = str(e)
                    workflow.nodes[node_id].status = 'failed'
                
                break

    def _execute_pipeline(self, workflow_id: str, graph: nx.DiGraph):
        """Exécution en pipeline"""
        
        # Combinaison séquentielle et parallèle
        workflow = self.workflows[workflow_id]
        
        # Identification des niveaux de pipeline
        levels = self._identify_pipeline_levels(graph)
        
        for level_nodes in levels:
            if workflow.status != WorkflowStatus.RUNNING:
                break
            
            if len(level_nodes) == 1:
                # Exécution séquentielle
                self._execute_node(workflow_id, level_nodes[0])
            else:
                # Exécution parallèle
                futures = []
                for node_id in level_nodes:
                    future = self.node_executor.submit(self._execute_node, workflow_id, node_id)
                    futures.append(future)
                
                # Attente de tous les nœuds du niveau
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        self.logger.error(f"Erreur exécution pipeline: {e}")

    def _execute_conditional(self, workflow_id: str, graph: nx.DiGraph):
        """Exécution conditionnelle"""
        
        workflow = self.workflows[workflow_id]
        executed_nodes = set()
        
        # Démarrage par les nœuds racines
        root_nodes = [node_id for node_id in graph.nodes() 
                     if graph.in_degree(node_id) == 0]
        
        for root_node in root_nodes:
            self._execute_conditional_branch(workflow_id, root_node, executed_nodes)

    def _execute_conditional_branch(self, workflow_id: str, node_id: str, executed_nodes: set):
        """Exécute une branche conditionnelle"""
        
        if node_id in executed_nodes:
            return
        
        workflow = self.workflows[workflow_id]
        graph = self.workflow_graphs[workflow_id]
        
        # Exécution du nœud
        self._execute_node(workflow_id, node_id)
        executed_nodes.add(node_id)
        
        # Évaluation des conditions pour les successeurs
        for successor in graph.successors(node_id):
            edge_data = graph.get_edge_data(node_id, successor)
            condition = edge_data.get('condition') if edge_data else None
            
            if condition:
                # Évaluation de la condition
                if self._evaluate_condition(workflow_id, condition):
                    self._execute_conditional_branch(workflow_id, successor, executed_nodes)
            else:
                # Pas de condition, exécution directe
                self._execute_conditional_branch(workflow_id, successor, executed_nodes)

    def _execute_node(self, workflow_id: str, node_id: str):
        """Exécute un nœud spécifique"""
        
        workflow = self.workflows[workflow_id]
        node = workflow.nodes[node_id]
        
        self.logger.info(f"Exécution nœud {node_id} - Agent: {node.agent_id}")
        
        node.status = 'running'
        node.started_at = datetime.now()
        
        try:
            if node.node_type == NodeType.AGENT:
                # Exécution via l'agent
                if self.core_engine and node.agent_id:
                    task_id = self.core_engine.submit_task(
                        name=node.method or 'provide_expertise',
                        agent_id=node.agent_id,
                        parameters=node.parameters
                    )
                    
                    # Attente du résultat
                    timeout = node.timeout
                    start_time = time.time()
                    
                    while time.time() - start_time < timeout:
                        task_status = self.core_engine.get_task_status(task_id)
                        if task_status and task_status.get('status') in ['completed', 'failed']:
                            if task_status['status'] == 'completed':
                                node.result = task_status.get('result')
                                node.status = 'completed'
                            else:
                                node.error = task_status.get('error')
                                node.status = 'failed'
                            break
                        time.sleep(0.5)
                    else:
                        raise Exception(f"Timeout nœud {node_id}")
                else:
                    # Simulation si pas de core engine
                    time.sleep(1)
                    node.result = f"Résultat simulé pour {node_id}"
                    node.status = 'completed'
            
            elif node.node_type == NodeType.CONDITION:
                # Évaluation de condition
                result = self._evaluate_conditions(workflow_id, node.conditions)
                node.result = result
                node.status = 'completed'
            
            else:
                # Autres types de nœuds
                node.result = f"Traitement {node.node_type.value} pour {node_id}"
                node.status = 'completed'
            
            node.completed_at = datetime.now()
            
            # Mise à jour des variables du workflow
            if node.result:
                workflow.variables[f"{node_id}_result"] = node.result
            
            self.logger.info(f"Nœud {node_id} terminé avec succès")
            
        except Exception as e:
            node.error = str(e)
            node.status = 'failed'
            node.completed_at = datetime.now()
            
            # Retry si possible
            if node.retry_count < node.max_retries:
                node.retry_count += 1
                node.status = 'pending'
                node.started_at = None
                node.completed_at = None
                node.error = None
                
                self.logger.info(f"Retry nœud {node_id} ({node.retry_count}/{node.max_retries})")
                
                # Re-exécution
                time.sleep(2 ** node.retry_count)  # Backoff exponentiel
                self._execute_node(workflow_id, node_id)
            else:
                self.logger.error(f"Nœud {node_id} échoué définitivement: {e}")
        
        # Sauvegarde
        self._save_node(workflow_id, node)

    def _check_node_dependencies(self, workflow_id: str, node_id: str) -> bool:
        """Vérifie si les dépendances d'un nœud sont satisfaites"""
        
        workflow = self.workflows[workflow_id]
        graph = self.workflow_graphs[workflow_id]
        
        # Vérification des prédécesseurs
        for predecessor in graph.predecessors(node_id):
            pred_node = workflow.nodes[predecessor]
            if pred_node.status != 'completed':
                return False
        
        return True

    def _evaluate_condition(self, workflow_id: str, condition: str) -> bool:
        """Évalue une condition"""
        
        workflow = self.workflows[workflow_id]
        
        try:
            # Contexte d'évaluation avec les variables du workflow
            context = workflow.variables.copy()
            
            # Évaluation sécurisée de la condition
            # Note: En production, utiliser un évaluateur plus sécurisé
            return eval(condition, {"__builtins__": {}}, context)
            
        except Exception as e:
            self.logger.error(f"Erreur évaluation condition '{condition}': {e}")
            return False

    def _evaluate_conditions(self, workflow_id: str, conditions: List[str]) -> bool:
        """Évalue une liste de conditions"""
        
        for condition in conditions:
            if not self._evaluate_condition(workflow_id, condition):
                return False
        
        return True

    def _identify_pipeline_levels(self, graph: nx.DiGraph) -> List[List[str]]:
        """Identifie les niveaux de pipeline"""
        
        levels = []
        remaining_nodes = set(graph.nodes())
        
        while remaining_nodes:
            # Nœuds sans dépendances dans les nœuds restants
            current_level = []
            for node in remaining_nodes:
                predecessors = set(graph.predecessors(node))
                if not predecessors.intersection(remaining_nodes):
                    current_level.append(node)
            
            if not current_level:
                # Cycle détecté
                break
            
            levels.append(current_level)
            remaining_nodes -= set(current_level)
        
        return levels

    def _save_workflow(self, workflow: Workflow):
        """Sauvegarde un workflow en base"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO workflows 
                    (workflow_id, name, description, status, execution_mode, created_at,
                     started_at, completed_at, created_by, priority, timeout, result, error)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    workflow.workflow_id, workflow.name, workflow.description,
                    workflow.status.value, workflow.execution_mode.value,
                    workflow.created_at, workflow.started_at, workflow.completed_at,
                    workflow.created_by, workflow.priority, workflow.timeout,
                    json.dumps(workflow.result) if workflow.result else None,
                    workflow.error
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde workflow: {e}")

    def _save_node(self, workflow_id: str, node: WorkflowNode):
        """Sauvegarde un nœud en base"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO workflow_nodes 
                    (node_id, workflow_id, name, node_type, agent_id, method, parameters,
                     conditions, dependencies, timeout, retry_count, max_retries, status,
                     result, error, started_at, completed_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    node.node_id, workflow_id, node.name, node.node_type.value,
                    node.agent_id, node.method, json.dumps(node.parameters),
                    json.dumps(node.conditions), json.dumps(node.dependencies),
                    node.timeout, node.retry_count, node.max_retries, node.status,
                    json.dumps(node.result) if node.result else None,
                    node.error, node.started_at, node.completed_at
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde nœud: {e}")

    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Retourne le statut d'un workflow"""
        
        if workflow_id not in self.workflows:
            return None
        
        workflow = self.workflows[workflow_id]
        
        return {
            'workflow_id': workflow.workflow_id,
            'name': workflow.name,
            'status': workflow.status.value,
            'execution_mode': workflow.execution_mode.value,
            'created_at': workflow.created_at.isoformat(),
            'started_at': workflow.started_at.isoformat() if workflow.started_at else None,
            'completed_at': workflow.completed_at.isoformat() if workflow.completed_at else None,
            'nodes_total': len(workflow.nodes),
            'nodes_completed': len([n for n in workflow.nodes.values() if n.status == 'completed']),
            'nodes_failed': len([n for n in workflow.nodes.values() if n.status == 'failed']),
            'progress': self._calculate_progress(workflow_id),
            'result': workflow.result,
            'error': workflow.error
        }

    def _calculate_progress(self, workflow_id: str) -> float:
        """Calcule le progrès d'un workflow"""
        
        workflow = self.workflows[workflow_id]
        
        if not workflow.nodes:
            return 0.0
        
        completed = len([n for n in workflow.nodes.values() if n.status == 'completed'])
        total = len(workflow.nodes)
        
        return (completed / total) * 100

    def cancel_workflow(self, workflow_id: str) -> bool:
        """Annule un workflow"""
        
        if workflow_id not in self.workflows:
            return False
        
        workflow = self.workflows[workflow_id]
        
        if workflow.status not in [WorkflowStatus.PENDING, WorkflowStatus.RUNNING]:
            return False
        
        workflow.status = WorkflowStatus.CANCELLED
        workflow.completed_at = datetime.now()
        
        # Annulation des nœuds en cours
        for node in workflow.nodes.values():
            if node.status == 'running':
                node.status = 'cancelled'
                node.completed_at = datetime.now()
        
        self.logger.info(f"Workflow {workflow_id} annulé")
        
        return True

    def get_orchestration_metrics(self) -> Dict[str, Any]:
        """Retourne les métriques d'orchestration"""
        
        total_workflows = len(self.completed_workflows) + len(self.failed_workflows)
        
        if total_workflows > 0:
            self.orchestration_metrics['success_rate'] = (
                len(self.completed_workflows) / total_workflows * 100
            )
        
        return self.orchestration_metrics.copy()

# Test de l'orchestrateur
if __name__ == '__main__':
    print("=== Test System Orchestrator ===")
    
    orchestrator = SystemOrchestrator()
    
    # Test de création de workflow
    workflow_id = orchestrator.create_from_pattern('mission_analysis')
    print(f"Workflow créé: {workflow_id}")
    
    # Test d'exécution
    if workflow_id:
        success = orchestrator.execute_workflow(workflow_id, {'mission_name': 'Test Mission'})
        print(f"Exécution démarrée: {success}")
        
        # Attente et vérification
        time.sleep(5)
        status = orchestrator.get_workflow_status(workflow_id)
        if status:
            print(f"Statut: {status['status']}")
            print(f"Progrès: {status['progress']:.1f}%")
    
    print("Test terminé")

