import pytest
from unittest.mock import AsyncMock, MagicMock
from agents.base.base_agent import EnhancedAgent, AgentState

class TestEnhancedAgent:
    @pytest.fixture
    def agent(self):
        return EnhancedAgent(
            agent_id="test_agent",
            agent_type="test",
            capabilities=["test_capability"],
            llm_config={"model": "test"}
        )
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        assert agent.id == "test_agent"
        assert agent.state == AgentState.IDLE
        assert agent.performance_metrics['confidence_score'] == 0.5
    
    @pytest.mark.asyncio
    async def test_memory_system(self, agent):
        experience = {
            'type': 'test',
            'importance': 0.8,
            'concepts': {'test_concept': 0.9}
        }
        
        agent.memory.add_experience(experience)
        
        assert len(agent.memory.short_term) == 1
        assert len(agent.memory.long_term) > 0
        assert 'test_concept' in agent.memory.semantic
