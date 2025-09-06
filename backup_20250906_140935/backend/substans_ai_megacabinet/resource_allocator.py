#!/usr/bin/env python3
"""
Resource Allocator System - Substans.AI Enterprise
Système d'allocation intelligente des ressources avec optimisation IA et prédiction de charge
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from collections import defaultdict
import threading
import time
from pathlib import Path
import heapq
from enum import Enum

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResourceType(Enum):
    """Types de ressources"""
    AGENT = "agent"
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    LICENSE = "license"
    HUMAN = "human"

class AllocationStatus(Enum):
    """Statuts d'allocation"""
    PENDING = "pending"
    ALLOCATED = "allocated"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class Resource:
    """Ressource système"""
    id: str
    name: str
    type: ResourceType
    capacity: float
    available_capacity: float
    unit: str
    cost_per_unit: float
    capabilities: List[str]
    location: str
    status: str
    metadata: Dict[str, Any]
    created_at: datetime
    last_updated: datetime
    
    def utilization_rate(self) -> float:
        """Calcule le taux d'utilisation"""
        if self.capacity == 0:
            return 0.0
        return ((self.capacity - self.available_capacity) / self.capacity) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['type'] = self.type.value
        data['created_at'] = self.created_at.isoformat()
        data['last_updated'] = self.last_updated.isoformat()
        data['utilization_rate'] = self.utilization_rate()
        return data

@dataclass
class ResourceRequest:
    """Demande de ressource"""
    id: str
    requester_id: str
    requester_type: str
    resource_type: ResourceType
    required_capacity: float
    required_capabilities: List[str]
    priority: int  # 1-10, 10 = le plus prioritaire
    start_time: datetime
    end_time: datetime
    max_cost: Optional[float]
    preferred_location: Optional[str]
    constraints: Dict[str, Any]
    status: AllocationStatus
    created_at: datetime
    
    def duration_hours(self) -> float:
        """Calcule la durée en heures"""
        return (self.end_time - self.start_time).total_seconds() / 3600
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['resource_type'] = self.resource_type.value
        data['status'] = self.status.value
        data['start_time'] = self.start_time.isoformat()
        data['end_time'] = self.end_time.isoformat()
        data['created_at'] = self.created_at.isoformat()
        data['duration_hours'] = self.duration_hours()
        return data

@dataclass
class Allocation:
    """Allocation de ressource"""
    id: str
    request_id: str
    resource_id: str
    allocated_capacity: float
    actual_capacity: float
    start_time: datetime
    end_time: datetime
    actual_start: Optional[datetime]
    actual_end: Optional[datetime]
    cost: float
    status: AllocationStatus
    performance_metrics: Dict[str, float]
    created_at: datetime
    
    def efficiency_rate(self) -> float:
        """Calcule le taux d'efficacité"""
        if self.allocated_capacity == 0:
            return 0.0
        return (self.actual_capacity / self.allocated_capacity) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['status'] = self.status.value
        data['start_time'] = self.start_time.isoformat()
        data['end_time'] = self.end_time.isoformat()
        data['actual_start'] = self.actual_start.isoformat() if self.actual_start else None
        data['actual_end'] = self.actual_end.isoformat() if self.actual_end else None
        data['created_at'] = self.created_at.isoformat()
        data['efficiency_rate'] = self.efficiency_rate()
        return data

class ResourceAllocator:
    """Système d'allocation intelligente des ressources"""
    
    def __init__(self, db_path: str = "resource_allocator.db"):
        self.db_path = db_path
        self.running = False
        self.allocator_thread = None
        
        # Configuration des algorithmes d'allocation
        self.allocation_algorithms = {
            'first_fit': self._first_fit_allocation,
            'best_fit': self._best_fit_allocation,
            'worst_fit': self._worst_fit_allocation,
            'priority_based': self._priority_based_allocation,
            'cost_optimized': self._cost_optimized_allocation,
            'ai_optimized': self._ai_optimized_allocation
        }
        
        # Configuration des ressources par défaut
        self.default_resources = {
            'senior_advisor': {
                'name': 'Senior Advisor',
                'type': ResourceType.AGENT,
                'capacity': 100.0,
                'unit': 'hours',
                'cost_per_unit': 500.0,
                'capabilities': ['strategy', 'leadership', 'coordination', 'analysis'],
                'location': 'cloud'
            },
            'data_analyst': {
                'name': 'Agent Analyse Données',
                'type': ResourceType.AGENT,
                'capacity': 168.0,  # 24/7
                'unit': 'hours',
                'cost_per_unit': 200.0,
                'capabilities': ['data_analysis', 'statistics', 'visualization', 'reporting'],
                'location': 'cloud'
            },
            'compute_cluster': {
                'name': 'Cluster de Calcul',
                'type': ResourceType.COMPUTE,
                'capacity': 1000.0,
                'unit': 'cpu_hours',
                'cost_per_unit': 50.0,
                'capabilities': ['ml_training', 'data_processing', 'simulation'],
                'location': 'datacenter'
            },
            'storage_system': {
                'name': 'Système de Stockage',
                'type': ResourceType.STORAGE,
                'capacity': 10000.0,
                'unit': 'GB',
                'cost_per_unit': 0.1,
                'capabilities': ['data_storage', 'backup', 'archiving'],
                'location': 'cloud'
            }
        }
        
        self._init_database()
        self._init_default_resources()
        logger.info("Resource Allocator System initialisé")
    
    def _init_database(self):
        """Initialise la base de données"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS resources (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    capacity REAL NOT NULL,
                    available_capacity REAL NOT NULL,
                    unit TEXT NOT NULL,
                    cost_per_unit REAL NOT NULL,
                    capabilities TEXT NOT NULL,
                    location TEXT NOT NULL,
                    status TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_updated TEXT NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS resource_requests (
                    id TEXT PRIMARY KEY,
                    requester_id TEXT NOT NULL,
                    requester_type TEXT NOT NULL,
                    resource_type TEXT NOT NULL,
                    required_capacity REAL NOT NULL,
                    required_capabilities TEXT NOT NULL,
                    priority INTEGER NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    max_cost REAL,
                    preferred_location TEXT,
                    constraints TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS allocations (
                    id TEXT PRIMARY KEY,
                    request_id TEXT NOT NULL,
                    resource_id TEXT NOT NULL,
                    allocated_capacity REAL NOT NULL,
                    actual_capacity REAL NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    actual_start TEXT,
                    actual_end TEXT,
                    cost REAL NOT NULL,
                    status TEXT NOT NULL,
                    performance_metrics TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (request_id) REFERENCES resource_requests (id),
                    FOREIGN KEY (resource_id) REFERENCES resources (id)
                );
                
                CREATE TABLE IF NOT EXISTS usage_history (
                    id TEXT PRIMARY KEY,
                    resource_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    utilization_rate REAL NOT NULL,
                    performance_score REAL NOT NULL,
                    cost REAL NOT NULL,
                    metadata TEXT NOT NULL,
                    FOREIGN KEY (resource_id) REFERENCES resources (id)
                );
                
                CREATE TABLE IF NOT EXISTS predictions (
                    id TEXT PRIMARY KEY,
                    resource_type TEXT NOT NULL,
                    prediction_type TEXT NOT NULL,
                    time_horizon TEXT NOT NULL,
                    predicted_value REAL NOT NULL,
                    confidence REAL NOT NULL,
                    factors TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                
                CREATE INDEX IF NOT EXISTS idx_requests_status ON resource_requests(status);
                CREATE INDEX IF NOT EXISTS idx_allocations_status ON allocations(status);
                CREATE INDEX IF NOT EXISTS idx_usage_timestamp ON usage_history(timestamp);
                CREATE INDEX IF NOT EXISTS idx_resources_type ON resources(type);
            """)
    
    def _init_default_resources(self):
        """Initialise les ressources par défaut"""
        for resource_id, config in self.default_resources.items():
            resource = Resource(
                id=resource_id,
                name=config['name'],
                type=config['type'],
                capacity=config['capacity'],
                available_capacity=config['capacity'],
                unit=config['unit'],
                cost_per_unit=config['cost_per_unit'],
                capabilities=config['capabilities'],
                location=config['location'],
                status='active',
                metadata={},
                created_at=datetime.now(),
                last_updated=datetime.now()
            )
            self.add_resource(resource)
    
    def add_resource(self, resource: Resource):
        """Ajoute une ressource au système"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO resources 
                (id, name, type, capacity, available_capacity, unit, cost_per_unit,
                 capabilities, location, status, metadata, created_at, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                resource.id, resource.name, resource.type.value, resource.capacity,
                resource.available_capacity, resource.unit, resource.cost_per_unit,
                json.dumps(resource.capabilities), resource.location, resource.status,
                json.dumps(resource.metadata), resource.created_at.isoformat(),
                resource.last_updated.isoformat()
            ))
        
        logger.info(f"Ressource ajoutée: {resource.name} ({resource.id})")
    
    def request_resource(self, request: ResourceRequest) -> str:
        """Demande une allocation de ressource"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO resource_requests 
                (id, requester_id, requester_type, resource_type, required_capacity,
                 required_capabilities, priority, start_time, end_time, max_cost,
                 preferred_location, constraints, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                request.id, request.requester_id, request.requester_type,
                request.resource_type.value, request.required_capacity,
                json.dumps(request.required_capabilities), request.priority,
                request.start_time.isoformat(), request.end_time.isoformat(),
                request.max_cost, request.preferred_location,
                json.dumps(request.constraints), request.status.value,
                request.created_at.isoformat()
            ))
        
        # Tenter l'allocation immédiate
        allocation = self.allocate_resource(request.id)
        
        logger.info(f"Demande de ressource créée: {request.id}")
        return request.id
    
    def allocate_resource(self, request_id: str, 
                         algorithm: str = 'ai_optimized') -> Optional[Allocation]:
        """Alloue une ressource selon l'algorithme spécifié"""
        # Récupérer la demande
        request = self.get_request(request_id)
        if not request or request.status != AllocationStatus.PENDING:
            return None
        
        # Récupérer les ressources compatibles
        compatible_resources = self._find_compatible_resources(request)
        if not compatible_resources:
            logger.warning(f"Aucune ressource compatible pour la demande {request_id}")
            return None
        
        # Appliquer l'algorithme d'allocation
        allocation_func = self.allocation_algorithms.get(algorithm, self._ai_optimized_allocation)
        allocation = allocation_func(request, compatible_resources)
        
        if allocation:
            # Sauvegarder l'allocation
            self._save_allocation(allocation)
            
            # Mettre à jour la disponibilité de la ressource
            self._update_resource_availability(allocation.resource_id, 
                                             -allocation.allocated_capacity)
            
            # Mettre à jour le statut de la demande
            self._update_request_status(request_id, AllocationStatus.ALLOCATED)
            
            logger.info(f"Ressource allouée: {allocation.resource_id} pour {request_id}")
        
        return allocation
    
    def _find_compatible_resources(self, request: ResourceRequest) -> List[Resource]:
        """Trouve les ressources compatibles avec une demande"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM resources 
                WHERE type = ? AND status = 'active' AND available_capacity >= ?
            """, (request.resource_type.value, request.required_capacity))
            
            compatible = []
            for row in cursor.fetchall():
                resource = Resource(
                    id=row['id'],
                    name=row['name'],
                    type=ResourceType(row['type']),
                    capacity=row['capacity'],
                    available_capacity=row['available_capacity'],
                    unit=row['unit'],
                    cost_per_unit=row['cost_per_unit'],
                    capabilities=json.loads(row['capabilities']),
                    location=row['location'],
                    status=row['status'],
                    metadata=json.loads(row['metadata']),
                    created_at=datetime.fromisoformat(row['created_at']),
                    last_updated=datetime.fromisoformat(row['last_updated'])
                )
                
                # Vérifier les capacités requises
                if all(cap in resource.capabilities for cap in request.required_capabilities):
                    # Vérifier la localisation préférée
                    if not request.preferred_location or resource.location == request.preferred_location:
                        compatible.append(resource)
            
            return compatible
    
    def _first_fit_allocation(self, request: ResourceRequest, 
                            resources: List[Resource]) -> Optional[Allocation]:
        """Algorithme First Fit - première ressource disponible"""
        for resource in resources:
            if resource.available_capacity >= request.required_capacity:
                return self._create_allocation(request, resource, request.required_capacity)
        return None
    
    def _best_fit_allocation(self, request: ResourceRequest, 
                           resources: List[Resource]) -> Optional[Allocation]:
        """Algorithme Best Fit - ressource avec le moins de gaspillage"""
        best_resource = None
        min_waste = float('inf')
        
        for resource in resources:
            if resource.available_capacity >= request.required_capacity:
                waste = resource.available_capacity - request.required_capacity
                if waste < min_waste:
                    min_waste = waste
                    best_resource = resource
        
        if best_resource:
            return self._create_allocation(request, best_resource, request.required_capacity)
        return None
    
    def _worst_fit_allocation(self, request: ResourceRequest, 
                            resources: List[Resource]) -> Optional[Allocation]:
        """Algorithme Worst Fit - ressource avec le plus de capacité restante"""
        worst_resource = None
        max_remaining = 0
        
        for resource in resources:
            if resource.available_capacity >= request.required_capacity:
                remaining = resource.available_capacity - request.required_capacity
                if remaining > max_remaining:
                    max_remaining = remaining
                    worst_resource = resource
        
        if worst_resource:
            return self._create_allocation(request, worst_resource, request.required_capacity)
        return None
    
    def _priority_based_allocation(self, request: ResourceRequest, 
                                 resources: List[Resource]) -> Optional[Allocation]:
        """Algorithme basé sur la priorité et l'efficacité"""
        # Trier par utilisation croissante (préférer les ressources moins utilisées)
        resources.sort(key=lambda r: r.utilization_rate())
        
        for resource in resources:
            if resource.available_capacity >= request.required_capacity:
                return self._create_allocation(request, resource, request.required_capacity)
        return None
    
    def _cost_optimized_allocation(self, request: ResourceRequest, 
                                 resources: List[Resource]) -> Optional[Allocation]:
        """Algorithme optimisé pour le coût"""
        # Trier par coût croissant
        resources.sort(key=lambda r: r.cost_per_unit)
        
        for resource in resources:
            if resource.available_capacity >= request.required_capacity:
                cost = resource.cost_per_unit * request.required_capacity * request.duration_hours()
                if not request.max_cost or cost <= request.max_cost:
                    return self._create_allocation(request, resource, request.required_capacity)
        return None
    
    def _ai_optimized_allocation(self, request: ResourceRequest, 
                               resources: List[Resource]) -> Optional[Allocation]:
        """Algorithme optimisé par IA - score composite"""
        scored_resources = []
        
        for resource in resources:
            if resource.available_capacity >= request.required_capacity:
                # Calculer le score composite
                score = self._calculate_allocation_score(request, resource)
                scored_resources.append((score, resource))
        
        if scored_resources:
            # Trier par score décroissant
            scored_resources.sort(key=lambda x: x[0], reverse=True)
            best_resource = scored_resources[0][1]
            return self._create_allocation(request, best_resource, request.required_capacity)
        
        return None
    
    def _calculate_allocation_score(self, request: ResourceRequest, 
                                  resource: Resource) -> float:
        """Calcule un score composite pour l'allocation"""
        score = 0.0
        
        # Facteur d'utilisation (préférer les ressources moins utilisées)
        utilization = resource.utilization_rate()
        utilization_score = max(0, 100 - utilization) / 100
        score += utilization_score * 0.3
        
        # Facteur de coût (préférer les ressources moins chères)
        if request.max_cost:
            cost = resource.cost_per_unit * request.required_capacity * request.duration_hours()
            cost_score = max(0, (request.max_cost - cost) / request.max_cost)
            score += cost_score * 0.25
        else:
            score += 0.25  # Score neutre si pas de contrainte de coût
        
        # Facteur de capacité (préférer les ressources avec capacité adaptée)
        capacity_ratio = request.required_capacity / resource.capacity
        if 0.3 <= capacity_ratio <= 0.8:  # Zone optimale
            capacity_score = 1.0
        else:
            capacity_score = max(0, 1 - abs(capacity_ratio - 0.55) / 0.45)
        score += capacity_score * 0.2
        
        # Facteur de localisation
        location_score = 1.0 if (not request.preferred_location or 
                               resource.location == request.preferred_location) else 0.5
        score += location_score * 0.15
        
        # Facteur de capacités (bonus pour capacités supplémentaires)
        required_caps = set(request.required_capabilities)
        resource_caps = set(resource.capabilities)
        extra_caps = resource_caps - required_caps
        capabilities_score = min(1.0, len(extra_caps) * 0.1)
        score += capabilities_score * 0.1
        
        return score
    
    def _create_allocation(self, request: ResourceRequest, resource: Resource, 
                         capacity: float) -> Allocation:
        """Crée une allocation"""
        cost = resource.cost_per_unit * capacity * request.duration_hours()
        
        allocation = Allocation(
            id=f"alloc_{request.id}_{resource.id}_{int(time.time())}",
            request_id=request.id,
            resource_id=resource.id,
            allocated_capacity=capacity,
            actual_capacity=0.0,  # Sera mis à jour pendant l'exécution
            start_time=request.start_time,
            end_time=request.end_time,
            actual_start=None,
            actual_end=None,
            cost=cost,
            status=AllocationStatus.ALLOCATED,
            performance_metrics={},
            created_at=datetime.now()
        )
        
        return allocation
    
    def _save_allocation(self, allocation: Allocation):
        """Sauvegarde une allocation"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO allocations 
                (id, request_id, resource_id, allocated_capacity, actual_capacity,
                 start_time, end_time, actual_start, actual_end, cost, status,
                 performance_metrics, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                allocation.id, allocation.request_id, allocation.resource_id,
                allocation.allocated_capacity, allocation.actual_capacity,
                allocation.start_time.isoformat(), allocation.end_time.isoformat(),
                allocation.actual_start.isoformat() if allocation.actual_start else None,
                allocation.actual_end.isoformat() if allocation.actual_end else None,
                allocation.cost, allocation.status.value,
                json.dumps(allocation.performance_metrics),
                allocation.created_at.isoformat()
            ))
    
    def _update_resource_availability(self, resource_id: str, capacity_change: float):
        """Met à jour la disponibilité d'une ressource"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE resources 
                SET available_capacity = available_capacity + ?,
                    last_updated = ?
                WHERE id = ?
            """, (capacity_change, datetime.now().isoformat(), resource_id))
    
    def _update_request_status(self, request_id: str, status: AllocationStatus):
        """Met à jour le statut d'une demande"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE resource_requests 
                SET status = ?
                WHERE id = ?
            """, (status.value, request_id))
    
    def get_request(self, request_id: str) -> Optional[ResourceRequest]:
        """Récupère une demande de ressource"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM resource_requests WHERE id = ?", (request_id,))
            row = cursor.fetchone()
            
            if row:
                return ResourceRequest(
                    id=row['id'],
                    requester_id=row['requester_id'],
                    requester_type=row['requester_type'],
                    resource_type=ResourceType(row['resource_type']),
                    required_capacity=row['required_capacity'],
                    required_capabilities=json.loads(row['required_capabilities']),
                    priority=row['priority'],
                    start_time=datetime.fromisoformat(row['start_time']),
                    end_time=datetime.fromisoformat(row['end_time']),
                    max_cost=row['max_cost'],
                    preferred_location=row['preferred_location'],
                    constraints=json.loads(row['constraints']),
                    status=AllocationStatus(row['status']),
                    created_at=datetime.fromisoformat(row['created_at'])
                )
            return None
    
    def get_resources(self, resource_type: Optional[ResourceType] = None) -> List[Resource]:
        """Récupère les ressources"""
        query = "SELECT * FROM resources"
        params = []
        
        if resource_type:
            query += " WHERE type = ?"
            params.append(resource_type.value)
        
        query += " ORDER BY name"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            
            resources = []
            for row in cursor.fetchall():
                resource = Resource(
                    id=row['id'],
                    name=row['name'],
                    type=ResourceType(row['type']),
                    capacity=row['capacity'],
                    available_capacity=row['available_capacity'],
                    unit=row['unit'],
                    cost_per_unit=row['cost_per_unit'],
                    capabilities=json.loads(row['capabilities']),
                    location=row['location'],
                    status=row['status'],
                    metadata=json.loads(row['metadata']),
                    created_at=datetime.fromisoformat(row['created_at']),
                    last_updated=datetime.fromisoformat(row['last_updated'])
                )
                resources.append(resource)
            
            return resources
    
    def get_allocations(self, status: Optional[AllocationStatus] = None) -> List[Allocation]:
        """Récupère les allocations"""
        query = "SELECT * FROM allocations"
        params = []
        
        if status:
            query += " WHERE status = ?"
            params.append(status.value)
        
        query += " ORDER BY created_at DESC"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            
            allocations = []
            for row in cursor.fetchall():
                allocation = Allocation(
                    id=row['id'],
                    request_id=row['request_id'],
                    resource_id=row['resource_id'],
                    allocated_capacity=row['allocated_capacity'],
                    actual_capacity=row['actual_capacity'],
                    start_time=datetime.fromisoformat(row['start_time']),
                    end_time=datetime.fromisoformat(row['end_time']),
                    actual_start=datetime.fromisoformat(row['actual_start']) if row['actual_start'] else None,
                    actual_end=datetime.fromisoformat(row['actual_end']) if row['actual_end'] else None,
                    cost=row['cost'],
                    status=AllocationStatus(row['status']),
                    performance_metrics=json.loads(row['performance_metrics']),
                    created_at=datetime.fromisoformat(row['created_at'])
                )
                allocations.append(allocation)
            
            return allocations
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Récupère les données pour le dashboard"""
        resources = self.get_resources()
        allocations = self.get_allocations()
        
        # Statistiques par type de ressource
        resource_stats = defaultdict(lambda: {
            'count': 0, 'total_capacity': 0, 'available_capacity': 0,
            'avg_utilization': 0, 'total_cost': 0
        })
        
        for resource in resources:
            stats = resource_stats[resource.type.value]
            stats['count'] += 1
            stats['total_capacity'] += resource.capacity
            stats['available_capacity'] += resource.available_capacity
            stats['total_cost'] += resource.cost_per_unit * resource.capacity
        
        # Calculer les utilisations moyennes
        for resource_type, stats in resource_stats.items():
            if stats['total_capacity'] > 0:
                used_capacity = stats['total_capacity'] - stats['available_capacity']
                stats['avg_utilization'] = (used_capacity / stats['total_capacity']) * 100
        
        # Statistiques d'allocation
        allocation_stats = defaultdict(int)
        total_cost = 0
        for allocation in allocations:
            allocation_stats[allocation.status.value] += 1
            total_cost += allocation.cost
        
        # Prédictions de charge
        predictions = self._predict_resource_demand()
        
        return {
            'resources': {
                'total': len(resources),
                'by_type': dict(resource_stats),
                'active': len([r for r in resources if r.status == 'active'])
            },
            'allocations': {
                'total': len(allocations),
                'by_status': dict(allocation_stats),
                'total_cost': total_cost
            },
            'predictions': predictions,
            'alerts': self._get_resource_alerts(),
            'last_updated': datetime.now().isoformat()
        }
    
    def _predict_resource_demand(self) -> Dict[str, Any]:
        """Prédit la demande future de ressources"""
        # Analyse simple basée sur l'historique récent
        predictions = {}
        
        # Récupérer l'historique des 30 derniers jours
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT resource_type, COUNT(*) as request_count,
                       AVG(required_capacity) as avg_capacity
                FROM resource_requests 
                WHERE created_at >= ? AND created_at <= ?
                GROUP BY resource_type
            """, (start_date.isoformat(), end_date.isoformat()))
            
            for row in cursor.fetchall():
                resource_type = row['resource_type']
                daily_requests = row['request_count'] / 30
                avg_capacity = row['avg_capacity']
                
                # Prédiction simple: tendance linéaire
                predicted_requests_7d = daily_requests * 7
                predicted_capacity_7d = predicted_requests_7d * avg_capacity
                
                predictions[resource_type] = {
                    'predicted_requests_7d': predicted_requests_7d,
                    'predicted_capacity_7d': predicted_capacity_7d,
                    'confidence': 0.7,  # Confiance basique
                    'trend': 'stable'  # Simplification
                }
        
        return predictions
    
    def _get_resource_alerts(self) -> List[Dict[str, Any]]:
        """Récupère les alertes de ressources"""
        alerts = []
        resources = self.get_resources()
        
        for resource in resources:
            utilization = resource.utilization_rate()
            
            # Alerte haute utilisation
            if utilization > 90:
                alerts.append({
                    'type': 'high_utilization',
                    'severity': 'critical',
                    'resource_id': resource.id,
                    'resource_name': resource.name,
                    'message': f"Utilisation critique: {utilization:.1f}%",
                    'value': utilization
                })
            elif utilization > 80:
                alerts.append({
                    'type': 'high_utilization',
                    'severity': 'warning',
                    'resource_id': resource.id,
                    'resource_name': resource.name,
                    'message': f"Utilisation élevée: {utilization:.1f}%",
                    'value': utilization
                })
            
            # Alerte faible utilisation
            elif utilization < 10 and resource.status == 'active':
                alerts.append({
                    'type': 'low_utilization',
                    'severity': 'info',
                    'resource_id': resource.id,
                    'resource_name': resource.name,
                    'message': f"Utilisation faible: {utilization:.1f}%",
                    'value': utilization
                })
        
        return alerts
    
    def start_allocator_service(self):
        """Démarre le service d'allocation en arrière-plan"""
        if self.running:
            return
        
        self.running = True
        self.allocator_thread = threading.Thread(target=self._allocator_loop, daemon=True)
        self.allocator_thread.start()
        logger.info("Service d'allocation démarré")
    
    def stop_allocator_service(self):
        """Arrête le service d'allocation"""
        self.running = False
        if self.allocator_thread:
            self.allocator_thread.join()
        logger.info("Service d'allocation arrêté")
    
    def _allocator_loop(self):
        """Boucle principale du service d'allocation"""
        while self.running:
            try:
                # Traiter les demandes en attente
                with sqlite3.connect(self.db_path) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.execute("""
                        SELECT id FROM resource_requests 
                        WHERE status = 'pending' 
                        ORDER BY priority DESC, created_at ASC
                    """)
                    
                    pending_requests = [row['id'] for row in cursor.fetchall()]
                
                for request_id in pending_requests:
                    self.allocate_resource(request_id)
                
                # Libérer les ressources des allocations terminées
                self._cleanup_completed_allocations()
                
                # Enregistrer les métriques d'utilisation
                self._record_usage_metrics()
                
                time.sleep(60)  # Attendre 1 minute
                
            except Exception as e:
                logger.error(f"Erreur dans la boucle d'allocation: {e}")
                time.sleep(10)
    
    def _cleanup_completed_allocations(self):
        """Nettoie les allocations terminées"""
        now = datetime.now()
        
        with sqlite3.connect(self.db_path) as conn:
            # Trouver les allocations expirées
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM allocations 
                WHERE status IN ('allocated', 'active') AND end_time < ?
            """, (now.isoformat(),))
            
            for row in cursor.fetchall():
                allocation_id = row['id']
                resource_id = row['resource_id']
                allocated_capacity = row['allocated_capacity']
                
                # Marquer comme terminée
                conn.execute("""
                    UPDATE allocations 
                    SET status = 'completed', actual_end = ?
                    WHERE id = ?
                """, (now.isoformat(), allocation_id))
                
                # Libérer la capacité
                self._update_resource_availability(resource_id, allocated_capacity)
                
                logger.info(f"Allocation terminée et nettoyée: {allocation_id}")
    
    def _record_usage_metrics(self):
        """Enregistre les métriques d'utilisation"""
        resources = self.get_resources()
        
        for resource in resources:
            utilization = resource.utilization_rate()
            performance_score = min(100, max(0, 100 - abs(utilization - 75)))  # Optimal à 75%
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO usage_history 
                    (id, resource_id, timestamp, utilization_rate, performance_score, cost, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"usage_{resource.id}_{int(time.time())}",
                    resource.id, datetime.now().isoformat(),
                    utilization, performance_score,
                    resource.cost_per_unit * (resource.capacity - resource.available_capacity),
                    json.dumps({'status': resource.status})
                ))

# Exemple d'utilisation
if __name__ == "__main__":
    # Créer le système d'allocation
    allocator = ResourceAllocator()
    
    # Démarrer le service
    allocator.start_allocator_service()
    
    # Créer une demande de ressource d'exemple
    request = ResourceRequest(
        id="req_test_001",
        requester_id="mission_bull_001",
        requester_type="mission",
        resource_type=ResourceType.AGENT,
        required_capacity=40.0,
        required_capabilities=["strategy", "analysis"],
        priority=8,
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(hours=48),
        max_cost=50000.0,
        preferred_location="cloud",
        constraints={},
        status=AllocationStatus.PENDING,
        created_at=datetime.now()
    )
    
    # Demander l'allocation
    request_id = allocator.request_resource(request)
    print(f"Demande créée: {request_id}")
    
    # Afficher le dashboard
    dashboard = allocator.get_dashboard_data()
    print(f"Ressources totales: {dashboard['resources']['total']}")
    print(f"Allocations totales: {dashboard['allocations']['total']}")
    print(f"Coût total: {dashboard['allocations']['total_cost']:.2f}€")
    print(f"Alertes: {len(dashboard['alerts'])}")
    
    # Arrêter le service
    allocator.stop_allocator_service()

