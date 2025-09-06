"""
Knowledge Base Sémantique - Base de Connaissances Intelligente
Système de gestion des connaissances avec IA sémantique et recherche cognitive
"""

import json
import logging
import numpy as np
import os
import pickle
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.decomposition import LatentDirichletAllocation
import networkx as nx
import re
from collections import defaultdict, Counter
import hashlib

# Configuration du logging
logging.basicConfig(level=logging.INFO)

class KnowledgeType(Enum):
    """Types de connaissances"""
    DOCUMENT = "document"
    EXPERTISE = "expertise"
    METHODOLOGY = "methodology"
    CASE_STUDY = "case_study"
    BEST_PRACTICE = "best_practice"
    LESSON_LEARNED = "lesson_learned"
    TEMPLATE = "template"
    REFERENCE = "reference"

class ContentFormat(Enum):
    """Formats de contenu"""
    TEXT = "text"
    MARKDOWN = "markdown"
    JSON = "json"
    PDF = "pdf"
    WORD = "word"
    EXCEL = "excel"
    IMAGE = "image"
    VIDEO = "video"

class AccessLevel(Enum):
    """Niveaux d'accès"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"

@dataclass
class KnowledgeItem:
    """Élément de connaissance"""
    item_id: str
    title: str
    content: str
    knowledge_type: KnowledgeType
    content_format: ContentFormat
    access_level: AccessLevel
    tags: List[str]
    categories: List[str]
    author: str
    source: str
    created_at: datetime
    updated_at: datetime
    version: int
    language: str
    quality_score: float
    usage_count: int
    metadata: Dict[str, Any]

@dataclass
class SemanticRelation:
    """Relation sémantique entre éléments"""
    relation_id: str
    source_id: str
    target_id: str
    relation_type: str
    strength: float
    confidence: float
    created_at: datetime
    metadata: Dict[str, Any]

@dataclass
class SearchResult:
    """Résultat de recherche"""
    item_id: str
    title: str
    content_preview: str
    relevance_score: float
    semantic_score: float
    combined_score: float
    knowledge_type: KnowledgeType
    tags: List[str]
    categories: List[str]
    metadata: Dict[str, Any]

class KnowledgeBaseSemantic:
    """
    Base de connaissances sémantique avec IA cognitive
    Gestion intelligente des connaissances avec recherche sémantique avancée
    """
    
    def __init__(self, data_path: str = None):
        self.kb_id = str(uuid.uuid4())
        self.logger = logging.getLogger(f"KnowledgeBaseSemantic-{self.kb_id[:8]}")
        
        # Chemins de données
        self.data_path = data_path or '/home/ubuntu/substans_ai_megacabinet/data/knowledge_base'
        self.models_path = os.path.join(self.data_path, 'semantic_models')
        self.db_path = os.path.join(self.data_path, 'knowledge_base.db')
        
        # Création des répertoires
        os.makedirs(self.data_path, exist_ok=True)
        os.makedirs(self.models_path, exist_ok=True)
        
        # Éléments de connaissance
        self.knowledge_items = {}
        self.semantic_relations = {}
        
        # Modèles sémantiques
        self.tfidf_vectorizer = None
        self.document_vectors = None
        self.topic_model = None
        self.knowledge_graph = nx.Graph()
        
        # Cache de recherche
        self.search_cache = {}
        self.cache_ttl = 1800  # 30 minutes
        
        # Statistiques
        self.kb_stats = {
            'total_items': 0,
            'total_relations': 0,
            'total_searches': 0,
            'cache_hits': 0,
            'average_quality_score': 0.0,
            'most_used_tags': [],
            'most_accessed_items': []
        }
        
        # Services
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.indexing_enabled = True
        
        # Base de données
        self._initialize_database()
        
        # Chargement des données existantes
        self._load_existing_knowledge()
        
        # Démarrage des services
        self._start_services()
        
        self.logger.info(f"Knowledge Base Sémantique initialisée - ID: {self.kb_id}")

    def _initialize_database(self):
        """Initialise la base de données de la KB"""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Table des éléments de connaissance
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS knowledge_items (
                    item_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    knowledge_type TEXT NOT NULL,
                    content_format TEXT NOT NULL,
                    access_level TEXT NOT NULL,
                    tags TEXT,
                    categories TEXT,
                    author TEXT,
                    source TEXT,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    version INTEGER DEFAULT 1,
                    language TEXT DEFAULT 'fr',
                    quality_score REAL DEFAULT 0.0,
                    usage_count INTEGER DEFAULT 0,
                    metadata TEXT
                )
            ''')
            
            # Index pour la recherche
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_knowledge_title 
                ON knowledge_items(title)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_knowledge_type 
                ON knowledge_items(knowledge_type)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_knowledge_tags 
                ON knowledge_items(tags)
            ''')
            
            # Table des relations sémantiques
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS semantic_relations (
                    relation_id TEXT PRIMARY KEY,
                    source_id TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    relation_type TEXT NOT NULL,
                    strength REAL NOT NULL,
                    confidence REAL NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    metadata TEXT,
                    FOREIGN KEY (source_id) REFERENCES knowledge_items (item_id),
                    FOREIGN KEY (target_id) REFERENCES knowledge_items (item_id)
                )
            ''')
            
            # Table des recherches
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS search_history (
                    search_id TEXT PRIMARY KEY,
                    query TEXT NOT NULL,
                    filters TEXT,
                    results_count INTEGER,
                    execution_time REAL,
                    user_id TEXT,
                    timestamp TIMESTAMP NOT NULL
                )
            ''')
            
            # Table des évaluations de qualité
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quality_evaluations (
                    evaluation_id TEXT PRIMARY KEY,
                    item_id TEXT NOT NULL,
                    evaluator TEXT,
                    quality_score REAL NOT NULL,
                    feedback TEXT,
                    timestamp TIMESTAMP NOT NULL,
                    FOREIGN KEY (item_id) REFERENCES knowledge_items (item_id)
                )
            ''')
            
            # Table des statistiques
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS kb_statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP NOT NULL,
                    total_items INTEGER,
                    total_relations INTEGER,
                    total_searches INTEGER,
                    cache_hits INTEGER,
                    average_quality_score REAL
                )
            ''')
            
            conn.commit()

    def add_knowledge(self, title: str, content: str, knowledge_type: KnowledgeType,
                     content_format: ContentFormat = ContentFormat.TEXT,
                     access_level: AccessLevel = AccessLevel.INTERNAL,
                     tags: List[str] = None, categories: List[str] = None,
                     author: str = 'system', source: str = '',
                     metadata: Dict[str, Any] = None) -> str:
        """Ajoute un élément de connaissance"""
        
        item_id = str(uuid.uuid4())
        
        # Calcul du score de qualité initial
        quality_score = self._calculate_quality_score(content, tags or [], categories or [])
        
        knowledge_item = KnowledgeItem(
            item_id=item_id,
            title=title,
            content=content,
            knowledge_type=knowledge_type,
            content_format=content_format,
            access_level=access_level,
            tags=tags or [],
            categories=categories or [],
            author=author,
            source=source,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            version=1,
            language='fr',
            quality_score=quality_score,
            usage_count=0,
            metadata=metadata or {}
        )
        
        # Stockage
        self.knowledge_items[item_id] = knowledge_item
        
        # Sauvegarde en base
        self._save_knowledge_item(knowledge_item)
        
        # Mise à jour des statistiques
        self.kb_stats['total_items'] = len(self.knowledge_items)
        
        # Déclenchement de l'indexation
        if self.indexing_enabled:
            self.executor.submit(self._index_knowledge_item, item_id)
        
        self.logger.info(f"Connaissance ajoutée: {title} (ID: {item_id})")
        
        return item_id

    def search_knowledge(self, query: str, knowledge_types: List[KnowledgeType] = None,
                        tags: List[str] = None, categories: List[str] = None,
                        access_level: AccessLevel = None, limit: int = 20,
                        semantic_search: bool = True, user_id: str = None) -> List[SearchResult]:
        """Recherche dans la base de connaissances"""
        
        start_time = time.time()
        
        # Vérification du cache
        cache_key = self._generate_cache_key(query, knowledge_types, tags, categories, access_level, limit)
        
        if cache_key in self.search_cache:
            cache_entry = self.search_cache[cache_key]
            if time.time() - cache_entry['timestamp'] < self.cache_ttl:
                self.kb_stats['cache_hits'] += 1
                return cache_entry['results']
        
        # Recherche textuelle de base
        text_results = self._text_search(query, knowledge_types, tags, categories, access_level)
        
        # Recherche sémantique si activée
        if semantic_search and self.tfidf_vectorizer is not None:
            semantic_results = self._semantic_search(query, knowledge_types, tags, categories, access_level)
            
            # Fusion des résultats
            results = self._merge_search_results(text_results, semantic_results)
        else:
            results = text_results
        
        # Tri par score combiné et limitation
        results.sort(key=lambda x: x.combined_score, reverse=True)
        results = results[:limit]
        
        # Mise à jour des statistiques d'usage
        for result in results:
            if result.item_id in self.knowledge_items:
                self.knowledge_items[result.item_id].usage_count += 1
        
        execution_time = time.time() - start_time
        
        # Cache des résultats
        self.search_cache[cache_key] = {
            'results': results,
            'timestamp': time.time()
        }
        
        # Sauvegarde de la recherche
        self._save_search_history(query, knowledge_types, tags, categories, len(results), execution_time, user_id)
        
        # Mise à jour des statistiques
        self.kb_stats['total_searches'] += 1
        
        self.logger.info(f"Recherche '{query}': {len(results)} résultats en {execution_time:.3f}s")
        
        return results

    def _text_search(self, query: str, knowledge_types: List[KnowledgeType] = None,
                    tags: List[str] = None, categories: List[str] = None,
                    access_level: AccessLevel = None) -> List[SearchResult]:
        """Recherche textuelle de base"""
        
        results = []
        query_lower = query.lower()
        query_words = set(re.findall(r'\w+', query_lower))
        
        for item_id, item in self.knowledge_items.items():
            # Filtres
            if knowledge_types and item.knowledge_type not in knowledge_types:
                continue
            if access_level and item.access_level != access_level:
                continue
            if tags and not any(tag in item.tags for tag in tags):
                continue
            if categories and not any(cat in item.categories for cat in categories):
                continue
            
            # Calcul du score de pertinence textuelle
            title_lower = item.title.lower()
            content_lower = item.content.lower()
            
            # Score basé sur la présence des mots
            title_words = set(re.findall(r'\w+', title_lower))
            content_words = set(re.findall(r'\w+', content_lower))
            
            title_matches = len(query_words.intersection(title_words))
            content_matches = len(query_words.intersection(content_words))
            
            if title_matches > 0 or content_matches > 0:
                # Score pondéré (titre plus important)
                relevance_score = (title_matches * 3 + content_matches) / len(query_words)
                relevance_score = min(relevance_score, 1.0)
                
                # Bonus pour correspondance exacte
                if query_lower in title_lower:
                    relevance_score += 0.5
                elif query_lower in content_lower:
                    relevance_score += 0.2
                
                # Prévisualisation du contenu
                content_preview = self._generate_content_preview(item.content, query_words)
                
                result = SearchResult(
                    item_id=item_id,
                    title=item.title,
                    content_preview=content_preview,
                    relevance_score=relevance_score,
                    semantic_score=0.0,
                    combined_score=relevance_score,
                    knowledge_type=item.knowledge_type,
                    tags=item.tags,
                    categories=item.categories,
                    metadata=item.metadata
                )
                
                results.append(result)
        
        return results

    def _semantic_search(self, query: str, knowledge_types: List[KnowledgeType] = None,
                        tags: List[str] = None, categories: List[str] = None,
                        access_level: AccessLevel = None) -> List[SearchResult]:
        """Recherche sémantique avancée"""
        
        if self.tfidf_vectorizer is None or self.document_vectors is None:
            return []
        
        results = []
        
        try:
            # Vectorisation de la requête
            query_vector = self.tfidf_vectorizer.transform([query])
            
            # Calcul des similarités cosinus
            similarities = cosine_similarity(query_vector, self.document_vectors).flatten()
            
            # Récupération des indices triés par similarité
            sorted_indices = np.argsort(similarities)[::-1]
            
            item_ids = list(self.knowledge_items.keys())
            
            for idx in sorted_indices:
                if similarities[idx] < 0.1:  # Seuil minimum
                    break
                
                if idx >= len(item_ids):
                    continue
                
                item_id = item_ids[idx]
                item = self.knowledge_items[item_id]
                
                # Filtres
                if knowledge_types and item.knowledge_type not in knowledge_types:
                    continue
                if access_level and item.access_level != access_level:
                    continue
                if tags and not any(tag in item.tags for tag in tags):
                    continue
                if categories and not any(cat in item.categories for cat in categories):
                    continue
                
                semantic_score = float(similarities[idx])
                
                # Prévisualisation du contenu
                content_preview = self._generate_content_preview(item.content, set(query.lower().split()))
                
                result = SearchResult(
                    item_id=item_id,
                    title=item.title,
                    content_preview=content_preview,
                    relevance_score=0.0,
                    semantic_score=semantic_score,
                    combined_score=semantic_score,
                    knowledge_type=item.knowledge_type,
                    tags=item.tags,
                    categories=item.categories,
                    metadata=item.metadata
                )
                
                results.append(result)
        
        except Exception as e:
            self.logger.error(f"Erreur recherche sémantique: {e}")
        
        return results

    def _calculate_quality_score(self, content: str, tags: List[str], categories: List[str]) -> float:
        """Calcule le score de qualité d'un contenu"""
        
        score = 0.0
        
        # Longueur du contenu
        content_length = len(content)
        if content_length > 1000:
            score += 0.3
        elif content_length > 500:
            score += 0.2
        elif content_length > 100:
            score += 0.1
        
        # Présence de tags
        if tags:
            score += min(len(tags) * 0.1, 0.3)
        
        # Présence de catégories
        if categories:
            score += min(len(categories) * 0.1, 0.2)
        
        # Structure du contenu (présence de titres, listes, etc.)
        if re.search(r'#{1,6}\s', content):  # Titres markdown
            score += 0.1
        if re.search(r'^\s*[-*+]\s', content, re.MULTILINE):  # Listes
            score += 0.1
        if re.search(r'https?://', content):  # Liens
            score += 0.1
        
        return min(score, 1.0)

    def _generate_content_preview(self, content: str, query_words: Set[str], max_length: int = 200) -> str:
        """Génère une prévisualisation du contenu avec mise en évidence"""
        
        # Recherche du meilleur passage
        sentences = re.split(r'[.!?]+', content)
        best_sentence = ""
        best_score = 0
        
        for sentence in sentences:
            sentence_words = set(re.findall(r'\w+', sentence.lower()))
            score = len(query_words.intersection(sentence_words))
            
            if score > best_score:
                best_score = score
                best_sentence = sentence.strip()
        
        # Si aucune phrase pertinente, prendre le début
        if not best_sentence:
            best_sentence = content[:max_length]
        
        # Limitation de la longueur
        if len(best_sentence) > max_length:
            best_sentence = best_sentence[:max_length] + "..."
        
        return best_sentence

    def _generate_cache_key(self, query: str, knowledge_types: List[KnowledgeType] = None,
                           tags: List[str] = None, categories: List[str] = None,
                           access_level: AccessLevel = None, limit: int = 20) -> str:
        """Génère une clé de cache pour la recherche"""
        
        key_data = {
            'query': query,
            'knowledge_types': [kt.value for kt in knowledge_types] if knowledge_types else None,
            'tags': sorted(tags) if tags else None,
            'categories': sorted(categories) if categories else None,
            'access_level': access_level.value if access_level else None,
            'limit': limit
        }
        
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()

    def _save_knowledge_item(self, item: KnowledgeItem):
        """Sauvegarde un élément de connaissance"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO knowledge_items 
                    (item_id, title, content, knowledge_type, content_format, access_level,
                     tags, categories, author, source, created_at, updated_at, version,
                     language, quality_score, usage_count, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item.item_id, item.title, item.content, item.knowledge_type.value,
                    item.content_format.value, item.access_level.value,
                    json.dumps(item.tags), json.dumps(item.categories),
                    item.author, item.source, item.created_at, item.updated_at,
                    item.version, item.language, item.quality_score,
                    item.usage_count, json.dumps(item.metadata)
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde élément: {e}")

    def _save_search_history(self, query: str, knowledge_types: List[KnowledgeType] = None,
                            tags: List[str] = None, categories: List[str] = None,
                            results_count: int = 0, execution_time: float = 0.0,
                            user_id: str = None):
        """Sauvegarde l'historique de recherche"""
        
        try:
            search_id = str(uuid.uuid4())
            filters = {
                'knowledge_types': [kt.value for kt in knowledge_types] if knowledge_types else None,
                'tags': tags,
                'categories': categories
            }
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO search_history 
                    (search_id, query, filters, results_count, execution_time, user_id, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    search_id, query, json.dumps(filters), results_count,
                    execution_time, user_id, datetime.now()
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde recherche: {e}")

    def _indexing_service(self):
        """Service d'indexation automatique"""
        
        while True:
            try:
                if self.indexing_enabled and len(self.knowledge_items) > 0:
                    self._rebuild_semantic_models()
                
                time.sleep(3600)  # Re-indexation toutes les heures
                
            except Exception as e:
                self.logger.error(f"Erreur service indexation: {e}")
                time.sleep(3600)

    def _cache_cleanup_service(self):
        """Service de nettoyage du cache"""
        
        while True:
            try:
                current_time = time.time()
                expired_keys = [
                    key for key, entry in self.search_cache.items()
                    if current_time - entry['timestamp'] > self.cache_ttl
                ]
                
                for key in expired_keys:
                    del self.search_cache[key]
                
                if expired_keys:
                    self.logger.info(f"{len(expired_keys)} entrées de cache supprimées")
                
                time.sleep(1800)  # Nettoyage toutes les 30 minutes
                
            except Exception as e:
                self.logger.error(f"Erreur service nettoyage cache: {e}")
                time.sleep(1800)

    def _statistics_service(self):
        """Service de collecte des statistiques"""
        
        while True:
            try:
                # Calcul des statistiques
                if self.knowledge_items:
                    quality_scores = [item.quality_score for item in self.knowledge_items.values()]
                    self.kb_stats['average_quality_score'] = sum(quality_scores) / len(quality_scores)
                
                # Tags les plus utilisés
                tag_counter = Counter()
                for item in self.knowledge_items.values():
                    tag_counter.update(item.tags)
                
                self.kb_stats['most_used_tags'] = [tag for tag, count in tag_counter.most_common(10)]
                
                # Éléments les plus consultés
                most_accessed = sorted(
                    self.knowledge_items.values(),
                    key=lambda x: x.usage_count,
                    reverse=True
                )[:10]
                
                self.kb_stats['most_accessed_items'] = [
                    {'id': item.item_id, 'title': item.title, 'usage_count': item.usage_count}
                    for item in most_accessed
                ]
                
                # Sauvegarde des statistiques
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO kb_statistics 
                        (timestamp, total_items, total_relations, total_searches, 
                         cache_hits, average_quality_score)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        datetime.now(),
                        self.kb_stats['total_items'],
                        self.kb_stats['total_relations'],
                        self.kb_stats['total_searches'],
                        self.kb_stats['cache_hits'],
                        self.kb_stats['average_quality_score']
                    ))
                    conn.commit()
                
                time.sleep(300)  # Statistiques toutes les 5 minutes
                
            except Exception as e:
                self.logger.error(f"Erreur service statistiques: {e}")
                time.sleep(300)

    def _rebuild_semantic_models(self):
        """Reconstruit les modèles sémantiques"""
        
        try:
            if not self.knowledge_items:
                return
            
            # Préparation des documents
            documents = [item.content for item in self.knowledge_items.values()]
            
            # Vectorisation TF-IDF
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=5000,
                stop_words='english',  # À adapter pour le français
                ngram_range=(1, 2)
            )
            
            self.document_vectors = self.tfidf_vectorizer.fit_transform(documents)
            
            # Sauvegarde des modèles
            models_data = {
                'tfidf_vectorizer': self.tfidf_vectorizer,
                'document_vectors': self.document_vectors
            }
            
            with open(os.path.join(self.models_path, 'semantic_models.pkl'), 'wb') as f:
                pickle.dump(models_data, f)
            
            self.logger.info("Modèles sémantiques reconstruits")
            
        except Exception as e:
            self.logger.error(f"Erreur reconstruction modèles sémantiques: {e}")

    def get_knowledge_item(self, item_id: str) -> Optional[KnowledgeItem]:
        """Récupère un élément de connaissance"""
        
        return self.knowledge_items.get(item_id)

    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques de la KB"""
        
        return self.kb_stats.copy()

    def list_knowledge_items(self, knowledge_type: KnowledgeType = None,
                            limit: int = 100) -> List[Dict[str, Any]]:
        """Liste les éléments de connaissance"""
        
        items = []
        
        for item in self.knowledge_items.values():
            if knowledge_type and item.knowledge_type != knowledge_type:
                continue
            
            items.append({
                'item_id': item.item_id,
                'title': item.title,
                'knowledge_type': item.knowledge_type.value,
                'tags': item.tags,
                'categories': item.categories,
                'author': item.author,
                'created_at': item.created_at.isoformat(),
                'quality_score': item.quality_score,
                'usage_count': item.usage_count
            })
            
            if len(items) >= limit:
                break
        
        return items

# Instance globale
_knowledge_base = None

def get_knowledge_base() -> KnowledgeBaseSemantic:
    """Retourne l'instance de la base de connaissances"""
    global _knowledge_base
    if _knowledge_base is None:
        _knowledge_base = KnowledgeBaseSemantic()
    return _knowledge_base

# Test de la base de connaissances
if __name__ == '__main__':
    print("=== Test Knowledge Base Sémantique ===")
    
    kb = KnowledgeBaseSemantic()
    
    # Test d'ajout de connaissance
    item_id = kb.add_knowledge(
        title="Guide de développement Python",
        content="Python est un langage de programmation polyvalent. Il est utilisé pour le développement web, l'analyse de données, l'intelligence artificielle et l'automatisation.",
        knowledge_type=KnowledgeType.DOCUMENT,
        tags=["python", "programmation", "développement"],
        categories=["technique", "guide"]
    )
    
    print(f"Connaissance ajoutée: {item_id}")
    
    # Test de recherche
    results = kb.search_knowledge("python développement")
    print(f"Résultats de recherche: {len(results)}")
    
    if results:
        print(f"Premier résultat: {results[0].title}")
        print(f"Score: {results[0].combined_score:.3f}")
    
    # Test des statistiques
    stats = kb.get_statistics()
    print(f"Statistiques: {stats['total_items']} éléments")
    
    print("Test terminé avec succès")

