"""
Tests pour les systèmes implémentés
"""

import pytest
import asyncio
from systems.predictive_intelligence_system import PredictiveIntelligenceSystem
from systems.trend_detection_system import TrendDetectionSystem

@pytest.mark.asyncio
async def test_predictive_intelligence():
    """Test du système d'intelligence prédictive"""
    system = PredictiveIntelligenceSystem()
    
    result = await system.predict('revenue', {'current_revenue': 100000})
    
    assert result['status'] == 'success'
    assert 'predictions' in result
    assert result['prediction_type'] == 'revenue'

@pytest.mark.asyncio
async def test_trend_detection():
    """Test du système de détection de tendances"""
    system = TrendDetectionSystem()
    
    data = [100, 105, 110, 108, 115, 120, 125, 130, 135, 140]
    result = await system.detect_trends(data)
    
    assert result['status'] == 'success'
    assert 'trends' in result
    assert len(result['trends']) > 0

def test_all_systems_imported():
    """Test que tous les systèmes peuvent être importés"""
    from systems import AVAILABLE_SYSTEMS
    assert len(AVAILABLE_SYSTEMS) >= 5
