"""
Collecteur de métriques pour Substans.AI
Compatible Windows
"""

import psutil
import asyncio
import json
from datetime import datetime
from typing import Dict, Any
import aiofiles
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import time
import os

# Métriques Prometheus
request_count = Counter('substans_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
request_duration = Histogram('substans_request_duration_seconds', 'Request duration', ['method', 'endpoint'])
active_agents = Gauge('substans_active_agents', 'Number of active agents')
memory_usage = Gauge('substans_memory_usage_bytes', 'Memory usage in bytes')
cpu_usage = Gauge('substans_cpu_usage_percent', 'CPU usage percentage')
agent_tasks = Counter('substans_agent_tasks_total', 'Total agent tasks', ['agent_id', 'status'])
cache_hits = Counter('substans_cache_hits_total', 'Cache hits')
cache_misses = Counter('substans_cache_misses_total', 'Cache misses')

class MetricsCollector:
    def __init__(self):
        self.metrics_dir = os.path.join(os.getcwd(), "metrics")
        os.makedirs(self.metrics_dir, exist_ok=True)
        self.metrics_file = os.path.join(self.metrics_dir, f"metrics_{datetime.now().strftime('%Y%m%d')}.json")
        
    async def collect_system_metrics(self):
        """Collecte les métriques système"""
        while True:
            try:
                # Métriques CPU
                cpu_percent = psutil.cpu_percent(interval=1)
                cpu_usage.set(cpu_percent)
                
                # Métriques mémoire
                memory = psutil.virtual_memory()
                memory_usage.set(memory.used)
                
                # Métriques disque
                disk = psutil.disk_usage('/')
                
                metrics = {
                    'timestamp': datetime.now().isoformat(),
                    'cpu': {
                        'percent': cpu_percent,
                        'count': psutil.cpu_count()
                    },
                    'memory': {
                        'total': memory.total,
                        'used': memory.used,
                        'percent': memory.percent
                    },
                    'disk': {
                        'total': disk.total,
                        'used': disk.used,
                        'percent': disk.percent
                    },
                    'network': self._get_network_stats()
                }
                
                # Sauvegarder les métriques
                await self._save_metrics(metrics)
                
                # Attendre 15 secondes avant la prochaine collecte
                await asyncio.sleep(15)
                
            except Exception as e:
                print(f"Erreur collecte métriques: {e}")
                await asyncio.sleep(30)
    
    def _get_network_stats(self) -> Dict:
        """Récupère les statistiques réseau"""
        net_io = psutil.net_io_counters()
        return {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv
        }
    
    async def _save_metrics(self, metrics: Dict):
        """Sauvegarde les métriques dans un fichier"""
        async with aiofiles.open(self.metrics_file, 'a') as f:
            await f.write(json.dumps(metrics) + '\n')
    
    def track_request(self, method: str, endpoint: str, status: int, duration: float):
        """Enregistre une requête"""
        request_count.labels(method=method, endpoint=endpoint, status=str(status)).inc()
        request_duration.labels(method=method, endpoint=endpoint).observe(duration)
    
    def track_agent_task(self, agent_id: str, status: str):
        """Enregistre une tâche d'agent"""
        agent_tasks.labels(agent_id=agent_id, status=status).inc()
    
    def track_cache(self, hit: bool):
        """Enregistre un accès cache"""
        if hit:
            cache_hits.inc()
        else:
            cache_misses.inc()
    
    def update_active_agents(self, count: int):
        """Met à jour le nombre d'agents actifs"""
        active_agents.set(count)
    
    def get_prometheus_metrics(self):
        """Retourne les métriques au format Prometheus"""
        return generate_latest()

# Instance globale
metrics_collector = MetricsCollector()