"""
Factory Pattern pour la gestion des agents
"""

from typing import Dict, Any, Type, Optional
import importlib

class AgentFactory:
    """Factory pour création dynamique des agents"""
    
    _registry: Dict[str, Type] = {}
    _instances: Dict[str, Any] = {}
    
    @classmethod
    def register(cls, agent_type: str, agent_class: Type):
        """Enregistre un type d'agent"""
        cls._registry[agent_type] = agent_class
        print(f"Agent '{agent_type}' enregistré")
    
    @classmethod
    def create(cls, agent_type: str, config: Dict = None) -> Any:
        """Crée une instance d'agent"""
        if agent_type not in cls._registry:
            raise ValueError(f"Type d'agent inconnu: {agent_type}")
        
        if agent_type not in cls._instances:
            cls._instances[agent_type] = cls._registry[agent_type](config or {})
        
        return cls._instances[agent_type]
    
    @classmethod
    def get_or_create(cls, agent_type: str, config: Dict = None) -> Any:
        """Récupère ou crée une instance"""
        if agent_type in cls._instances:
            return cls._instances[agent_type]
        return cls.create(agent_type, config)
    
    @classmethod
    def list_available(cls) -> list:
        """Liste les agents disponibles"""
        return list(cls._registry.keys())
    
    @classmethod
    def hot_swap(cls, agent_type: str, new_instance: Any):
        """Remplace une instance à chaud"""
        old_instance = cls._instances.get(agent_type)
        
        if old_instance and hasattr(old_instance, 'cleanup'):
            old_instance.cleanup()
        
        cls._instances[agent_type] = new_instance
        print(f"Agent '{agent_type}' remplacé à chaud")

# Instance globale
factory = AgentFactory()
