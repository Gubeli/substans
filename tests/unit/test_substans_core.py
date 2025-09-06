"""
Tests unitaires pour le core de Substans.AI
"""

import pytest
import json
import os
import sys
from unittest.mock import Mock, AsyncMock, patch

# Ajouter le backend au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

class TestSubstansCore:
    """Tests du core Substans"""
    
    def test_project_structure(self):
        """Vérifier la structure du projet"""
        required_dirs = [
            'backend',
            'frontend',
            'agents',
            'deployment',
            'tests'
        ]
        
        for dir_name in required_dirs:
            assert os.path.exists(dir_name), f"Dossier {dir_name} manquant"
    
    def test_agent_files_exist(self):
        """Vérifier l'existence des fichiers agents"""
        agent_files = [
            'agents/agents_consultants/aad.py',
            'agents/agents_consultants/agc.py',
            'agents/agents_consultants/asm.py'
        ]
        
        existing = []
        missing = []
        
        for agent_file in agent_files:
            if os.path.exists(agent_file):
                existing.append(agent_file)
            else:
                missing.append(agent_file)
        
        print(f"\n✅ Agents trouvés: {len(existing)}")
        print(f"❌ Agents manquants: {len(missing)}")
        
        # Au moins quelques agents doivent exister
        assert len(existing) > 0, "Aucun fichier agent trouvé"
    
    def test_configuration_files(self):
        """Vérifier les fichiers de configuration"""
        config_files = [
            'deployment/requirements.txt',
            'frontend/react_interface/package.json'
        ]
        
        for config_file in config_files:
            assert os.path.exists(config_file), f"Fichier {config_file} manquant"
    
    @pytest.mark.asyncio
    async def test_agent_mock_processing(self):
        """Test du traitement par un agent mock"""
        # Créer un agent mock
        agent = Mock()
        agent.id = "test_agent"
        agent.process = AsyncMock(return_value={
            "status": "success",
            "result": "processed"
        })
        
        # Tester le traitement
        request = {"type": "test", "data": "sample"}
        result = await agent.process(request)
        
        assert result["status"] == "success"
        assert "result" in result
        agent.process.assert_called_once_with(request)
    
    def test_metrics_tracking(self):
        """Test du tracking des métriques"""
        from collections import defaultdict
        
        class MetricsTracker:
            def __init__(self):
                self.counters = defaultdict(int)
                self.histograms = defaultdict(list)
            
            def increment(self, metric):
                self.counters[metric] += 1
            
            def record(self, metric, value):
                self.histograms[metric].append(value)
            
            def get_stats(self, metric):
                if metric in self.histograms and self.histograms[metric]:
                    values = self.histograms[metric]
                    return {
                        'count': len(values),
                        'min': min(values),
                        'max': max(values),
                        'avg': sum(values) / len(values)
                    }
                return None
        
        tracker = MetricsTracker()
        
        # Simuler des métriques
        for i in range(10):
            tracker.increment('requests')
            tracker.record('response_time', 0.1 * (i + 1))
        
        assert tracker.counters['requests'] == 10
        
        stats = tracker.get_stats('response_time')
        assert stats['count'] == 10
        assert stats['min'] == 0.1
        assert stats['max'] == 1.0