#!/usr/bin/env python3
"""
Advanced Analytics Dashboard - Dashboard Analytics Avancé
Système complet d'analytics avec métriques temps réel, prédictions IA et visualisations
"""

import os
import json
import sqlite3
import datetime
import threading
import time
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
from pathlib import Path
import logging
import statistics
from collections import defaultdict, deque
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.utils
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
import pickle
import base64
from io import BytesIO

# Configuration logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    RATE = "rate"
    PERCENTAGE = "percentage"

class TimeRange(Enum):
    LAST_HOUR = "1h"
    LAST_6_HOURS = "6h"
    LAST_24_HOURS = "24h"
    LAST_7_DAYS = "7d"
    LAST_30_DAYS = "30d"
    LAST_90_DAYS = "90d"

class AggregationType(Enum):
    SUM = "sum"
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    PERCENTILE_95 = "p95"
    PERCENTILE_99 = "p99"

@dataclass
class Metric:
    """Métrique système"""
    name: str
    value: float
    timestamp: datetime.datetime
    labels: Dict[str, str]
    metric_type: MetricType
    unit: str
    description: str

@dataclass
class Dashboard:
    """Configuration de dashboard"""
    id: str
    name: str
    description: str
    widgets: List[Dict[str, Any]]
    layout: Dict[str, Any]
    refresh_interval: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    owner: str
    is_public: bool
    tags: List[str]

@dataclass
class Widget:
    """Widget de dashboard"""
    id: str
    type: str  # chart, table, metric, alert
    title: str
    query: str
    config: Dict[str, Any]
    position: Dict[str, int]  # x, y, width, height
    refresh_interval: int

class PredictionEngine:
    """Moteur de prédictions IA"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.training_data = defaultdict(list)
        self.predictions_cache = {}
        self.min_samples = 50
        
    def add_training_data(self, metric_name: str, value: float, timestamp: datetime.datetime):
        """Ajoute des données d'entraînement"""
        self.training_data[metric_name].append({
            'value': value,
            'timestamp': timestamp,
            'hour': timestamp.hour,
            'day_of_week': timestamp.weekday(),
            'day_of_month': timestamp.day,
            'month': timestamp.month
        })
        
        # Garder seulement les 5000 derniers points
        if len(self.training_data[metric_name]) > 5000:
            self.training_data[metric_name] = self.training_data[metric_name][-5000:]
    
    def train_model(self, metric_name: str) -> bool:
        """Entraîne un modèle de prédiction"""
        if len(self.training_data[metric_name]) < self.min_samples:
            return False
        
        try:
            data = self.training_data[metric_name]
            
            # Préparer les features
            features = []
            targets = []
            
            for i in range(len(data) - 1):
                point = data[i]
                next_point = data[i + 1]
                
                # Features: valeur actuelle + contexte temporel
                feature_vector = [
                    point['value'],
                    point['hour'],
                    point['day_of_week'],
                    point['day_of_month'],
                    point['month']
                ]
                
                # Ajouter des features de tendance
                if i >= 5:
                    recent_values = [data[j]['value'] for j in range(i-4, i+1)]
                    feature_vector.extend([
                        statistics.mean(recent_values),
                        max(recent_values) - min(recent_values),
                        recent_values[-1] - recent_values[0]  # Tendance
                    ])
                else:
                    feature_vector.extend([point['value'], 0, 0])
                
                features.append(feature_vector)
                targets.append(next_point['value'])
            
            X = np.array(features)
            y = np.array(targets)
            
            # Normaliser les features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Entraîner le modèle Random Forest
            model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            model.fit(X_scaled, y)
            
            # Évaluer le modèle
            predictions = model.predict(X_scaled)
            mae = mean_absolute_error(y, predictions)
            r2 = r2_score(y, predictions)
            
            # Sauvegarder le modèle et le scaler
            self.models[metric_name] = {
                'model': model,
                'mae': mae,
                'r2': r2,
                'trained_at': datetime.datetime.now()
            }
            self.scalers[metric_name] = scaler
            
            logger.info(f"🤖 Modèle prédictif entraîné pour {metric_name} (MAE: {mae:.2f}, R²: {r2:.3f})")
            return True
            
        except Exception as e:
            logger.error(f"Erreur entraînement modèle {metric_name}: {e}")
            return False
    
    def predict(self, metric_name: str, steps_ahead: int = 1) -> List[Dict[str, Any]]:
        """Fait des prédictions"""
        if metric_name not in self.models or not self.training_data[metric_name]:
            return []
        
        try:
            model_info = self.models[metric_name]
            model = model_info['model']
            scaler = self.scalers[metric_name]
            
            # Prendre les dernières données
            recent_data = self.training_data[metric_name][-10:]
            if len(recent_data) < 5:
                return []
            
            predictions = []
            current_time = recent_data[-1]['timestamp']
            
            for step in range(steps_ahead):
                # Préparer les features pour la prédiction
                last_point = recent_data[-1]
                next_time = current_time + datetime.timedelta(minutes=30 * (step + 1))
                
                feature_vector = [
                    last_point['value'],
                    next_time.hour,
                    next_time.weekday(),
                    next_time.day,
                    next_time.month
                ]
                
                # Ajouter des features de tendance
                recent_values = [p['value'] for p in recent_data[-5:]]
                feature_vector.extend([
                    statistics.mean(recent_values),
                    max(recent_values) - min(recent_values),
                    recent_values[-1] - recent_values[0]
                ])
                
                # Normaliser et prédire
                X = np.array([feature_vector])
                X_scaled = scaler.transform(X)
                predicted_value = model.predict(X_scaled)[0]
                
                # Calculer l'intervalle de confiance (approximatif)
                confidence_interval = model_info['mae'] * 1.96  # 95% CI approximatif
                
                prediction = {
                    'timestamp': next_time,
                    'predicted_value': predicted_value,
                    'confidence_lower': predicted_value - confidence_interval,
                    'confidence_upper': predicted_value + confidence_interval,
                    'model_accuracy': model_info['r2']
                }
                
                predictions.append(prediction)
                
                # Mettre à jour les données récentes pour la prochaine prédiction
                recent_data.append({
                    'value': predicted_value,
                    'timestamp': next_time,
                    'hour': next_time.hour,
                    'day_of_week': next_time.weekday(),
                    'day_of_month': next_time.day,
                    'month': next_time.month
                })
            
            return predictions
            
        except Exception as e:
            logger.error(f"Erreur prédiction {metric_name}: {e}")
            return []

class AdvancedAnalyticsDashboard:
    """Dashboard Analytics Avancé"""
    
    def __init__(self, base_path: str = "/home/ubuntu/substans_ai_megacabinet"):
        self.base_path = Path(base_path)
        self.db_path = self.base_path / "data" / "analytics.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Composants
        self.prediction_engine = PredictionEngine()
        self.metrics_buffer = defaultdict(deque)
        self.dashboards = {}
        self.widgets = {}
        
        # Configuration
        self.retention_days = 90
        self.aggregation_interval = 300  # 5 minutes
        
        # Services
        self.running = False
        self.aggregation_thread = None
        self.prediction_thread = None
        
        self._init_database()
        self._init_default_dashboards()
        self._start_services()
    
    def _init_database(self):
        """Initialise la base de données"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    value REAL NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    labels TEXT,
                    metric_type TEXT NOT NULL,
                    unit TEXT,
                    description TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS aggregated_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    aggregation_type TEXT NOT NULL,
                    value REAL NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    time_range TEXT NOT NULL,
                    labels TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS dashboards (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    widgets TEXT NOT NULL,
                    layout TEXT NOT NULL,
                    refresh_interval INTEGER NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    owner TEXT NOT NULL,
                    is_public BOOLEAN NOT NULL,
                    tags TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT NOT NULL,
                    predicted_value REAL NOT NULL,
                    confidence_lower REAL NOT NULL,
                    confidence_upper REAL NOT NULL,
                    prediction_timestamp TIMESTAMP NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    model_accuracy REAL NOT NULL
                )
            """)
            
            # Index pour les performances
            conn.execute("CREATE INDEX IF NOT EXISTS idx_metrics_name_time ON metrics(name, timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_aggregated_name_time ON aggregated_metrics(name, timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_predictions_metric_time ON predictions(metric_name, prediction_timestamp)")
            
            conn.commit()
    
    def _init_default_dashboards(self):
        """Initialise les dashboards par défaut"""
        # Dashboard Système
        system_dashboard = Dashboard(
            id="system_overview",
            name="Vue d'ensemble Système",
            description="Métriques système principales",
            widgets=[
                {
                    "id": "cpu_chart",
                    "type": "line_chart",
                    "title": "Utilisation CPU",
                    "query": "cpu_percent",
                    "config": {"color": "#ff6b6b", "unit": "%"},
                    "position": {"x": 0, "y": 0, "width": 6, "height": 4}
                },
                {
                    "id": "memory_chart", 
                    "type": "line_chart",
                    "title": "Utilisation Mémoire",
                    "query": "memory_percent",
                    "config": {"color": "#4ecdc4", "unit": "%"},
                    "position": {"x": 6, "y": 0, "width": 6, "height": 4}
                },
                {
                    "id": "disk_gauge",
                    "type": "gauge",
                    "title": "Espace Disque",
                    "query": "disk_percent",
                    "config": {"max": 100, "unit": "%", "thresholds": [70, 85, 95]},
                    "position": {"x": 0, "y": 4, "width": 4, "height": 3}
                },
                {
                    "id": "network_chart",
                    "type": "area_chart",
                    "title": "Trafic Réseau",
                    "query": "network_bytes_total",
                    "config": {"color": "#45b7d1", "unit": "MB/s"},
                    "position": {"x": 4, "y": 4, "width": 8, "height": 3}
                }
            ],
            layout={"columns": 12, "rows": 8},
            refresh_interval=30,
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
            owner="system",
            is_public=True,
            tags=["system", "monitoring"]
        )
        
        # Dashboard Business
        business_dashboard = Dashboard(
            id="business_metrics",
            name="Métriques Business",
            description="KPIs et métriques métier",
            widgets=[
                {
                    "id": "missions_count",
                    "type": "metric",
                    "title": "Missions Actives",
                    "query": "active_missions_count",
                    "config": {"color": "#28a745", "icon": "briefcase"},
                    "position": {"x": 0, "y": 0, "width": 3, "height": 2}
                },
                {
                    "id": "success_rate",
                    "type": "metric",
                    "title": "Taux de Succès",
                    "query": "mission_success_rate",
                    "config": {"color": "#17a2b8", "unit": "%", "icon": "check-circle"},
                    "position": {"x": 3, "y": 0, "width": 3, "height": 2}
                },
                {
                    "id": "revenue_chart",
                    "type": "bar_chart",
                    "title": "Revenus Générés",
                    "query": "revenue_generated",
                    "config": {"color": "#ffc107", "unit": "€"},
                    "position": {"x": 0, "y": 2, "width": 12, "height": 4}
                },
                {
                    "id": "agents_performance",
                    "type": "heatmap",
                    "title": "Performance Agents",
                    "query": "agents_performance_matrix",
                    "config": {"colorscale": "Viridis"},
                    "position": {"x": 0, "y": 6, "width": 12, "height": 4}
                }
            ],
            layout={"columns": 12, "rows": 10},
            refresh_interval=60,
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
            owner="system",
            is_public=True,
            tags=["business", "kpi"]
        )
        
        # Dashboard Prédictif
        predictive_dashboard = Dashboard(
            id="predictive_analytics",
            name="Analytics Prédictifs",
            description="Prédictions et tendances IA",
            widgets=[
                {
                    "id": "cpu_prediction",
                    "type": "prediction_chart",
                    "title": "Prédiction CPU (24h)",
                    "query": "cpu_percent_prediction",
                    "config": {"prediction_hours": 24, "confidence_bands": True},
                    "position": {"x": 0, "y": 0, "width": 6, "height": 4}
                },
                {
                    "id": "memory_prediction",
                    "type": "prediction_chart", 
                    "title": "Prédiction Mémoire (24h)",
                    "query": "memory_percent_prediction",
                    "config": {"prediction_hours": 24, "confidence_bands": True},
                    "position": {"x": 6, "y": 0, "width": 6, "height": 4}
                },
                {
                    "id": "anomaly_detection",
                    "type": "anomaly_chart",
                    "title": "Détection d'Anomalies",
                    "query": "anomaly_scores",
                    "config": {"threshold": 0.7},
                    "position": {"x": 0, "y": 4, "width": 12, "height": 4}
                }
            ],
            layout={"columns": 12, "rows": 8},
            refresh_interval=300,
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
            owner="system",
            is_public=True,
            tags=["prediction", "ai", "anomaly"]
        )
        
        self.dashboards = {
            "system_overview": system_dashboard,
            "business_metrics": business_dashboard,
            "predictive_analytics": predictive_dashboard
        }
    
    def _start_services(self):
        """Démarre les services d'arrière-plan"""
        if self.running:
            return
        
        self.running = True
        
        # Thread d'agrégation
        self.aggregation_thread = threading.Thread(target=self._aggregation_loop, daemon=True)
        self.aggregation_thread.start()
        
        # Thread de prédiction
        self.prediction_thread = threading.Thread(target=self._prediction_loop, daemon=True)
        self.prediction_thread.start()
        
        logger.info("🚀 Services analytics démarrés")
    
    def stop_services(self):
        """Arrête les services"""
        self.running = False
        logger.info("🛑 Services analytics arrêtés")
    
    def _aggregation_loop(self):
        """Boucle d'agrégation des métriques"""
        while self.running:
            try:
                self._aggregate_metrics()
                self._cleanup_old_data()
            except Exception as e:
                logger.error(f"Erreur agrégation: {e}")
            
            time.sleep(self.aggregation_interval)
    
    def _prediction_loop(self):
        """Boucle de prédictions"""
        while self.running:
            try:
                self._update_predictions()
            except Exception as e:
                logger.error(f"Erreur prédictions: {e}")
            
            time.sleep(1800)  # 30 minutes
    
    def add_metric(self, name: str, value: float, labels: Dict[str, str] = None, 
                   metric_type: MetricType = MetricType.GAUGE, unit: str = "", 
                   description: str = ""):
        """Ajoute une métrique"""
        timestamp = datetime.datetime.now()
        
        metric = Metric(
            name=name,
            value=value,
            timestamp=timestamp,
            labels=labels or {},
            metric_type=metric_type,
            unit=unit,
            description=description
        )
        
        # Ajouter au buffer
        self.metrics_buffer[name].append(metric)
        
        # Garder seulement les 10000 derniers points
        if len(self.metrics_buffer[name]) > 10000:
            self.metrics_buffer[name].popleft()
        
        # Ajouter aux données d'entraînement
        self.prediction_engine.add_training_data(name, value, timestamp)
        
        # Sauvegarder en base
        self._save_metric(metric)
    
    def _save_metric(self, metric: Metric):
        """Sauvegarde une métrique en base"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO metrics (name, value, timestamp, labels, metric_type, unit, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    metric.name,
                    metric.value,
                    metric.timestamp.isoformat(),
                    json.dumps(metric.labels),
                    metric.metric_type.value,
                    metric.unit,
                    metric.description
                ))
        except Exception as e:
            logger.error(f"Erreur sauvegarde métrique: {e}")
    
    def _aggregate_metrics(self):
        """Agrège les métriques"""
        current_time = datetime.datetime.now()
        
        for metric_name, metrics in self.metrics_buffer.items():
            if not metrics:
                continue
            
            # Agrégations sur différentes périodes
            time_ranges = [
                (TimeRange.LAST_HOUR, datetime.timedelta(hours=1)),
                (TimeRange.LAST_24_HOURS, datetime.timedelta(hours=24)),
                (TimeRange.LAST_7_DAYS, datetime.timedelta(days=7))
            ]
            
            for time_range, delta in time_ranges:
                cutoff_time = current_time - delta
                recent_metrics = [m for m in metrics if m.timestamp >= cutoff_time]
                
                if not recent_metrics:
                    continue
                
                values = [m.value for m in recent_metrics]
                
                # Calculer les agrégations
                aggregations = {
                    AggregationType.AVG: statistics.mean(values),
                    AggregationType.MIN: min(values),
                    AggregationType.MAX: max(values),
                    AggregationType.SUM: sum(values),
                    AggregationType.COUNT: len(values)
                }
                
                # Percentiles si assez de données
                if len(values) >= 20:
                    aggregations[AggregationType.PERCENTILE_95] = np.percentile(values, 95)
                    aggregations[AggregationType.PERCENTILE_99] = np.percentile(values, 99)
                
                # Sauvegarder les agrégations
                for agg_type, agg_value in aggregations.items():
                    self._save_aggregation(metric_name, agg_type, agg_value, current_time, time_range)
    
    def _save_aggregation(self, metric_name: str, agg_type: AggregationType, 
                         value: float, timestamp: datetime.datetime, time_range: TimeRange):
        """Sauvegarde une agrégation"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO aggregated_metrics 
                    (name, aggregation_type, value, timestamp, time_range, labels)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    metric_name,
                    agg_type.value,
                    value,
                    timestamp.isoformat(),
                    time_range.value,
                    "{}"
                ))
        except Exception as e:
            logger.error(f"Erreur sauvegarde agrégation: {e}")
    
    def _update_predictions(self):
        """Met à jour les prédictions"""
        for metric_name in self.metrics_buffer.keys():
            # Entraîner le modèle si nécessaire
            if metric_name not in self.prediction_engine.models:
                self.prediction_engine.train_model(metric_name)
            
            # Faire des prédictions
            predictions = self.prediction_engine.predict(metric_name, steps_ahead=48)  # 24h
            
            # Sauvegarder les prédictions
            for prediction in predictions:
                self._save_prediction(metric_name, prediction)
    
    def _save_prediction(self, metric_name: str, prediction: Dict[str, Any]):
        """Sauvegarde une prédiction"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO predictions 
                    (metric_name, predicted_value, confidence_lower, confidence_upper, 
                     prediction_timestamp, created_at, model_accuracy)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    metric_name,
                    prediction['predicted_value'],
                    prediction['confidence_lower'],
                    prediction['confidence_upper'],
                    prediction['timestamp'].isoformat(),
                    datetime.datetime.now().isoformat(),
                    prediction['model_accuracy']
                ))
        except Exception as e:
            logger.error(f"Erreur sauvegarde prédiction: {e}")
    
    def _cleanup_old_data(self):
        """Nettoie les anciennes données"""
        try:
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=self.retention_days)
            
            with sqlite3.connect(self.db_path) as conn:
                # Nettoyer les anciennes métriques
                conn.execute("DELETE FROM metrics WHERE timestamp < ?", (cutoff_date.isoformat(),))
                
                # Nettoyer les anciennes agrégations
                conn.execute("DELETE FROM aggregated_metrics WHERE timestamp < ?", (cutoff_date.isoformat(),))
                
                # Nettoyer les anciennes prédictions
                conn.execute("DELETE FROM predictions WHERE created_at < ?", (cutoff_date.isoformat(),))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Erreur nettoyage données: {e}")
    
    def get_metric_data(self, metric_name: str, time_range: TimeRange = TimeRange.LAST_24_HOURS,
                       aggregation: AggregationType = AggregationType.AVG) -> List[Dict[str, Any]]:
        """Récupère les données d'une métrique"""
        try:
            # Calculer la période
            now = datetime.datetime.now()
            time_deltas = {
                TimeRange.LAST_HOUR: datetime.timedelta(hours=1),
                TimeRange.LAST_6_HOURS: datetime.timedelta(hours=6),
                TimeRange.LAST_24_HOURS: datetime.timedelta(hours=24),
                TimeRange.LAST_7_DAYS: datetime.timedelta(days=7),
                TimeRange.LAST_30_DAYS: datetime.timedelta(days=30),
                TimeRange.LAST_90_DAYS: datetime.timedelta(days=90)
            }
            
            start_time = now - time_deltas[time_range]
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT timestamp, value FROM metrics 
                    WHERE name = ? AND timestamp >= ?
                    ORDER BY timestamp
                """, (metric_name, start_time.isoformat()))
                
                data = []
                for row in cursor.fetchall():
                    data.append({
                        'timestamp': datetime.datetime.fromisoformat(row[0]),
                        'value': row[1]
                    })
                
                return data
                
        except Exception as e:
            logger.error(f"Erreur récupération données {metric_name}: {e}")
            return []
    
    def get_predictions(self, metric_name: str, hours_ahead: int = 24) -> List[Dict[str, Any]]:
        """Récupère les prédictions pour une métrique"""
        try:
            start_time = datetime.datetime.now()
            end_time = start_time + datetime.timedelta(hours=hours_ahead)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT prediction_timestamp, predicted_value, confidence_lower, 
                           confidence_upper, model_accuracy
                    FROM predictions 
                    WHERE metric_name = ? 
                    AND prediction_timestamp BETWEEN ? AND ?
                    ORDER BY prediction_timestamp
                """, (metric_name, start_time.isoformat(), end_time.isoformat()))
                
                predictions = []
                for row in cursor.fetchall():
                    predictions.append({
                        'timestamp': datetime.datetime.fromisoformat(row[0]),
                        'predicted_value': row[1],
                        'confidence_lower': row[2],
                        'confidence_upper': row[3],
                        'model_accuracy': row[4]
                    })
                
                return predictions
                
        except Exception as e:
            logger.error(f"Erreur récupération prédictions {metric_name}: {e}")
            return []
    
    def create_chart(self, metric_name: str, chart_type: str = "line", 
                    time_range: TimeRange = TimeRange.LAST_24_HOURS,
                    include_predictions: bool = False) -> str:
        """Crée un graphique pour une métrique"""
        try:
            # Récupérer les données historiques
            data = self.get_metric_data(metric_name, time_range)
            
            if not data:
                return ""
            
            # Créer le graphique selon le type
            if chart_type == "line":
                fig = go.Figure()
                
                # Données historiques
                timestamps = [d['timestamp'] for d in data]
                values = [d['value'] for d in data]
                
                fig.add_trace(go.Scatter(
                    x=timestamps,
                    y=values,
                    mode='lines+markers',
                    name=f'{metric_name} (Historique)',
                    line=dict(color='#1f77b4', width=2)
                ))
                
                # Ajouter les prédictions si demandé
                if include_predictions:
                    predictions = self.get_predictions(metric_name)
                    if predictions:
                        pred_timestamps = [p['timestamp'] for p in predictions]
                        pred_values = [p['predicted_value'] for p in predictions]
                        conf_lower = [p['confidence_lower'] for p in predictions]
                        conf_upper = [p['confidence_upper'] for p in predictions]
                        
                        # Ligne de prédiction
                        fig.add_trace(go.Scatter(
                            x=pred_timestamps,
                            y=pred_values,
                            mode='lines',
                            name=f'{metric_name} (Prédiction)',
                            line=dict(color='#ff7f0e', width=2, dash='dash')
                        ))
                        
                        # Bandes de confiance
                        fig.add_trace(go.Scatter(
                            x=pred_timestamps + pred_timestamps[::-1],
                            y=conf_upper + conf_lower[::-1],
                            fill='toself',
                            fillcolor='rgba(255, 127, 14, 0.2)',
                            line=dict(color='rgba(255,255,255,0)'),
                            name='Intervalle de confiance',
                            showlegend=True
                        ))
                
                fig.update_layout(
                    title=f'{metric_name} - {time_range.value}',
                    xaxis_title='Temps',
                    yaxis_title='Valeur',
                    hovermode='x unified',
                    template='plotly_white'
                )
                
            elif chart_type == "gauge":
                # Prendre la dernière valeur
                current_value = data[-1]['value'] if data else 0
                
                fig = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=current_value,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': metric_name},
                    gauge={
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 50], 'color': "lightgray"},
                            {'range': [50, 80], 'color': "gray"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ))
                
            elif chart_type == "bar":
                # Agrégation par heure pour les barres
                hourly_data = defaultdict(list)
                for d in data:
                    hour_key = d['timestamp'].replace(minute=0, second=0, microsecond=0)
                    hourly_data[hour_key].append(d['value'])
                
                hours = sorted(hourly_data.keys())
                avg_values = [statistics.mean(hourly_data[h]) for h in hours]
                
                fig = go.Figure(data=[
                    go.Bar(x=hours, y=avg_values, name=metric_name)
                ])
                
                fig.update_layout(
                    title=f'{metric_name} - Moyennes horaires',
                    xaxis_title='Heure',
                    yaxis_title='Valeur moyenne'
                )
            
            # Convertir en JSON pour l'interface web
            return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            
        except Exception as e:
            logger.error(f"Erreur création graphique {metric_name}: {e}")
            return ""
    
    def get_dashboard_data(self, dashboard_id: str) -> Dict[str, Any]:
        """Récupère les données d'un dashboard"""
        if dashboard_id not in self.dashboards:
            return {}
        
        dashboard = self.dashboards[dashboard_id]
        dashboard_data = asdict(dashboard)
        
        # Générer les données pour chaque widget
        widgets_data = {}
        for widget in dashboard.widgets:
            widget_id = widget['id']
            query = widget['query']
            widget_type = widget['type']
            
            try:
                if widget_type in ['line_chart', 'area_chart', 'bar_chart']:
                    chart_data = self.create_chart(query, widget_type.split('_')[0])
                    widgets_data[widget_id] = {
                        'type': 'chart',
                        'data': chart_data
                    }
                elif widget_type == 'gauge':
                    chart_data = self.create_chart(query, 'gauge')
                    widgets_data[widget_id] = {
                        'type': 'chart',
                        'data': chart_data
                    }
                elif widget_type == 'metric':
                    # Récupérer la dernière valeur
                    recent_data = self.get_metric_data(query, TimeRange.LAST_HOUR)
                    current_value = recent_data[-1]['value'] if recent_data else 0
                    widgets_data[widget_id] = {
                        'type': 'metric',
                        'value': current_value,
                        'config': widget['config']
                    }
                elif widget_type == 'prediction_chart':
                    chart_data = self.create_chart(query, 'line', include_predictions=True)
                    widgets_data[widget_id] = {
                        'type': 'chart',
                        'data': chart_data
                    }
                    
            except Exception as e:
                logger.error(f"Erreur génération widget {widget_id}: {e}")
                widgets_data[widget_id] = {
                    'type': 'error',
                    'message': f"Erreur: {e}"
                }
        
        dashboard_data['widgets_data'] = widgets_data
        return dashboard_data
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Récupère un résumé des analytics"""
        try:
            # Compter les métriques
            total_metrics = len(self.metrics_buffer)
            
            # Compter les modèles entraînés
            trained_models = len(self.prediction_engine.models)
            
            # Statistiques des données
            total_data_points = sum(len(buffer) for buffer in self.metrics_buffer.values())
            
            # Métriques récentes
            recent_metrics = {}
            for name, buffer in self.metrics_buffer.items():
                if buffer:
                    recent_metrics[name] = {
                        'current_value': buffer[-1].value,
                        'timestamp': buffer[-1].timestamp.isoformat(),
                        'unit': buffer[-1].unit
                    }
            
            # Prédictions disponibles
            predictions_count = 0
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM predictions")
                predictions_count = cursor.fetchone()[0]
            
            return {
                'total_metrics': total_metrics,
                'trained_models': trained_models,
                'total_data_points': total_data_points,
                'predictions_count': predictions_count,
                'dashboards_count': len(self.dashboards),
                'recent_metrics': recent_metrics,
                'system_status': 'running' if self.running else 'stopped',
                'last_updated': datetime.datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur résumé analytics: {e}")
            return {}

# Instance globale
advanced_analytics = AdvancedAnalyticsDashboard()

if __name__ == "__main__":
    # Test du système d'analytics
    analytics = AdvancedAnalyticsDashboard()
    
    # Ajouter des métriques de test
    import random
    for i in range(100):
        analytics.add_metric("cpu_percent", random.uniform(20, 90), metric_type=MetricType.GAUGE, unit="%")
        analytics.add_metric("memory_percent", random.uniform(30, 85), metric_type=MetricType.GAUGE, unit="%")
        analytics.add_metric("response_time", random.uniform(100, 2000), metric_type=MetricType.GAUGE, unit="ms")
        time.sleep(0.1)
    
    # Attendre un peu pour l'agrégation
    time.sleep(2)
    
    # Récupérer le résumé
    summary = analytics.get_analytics_summary()
    print(f"📊 Métriques totales: {summary['total_metrics']}")
    print(f"🤖 Modèles entraînés: {summary['trained_models']}")
    
    # Créer un graphique
    chart_json = analytics.create_chart("cpu_percent", "line", include_predictions=True)
    print(f"📈 Graphique généré: {len(chart_json)} caractères")
    
    # Arrêter les services
    analytics.stop_services()

