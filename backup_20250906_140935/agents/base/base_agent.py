# agents/base/base_agent.py
import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from collections import deque

class AgentState(Enum):
    IDLE = "idle"
    PROCESSING = "processing"
    WAITING = "waiting"
    ERROR = "error"
    LEARNING = "learning"

@dataclass
class AgentMemory:
    """Système de mémoire hiérarchique pour les agents"""
    short_term: deque = field(default_factory=lambda: deque(maxlen=100))
    long_term: Dict[str, Any] = field(default_factory=dict)
    episodic: List[Dict] = field(default_factory=list)
    semantic: Dict[str, float] = field(default_factory=dict)
    
    def add_experience(self, experience: Dict):
        """Ajoute une expérience avec gestion intelligente de la mémoire"""
        self.short_term.append(experience)
        
        if experience.get('importance', 0) > 0.7:
            key = f"{experience['type']}_{datetime.now().isoformat()}"
            self.long_term[key] = experience
        
        if 'concepts' in experience:
            for concept, weight in experience['concepts'].items():
                if concept not in self.semantic:
                    self.semantic[concept] = 0
                self.semantic[concept] = 0.9 * self.semantic[concept] + 0.1 * weight

class EnhancedAgent:
    """Classe de base améliorée pour tous les agents"""
    
    def __init__(self, agent_id: str, agent_type: str, capabilities: List[str], llm_config: Dict[str, Any]):
        self.id = agent_id or str(uuid.uuid4())
        self.type = agent_type
        self.capabilities = capabilities
        self.llm_config = llm_config
        self.state = AgentState.IDLE
        self.memory = AgentMemory()
        self.performance_metrics = {
            'success_rate': 0.0,
            'avg_response_time': 0.0,
            'tasks_completed': 0,
            'errors_count': 0,
            'confidence_score': 0.5
        }
        self.learning_rate = 0.01
        self.experience_buffer = deque(maxlen=1000)
        self.message_queue = asyncio.Queue()
        self.subscriptions = []
        self.tools = {}
        self.context_window = deque(maxlen=10)
