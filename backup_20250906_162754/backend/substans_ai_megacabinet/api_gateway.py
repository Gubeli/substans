#!/usr/bin/env python3
"""
API Gateway System - Substans.AI Enterprise
Passerelle API unifiée avec authentification, rate limiting, monitoring et documentation automatique
"""

from flask import Flask, request, jsonify, g
from flask_cors import CORS
import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from functools import wraps
import time
import hashlib
import jwt
import threading
from pathlib import Path
import requests
from collections import defaultdict, deque

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class APIEndpoint:
    """Point de terminaison API"""
    path: str
    method: str
    handler: str
    description: str
    parameters: Dict[str, Any]
    response_schema: Dict[str, Any]
    auth_required: bool
    rate_limit: int  # requêtes par minute
    version: str
    tags: List[str]
    deprecated: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class APIKey:
    """Clé API"""
    key: str
    name: str
    user_id: str
    permissions: List[str]
    rate_limit: int
    created_at: datetime
    expires_at: Optional[datetime]
    last_used: Optional[datetime]
    usage_count: int
    status: str  # 'active', 'suspended', 'expired'
    
    def is_valid(self) -> bool:
        """Vérifie si la clé est valide"""
        if self.status != 'active':
            return False
        if self.expires_at and datetime.now() > self.expires_at:
            return False
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['expires_at'] = self.expires_at.isoformat() if self.expires_at else None
        data['last_used'] = self.last_used.isoformat() if self.last_used else None
        return data

@dataclass
class APIRequest:
    """Requête API"""
    id: str
    endpoint: str
    method: str
    user_id: Optional[str]
    api_key: Optional[str]
    ip_address: str
    user_agent: str
    parameters: Dict[str, Any]
    response_code: int
    response_time: float
    timestamp: datetime
    error_message: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

class RateLimiter:
    """Limiteur de débit avec fenêtre glissante"""
    
    def __init__(self):
        self.requests = defaultdict(deque)
        self.lock = threading.Lock()
    
    def is_allowed(self, key: str, limit: int, window_seconds: int = 60) -> bool:
        """Vérifie si la requête est autorisée"""
        now = time.time()
        
        with self.lock:
            # Nettoyer les anciennes requêtes
            while self.requests[key] and self.requests[key][0] < now - window_seconds:
                self.requests[key].popleft()
            
            # Vérifier la limite
            if len(self.requests[key]) >= limit:
                return False
            
            # Ajouter la requête actuelle
            self.requests[key].append(now)
            return True
    
    def get_remaining(self, key: str, limit: int, window_seconds: int = 60) -> int:
        """Retourne le nombre de requêtes restantes"""
        now = time.time()
        
        with self.lock:
            # Nettoyer les anciennes requêtes
            while self.requests[key] and self.requests[key][0] < now - window_seconds:
                self.requests[key].popleft()
            
            return max(0, limit - len(self.requests[key]))

class APIGateway:
    """Passerelle API enterprise avec fonctionnalités avancées"""
    
    def __init__(self, db_path: str = "api_gateway.db", secret_key: str = None):
        self.db_path = db_path
        self.secret_key = secret_key or "substans_ai_secret_key_2024"
        self.app = Flask(__name__)
        self.app.secret_key = self.secret_key
        
        # Configuration CORS
        CORS(self.app, origins=["*"], methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
        
        # Composants
        self.rate_limiter = RateLimiter()
        self.endpoints = {}
        self.middleware_stack = []
        
        # Configuration par défaut
        self.default_rate_limit = 1000  # requêtes par minute
        self.default_auth_required = True
        
        # Statistiques en temps réel
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'avg_response_time': 0.0,
            'active_connections': 0
        }
        
        self._init_database()
        self._register_core_endpoints()
        self._setup_middleware()
        
        logger.info("API Gateway initialisé")
    
    def _init_database(self):
        """Initialise la base de données"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS api_keys (
                    key TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    permissions TEXT NOT NULL,
                    rate_limit INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT,
                    last_used TEXT,
                    usage_count INTEGER DEFAULT 0,
                    status TEXT NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS api_requests (
                    id TEXT PRIMARY KEY,
                    endpoint TEXT NOT NULL,
                    method TEXT NOT NULL,
                    user_id TEXT,
                    api_key TEXT,
                    ip_address TEXT NOT NULL,
                    user_agent TEXT NOT NULL,
                    parameters TEXT NOT NULL,
                    response_code INTEGER NOT NULL,
                    response_time REAL NOT NULL,
                    timestamp TEXT NOT NULL,
                    error_message TEXT
                );
                
                CREATE TABLE IF NOT EXISTS endpoints (
                    path TEXT NOT NULL,
                    method TEXT NOT NULL,
                    handler TEXT NOT NULL,
                    description TEXT NOT NULL,
                    parameters TEXT NOT NULL,
                    response_schema TEXT NOT NULL,
                    auth_required BOOLEAN NOT NULL,
                    rate_limit INTEGER NOT NULL,
                    version TEXT NOT NULL,
                    tags TEXT NOT NULL,
                    deprecated BOOLEAN DEFAULT FALSE,
                    PRIMARY KEY (path, method)
                );
                
                CREATE TABLE IF NOT EXISTS api_analytics (
                    id TEXT PRIMARY KEY,
                    endpoint TEXT NOT NULL,
                    method TEXT NOT NULL,
                    date TEXT NOT NULL,
                    hour INTEGER NOT NULL,
                    request_count INTEGER NOT NULL,
                    avg_response_time REAL NOT NULL,
                    error_count INTEGER NOT NULL,
                    unique_users INTEGER NOT NULL
                );
                
                CREATE INDEX IF NOT EXISTS idx_requests_timestamp ON api_requests(timestamp);
                CREATE INDEX IF NOT EXISTS idx_requests_endpoint ON api_requests(endpoint);
                CREATE INDEX IF NOT EXISTS idx_analytics_date ON api_analytics(date, hour);
            """)
        
        # Créer une clé API par défaut
        self._create_default_api_key()
    
    def _create_default_api_key(self):
        """Crée une clé API par défaut"""
        default_key = "substans_ai_master_key_2024"
        
        api_key = APIKey(
            key=default_key,
            name="Master Key",
            user_id="admin",
            permissions=["*"],
            rate_limit=10000,
            created_at=datetime.now(),
            expires_at=None,
            last_used=None,
            usage_count=0,
            status="active"
        )
        
        self.create_api_key(api_key)
    
    def create_api_key(self, api_key: APIKey):
        """Crée une clé API"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO api_keys 
                (key, name, user_id, permissions, rate_limit, created_at, 
                 expires_at, last_used, usage_count, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                api_key.key, api_key.name, api_key.user_id,
                json.dumps(api_key.permissions), api_key.rate_limit,
                api_key.created_at.isoformat(),
                api_key.expires_at.isoformat() if api_key.expires_at else None,
                api_key.last_used.isoformat() if api_key.last_used else None,
                api_key.usage_count, api_key.status
            ))
        
        logger.info(f"Clé API créée: {api_key.name}")
    
    def get_api_key(self, key: str) -> Optional[APIKey]:
        """Récupère une clé API"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM api_keys WHERE key = ?", (key,))
            row = cursor.fetchone()
            
            if row:
                return APIKey(
                    key=row['key'],
                    name=row['name'],
                    user_id=row['user_id'],
                    permissions=json.loads(row['permissions']),
                    rate_limit=row['rate_limit'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    expires_at=datetime.fromisoformat(row['expires_at']) if row['expires_at'] else None,
                    last_used=datetime.fromisoformat(row['last_used']) if row['last_used'] else None,
                    usage_count=row['usage_count'],
                    status=row['status']
                )
            return None
    
    def register_endpoint(self, endpoint: APIEndpoint, handler: Callable):
        """Enregistre un endpoint API"""
        # Sauvegarder en base
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO endpoints 
                (path, method, handler, description, parameters, response_schema,
                 auth_required, rate_limit, version, tags, deprecated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                endpoint.path, endpoint.method, endpoint.handler,
                endpoint.description, json.dumps(endpoint.parameters),
                json.dumps(endpoint.response_schema), endpoint.auth_required,
                endpoint.rate_limit, endpoint.version, json.dumps(endpoint.tags),
                endpoint.deprecated
            ))
        
        # Enregistrer dans Flask
        route_key = f"{endpoint.method}:{endpoint.path}"
        self.endpoints[route_key] = endpoint
        
        # Créer la route Flask avec middleware
        flask_handler = self._wrap_handler(handler, endpoint)
        self.app.add_url_rule(
            endpoint.path, 
            endpoint=f"{endpoint.method}_{endpoint.path.replace('/', '_')}",
            view_func=flask_handler,
            methods=[endpoint.method]
        )
        
        logger.info(f"Endpoint enregistré: {endpoint.method} {endpoint.path}")
    
    def _wrap_handler(self, handler: Callable, endpoint: APIEndpoint) -> Callable:
        """Enrobe un handler avec le middleware"""
        @wraps(handler)
        def wrapped_handler(*args, **kwargs):
            start_time = time.time()
            request_id = f"req_{int(start_time * 1000000)}"
            
            try:
                # Middleware d'authentification
                if endpoint.auth_required:
                    auth_result = self._authenticate_request()
                    if not auth_result['success']:
                        return jsonify({'error': auth_result['error']}), 401
                    g.user_id = auth_result['user_id']
                    g.api_key = auth_result['api_key']
                
                # Middleware de rate limiting
                rate_limit_key = g.get('api_key', request.remote_addr)
                if not self.rate_limiter.is_allowed(rate_limit_key, endpoint.rate_limit):
                    return jsonify({'error': 'Rate limit exceeded'}), 429
                
                # Exécuter le handler
                response = handler(*args, **kwargs)
                
                # Enregistrer la requête
                response_time = time.time() - start_time
                self._log_request(request_id, endpoint, 200, response_time)
                
                # Mettre à jour les statistiques
                self._update_stats(True, response_time)
                
                return response
                
            except Exception as e:
                response_time = time.time() - start_time
                self._log_request(request_id, endpoint, 500, response_time, str(e))
                self._update_stats(False, response_time)
                
                logger.error(f"Erreur dans {endpoint.path}: {e}")
                return jsonify({'error': 'Internal server error'}), 500
        
        return wrapped_handler
    
    def _authenticate_request(self) -> Dict[str, Any]:
        """Authentifie une requête"""
        # Vérifier l'en-tête Authorization
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return {'success': False, 'error': 'Missing Authorization header'}
        
        # Extraire la clé API
        if not auth_header.startswith('Bearer '):
            return {'success': False, 'error': 'Invalid Authorization format'}
        
        api_key_value = auth_header[7:]  # Enlever "Bearer "
        
        # Vérifier la clé API
        api_key = self.get_api_key(api_key_value)
        if not api_key or not api_key.is_valid():
            return {'success': False, 'error': 'Invalid or expired API key'}
        
        # Mettre à jour l'utilisation
        self._update_api_key_usage(api_key_value)
        
        return {
            'success': True,
            'user_id': api_key.user_id,
            'api_key': api_key_value
        }
    
    def _update_api_key_usage(self, key: str):
        """Met à jour l'utilisation d'une clé API"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE api_keys 
                SET last_used = ?, usage_count = usage_count + 1
                WHERE key = ?
            """, (datetime.now().isoformat(), key))
    
    def _log_request(self, request_id: str, endpoint: APIEndpoint, 
                    response_code: int, response_time: float, 
                    error_message: Optional[str] = None):
        """Enregistre une requête"""
        api_request = APIRequest(
            id=request_id,
            endpoint=endpoint.path,
            method=endpoint.method,
            user_id=g.get('user_id'),
            api_key=g.get('api_key'),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', ''),
            parameters=dict(request.args),
            response_code=response_code,
            response_time=response_time,
            timestamp=datetime.now(),
            error_message=error_message
        )
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO api_requests 
                (id, endpoint, method, user_id, api_key, ip_address, user_agent,
                 parameters, response_code, response_time, timestamp, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                api_request.id, api_request.endpoint, api_request.method,
                api_request.user_id, api_request.api_key, api_request.ip_address,
                api_request.user_agent, json.dumps(api_request.parameters),
                api_request.response_code, api_request.response_time,
                api_request.timestamp.isoformat(), api_request.error_message
            ))
    
    def _update_stats(self, success: bool, response_time: float):
        """Met à jour les statistiques"""
        self.stats['total_requests'] += 1
        
        if success:
            self.stats['successful_requests'] += 1
        else:
            self.stats['failed_requests'] += 1
        
        # Calcul de la moyenne mobile du temps de réponse
        current_avg = self.stats['avg_response_time']
        total_requests = self.stats['total_requests']
        self.stats['avg_response_time'] = (current_avg * (total_requests - 1) + response_time) / total_requests
    
    def _register_core_endpoints(self):
        """Enregistre les endpoints core de l'API"""
        
        # Endpoint de santé
        health_endpoint = APIEndpoint(
            path="/health",
            method="GET",
            handler="health_check",
            description="Vérifie l'état de santé de l'API",
            parameters={},
            response_schema={"status": "string", "timestamp": "string"},
            auth_required=False,
            rate_limit=100,
            version="v1",
            tags=["system"]
        )
        
        def health_check():
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0'
            })
        
        self.register_endpoint(health_endpoint, health_check)
        
        # Endpoint de statistiques
        stats_endpoint = APIEndpoint(
            path="/stats",
            method="GET",
            handler="get_stats",
            description="Récupère les statistiques de l'API",
            parameters={},
            response_schema={"stats": "object"},
            auth_required=True,
            rate_limit=60,
            version="v1",
            tags=["analytics"]
        )
        
        def get_stats():
            return jsonify({
                'stats': self.stats,
                'timestamp': datetime.now().isoformat()
            })
        
        self.register_endpoint(stats_endpoint, get_stats)
        
        # Endpoint de documentation
        docs_endpoint = APIEndpoint(
            path="/docs",
            method="GET",
            handler="get_documentation",
            description="Récupère la documentation de l'API",
            parameters={},
            response_schema={"endpoints": "array"},
            auth_required=False,
            rate_limit=30,
            version="v1",
            tags=["documentation"]
        )
        
        def get_documentation():
            endpoints_data = []
            
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("SELECT * FROM endpoints ORDER BY path, method")
                
                for row in cursor.fetchall():
                    endpoint_data = {
                        'path': row['path'],
                        'method': row['method'],
                        'description': row['description'],
                        'parameters': json.loads(row['parameters']),
                        'response_schema': json.loads(row['response_schema']),
                        'auth_required': bool(row['auth_required']),
                        'rate_limit': row['rate_limit'],
                        'version': row['version'],
                        'tags': json.loads(row['tags']),
                        'deprecated': bool(row['deprecated'])
                    }
                    endpoints_data.append(endpoint_data)
            
            return jsonify({
                'api_name': 'Substans.AI API',
                'version': '1.0.0',
                'description': 'API Gateway pour la plateforme Substans.AI',
                'endpoints': endpoints_data,
                'generated_at': datetime.now().isoformat()
            })
        
        self.register_endpoint(docs_endpoint, get_documentation)
    
    def _setup_middleware(self):
        """Configure le middleware global"""
        
        @self.app.before_request
        def before_request():
            """Middleware exécuté avant chaque requête"""
            g.start_time = time.time()
            self.stats['active_connections'] += 1
        
        @self.app.after_request
        def after_request(response):
            """Middleware exécuté après chaque requête"""
            self.stats['active_connections'] = max(0, self.stats['active_connections'] - 1)
            
            # Ajouter des en-têtes de sécurité
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            
            # Ajouter des informations de rate limiting
            if hasattr(g, 'api_key'):
                remaining = self.rate_limiter.get_remaining(g.api_key, self.default_rate_limit)
                response.headers['X-RateLimit-Remaining'] = str(remaining)
                response.headers['X-RateLimit-Limit'] = str(self.default_rate_limit)
            
            return response
        
        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({'error': 'Endpoint not found'}), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
            return jsonify({'error': 'Internal server error'}), 500
    
    def get_analytics(self, days: int = 7) -> Dict[str, Any]:
        """Récupère les analytics de l'API"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Requêtes par jour
            cursor = conn.execute("""
                SELECT DATE(timestamp) as date, COUNT(*) as count,
                       AVG(response_time) as avg_response_time,
                       SUM(CASE WHEN response_code >= 400 THEN 1 ELSE 0 END) as error_count
                FROM api_requests 
                WHERE timestamp >= ? AND timestamp <= ?
                GROUP BY DATE(timestamp)
                ORDER BY date
            """, (start_date.isoformat(), end_date.isoformat()))
            
            daily_stats = [dict(row) for row in cursor.fetchall()]
            
            # Endpoints les plus utilisés
            cursor = conn.execute("""
                SELECT endpoint, method, COUNT(*) as count,
                       AVG(response_time) as avg_response_time
                FROM api_requests 
                WHERE timestamp >= ? AND timestamp <= ?
                GROUP BY endpoint, method
                ORDER BY count DESC
                LIMIT 10
            """, (start_date.isoformat(), end_date.isoformat()))
            
            top_endpoints = [dict(row) for row in cursor.fetchall()]
            
            # Utilisateurs les plus actifs
            cursor = conn.execute("""
                SELECT user_id, COUNT(*) as count
                FROM api_requests 
                WHERE timestamp >= ? AND timestamp <= ? AND user_id IS NOT NULL
                GROUP BY user_id
                ORDER BY count DESC
                LIMIT 10
            """, (start_date.isoformat(), end_date.isoformat()))
            
            top_users = [dict(row) for row in cursor.fetchall()]
        
        return {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'days': days
            },
            'daily_stats': daily_stats,
            'top_endpoints': top_endpoints,
            'top_users': top_users,
            'current_stats': self.stats,
            'generated_at': datetime.now().isoformat()
        }
    
    def run(self, host: str = "0.0.0.0", port: int = 8000, debug: bool = False):
        """Lance le serveur API Gateway"""
        logger.info(f"Démarrage API Gateway sur {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)

# Exemple d'utilisation
if __name__ == "__main__":
    # Créer l'API Gateway
    gateway = APIGateway()
    
    # Enregistrer un endpoint d'exemple
    example_endpoint = APIEndpoint(
        path="/api/v1/missions",
        method="GET",
        handler="get_missions",
        description="Récupère la liste des missions",
        parameters={
            "status": {"type": "string", "description": "Filtre par statut"},
            "limit": {"type": "integer", "description": "Nombre maximum de résultats"}
        },
        response_schema={
            "missions": {"type": "array", "description": "Liste des missions"},
            "total": {"type": "integer", "description": "Nombre total de missions"}
        },
        auth_required=True,
        rate_limit=100,
        version="v1",
        tags=["missions"]
    )
    
    def get_missions():
        # Exemple de handler
        return jsonify({
            'missions': [
                {'id': 'mission_001', 'title': 'Analyse Bull', 'status': 'completed'},
                {'id': 'mission_002', 'title': 'Étude Marché', 'status': 'in_progress'}
            ],
            'total': 2
        })
    
    gateway.register_endpoint(example_endpoint, get_missions)
    
    # Lancer le serveur
    print("API Gateway démarré sur http://localhost:8000")
    print("Documentation: http://localhost:8000/docs")
    print("Santé: http://localhost:8000/health")
    print("Statistiques: http://localhost:8000/stats")
    
    gateway.run(port=8000, debug=True)

