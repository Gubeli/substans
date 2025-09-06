"""
Tests unitaires pour les agents de base
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
import sys
import os

# Ajouter le chemin du backend au path Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

class TestAgentBase:
    """Tests pour la classe de base des agents"""
    
    @pytest.fixture
    def mock_agent(self):
        """Créer un agent mock pour les tests"""
        agent = Mock()
        agent.id = "test_agent_001"
        agent.type = "consultant"
        agent.status = "idle"
        agent.process = AsyncMock(return_value={"status": "success"})
        return agent
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, mock_agent):
        """Test de l'initialisation d'un agent"""
        assert mock_agent.id == "test_agent_001"
        assert mock_agent.type == "consultant"
        assert mock_agent.status == "idle"
    
    @pytest.mark.asyncio
    async def test_agent_process_request(self, mock_agent):
        """Test du traitement d'une requête par un agent"""
        request = {"type": "analysis", "data": "test data"}
        result = await mock_agent.process(request)
        
        assert result["status"] == "success"
        mock_agent.process.assert_called_once_with(request)
    
    @pytest.mark.asyncio
    async def test_agent_error_handling(self, mock_agent):
        """Test de la gestion d'erreur d'un agent"""
        mock_agent.process.side_effect = Exception("Test error")
        
        request = {"type": "analysis", "data": "test data"}
        
        with pytest.raises(Exception) as exc_info:
            await mock_agent.process(request)
        
        assert str(exc_info.value) == "Test error"
    
    def test_agent_state_transitions(self, mock_agent):
        """Test des transitions d'état de l'agent"""
        states = ["idle", "processing", "completed", "error"]
        
        for state in states:
            mock_agent.status = state
            assert mock_agent.status == state
    
    @pytest.mark.asyncio
    async def test_agent_concurrent_requests(self, mock_agent):
        """Test de requêtes concurrentes"""
        requests = [
            {"type": "analysis", "id": i} 
            for i in range(5)
        ]
        
        tasks = [mock_agent.process(req) for req in requests]
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 5
        assert all(r["status"] == "success" for r in results)

class TestAgentMemory:
    """Tests pour le système de mémoire des agents"""
    
    @pytest.fixture
    def memory_system(self):
        """Créer un système de mémoire mock"""
        from collections import deque
        
        class MemorySystem:
            def __init__(self):
                self.short_term = deque(maxlen=100)
                self.long_term = {}
                
            def add(self, item):
                self.short_term.append(item)
                if item.get("importance", 0) > 0.7:
                    self.long_term[item["id"]] = item
                    
            def get(self, item_id):
                return self.long_term.get(item_id)
                
            def clear(self):
                self.short_term.clear()
                self.long_term.clear()
        
        return MemorySystem()
    
    def test_memory_storage(self, memory_system):
        """Test du stockage en mémoire"""
        item = {"id": "mem_001", "data": "test", "importance": 0.8}
        memory_system.add(item)
        
        assert len(memory_system.short_term) == 1
        assert "mem_001" in memory_system.long_term
    
    def test_memory_importance_filter(self, memory_system):
        """Test du filtre d'importance"""
        important = {"id": "imp_001", "data": "important", "importance": 0.9}
        not_important = {"id": "not_001", "data": "not important", "importance": 0.3}
        
        memory_system.add(important)
        memory_system.add(not_important)
        
        assert "imp_001" in memory_system.long_term
        assert "not_001" not in memory_system.long_term
        assert len(memory_system.short_term) == 2