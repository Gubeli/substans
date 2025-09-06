#!/usr/bin/env python3
"""
RBAC System - Substans.AI Enterprise
Système de contrôle d'accès basé sur les rôles (Role-Based Access Control)
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import secrets
import threading
import time
from collections import defaultdict

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PermissionType(Enum):
    """Types de permissions"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXECUTE = "execute"
    ADMIN = "admin"
    CREATE = "create"
    UPDATE = "update"
    MANAGE = "manage"

class ResourceType(Enum):
    """Types de ressources"""
    USER = "user"
    MISSION = "mission"
    AGENT = "agent"
    DOCUMENT = "document"
    SYSTEM = "system"
    API = "api"
    REPORT = "report"
    ANALYTICS = "analytics"
    SECURITY = "security"
    CONFIGURATION = "configuration"

class AccessResult(Enum):
    """Résultats d'accès"""
    GRANTED = "granted"
    DENIED = "denied"
    CONDITIONAL = "conditional"
    EXPIRED = "expired"

@dataclass
class Permission:
    """Permission système"""
    id: str
    name: str
    description: str
    resource_type: ResourceType
    permission_type: PermissionType
    conditions: Dict[str, Any]
    active: bool
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['resource_type'] = self.resource_type.value
        data['permission_type'] = self.permission_type.value
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data

@dataclass
class Role:
    """Rôle utilisateur"""
    id: str
    name: str
    description: str
    permissions: List[str]
    parent_roles: List[str]
    conditions: Dict[str, Any]
    priority: int
    active: bool
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data

@dataclass
class AccessPolicy:
    """Politique d'accès"""
    id: str
    name: str
    description: str
    resource_pattern: str
    conditions: Dict[str, Any]
    effect: str  # allow, deny
    priority: int
    active: bool
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data

@dataclass
class AccessRequest:
    """Demande d'accès"""
    user_id: str
    resource_type: ResourceType
    resource_id: str
    permission_type: PermissionType
    context: Dict[str, Any]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['resource_type'] = self.resource_type.value
        data['permission_type'] = self.permission_type.value
        data['timestamp'] = self.timestamp.isoformat()
        return data

@dataclass
class AccessLog:
    """Log d'accès"""
    id: str
    user_id: str
    resource_type: ResourceType
    resource_id: str
    permission_type: PermissionType
    result: AccessResult
    reason: str
    context: Dict[str, Any]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['resource_type'] = self.resource_type.value
        data['permission_type'] = self.permission_type.value
        data['result'] = self.result.value
        data['timestamp'] = self.timestamp.isoformat()
        return data

class RBACSystem:
    """Système RBAC Enterprise"""
    
    def __init__(self, db_path: str = "rbac.db"):
        self.db_path = db_path
        
        # Cache des permissions et rôles
        self.permission_cache = {}
        self.role_cache = {}
        self.user_roles_cache = {}
        self.cache_ttl = 300  # 5 minutes
        self.cache_timestamps = {}
        
        # Statistiques d'accès
        self.access_stats = defaultdict(int)
        
        # Permissions par défaut par ressource
        self.default_permissions = {
            ResourceType.USER: [PermissionType.READ, PermissionType.UPDATE],
            ResourceType.MISSION: [PermissionType.READ, PermissionType.WRITE, PermissionType.CREATE],
            ResourceType.AGENT: [PermissionType.READ, PermissionType.EXECUTE],
            ResourceType.DOCUMENT: [PermissionType.READ, PermissionType.WRITE, PermissionType.CREATE],
            ResourceType.SYSTEM: [PermissionType.READ],
            ResourceType.API: [PermissionType.READ, PermissionType.EXECUTE],
            ResourceType.REPORT: [PermissionType.READ, PermissionType.CREATE],
            ResourceType.ANALYTICS: [PermissionType.READ],
            ResourceType.SECURITY: [PermissionType.READ],
            ResourceType.CONFIGURATION: [PermissionType.READ]
        }
        
        # Rôles par défaut
        self.default_roles = {
            'admin': {
                'name': 'Administrateur',
                'description': 'Accès complet au système',
                'permissions': ['*'],
                'priority': 100
            },
            'manager': {
                'name': 'Manager',
                'description': 'Gestion des missions et équipes',
                'permissions': [
                    'mission:*', 'user:read', 'user:update', 'agent:*',
                    'document:*', 'report:*', 'analytics:read'
                ],
                'priority': 80
            },
            'consultant': {
                'name': 'Consultant',
                'description': 'Travail sur les missions assignées',
                'permissions': [
                    'mission:read', 'mission:write', 'agent:read', 'agent:execute',
                    'document:read', 'document:write', 'document:create', 'report:read'
                ],
                'priority': 60
            },
            'analyst': {
                'name': 'Analyste',
                'description': 'Analyse de données et reporting',
                'permissions': [
                    'mission:read', 'document:read', 'report:*', 'analytics:*',
                    'agent:read', 'agent:execute'
                ],
                'priority': 50
            },
            'viewer': {
                'name': 'Lecteur',
                'description': 'Accès en lecture seule',
                'permissions': [
                    'mission:read', 'document:read', 'report:read', 'analytics:read'
                ],
                'priority': 20
            }
        }
        
        self._init_database()
        self._init_default_permissions()
        self._init_default_roles()
        self._start_cache_cleanup()
        
        logger.info("RBAC System initialisé")
    
    def _init_database(self):
        """Initialise la base de données RBAC"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS permissions (
                    id TEXT PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT NOT NULL,
                    resource_type TEXT NOT NULL,
                    permission_type TEXT NOT NULL,
                    conditions TEXT NOT NULL,
                    active BOOLEAN DEFAULT TRUE,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS roles (
                    id TEXT PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT NOT NULL,
                    permissions TEXT NOT NULL,
                    parent_roles TEXT NOT NULL,
                    conditions TEXT NOT NULL,
                    priority INTEGER DEFAULT 0,
                    active BOOLEAN DEFAULT TRUE,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS user_roles (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    role_id TEXT NOT NULL,
                    granted_by TEXT NOT NULL,
                    granted_at TEXT NOT NULL,
                    expires_at TEXT,
                    conditions TEXT NOT NULL,
                    active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (role_id) REFERENCES roles (id),
                    UNIQUE(user_id, role_id)
                );
                
                CREATE TABLE IF NOT EXISTS access_policies (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    resource_pattern TEXT NOT NULL,
                    conditions TEXT NOT NULL,
                    effect TEXT NOT NULL,
                    priority INTEGER DEFAULT 0,
                    active BOOLEAN DEFAULT TRUE,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS access_logs (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    resource_type TEXT NOT NULL,
                    resource_id TEXT NOT NULL,
                    permission_type TEXT NOT NULL,
                    result TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    context TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS temporary_permissions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    permission_id TEXT NOT NULL,
                    granted_by TEXT NOT NULL,
                    granted_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (permission_id) REFERENCES permissions (id)
                );
                
                CREATE INDEX IF NOT EXISTS idx_user_roles_user_id ON user_roles(user_id);
                CREATE INDEX IF NOT EXISTS idx_access_logs_user_id ON access_logs(user_id);
                CREATE INDEX IF NOT EXISTS idx_access_logs_timestamp ON access_logs(timestamp);
                CREATE INDEX IF NOT EXISTS idx_temporary_permissions_user_id ON temporary_permissions(user_id);
                CREATE INDEX IF NOT EXISTS idx_temporary_permissions_expires_at ON temporary_permissions(expires_at);
            """)
    
    def _init_default_permissions(self):
        """Initialise les permissions par défaut"""
        for resource_type, permission_types in self.default_permissions.items():
            for permission_type in permission_types:
                permission_id = f"{resource_type.value}_{permission_type.value}"
                
                # Vérifier si la permission existe déjà
                if self.get_permission(permission_id):
                    continue
                
                permission = Permission(
                    id=permission_id,
                    name=f"{resource_type.value.title()} {permission_type.value.title()}",
                    description=f"Permission {permission_type.value} sur {resource_type.value}",
                    resource_type=resource_type,
                    permission_type=permission_type,
                    conditions={},
                    active=True,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
                self.create_permission(permission)
        
        # Permissions spéciales
        special_permissions = [
            {
                'id': 'system_admin',
                'name': 'Administration Système',
                'description': 'Accès complet à l\'administration système',
                'resource_type': ResourceType.SYSTEM,
                'permission_type': PermissionType.ADMIN,
                'conditions': {'require_mfa': True}
            },
            {
                'id': 'security_manage',
                'name': 'Gestion Sécurité',
                'description': 'Gestion des paramètres de sécurité',
                'resource_type': ResourceType.SECURITY,
                'permission_type': PermissionType.MANAGE,
                'conditions': {'require_mfa': True, 'ip_whitelist': True}
            },
            {
                'id': 'user_manage',
                'name': 'Gestion Utilisateurs',
                'description': 'Création et gestion des utilisateurs',
                'resource_type': ResourceType.USER,
                'permission_type': PermissionType.MANAGE,
                'conditions': {}
            }
        ]
        
        for perm_config in special_permissions:
            if self.get_permission(perm_config['id']):
                continue
            
            permission = Permission(
                id=perm_config['id'],
                name=perm_config['name'],
                description=perm_config['description'],
                resource_type=perm_config['resource_type'],
                permission_type=perm_config['permission_type'],
                conditions=perm_config['conditions'],
                active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.create_permission(permission)
    
    def _init_default_roles(self):
        """Initialise les rôles par défaut"""
        for role_id, config in self.default_roles.items():
            # Vérifier si le rôle existe déjà
            if self.get_role(role_id):
                continue
            
            role = Role(
                id=role_id,
                name=config['name'],
                description=config['description'],
                permissions=config['permissions'],
                parent_roles=[],
                conditions={},
                priority=config['priority'],
                active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.create_role(role)
    
    def create_permission(self, permission: Permission) -> bool:
        """Crée une nouvelle permission"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO permissions 
                    (id, name, description, resource_type, permission_type, 
                     conditions, active, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    permission.id, permission.name, permission.description,
                    permission.resource_type.value, permission.permission_type.value,
                    json.dumps(permission.conditions), permission.active,
                    permission.created_at.isoformat(), permission.updated_at.isoformat()
                ))
            
            # Invalider le cache
            self._invalidate_cache('permissions')
            
            logger.info(f"Permission créée: {permission.name}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur création permission: {e}")
            return False
    
    def create_role(self, role: Role) -> bool:
        """Crée un nouveau rôle"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO roles 
                    (id, name, description, permissions, parent_roles, 
                     conditions, priority, active, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    role.id, role.name, role.description,
                    json.dumps(role.permissions), json.dumps(role.parent_roles),
                    json.dumps(role.conditions), role.priority, role.active,
                    role.created_at.isoformat(), role.updated_at.isoformat()
                ))
            
            # Invalider le cache
            self._invalidate_cache('roles')
            
            logger.info(f"Rôle créé: {role.name}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur création rôle: {e}")
            return False
    
    def assign_role_to_user(self, user_id: str, role_id: str, granted_by: str,
                           expires_at: Optional[datetime] = None,
                           conditions: Dict[str, Any] = None) -> bool:
        """Assigne un rôle à un utilisateur"""
        try:
            assignment_id = f"ur_{int(time.time() * 1000000)}"
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO user_roles 
                    (id, user_id, role_id, granted_by, granted_at, expires_at, 
                     conditions, active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    assignment_id, user_id, role_id, granted_by,
                    datetime.now().isoformat(),
                    expires_at.isoformat() if expires_at else None,
                    json.dumps(conditions or {}), True
                ))
            
            # Invalider le cache utilisateur
            self._invalidate_user_cache(user_id)
            
            logger.info(f"Rôle {role_id} assigné à l'utilisateur {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur assignation rôle: {e}")
            return False
    
    def check_access(self, user_id: str, resource_type: ResourceType,
                    resource_id: str, permission_type: PermissionType,
                    context: Dict[str, Any] = None) -> Tuple[AccessResult, str]:
        """Vérifie l'accès d'un utilisateur à une ressource"""
        context = context or {}
        
        # Créer la demande d'accès
        request = AccessRequest(
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            permission_type=permission_type,
            context=context,
            timestamp=datetime.now()
        )
        
        # Vérifier les permissions
        result, reason = self._evaluate_access(request)
        
        # Enregistrer le log d'accès
        self._log_access(request, result, reason)
        
        # Mettre à jour les statistiques
        self.access_stats[f"{result.value}_{resource_type.value}_{permission_type.value}"] += 1
        
        return result, reason
    
    def _evaluate_access(self, request: AccessRequest) -> Tuple[AccessResult, str]:
        """Évalue une demande d'accès"""
        try:
            # Récupérer les rôles de l'utilisateur
            user_roles = self.get_user_roles(request.user_id)
            if not user_roles:
                return AccessResult.DENIED, "Aucun rôle assigné"
            
            # Vérifier les permissions temporaires
            temp_permissions = self._get_temporary_permissions(request.user_id)
            for temp_perm in temp_permissions:
                if (temp_perm['resource_type'] == request.resource_type.value and
                    temp_perm['permission_type'] == request.permission_type.value):
                    if datetime.now() < datetime.fromisoformat(temp_perm['expires_at']):
                        return AccessResult.GRANTED, "Permission temporaire"
                    else:
                        return AccessResult.EXPIRED, "Permission temporaire expirée"
            
            # Évaluer les permissions par rôle
            granted_permissions = set()
            denied_permissions = set()
            
            for role in user_roles:
                role_permissions = self._resolve_role_permissions(role['id'])
                
                for perm in role_permissions:
                    perm_key = f"{request.resource_type.value}:{request.permission_type.value}"
                    
                    # Vérifier si la permission correspond
                    if self._permission_matches(perm, perm_key, request):
                        # Vérifier les conditions
                        if self._check_conditions(perm.get('conditions', {}), request):
                            granted_permissions.add(perm_key)
                        else:
                            denied_permissions.add(perm_key)
            
            # Vérifier les politiques d'accès
            policies_result = self._evaluate_policies(request)
            if policies_result[0] == AccessResult.DENIED:
                return policies_result
            
            # Déterminer le résultat final
            perm_key = f"{request.resource_type.value}:{request.permission_type.value}"
            
            if perm_key in denied_permissions:
                return AccessResult.DENIED, "Permission explicitement refusée"
            
            if perm_key in granted_permissions:
                return AccessResult.GRANTED, "Permission accordée par rôle"
            
            # Vérifier les permissions génériques (*)
            if "*" in granted_permissions or f"{request.resource_type.value}:*" in granted_permissions:
                return AccessResult.GRANTED, "Permission générique accordée"
            
            return AccessResult.DENIED, "Aucune permission correspondante"
            
        except Exception as e:
            logger.error(f"Erreur évaluation accès: {e}")
            return AccessResult.DENIED, f"Erreur système: {str(e)}"
    
    def _resolve_role_permissions(self, role_id: str) -> List[Dict[str, Any]]:
        """Résout toutes les permissions d'un rôle (incluant l'héritage)"""
        permissions = []
        visited_roles = set()
        
        def resolve_recursive(current_role_id: str):
            if current_role_id in visited_roles:
                return
            
            visited_roles.add(current_role_id)
            role = self.get_role(current_role_id)
            
            if not role:
                return
            
            # Ajouter les permissions directes
            for perm_pattern in role.permissions:
                if perm_pattern == "*":
                    # Permission globale
                    permissions.append({
                        'pattern': '*',
                        'conditions': role.conditions
                    })
                else:
                    # Permission spécifique
                    permissions.append({
                        'pattern': perm_pattern,
                        'conditions': role.conditions
                    })
            
            # Résoudre les rôles parents
            for parent_role_id in role.parent_roles:
                resolve_recursive(parent_role_id)
        
        resolve_recursive(role_id)
        return permissions
    
    def _permission_matches(self, permission: Dict[str, Any], 
                          requested_perm: str, request: AccessRequest) -> bool:
        """Vérifie si une permission correspond à la demande"""
        pattern = permission['pattern']
        
        # Permission globale
        if pattern == "*":
            return True
        
        # Permission exacte
        if pattern == requested_perm:
            return True
        
        # Permission avec wildcard
        if pattern.endswith("*"):
            prefix = pattern[:-1]
            if requested_perm.startswith(prefix):
                return True
        
        # Permission par ressource
        resource_pattern = f"{request.resource_type.value}:*"
        if pattern == resource_pattern:
            return True
        
        return False
    
    def _check_conditions(self, conditions: Dict[str, Any], 
                         request: AccessRequest) -> bool:
        """Vérifie les conditions d'une permission"""
        if not conditions:
            return True
        
        context = request.context
        
        # Vérifier l'heure
        if 'time_range' in conditions:
            time_range = conditions['time_range']
            current_hour = datetime.now().hour
            
            if not (time_range['start'] <= current_hour <= time_range['end']):
                return False
        
        # Vérifier l'IP
        if 'allowed_ips' in conditions:
            user_ip = context.get('ip_address', '')
            if user_ip not in conditions['allowed_ips']:
                return False
        
        # Vérifier MFA
        if conditions.get('require_mfa', False):
            if not context.get('mfa_verified', False):
                return False
        
        # Vérifier les propriétés de la ressource
        if 'resource_conditions' in conditions:
            resource_conditions = conditions['resource_conditions']
            
            for key, expected_value in resource_conditions.items():
                actual_value = context.get(f'resource_{key}')
                if actual_value != expected_value:
                    return False
        
        return True
    
    def _evaluate_policies(self, request: AccessRequest) -> Tuple[AccessResult, str]:
        """Évalue les politiques d'accès"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM access_policies 
                WHERE active = TRUE 
                ORDER BY priority DESC
            """)
            
            policies = cursor.fetchall()
        
        for policy in policies:
            if self._policy_matches(policy, request):
                if policy['effect'] == 'deny':
                    return AccessResult.DENIED, f"Refusé par politique: {policy['name']}"
                elif policy['effect'] == 'allow':
                    return AccessResult.GRANTED, f"Accordé par politique: {policy['name']}"
        
        return AccessResult.CONDITIONAL, "Aucune politique applicable"
    
    def _policy_matches(self, policy: sqlite3.Row, request: AccessRequest) -> bool:
        """Vérifie si une politique correspond à la demande"""
        pattern = policy['resource_pattern']
        resource_path = f"{request.resource_type.value}/{request.resource_id}"
        
        # Pattern exact
        if pattern == resource_path:
            return True
        
        # Pattern avec wildcard
        if pattern.endswith("*"):
            prefix = pattern[:-1]
            if resource_path.startswith(prefix):
                return True
        
        # Vérifier les conditions de la politique
        conditions = json.loads(policy['conditions'])
        return self._check_conditions(conditions, request)
    
    def _get_temporary_permissions(self, user_id: str) -> List[Dict[str, Any]]:
        """Récupère les permissions temporaires d'un utilisateur"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT tp.*, p.resource_type, p.permission_type
                FROM temporary_permissions tp
                JOIN permissions p ON tp.permission_id = p.id
                WHERE tp.user_id = ? AND tp.active = TRUE
                AND tp.expires_at > datetime('now')
            """, (user_id,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def _log_access(self, request: AccessRequest, result: AccessResult, reason: str):
        """Enregistre un log d'accès"""
        log_id = f"log_{int(time.time() * 1000000)}"
        
        access_log = AccessLog(
            id=log_id,
            user_id=request.user_id,
            resource_type=request.resource_type,
            resource_id=request.resource_id,
            permission_type=request.permission_type,
            result=result,
            reason=reason,
            context=request.context,
            timestamp=request.timestamp
        )
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO access_logs 
                (id, user_id, resource_type, resource_id, permission_type,
                 result, reason, context, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                access_log.id, access_log.user_id, access_log.resource_type.value,
                access_log.resource_id, access_log.permission_type.value,
                access_log.result.value, access_log.reason,
                json.dumps(access_log.context), access_log.timestamp.isoformat()
            ))
    
    def get_permission(self, permission_id: str) -> Optional[Permission]:
        """Récupère une permission par ID"""
        # Vérifier le cache
        cache_key = f"permission_{permission_id}"
        if self._is_cache_valid(cache_key):
            return self.permission_cache.get(cache_key)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM permissions WHERE id = ?", (permission_id,))
            row = cursor.fetchone()
            
            if row:
                permission = Permission(
                    id=row['id'],
                    name=row['name'],
                    description=row['description'],
                    resource_type=ResourceType(row['resource_type']),
                    permission_type=PermissionType(row['permission_type']),
                    conditions=json.loads(row['conditions']),
                    active=bool(row['active']),
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at'])
                )
                
                # Mettre en cache
                self.permission_cache[cache_key] = permission
                self.cache_timestamps[cache_key] = time.time()
                
                return permission
        
        return None
    
    def get_role(self, role_id: str) -> Optional[Role]:
        """Récupère un rôle par ID"""
        # Vérifier le cache
        cache_key = f"role_{role_id}"
        if self._is_cache_valid(cache_key):
            return self.role_cache.get(cache_key)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM roles WHERE id = ?", (role_id,))
            row = cursor.fetchone()
            
            if row:
                role = Role(
                    id=row['id'],
                    name=row['name'],
                    description=row['description'],
                    permissions=json.loads(row['permissions']),
                    parent_roles=json.loads(row['parent_roles']),
                    conditions=json.loads(row['conditions']),
                    priority=row['priority'],
                    active=bool(row['active']),
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at'])
                )
                
                # Mettre en cache
                self.role_cache[cache_key] = role
                self.cache_timestamps[cache_key] = time.time()
                
                return role
        
        return None
    
    def get_user_roles(self, user_id: str) -> List[Dict[str, Any]]:
        """Récupère les rôles d'un utilisateur"""
        # Vérifier le cache
        cache_key = f"user_roles_{user_id}"
        if self._is_cache_valid(cache_key):
            return self.user_roles_cache.get(cache_key, [])
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT ur.*, r.name as role_name, r.priority
                FROM user_roles ur
                JOIN roles r ON ur.role_id = r.id
                WHERE ur.user_id = ? AND ur.active = TRUE
                AND (ur.expires_at IS NULL OR ur.expires_at > datetime('now'))
                ORDER BY r.priority DESC
            """, (user_id,))
            
            roles = [dict(row) for row in cursor.fetchall()]
            
            # Mettre en cache
            self.user_roles_cache[cache_key] = roles
            self.cache_timestamps[cache_key] = time.time()
            
            return roles
    
    def get_access_logs(self, user_id: Optional[str] = None,
                       resource_type: Optional[ResourceType] = None,
                       limit: int = 100) -> List[AccessLog]:
        """Récupère les logs d'accès"""
        query = "SELECT * FROM access_logs WHERE 1=1"
        params = []
        
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        
        if resource_type:
            query += " AND resource_type = ?"
            params.append(resource_type.value)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            
            logs = []
            for row in cursor.fetchall():
                log = AccessLog(
                    id=row['id'],
                    user_id=row['user_id'],
                    resource_type=ResourceType(row['resource_type']),
                    resource_id=row['resource_id'],
                    permission_type=PermissionType(row['permission_type']),
                    result=AccessResult(row['result']),
                    reason=row['reason'],
                    context=json.loads(row['context']),
                    timestamp=datetime.fromisoformat(row['timestamp'])
                )
                logs.append(log)
            
            return logs
    
    def get_rbac_dashboard(self) -> Dict[str, Any]:
        """Récupère le tableau de bord RBAC"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Statistiques générales
            cursor = conn.execute("SELECT COUNT(*) as count FROM permissions WHERE active = TRUE")
            active_permissions = cursor.fetchone()['count']
            
            cursor = conn.execute("SELECT COUNT(*) as count FROM roles WHERE active = TRUE")
            active_roles = cursor.fetchone()['count']
            
            cursor = conn.execute("SELECT COUNT(DISTINCT user_id) as count FROM user_roles WHERE active = TRUE")
            users_with_roles = cursor.fetchone()['count']
            
            # Statistiques d'accès des dernières 24h
            cursor = conn.execute("""
                SELECT result, COUNT(*) as count
                FROM access_logs 
                WHERE timestamp >= datetime('now', '-24 hours')
                GROUP BY result
            """)
            
            access_stats = {row['result']: row['count'] for row in cursor.fetchall()}
            
            # Top ressources accédées
            cursor = conn.execute("""
                SELECT resource_type, COUNT(*) as count
                FROM access_logs 
                WHERE timestamp >= datetime('now', '-24 hours')
                GROUP BY resource_type
                ORDER BY count DESC
                LIMIT 10
            """)
            
            top_resources = [dict(row) for row in cursor.fetchall()]
            
            # Rôles les plus utilisés
            cursor = conn.execute("""
                SELECT r.name, COUNT(ur.user_id) as user_count
                FROM roles r
                LEFT JOIN user_roles ur ON r.id = ur.role_id AND ur.active = TRUE
                WHERE r.active = TRUE
                GROUP BY r.id, r.name
                ORDER BY user_count DESC
                LIMIT 10
            """)
            
            top_roles = [dict(row) for row in cursor.fetchall()]
        
        return {
            'active_permissions': active_permissions,
            'active_roles': active_roles,
            'users_with_roles': users_with_roles,
            'access_stats_24h': access_stats,
            'top_resources': top_resources,
            'top_roles': top_roles,
            'cache_stats': {
                'permission_cache_size': len(self.permission_cache),
                'role_cache_size': len(self.role_cache),
                'user_roles_cache_size': len(self.user_roles_cache)
            },
            'generated_at': datetime.now().isoformat()
        }
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Vérifie si une entrée de cache est valide"""
        if cache_key not in self.cache_timestamps:
            return False
        
        return (time.time() - self.cache_timestamps[cache_key]) < self.cache_ttl
    
    def _invalidate_cache(self, cache_type: str):
        """Invalide un type de cache"""
        if cache_type == 'permissions':
            keys_to_remove = [k for k in self.permission_cache.keys() if k.startswith('permission_')]
            for key in keys_to_remove:
                self.permission_cache.pop(key, None)
                self.cache_timestamps.pop(key, None)
        
        elif cache_type == 'roles':
            keys_to_remove = [k for k in self.role_cache.keys() if k.startswith('role_')]
            for key in keys_to_remove:
                self.role_cache.pop(key, None)
                self.cache_timestamps.pop(key, None)
    
    def _invalidate_user_cache(self, user_id: str):
        """Invalide le cache d'un utilisateur"""
        cache_key = f"user_roles_{user_id}"
        self.user_roles_cache.pop(cache_key, None)
        self.cache_timestamps.pop(cache_key, None)
    
    def _start_cache_cleanup(self):
        """Démarre le nettoyage automatique du cache"""
        def cleanup_loop():
            while True:
                try:
                    current_time = time.time()
                    expired_keys = [
                        key for key, timestamp in self.cache_timestamps.items()
                        if (current_time - timestamp) > self.cache_ttl
                    ]
                    
                    for key in expired_keys:
                        self.permission_cache.pop(key, None)
                        self.role_cache.pop(key, None)
                        self.user_roles_cache.pop(key, None)
                        self.cache_timestamps.pop(key, None)
                    
                    # Nettoyer les permissions temporaires expirées
                    with sqlite3.connect(self.db_path) as conn:
                        conn.execute("""
                            UPDATE temporary_permissions 
                            SET active = FALSE 
                            WHERE expires_at < datetime('now')
                        """)
                    
                    time.sleep(300)  # 5 minutes
                    
                except Exception as e:
                    logger.error(f"Erreur nettoyage cache RBAC: {e}")
                    time.sleep(60)
        
        cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        cleanup_thread.start()
        logger.info("Nettoyage automatique du cache RBAC démarré")

# Exemple d'utilisation
if __name__ == "__main__":
    # Créer le système RBAC
    rbac = RBACSystem()
    
    # Assigner le rôle admin à l'utilisateur admin
    rbac.assign_role_to_user("admin_001", "admin", "system")
    
    # Tester l'accès
    result, reason = rbac.check_access(
        user_id="admin_001",
        resource_type=ResourceType.SYSTEM,
        resource_id="config",
        permission_type=PermissionType.ADMIN,
        context={'ip_address': '127.0.0.1', 'mfa_verified': True}
    )
    
    print(f"Résultat accès: {result.value} - {reason}")
    
    # Afficher le tableau de bord
    dashboard = rbac.get_rbac_dashboard()
    print(f"\nTableau de bord RBAC:")
    print(f"- Permissions actives: {dashboard['active_permissions']}")
    print(f"- Rôles actifs: {dashboard['active_roles']}")
    print(f"- Utilisateurs avec rôles: {dashboard['users_with_roles']}")
    print(f"- Statistiques d'accès 24h: {dashboard['access_stats_24h']}")

