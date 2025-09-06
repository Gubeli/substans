"""
Machine Learning Engine - Moteur d'Apprentissage Automatique
IA adaptative et prédictive pour la plateforme substans.ai
"""

import json
import logging
import numpy as np
import pandas as pd
import pickle
import os
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.feature_extraction.text import TfidfVectorizer
import warnings
warnings.filterwarnings('ignore')

# Configuration du logging
logging.basicConfig(level=logging.INFO)

class ModelType(Enum):
    """Types de modèles ML"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    RECOMMENDATION = "recommendation"
    PREDICTION = "prediction"
    OPTIMIZATION = "optimization"

class ModelStatus(Enum):
    """États des modèles"""
    TRAINING = "training"
    TRAINED = "trained"
    DEPLOYED = "deployed"
    RETRAINING = "retraining"
    DEPRECATED = "deprecated"
    FAILED = "failed"

@dataclass
class MLModel:
    """Modèle d'apprentissage automatique"""
    model_id: str
    name: str
    model_type: ModelType
    status: ModelStatus
    algorithm: str
    features: List[str]
    target: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    training_data_size: int
    created_at: datetime
    last_trained: datetime
    last_used: datetime
    usage_count: int
    model_path: str
    metadata: Dict[str, Any]

@dataclass
class Prediction:
    """Prédiction ML"""
    prediction_id: str
    model_id: str
    input_data: Dict[str, Any]
    prediction: Any
    confidence: float
    created_at: datetime
    execution_time: float

class MLEngine:
    """
    Moteur d'apprentissage automatique pour substans.ai
    IA adaptative avec apprentissage continu et optimisation des performances
    """
    
    def __init__(self, data_path: str = None):
        self.engine_id = str(uuid.uuid4())
        self.logger = logging.getLogger(f"MLEngine-{self.engine_id[:8]}")
        
        # Chemins de données
        self.data_path = data_path or '/home/ubuntu/substans_ai_megacabinet/data/ml_data'
        self.models_path = os.path.join(self.data_path, 'models')
        self.db_path = os.path.join(self.data_path, 'ml_engine.db')
        
        # Création des répertoires
        os.makedirs(self.data_path, exist_ok=True)
        os.makedirs(self.models_path, exist_ok=True)
        
        # Modèles chargés
        self.models = {}
        self.model_metadata = {}
        
        # Cache des prédictions
        self.prediction_cache = {}
        self.cache_ttl = 3600  # 1 heure
        
        # Données d'entraînement
        self.training_data = {}
        self.feature_extractors = {}
        
        # Métriques ML
        self.ml_metrics = {
            'models_trained': 0,
            'predictions_made': 0,
            'average_accuracy': 0.0,
            'average_response_time': 0.0,
            'cache_hit_rate': 0.0,
            'model_usage': {}
        }
        
        # Services
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.auto_retrain_enabled = True
        self.retrain_threshold = 0.1  # Seuil de dégradation pour re-entraînement
        
        # Base de données
        self._initialize_database()
        
        # Chargement des modèles existants
        self._load_existing_models()
        
        # Démarrage des services
        self._start_services()
        
        self.logger.info(f"ML Engine initialisé - ID: {self.engine_id}")

    def _initialize_database(self):
        """Initialise la base de données ML"""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Table des modèles
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ml_models (
                    model_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    model_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    algorithm TEXT NOT NULL,
                    features TEXT,
                    target TEXT,
                    accuracy REAL,
                    precision_score REAL,
                    recall_score REAL,
                    f1_score REAL,
                    training_data_size INTEGER,
                    created_at TIMESTAMP,
                    last_trained TIMESTAMP,
                    last_used TIMESTAMP,
                    usage_count INTEGER DEFAULT 0,
                    model_path TEXT,
                    metadata TEXT
                )
            ''')
            
            # Table des prédictions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS predictions (
                    prediction_id TEXT PRIMARY KEY,
                    model_id TEXT NOT NULL,
                    input_data TEXT,
                    prediction TEXT,
                    confidence REAL,
                    created_at TIMESTAMP,
                    execution_time REAL,
                    FOREIGN KEY (model_id) REFERENCES ml_models (model_id)
                )
            ''')
            
            # Table des données d'entraînement
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS training_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_id TEXT NOT NULL,
                    data_type TEXT NOT NULL,
                    features TEXT,
                    target TEXT,
                    created_at TIMESTAMP,
                    FOREIGN KEY (model_id) REFERENCES ml_models (model_id)
                )
            ''')
            
            # Table des métriques
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ml_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP,
                    models_trained INTEGER,
                    predictions_made INTEGER,
                    average_accuracy REAL,
                    average_response_time REAL,
                    cache_hit_rate REAL
                )
            ''')
            
            conn.commit()

    def _load_existing_models(self):
        """Charge les modèles existants"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM ml_models WHERE status = "deployed"')
                
                for row in cursor.fetchall():
                    model_data = dict(zip([col[0] for col in cursor.description], row))
                    
                    try:
                        # Chargement du modèle depuis le fichier
                        model_path = model_data['model_path']
                        if os.path.exists(model_path):
                            with open(model_path, 'rb') as f:
                                model = pickle.load(f)
                            
                            self.models[model_data['model_id']] = model
                            
                            # Reconstruction des métadonnées
                            metadata = json.loads(model_data['metadata']) if model_data['metadata'] else {}
                            
                            ml_model = MLModel(
                                model_id=model_data['model_id'],
                                name=model_data['name'],
                                model_type=ModelType(model_data['model_type']),
                                status=ModelStatus(model_data['status']),
                                algorithm=model_data['algorithm'],
                                features=json.loads(model_data['features']) if model_data['features'] else [],
                                target=model_data['target'],
                                accuracy=model_data['accuracy'] or 0.0,
                                precision=model_data['precision_score'] or 0.0,
                                recall=model_data['recall_score'] or 0.0,
                                f1_score=model_data['f1_score'] or 0.0,
                                training_data_size=model_data['training_data_size'] or 0,
                                created_at=datetime.fromisoformat(model_data['created_at']),
                                last_trained=datetime.fromisoformat(model_data['last_trained']),
                                last_used=datetime.fromisoformat(model_data['last_used']) if model_data['last_used'] else datetime.now(),
                                usage_count=model_data['usage_count'] or 0,
                                model_path=model_path,
                                metadata=metadata
                            )
                            
                            self.model_metadata[model_data['model_id']] = ml_model
                            
                            self.logger.info(f"Modèle {model_data['name']} chargé")
                    
                    except Exception as e:
                        self.logger.error(f"Erreur chargement modèle {model_data['name']}: {e}")
            
            self.logger.info(f"{len(self.models)} modèles chargés")
            
        except Exception as e:
            self.logger.error(f"Erreur chargement modèles: {e}")

    def _start_services(self):
        """Démarre les services ML"""
        
        # Service de re-entraînement automatique
        threading.Thread(target=self._auto_retrain_service, daemon=True).start()
        
        # Service de nettoyage du cache
        threading.Thread(target=self._cache_cleanup_service, daemon=True).start()
        
        # Service de métriques
        threading.Thread(target=self._metrics_service, daemon=True).start()

    def create_model(self, name: str, model_type: ModelType, algorithm: str,
                    features: List[str], target: str = None,
                    hyperparameters: Dict[str, Any] = None) -> str:
        """Crée un nouveau modèle ML"""
        
        model_id = str(uuid.uuid4())
        
        # Configuration du modèle selon l'algorithme
        if algorithm == 'random_forest_classifier':
            model = RandomForestClassifier(**(hyperparameters or {}))
        elif algorithm == 'random_forest_regressor':
            model = RandomForestRegressor(**(hyperparameters or {}))
        elif algorithm == 'kmeans':
            model = KMeans(**(hyperparameters or {}))
        else:
            raise ValueError(f"Algorithme non supporté: {algorithm}")
        
        # Métadonnées du modèle
        ml_model = MLModel(
            model_id=model_id,
            name=name,
            model_type=model_type,
            status=ModelStatus.TRAINING,
            algorithm=algorithm,
            features=features,
            target=target,
            accuracy=0.0,
            precision=0.0,
            recall=0.0,
            f1_score=0.0,
            training_data_size=0,
            created_at=datetime.now(),
            last_trained=datetime.now(),
            last_used=datetime.now(),
            usage_count=0,
            model_path=os.path.join(self.models_path, f"{model_id}.pkl"),
            metadata=hyperparameters or {}
        )
        
        self.models[model_id] = model
        self.model_metadata[model_id] = ml_model
        
        # Sauvegarde en base
        self._save_model_metadata(ml_model)
        
        self.logger.info(f"Modèle {name} créé - ID: {model_id}")
        
        return model_id

    def train_model(self, model_id: str, training_data: pd.DataFrame,
                   validation_split: float = 0.2) -> Dict[str, Any]:
        """Entraîne un modèle ML"""
        
        if model_id not in self.models:
            raise ValueError(f"Modèle {model_id} non trouvé")
        
        model = self.models[model_id]
        ml_model = self.model_metadata[model_id]
        
        self.logger.info(f"Entraînement du modèle {ml_model.name}")
        
        start_time = time.time()
        
        try:
            # Préparation des données
            X = training_data[ml_model.features]
            
            if ml_model.model_type in [ModelType.CLASSIFICATION, ModelType.REGRESSION]:
                y = training_data[ml_model.target]
                
                # Division train/validation
                X_train, X_val, y_train, y_val = train_test_split(
                    X, y, test_size=validation_split, random_state=42
                )
                
                # Entraînement
                model.fit(X_train, y_train)
                
                # Évaluation
                y_pred = model.predict(X_val)
                
                if ml_model.model_type == ModelType.CLASSIFICATION:
                    accuracy = accuracy_score(y_val, y_pred)
                    precision = precision_score(y_val, y_pred, average='weighted')
                    recall = recall_score(y_val, y_pred, average='weighted')
                    f1 = f1_score(y_val, y_pred, average='weighted')
                else:
                    # Métriques pour régression
                    from sklearn.metrics import mean_squared_error, r2_score
                    mse = mean_squared_error(y_val, y_pred)
                    r2 = r2_score(y_val, y_pred)
                    accuracy = r2
                    precision = 1 / (1 + mse)
                    recall = precision
                    f1 = precision
                
            elif ml_model.model_type == ModelType.CLUSTERING:
                # Entraînement clustering
                model.fit(X)
                
                # Métriques clustering
                from sklearn.metrics import silhouette_score
                labels = model.labels_
                accuracy = silhouette_score(X, labels)
                precision = accuracy
                recall = accuracy
                f1 = accuracy
            
            # Mise à jour des métriques
            ml_model.accuracy = accuracy
            ml_model.precision = precision
            ml_model.recall = recall
            ml_model.f1_score = f1
            ml_model.training_data_size = len(training_data)
            ml_model.last_trained = datetime.now()
            ml_model.status = ModelStatus.TRAINED
            
            # Sauvegarde du modèle
            with open(ml_model.model_path, 'wb') as f:
                pickle.dump(model, f)
            
            # Sauvegarde des métadonnées
            self._save_model_metadata(ml_model)
            
            # Sauvegarde des données d'entraînement
            self._save_training_data(model_id, training_data)
            
            training_time = time.time() - start_time
            
            self.ml_metrics['models_trained'] += 1
            
            result = {
                'model_id': model_id,
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'training_time': training_time,
                'training_data_size': len(training_data)
            }
            
            self.logger.info(f"Modèle {ml_model.name} entraîné - Accuracy: {accuracy:.3f}")
            
            return result
            
        except Exception as e:
            ml_model.status = ModelStatus.FAILED
            self._save_model_metadata(ml_model)
            self.logger.error(f"Erreur entraînement modèle {ml_model.name}: {e}")
            raise

    def predict(self, model_id: str, input_data: Dict[str, Any],
               use_cache: bool = True) -> Prediction:
        """Effectue une prédiction"""
        
        if model_id not in self.models:
            raise ValueError(f"Modèle {model_id} non trouvé")
        
        # Vérification du cache
        cache_key = f"{model_id}_{hash(str(sorted(input_data.items())))}"
        
        if use_cache and cache_key in self.prediction_cache:
            cache_entry = self.prediction_cache[cache_key]
            if time.time() - cache_entry['timestamp'] < self.cache_ttl:
                self.ml_metrics['cache_hit_rate'] = (
                    self.ml_metrics.get('cache_hit_rate', 0) * 0.9 + 0.1
                )
                return cache_entry['prediction']
        
        model = self.models[model_id]
        ml_model = self.model_metadata[model_id]
        
        start_time = time.time()
        
        try:
            # Préparation des données d'entrée
            input_df = pd.DataFrame([input_data])
            X = input_df[ml_model.features]
            
            # Prédiction
            if ml_model.model_type == ModelType.CLASSIFICATION:
                prediction = model.predict(X)[0]
                confidence = max(model.predict_proba(X)[0])
            elif ml_model.model_type == ModelType.REGRESSION:
                prediction = model.predict(X)[0]
                confidence = 0.8  # Confidence par défaut pour régression
            elif ml_model.model_type == ModelType.CLUSTERING:
                prediction = model.predict(X)[0]
                confidence = 0.7  # Confidence par défaut pour clustering
            else:
                prediction = model.predict(X)[0]
                confidence = 0.5
            
            execution_time = time.time() - start_time
            
            # Création de l'objet prédiction
            prediction_obj = Prediction(
                prediction_id=str(uuid.uuid4()),
                model_id=model_id,
                input_data=input_data,
                prediction=prediction,
                confidence=confidence,
                created_at=datetime.now(),
                execution_time=execution_time
            )
            
            # Mise à jour des statistiques
            ml_model.last_used = datetime.now()
            ml_model.usage_count += 1
            self.ml_metrics['predictions_made'] += 1
            
            # Mise à jour du temps de réponse moyen
            current_avg = self.ml_metrics.get('average_response_time', 0)
            self.ml_metrics['average_response_time'] = (
                current_avg * 0.9 + execution_time * 0.1
            )
            
            # Cache de la prédiction
            if use_cache:
                self.prediction_cache[cache_key] = {
                    'prediction': prediction_obj,
                    'timestamp': time.time()
                }
            
            # Sauvegarde de la prédiction
            self._save_prediction(prediction_obj)
            
            # Mise à jour des métadonnées du modèle
            self._save_model_metadata(ml_model)
            
            return prediction_obj
            
        except Exception as e:
            self.logger.error(f"Erreur prédiction modèle {ml_model.name}: {e}")
            raise

    def batch_predict(self, model_id: str, input_data_list: List[Dict[str, Any]]) -> List[Prediction]:
        """Effectue des prédictions en lot"""
        
        predictions = []
        
        for input_data in input_data_list:
            try:
                prediction = self.predict(model_id, input_data)
                predictions.append(prediction)
            except Exception as e:
                self.logger.error(f"Erreur prédiction batch: {e}")
        
        return predictions

    def recommend_agents(self, mission_context: Dict[str, Any], top_k: int = 5) -> List[Dict[str, Any]]:
        """Recommande les meilleurs agents pour une mission"""
        
        # Modèle de recommandation d'agents
        model_id = self._get_or_create_agent_recommendation_model()
        
        try:
            # Extraction des features de la mission
            features = self._extract_mission_features(mission_context)
            
            # Prédiction
            prediction = self.predict(model_id, features)
            
            # Conversion en recommandations
            recommendations = self._convert_to_agent_recommendations(
                prediction.prediction, top_k
            )
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Erreur recommandation agents: {e}")
            return []

    def optimize_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimise un workflow basé sur l'historique"""
        
        # Modèle d'optimisation de workflow
        model_id = self._get_or_create_workflow_optimization_model()
        
        try:
            # Extraction des features du workflow
            features = self._extract_workflow_features(workflow_data)
            
            # Prédiction des optimisations
            prediction = self.predict(model_id, features)
            
            # Conversion en recommandations d'optimisation
            optimizations = self._convert_to_workflow_optimizations(prediction.prediction)
            
            return optimizations
            
        except Exception as e:
            self.logger.error(f"Erreur optimisation workflow: {e}")
            return {}

    def predict_mission_success(self, mission_data: Dict[str, Any]) -> float:
        """Prédit la probabilité de succès d'une mission"""
        
        # Modèle de prédiction de succès
        model_id = self._get_or_create_success_prediction_model()
        
        try:
            # Extraction des features de la mission
            features = self._extract_mission_success_features(mission_data)
            
            # Prédiction
            prediction = self.predict(model_id, features)
            
            return float(prediction.prediction)
            
        except Exception as e:
            self.logger.error(f"Erreur prédiction succès mission: {e}")
            return 0.5

    def analyze_performance_trends(self, agent_id: str = None) -> Dict[str, Any]:
        """Analyse les tendances de performance"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Requête pour les données de performance
                if agent_id:
                    cursor.execute('''
                        SELECT created_at, confidence, execution_time
                        FROM predictions p
                        JOIN ml_models m ON p.model_id = m.model_id
                        WHERE m.metadata LIKE ?
                        ORDER BY created_at DESC
                        LIMIT 1000
                    ''', (f'%{agent_id}%',))
                else:
                    cursor.execute('''
                        SELECT created_at, confidence, execution_time
                        FROM predictions
                        ORDER BY created_at DESC
                        LIMIT 1000
                    ''')
                
                data = cursor.fetchall()
                
                if not data:
                    return {'trend': 'stable', 'confidence': 0.5}
                
                # Analyse des tendances
                df = pd.DataFrame(data, columns=['timestamp', 'confidence', 'execution_time'])
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                
                # Calcul des tendances
                recent_confidence = df.head(100)['confidence'].mean()
                older_confidence = df.tail(100)['confidence'].mean()
                
                recent_time = df.head(100)['execution_time'].mean()
                older_time = df.tail(100)['execution_time'].mean()
                
                confidence_trend = 'improving' if recent_confidence > older_confidence else 'declining'
                performance_trend = 'improving' if recent_time < older_time else 'declining'
                
                return {
                    'confidence_trend': confidence_trend,
                    'performance_trend': performance_trend,
                    'recent_confidence': recent_confidence,
                    'recent_execution_time': recent_time,
                    'data_points': len(data)
                }
                
        except Exception as e:
            self.logger.error(f"Erreur analyse tendances: {e}")
            return {'trend': 'unknown', 'confidence': 0.5}

    def _get_or_create_agent_recommendation_model(self) -> str:
        """Obtient ou crée le modèle de recommandation d'agents"""
        
        # Recherche d'un modèle existant
        for model_id, ml_model in self.model_metadata.items():
            if ml_model.name == 'agent_recommendation':
                return model_id
        
        # Création d'un nouveau modèle
        model_id = self.create_model(
            name='agent_recommendation',
            model_type=ModelType.RECOMMENDATION,
            algorithm='random_forest_classifier',
            features=['sector', 'complexity', 'urgency', 'budget', 'expertise_required'],
            target='best_agent'
        )
        
        # Entraînement avec des données simulées
        training_data = self._generate_agent_recommendation_training_data()
        self.train_model(model_id, training_data)
        
        return model_id

    def _get_or_create_workflow_optimization_model(self) -> str:
        """Obtient ou crée le modèle d'optimisation de workflow"""
        
        # Recherche d'un modèle existant
        for model_id, ml_model in self.model_metadata.items():
            if ml_model.name == 'workflow_optimization':
                return model_id
        
        # Création d'un nouveau modèle
        model_id = self.create_model(
            name='workflow_optimization',
            model_type=ModelType.OPTIMIZATION,
            algorithm='random_forest_regressor',
            features=['nodes_count', 'parallel_ratio', 'complexity', 'data_size'],
            target='execution_time'
        )
        
        # Entraînement avec des données simulées
        training_data = self._generate_workflow_optimization_training_data()
        self.train_model(model_id, training_data)
        
        return model_id

    def _get_or_create_success_prediction_model(self) -> str:
        """Obtient ou crée le modèle de prédiction de succès"""
        
        # Recherche d'un modèle existant
        for model_id, ml_model in self.model_metadata.items():
            if ml_model.name == 'success_prediction':
                return model_id
        
        # Création d'un nouveau modèle
        model_id = self.create_model(
            name='success_prediction',
            model_type=ModelType.PREDICTION,
            algorithm='random_forest_classifier',
            features=['budget', 'timeline', 'complexity', 'team_size', 'experience'],
            target='success_probability'
        )
        
        # Entraînement avec des données simulées
        training_data = self._generate_success_prediction_training_data()
        self.train_model(model_id, training_data)
        
        return model_id

    def _generate_agent_recommendation_training_data(self) -> pd.DataFrame:
        """Génère des données d'entraînement pour la recommandation d'agents"""
        
        np.random.seed(42)
        n_samples = 1000
        
        data = {
            'sector': np.random.choice(['tech', 'finance', 'healthcare', 'energy'], n_samples),
            'complexity': np.random.uniform(1, 10, n_samples),
            'urgency': np.random.uniform(1, 5, n_samples),
            'budget': np.random.uniform(10000, 1000000, n_samples),
            'expertise_required': np.random.choice(['junior', 'senior', 'expert'], n_samples),
            'best_agent': np.random.choice(['efs', 'eia', 'ec', 'ess', 'ebf'], n_samples)
        }
        
        return pd.DataFrame(data)

    def _generate_workflow_optimization_training_data(self) -> pd.DataFrame:
        """Génère des données d'entraînement pour l'optimisation de workflow"""
        
        np.random.seed(42)
        n_samples = 1000
        
        data = {
            'nodes_count': np.random.randint(3, 20, n_samples),
            'parallel_ratio': np.random.uniform(0, 1, n_samples),
            'complexity': np.random.uniform(1, 10, n_samples),
            'data_size': np.random.uniform(100, 10000, n_samples),
            'execution_time': np.random.uniform(60, 3600, n_samples)
        }
        
        return pd.DataFrame(data)

    def _generate_success_prediction_training_data(self) -> pd.DataFrame:
        """Génère des données d'entraînement pour la prédiction de succès"""
        
        np.random.seed(42)
        n_samples = 1000
        
        data = {
            'budget': np.random.uniform(10000, 1000000, n_samples),
            'timeline': np.random.uniform(1, 52, n_samples),  # semaines
            'complexity': np.random.uniform(1, 10, n_samples),
            'team_size': np.random.randint(1, 20, n_samples),
            'experience': np.random.uniform(1, 10, n_samples),
            'success_probability': np.random.uniform(0, 1, n_samples)
        }
        
        return pd.DataFrame(data)

    def _extract_mission_features(self, mission_context: Dict[str, Any]) -> Dict[str, Any]:
        """Extrait les features d'une mission"""
        
        return {
            'sector': mission_context.get('sector', 'tech'),
            'complexity': mission_context.get('complexity', 5),
            'urgency': mission_context.get('urgency', 3),
            'budget': mission_context.get('budget', 100000),
            'expertise_required': mission_context.get('expertise_required', 'senior')
        }

    def _extract_workflow_features(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrait les features d'un workflow"""
        
        return {
            'nodes_count': workflow_data.get('nodes_count', 5),
            'parallel_ratio': workflow_data.get('parallel_ratio', 0.3),
            'complexity': workflow_data.get('complexity', 5),
            'data_size': workflow_data.get('data_size', 1000)
        }

    def _extract_mission_success_features(self, mission_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrait les features pour la prédiction de succès"""
        
        return {
            'budget': mission_data.get('budget', 100000),
            'timeline': mission_data.get('timeline', 12),
            'complexity': mission_data.get('complexity', 5),
            'team_size': mission_data.get('team_size', 5),
            'experience': mission_data.get('experience', 5)
        }

    def _convert_to_agent_recommendations(self, prediction: Any, top_k: int) -> List[Dict[str, Any]]:
        """Convertit une prédiction en recommandations d'agents"""
        
        # Simulation de recommandations
        agents = ['efs', 'eia', 'ec', 'ess', 'ebf', 'ea', 'avs', 'aad']
        
        recommendations = []
        for i, agent in enumerate(agents[:top_k]):
            recommendations.append({
                'agent_id': agent,
                'confidence': max(0.5, 1.0 - i * 0.1),
                'reason': f'Recommandé basé sur l\'analyse ML'
            })
        
        return recommendations

    def _convert_to_workflow_optimizations(self, prediction: Any) -> Dict[str, Any]:
        """Convertit une prédiction en optimisations de workflow"""
        
        return {
            'estimated_time': float(prediction),
            'optimizations': [
                'Augmenter le parallélisme',
                'Optimiser l\'ordre des tâches',
                'Réduire les dépendances'
            ]
        }

    def _save_model_metadata(self, ml_model: MLModel):
        """Sauvegarde les métadonnées d'un modèle"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO ml_models 
                    (model_id, name, model_type, status, algorithm, features, target,
                     accuracy, precision_score, recall_score, f1_score, training_data_size,
                     created_at, last_trained, last_used, usage_count, model_path, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    ml_model.model_id, ml_model.name, ml_model.model_type.value,
                    ml_model.status.value, ml_model.algorithm,
                    json.dumps(ml_model.features), ml_model.target,
                    ml_model.accuracy, ml_model.precision, ml_model.recall, ml_model.f1_score,
                    ml_model.training_data_size, ml_model.created_at, ml_model.last_trained,
                    ml_model.last_used, ml_model.usage_count, ml_model.model_path,
                    json.dumps(ml_model.metadata)
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde métadonnées modèle: {e}")

    def _save_prediction(self, prediction: Prediction):
        """Sauvegarde une prédiction"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO predictions 
                    (prediction_id, model_id, input_data, prediction, confidence, created_at, execution_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    prediction.prediction_id, prediction.model_id,
                    json.dumps(prediction.input_data), json.dumps(prediction.prediction),
                    prediction.confidence, prediction.created_at, prediction.execution_time
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde prédiction: {e}")

    def _save_training_data(self, model_id: str, training_data: pd.DataFrame):
        """Sauvegarde les données d'entraînement"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO training_data (model_id, data_type, features, target, created_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    model_id, 'dataframe',
                    json.dumps(training_data.columns.tolist()),
                    json.dumps(training_data.iloc[0].to_dict()),
                    datetime.now()
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde données entraînement: {e}")

    def _auto_retrain_service(self):
        """Service de re-entraînement automatique"""
        
        while True:
            try:
                if self.auto_retrain_enabled:
                    for model_id, ml_model in self.model_metadata.items():
                        # Vérification si le modèle nécessite un re-entraînement
                        if self._needs_retraining(ml_model):
                            self.logger.info(f"Re-entraînement automatique du modèle {ml_model.name}")
                            
                            # Re-entraînement en arrière-plan
                            self.executor.submit(self._retrain_model, model_id)
                
                time.sleep(3600)  # Vérification toutes les heures
                
            except Exception as e:
                self.logger.error(f"Erreur service re-entraînement: {e}")
                time.sleep(3600)

    def _needs_retraining(self, ml_model: MLModel) -> bool:
        """Détermine si un modèle nécessite un re-entraînement"""
        
        # Critères de re-entraînement
        days_since_training = (datetime.now() - ml_model.last_trained).days
        
        # Re-entraînement si:
        # - Plus de 30 jours depuis le dernier entraînement
        # - Accuracy en dessous du seuil
        # - Usage élevé (plus de 1000 prédictions)
        
        return (days_since_training > 30 or 
                ml_model.accuracy < (1 - self.retrain_threshold) or
                ml_model.usage_count > 1000)

    def _retrain_model(self, model_id: str):
        """Re-entraîne un modèle"""
        
        try:
            ml_model = self.model_metadata[model_id]
            ml_model.status = ModelStatus.RETRAINING
            
            # Génération de nouvelles données d'entraînement
            if ml_model.name == 'agent_recommendation':
                training_data = self._generate_agent_recommendation_training_data()
            elif ml_model.name == 'workflow_optimization':
                training_data = self._generate_workflow_optimization_training_data()
            elif ml_model.name == 'success_prediction':
                training_data = self._generate_success_prediction_training_data()
            else:
                return
            
            # Re-entraînement
            self.train_model(model_id, training_data)
            
            ml_model.status = ModelStatus.DEPLOYED
            self._save_model_metadata(ml_model)
            
            self.logger.info(f"Modèle {ml_model.name} re-entraîné avec succès")
            
        except Exception as e:
            self.logger.error(f"Erreur re-entraînement modèle {model_id}: {e}")

    def _cache_cleanup_service(self):
        """Service de nettoyage du cache"""
        
        while True:
            try:
                current_time = time.time()
                expired_keys = [
                    key for key, entry in self.prediction_cache.items()
                    if current_time - entry['timestamp'] > self.cache_ttl
                ]
                
                for key in expired_keys:
                    del self.prediction_cache[key]
                
                if expired_keys:
                    self.logger.info(f"{len(expired_keys)} entrées de cache supprimées")
                
                time.sleep(1800)  # Nettoyage toutes les 30 minutes
                
            except Exception as e:
                self.logger.error(f"Erreur service nettoyage cache: {e}")
                time.sleep(1800)

    def _metrics_service(self):
        """Service de collecte des métriques"""
        
        while True:
            try:
                # Calcul de l'accuracy moyenne
                if self.model_metadata:
                    accuracies = [m.accuracy for m in self.model_metadata.values() if m.accuracy > 0]
                    if accuracies:
                        self.ml_metrics['average_accuracy'] = sum(accuracies) / len(accuracies)
                
                # Sauvegarde des métriques
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO ml_metrics 
                        (timestamp, models_trained, predictions_made, average_accuracy, 
                         average_response_time, cache_hit_rate)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        datetime.now(),
                        self.ml_metrics['models_trained'],
                        self.ml_metrics['predictions_made'],
                        self.ml_metrics['average_accuracy'],
                        self.ml_metrics['average_response_time'],
                        self.ml_metrics['cache_hit_rate']
                    ))
                    conn.commit()
                
                time.sleep(300)  # Métriques toutes les 5 minutes
                
            except Exception as e:
                self.logger.error(f"Erreur service métriques: {e}")
                time.sleep(300)

    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Retourne les informations d'un modèle"""
        
        if model_id not in self.model_metadata:
            return None
        
        ml_model = self.model_metadata[model_id]
        
        return {
            'model_id': ml_model.model_id,
            'name': ml_model.name,
            'model_type': ml_model.model_type.value,
            'status': ml_model.status.value,
            'algorithm': ml_model.algorithm,
            'accuracy': ml_model.accuracy,
            'precision': ml_model.precision,
            'recall': ml_model.recall,
            'f1_score': ml_model.f1_score,
            'training_data_size': ml_model.training_data_size,
            'usage_count': ml_model.usage_count,
            'created_at': ml_model.created_at.isoformat(),
            'last_trained': ml_model.last_trained.isoformat(),
            'last_used': ml_model.last_used.isoformat()
        }

    def get_ml_metrics(self) -> Dict[str, Any]:
        """Retourne les métriques ML"""
        
        return self.ml_metrics.copy()

    def list_models(self) -> List[Dict[str, Any]]:
        """Liste tous les modèles"""
        
        return [self.get_model_info(model_id) for model_id in self.model_metadata.keys()]

# Instance globale
_ml_engine = None

def get_ml_engine() -> MLEngine:
    """Retourne l'instance du moteur ML"""
    global _ml_engine
    if _ml_engine is None:
        _ml_engine = MLEngine()
    return _ml_engine

# Test du moteur ML
if __name__ == '__main__':
    print("=== Test ML Engine ===")
    
    ml_engine = MLEngine()
    
    # Test de création de modèle
    model_id = ml_engine.create_model(
        name='test_model',
        model_type=ModelType.CLASSIFICATION,
        algorithm='random_forest_classifier',
        features=['feature1', 'feature2', 'feature3'],
        target='target'
    )
    
    print(f"Modèle créé: {model_id}")
    
    # Test d'entraînement
    training_data = pd.DataFrame({
        'feature1': np.random.rand(100),
        'feature2': np.random.rand(100),
        'feature3': np.random.rand(100),
        'target': np.random.choice([0, 1], 100)
    })
    
    result = ml_engine.train_model(model_id, training_data)
    print(f"Entraînement terminé - Accuracy: {result['accuracy']:.3f}")
    
    # Test de prédiction
    prediction = ml_engine.predict(model_id, {
        'feature1': 0.5,
        'feature2': 0.3,
        'feature3': 0.8
    })
    
    print(f"Prédiction: {prediction.prediction} (Confidence: {prediction.confidence:.3f})")
    
    # Test de recommandation d'agents
    recommendations = ml_engine.recommend_agents({
        'sector': 'tech',
        'complexity': 7,
        'budget': 500000
    })
    
    print(f"Recommandations: {len(recommendations)} agents")
    
    print("Test terminé avec succès")

