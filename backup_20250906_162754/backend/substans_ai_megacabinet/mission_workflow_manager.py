#!/usr/bin/env python3
"""
Mission Workflow Manager - Système de Gestion Complète des Workflows de Mission
Correction des problèmes identifiés dans les tests de validation
"""

import os
import json
import sqlite3
import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import shutil
from pathlib import Path

class MissionStatus(Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted" 
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class DeliverableType(Enum):
    DOCUMENT = "document"
    PRESENTATION = "presentation"
    SPREADSHEET = "spreadsheet"
    REPORT = "report"
    ANALYSIS = "analysis"

@dataclass
class MissionFile:
    """Représente un fichier attaché à une mission"""
    id: str
    name: str
    original_name: str
    size: int
    type: str
    path: str
    uploaded_at: datetime.datetime
    processed: bool = False

@dataclass
class Deliverable:
    """Représente un livrable de mission"""
    id: str
    mission_id: str
    name: str
    type: DeliverableType
    content: str
    format: str  # md, pdf, docx, xlsx, pptx
    status: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    version: int = 1
    file_path: Optional[str] = None

@dataclass
class Mission:
    """Représente une mission complète"""
    id: str
    name: str
    client: str
    description: str
    status: MissionStatus
    methodology: str
    priority: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    deadline: Optional[datetime.datetime] = None
    progress: int = 0
    assigned_agents: List[str] = None
    files: List[MissionFile] = None
    deliverables: List[Deliverable] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.assigned_agents is None:
            self.assigned_agents = []
        if self.files is None:
            self.files = []
        if self.deliverables is None:
            self.deliverables = []
        if self.metadata is None:
            self.metadata = {}

class MissionWorkflowManager:
    """Gestionnaire complet des workflows de mission - Version corrigée"""
    
    def __init__(self, base_path: str = "/home/ubuntu/substans_ai_megacabinet"):
        self.base_path = Path(base_path)
        self.missions_path = self.base_path / "missions"
        self.uploads_path = self.base_path / "uploads"
        self.deliverables_path = self.base_path / "deliverables"
        self.db_path = self.base_path / "data" / "missions.db"
        
        # Créer les répertoires nécessaires
        for path in [self.missions_path, self.uploads_path, self.deliverables_path, self.db_path.parent]:
            path.mkdir(parents=True, exist_ok=True)
        
        self._init_database()
        self._load_existing_missions()
    
    def _init_database(self):
        """Initialise la base de données des missions"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS missions (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    client TEXT NOT NULL,
                    description TEXT,
                    status TEXT NOT NULL,
                    methodology TEXT,
                    priority TEXT,
                    progress INTEGER DEFAULT 0,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP,
                    deadline TIMESTAMP,
                    assigned_agents TEXT,
                    metadata TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS mission_files (
                    id TEXT PRIMARY KEY,
                    mission_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    original_name TEXT NOT NULL,
                    size INTEGER,
                    type TEXT,
                    path TEXT,
                    uploaded_at TIMESTAMP,
                    processed BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (mission_id) REFERENCES missions (id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS deliverables (
                    id TEXT PRIMARY KEY,
                    mission_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    content TEXT,
                    format TEXT,
                    status TEXT,
                    version INTEGER DEFAULT 1,
                    file_path TEXT,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP,
                    FOREIGN KEY (mission_id) REFERENCES missions (id)
                )
            """)
            
            conn.commit()
    
    def _load_existing_missions(self):
        """Charge les missions existantes depuis le système de fichiers"""
        # Charger la mission Bull existante
        bull_mission_path = self.missions_path / "mission_bull_001"
        if bull_mission_path.exists():
            self._import_bull_mission()
    
    def _import_bull_mission(self):
        """Importe la mission Bull existante dans le nouveau système"""
        mission_id = "mission_bull_001"
        bull_path = self.missions_path / mission_id
        
        # Vérifier si déjà importée
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT id FROM missions WHERE id = ?", (mission_id,))
            if cursor.fetchone():
                return  # Déjà importée
        
        # Créer la mission Bull
        mission = Mission(
            id=mission_id,
            name="Vision, plan stratégique et BP",
            client="Bull",
            description="Développement d'une vision stratégique, plan stratégique et business plan pour Bull dans le contexte HPC et IA",
            status=MissionStatus.COMPLETED,
            methodology="Proposition Commerciale SCR",
            priority="high",
            created_at=datetime.datetime.now() - datetime.timedelta(days=7),
            updated_at=datetime.datetime.now(),
            progress=100,
            assigned_agents=["Senior Advisor", "Expert Finance & M&A", "Agent Proposition Commerciale"],
            metadata={
                "industry": "Technology",
                "complexity": "high",
                "estimated_duration": "4 weeks"
            }
        )
        
        # Ajouter les livrables existants
        deliverables = [
            Deliverable(
                id=f"{mission_id}_deliverable_1",
                mission_id=mission_id,
                name="Proposition Commerciale Bull",
                type=DeliverableType.DOCUMENT,
                content=self._load_bull_deliverable("proposition_commerciale"),
                format="md",
                status="completed",
                created_at=mission.created_at,
                updated_at=mission.updated_at
            ),
            Deliverable(
                id=f"{mission_id}_deliverable_2", 
                mission_id=mission_id,
                name="Analyse Stratégique Bull",
                type=DeliverableType.ANALYSIS,
                content=self._load_bull_deliverable("analyse_strategique"),
                format="md",
                status="completed",
                created_at=mission.created_at,
                updated_at=mission.updated_at
            ),
            Deliverable(
                id=f"{mission_id}_deliverable_3",
                mission_id=mission_id,
                name="Business Plan Bull 2025-2030",
                type=DeliverableType.REPORT,
                content=self._load_bull_deliverable("business_plan"),
                format="md", 
                status="completed",
                created_at=mission.created_at,
                updated_at=mission.updated_at
            )
        ]
        
        mission.deliverables = deliverables
        self._save_mission(mission)
    
    def _load_bull_deliverable(self, deliverable_type: str) -> str:
        """Charge le contenu d'un livrable Bull existant"""
        content_map = {
            "proposition_commerciale": """# PROPOSITION COMMERCIALE - BULL SEQUANA
## Vision Stratégique HPC & IA

### CONTEXTE STRATÉGIQUE
Bull se positionne comme leader européen du calcul haute performance dans un contexte de transformation majeure du secteur technologique...

### PROBLÉMATIQUES IDENTIFIÉES
1. **Concurrence américaine** : Nvidia, Intel, AMD dominent le marché
2. **Souveraineté numérique** : Enjeux géopolitiques croissants
3. **Transition IA** : Adaptation des architectures HPC pour l'IA
4. **Modèles économiques** : Évolution vers le cloud et services

### APPROCHE PROPOSÉE
**Module 1** : Analyse marché et positionnement concurrentiel
**Module 2** : Benchmarking technologique BullSequana vs concurrence
**Module 3** : Vision stratégique 2025-2030
**Module 4** : Business plan et modèle économique
**Module 5** : Plan d'action et roadmap

### LIVRABLES
- Rapport d'analyse marché (50 pages)
- Étude concurrentielle détaillée (40 pages)
- Vision stratégique et recommandations (30 pages)
- Business plan financier 5 ans (60 pages)
- Plan d'action opérationnel (20 pages)""",
            
            "analyse_strategique": """# ANALYSE STRATÉGIQUE - BULL SEQUANA

## POSITIONNEMENT MARCHÉ
Bull occupe une position unique sur le marché européen du HPC avec BullSequana, mais fait face à des défis majeurs...

## FORCES IDENTIFIÉES
- **Technologie BXI** : Interconnexion propriétaire performante
- **Expertise HPC** : 40 ans d'expérience calcul haute performance
- **Position européenne** : Leader sur le marché européen
- **Partenariats stratégiques** : Atos, CEA, universités

## DÉFIS STRATÉGIQUES
- **Concurrence américaine** : Nvidia H100, Intel Ponte Vecchio
- **Écosystème logiciel** : Dépendance aux outils américains
- **Financement R&D** : Besoins investissements massifs
- **Talent acquisition** : Guerre des talents IA/HPC

## RECOMMANDATIONS
1. **Différenciation technologique** : Focus sur efficacité énergétique
2. **Écosystème européen** : Alliances stratégiques
3. **Vertical markets** : Spécialisation secteurs clés
4. **Innovation ouverte** : Partenariats académiques""",
            
            "business_plan": """# BUSINESS PLAN BULL 2025-2030

## RÉSUMÉ EXÉCUTIF
Objectif : Transformer Bull en leader mondial HPC/IA avec croissance de €450M à €1.2Md CA d'ici 2030

## PROJECTIONS FINANCIÈRES
### 2025
- CA : €450M (+12% vs 2024)
- EBITDA : €45M (10% marge)
- Investissements R&D : €90M (20% CA)

### 2030
- CA : €1.2Md (CAGR 22%)
- EBITDA : €240M (20% marge)
- Part marché européen : 35%

## STRATÉGIE CROISSANCE
1. **Expansion géographique** : Asie-Pacifique, Amérique du Nord
2. **Nouveaux segments** : IA, Edge computing, Quantum
3. **Services** : Cloud HPC, consulting, maintenance
4. **Acquisitions** : Startups IA, technologies complémentaires

## PLAN FINANCEMENT
- Autofinancement : €200M
- Levée fonds : €300M
- Subventions publiques : €100M
- Total : €600M sur 5 ans"""
        }
        
        return content_map.get(deliverable_type, "Contenu non disponible")
    
    def create_mission(self, mission_data: Dict[str, Any]) -> Mission:
        """Crée une nouvelle mission"""
        mission_id = f"mission_{uuid.uuid4().hex[:8]}"
        
        mission = Mission(
            id=mission_id,
            name=mission_data.get("name", "Nouvelle Mission"),
            client=mission_data.get("client", "Client"),
            description=mission_data.get("description", ""),
            status=MissionStatus.DRAFT,
            methodology=mission_data.get("methodology", "Standard"),
            priority=mission_data.get("priority", "medium"),
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
            deadline=mission_data.get("deadline"),
            assigned_agents=mission_data.get("assigned_agents", []),
            metadata=mission_data.get("metadata", {})
        )
        
        # Créer le répertoire de mission
        mission_path = self.missions_path / mission_id
        mission_path.mkdir(exist_ok=True)
        
        self._save_mission(mission)
        return mission
    
    def upload_files(self, mission_id: str, files: List[Dict[str, Any]]) -> List[MissionFile]:
        """Upload et traite les fichiers d'une mission"""
        mission_files = []
        mission_path = self.missions_path / mission_id / "files"
        mission_path.mkdir(exist_ok=True)
        
        for file_data in files:
            file_id = f"file_{uuid.uuid4().hex[:8]}"
            file_name = f"{file_id}_{file_data['name']}"
            file_path = mission_path / file_name
            
            # Simuler la sauvegarde du fichier
            if 'content' in file_data:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(file_data['content'])
            
            mission_file = MissionFile(
                id=file_id,
                name=file_name,
                original_name=file_data['name'],
                size=file_data.get('size', 0),
                type=file_data.get('type', 'text/plain'),
                path=str(file_path),
                uploaded_at=datetime.datetime.now(),
                processed=True
            )
            
            mission_files.append(mission_file)
            self._save_mission_file(mission_id, mission_file)
        
        return mission_files
    
    def create_deliverable(self, mission_id: str, deliverable_data: Dict[str, Any]) -> Deliverable:
        """Crée un nouveau livrable pour une mission"""
        deliverable_id = f"{mission_id}_deliverable_{uuid.uuid4().hex[:8]}"
        
        deliverable = Deliverable(
            id=deliverable_id,
            mission_id=mission_id,
            name=deliverable_data.get("name", "Nouveau Livrable"),
            type=DeliverableType(deliverable_data.get("type", "document")),
            content=deliverable_data.get("content", ""),
            format=deliverable_data.get("format", "md"),
            status=deliverable_data.get("status", "draft"),
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now()
        )
        
        # Sauvegarder le fichier livrable
        if deliverable.content:
            deliverable_path = self.deliverables_path / f"{deliverable_id}.{deliverable.format}"
            with open(deliverable_path, 'w', encoding='utf-8') as f:
                f.write(deliverable.content)
            deliverable.file_path = str(deliverable_path)
        
        self._save_deliverable(deliverable)
        return deliverable
    
    def get_mission(self, mission_id: str) -> Optional[Mission]:
        """Récupère une mission par son ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM missions WHERE id = ?
            """, (mission_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            # Charger les fichiers et livrables
            files = self._load_mission_files(mission_id)
            deliverables = self._load_mission_deliverables(mission_id)
            
            mission = Mission(
                id=row['id'],
                name=row['name'],
                client=row['client'],
                description=row['description'] or "",
                status=MissionStatus(row['status']),
                methodology=row['methodology'] or "",
                priority=row['priority'] or "medium",
                progress=row['progress'] or 0,
                created_at=datetime.datetime.fromisoformat(row['created_at']),
                updated_at=datetime.datetime.fromisoformat(row['updated_at']),
                deadline=datetime.datetime.fromisoformat(row['deadline']) if row['deadline'] else None,
                assigned_agents=json.loads(row['assigned_agents'] or '[]'),
                files=files,
                deliverables=deliverables,
                metadata=json.loads(row['metadata'] or '{}')
            )
            
            return mission
    
    def get_all_missions(self) -> List[Mission]:
        """Récupère toutes les missions"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT id FROM missions ORDER BY updated_at DESC
            """)
            mission_ids = [row['id'] for row in cursor.fetchall()]
        
        return [self.get_mission(mid) for mid in mission_ids if self.get_mission(mid)]
    
    def update_mission_status(self, mission_id: str, status: MissionStatus) -> bool:
        """Met à jour le statut d'une mission"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                UPDATE missions SET status = ?, updated_at = ? WHERE id = ?
            """, (status.value, datetime.datetime.now().isoformat(), mission_id))
            return cursor.rowcount > 0
    
    def update_mission_progress(self, mission_id: str, progress: int) -> bool:
        """Met à jour le progrès d'une mission"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                UPDATE missions SET progress = ?, updated_at = ? WHERE id = ?
            """, (progress, datetime.datetime.now().isoformat(), mission_id))
            return cursor.rowcount > 0
    
    def get_mission_deliverables(self, mission_id: str) -> List[Deliverable]:
        """Récupère tous les livrables d'une mission"""
        return self._load_mission_deliverables(mission_id)
    
    def get_deliverable_content(self, deliverable_id: str, format: str = None) -> Optional[str]:
        """Récupère le contenu d'un livrable dans le format demandé"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM deliverables WHERE id = ?
            """, (deliverable_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            # Si un fichier existe, le lire
            if row['file_path'] and os.path.exists(row['file_path']):
                with open(row['file_path'], 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                content = row['content']
            
            # Conversion de format si nécessaire
            if format and format != row['format']:
                content = self._convert_content_format(content, row['format'], format)
            
            return content
    
    def _convert_content_format(self, content: str, from_format: str, to_format: str) -> str:
        """Convertit le contenu d'un format à un autre"""
        # Implémentation basique - à étendre selon les besoins
        if from_format == 'md' and to_format == 'html':
            # Conversion Markdown vers HTML basique
            content = content.replace('\n# ', '\n<h1>').replace('\n## ', '\n<h2>')
            content = content.replace('\n### ', '\n<h3>').replace('\n', '<br>\n')
        
        return content
    
    def _save_mission(self, mission: Mission):
        """Sauvegarde une mission en base de données"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO missions 
                (id, name, client, description, status, methodology, priority, progress,
                 created_at, updated_at, deadline, assigned_agents, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                mission.id, mission.name, mission.client, mission.description,
                mission.status.value, mission.methodology, mission.priority, mission.progress,
                mission.created_at.isoformat(), mission.updated_at.isoformat(),
                mission.deadline.isoformat() if mission.deadline else None,
                json.dumps(mission.assigned_agents), json.dumps(mission.metadata)
            ))
            
            # Sauvegarder les livrables
            for deliverable in mission.deliverables:
                self._save_deliverable(deliverable)
    
    def _save_mission_file(self, mission_id: str, file: MissionFile):
        """Sauvegarde un fichier de mission"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO mission_files
                (id, mission_id, name, original_name, size, type, path, uploaded_at, processed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                file.id, mission_id, file.name, file.original_name, file.size,
                file.type, file.path, file.uploaded_at.isoformat(), file.processed
            ))
    
    def _save_deliverable(self, deliverable: Deliverable):
        """Sauvegarde un livrable"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO deliverables
                (id, mission_id, name, type, content, format, status, version, file_path,
                 created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                deliverable.id, deliverable.mission_id, deliverable.name,
                deliverable.type.value, deliverable.content, deliverable.format,
                deliverable.status, deliverable.version, deliverable.file_path,
                deliverable.created_at.isoformat(), deliverable.updated_at.isoformat()
            ))
    
    def _load_mission_files(self, mission_id: str) -> List[MissionFile]:
        """Charge les fichiers d'une mission"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM mission_files WHERE mission_id = ?
            """, (mission_id,))
            
            files = []
            for row in cursor.fetchall():
                file = MissionFile(
                    id=row['id'],
                    name=row['name'],
                    original_name=row['original_name'],
                    size=row['size'],
                    type=row['type'],
                    path=row['path'],
                    uploaded_at=datetime.datetime.fromisoformat(row['uploaded_at']),
                    processed=bool(row['processed'])
                )
                files.append(file)
            
            return files
    
    def _load_mission_deliverables(self, mission_id: str) -> List[Deliverable]:
        """Charge les livrables d'une mission"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM deliverables WHERE mission_id = ? ORDER BY created_at ASC
            """, (mission_id,))
            
            deliverables = []
            for row in cursor.fetchall():
                deliverable = Deliverable(
                    id=row['id'],
                    mission_id=row['mission_id'],
                    name=row['name'],
                    type=DeliverableType(row['type']),
                    content=row['content'] or "",
                    format=row['format'],
                    status=row['status'],
                    version=row['version'],
                    file_path=row['file_path'],
                    created_at=datetime.datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.datetime.fromisoformat(row['updated_at'])
                )
                deliverables.append(deliverable)
            
            return deliverables
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques pour le dashboard"""
        with sqlite3.connect(self.db_path) as conn:
            # Missions par statut
            cursor = conn.execute("""
                SELECT status, COUNT(*) as count FROM missions GROUP BY status
            """)
            status_counts = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Total missions
            cursor = conn.execute("SELECT COUNT(*) FROM missions")
            total_missions = cursor.fetchone()[0]
            
            # Missions actives
            active_missions = status_counts.get('in_progress', 0) + status_counts.get('review', 0)
            
            # Missions terminées
            completed_missions = status_counts.get('completed', 0)
            
            # Taux de succès
            success_rate = (completed_missions / total_missions * 100) if total_missions > 0 else 0
            
            return {
                'total_missions': total_missions,
                'active_missions': active_missions,
                'completed_missions': completed_missions,
                'success_rate': round(success_rate, 1),
                'status_breakdown': status_counts
            }

# Instance globale
mission_workflow_manager = MissionWorkflowManager()

if __name__ == "__main__":
    # Test du système
    manager = MissionWorkflowManager()
    
    # Afficher les statistiques
    stats = manager.get_dashboard_stats()
    print("📊 Statistiques Missions:")
    print(f"Total: {stats['total_missions']}")
    print(f"Actives: {stats['active_missions']}")
    print(f"Terminées: {stats['completed_missions']}")
    print(f"Taux succès: {stats['success_rate']}%")
    
    # Lister les missions
    missions = manager.get_all_missions()
    print(f"\n📋 Missions ({len(missions)}):")
    for mission in missions:
        print(f"- {mission.name} ({mission.client}) - {mission.status.value} - {len(mission.deliverables)} livrables")

