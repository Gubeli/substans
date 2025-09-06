#!/usr/bin/env python3
"""
Enterprise Backup & Recovery System - Système de Sauvegarde et Récupération Enterprise
Système complet de sauvegarde avec RPO < 1h, tests automatiques et recovery point objective
"""

import os
import json
import sqlite3
import datetime
import threading
import time
import shutil
import zipfile
import hashlib
import subprocess
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
from pathlib import Path
import logging
import schedule
import boto3
from botocore.exceptions import ClientError
import paramiko
import ftplib
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from email.mime.base import MimeBase
from email import encoders
import psutil
import tarfile
import gzip

# Configuration logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BackupType(Enum):
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    SNAPSHOT = "snapshot"

class BackupStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class StorageType(Enum):
    LOCAL = "local"
    S3 = "s3"
    FTP = "ftp"
    SFTP = "sftp"
    NFS = "nfs"
    CLOUD = "cloud"

class CompressionType(Enum):
    NONE = "none"
    GZIP = "gzip"
    ZIP = "zip"
    TAR_GZ = "tar.gz"
    TAR_BZ2 = "tar.bz2"

class EncryptionType(Enum):
    NONE = "none"
    AES256 = "aes256"
    GPG = "gpg"

@dataclass
class BackupJob:
    """Job de sauvegarde"""
    id: str
    name: str
    description: str
    backup_type: BackupType
    source_paths: List[str]
    destination: str
    storage_type: StorageType
    compression: CompressionType
    encryption: EncryptionType
    schedule_cron: str
    retention_days: int
    enabled: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime
    last_run: Optional[datetime.datetime]
    next_run: Optional[datetime.datetime]
    success_count: int
    failure_count: int
    total_size_bytes: int
    config: Dict[str, Any]

@dataclass
class BackupExecution:
    """Exécution de sauvegarde"""
    id: str
    job_id: str
    backup_type: BackupType
    status: BackupStatus
    started_at: datetime.datetime
    completed_at: Optional[datetime.datetime]
    duration_seconds: Optional[int]
    size_bytes: int
    compressed_size_bytes: int
    files_count: int
    success_files: int
    failed_files: int
    backup_path: str
    checksum: str
    error_message: Optional[str]
    metadata: Dict[str, Any]

@dataclass
class RestoreJob:
    """Job de restauration"""
    id: str
    backup_execution_id: str
    restore_path: str
    status: BackupStatus
    started_at: datetime.datetime
    completed_at: Optional[datetime.datetime]
    files_restored: int
    files_failed: int
    requested_by: str
    metadata: Dict[str, Any]

class StorageManager:
    """Gestionnaire de stockage"""
    
    def __init__(self):
        self.storage_configs = {}
    
    def configure_storage(self, storage_type: StorageType, config: Dict[str, Any]):
        """Configure un type de stockage"""
        self.storage_configs[storage_type] = config
    
    def upload_file(self, local_path: str, remote_path: str, storage_type: StorageType) -> bool:
        """Upload un fichier vers le stockage"""
        try:
            if storage_type == StorageType.LOCAL:
                return self._upload_local(local_path, remote_path)
            elif storage_type == StorageType.S3:
                return self._upload_s3(local_path, remote_path)
            elif storage_type == StorageType.FTP:
                return self._upload_ftp(local_path, remote_path)
            elif storage_type == StorageType.SFTP:
                return self._upload_sftp(local_path, remote_path)
            else:
                logger.error(f"Type de stockage non supporté: {storage_type}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur upload {storage_type.value}: {e}")
            return False
    
    def download_file(self, remote_path: str, local_path: str, storage_type: StorageType) -> bool:
        """Télécharge un fichier depuis le stockage"""
        try:
            if storage_type == StorageType.LOCAL:
                return self._download_local(remote_path, local_path)
            elif storage_type == StorageType.S3:
                return self._download_s3(remote_path, local_path)
            elif storage_type == StorageType.FTP:
                return self._download_ftp(remote_path, local_path)
            elif storage_type == StorageType.SFTP:
                return self._download_sftp(remote_path, local_path)
            else:
                logger.error(f"Type de stockage non supporté: {storage_type}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur download {storage_type.value}: {e}")
            return False
    
    def _upload_local(self, local_path: str, remote_path: str) -> bool:
        """Upload local (copie de fichier)"""
        try:
            os.makedirs(os.path.dirname(remote_path), exist_ok=True)
            shutil.copy2(local_path, remote_path)
            return True
        except Exception as e:
            logger.error(f"Erreur copie locale: {e}")
            return False
    
    def _download_local(self, remote_path: str, local_path: str) -> bool:
        """Download local (copie de fichier)"""
        try:
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            shutil.copy2(remote_path, local_path)
            return True
        except Exception as e:
            logger.error(f"Erreur copie locale: {e}")
            return False
    
    def _upload_s3(self, local_path: str, remote_path: str) -> bool:
        """Upload vers S3"""
        try:
            config = self.storage_configs.get(StorageType.S3, {})
            s3_client = boto3.client(
                's3',
                aws_access_key_id=config.get('access_key'),
                aws_secret_access_key=config.get('secret_key'),
                region_name=config.get('region', 'us-east-1')
            )
            
            bucket = config.get('bucket')
            s3_client.upload_file(local_path, bucket, remote_path)
            return True
            
        except Exception as e:
            logger.error(f"Erreur upload S3: {e}")
            return False
    
    def _download_s3(self, remote_path: str, local_path: str) -> bool:
        """Download depuis S3"""
        try:
            config = self.storage_configs.get(StorageType.S3, {})
            s3_client = boto3.client(
                's3',
                aws_access_key_id=config.get('access_key'),
                aws_secret_access_key=config.get('secret_key'),
                region_name=config.get('region', 'us-east-1')
            )
            
            bucket = config.get('bucket')
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            s3_client.download_file(bucket, remote_path, local_path)
            return True
            
        except Exception as e:
            logger.error(f"Erreur download S3: {e}")
            return False
    
    def _upload_sftp(self, local_path: str, remote_path: str) -> bool:
        """Upload via SFTP"""
        try:
            config = self.storage_configs.get(StorageType.SFTP, {})
            
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                hostname=config.get('host'),
                port=config.get('port', 22),
                username=config.get('username'),
                password=config.get('password'),
                key_filename=config.get('key_file')
            )
            
            sftp = ssh.open_sftp()
            
            # Créer les dossiers distants si nécessaire
            remote_dir = os.path.dirname(remote_path)
            try:
                sftp.makedirs(remote_dir)
            except:
                pass
            
            sftp.put(local_path, remote_path)
            sftp.close()
            ssh.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur upload SFTP: {e}")
            return False
    
    def _download_sftp(self, remote_path: str, local_path: str) -> bool:
        """Download via SFTP"""
        try:
            config = self.storage_configs.get(StorageType.SFTP, {})
            
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                hostname=config.get('host'),
                port=config.get('port', 22),
                username=config.get('username'),
                password=config.get('password'),
                key_filename=config.get('key_file')
            )
            
            sftp = ssh.open_sftp()
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            sftp.get(remote_path, local_path)
            sftp.close()
            ssh.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur download SFTP: {e}")
            return False

class CompressionManager:
    """Gestionnaire de compression"""
    
    @staticmethod
    def compress_file(source_path: str, destination_path: str, compression_type: CompressionType) -> bool:
        """Compresse un fichier"""
        try:
            if compression_type == CompressionType.NONE:
                shutil.copy2(source_path, destination_path)
                return True
            elif compression_type == CompressionType.GZIP:
                with open(source_path, 'rb') as f_in:
                    with gzip.open(destination_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                return True
            elif compression_type == CompressionType.ZIP:
                with zipfile.ZipFile(destination_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    zipf.write(source_path, os.path.basename(source_path))
                return True
            elif compression_type == CompressionType.TAR_GZ:
                with tarfile.open(destination_path, 'w:gz') as tar:
                    tar.add(source_path, arcname=os.path.basename(source_path))
                return True
            else:
                logger.error(f"Type de compression non supporté: {compression_type}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur compression: {e}")
            return False
    
    @staticmethod
    def compress_directory(source_dir: str, destination_path: str, compression_type: CompressionType) -> bool:
        """Compresse un répertoire"""
        try:
            if compression_type == CompressionType.ZIP:
                with zipfile.ZipFile(destination_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk(source_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, source_dir)
                            zipf.write(file_path, arcname)
                return True
            elif compression_type == CompressionType.TAR_GZ:
                with tarfile.open(destination_path, 'w:gz') as tar:
                    tar.add(source_dir, arcname=os.path.basename(source_dir))
                return True
            else:
                logger.error(f"Compression répertoire non supportée: {compression_type}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur compression répertoire: {e}")
            return False
    
    @staticmethod
    def decompress_file(source_path: str, destination_path: str, compression_type: CompressionType) -> bool:
        """Décompresse un fichier"""
        try:
            if compression_type == CompressionType.NONE:
                shutil.copy2(source_path, destination_path)
                return True
            elif compression_type == CompressionType.GZIP:
                with gzip.open(source_path, 'rb') as f_in:
                    with open(destination_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                return True
            elif compression_type == CompressionType.ZIP:
                with zipfile.ZipFile(source_path, 'r') as zipf:
                    zipf.extractall(os.path.dirname(destination_path))
                return True
            elif compression_type == CompressionType.TAR_GZ:
                with tarfile.open(source_path, 'r:gz') as tar:
                    tar.extractall(os.path.dirname(destination_path))
                return True
            else:
                logger.error(f"Type de décompression non supporté: {compression_type}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur décompression: {e}")
            return False

class EnterpriseBackupRecovery:
    """Système de sauvegarde et récupération enterprise"""
    
    def __init__(self, base_path: str = "/home/ubuntu/substans_ai_megacabinet"):
        self.base_path = Path(base_path)
        self.db_path = self.base_path / "data" / "backup.db"
        self.backup_base_path = self.base_path / "backups"
        self.temp_path = self.base_path / "temp" / "backup"
        
        # Créer les répertoires
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.backup_base_path.mkdir(parents=True, exist_ok=True)
        self.temp_path.mkdir(parents=True, exist_ok=True)
        
        # Composants
        self.storage_manager = StorageManager()
        self.backup_jobs = {}
        self.running_executions = {}
        
        # Configuration
        self.max_concurrent_backups = 3
        self.rpo_hours = 1  # Recovery Point Objective
        self.rto_hours = 4  # Recovery Time Objective
        
        # Services
        self.running = False
        self.scheduler_thread = None
        self.monitor_thread = None
        
        self._init_database()
        self._init_default_jobs()
        self._configure_default_storage()
        self._start_services()
    
    def _init_database(self):
        """Initialise la base de données"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS backup_jobs (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    backup_type TEXT NOT NULL,
                    source_paths TEXT NOT NULL,
                    destination TEXT NOT NULL,
                    storage_type TEXT NOT NULL,
                    compression TEXT NOT NULL,
                    encryption TEXT NOT NULL,
                    schedule_cron TEXT NOT NULL,
                    retention_days INTEGER NOT NULL,
                    enabled BOOLEAN NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    last_run TIMESTAMP,
                    next_run TIMESTAMP,
                    success_count INTEGER DEFAULT 0,
                    failure_count INTEGER DEFAULT 0,
                    total_size_bytes INTEGER DEFAULT 0,
                    config TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS backup_executions (
                    id TEXT PRIMARY KEY,
                    job_id TEXT NOT NULL,
                    backup_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    started_at TIMESTAMP NOT NULL,
                    completed_at TIMESTAMP,
                    duration_seconds INTEGER,
                    size_bytes INTEGER DEFAULT 0,
                    compressed_size_bytes INTEGER DEFAULT 0,
                    files_count INTEGER DEFAULT 0,
                    success_files INTEGER DEFAULT 0,
                    failed_files INTEGER DEFAULT 0,
                    backup_path TEXT NOT NULL,
                    checksum TEXT,
                    error_message TEXT,
                    metadata TEXT,
                    FOREIGN KEY (job_id) REFERENCES backup_jobs (id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS restore_jobs (
                    id TEXT PRIMARY KEY,
                    backup_execution_id TEXT NOT NULL,
                    restore_path TEXT NOT NULL,
                    status TEXT NOT NULL,
                    started_at TIMESTAMP NOT NULL,
                    completed_at TIMESTAMP,
                    files_restored INTEGER DEFAULT 0,
                    files_failed INTEGER DEFAULT 0,
                    requested_by TEXT NOT NULL,
                    metadata TEXT,
                    FOREIGN KEY (backup_execution_id) REFERENCES backup_executions (id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS backup_verification (
                    id TEXT PRIMARY KEY,
                    execution_id TEXT NOT NULL,
                    verification_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    started_at TIMESTAMP NOT NULL,
                    completed_at TIMESTAMP,
                    files_verified INTEGER DEFAULT 0,
                    files_corrupted INTEGER DEFAULT 0,
                    checksum_matches BOOLEAN,
                    error_message TEXT,
                    FOREIGN KEY (execution_id) REFERENCES backup_executions (id)
                )
            """)
            
            # Index pour les performances
            conn.execute("CREATE INDEX IF NOT EXISTS idx_executions_job_status ON backup_executions(job_id, status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_executions_started ON backup_executions(started_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_next_run ON backup_jobs(next_run)")
            
            conn.commit()
    
    def _init_default_jobs(self):
        """Initialise les jobs de sauvegarde par défaut"""
        default_jobs = [
            {
                "name": "Sauvegarde Système Critique",
                "description": "Sauvegarde des fichiers système critiques",
                "backup_type": BackupType.FULL,
                "source_paths": [
                    str(self.base_path / "data"),
                    str(self.base_path / "agents_consultants"),
                    str(self.base_path / "experts_metiers"),
                    str(self.base_path / "experts_domaines")
                ],
                "storage_type": StorageType.LOCAL,
                "compression": CompressionType.TAR_GZ,
                "encryption": EncryptionType.NONE,
                "schedule_cron": "0 */2 * * *",  # Toutes les 2 heures
                "retention_days": 30
            },
            {
                "name": "Sauvegarde Base de Données",
                "description": "Sauvegarde des bases de données SQLite",
                "backup_type": BackupType.INCREMENTAL,
                "source_paths": [
                    str(self.base_path / "data" / "*.db")
                ],
                "storage_type": StorageType.LOCAL,
                "compression": CompressionType.GZIP,
                "encryption": EncryptionType.NONE,
                "schedule_cron": "0 * * * *",  # Toutes les heures
                "retention_days": 7
            },
            {
                "name": "Sauvegarde Configuration",
                "description": "Sauvegarde des fichiers de configuration",
                "backup_type": BackupType.DIFFERENTIAL,
                "source_paths": [
                    str(self.base_path / "*.json"),
                    str(self.base_path / "*.py"),
                    str(self.base_path / "interface-chef-substans")
                ],
                "storage_type": StorageType.LOCAL,
                "compression": CompressionType.ZIP,
                "encryption": EncryptionType.NONE,
                "schedule_cron": "0 6 * * *",  # Tous les jours à 6h
                "retention_days": 90
            },
            {
                "name": "Sauvegarde Missions",
                "description": "Sauvegarde des données de missions",
                "backup_type": BackupType.INCREMENTAL,
                "source_paths": [
                    str(self.base_path / "missions")
                ],
                "storage_type": StorageType.LOCAL,
                "compression": CompressionType.TAR_GZ,
                "encryption": EncryptionType.NONE,
                "schedule_cron": "0 */4 * * *",  # Toutes les 4 heures
                "retention_days": 60
            }
        ]
        
        for job_data in default_jobs:
            job = BackupJob(
                id=str(uuid.uuid4()),
                name=job_data["name"],
                description=job_data["description"],
                backup_type=job_data["backup_type"],
                source_paths=job_data["source_paths"],
                destination=str(self.backup_base_path / job_data["name"].lower().replace(" ", "_")),
                storage_type=job_data["storage_type"],
                compression=job_data["compression"],
                encryption=job_data["encryption"],
                schedule_cron=job_data["schedule_cron"],
                retention_days=job_data["retention_days"],
                enabled=True,
                created_at=datetime.datetime.now(),
                updated_at=datetime.datetime.now(),
                last_run=None,
                next_run=self._calculate_next_run(job_data["schedule_cron"]),
                success_count=0,
                failure_count=0,
                total_size_bytes=0,
                config={}
            )
            self.backup_jobs[job.id] = job
    
    def _configure_default_storage(self):
        """Configure les types de stockage par défaut"""
        # Configuration locale
        self.storage_manager.configure_storage(StorageType.LOCAL, {
            "base_path": str(self.backup_base_path)
        })
        
        # Configuration S3 (exemple)
        self.storage_manager.configure_storage(StorageType.S3, {
            "access_key": "YOUR_ACCESS_KEY",
            "secret_key": "YOUR_SECRET_KEY",
            "bucket": "substans-ai-backups",
            "region": "eu-west-1"
        })
        
        # Configuration SFTP (exemple)
        self.storage_manager.configure_storage(StorageType.SFTP, {
            "host": "backup.substans.ai",
            "port": 22,
            "username": "backup_user",
            "password": "backup_password"
        })
    
    def _start_services(self):
        """Démarre les services d'arrière-plan"""
        if self.running:
            return
        
        self.running = True
        
        # Thread de planification
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        # Thread de monitoring
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        logger.info("🚀 Services de sauvegarde démarrés")
    
    def stop_services(self):
        """Arrête les services"""
        self.running = False
        logger.info("🛑 Services de sauvegarde arrêtés")
    
    def _scheduler_loop(self):
        """Boucle de planification des sauvegardes"""
        while self.running:
            try:
                current_time = datetime.datetime.now()
                
                for job in self.backup_jobs.values():
                    if not job.enabled:
                        continue
                    
                    if job.next_run and current_time >= job.next_run:
                        # Vérifier si on peut lancer la sauvegarde
                        if len(self.running_executions) < self.max_concurrent_backups:
                            self._start_backup_execution(job)
                        else:
                            logger.warning(f"⏳ Sauvegarde {job.name} reportée - trop d'exécutions en cours")
                
            except Exception as e:
                logger.error(f"Erreur planificateur: {e}")
            
            time.sleep(60)  # Vérifier chaque minute
    
    def _monitor_loop(self):
        """Boucle de monitoring des sauvegardes"""
        while self.running:
            try:
                # Vérifier les exécutions en cours
                self._check_running_executions()
                
                # Nettoyer les anciennes sauvegardes
                self._cleanup_old_backups()
                
                # Vérifier l'intégrité des sauvegardes
                self._verify_backup_integrity()
                
                # Tester les procédures de restauration
                self._test_restore_procedures()
                
            except Exception as e:
                logger.error(f"Erreur monitoring: {e}")
            
            time.sleep(300)  # Vérifier toutes les 5 minutes
    
    def _start_backup_execution(self, job: BackupJob):
        """Démarre l'exécution d'une sauvegarde"""
        execution_id = str(uuid.uuid4())
        
        execution = BackupExecution(
            id=execution_id,
            job_id=job.id,
            backup_type=job.backup_type,
            status=BackupStatus.RUNNING,
            started_at=datetime.datetime.now(),
            completed_at=None,
            duration_seconds=None,
            size_bytes=0,
            compressed_size_bytes=0,
            files_count=0,
            success_files=0,
            failed_files=0,
            backup_path="",
            checksum="",
            error_message=None,
            metadata={}
        )
        
        # Ajouter aux exécutions en cours
        self.running_executions[execution_id] = execution
        
        # Mettre à jour le job
        job.last_run = datetime.datetime.now()
        job.next_run = self._calculate_next_run(job.schedule_cron)
        
        # Lancer l'exécution dans un thread séparé
        thread = threading.Thread(
            target=self._execute_backup,
            args=(job, execution),
            daemon=True
        )
        thread.start()
        
        logger.info(f"🚀 Démarrage sauvegarde: {job.name}")
    
    def _execute_backup(self, job: BackupJob, execution: BackupExecution):
        """Exécute une sauvegarde"""
        try:
            # Créer le répertoire de destination
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{job.name.lower().replace(' ', '_')}_{timestamp}"
            backup_dir = self.backup_base_path / backup_name
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            execution.backup_path = str(backup_dir)
            
            # Collecter les fichiers à sauvegarder
            files_to_backup = []
            for source_path in job.source_paths:
                if "*" in source_path:
                    # Gérer les wildcards
                    import glob
                    files_to_backup.extend(glob.glob(source_path, recursive=True))
                else:
                    if os.path.exists(source_path):
                        if os.path.isfile(source_path):
                            files_to_backup.append(source_path)
                        elif os.path.isdir(source_path):
                            for root, dirs, files in os.walk(source_path):
                                for file in files:
                                    files_to_backup.append(os.path.join(root, file))
            
            execution.files_count = len(files_to_backup)
            
            # Sauvegarder les fichiers
            total_size = 0
            success_count = 0
            failed_count = 0
            
            for file_path in files_to_backup:
                try:
                    # Calculer le chemin relatif
                    rel_path = os.path.relpath(file_path, self.base_path)
                    dest_path = backup_dir / rel_path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copier le fichier
                    shutil.copy2(file_path, dest_path)
                    
                    # Calculer la taille
                    file_size = os.path.getsize(file_path)
                    total_size += file_size
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"Erreur sauvegarde fichier {file_path}: {e}")
                    failed_count += 1
            
            execution.size_bytes = total_size
            execution.success_files = success_count
            execution.failed_files = failed_count
            
            # Compression si nécessaire
            if job.compression != CompressionType.NONE:
                compressed_path = f"{backup_dir}.{job.compression.value}"
                if CompressionManager.compress_directory(str(backup_dir), compressed_path, job.compression):
                    # Supprimer le répertoire non compressé
                    shutil.rmtree(backup_dir)
                    execution.backup_path = compressed_path
                    execution.compressed_size_bytes = os.path.getsize(compressed_path)
                else:
                    execution.compressed_size_bytes = total_size
            else:
                execution.compressed_size_bytes = total_size
            
            # Calculer le checksum
            execution.checksum = self._calculate_checksum(execution.backup_path)
            
            # Upload vers le stockage distant si nécessaire
            if job.storage_type != StorageType.LOCAL:
                remote_path = f"substans_ai_backups/{backup_name}"
                if self.storage_manager.upload_file(execution.backup_path, remote_path, job.storage_type):
                    execution.metadata["remote_path"] = remote_path
                else:
                    raise Exception("Échec upload vers stockage distant")
            
            # Marquer comme terminé
            execution.status = BackupStatus.COMPLETED
            execution.completed_at = datetime.datetime.now()
            execution.duration_seconds = int((execution.completed_at - execution.started_at).total_seconds())
            
            # Mettre à jour les statistiques du job
            job.success_count += 1
            job.total_size_bytes += execution.compressed_size_bytes
            
            logger.info(f"✅ Sauvegarde terminée: {job.name} ({execution.compressed_size_bytes / 1024 / 1024:.1f} MB)")
            
        except Exception as e:
            execution.status = BackupStatus.FAILED
            execution.error_message = str(e)
            execution.completed_at = datetime.datetime.now()
            execution.duration_seconds = int((execution.completed_at - execution.started_at).total_seconds())
            
            job.failure_count += 1
            
            logger.error(f"❌ Échec sauvegarde {job.name}: {e}")
        
        finally:
            # Sauvegarder l'exécution en base
            self._save_execution(execution)
            
            # Retirer des exécutions en cours
            if execution.id in self.running_executions:
                del self.running_executions[execution.id]
    
    def _calculate_checksum(self, file_path: str) -> str:
        """Calcule le checksum d'un fichier"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"Erreur calcul checksum: {e}")
            return ""
    
    def _save_execution(self, execution: BackupExecution):
        """Sauvegarde une exécution en base"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO backup_executions
                    (id, job_id, backup_type, status, started_at, completed_at, duration_seconds,
                     size_bytes, compressed_size_bytes, files_count, success_files, failed_files,
                     backup_path, checksum, error_message, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    execution.id, execution.job_id, execution.backup_type.value,
                    execution.status.value, execution.started_at.isoformat(),
                    execution.completed_at.isoformat() if execution.completed_at else None,
                    execution.duration_seconds, execution.size_bytes, execution.compressed_size_bytes,
                    execution.files_count, execution.success_files, execution.failed_files,
                    execution.backup_path, execution.checksum, execution.error_message,
                    json.dumps(execution.metadata)
                ))
        except Exception as e:
            logger.error(f"Erreur sauvegarde exécution: {e}")
    
    def _calculate_next_run(self, cron_expression: str) -> datetime.datetime:
        """Calcule la prochaine exécution basée sur l'expression cron"""
        # Implémentation simplifiée - en production, utiliser croniter
        try:
            # Parser basique pour quelques patterns courants
            parts = cron_expression.split()
            if len(parts) != 5:
                return datetime.datetime.now() + datetime.timedelta(hours=1)
            
            minute, hour, day, month, weekday = parts
            
            now = datetime.datetime.now()
            next_run = now.replace(second=0, microsecond=0)
            
            # Si c'est */X, calculer l'intervalle
            if hour.startswith("*/"):
                interval = int(hour[2:])
                next_run = next_run + datetime.timedelta(hours=interval)
            elif hour.isdigit():
                target_hour = int(hour)
                if now.hour >= target_hour:
                    next_run = next_run.replace(hour=target_hour) + datetime.timedelta(days=1)
                else:
                    next_run = next_run.replace(hour=target_hour)
            
            return next_run
            
        except Exception as e:
            logger.error(f"Erreur calcul prochaine exécution: {e}")
            return datetime.datetime.now() + datetime.timedelta(hours=1)
    
    def _check_running_executions(self):
        """Vérifie les exécutions en cours"""
        for execution_id, execution in list(self.running_executions.items()):
            # Vérifier si l'exécution est bloquée (plus de 2 heures)
            if execution.started_at < datetime.datetime.now() - datetime.timedelta(hours=2):
                logger.warning(f"⚠️ Exécution bloquée détectée: {execution_id}")
                execution.status = BackupStatus.FAILED
                execution.error_message = "Timeout - exécution bloquée"
                execution.completed_at = datetime.datetime.now()
                self._save_execution(execution)
                del self.running_executions[execution_id]
    
    def _cleanup_old_backups(self):
        """Nettoie les anciennes sauvegardes"""
        try:
            for job in self.backup_jobs.values():
                cutoff_date = datetime.datetime.now() - datetime.timedelta(days=job.retention_days)
                
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute("""
                        SELECT id, backup_path FROM backup_executions
                        WHERE job_id = ? AND started_at < ? AND status = 'completed'
                    """, (job.id, cutoff_date.isoformat()))
                    
                    for row in cursor.fetchall():
                        execution_id, backup_path = row
                        
                        # Supprimer le fichier de sauvegarde
                        if os.path.exists(backup_path):
                            if os.path.isfile(backup_path):
                                os.remove(backup_path)
                            elif os.path.isdir(backup_path):
                                shutil.rmtree(backup_path)
                        
                        # Supprimer l'enregistrement
                        conn.execute("DELETE FROM backup_executions WHERE id = ?", (execution_id,))
                    
                    conn.commit()
                    
        except Exception as e:
            logger.error(f"Erreur nettoyage sauvegardes: {e}")
    
    def _verify_backup_integrity(self):
        """Vérifie l'intégrité des sauvegardes"""
        try:
            # Vérifier les sauvegardes récentes (dernières 24h)
            cutoff_date = datetime.datetime.now() - datetime.timedelta(hours=24)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT id, backup_path, checksum FROM backup_executions
                    WHERE started_at >= ? AND status = 'completed' AND checksum IS NOT NULL
                """, (cutoff_date.isoformat(),))
                
                for row in cursor.fetchall():
                    execution_id, backup_path, stored_checksum = row
                    
                    if os.path.exists(backup_path):
                        current_checksum = self._calculate_checksum(backup_path)
                        
                        if current_checksum != stored_checksum:
                            logger.error(f"🔴 Corruption détectée: {backup_path}")
                            # Enregistrer la vérification
                            self._save_verification_result(execution_id, "checksum", False, "Checksum mismatch")
                        else:
                            self._save_verification_result(execution_id, "checksum", True, "OK")
                    else:
                        logger.error(f"🔴 Fichier sauvegarde manquant: {backup_path}")
                        self._save_verification_result(execution_id, "existence", False, "File missing")
                        
        except Exception as e:
            logger.error(f"Erreur vérification intégrité: {e}")
    
    def _save_verification_result(self, execution_id: str, verification_type: str, 
                                success: bool, message: str):
        """Sauvegarde un résultat de vérification"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO backup_verification
                    (id, execution_id, verification_type, status, started_at, completed_at,
                     checksum_matches, error_message)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(uuid.uuid4()),
                    execution_id,
                    verification_type,
                    "completed",
                    datetime.datetime.now().isoformat(),
                    datetime.datetime.now().isoformat(),
                    success,
                    message if not success else None
                ))
        except Exception as e:
            logger.error(f"Erreur sauvegarde vérification: {e}")
    
    def _test_restore_procedures(self):
        """Teste les procédures de restauration"""
        # Test de restauration automatique une fois par semaine
        last_test_file = self.base_path / "data" / "last_restore_test.txt"
        
        try:
            if last_test_file.exists():
                with open(last_test_file, 'r') as f:
                    last_test_str = f.read().strip()
                    last_test = datetime.datetime.fromisoformat(last_test_str)
                    
                    # Tester seulement si le dernier test date de plus d'une semaine
                    if datetime.datetime.now() - last_test < datetime.timedelta(days=7):
                        return
            
            # Sélectionner une sauvegarde récente pour le test
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT id, backup_path FROM backup_executions
                    WHERE status = 'completed' AND backup_path IS NOT NULL
                    ORDER BY started_at DESC LIMIT 1
                """)
                
                row = cursor.fetchone()
                if row:
                    execution_id, backup_path = row
                    
                    # Créer un répertoire de test
                    test_restore_dir = self.temp_path / f"restore_test_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    test_restore_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Tenter la restauration
                    success = self._perform_restore_test(backup_path, str(test_restore_dir))
                    
                    # Nettoyer le répertoire de test
                    shutil.rmtree(test_restore_dir, ignore_errors=True)
                    
                    if success:
                        logger.info("✅ Test de restauration réussi")
                    else:
                        logger.error("❌ Échec du test de restauration")
                    
                    # Enregistrer la date du test
                    with open(last_test_file, 'w') as f:
                        f.write(datetime.datetime.now().isoformat())
                        
        except Exception as e:
            logger.error(f"Erreur test restauration: {e}")
    
    def _perform_restore_test(self, backup_path: str, restore_dir: str) -> bool:
        """Effectue un test de restauration"""
        try:
            # Déterminer le type de compression
            if backup_path.endswith('.tar.gz'):
                compression = CompressionType.TAR_GZ
            elif backup_path.endswith('.zip'):
                compression = CompressionType.ZIP
            elif backup_path.endswith('.gz'):
                compression = CompressionType.GZIP
            else:
                compression = CompressionType.NONE
            
            # Décompresser
            return CompressionManager.decompress_file(backup_path, restore_dir, compression)
            
        except Exception as e:
            logger.error(f"Erreur test restauration: {e}")
            return False
    
    def create_backup_job(self, name: str, description: str, source_paths: List[str],
                         backup_type: BackupType = BackupType.INCREMENTAL,
                         storage_type: StorageType = StorageType.LOCAL,
                         compression: CompressionType = CompressionType.TAR_GZ,
                         schedule_cron: str = "0 2 * * *",
                         retention_days: int = 30) -> str:
        """Crée un nouveau job de sauvegarde"""
        job_id = str(uuid.uuid4())
        
        job = BackupJob(
            id=job_id,
            name=name,
            description=description,
            backup_type=backup_type,
            source_paths=source_paths,
            destination=str(self.backup_base_path / name.lower().replace(" ", "_")),
            storage_type=storage_type,
            compression=compression,
            encryption=EncryptionType.NONE,
            schedule_cron=schedule_cron,
            retention_days=retention_days,
            enabled=True,
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
            last_run=None,
            next_run=self._calculate_next_run(schedule_cron),
            success_count=0,
            failure_count=0,
            total_size_bytes=0,
            config={}
        )
        
        self.backup_jobs[job_id] = job
        logger.info(f"✅ Job de sauvegarde créé: {name}")
        return job_id
    
    def start_manual_backup(self, job_id: str) -> str:
        """Démarre une sauvegarde manuelle"""
        if job_id not in self.backup_jobs:
            raise ValueError(f"Job non trouvé: {job_id}")
        
        job = self.backup_jobs[job_id]
        
        if len(self.running_executions) >= self.max_concurrent_backups:
            raise RuntimeError("Trop de sauvegardes en cours")
        
        self._start_backup_execution(job)
        return f"Sauvegarde démarrée: {job.name}"
    
    def restore_backup(self, execution_id: str, restore_path: str, requested_by: str = "system") -> str:
        """Restaure une sauvegarde"""
        try:
            # Récupérer l'exécution de sauvegarde
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT backup_path, compression FROM backup_executions e
                    JOIN backup_jobs j ON e.job_id = j.id
                    WHERE e.id = ? AND e.status = 'completed'
                """, (execution_id,))
                
                row = cursor.fetchone()
                if not row:
                    raise ValueError("Sauvegarde non trouvée ou incomplète")
                
                backup_path, compression_str = row
                compression = CompressionType(compression_str)
            
            # Créer le job de restauration
            restore_id = str(uuid.uuid4())
            restore_job = RestoreJob(
                id=restore_id,
                backup_execution_id=execution_id,
                restore_path=restore_path,
                status=BackupStatus.RUNNING,
                started_at=datetime.datetime.now(),
                completed_at=None,
                files_restored=0,
                files_failed=0,
                requested_by=requested_by,
                metadata={}
            )
            
            # Effectuer la restauration
            os.makedirs(restore_path, exist_ok=True)
            
            if CompressionManager.decompress_file(backup_path, restore_path, compression):
                restore_job.status = BackupStatus.COMPLETED
                restore_job.completed_at = datetime.datetime.now()
                logger.info(f"✅ Restauration terminée: {restore_path}")
            else:
                restore_job.status = BackupStatus.FAILED
                restore_job.completed_at = datetime.datetime.now()
                logger.error(f"❌ Échec restauration: {restore_path}")
            
            # Sauvegarder le job de restauration
            self._save_restore_job(restore_job)
            
            return restore_id
            
        except Exception as e:
            logger.error(f"Erreur restauration: {e}")
            raise
    
    def _save_restore_job(self, restore_job: RestoreJob):
        """Sauvegarde un job de restauration"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO restore_jobs
                    (id, backup_execution_id, restore_path, status, started_at, completed_at,
                     files_restored, files_failed, requested_by, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    restore_job.id, restore_job.backup_execution_id, restore_job.restore_path,
                    restore_job.status.value, restore_job.started_at.isoformat(),
                    restore_job.completed_at.isoformat() if restore_job.completed_at else None,
                    restore_job.files_restored, restore_job.files_failed,
                    restore_job.requested_by, json.dumps(restore_job.metadata)
                ))
        except Exception as e:
            logger.error(f"Erreur sauvegarde job restauration: {e}")
    
    def get_backup_status(self) -> Dict[str, Any]:
        """Récupère le statut des sauvegardes"""
        try:
            # Statistiques générales
            total_jobs = len(self.backup_jobs)
            enabled_jobs = sum(1 for job in self.backup_jobs.values() if job.enabled)
            running_backups = len(self.running_executions)
            
            # Statistiques des exécutions (dernières 24h)
            cutoff_date = datetime.datetime.now() - datetime.timedelta(hours=24)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT status, COUNT(*) FROM backup_executions
                    WHERE started_at >= ?
                    GROUP BY status
                """, (cutoff_date.isoformat(),))
                
                status_stats = dict(cursor.fetchall())
                
                # Taille totale des sauvegardes
                cursor = conn.execute("SELECT SUM(compressed_size_bytes) FROM backup_executions WHERE status = 'completed'")
                total_size = cursor.fetchone()[0] or 0
                
                # Prochaines exécutions
                next_runs = []
                for job in self.backup_jobs.values():
                    if job.enabled and job.next_run:
                        next_runs.append({
                            'job_name': job.name,
                            'next_run': job.next_run.isoformat(),
                            'backup_type': job.backup_type.value
                        })
                
                next_runs.sort(key=lambda x: x['next_run'])
            
            # Vérifier le RPO
            rpo_status = self._check_rpo_compliance()
            
            return {
                'total_jobs': total_jobs,
                'enabled_jobs': enabled_jobs,
                'running_backups': running_backups,
                'status_stats_24h': status_stats,
                'total_backup_size_gb': round(total_size / (1024**3), 2),
                'next_runs': next_runs[:5],  # 5 prochaines
                'rpo_compliance': rpo_status,
                'rpo_hours': self.rpo_hours,
                'rto_hours': self.rto_hours,
                'system_status': 'running' if self.running else 'stopped',
                'last_updated': datetime.datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur statut sauvegardes: {e}")
            return {}
    
    def _check_rpo_compliance(self) -> bool:
        """Vérifie la conformité RPO"""
        try:
            rpo_cutoff = datetime.datetime.now() - datetime.timedelta(hours=self.rpo_hours)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM backup_executions
                    WHERE started_at >= ? AND status = 'completed'
                """, (rpo_cutoff.isoformat(),))
                
                recent_backups = cursor.fetchone()[0]
                return recent_backups > 0
                
        except Exception as e:
            logger.error(f"Erreur vérification RPO: {e}")
            return False

# Instance globale
enterprise_backup = EnterpriseBackupRecovery()

if __name__ == "__main__":
    # Test du système de sauvegarde
    backup_system = EnterpriseBackupRecovery()
    
    # Créer un job de test
    job_id = backup_system.create_backup_job(
        name="Test Backup",
        description="Test de sauvegarde",
        source_paths=["/home/ubuntu/substans_ai_megacabinet/data"],
        schedule_cron="0 */6 * * *"
    )
    
    # Démarrer une sauvegarde manuelle
    try:
        result = backup_system.start_manual_backup(job_id)
        print(f"✅ {result}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # Attendre un peu
    time.sleep(5)
    
    # Récupérer le statut
    status = backup_system.get_backup_status()
    print(f"📊 Jobs totaux: {status['total_jobs']}")
    print(f"🏃 Sauvegardes en cours: {status['running_backups']}")
    
    # Arrêter les services
    backup_system.stop_services()

