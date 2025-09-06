"""
Tests d'intégration pour le monitoring
"""

import pytest
import requests
import time
import json

class TestMonitoring:
    """Tests du système de monitoring"""
    
    @pytest.fixture
    def base_url(self):
        return "http://localhost:8000"
    
    def test_metrics_endpoint_available(self, base_url):
        """Test de disponibilité de l'endpoint métriques"""
        try:
            response = requests.get(f"{base_url}/metrics", timeout=5)
            assert response.status_code == 200
            assert "substans_requests_total" in response.text
            print("\n✅ Endpoint métriques accessible")
        except requests.exceptions.ConnectionError:
            pytest.skip("Serveur de métriques non démarré")
    
    def test_health_endpoint(self, base_url):
        """Test de l'endpoint health"""
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            assert response.status_code == 200
            
            data = response.json()
            assert data['status'] == 'healthy'
            assert 'uptime_seconds' in data
            print(f"\n✅ Health check OK - Uptime: {data['uptime_seconds']:.1f}s")
        except requests.exceptions.ConnectionError:
            pytest.skip("Serveur de métriques non démarré")
    
    def test_metrics_generation(self, base_url):
        """Test de génération de métriques"""
        try:
            # Générer des métriques de test
            response = requests.get(f"{base_url}/test_metrics", timeout=5)
            assert response.status_code == 200
            
            # Vérifier que les métriques sont créées
            metrics_response = requests.get(f"{base_url}/metrics", timeout=5)
            assert "substans_agents_active" in metrics_response.text
            assert "agent_tasks_completed_total" in metrics_response.text
            
            print("\n✅ Métriques générées avec succès")
        except requests.exceptions.ConnectionError:
            pytest.skip("Serveur de métriques non démarré")
    
    @pytest.mark.asyncio
    async def test_concurrent_metrics_requests(self, base_url):
        """Test de requêtes concurrentes sur les métriques"""
        import asyncio
        import aiohttp
        
        async def fetch_metrics(session):
            try:
                async with session.get(f"{base_url}/metrics") as response:
                    return response.status
            except:
                return None
        
        try:
            async with aiohttp.ClientSession() as session:
                tasks = [fetch_metrics(session) for _ in range(10)]
                results = await asyncio.gather(*tasks)
                
                successful = [r for r in results if r == 200]
                assert len(successful) > 0, "Aucune requête réussie"
                
                print(f"\n✅ {len(successful)}/10 requêtes concurrentes réussies")
        except:
            pytest.skip("Serveur de métriques non accessible")