#!/usr/bin/env python3
"""
Encryption System - Substans.AI Enterprise
Système de chiffrement avancé pour la sécurité des données
"""

import os
import json
import base64
import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import threading
import time
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import hmac

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EncryptionAlgorithm(Enum):
    """Algorithmes de chiffrement"""
    AES_256_GCM = "aes_256_gcm"
    AES_256_CBC = "aes_256_cbc"
    FERNET = "fernet"
    RSA_2048 = "rsa_2048"
    RSA_4096 = "rsa_4096"
    CHACHA20_POLY1305 = "chacha20_poly1305"

class KeyType(Enum):
    """Types de clés"""
    SYMMETRIC = "symmetric"
    ASYMMETRIC_PUBLIC = "asymmetric_public"
    ASYMMETRIC_PRIVATE = "asymmetric_private"
    DERIVED = "derived"
    MASTER = "master"

class SecurityLevel(Enum):
    """Niveaux de sécurité"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    TOP_SECRET = "top_secret"

@dataclass
class EncryptionKey:
    """Clé de chiffrement"""
    id: str
    name: str
    key_type: KeyType
    algorithm: EncryptionAlgorithm
    security_level: SecurityLevel
    key_data: bytes
    salt: Optional[bytes]
    iv: Optional[bytes]
    created_at: datetime
    expires_at: Optional[datetime]
    usage_count: int
    max_usage: Optional[int]
    metadata: Dict[str, Any]
    is_active: bool
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['key_type'] = self.key_type.value
        data['algorithm'] = self.algorithm.value
        data['security_level'] = self.security_level.value
        data['key_data'] = base64.b64encode(self.key_data).decode()
        data['salt'] = base64.b64encode(self.salt).decode() if self.salt else None
        data['iv'] = base64.b64encode(self.iv).decode() if self.iv else None
        data['created_at'] = self.created_at.isoformat()
        data['expires_at'] = self.expires_at.isoformat() if self.expires_at else None
        return data

@dataclass
class EncryptionResult:
    """Résultat de chiffrement"""
    encrypted_data: bytes
    key_id: str
    algorithm: EncryptionAlgorithm
    iv: Optional[bytes]
    tag: Optional[bytes]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'encrypted_data': base64.b64encode(self.encrypted_data).decode(),
            'key_id': self.key_id,
            'algorithm': self.algorithm.value,
            'iv': base64.b64encode(self.iv).decode() if self.iv else None,
            'tag': base64.b64encode(self.tag).decode() if self.tag else None,
            'metadata': self.metadata
        }

@dataclass
class EncryptionPolicy:
    """Politique de chiffrement"""
    id: str
    name: str
    description: str
    data_types: List[str]
    required_algorithm: EncryptionAlgorithm
    min_security_level: SecurityLevel
    key_rotation_days: int
    max_key_usage: Optional[int]
    require_authentication: bool
    audit_level: str
    conditions: Dict[str, Any]
    active: bool
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['required_algorithm'] = self.required_algorithm.value
        data['min_security_level'] = self.min_security_level.value
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data

class EncryptionSystem:
    """Système de chiffrement enterprise"""
    
    def __init__(self, db_path: str = "encryption.db", key_store_path: str = "keystore"):
        self.db_path = db_path
        self.key_store_path = key_store_path
        
        # Configuration du système
        self.config = {
            'default_algorithm': EncryptionAlgorithm.AES_256_GCM,
            'default_security_level': SecurityLevel.HIGH,
            'key_rotation_enabled': True,
            'key_rotation_interval': 90,  # jours
            'max_key_age_days': 365,
            'require_key_backup': True,
            'audit_all_operations': True,
            'performance_monitoring': True
        }
        
        # Cache des clés actives
        self.key_cache = {}
        self.cache_lock = threading.RLock()
        
        # Métriques de performance
        self.performance_metrics = {
            'encryption_operations': 0,
            'decryption_operations': 0,
            'key_generations': 0,
            'key_rotations': 0,
            'average_encryption_time': 0,
            'average_decryption_time': 0,
            'cache_hit_rate': 0,
            'total_keys_managed': 0
        }
        
        # Politiques de chiffrement par défaut
        self.default_policies = {
            'personal_data': {
                'name': 'Données Personnelles',
                'description': 'Chiffrement des données personnelles (RGPD)',
                'data_types': ['user_data', 'personal_info', 'contact_info'],
                'required_algorithm': EncryptionAlgorithm.AES_256_GCM,
                'min_security_level': SecurityLevel.HIGH,
                'key_rotation_days': 90,
                'max_key_usage': 10000,
                'require_authentication': True,
                'audit_level': 'detailed'
            },
            'financial_data': {
                'name': 'Données Financières',
                'description': 'Chiffrement des données financières sensibles',
                'data_types': ['financial_records', 'payment_info', 'bank_details'],
                'required_algorithm': EncryptionAlgorithm.AES_256_GCM,
                'min_security_level': SecurityLevel.CRITICAL,
                'key_rotation_days': 30,
                'max_key_usage': 5000,
                'require_authentication': True,
                'audit_level': 'detailed'
            },
            'business_data': {
                'name': 'Données Métier',
                'description': 'Chiffrement des données métier standard',
                'data_types': ['documents', 'reports', 'analytics'],
                'required_algorithm': EncryptionAlgorithm.AES_256_CBC,
                'min_security_level': SecurityLevel.MEDIUM,
                'key_rotation_days': 180,
                'max_key_usage': 50000,
                'require_authentication': False,
                'audit_level': 'standard'
            }
        }
        
        # Créer le répertoire de stockage des clés
        os.makedirs(self.key_store_path, exist_ok=True)
        
        self._init_database()
        self._init_master_key()
        self._init_default_policies()
        self._start_encryption_services()
        
        logger.info("Encryption System initialisé")
    
    def _init_database(self):
        """Initialise la base de données de chiffrement"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS encryption_keys (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    key_type TEXT NOT NULL,
                    algorithm TEXT NOT NULL,
                    security_level TEXT NOT NULL,
                    key_data_hash TEXT NOT NULL,
                    salt TEXT,
                    iv TEXT,
                    created_at TEXT NOT NULL,
                    expires_at TEXT,
                    usage_count INTEGER DEFAULT 0,
                    max_usage INTEGER,
                    metadata TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE
                );
                
                CREATE TABLE IF NOT EXISTS encryption_policies (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    data_types TEXT NOT NULL,
                    required_algorithm TEXT NOT NULL,
                    min_security_level TEXT NOT NULL,
                    key_rotation_days INTEGER NOT NULL,
                    max_key_usage INTEGER,
                    require_authentication BOOLEAN NOT NULL,
                    audit_level TEXT NOT NULL,
                    conditions TEXT NOT NULL,
                    active BOOLEAN DEFAULT TRUE,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS encryption_operations (
                    id TEXT PRIMARY KEY,
                    operation_type TEXT NOT NULL,
                    key_id TEXT NOT NULL,
                    algorithm TEXT NOT NULL,
                    data_size INTEGER NOT NULL,
                    processing_time REAL NOT NULL,
                    success BOOLEAN NOT NULL,
                    error_message TEXT,
                    user_id TEXT,
                    ip_address TEXT,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (key_id) REFERENCES encryption_keys (id)
                );
                
                CREATE TABLE IF NOT EXISTS key_rotations (
                    id TEXT PRIMARY KEY,
                    old_key_id TEXT NOT NULL,
                    new_key_id TEXT NOT NULL,
                    rotation_reason TEXT NOT NULL,
                    affected_records INTEGER DEFAULT 0,
                    rotation_time REAL NOT NULL,
                    success BOOLEAN NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (old_key_id) REFERENCES encryption_keys (id),
                    FOREIGN KEY (new_key_id) REFERENCES encryption_keys (id)
                );
                
                CREATE TABLE IF NOT EXISTS encrypted_data_registry (
                    id TEXT PRIMARY KEY,
                    data_identifier TEXT NOT NULL,
                    data_type TEXT NOT NULL,
                    key_id TEXT NOT NULL,
                    algorithm TEXT NOT NULL,
                    encryption_metadata TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_accessed TEXT,
                    access_count INTEGER DEFAULT 0,
                    FOREIGN KEY (key_id) REFERENCES encryption_keys (id)
                );
                
                CREATE INDEX IF NOT EXISTS idx_encryption_keys_algorithm ON encryption_keys(algorithm);
                CREATE INDEX IF NOT EXISTS idx_encryption_keys_security_level ON encryption_keys(security_level);
                CREATE INDEX IF NOT EXISTS idx_encryption_operations_timestamp ON encryption_operations(timestamp);
                CREATE INDEX IF NOT EXISTS idx_key_rotations_timestamp ON key_rotations(timestamp);
                CREATE INDEX IF NOT EXISTS idx_encrypted_data_registry_data_type ON encrypted_data_registry(data_type);
            """)
    
    def _init_master_key(self):
        """Initialise la clé maître"""
        master_key_file = os.path.join(self.key_store_path, "master.key")
        
        if not os.path.exists(master_key_file):
            # Générer une nouvelle clé maître
            master_key = Fernet.generate_key()
            
            # Sauvegarder de manière sécurisée
            with open(master_key_file, 'wb') as f:
                f.write(master_key)
            
            # Permissions restrictives
            os.chmod(master_key_file, 0o600)
            
            logger.info("Clé maître générée et sauvegardée")
        
        # Charger la clé maître
        with open(master_key_file, 'rb') as f:
            self.master_key = f.read()
        
        self.master_fernet = Fernet(self.master_key)
    
    def _init_default_policies(self):
        """Initialise les politiques de chiffrement par défaut"""
        for policy_id, config in self.default_policies.items():
            if not self.get_encryption_policy(policy_id):
                policy = EncryptionPolicy(
                    id=policy_id,
                    name=config['name'],
                    description=config['description'],
                    data_types=config['data_types'],
                    required_algorithm=config['required_algorithm'],
                    min_security_level=config['min_security_level'],
                    key_rotation_days=config['key_rotation_days'],
                    max_key_usage=config['max_key_usage'],
                    require_authentication=config['require_authentication'],
                    audit_level=config['audit_level'],
                    conditions={},
                    active=True,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
                self.create_encryption_policy(policy)
    
    def generate_key(self, name: str, algorithm: EncryptionAlgorithm,
                    security_level: SecurityLevel = SecurityLevel.HIGH,
                    expires_in_days: Optional[int] = None,
                    max_usage: Optional[int] = None,
                    metadata: Dict[str, Any] = None) -> str:
        """Génère une nouvelle clé de chiffrement"""
        
        key_id = f"key_{int(time.time() * 1000000)}"
        metadata = metadata or {}
        
        # Générer la clé selon l'algorithme
        if algorithm == EncryptionAlgorithm.AES_256_GCM:
            key_data = os.urandom(32)  # 256 bits
            salt = os.urandom(16)
            iv = None
        elif algorithm == EncryptionAlgorithm.AES_256_CBC:
            key_data = os.urandom(32)  # 256 bits
            salt = os.urandom(16)
            iv = os.urandom(16)
        elif algorithm == EncryptionAlgorithm.FERNET:
            key_data = Fernet.generate_key()
            salt = None
            iv = None
        elif algorithm == EncryptionAlgorithm.RSA_2048:
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            key_data = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            salt = None
            iv = None
        elif algorithm == EncryptionAlgorithm.RSA_4096:
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=4096,
                backend=default_backend()
            )
            key_data = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            salt = None
            iv = None
        elif algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
            key_data = os.urandom(32)  # 256 bits
            salt = os.urandom(16)
            iv = None
        else:
            raise ValueError(f"Algorithme non supporté: {algorithm}")
        
        # Déterminer le type de clé
        if algorithm in [EncryptionAlgorithm.RSA_2048, EncryptionAlgorithm.RSA_4096]:
            key_type = KeyType.ASYMMETRIC_PRIVATE
        else:
            key_type = KeyType.SYMMETRIC
        
        # Calculer la date d'expiration
        expires_at = None
        if expires_in_days:
            expires_at = datetime.now() + timedelta(days=expires_in_days)
        
        # Créer l'objet clé
        encryption_key = EncryptionKey(
            id=key_id,
            name=name,
            key_type=key_type,
            algorithm=algorithm,
            security_level=security_level,
            key_data=key_data,
            salt=salt,
            iv=iv,
            created_at=datetime.now(),
            expires_at=expires_at,
            usage_count=0,
            max_usage=max_usage,
            metadata=metadata,
            is_active=True
        )
        
        # Sauvegarder la clé
        self._save_key(encryption_key)
        
        # Ajouter au cache
        with self.cache_lock:
            self.key_cache[key_id] = encryption_key
        
        # Mettre à jour les métriques
        self.performance_metrics['key_generations'] += 1
        self.performance_metrics['total_keys_managed'] += 1
        
        logger.info(f"Clé générée: {key_id} ({algorithm.value})")
        return key_id
    
    def _save_key(self, key: EncryptionKey):
        """Sauvegarde une clé de manière sécurisée"""
        # Chiffrer la clé avec la clé maître
        encrypted_key_data = self.master_fernet.encrypt(key.key_data)
        
        # Calculer le hash pour la base de données
        key_data_hash = hashlib.sha256(key.key_data).hexdigest()
        
        # Sauvegarder dans la base de données
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO encryption_keys 
                (id, name, key_type, algorithm, security_level, key_data_hash,
                 salt, iv, created_at, expires_at, usage_count, max_usage,
                 metadata, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                key.id, key.name, key.key_type.value, key.algorithm.value,
                key.security_level.value, key_data_hash,
                base64.b64encode(key.salt).decode() if key.salt else None,
                base64.b64encode(key.iv).decode() if key.iv else None,
                key.created_at.isoformat(),
                key.expires_at.isoformat() if key.expires_at else None,
                key.usage_count, key.max_usage,
                json.dumps(key.metadata), key.is_active
            ))
        
        # Sauvegarder la clé chiffrée sur disque
        key_file = os.path.join(self.key_store_path, f"{key.id}.key")
        with open(key_file, 'wb') as f:
            f.write(encrypted_key_data)
        
        # Permissions restrictives
        os.chmod(key_file, 0o600)
    
    def get_key(self, key_id: str) -> Optional[EncryptionKey]:
        """Récupère une clé de chiffrement"""
        # Vérifier le cache
        with self.cache_lock:
            if key_id in self.key_cache:
                return self.key_cache[key_id]
        
        # Charger depuis la base de données
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM encryption_keys WHERE id = ?", (key_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
        
        # Charger la clé chiffrée depuis le disque
        key_file = os.path.join(self.key_store_path, f"{key_id}.key")
        if not os.path.exists(key_file):
            logger.error(f"Fichier clé manquant: {key_file}")
            return None
        
        with open(key_file, 'rb') as f:
            encrypted_key_data = f.read()
        
        # Déchiffrer la clé
        try:
            key_data = self.master_fernet.decrypt(encrypted_key_data)
        except Exception as e:
            logger.error(f"Erreur déchiffrement clé {key_id}: {e}")
            return None
        
        # Reconstruire l'objet clé
        encryption_key = EncryptionKey(
            id=row['id'],
            name=row['name'],
            key_type=KeyType(row['key_type']),
            algorithm=EncryptionAlgorithm(row['algorithm']),
            security_level=SecurityLevel(row['security_level']),
            key_data=key_data,
            salt=base64.b64decode(row['salt']) if row['salt'] else None,
            iv=base64.b64decode(row['iv']) if row['iv'] else None,
            created_at=datetime.fromisoformat(row['created_at']),
            expires_at=datetime.fromisoformat(row['expires_at']) if row['expires_at'] else None,
            usage_count=row['usage_count'],
            max_usage=row['max_usage'],
            metadata=json.loads(row['metadata']),
            is_active=bool(row['is_active'])
        )
        
        # Ajouter au cache
        with self.cache_lock:
            self.key_cache[key_id] = encryption_key
        
        return encryption_key
    
    def encrypt_data(self, data: Union[str, bytes], key_id: Optional[str] = None,
                    algorithm: Optional[EncryptionAlgorithm] = None,
                    data_type: Optional[str] = None,
                    user_id: Optional[str] = None,
                    ip_address: str = "") -> EncryptionResult:
        """Chiffre des données"""
        
        start_time = time.time()
        
        # Convertir en bytes si nécessaire
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Déterminer la clé à utiliser
        if not key_id:
            # Sélectionner une clé selon la politique
            key_id = self._select_key_for_data_type(data_type, algorithm)
        
        if not key_id:
            # Générer une nouvelle clé si nécessaire
            algorithm = algorithm or self.config['default_algorithm']
            key_id = self.generate_key(
                name=f"auto_key_{data_type or 'generic'}",
                algorithm=algorithm,
                security_level=self.config['default_security_level']
            )
        
        # Récupérer la clé
        key = self.get_key(key_id)
        if not key:
            raise ValueError(f"Clé introuvable: {key_id}")
        
        # Vérifier la validité de la clé
        if not key.is_active:
            raise ValueError(f"Clé inactive: {key_id}")
        
        if key.expires_at and key.expires_at < datetime.now():
            raise ValueError(f"Clé expirée: {key_id}")
        
        if key.max_usage and key.usage_count >= key.max_usage:
            raise ValueError(f"Limite d'utilisation atteinte: {key_id}")
        
        # Chiffrer selon l'algorithme
        try:
            if key.algorithm == EncryptionAlgorithm.AES_256_GCM:
                encrypted_data, iv, tag = self._encrypt_aes_gcm(data, key.key_data)
            elif key.algorithm == EncryptionAlgorithm.AES_256_CBC:
                encrypted_data, iv = self._encrypt_aes_cbc(data, key.key_data, key.iv)
                tag = None
            elif key.algorithm == EncryptionAlgorithm.FERNET:
                fernet = Fernet(key.key_data)
                encrypted_data = fernet.encrypt(data)
                iv = None
                tag = None
            elif key.algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
                encrypted_data, iv, tag = self._encrypt_chacha20_poly1305(data, key.key_data)
            else:
                raise ValueError(f"Algorithme de chiffrement non supporté: {key.algorithm}")
            
            # Incrémenter le compteur d'utilisation
            self._increment_key_usage(key_id)
            
            # Créer le résultat
            result = EncryptionResult(
                encrypted_data=encrypted_data,
                key_id=key_id,
                algorithm=key.algorithm,
                iv=iv,
                tag=tag,
                metadata={
                    'data_type': data_type,
                    'original_size': len(data),
                    'encrypted_size': len(encrypted_data),
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            # Enregistrer l'opération
            processing_time = time.time() - start_time
            self._log_operation('encrypt', key_id, key.algorithm, len(data), 
                              processing_time, True, None, user_id, ip_address)
            
            # Enregistrer dans le registre des données chiffrées
            if data_type:
                self._register_encrypted_data(result, data_type)
            
            # Mettre à jour les métriques
            self.performance_metrics['encryption_operations'] += 1
            self._update_average_time('encryption', processing_time)
            
            logger.debug(f"Données chiffrées avec la clé {key_id}")
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            self._log_operation('encrypt', key_id, key.algorithm, len(data), 
                              processing_time, False, str(e), user_id, ip_address)
            raise
    
    def decrypt_data(self, encrypted_result: Union[EncryptionResult, Dict[str, Any]],
                    user_id: Optional[str] = None,
                    ip_address: str = "") -> bytes:
        """Déchiffre des données"""
        
        start_time = time.time()
        
        # Convertir depuis dict si nécessaire
        if isinstance(encrypted_result, dict):
            encrypted_result = EncryptionResult(
                encrypted_data=base64.b64decode(encrypted_result['encrypted_data']),
                key_id=encrypted_result['key_id'],
                algorithm=EncryptionAlgorithm(encrypted_result['algorithm']),
                iv=base64.b64decode(encrypted_result['iv']) if encrypted_result.get('iv') else None,
                tag=base64.b64decode(encrypted_result['tag']) if encrypted_result.get('tag') else None,
                metadata=encrypted_result.get('metadata', {})
            )
        
        # Récupérer la clé
        key = self.get_key(encrypted_result.key_id)
        if not key:
            raise ValueError(f"Clé introuvable: {encrypted_result.key_id}")
        
        # Déchiffrer selon l'algorithme
        try:
            if encrypted_result.algorithm == EncryptionAlgorithm.AES_256_GCM:
                decrypted_data = self._decrypt_aes_gcm(
                    encrypted_result.encrypted_data, key.key_data,
                    encrypted_result.iv, encrypted_result.tag
                )
            elif encrypted_result.algorithm == EncryptionAlgorithm.AES_256_CBC:
                decrypted_data = self._decrypt_aes_cbc(
                    encrypted_result.encrypted_data, key.key_data, encrypted_result.iv
                )
            elif encrypted_result.algorithm == EncryptionAlgorithm.FERNET:
                fernet = Fernet(key.key_data)
                decrypted_data = fernet.decrypt(encrypted_result.encrypted_data)
            elif encrypted_result.algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
                decrypted_data = self._decrypt_chacha20_poly1305(
                    encrypted_result.encrypted_data, key.key_data,
                    encrypted_result.iv, encrypted_result.tag
                )
            else:
                raise ValueError(f"Algorithme de déchiffrement non supporté: {encrypted_result.algorithm}")
            
            # Enregistrer l'opération
            processing_time = time.time() - start_time
            self._log_operation('decrypt', encrypted_result.key_id, encrypted_result.algorithm,
                              len(encrypted_result.encrypted_data), processing_time, True,
                              None, user_id, ip_address)
            
            # Mettre à jour les métriques
            self.performance_metrics['decryption_operations'] += 1
            self._update_average_time('decryption', processing_time)
            
            logger.debug(f"Données déchiffrées avec la clé {encrypted_result.key_id}")
            return decrypted_data
            
        except Exception as e:
            processing_time = time.time() - start_time
            self._log_operation('decrypt', encrypted_result.key_id, encrypted_result.algorithm,
                              len(encrypted_result.encrypted_data), processing_time, False,
                              str(e), user_id, ip_address)
            raise
    
    def _encrypt_aes_gcm(self, data: bytes, key: bytes) -> Tuple[bytes, bytes, bytes]:
        """Chiffrement AES-256-GCM"""
        iv = os.urandom(12)  # 96 bits pour GCM
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(data) + encryptor.finalize()
        return encrypted_data, iv, encryptor.tag
    
    def _decrypt_aes_gcm(self, encrypted_data: bytes, key: bytes, iv: bytes, tag: bytes) -> bytes:
        """Déchiffrement AES-256-GCM"""
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        return decryptor.update(encrypted_data) + decryptor.finalize()
    
    def _encrypt_aes_cbc(self, data: bytes, key: bytes, iv: bytes) -> Tuple[bytes, bytes]:
        """Chiffrement AES-256-CBC"""
        if not iv:
            iv = os.urandom(16)
        
        # Padding PKCS7
        pad_len = 16 - (len(data) % 16)
        padded_data = data + bytes([pad_len] * pad_len)
        
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        return encrypted_data, iv
    
    def _decrypt_aes_cbc(self, encrypted_data: bytes, key: bytes, iv: bytes) -> bytes:
        """Déchiffrement AES-256-CBC"""
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
        
        # Retirer le padding PKCS7
        pad_len = padded_data[-1]
        return padded_data[:-pad_len]
    
    def _encrypt_chacha20_poly1305(self, data: bytes, key: bytes) -> Tuple[bytes, bytes, bytes]:
        """Chiffrement ChaCha20-Poly1305"""
        nonce = os.urandom(12)
        cipher = Cipher(algorithms.ChaCha20(key, nonce), None, backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(data) + encryptor.finalize()
        
        # Calculer le tag d'authentification
        h = hmac.new(key, nonce + encrypted_data, hashlib.sha256)
        tag = h.digest()[:16]  # 128 bits
        
        return encrypted_data, nonce, tag
    
    def _decrypt_chacha20_poly1305(self, encrypted_data: bytes, key: bytes, 
                                  nonce: bytes, tag: bytes) -> bytes:
        """Déchiffrement ChaCha20-Poly1305"""
        # Vérifier le tag d'authentification
        h = hmac.new(key, nonce + encrypted_data, hashlib.sha256)
        expected_tag = h.digest()[:16]
        
        if not hmac.compare_digest(tag, expected_tag):
            raise ValueError("Tag d'authentification invalide")
        
        cipher = Cipher(algorithms.ChaCha20(key, nonce), None, backend=default_backend())
        decryptor = cipher.decryptor()
        return decryptor.update(encrypted_data) + decryptor.finalize()
    
    def _select_key_for_data_type(self, data_type: Optional[str], 
                                 algorithm: Optional[EncryptionAlgorithm]) -> Optional[str]:
        """Sélectionne une clé appropriée pour un type de données"""
        if not data_type:
            return None
        
        # Trouver une politique applicable
        policy = self._find_policy_for_data_type(data_type)
        if not policy:
            return None
        
        # Chercher une clé existante compatible
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            query = """
                SELECT id FROM encryption_keys 
                WHERE algorithm = ? AND security_level >= ? AND is_active = TRUE
                AND (expires_at IS NULL OR expires_at > ?)
                AND (max_usage IS NULL OR usage_count < max_usage)
                ORDER BY created_at DESC
                LIMIT 1
            """
            
            cursor = conn.execute(query, (
                policy.required_algorithm.value,
                policy.min_security_level.value,
                datetime.now().isoformat()
            ))
            
            row = cursor.fetchone()
            return row['id'] if row else None
    
    def _find_policy_for_data_type(self, data_type: str) -> Optional[EncryptionPolicy]:
        """Trouve une politique pour un type de données"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM encryption_policies WHERE active = TRUE")
            
            for row in cursor.fetchall():
                data_types = json.loads(row['data_types'])
                if data_type in data_types:
                    return EncryptionPolicy(
                        id=row['id'],
                        name=row['name'],
                        description=row['description'],
                        data_types=data_types,
                        required_algorithm=EncryptionAlgorithm(row['required_algorithm']),
                        min_security_level=SecurityLevel(row['min_security_level']),
                        key_rotation_days=row['key_rotation_days'],
                        max_key_usage=row['max_key_usage'],
                        require_authentication=bool(row['require_authentication']),
                        audit_level=row['audit_level'],
                        conditions=json.loads(row['conditions']),
                        active=bool(row['active']),
                        created_at=datetime.fromisoformat(row['created_at']),
                        updated_at=datetime.fromisoformat(row['updated_at'])
                    )
        
        return None
    
    def _increment_key_usage(self, key_id: str):
        """Incrémente le compteur d'utilisation d'une clé"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE encryption_keys 
                SET usage_count = usage_count + 1 
                WHERE id = ?
            """, (key_id,))
        
        # Mettre à jour le cache
        with self.cache_lock:
            if key_id in self.key_cache:
                self.key_cache[key_id].usage_count += 1
    
    def _log_operation(self, operation_type: str, key_id: str, algorithm: EncryptionAlgorithm,
                      data_size: int, processing_time: float, success: bool,
                      error_message: Optional[str], user_id: Optional[str], ip_address: str):
        """Enregistre une opération de chiffrement"""
        operation_id = f"op_{int(time.time() * 1000000)}"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO encryption_operations 
                (id, operation_type, key_id, algorithm, data_size, processing_time,
                 success, error_message, user_id, ip_address, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                operation_id, operation_type, key_id, algorithm.value, data_size,
                processing_time, success, error_message, user_id, ip_address,
                datetime.now().isoformat()
            ))
    
    def _register_encrypted_data(self, result: EncryptionResult, data_type: str):
        """Enregistre des données chiffrées dans le registre"""
        registry_id = f"reg_{int(time.time() * 1000000)}"
        data_identifier = hashlib.sha256(result.encrypted_data).hexdigest()[:16]
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO encrypted_data_registry 
                (id, data_identifier, data_type, key_id, algorithm, 
                 encryption_metadata, created_at, access_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                registry_id, data_identifier, data_type, result.key_id,
                result.algorithm.value, json.dumps(result.metadata),
                datetime.now().isoformat(), 0
            ))
    
    def _update_average_time(self, operation_type: str, processing_time: float):
        """Met à jour le temps moyen de traitement"""
        metric_key = f'average_{operation_type}_time'
        current_avg = self.performance_metrics[metric_key]
        operations_count = self.performance_metrics[f'{operation_type}_operations']
        
        # Calcul de la moyenne mobile
        new_avg = ((current_avg * (operations_count - 1)) + processing_time) / operations_count
        self.performance_metrics[metric_key] = round(new_avg, 4)
    
    def create_encryption_policy(self, policy: EncryptionPolicy) -> bool:
        """Crée une politique de chiffrement"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO encryption_policies 
                    (id, name, description, data_types, required_algorithm,
                     min_security_level, key_rotation_days, max_key_usage,
                     require_authentication, audit_level, conditions, active,
                     created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    policy.id, policy.name, policy.description,
                    json.dumps(policy.data_types), policy.required_algorithm.value,
                    policy.min_security_level.value, policy.key_rotation_days,
                    policy.max_key_usage, policy.require_authentication,
                    policy.audit_level, json.dumps(policy.conditions),
                    policy.active, policy.created_at.isoformat(),
                    policy.updated_at.isoformat()
                ))
            
            logger.info(f"Politique de chiffrement créée: {policy.name}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur création politique: {e}")
            return False
    
    def get_encryption_policy(self, policy_id: str) -> Optional[EncryptionPolicy]:
        """Récupère une politique de chiffrement"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM encryption_policies WHERE id = ?", (policy_id,))
            row = cursor.fetchone()
            
            if row:
                return EncryptionPolicy(
                    id=row['id'],
                    name=row['name'],
                    description=row['description'],
                    data_types=json.loads(row['data_types']),
                    required_algorithm=EncryptionAlgorithm(row['required_algorithm']),
                    min_security_level=SecurityLevel(row['min_security_level']),
                    key_rotation_days=row['key_rotation_days'],
                    max_key_usage=row['max_key_usage'],
                    require_authentication=bool(row['require_authentication']),
                    audit_level=row['audit_level'],
                    conditions=json.loads(row['conditions']),
                    active=bool(row['active']),
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at'])
                )
        
        return None
    
    def rotate_key(self, old_key_id: str, reason: str = "scheduled_rotation") -> str:
        """Effectue une rotation de clé"""
        start_time = time.time()
        
        # Récupérer l'ancienne clé
        old_key = self.get_key(old_key_id)
        if not old_key:
            raise ValueError(f"Clé introuvable: {old_key_id}")
        
        # Générer une nouvelle clé avec les mêmes paramètres
        new_key_id = self.generate_key(
            name=f"{old_key.name}_rotated",
            algorithm=old_key.algorithm,
            security_level=old_key.security_level,
            expires_in_days=365 if not old_key.expires_at else None,
            max_usage=old_key.max_usage,
            metadata={**old_key.metadata, 'rotated_from': old_key_id}
        )
        
        # Désactiver l'ancienne clé
        self._deactivate_key(old_key_id)
        
        # Enregistrer la rotation
        rotation_time = time.time() - start_time
        self._log_key_rotation(old_key_id, new_key_id, reason, rotation_time, True)
        
        # Mettre à jour les métriques
        self.performance_metrics['key_rotations'] += 1
        
        logger.info(f"Rotation de clé effectuée: {old_key_id} -> {new_key_id}")
        return new_key_id
    
    def _deactivate_key(self, key_id: str):
        """Désactive une clé"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE encryption_keys SET is_active = FALSE WHERE id = ?", (key_id,))
        
        # Retirer du cache
        with self.cache_lock:
            if key_id in self.key_cache:
                self.key_cache[key_id].is_active = False
    
    def _log_key_rotation(self, old_key_id: str, new_key_id: str, reason: str,
                         rotation_time: float, success: bool):
        """Enregistre une rotation de clé"""
        rotation_id = f"rot_{int(time.time() * 1000000)}"
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO key_rotations 
                (id, old_key_id, new_key_id, rotation_reason, rotation_time,
                 success, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                rotation_id, old_key_id, new_key_id, reason, rotation_time,
                success, datetime.now().isoformat()
            ))
    
    def get_encryption_dashboard(self) -> Dict[str, Any]:
        """Récupère le tableau de bord de chiffrement"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Statistiques des clés
            cursor = conn.execute("""
                SELECT algorithm, security_level, COUNT(*) as count
                FROM encryption_keys 
                WHERE is_active = TRUE
                GROUP BY algorithm, security_level
            """)
            
            key_stats = {}
            for row in cursor.fetchall():
                key = f"{row['algorithm']}_{row['security_level']}"
                key_stats[key] = row['count']
            
            # Opérations récentes
            cursor = conn.execute("""
                SELECT operation_type, COUNT(*) as count,
                       AVG(processing_time) as avg_time,
                       SUM(CASE WHEN success THEN 1 ELSE 0 END) as success_count
                FROM encryption_operations 
                WHERE timestamp >= datetime('now', '-24 hours')
                GROUP BY operation_type
            """)
            
            operation_stats = {}
            for row in cursor.fetchall():
                operation_stats[row['operation_type']] = {
                    'count': row['count'],
                    'avg_time': round(row['avg_time'], 4),
                    'success_rate': round((row['success_count'] / row['count']) * 100, 2)
                }
            
            # Clés expirant bientôt
            cursor = conn.execute("""
                SELECT COUNT(*) as count FROM encryption_keys 
                WHERE is_active = TRUE 
                AND expires_at IS NOT NULL 
                AND expires_at <= datetime('now', '+30 days')
            """)
            
            expiring_keys = cursor.fetchone()['count']
            
            # Politiques actives
            cursor = conn.execute("SELECT COUNT(*) as count FROM encryption_policies WHERE active = TRUE")
            active_policies = cursor.fetchone()['count']
        
        return {
            'key_statistics': key_stats,
            'operation_statistics': operation_stats,
            'expiring_keys_30_days': expiring_keys,
            'active_policies': active_policies,
            'performance_metrics': self.performance_metrics,
            'cache_size': len(self.key_cache),
            'generated_at': datetime.now().isoformat()
        }
    
    def _start_encryption_services(self):
        """Démarre les services de chiffrement"""
        def encryption_maintenance():
            while True:
                try:
                    # Rotation automatique des clés
                    self._auto_rotate_keys()
                    
                    # Nettoyage du cache
                    self._cleanup_key_cache()
                    
                    # Vérification de l'intégrité des clés
                    self._verify_key_integrity()
                    
                    time.sleep(3600)  # 1 heure
                    
                except Exception as e:
                    logger.error(f"Erreur maintenance chiffrement: {e}")
                    time.sleep(300)
        
        maintenance_thread = threading.Thread(target=encryption_maintenance, daemon=True)
        maintenance_thread.start()
        logger.info("Services de chiffrement démarrés")
    
    def _auto_rotate_keys(self):
        """Rotation automatique des clés"""
        if not self.config['key_rotation_enabled']:
            return
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Trouver les clés à faire tourner
            cursor = conn.execute("""
                SELECT id FROM encryption_keys 
                WHERE is_active = TRUE 
                AND created_at <= datetime('now', '-{} days')
            """.format(self.config['key_rotation_interval']))
            
            for row in cursor.fetchall():
                try:
                    self.rotate_key(row['id'], "automatic_rotation")
                except Exception as e:
                    logger.error(f"Erreur rotation automatique clé {row['id']}: {e}")
    
    def _cleanup_key_cache(self):
        """Nettoie le cache des clés"""
        with self.cache_lock:
            # Retirer les clés inactives du cache
            inactive_keys = [
                key_id for key_id, key in self.key_cache.items()
                if not key.is_active or (key.expires_at and key.expires_at < datetime.now())
            ]
            
            for key_id in inactive_keys:
                del self.key_cache[key_id]
            
            if inactive_keys:
                logger.info(f"Nettoyé {len(inactive_keys)} clés du cache")
    
    def _verify_key_integrity(self):
        """Vérifie l'intégrité des clés"""
        # Vérifier que tous les fichiers de clés existent
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT id FROM encryption_keys WHERE is_active = TRUE")
            
            for row in cursor.fetchall():
                key_file = os.path.join(self.key_store_path, f"{row['id']}.key")
                if not os.path.exists(key_file):
                    logger.error(f"Fichier clé manquant: {key_file}")
                    # Désactiver la clé
                    self._deactivate_key(row['id'])

# Exemple d'utilisation
if __name__ == "__main__":
    # Créer le système de chiffrement
    encryption_system = EncryptionSystem()
    
    # Générer une clé
    key_id = encryption_system.generate_key(
        name="test_key",
        algorithm=EncryptionAlgorithm.AES_256_GCM,
        security_level=SecurityLevel.HIGH
    )
    
    # Chiffrer des données
    test_data = "Données confidentielles à chiffrer"
    encrypted_result = encryption_system.encrypt_data(
        data=test_data,
        key_id=key_id,
        data_type="personal_data"
    )
    
    print(f"Données chiffrées avec la clé: {encrypted_result.key_id}")
    print(f"Algorithme: {encrypted_result.algorithm.value}")
    
    # Déchiffrer les données
    decrypted_data = encryption_system.decrypt_data(encrypted_result)
    decrypted_text = decrypted_data.decode('utf-8')
    
    print(f"Données déchiffrées: {decrypted_text}")
    print(f"Vérification: {test_data == decrypted_text}")
    
    # Afficher le tableau de bord
    dashboard = encryption_system.get_encryption_dashboard()
    print(f"\nTableau de bord chiffrement:")
    print(f"- Statistiques clés: {dashboard['key_statistics']}")
    print(f"- Clés expirant (30j): {dashboard['expiring_keys_30_days']}")
    print(f"- Politiques actives: {dashboard['active_policies']}")
    print(f"- Opérations chiffrement: {dashboard['performance_metrics']['encryption_operations']}")
    print(f"- Opérations déchiffrement: {dashboard['performance_metrics']['decryption_operations']}")

