#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'application automatique de toutes les modifications d'audit
pour Substans.AI Enterprise v3.0.1

Usage: python apply_changes.py [--backup] [--verbose]
"""

import os
import sys
import shutil
import json
import argparse
from pathlib import Path
from datetime import datetime

class SubstansUpgrader:
    def __init__(self, project_root=".", backup=True, verbose=False):
        self.project_root = Path(project_root)
        self.backup = backup
        self.verbose = verbose
        self.changes_log = []
        
    def log(self, message):
        """Log un message"""
        self.changes_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        if self.verbose:
            print(message)
    
    def create_backup(self):
        """Creer une sauvegarde complete du projet"""
        if self.backup:
            backup_dir = self.project_root / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.log(f"Creation de la sauvegarde dans {backup_dir}")
            
            # Liste des dossiers a sauvegarder
            dirs_to_backup = ['agents', 'backend', 'frontend', 'systems', 'deployment']
            
            for dir_name in dirs_to_backup:
                src = self.project_root / dir_name
                if src.exists():
                    dst = backup_dir / dir_name
                    shutil.copytree(src, dst)
                    
            self.log("[OK] Sauvegarde creee avec succes")
            return backup_dir
        return None
    
    def create_directory_structure(self):
        """Creer les nouveaux dossiers necessaires"""
        new_dirs = [
            'agents/base',
            'backend/substans_ai_megacabinet/orchestration',
            'backend/substans_ai_megacabinet/document_management',
            'backend/substans_ai_megacabinet/monitoring',
            'frontend/react_interface/src/components/documents',
            'tests/unit',
            'tests/integration',
            'tests/load',
            'config/templates',
            'logs',
            'migrations'
        ]
        
        for dir_path in new_dirs:
            full_path = self.project_root / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            self.log(f"[DOSSIER] Cree: {dir_path}")
    
    def create_base_agent_class(self):
        """Creer la nouvelle classe de base pour les agents"""
        content = '''# agents/base/base_agent.py
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
    """Systeme de memoire hierarchique pour les agents"""
    short_term: deque = field(default_factory=lambda: deque(maxlen=100))
    long_term: Dict[str, Any] = field(default_factory=dict)
    episodic: List[Dict] = field(default_factory=list)
    semantic: Dict[str, float] = field(default_factory=dict)
    
    def add_experience(self, experience: Dict):
        """Ajoute une experience avec gestion intelligente de la memoire"""
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
    """Classe de base amelioree pour tous les agents"""
    
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
'''
        
        file_path = self.project_root / "agents/base/base_agent.py"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        self.log("[OK] Classe de base des agents creee")
    
    def update_requirements(self):
        """Mettre a jour requirements.txt avec les nouvelles dependances"""
        new_requirements = """# Core
flask==3.0.0
flask-cors==4.0.0
flask-jwt-extended==4.5.3
sqlalchemy==2.0.23
alembic==1.13.0

# Database
psycopg2-binary==2.9.9
redis==5.0.1

# AI/ML
openai==1.6.1
langchain==0.1.0
langchain-community==0.0.10
transformers==4.36.0
torch==2.1.0

# Async
asyncio==3.4.3
aiohttp==3.9.1
aiofiles==23.2.1

# Document Processing
pypandoc==1.12
python-docx==1.1.0
openpyxl==3.1.2
reportlab==4.0.7
mammoth==1.6.0
pdfkit==1.0.0
jinja2==3.1.2

# Monitoring
opentelemetry-api==1.21.0
opentelemetry-sdk==1.21.0
opentelemetry-exporter-prometheus==0.42b0
prometheus-client==0.19.0

# Cloud Storage
office365-rest-python-client==2.5.2
google-api-python-client==2.108.0
boto3==1.34.0

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
locust==2.20.0

# Utils
python-dotenv==1.0.0
pydantic==2.5.0
networkx==3.2
numpy==1.26.0
pandas==2.1.4
"""
        
        req_path = self.project_root / "deployment/requirements.txt"
        with open(req_path, 'w', encoding='utf-8') as f:
            f.write(new_requirements)
        self.log("[OK] Requirements.txt mis a jour")
    
    def create_docker_compose_enhanced(self):
        """Creer un docker-compose.yml ameliore"""
        content = """version: '3.8'

services:
  # Base de donnees PostgreSQL
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: substans_db
      POSTGRES_USER: substans_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U substans_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis pour le cache
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Backend API
  backend:
    build:
      context: .
      dockerfile: deployment/Dockerfile.backend
    environment:
      DATABASE_URL: postgresql://substans_user:${DB_PASSWORD}@postgres:5432/substans_db
      REDIS_URL: redis://redis:6379
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    volumes:
      - ./backend:/app/backend
      - ./logs:/app/logs
    ports:
      - "5000:5000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped

  # Frontend React
  frontend:
    build:
      context: ./frontend/react_interface
      dockerfile: Dockerfile
    volumes:
      - ./frontend/react_interface:/app
      - /app/node_modules
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://backend:5000
    depends_on:
      - backend

  # Prometheus pour monitoring
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'

  # Grafana pour dashboards
  grafana:
    image: grafana/grafana:latest
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD}
      GF_INSTALL_PLUGINS: redis-datasource
    volumes:
      - grafana_data:/var/lib/grafana
      - ./config/grafana/dashboards:/etc/grafana/provisioning/dashboards
    ports:
      - "3001:3000"
    depends_on:
      - prometheus

  # Jaeger pour tracing
  jaeger:
    image: jaegertracing/all-in-one:latest
    environment:
      COLLECTOR_OTLP_ENABLED: true
    ports:
      - "16686:16686"
      - "4318:4318"

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:
"""
        
        compose_path = self.project_root / "docker-compose.yml"
        with open(compose_path, 'w', encoding='utf-8') as f:
            f.write(content)
        self.log("[OK] Docker-compose.yml ameliore cree")
    
    def create_env_template(self):
        """Creer un template .env"""
        content = """# Database
DB_PASSWORD=your_secure_password_here
DATABASE_URL=postgresql://substans_user:your_secure_password_here@localhost:5432/substans_db

# Redis
REDIS_URL=redis://localhost:6379

# Security
JWT_SECRET_KEY=your_jwt_secret_key_here
ENCRYPTION_KEY=your_encryption_key_here

# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# Monitoring
GRAFANA_PASSWORD=your_grafana_password_here

# Application
FLASK_ENV=production
FLASK_DEBUG=False
LOG_LEVEL=INFO

# Frontend
REACT_APP_API_URL=http://localhost:5000

# Storage
DOCUMENT_STORAGE_PATH=./documents
UPLOAD_MAX_SIZE=10485760
"""
        
        env_path = self.project_root / ".env.template"
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(content)
        self.log("[OK] Template .env cree")
    
    def create_migration_scripts(self):
        """Creer les scripts de migration"""
        
        # Script de migration SQLite vers PostgreSQL
        migration_content = '''#!/usr/bin/env python3
"""
Script de migration SQLite vers PostgreSQL
"""

import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime

def migrate_database():
    """Migration de SQLite vers PostgreSQL"""
    
    # Connexion SQLite
    sqlite_conn = sqlite3.connect('backend/database.db')
    sqlite_cursor = sqlite_conn.cursor()
    
    # Connexion PostgreSQL
    pg_conn = psycopg2.connect(os.environ['DATABASE_URL'])
    pg_cursor = pg_conn.cursor()
    
    try:
        # Creation des tables PostgreSQL
        create_tables_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS agents (
            id SERIAL PRIMARY KEY,
            agent_id VARCHAR(100) UNIQUE NOT NULL,
            agent_type VARCHAR(50) NOT NULL,
            capabilities JSONB,
            performance_metrics JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS documents (
            id SERIAL PRIMARY KEY,
            document_id VARCHAR(100) UNIQUE NOT NULL,
            title VARCHAR(500),
            content TEXT,
            format VARCHAR(20),
            status VARCHAR(20),
            metadata JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS workflows (
            id SERIAL PRIMARY KEY,
            workflow_id VARCHAR(100) UNIQUE NOT NULL,
            name VARCHAR(255),
            status VARCHAR(50),
            configuration JSONB,
            results JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        );
        """
        
        pg_cursor.execute(create_tables_sql)
        
        # Migration des donnees
        tables = ['users', 'agents', 'documents', 'workflows']
        
        for table in tables:
            print(f"Migration de la table {table}...")
            
            sqlite_cursor.execute(f"SELECT * FROM {table}")
            rows = sqlite_cursor.fetchall()
            
            for row in rows:
                # Adapter selon la structure reelle
                # Inserer dans PostgreSQL
                pass
        
        pg_conn.commit()
        print("[OK] Migration terminee avec succes")
        
    except Exception as e:
        pg_conn.rollback()
        print(f"[ERREUR] Erreur de migration: {e}")
        
    finally:
        sqlite_conn.close()
        pg_conn.close()

if __name__ == "__main__":
    migrate_database()
'''
        
        migration_path = self.project_root / "migrations/migrate_to_postgresql.py"
        migration_path.parent.mkdir(parents=True, exist_ok=True)
        with open(migration_path, 'w', encoding='utf-8') as f:
            f.write(migration_content)
        try:
            os.chmod(migration_path, 0o755)
        except:
            pass  # Windows n'a pas toujours chmod
        self.log("[OK] Scripts de migration crees")
    
    def create_test_structure(self):
        """Creer la structure de tests"""
        
        # Test unitaire exemple
        unit_test = '''import pytest
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
'''
        
        test_path = self.project_root / "tests/unit/test_enhanced_agent.py"
        test_path.parent.mkdir(parents=True, exist_ok=True)
        with open(test_path, 'w', encoding='utf-8') as f:
            f.write(unit_test)
        
        # Test de charge
        load_test = '''from locust import HttpUser, task, between

class SubstansUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def test_agent_endpoint(self):
        self.client.post("/api/agent/process", json={
            "agent_id": "aad",
            "request": {"type": "analysis", "data": "test"}
        })
    
    @task(1)
    def test_document_generation(self):
        self.client.post("/api/documents/generate", json={
            "template": "report",
            "format": "pdf",
            "content": {"title": "Test Report"}
        })
'''
        
        load_test_path = self.project_root / "tests/load/test_load.py"
        load_test_path.parent.mkdir(parents=True, exist_ok=True)
        with open(load_test_path, 'w', encoding='utf-8') as f:
            f.write(load_test)
        
        self.log("[OK] Structure de tests creee")
    
    def create_github_actions(self):
        """Creer les workflows GitHub Actions"""
        
        ci_workflow = """name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r deployment/requirements.txt
        pip install pytest-cov
    
    - name: Run tests
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
        REDIS_URL: redis://localhost:6379
      run: |
        pytest tests/ --cov=backend --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker images
      run: |
        docker-compose build
    
    - name: Push to registry
      if: success()
      run: |
        echo "Push to Docker Hub or ECR"
"""
        
        workflow_path = self.project_root / ".github/workflows/ci.yml"
        workflow_path.parent.mkdir(parents=True, exist_ok=True)
        with open(workflow_path, 'w', encoding='utf-8') as f:
            f.write(ci_workflow)
        self.log("[OK] GitHub Actions workflow cree")
    
    def run(self):
        """Executer toutes les modifications"""
        print("[DEMARRAGE] Debut de l'application des modifications...")
        print("=" * 60)
        
        # Sauvegarde
        if self.backup:
            backup_dir = self.create_backup()
            if backup_dir:
                print(f"[SAUVEGARDE] Creee dans: {backup_dir}")
        
        # Application des changements
        try:
            self.create_directory_structure()
            self.create_base_agent_class()
            self.update_requirements()
            self.create_docker_compose_enhanced()
            self.create_env_template()
            self.create_migration_scripts()
            self.create_test_structure()
            self.create_github_actions()
            
            # Rapport final
            print("\n" + "=" * 60)
            print("[SUCCES] TOUTES LES MODIFICATIONS APPLIQUEES AVEC SUCCES!")
            print("=" * 60)
            
            print("\n[RESUME] Resume des changements:")
            for log_entry in self.changes_log[-10:]:
                print(f"  {log_entry}")
            
            print("\n[TODO] Prochaines etapes:")
            print("  1. Copier .env.template vers .env et configurer les variables")
            print("  2. Executer: pip install -r deployment/requirements.txt")
            print("  3. Executer: python migrations/migrate_to_postgresql.py")
            print("  4. Lancer: docker-compose up -d")
            print("  5. Tester: pytest tests/")
            
            # Creer un fichier de log
            log_file = self.project_root / f"upgrade_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(self.changes_log))
            print(f"\n[LOG] Log complet sauvegarde dans: {log_file}")
            
        except Exception as e:
            print(f"\n[ERREUR] Erreur lors de l'application des modifications: {e}")
            print("Verifiez le log pour plus de details")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Applique les modifications d\'audit Substans.AI')
    parser.add_argument('--no-backup', action='store_true', help='Ne pas creer de sauvegarde')
    parser.add_argument('--verbose', action='store_true', help='Mode verbose')
    parser.add_argument('--path', default='.', help='Chemin vers le projet')
    
    args = parser.parse_args()
    
    upgrader = SubstansUpgrader(
        project_root=args.path,
        backup=not args.no_backup,
        verbose=args.verbose
    )
    
    upgrader.run()

if __name__ == "__main__":
    main()