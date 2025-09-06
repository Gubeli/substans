"""
Systems Module
Tous les systèmes enterprise de Substans.AI v3.1.0
"""

# Import des systèmes
from .predictive_intelligence_system import PredictiveIntelligenceSystem
from .trend_detection_system import TrendDetectionSystem
from .advanced_performance_analytics import AdvancedPerformanceAnalytics
from .content_scheduler import ContentScheduler
from .mobile_interface_optimizer import MobileInterfaceOptimizer

# Liste des systèmes disponibles
AVAILABLE_SYSTEMS = [
    'PredictiveIntelligenceSystem',
    'TrendDetectionSystem',
    'AdvancedPerformanceAnalytics',
    'ContentScheduler',
    'MobileInterfaceOptimizer',
    # Ajouter les autres au fur et à mesure
]

__all__ = AVAILABLE_SYSTEMS
__version__ = "3.1.0"
