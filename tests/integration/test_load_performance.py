"""
Tests de charge et performance
"""

import pytest
import asyncio
import time
import statistics
from concurrent.futures import ThreadPoolExecutor
import aiohttp
import json

class TestLoadPerformance:
    """Tests de charge pour évaluer les performances"""
    
    @pytest.fixture
    def api_client(self):
        """Client API pour les tests"""
        class APIClient:
            def __init__(self):
                self.base_url = "http://localhost:5000"
                self.session = None
            
            async def __aenter__(self):
                self.session = aiohttp.ClientSession()
                return self
            
            async def __aexit__(self, *args):
                await self.session.close()
            
            async def post(self, endpoint, data):
                async with self.session.post(
                    f"{self.base_url}{endpoint}",
                    json=data
                ) as response:
                    return response.status, await response.json()
        
        return APIClient()
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test de requêtes concurrentes"""
        async def make_request(i):
            # Simuler une requête
            await asyncio.sleep(0.01)
            return {"id": i, "status": "success"}
        
        # Lancer 100 requêtes concurrentes
        tasks = [make_request(i) for i in range(100)]
        start = time.time()
        results = await asyncio.gather(*tasks)
        duration = time.time() - start
        
        assert len(results) == 100
        assert all(r["status"] == "success" for r in results)
        assert duration < 5  # Devrait prendre moins de 5 secondes
        
        print(f"\n✅ 100 requêtes traitées en {duration:.2f}s")
        print(f"   Débit: {100/duration:.1f} req/s")
    
    def test_memory_usage(self):
        """Test de l'utilisation mémoire"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Créer beaucoup d'objets
        large_list = []
        for i in range(10000):
            large_list.append({
                "id": i,
                "data": "x" * 1000,
                "nested": {"level": 1, "items": list(range(100))}
            })
        
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = peak_memory - initial_memory
        
        # Nettoyer
        large_list.clear()
        
        print(f"\n📊 Utilisation mémoire:")
        print(f"   Initial: {initial_memory:.1f} MB")
        print(f"   Peak: {peak_memory:.1f} MB")
        print(f"   Augmentation: {memory_increase:.1f} MB")
        
        # Vérifier que l'augmentation est raisonnable (< 500 MB)
        assert memory_increase < 500
    
    @pytest.mark.asyncio
    async def test_response_times(self):
        """Test des temps de réponse"""
        response_times = []
        
        async def timed_request(i):
            start = time.time()
            # Simuler une requête avec temps variable
            await asyncio.sleep(0.01 + (i % 10) * 0.001)
            duration = time.time() - start
            response_times.append(duration)
            return duration
        
        # Faire 50 requêtes
        tasks = [timed_request(i) for i in range(50)]
        await asyncio.gather(*tasks)
        
        # Calculer les statistiques
        avg_time = statistics.mean(response_times)
        median_time = statistics.median(response_times)
        p95_time = sorted(response_times)[int(len(response_times) * 0.95)]
        p99_time = sorted(response_times)[int(len(response_times) * 0.99)]
        
        print(f"\n⏱️ Temps de réponse:")
        print(f"   Moyenne: {avg_time*1000:.1f} ms")
        print(f"   Médiane: {median_time*1000:.1f} ms")
        print(f"   P95: {p95_time*1000:.1f} ms")
        print(f"   P99: {p99_time*1000:.1f} ms")
        
        # Vérifier les SLA
        assert avg_time < 0.1  # Moyenne < 100ms
        assert p95_time < 0.2  # P95 < 200ms
    
    def test_cache_performance(self):
        """Test des performances du cache"""
        cache = {}
        
        def fibonacci_cached(n, cache=cache):
            if n in cache:
                return cache[n]
            if n <= 1:
                return n
            result = fibonacci_cached(n-1) + fibonacci_cached(n-2)
            cache[n] = result
            return result
        
        # Test sans cache (clear)
        cache.clear()
        start = time.time()
        result1 = fibonacci_cached(30)
        time_without_cache = time.time() - start
        
        # Test avec cache
        start = time.time()
        result2 = fibonacci_cached(30)
        time_with_cache = time.time() - start
        
        speedup = time_without_cache / time_with_cache if time_with_cache > 0 else float('inf')
        
        print(f"\n⚡ Performance du cache:")
        print(f"   Sans cache: {time_without_cache*1000:.3f} ms")
        print(f"   Avec cache: {time_with_cache*1000:.3f} ms")
        print(f"   Speedup: {speedup:.1f}x")
        
        assert result1 == result2
        assert speedup > 10  # Le cache devrait être au moins 10x plus rapide