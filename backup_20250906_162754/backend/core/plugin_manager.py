"""
Système de plugins extensible
"""

import os
import json
import importlib.util
from typing import Dict, Any, Optional
from pathlib import Path

class PluginManager:
    """Gestionnaire de plugins"""
    
    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = Path(plugins_dir)
        self.plugins_dir.mkdir(exist_ok=True)
        self.loaded_plugins = {}
        self.metadata = {}
    
    def discover_plugins(self) -> list:
        """Découvre les plugins disponibles"""
        discovered = []
        
        for file in self.plugins_dir.glob("*.py"):
            if not file.name.startswith("__"):
                plugin_name = file.stem
                discovered.append(plugin_name)
                
                # Charger les métadonnées si disponibles
                metadata_file = self.plugins_dir / f"{plugin_name}.json"
                if metadata_file.exists():
                    with open(metadata_file) as f:
                        self.metadata[plugin_name] = json.load(f)
        
        return discovered
    
    def load_plugin(self, plugin_name: str) -> bool:
        """Charge un plugin"""
        if plugin_name in self.loaded_plugins:
            return True
        
        plugin_path = self.plugins_dir / f"{plugin_name}.py"
        
        if not plugin_path.exists():
            return False
        
        try:
            # Chargement dynamique
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            self.loaded_plugins[plugin_name] = module
            print(f"Plugin '{plugin_name}' chargé")
            return True
            
        except Exception as e:
            print(f"Erreur chargement plugin {plugin_name}: {e}")
            return False
    
    def execute_plugin(self, plugin_name: str, data: Dict) -> Optional[Dict]:
        """Exécute un plugin"""
        if plugin_name not in self.loaded_plugins:
            if not self.load_plugin(plugin_name):
                return None
        
        module = self.loaded_plugins[plugin_name]
        
        if hasattr(module, 'execute'):
            return module.execute(data)
        
        return None
    
    def get_loaded_plugins(self) -> list:
        """Liste les plugins chargés"""
        return list(self.loaded_plugins.keys())

# Instance globale
plugin_manager = PluginManager()
