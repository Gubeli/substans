"""
Gestionnaire de cache Redis pour Windows
"""

import redis
import json
import asyncio
from typing import Any, Optional
import pickle
import hashlib
from datetime import timedelta

class RedisManager:
    def __init__(self, host='localhost', port=6379, db=0):
        """Initialise la connexion Redis"""
        try:
            self.client = redis.Redis(
                host=host,
                port=port,
                db=db,
                decode_responses=False,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test de connexion
            self.client.ping()
            print("✅ Redis connecté avec succès")
        except redis.ConnectionError:
            print("⚠️ Redis non disponible - Mode dégradé activé")
            self.client = None
            self.fallback_cache = {}
    
    async def get(self, key: str) -> Optional[Any]:
        """Récupère une valeur du cache"""
        if self.client:
            try:
                value = self.client.get(key)
                if value:
                    return pickle.loads(value)
            except Exception as e:
                print(f"Erreur Redis GET: {e}")
        else:
            # Fallback sur cache mémoire
            return self.fallback_cache.get(key)
        return None
    
    async def set(self, key: str, value: Any, expire: int = 3600):
        """Stocke une valeur dans le cache"""
        if self.client:
            try:
                serialized = pickle.dumps(value)
                self.client.setex(key, expire, serialized)
                return True
            except Exception as e:
                print(f"Erreur Redis SET: {e}")
        else:
            # Fallback sur cache mémoire
            self.fallback_cache[key] = value
            # Limiter la taille du cache mémoire
            if len(self.fallback_cache) > 1000:
                # Supprimer les 100 plus anciennes entrées
                keys_to_remove = list(self.fallback_cache.keys())[:100]
                for k in keys_to_remove:
                    del self.fallback_cache[k]
        return False
    
    async def delete(self, key: str):
        """Supprime une clé du cache"""
        if self.client:
            try:
                self.client.delete(key)
            except Exception as e:
                print(f"Erreur Redis DELETE: {e}")
        else:
            self.fallback_cache.pop(key, None)
    
    async def clear(self):
        """Vide tout le cache"""
        if self.client:
            try:
                self.client.flushdb()
            except Exception as e:
                print(f"Erreur Redis FLUSH: {e}")
        else:
            self.fallback_cache.clear()
    
    def generate_key(self, *args) -> str:
        """Génère une clé unique basée sur les arguments"""
        key_data = ':'.join(str(arg) for arg in args)
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def get_or_set(self, key: str, func, expire: int = 3600):
        """Pattern cache-aside : récupère ou calcule et stocke"""
        value = await self.get(key)
        if value is None:
            value = await func() if asyncio.iscoroutinefunction(func) else func()
            await self.set(key, value, expire)
        return value

# Instance globale
redis_manager = RedisManager()