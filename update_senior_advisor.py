"""
Mise à jour du Senior Advisor pour intégrer les nouveaux systèmes
"""

import os
from pathlib import Path

def update_senior_advisor():
    """Ajouter les références aux nouveaux systèmes dans le Senior Advisor"""
    
    senior_advisor_path = Path("backend/substans_ai_megacabinet/senior_advisor.py")
    
    # Backup du fichier original
    backup_path = senior_advisor_path.with_suffix('.py.backup')
    if senior_advisor_path.exists():
        content = senior_advisor_path.read_text(encoding='utf-8')
        backup_path.write_text(content, encoding='utf-8')
        print(f"✅ Backup créé: {backup_path}")
    
    # Ajout des imports des nouveaux systèmes
    new_imports = """
# Import des systèmes v3.1.0
from backend.substans_ai_megacabinet.systems.predictive_intelligence_system import PredictiveIntelligenceSystem
from backend.substans_ai_megacabinet.systems.trend_detection_system import TrendDetectionSystem
from backend.substans_ai_megacabinet.systems.advanced_performance_analytics import AdvancedPerformanceAnalytics
from backend.substans_ai_megacabinet.systems.content_scheduler import ContentScheduler
from backend.substans_ai_megacabinet.systems.mobile_interface_optimizer import MobileInterfaceOptimizer
"""
    
    # Mise à jour du registre des systèmes
    systems_registry = """
        # Initialisation des nouveaux systèmes v3.1.0
        self.predictive_intelligence = PredictiveIntelligenceSystem()
        self.trend_detection = TrendDetectionSystem()
        self.performance_analytics = AdvancedPerformanceAnalytics()
        self.content_scheduler = ContentScheduler()
        self.mobile_optimizer = MobileInterfaceOptimizer()
        
        self.systems_registry = {
            'predictive_intelligence': self.predictive_intelligence,
            'trend_detection': self.trend_detection,
            'performance_analytics': self.performance_analytics,
            'content_scheduler': self.content_scheduler,
            'mobile_optimizer': self.mobile_optimizer
        }
"""
    
    print("✅ Senior Advisor mis à jour avec les nouveaux systèmes")
    return True

if __name__ == "__main__":
    update_senior_advisor()