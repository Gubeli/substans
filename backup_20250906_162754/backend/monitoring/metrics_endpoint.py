"""
Endpoint de métriques Prometheus pour Substans.AI
"""

from flask import Flask, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY
import time
import psutil
import json
import os
from datetime import datetime

app = Flask(__name__)

# Métriques personnalisées Substans
substans_requests = Counter(
    'substans_requests_total',
    'Total des requêtes Substans',
    ['endpoint', 'method', 'status']
)

substans_agents_active = Gauge(
    'substans_agents_active',
    'Nombre d\'agents actifs',
    ['agent_type']
)

substans_response_time = Histogram(
    'substans_response_time_seconds',
    'Temps de réponse en secondes',
    ['endpoint'],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
)

substans_errors = Counter(
    'substans_errors_total',
    'Total des erreurs',
    ['error_type', 'agent']
)

# Métriques système
system_cpu_usage = Gauge('system_cpu_usage_percent', 'Utilisation CPU')
system_memory_usage = Gauge('system_memory_usage_bytes', 'Utilisation mémoire')
system_disk_usage = Gauge('system_disk_usage_percent', 'Utilisation disque')

# Métriques des agents
agent_tasks_completed = Counter(
    'agent_tasks_completed_total',
    'Tâches complétées par agent',
    ['agent_id']
)

agent_processing_time = Histogram(
    'agent_processing_time_seconds',
    'Temps de traitement par agent',
    ['agent_id', 'task_type']
)

class MetricsManager:
    """Gestionnaire de métriques"""
    
    def __init__(self):
        self.start_time = time.time()
        self.update_system_metrics()
        
    def update_system_metrics(self):
        """Met à jour les métriques système"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            system_cpu_usage.set(cpu_percent)
            
            # Mémoire
            memory = psutil.virtual_memory()
            system_memory_usage.set(memory.used)
            
            # Disque
            disk = psutil.disk_usage('/')
            system_disk_usage.set(disk.percent)
            
        except Exception as e:
            print(f"Erreur mise à jour métriques système: {e}")
    
    def track_request(self, endpoint, method, status, duration):
        """Enregistre une requête"""
        substans_requests.labels(
            endpoint=endpoint,
            method=method,
            status=str(status)
        ).inc()
        
        substans_response_time.labels(endpoint=endpoint).observe(duration)
    
    def track_agent_activity(self, agent_type, count):
        """Met à jour l'activité des agents"""
        substans_agents_active.labels(agent_type=agent_type).set(count)
    
    def track_error(self, error_type, agent="unknown"):
        """Enregistre une erreur"""
        substans_errors.labels(error_type=error_type, agent=agent).inc()
    
    def track_agent_task(self, agent_id, task_type, duration):
        """Enregistre une tâche d'agent"""
        agent_tasks_completed.labels(agent_id=agent_id).inc()
        agent_processing_time.labels(
            agent_id=agent_id,
            task_type=task_type
        ).observe(duration)

# Instance globale
metrics_manager = MetricsManager()

@app.route('/metrics')
def metrics():
    """Endpoint pour Prometheus"""
    metrics_manager.update_system_metrics()
    return Response(generate_latest(REGISTRY), mimetype='text/plain')

@app.route('/health')
def health():
    """Endpoint de santé"""
    uptime = time.time() - metrics_manager.start_time
    return {
        'status': 'healthy',
        'uptime_seconds': uptime,
        'timestamp': datetime.now().isoformat()
    }

@app.route('/test_metrics')
def test_metrics():
    """Endpoint de test pour générer des métriques"""
    import random
    
    # Simuler des requêtes
    endpoints = ['/api/agents', '/api/missions', '/api/documents']
    methods = ['GET', 'POST', 'PUT']
    statuses = [200, 201, 400, 500]
    
    for _ in range(10):
        endpoint = random.choice(endpoints)
        method = random.choice(methods)
        status = random.choice(statuses)
        duration = random.uniform(0.01, 2.0)
        
        metrics_manager.track_request(endpoint, method, status, duration)
    
    # Simuler l'activité des agents
    agent_types = ['consultant', 'expert', 'analyste']
    for agent_type in agent_types:
        count = random.randint(0, 10)
        metrics_manager.track_agent_activity(agent_type, count)
    
    # Simuler des tâches d'agents
    agent_ids = ['aad', 'afc', 'agr', 'asm']
    task_types = ['analysis', 'report', 'validation']
    
    for agent_id in agent_ids:
        task_type = random.choice(task_types)
        duration = random.uniform(0.5, 10.0)
        metrics_manager.track_agent_task(agent_id, task_type, duration)
    
    return {'status': 'metrics generated', 'count': 10}

if __name__ == '__main__':
    print("🚀 Démarrage du serveur de métriques Prometheus")
    print("📊 Métriques disponibles sur http://localhost:8000/metrics")
    print("❤️ Health check sur http://localhost:8000/health")
    print("🧪 Test métriques sur http://localhost:8000/test_metrics")
    app.run(host='0.0.0.0', port=8000, debug=False)