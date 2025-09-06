"""
Predictive Intelligence - Intelligence Prédictive Avancée
Système de prédiction et d'analyse prédictive avec ML pour le conseil
"""

import json
import logging
import numpy as np
import pandas as pd
import os
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report
from sklearn.cluster import KMeans
import joblib
import warnings
warnings.filterwarnings('ignore')

# Configuration du logging
logging.basicConfig(level=logging.INFO)

class PredictionType(Enum):
    """Types de prédictions"""
    PROJECT_SUCCESS = "project_success"
    DURATION_ESTIMATE = "duration_estimate"
    BUDGET_ESTIMATE = "budget_estimate"
    RISK_ASSESSMENT = "risk_assessment"
    RESOURCE_NEEDS = "resource_needs"
    CLIENT_SATISFACTION = "client_satisfaction"
    METHODOLOGY_PERFORMANCE = "methodology_performance"
    MARKET_TRENDS = "market_trends"
    COMPETITIVE_ANALYSIS = "competitive_analysis"
    BUSINESS_OPPORTUNITY = "business_opportunity"

class ModelType(Enum):
    """Types de modèles ML"""
    REGRESSION = "regression"
    CLASSIFICATION = "classification"
    CLUSTERING = "clustering"
    TIME_SERIES = "time_series"
    ENSEMBLE = "ensemble"

class ConfidenceLevel(Enum):
    """Niveaux de confiance"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

@dataclass
class PredictionRequest:
    """Demande de prédiction"""
    request_id: str
    prediction_type: PredictionType
    input_data: Dict[str, Any]
    context: Dict[str, Any]
    requested_at: datetime
    requester_id: str
    priority: int

@dataclass
class PredictionResult:
    """Résultat de prédiction"""
    prediction_id: str
    request_id: str
    prediction_type: PredictionType
    predicted_value: Any
    confidence_score: float
    confidence_level: ConfidenceLevel
    model_used: str
    feature_importance: Dict[str, float]
    prediction_interval: Tuple[float, float]
    metadata: Dict[str, Any]
    created_at: datetime
    expires_at: datetime

@dataclass
class ModelMetrics:
    """Métriques de modèle"""
    model_id: str
    model_type: ModelType
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    mse: float
    r2_score: float
    cross_val_score: float
    training_samples: int
    last_trained: datetime
    feature_count: int

@dataclass
class TrendAnalysis:
    """Analyse de tendances"""
    trend_id: str
    trend_name: str
    trend_type: str
    direction: str  # "increasing", "decreasing", "stable", "volatile"
    strength: float  # 0-1
    confidence: float  # 0-1
    time_horizon: int  # en jours
    key_factors: List[str]
    impact_assessment: Dict[str, float]
    recommendations: List[str]
    detected_at: datetime

class PredictiveIntelligence:
    """
    Système d'Intelligence Prédictive avec ML Avancé
    Prédictions et analyses prédictives pour le conseil stratégique
    """
    
    def __init__(self, data_path: str = None):
        self.system_id = str(uuid.uuid4())
        self.logger = logging.getLogger(f"PredictiveIntelligence-{self.system_id[:8]}")
        
        # Chemins de données
        self.data_path = data_path or '/home/ubuntu/substans_ai_megacabinet/data/predictive'
        self.models_path = os.path.join(self.data_path, 'ml_models')
        self.db_path = os.path.join(self.data_path, 'predictive.db')
        
        # Création des répertoires
        os.makedirs(self.data_path, exist_ok=True)
        os.makedirs(self.models_path, exist_ok=True)
        
        # Modèles ML
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.model_metrics = {}
        
        # Données d'entraînement
        self.training_data = {}
        self.feature_definitions = {}
        
        # Cache de prédictions
        self.prediction_cache = {}
        self.cache_ttl = 1800  # 30 minutes
        
        # Historique et tendances
        self.prediction_history = []
        self.trend_analyses = {}
        
        # Statistiques
        self.system_stats = {
            'total_predictions': 0,
            'successful_predictions': 0,
            'average_confidence': 0.0,
            'model_performance': {},
            'prediction_types_frequency': {},
            'trend_detection_count': 0
        }
        
        # Services
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.auto_retrain = True
        self.trend_detection_enabled = True
        
        # Base de données
        self._initialize_database()
        
        # Chargement des modèles existants
        self._load_existing_models()
        
        # Initialisation des données d'entraînement
        self._initialize_training_data()
        
        # Entraînement initial des modèles
        self._train_initial_models()
        
        # Démarrage des services
        self._start_services()
        
        self.logger.info(f"Intelligence Prédictive initialisée - ID: {self.system_id}")

    def _initialize_database(self):
        """Initialise la base de données"""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Table des demandes de prédiction
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS prediction_requests (
                    request_id TEXT PRIMARY KEY,
                    prediction_type TEXT NOT NULL,
                    input_data TEXT NOT NULL,
                    context TEXT,
                    requested_at TIMESTAMP NOT NULL,
                    requester_id TEXT,
                    priority INTEGER DEFAULT 1
                )
            ''')
            
            # Table des résultats de prédiction
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS prediction_results (
                    prediction_id TEXT PRIMARY KEY,
                    request_id TEXT NOT NULL,
                    prediction_type TEXT NOT NULL,
                    predicted_value TEXT NOT NULL,
                    confidence_score REAL NOT NULL,
                    confidence_level TEXT NOT NULL,
                    model_used TEXT NOT NULL,
                    feature_importance TEXT,
                    prediction_interval TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (request_id) REFERENCES prediction_requests (request_id)
                )
            ''')
            
            # Table des métriques de modèles
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS model_metrics (
                    model_id TEXT PRIMARY KEY,
                    model_type TEXT NOT NULL,
                    accuracy REAL,
                    precision REAL,
                    recall REAL,
                    f1_score REAL,
                    mse REAL,
                    r2_score REAL,
                    cross_val_score REAL,
                    training_samples INTEGER,
                    last_trained TIMESTAMP NOT NULL,
                    feature_count INTEGER
                )
            ''')
            
            # Table des analyses de tendances
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trend_analyses (
                    trend_id TEXT PRIMARY KEY,
                    trend_name TEXT NOT NULL,
                    trend_type TEXT NOT NULL,
                    direction TEXT NOT NULL,
                    strength REAL NOT NULL,
                    confidence REAL NOT NULL,
                    time_horizon INTEGER,
                    key_factors TEXT,
                    impact_assessment TEXT,
                    recommendations TEXT,
                    detected_at TIMESTAMP NOT NULL
                )
            ''')
            
            # Table des données d'entraînement
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS training_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prediction_type TEXT NOT NULL,
                    features TEXT NOT NULL,
                    target TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP NOT NULL
                )
            ''')
            
            # Index pour les performances
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_predictions_type 
                ON prediction_results(prediction_type)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_predictions_created 
                ON prediction_results(created_at)
            ''')
            
            conn.commit()

    def _initialize_training_data(self):
        """Initialise les données d'entraînement synthétiques"""
        
        # Définition des features pour chaque type de prédiction
        self.feature_definitions = {
            PredictionType.PROJECT_SUCCESS: [
                'team_size', 'budget_amount', 'timeline_days', 'complexity_score',
                'client_engagement', 'methodology_maturity', 'risk_factors_count',
                'stakeholder_count', 'industry_experience', 'team_experience'
            ],
            PredictionType.DURATION_ESTIMATE: [
                'scope_complexity', 'team_size', 'methodology_steps', 'dependencies_count',
                'resource_availability', 'client_responsiveness', 'change_requests_expected',
                'industry_type', 'project_type', 'historical_similar_duration'
            ],
            PredictionType.BUDGET_ESTIMATE: [
                'scope_size', 'team_composition', 'duration_estimate', 'complexity_level',
                'resource_costs', 'travel_requirements', 'technology_needs',
                'client_location', 'market_rates', 'competition_level'
            ],
            PredictionType.RISK_ASSESSMENT: [
                'project_complexity', 'client_stability', 'market_volatility', 'team_turnover',
                'technology_maturity', 'regulatory_changes', 'competitive_pressure',
                'budget_constraints', 'timeline_pressure', 'stakeholder_alignment'
            ]
        }
        
        # Génération de données d'entraînement synthétiques
        np.random.seed(42)
        
        for prediction_type, features in self.feature_definitions.items():
            training_samples = []
            
            for _ in range(1000):  # 1000 échantillons par type
                # Génération de features aléatoires
                feature_values = {}
                
                for feature in features:
                    if 'count' in feature or 'size' in feature:
                        feature_values[feature] = np.random.randint(1, 20)
                    elif 'score' in feature or 'level' in feature:
                        feature_values[feature] = np.random.uniform(0, 1)
                    elif 'amount' in feature or 'cost' in feature:
                        feature_values[feature] = np.random.uniform(10000, 500000)
                    elif 'days' in feature or 'duration' in feature:
                        feature_values[feature] = np.random.randint(10, 365)
                    else:
                        feature_values[feature] = np.random.uniform(0, 1)
                
                # Génération de target basée sur les features (logique simplifiée)
                if prediction_type == PredictionType.PROJECT_SUCCESS:
                    success_prob = (
                        feature_values['team_experience'] * 0.3 +
                        feature_values['client_engagement'] * 0.3 +
                        (1 - feature_values['complexity_score']) * 0.2 +
                        feature_values['methodology_maturity'] * 0.2
                    )
                    target = 1 if success_prob > 0.6 else 0
                
                elif prediction_type == PredictionType.DURATION_ESTIMATE:
                    base_duration = feature_values['methodology_steps'] * 5
                    complexity_factor = 1 + feature_values['scope_complexity']
                    team_factor = max(0.5, 1 - (feature_values['team_size'] - 5) * 0.1)
                    target = base_duration * complexity_factor * team_factor
                
                elif prediction_type == PredictionType.BUDGET_ESTIMATE:
                    base_cost = feature_values['duration_estimate'] * 1000
                    team_cost = feature_values['team_composition'] * 50000
                    complexity_multiplier = 1 + feature_values['complexity_level']
                    target = (base_cost + team_cost) * complexity_multiplier
                
                elif prediction_type == PredictionType.RISK_ASSESSMENT:
                    risk_score = (
                        feature_values['project_complexity'] * 0.25 +
                        feature_values['market_volatility'] * 0.25 +
                        feature_values['timeline_pressure'] * 0.25 +
                        (1 - feature_values['stakeholder_alignment']) * 0.25
                    )
                    target = min(1.0, risk_score)
                
                training_samples.append({
                    'features': feature_values,
                    'target': target,
                    'metadata': {'synthetic': True, 'generated_at': datetime.now().isoformat()}
                })
            
            self.training_data[prediction_type] = training_samples
        
        self.logger.info(f"Données d'entraînement initialisées pour {len(self.feature_definitions)} types de prédiction")

    def _train_initial_models(self):
        """Entraîne les modèles initiaux"""
        
        for prediction_type, samples in self.training_data.items():
            try:
                self._train_model_for_type(prediction_type, samples)
            except Exception as e:
                self.logger.error(f"Erreur entraînement modèle {prediction_type}: {e}")
        
        self.logger.info(f"{len(self.models)} modèles entraînés")

    def _train_model_for_type(self, prediction_type: PredictionType, samples: List[Dict]):
        """Entraîne un modèle pour un type de prédiction spécifique"""
        
        if len(samples) < 10:
            self.logger.warning(f"Pas assez de données pour {prediction_type}")
            return
        
        # Préparation des données
        features_list = []
        targets = []
        
        for sample in samples:
            feature_vector = []
            for feature_name in self.feature_definitions[prediction_type]:
                feature_vector.append(sample['features'].get(feature_name, 0))
            features_list.append(feature_vector)
            targets.append(sample['target'])
        
        X = np.array(features_list)
        y = np.array(targets)
        
        # Normalisation des features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Division train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        # Choix du modèle selon le type de prédiction
        if prediction_type in [PredictionType.PROJECT_SUCCESS]:
            # Classification
            model = GradientBoostingClassifier(n_estimators=100, random_state=42)
            model_type = ModelType.CLASSIFICATION
        else:
            # Régression
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model_type = ModelType.REGRESSION
        
        # Entraînement
        model.fit(X_train, y_train)
        
        # Évaluation
        if model_type == ModelType.CLASSIFICATION:
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Cross-validation
            cv_scores = cross_val_score(model, X_scaled, y, cv=5)
            
            metrics = ModelMetrics(
                model_id=f"{prediction_type.value}_model",
                model_type=model_type,
                accuracy=accuracy,
                precision=0.0,  # À calculer si nécessaire
                recall=0.0,
                f1_score=0.0,
                mse=0.0,
                r2_score=0.0,
                cross_val_score=cv_scores.mean(),
                training_samples=len(samples),
                last_trained=datetime.now(),
                feature_count=len(self.feature_definitions[prediction_type])
            )
        else:
            y_pred = model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            r2 = model.score(X_test, y_test)
            
            # Cross-validation
            cv_scores = cross_val_score(model, X_scaled, y, cv=5, scoring='r2')
            
            metrics = ModelMetrics(
                model_id=f"{prediction_type.value}_model",
                model_type=model_type,
                accuracy=0.0,
                precision=0.0,
                recall=0.0,
                f1_score=0.0,
                mse=mse,
                r2_score=r2,
                cross_val_score=cv_scores.mean(),
                training_samples=len(samples),
                last_trained=datetime.now(),
                feature_count=len(self.feature_definitions[prediction_type])
            )
        
        # Sauvegarde du modèle et des composants
        model_id = f"{prediction_type.value}_model"
        self.models[model_id] = model
        self.scalers[model_id] = scaler
        self.model_metrics[model_id] = metrics
        
        # Sauvegarde sur disque
        model_path = os.path.join(self.models_path, f"{model_id}.joblib")
        scaler_path = os.path.join(self.models_path, f"{model_id}_scaler.joblib")
        
        joblib.dump(model, model_path)
        joblib.dump(scaler, scaler_path)
        
        # Sauvegarde des métriques en base
        self._save_model_metrics(metrics)
        
        self.logger.info(f"Modèle {model_id} entraîné - Score: {metrics.cross_val_score:.3f}")

    def predict(self, prediction_type: PredictionType, input_data: Dict[str, Any],
                context: Dict[str, Any] = None, requester_id: str = None) -> PredictionResult:
        """Effectue une prédiction"""
        
        request_id = str(uuid.uuid4())
        
        # Création de la demande
        request = PredictionRequest(
            request_id=request_id,
            prediction_type=prediction_type,
            input_data=input_data,
            context=context or {},
            requested_at=datetime.now(),
            requester_id=requester_id or 'system',
            priority=1
        )
        
        # Vérification du cache
        cache_key = self._generate_prediction_cache_key(prediction_type, input_data)
        
        if cache_key in self.prediction_cache:
            cache_entry = self.prediction_cache[cache_key]
            if time.time() - cache_entry['timestamp'] < self.cache_ttl:
                return cache_entry['result']
        
        # Prédiction
        try:
            result = self._execute_prediction(request)
            
            # Cache du résultat
            self.prediction_cache[cache_key] = {
                'result': result,
                'timestamp': time.time()
            }
            
            # Sauvegarde
            self._save_prediction_request(request)
            self._save_prediction_result(result)
            
            # Mise à jour des statistiques
            self.system_stats['total_predictions'] += 1
            if result.confidence_score > 0.7:
                self.system_stats['successful_predictions'] += 1
            
            # Mise à jour de la fréquence des types
            type_key = prediction_type.value
            if type_key not in self.system_stats['prediction_types_frequency']:
                self.system_stats['prediction_types_frequency'][type_key] = 0
            self.system_stats['prediction_types_frequency'][type_key] += 1
            
            self.logger.info(f"Prédiction {prediction_type.value} - Confiance: {result.confidence_score:.3f}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Erreur prédiction {prediction_type}: {e}")
            
            # Résultat d'erreur
            return PredictionResult(
                prediction_id=str(uuid.uuid4()),
                request_id=request_id,
                prediction_type=prediction_type,
                predicted_value=None,
                confidence_score=0.0,
                confidence_level=ConfidenceLevel.LOW,
                model_used="error",
                feature_importance={},
                prediction_interval=(0.0, 0.0),
                metadata={'error': str(e)},
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=1)
            )

    def _execute_prediction(self, request: PredictionRequest) -> PredictionResult:
        """Exécute une prédiction"""
        
        prediction_type = request.prediction_type
        input_data = request.input_data
        
        # Vérification du modèle
        model_id = f"{prediction_type.value}_model"
        
        if model_id not in self.models:
            raise ValueError(f"Modèle non disponible pour {prediction_type}")
        
        model = self.models[model_id]
        scaler = self.scalers[model_id]
        
        # Préparation des features
        feature_vector = []
        feature_names = self.feature_definitions[prediction_type]
        
        for feature_name in feature_names:
            value = input_data.get(feature_name, 0)
            feature_vector.append(float(value))
        
        # Normalisation
        X = np.array([feature_vector])
        X_scaled = scaler.transform(X)
        
        # Prédiction
        if hasattr(model, 'predict_proba'):
            # Classification avec probabilités
            prediction_proba = model.predict_proba(X_scaled)[0]
            predicted_value = model.predict(X_scaled)[0]
            confidence_score = float(np.max(prediction_proba))
        else:
            # Régression
            predicted_value = float(model.predict(X_scaled)[0])
            
            # Estimation de confiance basée sur la variance des arbres (pour RandomForest)
            if hasattr(model, 'estimators_'):
                tree_predictions = [tree.predict(X_scaled)[0] for tree in model.estimators_]
                prediction_std = np.std(tree_predictions)
                confidence_score = max(0.1, 1.0 - min(1.0, prediction_std / abs(predicted_value + 1e-6)))
            else:
                confidence_score = 0.7  # Valeur par défaut
        
        # Niveau de confiance
        if confidence_score >= 0.9:
            confidence_level = ConfidenceLevel.VERY_HIGH
        elif confidence_score >= 0.75:
            confidence_level = ConfidenceLevel.HIGH
        elif confidence_score >= 0.6:
            confidence_level = ConfidenceLevel.MEDIUM
        else:
            confidence_level = ConfidenceLevel.LOW
        
        # Importance des features
        feature_importance = {}
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            for i, feature_name in enumerate(feature_names):
                if i < len(importances):
                    feature_importance[feature_name] = float(importances[i])
        
        # Intervalle de prédiction (estimation simplifiée)
        if prediction_type in [PredictionType.PROJECT_SUCCESS]:
            prediction_interval = (0.0, 1.0)
        else:
            margin = abs(predicted_value) * (1 - confidence_score) * 0.5
            prediction_interval = (
                float(predicted_value - margin),
                float(predicted_value + margin)
            )
        
        # Création du résultat
        result = PredictionResult(
            prediction_id=str(uuid.uuid4()),
            request_id=request.request_id,
            prediction_type=prediction_type,
            predicted_value=predicted_value,
            confidence_score=confidence_score,
            confidence_level=confidence_level,
            model_used=model_id,
            feature_importance=feature_importance,
            prediction_interval=prediction_interval,
            metadata={
                'model_type': self.model_metrics[model_id].model_type.value,
                'training_samples': self.model_metrics[model_id].training_samples,
                'model_accuracy': self.model_metrics[model_id].cross_val_score
            },
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=24)
        )
        
        return result

    def analyze_trends(self, data_source: str, time_horizon: int = 30) -> List[TrendAnalysis]:
        """Analyse les tendances dans les données"""
        
        trends = []
        
        # Analyse des tendances de succès des projets
        success_trend = self._analyze_project_success_trend(time_horizon)
        if success_trend:
            trends.append(success_trend)
        
        # Analyse des tendances de durée
        duration_trend = self._analyze_duration_trend(time_horizon)
        if duration_trend:
            trends.append(duration_trend)
        
        # Analyse des tendances de budget
        budget_trend = self._analyze_budget_trend(time_horizon)
        if budget_trend:
            trends.append(budget_trend)
        
        # Sauvegarde des tendances
        for trend in trends:
            self.trend_analyses[trend.trend_id] = trend
            self._save_trend_analysis(trend)
        
        self.system_stats['trend_detection_count'] = len(self.trend_analyses)
        
        self.logger.info(f"{len(trends)} tendances détectées")
        
        return trends

    def _analyze_project_success_trend(self, time_horizon: int) -> Optional[TrendAnalysis]:
        """Analyse la tendance de succès des projets"""
        
        # Simulation de données de tendance
        # Dans un vrai système, ceci analyserait les données historiques
        
        success_rates = np.random.uniform(0.6, 0.9, 30)  # 30 derniers jours
        
        # Calcul de la tendance
        x = np.arange(len(success_rates))
        slope, _ = np.polyfit(x, success_rates, 1)
        
        if slope > 0.01:
            direction = "increasing"
            strength = min(1.0, abs(slope) * 10)
        elif slope < -0.01:
            direction = "decreasing"
            strength = min(1.0, abs(slope) * 10)
        else:
            direction = "stable"
            strength = 0.3
        
        confidence = min(1.0, 0.7 + strength * 0.3)
        
        return TrendAnalysis(
            trend_id=str(uuid.uuid4()),
            trend_name="Taux de succès des projets",
            trend_type="project_performance",
            direction=direction,
            strength=strength,
            confidence=confidence,
            time_horizon=time_horizon,
            key_factors=["team_experience", "methodology_maturity", "client_engagement"],
            impact_assessment={
                "business_impact": 0.8,
                "operational_impact": 0.6,
                "strategic_impact": 0.7
            },
            recommendations=[
                "Renforcer la formation des équipes",
                "Améliorer l'engagement client",
                "Optimiser les méthodologies"
            ],
            detected_at=datetime.now()
        )

    def _analyze_duration_trend(self, time_horizon: int) -> Optional[TrendAnalysis]:
        """Analyse la tendance des durées de projet"""
        
        # Simulation de données de durée
        durations = np.random.uniform(30, 120, 30)  # 30 derniers projets
        
        # Calcul de la tendance
        x = np.arange(len(durations))
        slope, _ = np.polyfit(x, durations, 1)
        
        if slope > 1:
            direction = "increasing"
            strength = min(1.0, abs(slope) / 10)
        elif slope < -1:
            direction = "decreasing"
            strength = min(1.0, abs(slope) / 10)
        else:
            direction = "stable"
            strength = 0.2
        
        confidence = min(1.0, 0.6 + strength * 0.4)
        
        return TrendAnalysis(
            trend_id=str(uuid.uuid4()),
            trend_name="Durée des projets",
            trend_type="project_duration",
            direction=direction,
            strength=strength,
            confidence=confidence,
            time_horizon=time_horizon,
            key_factors=["scope_complexity", "team_size", "client_responsiveness"],
            impact_assessment={
                "cost_impact": 0.9,
                "resource_impact": 0.8,
                "client_satisfaction_impact": 0.6
            },
            recommendations=[
                "Améliorer l'estimation initiale",
                "Optimiser la gestion des changements",
                "Renforcer la communication client"
            ],
            detected_at=datetime.now()
        )

    def _analyze_budget_trend(self, time_horizon: int) -> Optional[TrendAnalysis]:
        """Analyse la tendance des budgets"""
        
        # Simulation de données de budget
        budgets = np.random.uniform(50000, 300000, 30)
        
        # Calcul de la tendance
        x = np.arange(len(budgets))
        slope, _ = np.polyfit(x, budgets, 1)
        
        if slope > 1000:
            direction = "increasing"
            strength = min(1.0, abs(slope) / 10000)
        elif slope < -1000:
            direction = "decreasing"
            strength = min(1.0, abs(slope) / 10000)
        else:
            direction = "stable"
            strength = 0.3
        
        confidence = min(1.0, 0.65 + strength * 0.35)
        
        return TrendAnalysis(
            trend_id=str(uuid.uuid4()),
            trend_name="Budget des projets",
            trend_type="project_budget",
            direction=direction,
            strength=strength,
            confidence=confidence,
            time_horizon=time_horizon,
            key_factors=["market_rates", "complexity_level", "competition"],
            impact_assessment={
                "profitability_impact": 0.9,
                "competitiveness_impact": 0.7,
                "growth_impact": 0.6
            },
            recommendations=[
                "Optimiser les coûts opérationnels",
                "Améliorer la proposition de valeur",
                "Diversifier les offres"
            ],
            detected_at=datetime.now()
        )

    def get_model_performance(self, model_id: str = None) -> Dict[str, Any]:
        """Retourne les performances des modèles"""
        
        if model_id:
            if model_id in self.model_metrics:
                return asdict(self.model_metrics[model_id])
            else:
                return {}
        
        # Toutes les performances
        performance_data = {}
        
        for mid, metrics in self.model_metrics.items():
            performance_data[mid] = {
                'model_type': metrics.model_type.value,
                'accuracy': metrics.accuracy,
                'cross_val_score': metrics.cross_val_score,
                'training_samples': metrics.training_samples,
                'last_trained': metrics.last_trained.isoformat(),
                'feature_count': metrics.feature_count
            }
        
        return performance_data

    def retrain_model(self, prediction_type: PredictionType, new_data: List[Dict] = None):
        """Re-entraîne un modèle avec de nouvelles données"""
        
        if new_data:
            # Ajout des nouvelles données
            if prediction_type not in self.training_data:
                self.training_data[prediction_type] = []
            
            self.training_data[prediction_type].extend(new_data)
        
        # Re-entraînement
        if prediction_type in self.training_data:
            self._train_model_for_type(prediction_type, self.training_data[prediction_type])
            self.logger.info(f"Modèle {prediction_type.value} re-entraîné")

    def _generate_prediction_cache_key(self, prediction_type: PredictionType, 
                                     input_data: Dict[str, Any]) -> str:
        """Génère une clé de cache pour la prédiction"""
        
        key_data = {
            'type': prediction_type.value,
            'data': input_data
        }
        
        key_str = json.dumps(key_data, sort_keys=True)
        return str(hash(key_str))

    def _save_prediction_request(self, request: PredictionRequest):
        """Sauvegarde une demande de prédiction"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO prediction_requests 
                    (request_id, prediction_type, input_data, context, 
                     requested_at, requester_id, priority)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    request.request_id, request.prediction_type.value,
                    json.dumps(request.input_data), json.dumps(request.context),
                    request.requested_at, request.requester_id, request.priority
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde demande: {e}")

    def _save_prediction_result(self, result: PredictionResult):
        """Sauvegarde un résultat de prédiction"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO prediction_results 
                    (prediction_id, request_id, prediction_type, predicted_value,
                     confidence_score, confidence_level, model_used, feature_importance,
                     prediction_interval, metadata, created_at, expires_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    result.prediction_id, result.request_id, result.prediction_type.value,
                    json.dumps(result.predicted_value), result.confidence_score,
                    result.confidence_level.value, result.model_used,
                    json.dumps(result.feature_importance),
                    json.dumps(result.prediction_interval),
                    json.dumps(result.metadata), result.created_at, result.expires_at
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde résultat: {e}")

    def _save_model_metrics(self, metrics: ModelMetrics):
        """Sauvegarde les métriques de modèle"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO model_metrics 
                    (model_id, model_type, accuracy, precision, recall, f1_score,
                     mse, r2_score, cross_val_score, training_samples, 
                     last_trained, feature_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    metrics.model_id, metrics.model_type.value, metrics.accuracy,
                    metrics.precision, metrics.recall, metrics.f1_score,
                    metrics.mse, metrics.r2_score, metrics.cross_val_score,
                    metrics.training_samples, metrics.last_trained, metrics.feature_count
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde métriques: {e}")

    def _save_trend_analysis(self, trend: TrendAnalysis):
        """Sauvegarde une analyse de tendance"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO trend_analyses 
                    (trend_id, trend_name, trend_type, direction, strength,
                     confidence, time_horizon, key_factors, impact_assessment,
                     recommendations, detected_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    trend.trend_id, trend.trend_name, trend.trend_type,
                    trend.direction, trend.strength, trend.confidence,
                    trend.time_horizon, json.dumps(trend.key_factors),
                    json.dumps(trend.impact_assessment),
                    json.dumps(trend.recommendations), trend.detected_at
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde tendance: {e}")

    def _load_existing_models(self):
        """Charge les modèles existants"""
        
        try:
            for filename in os.listdir(self.models_path):
                if filename.endswith('.joblib') and not filename.endswith('_scaler.joblib'):
                    model_id = filename.replace('.joblib', '')
                    model_path = os.path.join(self.models_path, filename)
                    scaler_path = os.path.join(self.models_path, f"{model_id}_scaler.joblib")
                    
                    if os.path.exists(scaler_path):
                        self.models[model_id] = joblib.load(model_path)
                        self.scalers[model_id] = joblib.load(scaler_path)
            
            self.logger.info(f"{len(self.models)} modèles chargés")
            
        except Exception as e:
            self.logger.error(f"Erreur chargement modèles: {e}")

    def _start_services(self):
        """Démarre les services du système"""
        
        # Service de re-entraînement automatique
        if self.auto_retrain:
            threading.Thread(target=self._retraining_service, daemon=True).start()
        
        # Service de détection de tendances
        if self.trend_detection_enabled:
            threading.Thread(target=self._trend_detection_service, daemon=True).start()
        
        # Service de nettoyage du cache
        threading.Thread(target=self._cache_cleanup_service, daemon=True).start()

    def _retraining_service(self):
        """Service de re-entraînement automatique"""
        
        while True:
            try:
                # Re-entraînement quotidien
                for prediction_type in self.training_data.keys():
                    if len(self.training_data[prediction_type]) > 100:
                        self.retrain_model(prediction_type)
                
                time.sleep(86400)  # 24 heures
                
            except Exception as e:
                self.logger.error(f"Erreur service re-entraînement: {e}")
                time.sleep(86400)

    def _trend_detection_service(self):
        """Service de détection de tendances"""
        
        while True:
            try:
                self.analyze_trends("system", time_horizon=30)
                
                time.sleep(3600)  # Toutes les heures
                
            except Exception as e:
                self.logger.error(f"Erreur service détection tendances: {e}")
                time.sleep(3600)

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
                    self.logger.info(f"{len(expired_keys)} prédictions expirées supprimées du cache")
                
                time.sleep(1800)  # Nettoyage toutes les 30 minutes
                
            except Exception as e:
                self.logger.error(f"Erreur service nettoyage cache: {e}")
                time.sleep(1800)

    def get_system_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques du système"""
        
        # Mise à jour des statistiques
        if self.system_stats['total_predictions'] > 0:
            self.system_stats['average_confidence'] = (
                self.system_stats['successful_predictions'] / 
                self.system_stats['total_predictions']
            )
        
        # Performance des modèles
        self.system_stats['model_performance'] = {}
        for model_id, metrics in self.model_metrics.items():
            self.system_stats['model_performance'][model_id] = {
                'cross_val_score': metrics.cross_val_score,
                'training_samples': metrics.training_samples
            }
        
        return self.system_stats.copy()

# Instance globale
_predictive_intelligence = None

def get_predictive_intelligence() -> PredictiveIntelligence:
    """Retourne l'instance d'intelligence prédictive"""
    global _predictive_intelligence
    if _predictive_intelligence is None:
        _predictive_intelligence = PredictiveIntelligence()
    return _predictive_intelligence

# Test du système
if __name__ == '__main__':
    print("=== Test Intelligence Prédictive ===")
    
    pi = PredictiveIntelligence()
    
    # Test de prédiction de succès de projet
    project_data = {
        'team_size': 5,
        'budget_amount': 150000,
        'timeline_days': 90,
        'complexity_score': 0.7,
        'client_engagement': 0.8,
        'methodology_maturity': 0.9,
        'risk_factors_count': 3,
        'stakeholder_count': 8,
        'industry_experience': 0.8,
        'team_experience': 0.7
    }
    
    result = pi.predict(PredictionType.PROJECT_SUCCESS, project_data)
    print(f"Prédiction succès projet: {result.predicted_value}")
    print(f"Confiance: {result.confidence_score:.3f}")
    print(f"Niveau: {result.confidence_level.value}")
    
    # Test de prédiction de durée
    duration_data = {
        'scope_complexity': 0.8,
        'team_size': 5,
        'methodology_steps': 12,
        'dependencies_count': 8,
        'resource_availability': 0.9,
        'client_responsiveness': 0.7,
        'change_requests_expected': 3,
        'industry_type': 1,
        'project_type': 2,
        'historical_similar_duration': 85
    }
    
    result = pi.predict(PredictionType.DURATION_ESTIMATE, duration_data)
    print(f"Prédiction durée: {result.predicted_value:.1f} jours")
    print(f"Confiance: {result.confidence_score:.3f}")
    
    # Test d'analyse de tendances
    trends = pi.analyze_trends("system")
    print(f"Tendances détectées: {len(trends)}")
    
    if trends:
        trend = trends[0]
        print(f"Tendance: {trend.trend_name}")
        print(f"Direction: {trend.direction}")
        print(f"Force: {trend.strength:.3f}")
    
    # Test des statistiques
    stats = pi.get_system_statistics()
    print(f"Statistiques: {stats['total_predictions']} prédictions")
    
    print("Test terminé avec succès")

