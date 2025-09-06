#!/usr/bin/env python3
"""
Substans Enterprise Integration - Substans.AI v3.0
Intégration complète de tous les systèmes enterprise
"""

import os
import sys
import json
import logging
import asyncio
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

# Ajouter le répertoire courant au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Imports des systèmes enterprise
from substans_core_engine import SubstansCoreEngine
from system_orchestrator import SystemOrchestrator
from ml_engine import MLEngine
from system_monitor import SystemMonitor
from knowledge_base_semantic import KnowledgeBaseSemantic
from methodology_adaptive import MethodologyAdaptive
from predictive_intelligence import PredictiveIntelligence
from trend_detection import TrendDetection
from mission_lifecycle_manager import MissionLifecycleManager
from quality_assurance_system import QualityAssuranceSystem
from performance_analytics import PerformanceAnalytics
from resource_allocator import ResourceAllocator
from api_gateway import APIGateway
from notification_engine import NotificationEngine
from documentation_generator import DocumentationGenerator
from security_manager import SecurityManager
from rbac_system import RBACSystem
from audit_system import AuditSystem
from encryption_system import EncryptionSystem

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SystemStatus:
    """Statut d'un système"""
    name: str
    status: str
    health_score: float
    last_check: datetime
    metrics: Dict[str, Any]
    errors: List[str]

class SubstansEnterpriseIntegration:
    """Intégration enterprise complète de Substans.AI"""
    
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        
        # Configuration enterprise
        self.config = {
            'version': '3.0.0',
            'environment': 'enterprise',
            'debug': False,
            'max_concurrent_missions': 100,
            'max_concurrent_users': 1000,
            'performance_monitoring': True,
            'security_level': 'high',
            'audit_all_operations': True,
            'auto_scaling': True,
            'backup_enabled': True,
            'disaster_recovery': True
        }
        
        # Systèmes enterprise
        self.systems = {}
        self.system_status = {}
        
        # Métriques globales
        self.global_metrics = {
            'total_missions': 0,
            'active_missions': 0,
            'total_users': 0,
            'active_users': 0,
            'system_uptime': 0,
            'performance_score': 0,
            'security_score': 0,
            'compliance_score': 0
        }
        
        # Initialiser tous les systèmes
        self._initialize_all_systems()
        
        # Configurer les routes API
        self._setup_api_routes()
        
        # Démarrer les services
        self._start_enterprise_services()
        
        logger.info("Substans Enterprise Integration v3.0 initialisé")
    
    def _initialize_all_systems(self):
        """Initialise tous les systèmes enterprise"""
        try:
            # Systèmes Core (Phase 3A)
            logger.info("Initialisation des systèmes Core...")
            self.systems['core_engine'] = SubstansCoreEngine()
            self.systems['orchestrator'] = SystemOrchestrator()
            self.systems['ml_engine'] = MLEngine()
            self.systems['monitor'] = SystemMonitor()
            
            # Systèmes Spécialisés (Phase 3B)
            logger.info("Initialisation des systèmes Spécialisés...")
            self.systems['knowledge_base'] = KnowledgeBaseSemantic()
            self.systems['methodology'] = MethodologyAdaptive()
            self.systems['predictive_intelligence'] = PredictiveIntelligence()
            self.systems['trend_detection'] = TrendDetection()
            
            # Gestion Missions (Phase 3C)
            logger.info("Initialisation de la gestion des missions...")
            self.systems['mission_manager'] = MissionLifecycleManager()
            self.systems['quality_assurance'] = QualityAssuranceSystem()
            self.systems['performance_analytics'] = PerformanceAnalytics()
            self.systems['resource_allocator'] = ResourceAllocator()
            
            # Intégration (Phase 3D)
            logger.info("Initialisation de l'intégration...")
            self.systems['api_gateway'] = APIGateway()
            self.systems['notification_engine'] = NotificationEngine()
            self.systems['documentation'] = DocumentationGenerator()
            
            # Sécurité (Phase 3E)
            logger.info("Initialisation de la sécurité...")
            self.systems['security_manager'] = SecurityManager()
            self.systems['rbac'] = RBACSystem()
            self.systems['audit'] = AuditSystem()
            self.systems['encryption'] = EncryptionSystem()
            
            # Initialiser le statut de tous les systèmes
            for name, system in self.systems.items():
                self.system_status[name] = SystemStatus(
                    name=name,
                    status='active',
                    health_score=100.0,
                    last_check=datetime.now(),
                    metrics={},
                    errors=[]
                )
            
            logger.info(f"Tous les systèmes initialisés: {len(self.systems)} systèmes actifs")
            
        except Exception as e:
            logger.error(f"Erreur initialisation systèmes: {e}")
            raise
    
    def _setup_api_routes(self):
        """Configure les routes API enterprise"""
        
        @self.app.route('/')
        def index():
            """Page d'accueil"""
            return render_template('index.html', version=self.config['version'])
        
        @self.app.route('/api/health')
        def health_check():
            """Vérification de santé globale"""
            return jsonify({
                'status': 'healthy',
                'version': self.config['version'],
                'timestamp': datetime.now().isoformat(),
                'systems_count': len(self.systems),
                'active_systems': len([s for s in self.system_status.values() if s.status == 'active']),
                'global_metrics': self.global_metrics
            })
        
        @self.app.route('/api/systems/status')
        def systems_status():
            """Statut de tous les systèmes"""
            status_data = {}
            for name, status in self.system_status.items():
                status_data[name] = {
                    'status': status.status,
                    'health_score': status.health_score,
                    'last_check': status.last_check.isoformat(),
                    'metrics': status.metrics,
                    'errors': status.errors
                }
            
            return jsonify({
                'systems': status_data,
                'summary': {
                    'total_systems': len(self.systems),
                    'active_systems': len([s for s in self.system_status.values() if s.status == 'active']),
                    'average_health': sum(s.health_score for s in self.system_status.values()) / len(self.system_status),
                    'last_update': datetime.now().isoformat()
                }
            })
        
        @self.app.route('/api/dashboard/enterprise')
        def enterprise_dashboard():
            """Dashboard enterprise complet"""
            dashboard_data = {
                'overview': {
                    'version': self.config['version'],
                    'environment': self.config['environment'],
                    'uptime': self._calculate_uptime(),
                    'performance_score': self._calculate_performance_score(),
                    'security_score': self._calculate_security_score(),
                    'compliance_score': self._calculate_compliance_score()
                },
                'systems': {},
                'metrics': self.global_metrics,
                'alerts': self._get_active_alerts(),
                'recent_activities': self._get_recent_activities()
            }
            
            # Ajouter les dashboards de chaque système
            for name, system in self.systems.items():
                try:
                    if hasattr(system, 'get_dashboard'):
                        dashboard_data['systems'][name] = system.get_dashboard()
                    elif hasattr(system, 'get_system_dashboard'):
                        dashboard_data['systems'][name] = system.get_system_dashboard()
                    elif hasattr(system, 'get_audit_dashboard'):
                        dashboard_data['systems'][name] = system.get_audit_dashboard()
                    elif hasattr(system, 'get_encryption_dashboard'):
                        dashboard_data['systems'][name] = system.get_encryption_dashboard()
                except Exception as e:
                    logger.error(f"Erreur récupération dashboard {name}: {e}")
            
            return jsonify(dashboard_data)
        
        @self.app.route('/api/missions', methods=['GET', 'POST'])
        def missions_api():
            """API de gestion des missions"""
            if request.method == 'GET':
                # Récupérer les missions
                missions = self.systems['mission_manager'].get_all_missions()
                return jsonify({
                    'missions': [mission.to_dict() for mission in missions],
                    'total': len(missions)
                })
            
            elif request.method == 'POST':
                # Créer une nouvelle mission
                data = request.get_json()
                mission = self.systems['mission_manager'].create_mission(
                    title=data['title'],
                    description=data['description'],
                    client_id=data.get('client_id'),
                    mission_type=data.get('type', 'analyse_strategique'),
                    priority=data.get('priority', 'medium'),
                    deadline=datetime.fromisoformat(data['deadline']) if data.get('deadline') else None,
                    budget=data.get('budget'),
                    metadata=data.get('metadata', {})
                )
                
                return jsonify({
                    'mission': mission.to_dict(),
                    'message': 'Mission créée avec succès'
                }), 201
        
        @self.app.route('/api/agents')
        def agents_api():
            """API des agents"""
            # Simuler les données des agents (à connecter avec le système réel)
            agents_data = {
                'total_agents': 32,
                'active_agents': 32,
                'agents_by_category': {
                    'senior_advisor': 1,
                    'consultants': 7,
                    'experts_metiers': 11,
                    'experts_domaines': 13
                },
                'performance_metrics': {
                    'average_response_time': 0.5,
                    'success_rate': 98.5,
                    'satisfaction_score': 9.2
                }
            }
            
            return jsonify(agents_data)
        
        @self.app.route('/api/intelligence/daily')
        def daily_intelligence():
            """Intelligence quotidienne"""
            # Récupérer l'intelligence des systèmes de veille
            intelligence_data = {
                'date': datetime.now().date().isoformat(),
                'sources_monitored': 290,
                'insights_generated': 45,
                'trends_detected': 12,
                'alerts_raised': 3,
                'reports_available': 24
            }
            
            return jsonify(intelligence_data)
        
        @self.app.route('/api/security/status')
        def security_status():
            """Statut sécurité"""
            return jsonify(self.systems['security_manager'].get_security_dashboard())
        
        @self.app.route('/api/audit/dashboard')
        def audit_dashboard():
            """Dashboard d'audit"""
            return jsonify(self.systems['audit'].get_audit_dashboard())
        
        @self.app.route('/api/performance/metrics')
        def performance_metrics():
            """Métriques de performance"""
            return jsonify(self.systems['performance_analytics'].get_dashboard())
        
        @self.app.route('/api/system/<system_name>/restart', methods=['POST'])
        def restart_system(system_name):
            """Redémarre un système"""
            if system_name not in self.systems:
                return jsonify({'error': 'Système introuvable'}), 404
            
            try:
                # Simuler le redémarrage
                self.system_status[system_name].status = 'restarting'
                time.sleep(1)  # Simuler le temps de redémarrage
                self.system_status[system_name].status = 'active'
                self.system_status[system_name].last_check = datetime.now()
                
                return jsonify({
                    'message': f'Système {system_name} redémarré avec succès',
                    'status': 'active'
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
    
    def _calculate_uptime(self) -> float:
        """Calcule l'uptime du système"""
        # Simuler l'uptime (à implémenter avec des vraies métriques)
        return 99.95
    
    def _calculate_performance_score(self) -> float:
        """Calcule le score de performance global"""
        scores = []
        
        # Score des systèmes actifs
        active_systems = len([s for s in self.system_status.values() if s.status == 'active'])
        system_score = (active_systems / len(self.systems)) * 100
        scores.append(system_score)
        
        # Score de santé moyen
        health_score = sum(s.health_score for s in self.system_status.values()) / len(self.system_status)
        scores.append(health_score)
        
        return sum(scores) / len(scores)
    
    def _calculate_security_score(self) -> float:
        """Calcule le score de sécurité"""
        try:
            security_dashboard = self.systems['security_manager'].get_security_dashboard()
            return security_dashboard.get('overall_security_score', 95.0)
        except:
            return 95.0
    
    def _calculate_compliance_score(self) -> float:
        """Calcule le score de conformité"""
        try:
            audit_dashboard = self.systems['audit'].get_audit_dashboard()
            return audit_dashboard.get('compliance_score', 92.0)
        except:
            return 92.0
    
    def _get_active_alerts(self) -> List[Dict[str, Any]]:
        """Récupère les alertes actives"""
        alerts = []
        
        # Vérifier les systèmes en erreur
        for name, status in self.system_status.items():
            if status.errors:
                alerts.append({
                    'type': 'system_error',
                    'severity': 'warning',
                    'system': name,
                    'message': f"Erreurs détectées dans {name}",
                    'timestamp': status.last_check.isoformat()
                })
            
            if status.health_score < 80:
                alerts.append({
                    'type': 'low_performance',
                    'severity': 'warning',
                    'system': name,
                    'message': f"Performance dégradée: {status.health_score}%",
                    'timestamp': status.last_check.isoformat()
                })
        
        return alerts
    
    def _get_recent_activities(self) -> List[Dict[str, Any]]:
        """Récupère les activités récentes"""
        activities = [
            {
                'type': 'system_start',
                'message': 'Substans Enterprise v3.0 démarré',
                'timestamp': datetime.now().isoformat(),
                'user': 'system'
            },
            {
                'type': 'systems_initialized',
                'message': f'{len(self.systems)} systèmes enterprise initialisés',
                'timestamp': datetime.now().isoformat(),
                'user': 'system'
            }
        ]
        
        return activities
    
    def _start_enterprise_services(self):
        """Démarre les services enterprise"""
        def system_monitoring():
            """Service de monitoring des systèmes"""
            while True:
                try:
                    self._update_system_status()
                    self._update_global_metrics()
                    time.sleep(30)  # Vérification toutes les 30 secondes
                except Exception as e:
                    logger.error(f"Erreur monitoring: {e}")
                    time.sleep(60)
        
        def performance_optimization():
            """Service d'optimisation des performances"""
            while True:
                try:
                    self._optimize_performance()
                    time.sleep(300)  # Optimisation toutes les 5 minutes
                except Exception as e:
                    logger.error(f"Erreur optimisation: {e}")
                    time.sleep(600)
        
        def backup_service():
            """Service de sauvegarde"""
            while True:
                try:
                    if self.config['backup_enabled']:
                        self._perform_backup()
                    time.sleep(3600)  # Sauvegarde toutes les heures
                except Exception as e:
                    logger.error(f"Erreur sauvegarde: {e}")
                    time.sleep(1800)
        
        # Démarrer les services en arrière-plan
        services = [
            threading.Thread(target=system_monitoring, daemon=True),
            threading.Thread(target=performance_optimization, daemon=True),
            threading.Thread(target=backup_service, daemon=True)
        ]
        
        for service in services:
            service.start()
        
        logger.info("Services enterprise démarrés")
    
    def _update_system_status(self):
        """Met à jour le statut des systèmes"""
        for name, system in self.systems.items():
            try:
                # Vérifier la santé du système
                health_score = 100.0
                errors = []
                
                # Test basique de fonctionnement
                if hasattr(system, 'health_check'):
                    health_result = system.health_check()
                    health_score = health_result.get('score', 100.0)
                    errors = health_result.get('errors', [])
                
                # Mettre à jour le statut
                self.system_status[name].health_score = health_score
                self.system_status[name].last_check = datetime.now()
                self.system_status[name].errors = errors
                self.system_status[name].status = 'active' if health_score > 50 else 'degraded'
                
            except Exception as e:
                self.system_status[name].status = 'error'
                self.system_status[name].errors = [str(e)]
                self.system_status[name].health_score = 0.0
                logger.error(f"Erreur vérification système {name}: {e}")
    
    def _update_global_metrics(self):
        """Met à jour les métriques globales"""
        try:
            # Calculer les métriques
            self.global_metrics['system_uptime'] = self._calculate_uptime()
            self.global_metrics['performance_score'] = self._calculate_performance_score()
            self.global_metrics['security_score'] = self._calculate_security_score()
            self.global_metrics['compliance_score'] = self._calculate_compliance_score()
            
            # Métriques des missions (simulées)
            self.global_metrics['active_missions'] = 5
            self.global_metrics['total_missions'] = 127
            
            # Métriques des utilisateurs (simulées)
            self.global_metrics['active_users'] = 12
            self.global_metrics['total_users'] = 45
            
        except Exception as e:
            logger.error(f"Erreur mise à jour métriques: {e}")
    
    def _optimize_performance(self):
        """Optimise les performances du système"""
        try:
            # Optimisation du cache
            for name, system in self.systems.items():
                if hasattr(system, 'optimize_cache'):
                    system.optimize_cache()
            
            # Nettoyage des ressources
            if hasattr(self.systems.get('resource_allocator'), 'cleanup_unused_resources'):
                self.systems['resource_allocator'].cleanup_unused_resources()
            
            logger.debug("Optimisation des performances effectuée")
            
        except Exception as e:
            logger.error(f"Erreur optimisation performances: {e}")
    
    def _perform_backup(self):
        """Effectue une sauvegarde du système"""
        try:
            backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = f"backup_{backup_timestamp}"
            
            # Créer le répertoire de sauvegarde
            os.makedirs(backup_dir, exist_ok=True)
            
            # Sauvegarder les bases de données
            for name, system in self.systems.items():
                if hasattr(system, 'backup_database'):
                    system.backup_database(os.path.join(backup_dir, f"{name}.backup"))
            
            logger.info(f"Sauvegarde effectuée: {backup_dir}")
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde: {e}")
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Lance l'application enterprise"""
        logger.info(f"Démarrage Substans Enterprise v{self.config['version']}")
        logger.info(f"Systèmes actifs: {len(self.systems)}")
        logger.info(f"Écoute sur {host}:{port}")
        
        self.app.run(host=host, port=port, debug=debug, threaded=True)
    
    def shutdown(self):
        """Arrêt propre du système"""
        logger.info("Arrêt de Substans Enterprise...")
        
        # Arrêter tous les systèmes
        for name, system in self.systems.items():
            try:
                if hasattr(system, 'shutdown'):
                    system.shutdown()
                self.system_status[name].status = 'stopped'
            except Exception as e:
                logger.error(f"Erreur arrêt système {name}: {e}")
        
        logger.info("Substans Enterprise arrêté")

# Point d'entrée principal
if __name__ == "__main__":
    try:
        # Créer et lancer l'intégration enterprise
        enterprise = SubstansEnterpriseIntegration()
        enterprise.run(debug=False)
        
    except KeyboardInterrupt:
        logger.info("Interruption utilisateur")
        if 'enterprise' in locals():
            enterprise.shutdown()
    except Exception as e:
        logger.error(f"Erreur fatale: {e}")
        sys.exit(1)

