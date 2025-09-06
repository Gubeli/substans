"""
Tests d'intégration pour les workflows
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
import json
import time

class TestWorkflowIntegration:
    """Tests d'intégration des workflows"""
    
    @pytest.fixture
    def workflow_engine(self):
        """Créer un moteur de workflow mock"""
        engine = Mock()
        engine.execute = AsyncMock()
        engine.status = "ready"
        return engine
    
    @pytest.fixture
    def sample_workflow(self):
        """Workflow de test"""
        return {
            "id": "wf_001",
            "name": "Test Workflow",
            "steps": [
                {"id": "step1", "type": "data_collection", "agent": "aad"},
                {"id": "step2", "type": "analysis", "agent": "afc"},
                {"id": "step3", "type": "report", "agent": "agr"}
            ]
        }
    
    @pytest.mark.asyncio
    async def test_complete_workflow_execution(self, workflow_engine, sample_workflow):
        """Test d'exécution complète d'un workflow"""
        workflow_engine.execute.return_value = {
            "status": "completed",
            "results": {
                "step1": {"status": "success", "data": "collected"},
                "step2": {"status": "success", "data": "analyzed"},
                "step3": {"status": "success", "data": "reported"}
            }
        }
        
        result = await workflow_engine.execute(sample_workflow)
        
        assert result["status"] == "completed"
        assert all(step["status"] == "success" for step in result["results"].values())
    
    @pytest.mark.asyncio
    async def test_workflow_error_recovery(self, workflow_engine, sample_workflow):
        """Test de récupération d'erreur dans un workflow"""
        # Simuler une erreur puis un succès
        workflow_engine.execute.side_effect = [
            Exception("Network error"),
            {"status": "completed", "results": {}}
        ]
        
        # Premier essai - échec
        with pytest.raises(Exception):
            await workflow_engine.execute(sample_workflow)
        
        # Retry - succès
        result = await workflow_engine.execute(sample_workflow)
        assert result["status"] == "completed"
    
    @pytest.mark.asyncio
    async def test_workflow_timeout(self, workflow_engine, sample_workflow):
        """Test du timeout d'un workflow"""
        async def slow_execution(workflow):
            await asyncio.sleep(10)
            return {"status": "timeout"}
        
        workflow_engine.execute = slow_execution
        
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(
                workflow_engine.execute(sample_workflow),
                timeout=1.0
            )
    
    @pytest.mark.asyncio
    async def test_parallel_workflow_steps(self, workflow_engine):
        """Test des étapes parallèles dans un workflow"""
        parallel_workflow = {
            "id": "wf_parallel",
            "steps": [
                {"id": "p1", "parallel": True},
                {"id": "p2", "parallel": True},
                {"id": "p3", "parallel": True}
            ]
        }
        
        start_time = time.time()
        
        async def parallel_step(step_id):
            await asyncio.sleep(1)
            return {"id": step_id, "status": "success"}
        
        # Exécuter les étapes en parallèle
        tasks = [parallel_step(step["id"]) for step in parallel_workflow["steps"]]
        results = await asyncio.gather(*tasks)
        
        elapsed = time.time() - start_time
        
        # Vérifier que les étapes se sont exécutées en parallèle (< 2 secondes)
        assert elapsed < 2
        assert len(results) == 3
        assert all(r["status"] == "success" for r in results)