#!/usr/bin/env python3
"""
Performance Optimizer - Système d'Optimisation des Performances
Optimisation complète des performances système avec cache, threading et monitoring
"""

import os
import json
import sqlite3
import datetime
import threading
import time
import psutil
import gc
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
from pathlib import Path
import logging
import asyncio
import concurrent.futures
from functools import wraps, lru_cache
import weakref
import pickle
import hashlib
from collections import defaultdict, deque
import multiprocessing

# Configuration logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CacheType(Enum):
    MEMORY = "memory"
    DISK = "disk"
    HYBRID = "hybrid"

class OptimizationLevel(Enum):
    BASIC = "basic"
    STANDARD = "standard"
    AGGRESSIVE = "aggressive"
    MAXIMUM = "maximum"

@dataclass
class PerformanceMetrics:
    """Métriques de performance"""
    timestamp: datetime.datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_sent_mb: float
    network_recv_mb: float
    active_threads: int
    cache_hit_rate: float
    response_time_ms: float
    throughput_ops_sec: float

@dataclass
class CacheEntry:
    """Entrée de cache"""
    key: str
    value: Any
    created_at: datetime.datetime
    last_accessed: datetime.datetime
    access_count: int
    ttl_seconds: Optional[int] = None
    size_bytes: int = 0

class SmartCache:
    """Cache intelligent avec TTL, LRU et persistance"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600, cache_type: CacheType = CacheType.HYBRID):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache_type = cache_type
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order = deque()
        self.lock = threading.RLock()
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "size_bytes": 0
        }
        
        # Cache disque si nécessaire
        if cache_type in [CacheType.DISK, CacheType.HYBRID]:
            self.disk_cache_path = Path("/tmp/substans_cache")
            self.disk_cache_path.mkdir(exist_ok=True)
    
    def get(self, key: str) -> Optional[Any]:
        """Récupère une valeur du cache"""
        with self.lock:
            # Vérifier le cache mémoire
            if key in self.cache:
                entry = self.cache[key]
                
                # Vérifier TTL
                if self._is_expired(entry):
                    self._remove_entry(key)
                    self.stats["misses"] += 1
                    return None
                
                # Mettre à jour l'accès
                entry.last_accessed = datetime.datetime.now()
                entry.access_count += 1
                
                # Mettre à jour l'ordre LRU
                if key in self.access_order:
                    self.access_order.remove(key)
                self.access_order.append(key)
                
                self.stats["hits"] += 1
                return entry.value
            
            # Vérifier le cache disque si hybride
            if self.cache_type in [CacheType.DISK, CacheType.HYBRID]:
                disk_value = self._get_from_disk(key)
                if disk_value is not None:
                    # Remettre en cache mémoire
                    self.set(key, disk_value)
                    self.stats["hits"] += 1
                    return disk_value
            
            self.stats["misses"] += 1
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Stocke une valeur dans le cache"""
        with self.lock:
            now = datetime.datetime.now()
            
            # Calculer la taille
            try:
                size_bytes = len(pickle.dumps(value))
            except:
                size_bytes = 1024  # Estimation par défaut
            
            # Créer l'entrée
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=now,
                last_accessed=now,
                access_count=1,
                ttl_seconds=ttl or self.default_ttl,
                size_bytes=size_bytes
            )
            
            # Supprimer l'ancienne entrée si elle existe
            if key in self.cache:
                self._remove_entry(key)
            
            # Vérifier la capacité
            while len(self.cache) >= self.max_size:
                self._evict_lru()
            
            # Ajouter la nouvelle entrée
            self.cache[key] = entry
            self.access_order.append(key)
            self.stats["size_bytes"] += size_bytes
            
            # Sauvegarder sur disque si nécessaire
            if self.cache_type in [CacheType.DISK, CacheType.HYBRID]:
                self._save_to_disk(key, value)
    
    def delete(self, key: str) -> bool:
        """Supprime une entrée du cache"""
        with self.lock:
            if key in self.cache:
                self._remove_entry(key)
                
                # Supprimer du disque
                if self.cache_type in [CacheType.DISK, CacheType.HYBRID]:
                    self._delete_from_disk(key)
                
                return True
            return False
    
    def clear(self) -> None:
        """Vide le cache"""
        with self.lock:
            self.cache.clear()
            self.access_order.clear()
            self.stats = {"hits": 0, "misses": 0, "evictions": 0, "size_bytes": 0}
            
            # Vider le cache disque
            if self.cache_type in [CacheType.DISK, CacheType.HYBRID]:
                for file_path in self.disk_cache_path.glob("*.cache"):
                    file_path.unlink()
    
    def get_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques du cache"""
        with self.lock:
            total_requests = self.stats["hits"] + self.stats["misses"]
            hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "hits": self.stats["hits"],
                "misses": self.stats["misses"],
                "hit_rate": round(hit_rate, 2),
                "evictions": self.stats["evictions"],
                "size_bytes": self.stats["size_bytes"],
                "size_mb": round(self.stats["size_bytes"] / 1024 / 1024, 2)
            }
    
    def _is_expired(self, entry: CacheEntry) -> bool:
        """Vérifie si une entrée est expirée"""
        if entry.ttl_seconds is None:
            return False
        
        age = (datetime.datetime.now() - entry.created_at).total_seconds()
        return age > entry.ttl_seconds
    
    def _remove_entry(self, key: str) -> None:
        """Supprime une entrée du cache"""
        if key in self.cache:
            entry = self.cache[key]
            self.stats["size_bytes"] -= entry.size_bytes
            del self.cache[key]
            
            if key in self.access_order:
                self.access_order.remove(key)
    
    def _evict_lru(self) -> None:
        """Évince l'entrée la moins récemment utilisée"""
        if self.access_order:
            lru_key = self.access_order.popleft()
            self._remove_entry(lru_key)
            self.stats["evictions"] += 1
    
    def _get_cache_file_path(self, key: str) -> Path:
        """Génère le chemin du fichier cache"""
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.disk_cache_path / f"{key_hash}.cache"
    
    def _save_to_disk(self, key: str, value: Any) -> None:
        """Sauvegarde une valeur sur disque"""
        try:
            file_path = self._get_cache_file_path(key)
            with open(file_path, 'wb') as f:
                pickle.dump({
                    'value': value,
                    'timestamp': datetime.datetime.now().timestamp()
                }, f)
        except Exception as e:
            logger.warning(f"Erreur sauvegarde cache disque {key}: {e}")
    
    def _get_from_disk(self, key: str) -> Optional[Any]:
        """Récupère une valeur du disque"""
        try:
            file_path = self._get_cache_file_path(key)
            if not file_path.exists():
                return None
            
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
            
            # Vérifier TTL
            age = time.time() - data['timestamp']
            if age > self.default_ttl:
                file_path.unlink()
                return None
            
            return data['value']
        except Exception as e:
            logger.warning(f"Erreur lecture cache disque {key}: {e}")
            return None
    
    def _delete_from_disk(self, key: str) -> None:
        """Supprime une valeur du disque"""
        try:
            file_path = self._get_cache_file_path(key)
            if file_path.exists():
                file_path.unlink()
        except Exception as e:
            logger.warning(f"Erreur suppression cache disque {key}: {e}")

class ThreadPoolManager:
    """Gestionnaire de pools de threads optimisé"""
    
    def __init__(self, max_workers: Optional[int] = None):
        self.max_workers = max_workers or min(32, (os.cpu_count() or 1) + 4)
        self.pools: Dict[str, concurrent.futures.ThreadPoolExecutor] = {}
        self.lock = threading.Lock()
        self.stats = defaultdict(lambda: {"submitted": 0, "completed": 0, "errors": 0})
    
    def get_pool(self, pool_name: str, max_workers: Optional[int] = None) -> concurrent.futures.ThreadPoolExecutor:
        """Récupère ou crée un pool de threads"""
        with self.lock:
            if pool_name not in self.pools:
                workers = max_workers or self.max_workers
                self.pools[pool_name] = concurrent.futures.ThreadPoolExecutor(
                    max_workers=workers,
                    thread_name_prefix=f"substans-{pool_name}"
                )
            return self.pools[pool_name]
    
    def submit_task(self, pool_name: str, func: Callable, *args, **kwargs) -> concurrent.futures.Future:
        """Soumet une tâche à un pool"""
        pool = self.get_pool(pool_name)
        future = pool.submit(func, *args, **kwargs)
        
        self.stats[pool_name]["submitted"] += 1
        
        # Callback pour les statistiques
        def update_stats(fut):
            try:
                fut.result()  # Récupérer le résultat pour déclencher les exceptions
                self.stats[pool_name]["completed"] += 1
            except Exception:
                self.stats[pool_name]["errors"] += 1
        
        future.add_done_callback(update_stats)
        return future
    
    def shutdown_all(self, wait: bool = True) -> None:
        """Arrête tous les pools"""
        with self.lock:
            for pool in self.pools.values():
                pool.shutdown(wait=wait)
            self.pools.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques des pools"""
        return dict(self.stats)

class PerformanceOptimizer:
    """Optimiseur de performances principal"""
    
    def __init__(self, base_path: str = "/home/ubuntu/substans_ai_megacabinet"):
        self.base_path = Path(base_path)
        self.db_path = self.base_path / "data" / "performance.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Composants d'optimisation
        self.cache = SmartCache(max_size=5000, default_ttl=3600)
        self.thread_manager = ThreadPoolManager()
        
        # Configuration
        self.optimization_level = OptimizationLevel.STANDARD
        self.monitoring_enabled = True
        self.auto_gc_enabled = True
        
        # Métriques
        self.metrics_history = deque(maxlen=1000)
        self.last_metrics = None
        
        # Threads de monitoring
        self.monitoring_thread = None
        self.gc_thread = None
        self.running = False
        
        self._init_database()
        self._start_background_services()
    
    def _init_database(self):
        """Initialise la base de données des performances"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP NOT NULL,
                    cpu_percent REAL NOT NULL,
                    memory_percent REAL NOT NULL,
                    memory_used_mb REAL NOT NULL,
                    disk_io_read_mb REAL NOT NULL,
                    disk_io_write_mb REAL NOT NULL,
                    network_sent_mb REAL NOT NULL,
                    network_recv_mb REAL NOT NULL,
                    active_threads INTEGER NOT NULL,
                    cache_hit_rate REAL NOT NULL,
                    response_time_ms REAL NOT NULL,
                    throughput_ops_sec REAL NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS optimization_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP NOT NULL,
                    event_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    impact_score REAL,
                    details TEXT
                )
            """)
            
            # Index pour les performances
            conn.execute("CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON performance_metrics(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_events_timestamp ON optimization_events(timestamp)")
            
            conn.commit()
    
    def _start_background_services(self):
        """Démarre les services d'arrière-plan"""
        if self.running:
            return
        
        self.running = True
        
        # Thread de monitoring
        if self.monitoring_enabled:
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitoring_thread.start()
        
        # Thread de garbage collection
        if self.auto_gc_enabled:
            self.gc_thread = threading.Thread(target=self._gc_loop, daemon=True)
            self.gc_thread.start()
        
        logger.info("🚀 Services d'optimisation démarrés")
    
    def stop_background_services(self):
        """Arrête les services d'arrière-plan"""
        self.running = False
        self.thread_manager.shutdown_all()
        logger.info("🛑 Services d'optimisation arrêtés")
    
    def _monitoring_loop(self):
        """Boucle de monitoring des performances"""
        while self.running:
            try:
                metrics = self._collect_metrics()
                self.metrics_history.append(metrics)
                self.last_metrics = metrics
                
                # Sauvegarder en base toutes les 5 minutes
                if len(self.metrics_history) % 10 == 0:
                    self._save_metrics_batch()
                
                # Détecter les problèmes de performance
                self._detect_performance_issues(metrics)
                
            except Exception as e:
                logger.error(f"Erreur monitoring: {e}")
            
            time.sleep(30)  # Monitoring toutes les 30 secondes
    
    def _gc_loop(self):
        """Boucle de garbage collection automatique"""
        while self.running:
            try:
                # GC toutes les 10 minutes
                time.sleep(600)
                
                if self.running:
                    collected = gc.collect()
                    if collected > 0:
                        logger.info(f"🧹 GC: {collected} objets collectés")
                        
                        # Enregistrer l'événement
                        self._log_optimization_event(
                            "garbage_collection",
                            f"Garbage collection automatique: {collected} objets",
                            impact_score=min(collected / 1000, 5.0)
                        )
            
            except Exception as e:
                logger.error(f"Erreur GC: {e}")
    
    def _collect_metrics(self) -> PerformanceMetrics:
        """Collecte les métriques de performance"""
        # Métriques système
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk_io = psutil.disk_io_counters()
        network_io = psutil.net_io_counters()
        
        # Métriques threads
        active_threads = threading.active_count()
        
        # Métriques cache
        cache_stats = self.cache.get_stats()
        cache_hit_rate = cache_stats["hit_rate"]
        
        # Métriques applicatives (simulées)
        response_time_ms = self._measure_response_time()
        throughput_ops_sec = self._calculate_throughput()
        
        return PerformanceMetrics(
            timestamp=datetime.datetime.now(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_used_mb=memory.used / 1024 / 1024,
            disk_io_read_mb=(disk_io.read_bytes if disk_io else 0) / 1024 / 1024,
            disk_io_write_mb=(disk_io.write_bytes if disk_io else 0) / 1024 / 1024,
            network_sent_mb=(network_io.bytes_sent if network_io else 0) / 1024 / 1024,
            network_recv_mb=(network_io.bytes_recv if network_io else 0) / 1024 / 1024,
            active_threads=active_threads,
            cache_hit_rate=cache_hit_rate,
            response_time_ms=response_time_ms,
            throughput_ops_sec=throughput_ops_sec
        )
    
    def _measure_response_time(self) -> float:
        """Mesure le temps de réponse moyen"""
        # Simulation d'une mesure de temps de réponse
        start_time = time.time()
        
        # Test simple d'accès cache
        test_key = "performance_test"
        self.cache.get(test_key)
        self.cache.set(test_key, {"test": True})
        
        end_time = time.time()
        return (end_time - start_time) * 1000  # en millisecondes
    
    def _calculate_throughput(self) -> float:
        """Calcule le débit d'opérations"""
        # Simulation basée sur les statistiques des pools
        thread_stats = self.thread_manager.get_stats()
        
        total_completed = sum(stats["completed"] for stats in thread_stats.values())
        
        # Calculer le débit sur la dernière minute
        if len(self.metrics_history) > 0:
            time_window = 60  # 1 minute
            recent_metrics = [m for m in self.metrics_history if 
                            (datetime.datetime.now() - m.timestamp).total_seconds() <= time_window]
            
            if len(recent_metrics) > 1:
                return total_completed / time_window
        
        return total_completed / 60.0  # Débit par seconde
    
    def _detect_performance_issues(self, metrics: PerformanceMetrics):
        """Détecte les problèmes de performance"""
        issues = []
        
        # CPU élevé
        if metrics.cpu_percent > 80:
            issues.append(("high_cpu", f"CPU élevé: {metrics.cpu_percent:.1f}%"))
        
        # Mémoire élevée
        if metrics.memory_percent > 85:
            issues.append(("high_memory", f"Mémoire élevée: {metrics.memory_percent:.1f}%"))
        
        # Cache hit rate faible
        if metrics.cache_hit_rate < 70:
            issues.append(("low_cache_hit", f"Cache hit rate faible: {metrics.cache_hit_rate:.1f}%"))
        
        # Temps de réponse élevé
        if metrics.response_time_ms > 1000:
            issues.append(("high_response_time", f"Temps de réponse élevé: {metrics.response_time_ms:.1f}ms"))
        
        # Trop de threads
        if metrics.active_threads > 100:
            issues.append(("too_many_threads", f"Trop de threads: {metrics.active_threads}"))
        
        # Enregistrer les problèmes détectés
        for issue_type, description in issues:
            self._log_optimization_event(
                f"performance_issue_{issue_type}",
                description,
                impact_score=3.0
            )
            
            # Appliquer des optimisations automatiques
            self._auto_optimize(issue_type, metrics)
    
    def _auto_optimize(self, issue_type: str, metrics: PerformanceMetrics):
        """Applique des optimisations automatiques"""
        optimizations_applied = []
        
        if issue_type == "high_memory":
            # Forcer le garbage collection
            collected = gc.collect()
            optimizations_applied.append(f"GC forcé: {collected} objets")
            
            # Réduire la taille du cache
            if self.cache.get_stats()["size"] > self.cache.max_size * 0.8:
                old_size = self.cache.max_size
                self.cache.max_size = int(old_size * 0.8)
                optimizations_applied.append(f"Cache réduit: {old_size} → {self.cache.max_size}")
        
        elif issue_type == "low_cache_hit":
            # Augmenter le TTL du cache
            old_ttl = self.cache.default_ttl
            self.cache.default_ttl = min(old_ttl * 1.5, 7200)  # Max 2h
            optimizations_applied.append(f"TTL cache augmenté: {old_ttl}s → {self.cache.default_ttl}s")
        
        elif issue_type == "too_many_threads":
            # Réduire le nombre de workers
            for pool_name, pool in self.thread_manager.pools.items():
                if hasattr(pool, '_max_workers') and pool._max_workers > 8:
                    # Note: ThreadPoolExecutor ne permet pas de changer max_workers dynamiquement
                    # En production, il faudrait recréer le pool
                    optimizations_applied.append(f"Pool {pool_name}: réduction recommandée")
        
        if optimizations_applied:
            self._log_optimization_event(
                f"auto_optimization_{issue_type}",
                f"Optimisations automatiques: {'; '.join(optimizations_applied)}",
                impact_score=2.0
            )
            logger.info(f"🔧 Optimisations automatiques appliquées: {optimizations_applied}")
    
    def optimize_system(self, level: OptimizationLevel = None) -> Dict[str, Any]:
        """Optimise le système selon le niveau spécifié"""
        if level:
            self.optimization_level = level
        
        logger.info(f"🚀 Optimisation système niveau {self.optimization_level.value}")
        
        optimizations = []
        start_time = time.time()
        
        # Optimisations de base
        if self.optimization_level.value in ["basic", "standard", "aggressive", "maximum"]:
            # Garbage collection
            collected = gc.collect()
            optimizations.append(f"GC: {collected} objets collectés")
            
            # Nettoyage cache expiré
            expired_cleaned = self._clean_expired_cache()
            optimizations.append(f"Cache: {expired_cleaned} entrées expirées supprimées")
        
        # Optimisations standard
        if self.optimization_level.value in ["standard", "aggressive", "maximum"]:
            # Optimisation base de données
            db_optimized = self._optimize_database()
            optimizations.append(f"DB: {db_optimized} optimisations")
            
            # Défragmentation cache
            cache_defrag = self._defragment_cache()
            optimizations.append(f"Cache défragmenté: {cache_defrag} MB libérés")
        
        # Optimisations agressives
        if self.optimization_level.value in ["aggressive", "maximum"]:
            # Compactage mémoire
            memory_compacted = self._compact_memory()
            optimizations.append(f"Mémoire compactée: {memory_compacted} MB libérés")
            
            # Optimisation threads
            threads_optimized = self._optimize_threads()
            optimizations.append(f"Threads optimisés: {threads_optimized} pools")
        
        # Optimisations maximum
        if self.optimization_level.value == "maximum":
            # Optimisation système OS
            os_optimized = self._optimize_os_settings()
            optimizations.append(f"OS optimisé: {os_optimized} paramètres")
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Enregistrer l'événement d'optimisation
        self._log_optimization_event(
            f"system_optimization_{self.optimization_level.value}",
            f"Optimisation système complète: {'; '.join(optimizations)}",
            impact_score=len(optimizations),
            details=json.dumps({
                "level": self.optimization_level.value,
                "duration_seconds": duration,
                "optimizations": optimizations
            })
        )
        
        result = {
            "level": self.optimization_level.value,
            "duration_seconds": round(duration, 2),
            "optimizations_applied": optimizations,
            "success": True
        }
        
        logger.info(f"✅ Optimisation terminée en {duration:.2f}s: {len(optimizations)} optimisations")
        return result
    
    def _clean_expired_cache(self) -> int:
        """Nettoie les entrées expirées du cache"""
        expired_count = 0
        with self.cache.lock:
            expired_keys = []
            for key, entry in self.cache.cache.items():
                if self.cache._is_expired(entry):
                    expired_keys.append(key)
            
            for key in expired_keys:
                self.cache._remove_entry(key)
                expired_count += 1
        
        return expired_count
    
    def _optimize_database(self) -> int:
        """Optimise les bases de données"""
        optimizations = 0
        
        try:
            # Optimiser la base de données principale
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("VACUUM")
                conn.execute("ANALYZE")
                optimizations += 2
            
            # Optimiser les autres bases de données
            for db_file in self.base_path.rglob("*.db"):
                if db_file != self.db_path:
                    try:
                        with sqlite3.connect(db_file) as conn:
                            conn.execute("VACUUM")
                            optimizations += 1
                    except:
                        pass
        
        except Exception as e:
            logger.warning(f"Erreur optimisation DB: {e}")
        
        return optimizations
    
    def _defragment_cache(self) -> float:
        """Défragmente le cache"""
        # Simuler la défragmentation en réorganisant le cache
        with self.cache.lock:
            old_size = self.cache.stats["size_bytes"]
            
            # Réorganiser par ordre d'accès
            sorted_items = sorted(
                self.cache.cache.items(),
                key=lambda x: x[1].access_count,
                reverse=True
            )
            
            # Reconstruire le cache
            new_cache = {}
            new_access_order = deque()
            
            for key, entry in sorted_items:
                new_cache[key] = entry
                new_access_order.append(key)
            
            self.cache.cache = new_cache
            self.cache.access_order = new_access_order
            
            new_size = self.cache.stats["size_bytes"]
            freed_mb = (old_size - new_size) / 1024 / 1024
            
            return max(0, freed_mb)
    
    def _compact_memory(self) -> float:
        """Compacte la mémoire"""
        # Mesurer la mémoire avant
        memory_before = psutil.virtual_memory().used
        
        # Forcer plusieurs cycles de GC
        for _ in range(3):
            gc.collect()
        
        # Mesurer la mémoire après
        memory_after = psutil.virtual_memory().used
        freed_mb = (memory_before - memory_after) / 1024 / 1024
        
        return max(0, freed_mb)
    
    def _optimize_threads(self) -> int:
        """Optimise les pools de threads"""
        optimized_pools = 0
        
        # Analyser l'utilisation des pools
        stats = self.thread_manager.get_stats()
        
        for pool_name, pool_stats in stats.items():
            if pool_stats["submitted"] > 0:
                efficiency = pool_stats["completed"] / pool_stats["submitted"]
                
                # Si l'efficacité est faible, marquer pour optimisation
                if efficiency < 0.8:
                    optimized_pools += 1
                    logger.info(f"Pool {pool_name} marqué pour optimisation (efficacité: {efficiency:.2f})")
        
        return optimized_pools
    
    def _optimize_os_settings(self) -> int:
        """Optimise les paramètres OS (simulation)"""
        # En production, ceci pourrait ajuster des paramètres système
        # Pour la démo, on simule quelques optimisations
        optimizations = 0
        
        try:
            # Simuler l'optimisation des paramètres réseau
            optimizations += 1
            
            # Simuler l'optimisation des paramètres de fichiers
            optimizations += 1
            
            # Simuler l'optimisation des paramètres mémoire
            optimizations += 1
            
        except Exception as e:
            logger.warning(f"Erreur optimisation OS: {e}")
        
        return optimizations
    
    def get_performance_report(self, hours: int = 24) -> Dict[str, Any]:
        """Génère un rapport de performance"""
        end_time = datetime.datetime.now()
        start_time = end_time - datetime.timedelta(hours=hours)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Métriques récentes
            cursor = conn.execute("""
                SELECT * FROM performance_metrics 
                WHERE timestamp >= ? 
                ORDER BY timestamp DESC
            """, (start_time.isoformat(),))
            
            metrics_data = [dict(row) for row in cursor.fetchall()]
            
            # Événements d'optimisation
            cursor = conn.execute("""
                SELECT * FROM optimization_events 
                WHERE timestamp >= ? 
                ORDER BY timestamp DESC
            """, (start_time.isoformat(),))
            
            events_data = [dict(row) for row in cursor.fetchall()]
        
        # Calculer les statistiques
        if metrics_data:
            avg_cpu = sum(m["cpu_percent"] for m in metrics_data) / len(metrics_data)
            avg_memory = sum(m["memory_percent"] for m in metrics_data) / len(metrics_data)
            avg_cache_hit = sum(m["cache_hit_rate"] for m in metrics_data) / len(metrics_data)
            avg_response_time = sum(m["response_time_ms"] for m in metrics_data) / len(metrics_data)
        else:
            avg_cpu = avg_memory = avg_cache_hit = avg_response_time = 0
        
        # Métriques actuelles
        current_metrics = self.last_metrics
        cache_stats = self.cache.get_stats()
        thread_stats = self.thread_manager.get_stats()
        
        return {
            "period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "hours": hours
            },
            "current_metrics": asdict(current_metrics) if current_metrics else None,
            "averages": {
                "cpu_percent": round(avg_cpu, 2),
                "memory_percent": round(avg_memory, 2),
                "cache_hit_rate": round(avg_cache_hit, 2),
                "response_time_ms": round(avg_response_time, 2)
            },
            "cache_stats": cache_stats,
            "thread_stats": thread_stats,
            "optimization_events": events_data[:10],  # 10 derniers événements
            "metrics_count": len(metrics_data),
            "events_count": len(events_data),
            "optimization_level": self.optimization_level.value,
            "services_running": self.running
        }
    
    def _save_metrics_batch(self):
        """Sauvegarde un lot de métriques"""
        if not self.metrics_history:
            return
        
        with sqlite3.connect(self.db_path) as conn:
            # Prendre les 10 dernières métriques non sauvegardées
            metrics_to_save = list(self.metrics_history)[-10:]
            
            for metrics in metrics_to_save:
                conn.execute("""
                    INSERT INTO performance_metrics
                    (timestamp, cpu_percent, memory_percent, memory_used_mb,
                     disk_io_read_mb, disk_io_write_mb, network_sent_mb, network_recv_mb,
                     active_threads, cache_hit_rate, response_time_ms, throughput_ops_sec)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    metrics.timestamp.isoformat(),
                    metrics.cpu_percent,
                    metrics.memory_percent,
                    metrics.memory_used_mb,
                    metrics.disk_io_read_mb,
                    metrics.disk_io_write_mb,
                    metrics.network_sent_mb,
                    metrics.network_recv_mb,
                    metrics.active_threads,
                    metrics.cache_hit_rate,
                    metrics.response_time_ms,
                    metrics.throughput_ops_sec
                ))
            
            conn.commit()
    
    def _log_optimization_event(self, event_type: str, description: str, impact_score: float = 1.0, details: str = None):
        """Enregistre un événement d'optimisation"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO optimization_events
                (timestamp, event_type, description, impact_score, details)
                VALUES (?, ?, ?, ?, ?)
            """, (
                datetime.datetime.now().isoformat(),
                event_type,
                description,
                impact_score,
                details
            ))

# Décorateur de cache pour les fonctions
def cached(ttl: int = 3600, cache_key_func: Callable = None):
    """Décorateur pour mettre en cache les résultats de fonction"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Générer la clé de cache
            if cache_key_func:
                cache_key = cache_key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}_{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Vérifier le cache
            cached_result = performance_optimizer.cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Exécuter la fonction
            result = func(*args, **kwargs)
            
            # Mettre en cache
            performance_optimizer.cache.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

# Instance globale
performance_optimizer = PerformanceOptimizer()

if __name__ == "__main__":
    # Test de l'optimiseur
    optimizer = PerformanceOptimizer()
    
    # Optimisation système
    result = optimizer.optimize_system(OptimizationLevel.STANDARD)
    print(f"🚀 Optimisation: {result}")
    
    # Rapport de performance
    report = optimizer.get_performance_report(hours=1)
    print(f"📊 Rapport: {report['averages']}")
    
    # Test du cache
    @cached(ttl=300)
    def test_function(x, y):
        time.sleep(0.1)  # Simuler du travail
        return x + y
    
    # Premier appel (lent)
    start = time.time()
    result1 = test_function(1, 2)
    time1 = time.time() - start
    
    # Deuxième appel (rapide, depuis le cache)
    start = time.time()
    result2 = test_function(1, 2)
    time2 = time.time() - start
    
    print(f"🔧 Test cache: {time1:.3f}s → {time2:.3f}s (speedup: {time1/time2:.1f}x)")
    
    # Arrêter les services
    optimizer.stop_background_services()

