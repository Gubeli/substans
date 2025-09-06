#!/usr/bin/env python3
"""
Security Manager - Substans.AI Enterprise
Système de sécurité complet avec authentification, autorisation et audit
"""

import hashlib
import secrets
import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import jwt
import bcrypt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import re
import threading
import time
from collections import defaultdict, deque
import ipaddress

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """Niveaux de sécurité"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ThreatLevel(Enum):
    """Niveaux de menace"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AuthenticationMethod(Enum):
    """Méthodes d'authentification"""
    PASSWORD = "password"
    API_KEY = "api_key"
    JWT_TOKEN = "jwt_token"
    OAUTH = "oauth"
    MFA = "mfa"

@dataclass
class User:
    """Utilisateur du système"""
    id: str
    username: str
    email: str
    password_hash: str
    salt: str
    roles: List[str]
    permissions: List[str]
    security_level: SecurityLevel
    mfa_enabled: bool
    mfa_secret: Optional[str]
    last_login: Optional[datetime]
    failed_login_attempts: int
    account_locked: bool
    locked_until: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    active: bool
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['security_level'] = self.security_level.value
        data['last_login'] = self.last_login.isoformat() if self.last_login else None
        data['locked_until'] = self.locked_until.isoformat() if self.locked_until else None
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data

@dataclass
class SecurityEvent:
    """Événement de sécurité"""
    id: str
    event_type: str
    threat_level: ThreatLevel
    user_id: Optional[str]
    ip_address: str
    user_agent: str
    description: str
    details: Dict[str, Any]
    timestamp: datetime
    resolved: bool
    resolution_notes: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['threat_level'] = self.threat_level.value
        data['timestamp'] = self.timestamp.isoformat()
        return data

@dataclass
class SecurityPolicy:
    """Politique de sécurité"""
    id: str
    name: str
    description: str
    rules: Dict[str, Any]
    security_level: SecurityLevel
    active: bool
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['security_level'] = self.security_level.value
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data

class SecurityManager:
    """Gestionnaire de sécurité enterprise"""
    
    def __init__(self, db_path: str = "security.db", secret_key: str = None):
        self.db_path = db_path
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        
        # Configuration de sécurité
        self.config = {
            'password_policy': {
                'min_length': 12,
                'require_uppercase': True,
                'require_lowercase': True,
                'require_digits': True,
                'require_special': True,
                'max_age_days': 90,
                'history_count': 5
            },
            'session_policy': {
                'timeout_minutes': 60,
                'max_concurrent_sessions': 3,
                'require_https': True
            },
            'lockout_policy': {
                'max_failed_attempts': 5,
                'lockout_duration_minutes': 30,
                'progressive_delay': True
            },
            'audit_policy': {
                'log_all_access': True,
                'log_failed_attempts': True,
                'retention_days': 365
            }
        }
        
        # Système de détection d'intrusion
        self.intrusion_detection = {
            'failed_logins': defaultdict(deque),
            'suspicious_ips': set(),
            'rate_limits': defaultdict(deque),
            'blocked_ips': defaultdict(datetime)
        }
        
        # Chiffrement
        self.encryption_key = self._derive_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Politiques de sécurité par défaut
        self.default_policies = {
            'admin_policy': {
                'name': 'Politique Administrateur',
                'description': 'Politique de sécurité pour les administrateurs',
                'rules': {
                    'mfa_required': True,
                    'session_timeout': 30,
                    'ip_whitelist_required': True,
                    'audit_all_actions': True,
                    'password_complexity': 'high'
                },
                'security_level': SecurityLevel.CRITICAL
            },
            'user_policy': {
                'name': 'Politique Utilisateur',
                'description': 'Politique de sécurité pour les utilisateurs standard',
                'rules': {
                    'mfa_required': False,
                    'session_timeout': 60,
                    'ip_whitelist_required': False,
                    'audit_all_actions': False,
                    'password_complexity': 'medium'
                },
                'security_level': SecurityLevel.MEDIUM
            }
        }
        
        self._init_database()
        self._init_default_policies()
        self._start_security_monitor()
        
        logger.info("Security Manager initialisé")
    
    def _init_database(self):
        """Initialise la base de données de sécurité"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    roles TEXT NOT NULL,
                    permissions TEXT NOT NULL,
                    security_level TEXT NOT NULL,
                    mfa_enabled BOOLEAN NOT NULL,
                    mfa_secret TEXT,
                    last_login TEXT,
                    failed_login_attempts INTEGER DEFAULT 0,
                    account_locked BOOLEAN DEFAULT FALSE,
                    locked_until TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    active BOOLEAN DEFAULT TRUE
                );
                
                CREATE TABLE IF NOT EXISTS security_events (
                    id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    threat_level TEXT NOT NULL,
                    user_id TEXT,
                    ip_address TEXT NOT NULL,
                    user_agent TEXT NOT NULL,
                    description TEXT NOT NULL,
                    details TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    resolved BOOLEAN DEFAULT FALSE,
                    resolution_notes TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                );
                
                CREATE TABLE IF NOT EXISTS security_policies (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    rules TEXT NOT NULL,
                    security_level TEXT NOT NULL,
                    active BOOLEAN DEFAULT TRUE,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    token TEXT NOT NULL,
                    ip_address TEXT NOT NULL,
                    user_agent TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    last_activity TEXT NOT NULL,
                    active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                );
                
                CREATE TABLE IF NOT EXISTS password_history (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                );
                
                CREATE TABLE IF NOT EXISTS ip_whitelist (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    ip_address TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                );
                
                CREATE INDEX IF NOT EXISTS idx_security_events_timestamp ON security_events(timestamp);
                CREATE INDEX IF NOT EXISTS idx_security_events_threat_level ON security_events(threat_level);
                CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
                CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at);
            """)
        
        # Créer un utilisateur admin par défaut
        self._create_default_admin()
    
    def _create_default_admin(self):
        """Crée un utilisateur administrateur par défaut"""
        admin_id = "admin_001"
        
        # Vérifier si l'admin existe déjà
        if self.get_user(admin_id):
            return
        
        # Créer l'admin
        admin_user = User(
            id=admin_id,
            username="admin",
            email="admin@substans.ai",
            password_hash="",  # Sera défini par create_user
            salt="",
            roles=["admin", "user"],
            permissions=["*"],
            security_level=SecurityLevel.CRITICAL,
            mfa_enabled=True,
            mfa_secret=secrets.token_urlsafe(32),
            last_login=None,
            failed_login_attempts=0,
            account_locked=False,
            locked_until=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            active=True
        )
        
        self.create_user(admin_user, "SubstansAI@2024!")
        logger.info("Utilisateur admin par défaut créé")
    
    def _derive_encryption_key(self) -> bytes:
        """Dérive une clé de chiffrement"""
        password = self.secret_key.encode()
        salt = b'substans_ai_salt_2024'  # En production, utiliser un salt aléatoire
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def _init_default_policies(self):
        """Initialise les politiques de sécurité par défaut"""
        for policy_id, config in self.default_policies.items():
            policy = SecurityPolicy(
                id=policy_id,
                name=config['name'],
                description=config['description'],
                rules=config['rules'],
                security_level=config['security_level'],
                active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            self.create_security_policy(policy)
    
    def create_user(self, user: User, password: str) -> bool:
        """Crée un nouvel utilisateur"""
        try:
            # Valider le mot de passe
            if not self._validate_password(password):
                raise ValueError("Le mot de passe ne respecte pas la politique de sécurité")
            
            # Générer le salt et hasher le mot de passe
            salt = secrets.token_hex(32)
            password_hash = self._hash_password(password, salt)
            
            user.salt = salt
            user.password_hash = password_hash
            
            # Sauvegarder en base
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO users 
                    (id, username, email, password_hash, salt, roles, permissions,
                     security_level, mfa_enabled, mfa_secret, last_login,
                     failed_login_attempts, account_locked, locked_until,
                     created_at, updated_at, active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user.id, user.username, user.email, user.password_hash,
                    user.salt, json.dumps(user.roles), json.dumps(user.permissions),
                    user.security_level.value, user.mfa_enabled, user.mfa_secret,
                    user.last_login.isoformat() if user.last_login else None,
                    user.failed_login_attempts, user.account_locked,
                    user.locked_until.isoformat() if user.locked_until else None,
                    user.created_at.isoformat(), user.updated_at.isoformat(),
                    user.active
                ))
            
            # Ajouter à l'historique des mots de passe
            self._add_password_to_history(user.id, password_hash)
            
            # Enregistrer l'événement de sécurité
            self._log_security_event(
                event_type="user_created",
                threat_level=ThreatLevel.INFO,
                user_id=user.id,
                description=f"Utilisateur créé: {user.username}",
                details={'username': user.username, 'email': user.email}
            )
            
            logger.info(f"Utilisateur créé: {user.username}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur création utilisateur: {e}")
            return False
    
    def authenticate_user(self, username: str, password: str, 
                         ip_address: str = "", user_agent: str = "") -> Optional[Dict[str, Any]]:
        """Authentifie un utilisateur"""
        try:
            # Vérifier les tentatives de connexion suspectes
            if self._is_ip_blocked(ip_address):
                self._log_security_event(
                    event_type="blocked_ip_attempt",
                    threat_level=ThreatLevel.HIGH,
                    description=f"Tentative de connexion depuis IP bloquée: {ip_address}",
                    details={'ip_address': ip_address, 'username': username},
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                return None
            
            # Récupérer l'utilisateur
            user = self.get_user_by_username(username)
            if not user:
                self._handle_failed_login(None, ip_address, user_agent, "Utilisateur inexistant")
                return None
            
            # Vérifier si le compte est verrouillé
            if user.account_locked:
                if user.locked_until and datetime.now() < user.locked_until:
                    self._log_security_event(
                        event_type="locked_account_attempt",
                        threat_level=ThreatLevel.MEDIUM,
                        user_id=user.id,
                        description=f"Tentative de connexion sur compte verrouillé: {username}",
                        details={'username': username, 'locked_until': user.locked_until.isoformat()},
                        ip_address=ip_address,
                        user_agent=user_agent
                    )
                    return None
                else:
                    # Déverrouiller le compte si la période est expirée
                    self._unlock_user_account(user.id)
                    user.account_locked = False
            
            # Vérifier le mot de passe
            if not self._verify_password(password, user.password_hash, user.salt):
                self._handle_failed_login(user.id, ip_address, user_agent, "Mot de passe incorrect")
                return None
            
            # Vérifier la whitelist IP si requise
            if self._requires_ip_whitelist(user):
                if not self._is_ip_whitelisted(user.id, ip_address):
                    self._log_security_event(
                        event_type="ip_not_whitelisted",
                        threat_level=ThreatLevel.HIGH,
                        user_id=user.id,
                        description=f"Connexion depuis IP non autorisée: {ip_address}",
                        details={'ip_address': ip_address, 'username': username},
                        ip_address=ip_address,
                        user_agent=user_agent
                    )
                    return None
            
            # Authentification réussie
            self._handle_successful_login(user.id, ip_address, user_agent)
            
            # Créer une session
            session_token = self._create_session(user.id, ip_address, user_agent)
            
            # Générer un JWT token
            jwt_token = self._generate_jwt_token(user)
            
            return {
                'user_id': user.id,
                'username': user.username,
                'roles': user.roles,
                'permissions': user.permissions,
                'session_token': session_token,
                'jwt_token': jwt_token,
                'mfa_required': user.mfa_enabled,
                'security_level': user.security_level.value
            }
            
        except Exception as e:
            logger.error(f"Erreur authentification: {e}")
            return None
    
    def _validate_password(self, password: str) -> bool:
        """Valide un mot de passe selon la politique"""
        policy = self.config['password_policy']
        
        if len(password) < policy['min_length']:
            return False
        
        if policy['require_uppercase'] and not re.search(r'[A-Z]', password):
            return False
        
        if policy['require_lowercase'] and not re.search(r'[a-z]', password):
            return False
        
        if policy['require_digits'] and not re.search(r'\d', password):
            return False
        
        if policy['require_special'] and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False
        
        return True
    
    def _hash_password(self, password: str, salt: str) -> str:
        """Hashe un mot de passe avec salt"""
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
    
    def _verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        """Vérifie un mot de passe"""
        return self._hash_password(password, salt) == password_hash
    
    def _handle_failed_login(self, user_id: Optional[str], ip_address: str, 
                           user_agent: str, reason: str):
        """Gère une tentative de connexion échouée"""
        # Incrémenter le compteur d'échecs pour l'IP
        self.intrusion_detection['failed_logins'][ip_address].append(datetime.now())
        
        # Nettoyer les anciens échecs (> 1 heure)
        cutoff = datetime.now() - timedelta(hours=1)
        while (self.intrusion_detection['failed_logins'][ip_address] and 
               self.intrusion_detection['failed_logins'][ip_address][0] < cutoff):
            self.intrusion_detection['failed_logins'][ip_address].popleft()
        
        # Vérifier si l'IP doit être bloquée
        failed_count = len(self.intrusion_detection['failed_logins'][ip_address])
        if failed_count >= 10:  # 10 échecs en 1 heure
            self._block_ip(ip_address, duration_minutes=60)
        
        # Incrémenter le compteur d'échecs pour l'utilisateur
        if user_id:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE users 
                    SET failed_login_attempts = failed_login_attempts + 1,
                        updated_at = ?
                    WHERE id = ?
                """, (datetime.now().isoformat(), user_id))
                
                # Vérifier si le compte doit être verrouillé
                cursor = conn.execute("SELECT failed_login_attempts FROM users WHERE id = ?", (user_id,))
                row = cursor.fetchone()
                if row and row[0] >= self.config['lockout_policy']['max_failed_attempts']:
                    self._lock_user_account(user_id)
        
        # Enregistrer l'événement
        self._log_security_event(
            event_type="failed_login",
            threat_level=ThreatLevel.MEDIUM if failed_count < 5 else ThreatLevel.HIGH,
            user_id=user_id,
            description=f"Échec de connexion: {reason}",
            details={'reason': reason, 'failed_count': failed_count},
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def _handle_successful_login(self, user_id: str, ip_address: str, user_agent: str):
        """Gère une connexion réussie"""
        # Réinitialiser le compteur d'échecs
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE users 
                SET failed_login_attempts = 0, last_login = ?, updated_at = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), datetime.now().isoformat(), user_id))
        
        # Nettoyer les échecs pour cette IP
        if ip_address in self.intrusion_detection['failed_logins']:
            self.intrusion_detection['failed_logins'][ip_address].clear()
        
        # Enregistrer l'événement
        self._log_security_event(
            event_type="successful_login",
            threat_level=ThreatLevel.INFO,
            user_id=user_id,
            description="Connexion réussie",
            details={'ip_address': ip_address},
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def _lock_user_account(self, user_id: str):
        """Verrouille un compte utilisateur"""
        lockout_duration = self.config['lockout_policy']['lockout_duration_minutes']
        locked_until = datetime.now() + timedelta(minutes=lockout_duration)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE users 
                SET account_locked = TRUE, locked_until = ?, updated_at = ?
                WHERE id = ?
            """, (locked_until.isoformat(), datetime.now().isoformat(), user_id))
        
        self._log_security_event(
            event_type="account_locked",
            threat_level=ThreatLevel.HIGH,
            user_id=user_id,
            description=f"Compte verrouillé jusqu'à {locked_until}",
            details={'locked_until': locked_until.isoformat(), 'duration_minutes': lockout_duration}
        )
    
    def _unlock_user_account(self, user_id: str):
        """Déverrouille un compte utilisateur"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE users 
                SET account_locked = FALSE, locked_until = NULL, 
                    failed_login_attempts = 0, updated_at = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), user_id))
        
        self._log_security_event(
            event_type="account_unlocked",
            threat_level=ThreatLevel.INFO,
            user_id=user_id,
            description="Compte déverrouillé",
            details={}
        )
    
    def _block_ip(self, ip_address: str, duration_minutes: int = 60):
        """Bloque une adresse IP"""
        blocked_until = datetime.now() + timedelta(minutes=duration_minutes)
        self.intrusion_detection['blocked_ips'][ip_address] = blocked_until
        
        self._log_security_event(
            event_type="ip_blocked",
            threat_level=ThreatLevel.HIGH,
            description=f"IP bloquée: {ip_address}",
            details={'ip_address': ip_address, 'blocked_until': blocked_until.isoformat()},
            ip_address=ip_address
        )
    
    def _is_ip_blocked(self, ip_address: str) -> bool:
        """Vérifie si une IP est bloquée"""
        if ip_address in self.intrusion_detection['blocked_ips']:
            blocked_until = self.intrusion_detection['blocked_ips'][ip_address]
            if datetime.now() < blocked_until:
                return True
            else:
                # Débloquer l'IP
                del self.intrusion_detection['blocked_ips'][ip_address]
        
        return False
    
    def _create_session(self, user_id: str, ip_address: str, user_agent: str) -> str:
        """Crée une session utilisateur"""
        session_id = secrets.token_urlsafe(32)
        session_token = secrets.token_urlsafe(64)
        
        timeout_minutes = self.config['session_policy']['timeout_minutes']
        expires_at = datetime.now() + timedelta(minutes=timeout_minutes)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO sessions 
                (id, user_id, token, ip_address, user_agent, created_at, 
                 expires_at, last_activity, active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id, user_id, session_token, ip_address, user_agent,
                datetime.now().isoformat(), expires_at.isoformat(),
                datetime.now().isoformat(), True
            ))
        
        return session_token
    
    def _generate_jwt_token(self, user: User) -> str:
        """Génère un token JWT"""
        payload = {
            'user_id': user.id,
            'username': user.username,
            'roles': user.roles,
            'permissions': user.permissions,
            'security_level': user.security_level.value,
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow(),
            'iss': 'substans.ai'
        }
        
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def validate_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Valide un token JWT"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Récupère un utilisateur par ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            
            if row:
                return User(
                    id=row['id'],
                    username=row['username'],
                    email=row['email'],
                    password_hash=row['password_hash'],
                    salt=row['salt'],
                    roles=json.loads(row['roles']),
                    permissions=json.loads(row['permissions']),
                    security_level=SecurityLevel(row['security_level']),
                    mfa_enabled=bool(row['mfa_enabled']),
                    mfa_secret=row['mfa_secret'],
                    last_login=datetime.fromisoformat(row['last_login']) if row['last_login'] else None,
                    failed_login_attempts=row['failed_login_attempts'],
                    account_locked=bool(row['account_locked']),
                    locked_until=datetime.fromisoformat(row['locked_until']) if row['locked_until'] else None,
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at']),
                    active=bool(row['active'])
                )
            return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Récupère un utilisateur par nom d'utilisateur"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            
            if row:
                return self.get_user(row['id'])
            return None
    
    def _log_security_event(self, event_type: str, threat_level: ThreatLevel,
                          description: str, details: Dict[str, Any],
                          user_id: Optional[str] = None, ip_address: str = "",
                          user_agent: str = ""):
        """Enregistre un événement de sécurité"""
        event_id = f"sec_{int(time.time() * 1000000)}"
        
        event = SecurityEvent(
            id=event_id,
            event_type=event_type,
            threat_level=threat_level,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            description=description,
            details=details,
            timestamp=datetime.now(),
            resolved=False,
            resolution_notes=None
        )
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO security_events 
                (id, event_type, threat_level, user_id, ip_address, user_agent,
                 description, details, timestamp, resolved, resolution_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.id, event.event_type, event.threat_level.value,
                event.user_id, event.ip_address, event.user_agent,
                event.description, json.dumps(event.details),
                event.timestamp.isoformat(), event.resolved, event.resolution_notes
            ))
    
    def create_security_policy(self, policy: SecurityPolicy):
        """Crée une politique de sécurité"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO security_policies 
                (id, name, description, rules, security_level, active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                policy.id, policy.name, policy.description,
                json.dumps(policy.rules), policy.security_level.value,
                policy.active, policy.created_at.isoformat(),
                policy.updated_at.isoformat()
            ))
    
    def _requires_ip_whitelist(self, user: User) -> bool:
        """Vérifie si l'utilisateur nécessite une whitelist IP"""
        # Vérifier les politiques de sécurité
        if user.security_level in [SecurityLevel.HIGH, SecurityLevel.CRITICAL]:
            return True
        
        # Vérifier les rôles admin
        if 'admin' in user.roles:
            return True
        
        return False
    
    def _is_ip_whitelisted(self, user_id: str, ip_address: str) -> bool:
        """Vérifie si une IP est dans la whitelist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT COUNT(*) FROM ip_whitelist 
                WHERE (user_id = ? OR user_id IS NULL) 
                AND ip_address = ? AND active = TRUE
            """, (user_id, ip_address))
            
            count = cursor.fetchone()[0]
            return count > 0
    
    def _add_password_to_history(self, user_id: str, password_hash: str):
        """Ajoute un mot de passe à l'historique"""
        history_id = f"pwd_{int(time.time() * 1000000)}"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO password_history (id, user_id, password_hash, created_at)
                VALUES (?, ?, ?, ?)
            """, (history_id, user_id, password_hash, datetime.now().isoformat()))
            
            # Nettoyer l'ancien historique (garder seulement les N derniers)
            history_count = self.config['password_policy']['history_count']
            conn.execute("""
                DELETE FROM password_history 
                WHERE user_id = ? AND id NOT IN (
                    SELECT id FROM password_history 
                    WHERE user_id = ? 
                    ORDER BY created_at DESC 
                    LIMIT ?
                )
            """, (user_id, user_id, history_count))
    
    def get_security_events(self, threat_level: Optional[ThreatLevel] = None,
                          limit: int = 100) -> List[SecurityEvent]:
        """Récupère les événements de sécurité"""
        query = "SELECT * FROM security_events"
        params = []
        
        if threat_level:
            query += " WHERE threat_level = ?"
            params.append(threat_level.value)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            
            events = []
            for row in cursor.fetchall():
                event = SecurityEvent(
                    id=row['id'],
                    event_type=row['event_type'],
                    threat_level=ThreatLevel(row['threat_level']),
                    user_id=row['user_id'],
                    ip_address=row['ip_address'],
                    user_agent=row['user_agent'],
                    description=row['description'],
                    details=json.loads(row['details']),
                    timestamp=datetime.fromisoformat(row['timestamp']),
                    resolved=bool(row['resolved']),
                    resolution_notes=row['resolution_notes']
                )
                events.append(event)
            
            return events
    
    def get_security_dashboard(self) -> Dict[str, Any]:
        """Récupère le tableau de bord de sécurité"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Statistiques des événements
            cursor = conn.execute("""
                SELECT threat_level, COUNT(*) as count
                FROM security_events 
                WHERE timestamp >= datetime('now', '-24 hours')
                GROUP BY threat_level
            """)
            
            threat_stats = {row['threat_level']: row['count'] for row in cursor.fetchall()}
            
            # Utilisateurs actifs
            cursor = conn.execute("""
                SELECT COUNT(*) as count FROM users WHERE active = TRUE
            """)
            active_users = cursor.fetchone()['count']
            
            # Sessions actives
            cursor = conn.execute("""
                SELECT COUNT(*) as count FROM sessions 
                WHERE active = TRUE AND expires_at > datetime('now')
            """)
            active_sessions = cursor.fetchone()['count']
            
            # Comptes verrouillés
            cursor = conn.execute("""
                SELECT COUNT(*) as count FROM users WHERE account_locked = TRUE
            """)
            locked_accounts = cursor.fetchone()['count']
            
            # IPs bloquées
            blocked_ips_count = len(self.intrusion_detection['blocked_ips'])
            
            # Événements récents
            recent_events = self.get_security_events(limit=10)
        
        return {
            'threat_stats': threat_stats,
            'active_users': active_users,
            'active_sessions': active_sessions,
            'locked_accounts': locked_accounts,
            'blocked_ips': blocked_ips_count,
            'recent_events': [event.to_dict() for event in recent_events],
            'generated_at': datetime.now().isoformat()
        }
    
    def _start_security_monitor(self):
        """Démarre le monitoring de sécurité"""
        def monitor_loop():
            while True:
                try:
                    # Nettoyer les sessions expirées
                    with sqlite3.connect(self.db_path) as conn:
                        conn.execute("""
                            UPDATE sessions SET active = FALSE 
                            WHERE expires_at < datetime('now')
                        """)
                    
                    # Nettoyer les anciens événements de sécurité
                    retention_days = self.config['audit_policy']['retention_days']
                    cutoff_date = datetime.now() - timedelta(days=retention_days)
                    
                    with sqlite3.connect(self.db_path) as conn:
                        conn.execute("""
                            DELETE FROM security_events 
                            WHERE timestamp < ? AND resolved = TRUE
                        """, (cutoff_date.isoformat(),))
                    
                    # Nettoyer les IPs bloquées expirées
                    now = datetime.now()
                    expired_ips = [
                        ip for ip, blocked_until in self.intrusion_detection['blocked_ips'].items()
                        if now >= blocked_until
                    ]
                    
                    for ip in expired_ips:
                        del self.intrusion_detection['blocked_ips'][ip]
                    
                    time.sleep(300)  # 5 minutes
                    
                except Exception as e:
                    logger.error(f"Erreur monitoring sécurité: {e}")
                    time.sleep(60)
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        logger.info("Monitoring de sécurité démarré")

# Exemple d'utilisation
if __name__ == "__main__":
    # Créer le gestionnaire de sécurité
    security_manager = SecurityManager()
    
    # Tester l'authentification admin
    auth_result = security_manager.authenticate_user(
        username="admin",
        password="SubstansAI@2024!",
        ip_address="127.0.0.1",
        user_agent="Test Client"
    )
    
    if auth_result:
        print(f"Authentification réussie: {auth_result['username']}")
        print(f"Token JWT: {auth_result['jwt_token'][:50]}...")
        
        # Valider le token JWT
        payload = security_manager.validate_jwt_token(auth_result['jwt_token'])
        if payload:
            print(f"Token valide pour: {payload['username']}")
    else:
        print("Échec de l'authentification")
    
    # Afficher le tableau de bord de sécurité
    dashboard = security_manager.get_security_dashboard()
    print(f"\nTableau de bord sécurité:")
    print(f"- Utilisateurs actifs: {dashboard['active_users']}")
    print(f"- Sessions actives: {dashboard['active_sessions']}")
    print(f"- Comptes verrouillés: {dashboard['locked_accounts']}")
    print(f"- IPs bloquées: {dashboard['blocked_ips']}")
    print(f"- Événements récents: {len(dashboard['recent_events'])}")

