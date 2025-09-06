"""
Trend Detection - Système de Détection Avancée de Tendances
Détection et analyse des tendances pour le conseil stratégique
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
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import DBSCAN, KMeans
from sklearn.linear_model import LinearRegression
from scipy import stats
from scipy.signal import find_peaks
import warnings
warnings.filterwarnings('ignore')

# Configuration du logging
logging.basicConfig(level=logging.INFO)

class TrendType(Enum):
    """Types de tendances"""
    MARKET = "market"
    TECHNOLOGY = "technology"
    BUSINESS = "business"
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    STRATEGIC = "strategic"
    COMPETITIVE = "competitive"
    REGULATORY = "regulatory"
    SOCIAL = "social"
    ENVIRONMENTAL = "environmental"

class TrendDirection(Enum):
    """Directions de tendances"""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"
    CYCLICAL = "cyclical"
    SEASONAL = "seasonal"

class TrendStrength(Enum):
    """Force des tendances"""
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    VERY_STRONG = "very_strong"

class TrendImpact(Enum):
    """Impact des tendances"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class DataPoint:
    """Point de données pour l'analyse de tendances"""
    timestamp: datetime
    value: float
    source: str
    category: str
    metadata: Dict[str, Any]

@dataclass
class TrendPattern:
    """Pattern de tendance détecté"""
    pattern_id: str
    pattern_type: str
    start_date: datetime
    end_date: datetime
    duration_days: int
    strength: float
    confidence: float
    parameters: Dict[str, Any]
    detected_at: datetime

@dataclass
class TrendAlert:
    """Alerte de tendance"""
    alert_id: str
    trend_id: str
    alert_type: str
    severity: TrendImpact
    message: str
    recommendations: List[str]
    triggered_at: datetime
    expires_at: datetime

@dataclass
class TrendForecast:
    """Prévision de tendance"""
    forecast_id: str
    trend_id: str
    forecast_horizon: int  # en jours
    predicted_values: List[float]
    confidence_intervals: List[Tuple[float, float]]
    forecast_accuracy: float
    methodology: str
    created_at: datetime

@dataclass
class DetectedTrend:
    """Tendance détectée"""
    trend_id: str
    trend_name: str
    trend_type: TrendType
    direction: TrendDirection
    strength: TrendStrength
    impact: TrendImpact
    confidence: float
    start_date: datetime
    detection_date: datetime
    data_points_count: int
    key_indicators: List[str]
    correlation_factors: Dict[str, float]
    patterns: List[TrendPattern]
    forecasts: List[TrendForecast]
    alerts: List[TrendAlert]
    metadata: Dict[str, Any]

class TrendDetection:
    """
    Système de Détection Avancée de Tendances
    Détection, analyse et prévision des tendances pour le conseil
    """
    
    def __init__(self, data_path: str = None):
        self.system_id = str(uuid.uuid4())
        self.logger = logging.getLogger(f"TrendDetection-{self.system_id[:8]}")
        
        # Chemins de données
        self.data_path = data_path or '/home/ubuntu/substans_ai_megacabinet/data/trends'
        self.db_path = os.path.join(self.data_path, 'trends.db')
        
        # Création des répertoires
        os.makedirs(self.data_path, exist_ok=True)
        
        # Données et tendances
        self.data_points = []
        self.detected_trends = {}
        self.trend_patterns = {}
        self.trend_alerts = {}
        self.trend_forecasts = {}
        
        # Configuration de détection
        self.detection_config = {
            'min_data_points': 10,
            'trend_window_days': 30,
            'volatility_threshold': 0.2,
            'correlation_threshold': 0.7,
            'confidence_threshold': 0.6,
            'forecast_horizon': 30,
            'alert_thresholds': {
                TrendImpact.LOW: 0.3,
                TrendImpact.MEDIUM: 0.5,
                TrendImpact.HIGH: 0.7,
                TrendImpact.CRITICAL: 0.9
            }
        }
        
        # Algorithmes de détection
        self.detection_algorithms = {
            'linear_trend': self._detect_linear_trend,
            'seasonal_trend': self._detect_seasonal_trend,
            'cyclical_trend': self._detect_cyclical_trend,
            'breakpoint_trend': self._detect_breakpoint_trend,
            'volatility_trend': self._detect_volatility_trend
        }
        
        # Modèles de prévision
        self.forecast_models = {}
        
        # Cache et optimisations
        self.analysis_cache = {}
        self.cache_ttl = 3600  # 1 heure
        
        # Statistiques
        self.system_stats = {
            'total_data_points': 0,
            'trends_detected': 0,
            'patterns_identified': 0,
            'alerts_generated': 0,
            'forecasts_created': 0,
            'detection_accuracy': 0.0,
            'processing_time_avg': 0.0
        }
        
        # Services
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.auto_detection = True
        self.real_time_monitoring = True
        
        # Base de données
        self._initialize_database()
        
        # Chargement des données existantes
        self._load_existing_data()
        
        # Génération de données de test
        self._generate_sample_data()
        
        # Démarrage des services
        self._start_services()
        
        self.logger.info(f"Détection de Tendances initialisée - ID: {self.system_id}")

    def _initialize_database(self):
        """Initialise la base de données"""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Table des points de données
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS data_points (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP NOT NULL,
                    value REAL NOT NULL,
                    source TEXT NOT NULL,
                    category TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table des tendances détectées
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS detected_trends (
                    trend_id TEXT PRIMARY KEY,
                    trend_name TEXT NOT NULL,
                    trend_type TEXT NOT NULL,
                    direction TEXT NOT NULL,
                    strength TEXT NOT NULL,
                    impact TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    start_date TIMESTAMP NOT NULL,
                    detection_date TIMESTAMP NOT NULL,
                    data_points_count INTEGER,
                    key_indicators TEXT,
                    correlation_factors TEXT,
                    metadata TEXT
                )
            ''')
            
            # Table des patterns
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trend_patterns (
                    pattern_id TEXT PRIMARY KEY,
                    pattern_type TEXT NOT NULL,
                    start_date TIMESTAMP NOT NULL,
                    end_date TIMESTAMP NOT NULL,
                    duration_days INTEGER,
                    strength REAL NOT NULL,
                    confidence REAL NOT NULL,
                    parameters TEXT,
                    detected_at TIMESTAMP NOT NULL
                )
            ''')
            
            # Table des alertes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trend_alerts (
                    alert_id TEXT PRIMARY KEY,
                    trend_id TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    recommendations TEXT,
                    triggered_at TIMESTAMP NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (trend_id) REFERENCES detected_trends (trend_id)
                )
            ''')
            
            # Table des prévisions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trend_forecasts (
                    forecast_id TEXT PRIMARY KEY,
                    trend_id TEXT NOT NULL,
                    forecast_horizon INTEGER NOT NULL,
                    predicted_values TEXT NOT NULL,
                    confidence_intervals TEXT,
                    forecast_accuracy REAL,
                    methodology TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (trend_id) REFERENCES detected_trends (trend_id)
                )
            ''')
            
            # Index pour les performances
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_data_points_timestamp 
                ON data_points(timestamp)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_trends_detection_date 
                ON detected_trends(detection_date)
            ''')
            
            conn.commit()

    def _generate_sample_data(self):
        """Génère des données d'exemple pour les tests"""
        
        # Génération de données de marché
        base_date = datetime.now() - timedelta(days=90)
        
        # Tendance croissante avec bruit
        for i in range(90):
            date = base_date + timedelta(days=i)
            
            # Tendance de marché tech
            trend_value = 100 + i * 0.5 + np.random.normal(0, 5)
            self.add_data_point(date, trend_value, "market_analysis", "technology")
            
            # Tendance financière
            financial_value = 1000 + i * 2 + np.random.normal(0, 20)
            self.add_data_point(date, financial_value, "financial_analysis", "revenue")
            
            # Tendance cyclique
            cyclical_value = 50 + 20 * np.sin(2 * np.pi * i / 30) + np.random.normal(0, 3)
            self.add_data_point(date, cyclical_value, "operational_metrics", "performance")
        
        self.logger.info("Données d'exemple générées")

    def add_data_point(self, timestamp: datetime, value: float, source: str, 
                      category: str, metadata: Dict[str, Any] = None):
        """Ajoute un point de données"""
        
        data_point = DataPoint(
            timestamp=timestamp,
            value=value,
            source=source,
            category=category,
            metadata=metadata or {}
        )
        
        self.data_points.append(data_point)
        self.system_stats['total_data_points'] += 1
        
        # Sauvegarde en base
        self._save_data_point(data_point)
        
        # Déclenchement de la détection en temps réel
        if self.real_time_monitoring and len(self.data_points) > self.detection_config['min_data_points']:
            self.executor.submit(self._trigger_real_time_detection, category)

    def detect_trends(self, category: str = None, time_window: int = None) -> List[DetectedTrend]:
        """Détecte les tendances dans les données"""
        
        start_time = time.time()
        
        # Filtrage des données
        filtered_data = self._filter_data_points(category, time_window)
        
        if len(filtered_data) < self.detection_config['min_data_points']:
            self.logger.warning(f"Pas assez de données pour la détection ({len(filtered_data)} points)")
            return []
        
        detected_trends = []
        
        # Application des algorithmes de détection
        for algo_name, algo_func in self.detection_algorithms.items():
            try:
                trends = algo_func(filtered_data)
                detected_trends.extend(trends)
            except Exception as e:
                self.logger.error(f"Erreur algorithme {algo_name}: {e}")
        
        # Déduplication et consolidation
        consolidated_trends = self._consolidate_trends(detected_trends)
        
        # Génération des patterns
        for trend in consolidated_trends:
            patterns = self._identify_patterns(trend, filtered_data)
            trend.patterns = patterns
            
            # Génération des prévisions
            forecasts = self._generate_forecasts(trend, filtered_data)
            trend.forecasts = forecasts
            
            # Génération des alertes
            alerts = self._generate_alerts(trend)
            trend.alerts = alerts
            
            # Sauvegarde
            self.detected_trends[trend.trend_id] = trend
            self._save_detected_trend(trend)
        
        # Mise à jour des statistiques
        processing_time = time.time() - start_time
        self.system_stats['trends_detected'] += len(consolidated_trends)
        self.system_stats['processing_time_avg'] = (
            (self.system_stats['processing_time_avg'] + processing_time) / 2
        )
        
        self.logger.info(f"{len(consolidated_trends)} tendances détectées en {processing_time:.2f}s")
        
        return consolidated_trends

    def _detect_linear_trend(self, data_points: List[DataPoint]) -> List[DetectedTrend]:
        """Détecte les tendances linéaires"""
        
        if len(data_points) < 5:
            return []
        
        # Préparation des données
        timestamps = [(dp.timestamp - data_points[0].timestamp).total_seconds() / 86400 
                     for dp in data_points]
        values = [dp.value for dp in data_points]
        
        # Régression linéaire
        X = np.array(timestamps).reshape(-1, 1)
        y = np.array(values)
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Calcul des métriques
        r2_score = model.score(X, y)
        slope = model.coef_[0]
        
        # Détermination de la direction
        if abs(slope) < 0.1:
            direction = TrendDirection.STABLE
            strength = TrendStrength.WEAK
        elif slope > 0:
            direction = TrendDirection.INCREASING
            strength = TrendStrength.STRONG if abs(slope) > 1 else TrendStrength.MODERATE
        else:
            direction = TrendDirection.DECREASING
            strength = TrendStrength.STRONG if abs(slope) > 1 else TrendStrength.MODERATE
        
        # Évaluation de l'impact
        value_range = max(values) - min(values)
        relative_change = abs(slope * len(timestamps)) / (sum(values) / len(values))
        
        if relative_change > 0.5:
            impact = TrendImpact.HIGH
        elif relative_change > 0.2:
            impact = TrendImpact.MEDIUM
        else:
            impact = TrendImpact.LOW
        
        # Confiance basée sur R²
        confidence = min(0.95, max(0.1, r2_score))
        
        if confidence < self.detection_config['confidence_threshold']:
            return []
        
        # Création de la tendance
        trend = DetectedTrend(
            trend_id=str(uuid.uuid4()),
            trend_name=f"Tendance linéaire {direction.value}",
            trend_type=TrendType.BUSINESS,
            direction=direction,
            strength=strength,
            impact=impact,
            confidence=confidence,
            start_date=data_points[0].timestamp,
            detection_date=datetime.now(),
            data_points_count=len(data_points),
            key_indicators=['slope', 'r2_score', 'relative_change'],
            correlation_factors={'slope': slope, 'r2_score': r2_score, 'relative_change': relative_change},
            patterns=[],
            forecasts=[],
            alerts=[],
            metadata={
                'algorithm': 'linear_trend',
                'slope': slope,
                'intercept': model.intercept_,
                'r2_score': r2_score,
                'value_range': value_range
            }
        )
        
        return [trend]

    def _detect_seasonal_trend(self, data_points: List[DataPoint]) -> List[DetectedTrend]:
        """Détecte les tendances saisonnières"""
        
        if len(data_points) < 30:  # Besoin d'au moins un mois de données
            return []
        
        values = [dp.value for dp in data_points]
        
        # Analyse de Fourier pour détecter la périodicité
        fft = np.fft.fft(values)
        frequencies = np.fft.fftfreq(len(values))
        
        # Recherche des pics de fréquence
        magnitude = np.abs(fft)
        peaks, _ = find_peaks(magnitude[1:len(magnitude)//2], height=np.max(magnitude) * 0.1)
        
        if len(peaks) == 0:
            return []
        
        # Période dominante
        dominant_freq_idx = peaks[np.argmax(magnitude[peaks + 1])]
        period = 1 / abs(frequencies[dominant_freq_idx + 1])
        
        # Vérification de la saisonnalité
        if period < 7 or period > 365:  # Entre une semaine et un an
            return []
        
        # Calcul de l'amplitude saisonnière
        seasonal_amplitude = np.std(values) / np.mean(values)
        
        # Force de la tendance saisonnière
        if seasonal_amplitude > 0.3:
            strength = TrendStrength.STRONG
            impact = TrendImpact.HIGH
        elif seasonal_amplitude > 0.15:
            strength = TrendStrength.MODERATE
            impact = TrendImpact.MEDIUM
        else:
            strength = TrendStrength.WEAK
            impact = TrendImpact.LOW
        
        confidence = min(0.9, seasonal_amplitude * 2)
        
        if confidence < self.detection_config['confidence_threshold']:
            return []
        
        trend = DetectedTrend(
            trend_id=str(uuid.uuid4()),
            trend_name=f"Tendance saisonnière (période: {period:.1f} jours)",
            trend_type=TrendType.OPERATIONAL,
            direction=TrendDirection.SEASONAL,
            strength=strength,
            impact=impact,
            confidence=confidence,
            start_date=data_points[0].timestamp,
            detection_date=datetime.now(),
            data_points_count=len(data_points),
            key_indicators=['period', 'amplitude', 'seasonal_strength'],
            correlation_factors={'period': period, 'amplitude': seasonal_amplitude},
            patterns=[],
            forecasts=[],
            alerts=[],
            metadata={
                'algorithm': 'seasonal_trend',
                'period_days': period,
                'seasonal_amplitude': seasonal_amplitude,
                'dominant_frequency': frequencies[dominant_freq_idx + 1]
            }
        )
        
        return [trend]

    def _detect_cyclical_trend(self, data_points: List[DataPoint]) -> List[DetectedTrend]:
        """Détecte les tendances cycliques"""
        
        if len(data_points) < 20:
            return []
        
        values = np.array([dp.value for dp in data_points])
        
        # Détection de cycles par autocorrélation
        autocorr = np.correlate(values, values, mode='full')
        autocorr = autocorr[autocorr.size // 2:]
        
        # Normalisation
        autocorr = autocorr / autocorr[0]
        
        # Recherche de pics d'autocorrélation
        peaks, properties = find_peaks(autocorr[1:], height=0.3, distance=5)
        
        if len(peaks) == 0:
            return []
        
        # Cycle dominant
        cycle_length = peaks[0] + 1
        cycle_strength = autocorr[peaks[0] + 1]
        
        # Évaluation de la force cyclique
        if cycle_strength > 0.7:
            strength = TrendStrength.STRONG
            impact = TrendImpact.HIGH
        elif cycle_strength > 0.5:
            strength = TrendStrength.MODERATE
            impact = TrendImpact.MEDIUM
        else:
            strength = TrendStrength.WEAK
            impact = TrendImpact.LOW
        
        confidence = cycle_strength
        
        if confidence < self.detection_config['confidence_threshold']:
            return []
        
        trend = DetectedTrend(
            trend_id=str(uuid.uuid4()),
            trend_name=f"Tendance cyclique (cycle: {cycle_length} points)",
            trend_type=TrendType.MARKET,
            direction=TrendDirection.CYCLICAL,
            strength=strength,
            impact=impact,
            confidence=confidence,
            start_date=data_points[0].timestamp,
            detection_date=datetime.now(),
            data_points_count=len(data_points),
            key_indicators=['cycle_length', 'cycle_strength', 'autocorrelation'],
            correlation_factors={'cycle_length': cycle_length, 'cycle_strength': cycle_strength},
            patterns=[],
            forecasts=[],
            alerts=[],
            metadata={
                'algorithm': 'cyclical_trend',
                'cycle_length': cycle_length,
                'cycle_strength': cycle_strength,
                'autocorrelation_peaks': len(peaks)
            }
        )
        
        return [trend]

    def _detect_breakpoint_trend(self, data_points: List[DataPoint]) -> List[DetectedTrend]:
        """Détecte les points de rupture dans les tendances"""
        
        if len(data_points) < 15:
            return []
        
        values = np.array([dp.value for dp in data_points])
        
        # Détection de points de rupture par segmentation
        breakpoints = []
        window_size = min(10, len(values) // 3)
        
        for i in range(window_size, len(values) - window_size):
            # Comparaison des moyennes avant/après
            before_mean = np.mean(values[i-window_size:i])
            after_mean = np.mean(values[i:i+window_size])
            
            # Test statistique
            t_stat, p_value = stats.ttest_ind(
                values[i-window_size:i], 
                values[i:i+window_size]
            )
            
            # Critère de rupture significative
            if p_value < 0.05 and abs(after_mean - before_mean) > np.std(values) * 0.5:
                breakpoints.append({
                    'index': i,
                    'timestamp': data_points[i].timestamp,
                    'before_mean': before_mean,
                    'after_mean': after_mean,
                    'change_magnitude': abs(after_mean - before_mean),
                    'p_value': p_value
                })
        
        if len(breakpoints) == 0:
            return []
        
        # Sélection du point de rupture le plus significatif
        main_breakpoint = max(breakpoints, key=lambda x: x['change_magnitude'])
        
        # Détermination de la direction du changement
        if main_breakpoint['after_mean'] > main_breakpoint['before_mean']:
            direction = TrendDirection.INCREASING
        else:
            direction = TrendDirection.DECREASING
        
        # Force basée sur l'ampleur du changement
        relative_change = main_breakpoint['change_magnitude'] / np.mean(values)
        
        if relative_change > 0.5:
            strength = TrendStrength.VERY_STRONG
            impact = TrendImpact.CRITICAL
        elif relative_change > 0.3:
            strength = TrendStrength.STRONG
            impact = TrendImpact.HIGH
        elif relative_change > 0.15:
            strength = TrendStrength.MODERATE
            impact = TrendImpact.MEDIUM
        else:
            strength = TrendStrength.WEAK
            impact = TrendImpact.LOW
        
        confidence = 1 - main_breakpoint['p_value']
        
        trend = DetectedTrend(
            trend_id=str(uuid.uuid4()),
            trend_name=f"Point de rupture {direction.value}",
            trend_type=TrendType.STRATEGIC,
            direction=direction,
            strength=strength,
            impact=impact,
            confidence=confidence,
            start_date=main_breakpoint['timestamp'],
            detection_date=datetime.now(),
            data_points_count=len(data_points),
            key_indicators=['breakpoint_magnitude', 'statistical_significance', 'relative_change'],
            correlation_factors={
                'change_magnitude': main_breakpoint['change_magnitude'],
                'relative_change': relative_change,
                'p_value': main_breakpoint['p_value']
            },
            patterns=[],
            forecasts=[],
            alerts=[],
            metadata={
                'algorithm': 'breakpoint_trend',
                'breakpoint_index': main_breakpoint['index'],
                'breakpoint_timestamp': main_breakpoint['timestamp'].isoformat(),
                'before_mean': main_breakpoint['before_mean'],
                'after_mean': main_breakpoint['after_mean'],
                'total_breakpoints': len(breakpoints)
            }
        )
        
        return [trend]

    def _detect_volatility_trend(self, data_points: List[DataPoint]) -> List[DetectedTrend]:
        """Détecte les tendances de volatilité"""
        
        if len(data_points) < 10:
            return []
        
        values = np.array([dp.value for dp in data_points])
        
        # Calcul de la volatilité mobile
        window_size = min(10, len(values) // 2)
        volatilities = []
        
        for i in range(window_size, len(values)):
            window_values = values[i-window_size:i]
            volatility = np.std(window_values) / np.mean(window_values)
            volatilities.append(volatility)
        
        if len(volatilities) < 5:
            return []
        
        # Tendance de la volatilité
        X = np.arange(len(volatilities)).reshape(-1, 1)
        y = np.array(volatilities)
        
        model = LinearRegression()
        model.fit(X, y)
        
        volatility_trend = model.coef_[0]
        r2_score = model.score(X, y)
        
        # Classification de la volatilité
        avg_volatility = np.mean(volatilities)
        
        if avg_volatility > self.detection_config['volatility_threshold']:
            if volatility_trend > 0.01:
                direction = TrendDirection.VOLATILE
                trend_name = "Volatilité croissante"
            elif volatility_trend < -0.01:
                direction = TrendDirection.STABLE
                trend_name = "Volatilité décroissante"
            else:
                direction = TrendDirection.VOLATILE
                trend_name = "Haute volatilité"
        else:
            direction = TrendDirection.STABLE
            trend_name = "Faible volatilité"
        
        # Force basée sur le niveau de volatilité
        if avg_volatility > 0.4:
            strength = TrendStrength.VERY_STRONG
            impact = TrendImpact.CRITICAL
        elif avg_volatility > 0.3:
            strength = TrendStrength.STRONG
            impact = TrendImpact.HIGH
        elif avg_volatility > 0.2:
            strength = TrendStrength.MODERATE
            impact = TrendImpact.MEDIUM
        else:
            strength = TrendStrength.WEAK
            impact = TrendImpact.LOW
        
        confidence = min(0.9, r2_score + avg_volatility)
        
        if confidence < self.detection_config['confidence_threshold']:
            return []
        
        trend = DetectedTrend(
            trend_id=str(uuid.uuid4()),
            trend_name=trend_name,
            trend_type=TrendType.FINANCIAL,
            direction=direction,
            strength=strength,
            impact=impact,
            confidence=confidence,
            start_date=data_points[window_size].timestamp,
            detection_date=datetime.now(),
            data_points_count=len(data_points),
            key_indicators=['average_volatility', 'volatility_trend', 'stability'],
            correlation_factors={
                'avg_volatility': avg_volatility,
                'volatility_trend': volatility_trend,
                'r2_score': r2_score
            },
            patterns=[],
            forecasts=[],
            alerts=[],
            metadata={
                'algorithm': 'volatility_trend',
                'average_volatility': avg_volatility,
                'volatility_trend': volatility_trend,
                'window_size': window_size
            }
        )
        
        return [trend]

    def _consolidate_trends(self, trends: List[DetectedTrend]) -> List[DetectedTrend]:
        """Consolide les tendances similaires"""
        
        if len(trends) <= 1:
            return trends
        
        consolidated = []
        used_indices = set()
        
        for i, trend1 in enumerate(trends):
            if i in used_indices:
                continue
            
            similar_trends = [trend1]
            used_indices.add(i)
            
            for j, trend2 in enumerate(trends[i+1:], i+1):
                if j in used_indices:
                    continue
                
                # Critères de similarité
                same_type = trend1.trend_type == trend2.trend_type
                same_direction = trend1.direction == trend2.direction
                time_overlap = abs((trend1.start_date - trend2.start_date).days) < 7
                
                if same_type and same_direction and time_overlap:
                    similar_trends.append(trend2)
                    used_indices.add(j)
            
            # Consolidation des tendances similaires
            if len(similar_trends) > 1:
                consolidated_trend = self._merge_trends(similar_trends)
                consolidated.append(consolidated_trend)
            else:
                consolidated.append(trend1)
        
        return consolidated

    def _merge_trends(self, trends: List[DetectedTrend]) -> DetectedTrend:
        """Fusionne plusieurs tendances similaires"""
        
        # Tendance avec la plus haute confiance comme base
        base_trend = max(trends, key=lambda t: t.confidence)
        
        # Agrégation des métriques
        avg_confidence = sum(t.confidence for t in trends) / len(trends)
        total_data_points = sum(t.data_points_count for t in trends)
        earliest_start = min(t.start_date for t in trends)
        
        # Force maximale
        strength_values = {'weak': 1, 'moderate': 2, 'strong': 3, 'very_strong': 4}
        max_strength_value = max(strength_values[t.strength.value] for t in trends)
        max_strength = [k for k, v in strength_values.items() if v == max_strength_value][0]
        
        # Impact maximal
        impact_values = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
        max_impact_value = max(impact_values[t.impact.value] for t in trends)
        max_impact = [k for k, v in impact_values.items() if v == max_impact_value][0]
        
        # Fusion des facteurs de corrélation
        merged_factors = {}
        for trend in trends:
            for factor, value in trend.correlation_factors.items():
                if factor in merged_factors:
                    merged_factors[factor] = (merged_factors[factor] + value) / 2
                else:
                    merged_factors[factor] = value
        
        # Création de la tendance fusionnée
        merged_trend = DetectedTrend(
            trend_id=str(uuid.uuid4()),
            trend_name=f"{base_trend.trend_name} (consolidée)",
            trend_type=base_trend.trend_type,
            direction=base_trend.direction,
            strength=TrendStrength(max_strength),
            impact=TrendImpact(max_impact),
            confidence=avg_confidence,
            start_date=earliest_start,
            detection_date=datetime.now(),
            data_points_count=total_data_points,
            key_indicators=list(set().union(*(t.key_indicators for t in trends))),
            correlation_factors=merged_factors,
            patterns=[],
            forecasts=[],
            alerts=[],
            metadata={
                'consolidated_from': len(trends),
                'source_algorithms': list(set(t.metadata.get('algorithm', 'unknown') for t in trends)),
                'original_trend_ids': [t.trend_id for t in trends]
            }
        )
        
        return merged_trend

    def _identify_patterns(self, trend: DetectedTrend, data_points: List[DataPoint]) -> List[TrendPattern]:
        """Identifie les patterns dans une tendance"""
        
        patterns = []
        
        # Pattern de croissance accélérée
        if trend.direction == TrendDirection.INCREASING:
            acceleration_pattern = self._detect_acceleration_pattern(data_points)
            if acceleration_pattern:
                patterns.append(acceleration_pattern)
        
        # Pattern de stabilisation
        if trend.strength == TrendStrength.WEAK:
            stabilization_pattern = self._detect_stabilization_pattern(data_points)
            if stabilization_pattern:
                patterns.append(stabilization_pattern)
        
        # Pattern de récurrence
        recurrence_pattern = self._detect_recurrence_pattern(data_points)
        if recurrence_pattern:
            patterns.append(recurrence_pattern)
        
        # Sauvegarde des patterns
        for pattern in patterns:
            self.trend_patterns[pattern.pattern_id] = pattern
            self._save_trend_pattern(pattern)
        
        self.system_stats['patterns_identified'] += len(patterns)
        
        return patterns

    def _detect_acceleration_pattern(self, data_points: List[DataPoint]) -> Optional[TrendPattern]:
        """Détecte un pattern d'accélération"""
        
        if len(data_points) < 10:
            return None
        
        values = [dp.value for dp in data_points]
        
        # Calcul des dérivées secondes (accélération)
        first_diff = np.diff(values)
        second_diff = np.diff(first_diff)
        
        # Test d'accélération significative
        if len(second_diff) > 0 and np.mean(second_diff) > np.std(values) * 0.1:
            return TrendPattern(
                pattern_id=str(uuid.uuid4()),
                pattern_type="acceleration",
                start_date=data_points[0].timestamp,
                end_date=data_points[-1].timestamp,
                duration_days=(data_points[-1].timestamp - data_points[0].timestamp).days,
                strength=min(1.0, abs(np.mean(second_diff)) / np.std(values)),
                confidence=0.8,
                parameters={'acceleration_rate': np.mean(second_diff)},
                detected_at=datetime.now()
            )
        
        return None

    def _detect_stabilization_pattern(self, data_points: List[DataPoint]) -> Optional[TrendPattern]:
        """Détecte un pattern de stabilisation"""
        
        if len(data_points) < 15:
            return None
        
        values = np.array([dp.value for dp in data_points])
        
        # Test de stabilité sur la fin de la série
        recent_values = values[-10:]
        stability_coefficient = np.std(recent_values) / np.mean(recent_values)
        
        if stability_coefficient < 0.05:  # Très stable
            return TrendPattern(
                pattern_id=str(uuid.uuid4()),
                pattern_type="stabilization",
                start_date=data_points[-10].timestamp,
                end_date=data_points[-1].timestamp,
                duration_days=10,
                strength=1.0 - stability_coefficient * 10,
                confidence=0.9,
                parameters={'stability_coefficient': stability_coefficient},
                detected_at=datetime.now()
            )
        
        return None

    def _detect_recurrence_pattern(self, data_points: List[DataPoint]) -> Optional[TrendPattern]:
        """Détecte un pattern de récurrence"""
        
        if len(data_points) < 20:
            return None
        
        values = np.array([dp.value for dp in data_points])
        
        # Recherche de motifs récurrents par autocorrélation
        autocorr = np.correlate(values, values, mode='full')
        autocorr = autocorr[autocorr.size // 2:]
        autocorr = autocorr / autocorr[0]
        
        # Recherche de pics significatifs
        peaks, _ = find_peaks(autocorr[1:], height=0.5, distance=3)
        
        if len(peaks) > 0:
            recurrence_period = peaks[0] + 1
            recurrence_strength = autocorr[peaks[0] + 1]
            
            return TrendPattern(
                pattern_id=str(uuid.uuid4()),
                pattern_type="recurrence",
                start_date=data_points[0].timestamp,
                end_date=data_points[-1].timestamp,
                duration_days=(data_points[-1].timestamp - data_points[0].timestamp).days,
                strength=recurrence_strength,
                confidence=0.7,
                parameters={
                    'recurrence_period': recurrence_period,
                    'recurrence_strength': recurrence_strength
                },
                detected_at=datetime.now()
            )
        
        return None

    def _generate_forecasts(self, trend: DetectedTrend, data_points: List[DataPoint]) -> List[TrendForecast]:
        """Génère des prévisions pour une tendance"""
        
        forecasts = []
        
        # Prévision linéaire simple
        linear_forecast = self._create_linear_forecast(trend, data_points)
        if linear_forecast:
            forecasts.append(linear_forecast)
        
        # Sauvegarde des prévisions
        for forecast in forecasts:
            self.trend_forecasts[forecast.forecast_id] = forecast
            self._save_trend_forecast(forecast)
        
        self.system_stats['forecasts_created'] += len(forecasts)
        
        return forecasts

    def _create_linear_forecast(self, trend: DetectedTrend, data_points: List[DataPoint]) -> Optional[TrendForecast]:
        """Crée une prévision linéaire"""
        
        if len(data_points) < 5:
            return None
        
        # Préparation des données
        timestamps = [(dp.timestamp - data_points[0].timestamp).total_seconds() / 86400 
                     for dp in data_points]
        values = [dp.value for dp in data_points]
        
        # Modèle de régression
        X = np.array(timestamps).reshape(-1, 1)
        y = np.array(values)
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Génération des prévisions
        horizon = self.detection_config['forecast_horizon']
        future_timestamps = np.arange(len(timestamps), len(timestamps) + horizon).reshape(-1, 1)
        predicted_values = model.predict(future_timestamps).tolist()
        
        # Intervalles de confiance (estimation simplifiée)
        prediction_std = np.std(y - model.predict(X))
        confidence_intervals = [
            (pred - 1.96 * prediction_std, pred + 1.96 * prediction_std)
            for pred in predicted_values
        ]
        
        # Précision basée sur R²
        forecast_accuracy = model.score(X, y)
        
        return TrendForecast(
            forecast_id=str(uuid.uuid4()),
            trend_id=trend.trend_id,
            forecast_horizon=horizon,
            predicted_values=predicted_values,
            confidence_intervals=confidence_intervals,
            forecast_accuracy=forecast_accuracy,
            methodology="linear_regression",
            created_at=datetime.now()
        )

    def _generate_alerts(self, trend: DetectedTrend) -> List[TrendAlert]:
        """Génère des alertes pour une tendance"""
        
        alerts = []
        
        # Alerte d'impact critique
        if trend.impact == TrendImpact.CRITICAL:
            alert = TrendAlert(
                alert_id=str(uuid.uuid4()),
                trend_id=trend.trend_id,
                alert_type="critical_impact",
                severity=TrendImpact.CRITICAL,
                message=f"Tendance critique détectée: {trend.trend_name}",
                recommendations=[
                    "Analyse immédiate requise",
                    "Évaluation de l'impact business",
                    "Plan d'action urgent"
                ],
                triggered_at=datetime.now(),
                expires_at=datetime.now() + timedelta(days=7)
            )
            alerts.append(alert)
        
        # Alerte de changement de direction
        if trend.strength in [TrendStrength.STRONG, TrendStrength.VERY_STRONG]:
            alert = TrendAlert(
                alert_id=str(uuid.uuid4()),
                trend_id=trend.trend_id,
                alert_type="strong_trend",
                severity=trend.impact,
                message=f"Tendance forte détectée: {trend.direction.value}",
                recommendations=[
                    "Surveillance renforcée",
                    "Adaptation stratégique",
                    "Communication aux parties prenantes"
                ],
                triggered_at=datetime.now(),
                expires_at=datetime.now() + timedelta(days=14)
            )
            alerts.append(alert)
        
        # Sauvegarde des alertes
        for alert in alerts:
            self.trend_alerts[alert.alert_id] = alert
            self._save_trend_alert(alert)
        
        self.system_stats['alerts_generated'] += len(alerts)
        
        return alerts

    def _filter_data_points(self, category: str = None, time_window: int = None) -> List[DataPoint]:
        """Filtre les points de données selon les critères"""
        
        filtered = self.data_points.copy()
        
        # Filtre par catégorie
        if category:
            filtered = [dp for dp in filtered if dp.category == category]
        
        # Filtre par fenêtre temporelle
        if time_window:
            cutoff_date = datetime.now() - timedelta(days=time_window)
            filtered = [dp for dp in filtered if dp.timestamp >= cutoff_date]
        
        # Tri par timestamp
        filtered.sort(key=lambda dp: dp.timestamp)
        
        return filtered

    def _trigger_real_time_detection(self, category: str):
        """Déclenche la détection en temps réel"""
        
        try:
            trends = self.detect_trends(category=category, time_window=30)
            
            if trends:
                self.logger.info(f"Détection temps réel: {len(trends)} tendances pour {category}")
        
        except Exception as e:
            self.logger.error(f"Erreur détection temps réel: {e}")

    def _save_data_point(self, data_point: DataPoint):
        """Sauvegarde un point de données"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO data_points (timestamp, value, source, category, metadata)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    data_point.timestamp, data_point.value, data_point.source,
                    data_point.category, json.dumps(data_point.metadata)
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde point de données: {e}")

    def _save_detected_trend(self, trend: DetectedTrend):
        """Sauvegarde une tendance détectée"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO detected_trends 
                    (trend_id, trend_name, trend_type, direction, strength, impact,
                     confidence, start_date, detection_date, data_points_count,
                     key_indicators, correlation_factors, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    trend.trend_id, trend.trend_name, trend.trend_type.value,
                    trend.direction.value, trend.strength.value, trend.impact.value,
                    trend.confidence, trend.start_date, trend.detection_date,
                    trend.data_points_count, json.dumps(trend.key_indicators),
                    json.dumps(trend.correlation_factors), json.dumps(trend.metadata)
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde tendance: {e}")

    def _save_trend_pattern(self, pattern: TrendPattern):
        """Sauvegarde un pattern de tendance"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO trend_patterns 
                    (pattern_id, pattern_type, start_date, end_date, duration_days,
                     strength, confidence, parameters, detected_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    pattern.pattern_id, pattern.pattern_type, pattern.start_date,
                    pattern.end_date, pattern.duration_days, pattern.strength,
                    pattern.confidence, json.dumps(pattern.parameters), pattern.detected_at
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde pattern: {e}")

    def _save_trend_alert(self, alert: TrendAlert):
        """Sauvegarde une alerte de tendance"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO trend_alerts 
                    (alert_id, trend_id, alert_type, severity, message,
                     recommendations, triggered_at, expires_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    alert.alert_id, alert.trend_id, alert.alert_type,
                    alert.severity.value, alert.message,
                    json.dumps(alert.recommendations), alert.triggered_at, alert.expires_at
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde alerte: {e}")

    def _save_trend_forecast(self, forecast: TrendForecast):
        """Sauvegarde une prévision de tendance"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO trend_forecasts 
                    (forecast_id, trend_id, forecast_horizon, predicted_values,
                     confidence_intervals, forecast_accuracy, methodology, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    forecast.forecast_id, forecast.trend_id, forecast.forecast_horizon,
                    json.dumps(forecast.predicted_values),
                    json.dumps(forecast.confidence_intervals),
                    forecast.forecast_accuracy, forecast.methodology, forecast.created_at
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde prévision: {e}")

    def _load_existing_data(self):
        """Charge les données existantes"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Chargement des points de données récents
                cursor.execute('''
                    SELECT timestamp, value, source, category, metadata
                    FROM data_points
                    WHERE timestamp > datetime('now', '-90 days')
                    ORDER BY timestamp
                ''')
                
                for row in cursor.fetchall():
                    data_point = DataPoint(
                        timestamp=datetime.fromisoformat(row[0]),
                        value=row[1],
                        source=row[2],
                        category=row[3],
                        metadata=json.loads(row[4]) if row[4] else {}
                    )
                    self.data_points.append(data_point)
                
                self.system_stats['total_data_points'] = len(self.data_points)
                self.logger.info(f"{len(self.data_points)} points de données chargés")
                
        except Exception as e:
            self.logger.error(f"Erreur chargement données: {e}")

    def _start_services(self):
        """Démarre les services du système"""
        
        # Service de détection automatique
        if self.auto_detection:
            threading.Thread(target=self._auto_detection_service, daemon=True).start()
        
        # Service de nettoyage du cache
        threading.Thread(target=self._cache_cleanup_service, daemon=True).start()

    def _auto_detection_service(self):
        """Service de détection automatique"""
        
        while True:
            try:
                # Détection automatique toutes les heures
                categories = set(dp.category for dp in self.data_points)
                
                for category in categories:
                    self.detect_trends(category=category, time_window=30)
                
                time.sleep(3600)  # 1 heure
                
            except Exception as e:
                self.logger.error(f"Erreur service détection automatique: {e}")
                time.sleep(3600)

    def _cache_cleanup_service(self):
        """Service de nettoyage du cache"""
        
        while True:
            try:
                current_time = time.time()
                expired_keys = [
                    key for key, entry in self.analysis_cache.items()
                    if current_time - entry.get('timestamp', 0) > self.cache_ttl
                ]
                
                for key in expired_keys:
                    del self.analysis_cache[key]
                
                if expired_keys:
                    self.logger.info(f"{len(expired_keys)} entrées de cache expirées supprimées")
                
                time.sleep(1800)  # 30 minutes
                
            except Exception as e:
                self.logger.error(f"Erreur service nettoyage cache: {e}")
                time.sleep(1800)

    def get_trend_summary(self, trend_id: str = None) -> Dict[str, Any]:
        """Retourne un résumé des tendances"""
        
        if trend_id and trend_id in self.detected_trends:
            trend = self.detected_trends[trend_id]
            return {
                'trend_id': trend.trend_id,
                'trend_name': trend.trend_name,
                'type': trend.trend_type.value,
                'direction': trend.direction.value,
                'strength': trend.strength.value,
                'impact': trend.impact.value,
                'confidence': trend.confidence,
                'patterns_count': len(trend.patterns),
                'forecasts_count': len(trend.forecasts),
                'alerts_count': len(trend.alerts)
            }
        
        # Résumé global
        return {
            'total_trends': len(self.detected_trends),
            'trends_by_type': self._count_trends_by_type(),
            'trends_by_impact': self._count_trends_by_impact(),
            'active_alerts': len([a for a in self.trend_alerts.values() 
                                if a.expires_at > datetime.now()]),
            'recent_forecasts': len([f for f in self.trend_forecasts.values() 
                                   if f.created_at > datetime.now() - timedelta(days=7)]),
            'system_stats': self.system_stats
        }

    def _count_trends_by_type(self) -> Dict[str, int]:
        """Compte les tendances par type"""
        
        counts = {}
        for trend in self.detected_trends.values():
            trend_type = trend.trend_type.value
            counts[trend_type] = counts.get(trend_type, 0) + 1
        
        return counts

    def _count_trends_by_impact(self) -> Dict[str, int]:
        """Compte les tendances par impact"""
        
        counts = {}
        for trend in self.detected_trends.values():
            impact = trend.impact.value
            counts[impact] = counts.get(impact, 0) + 1
        
        return counts

    def get_system_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques du système"""
        
        return self.system_stats.copy()

# Instance globale
_trend_detection = None

def get_trend_detection() -> TrendDetection:
    """Retourne l'instance de détection de tendances"""
    global _trend_detection
    if _trend_detection is None:
        _trend_detection = TrendDetection()
    return _trend_detection

# Test du système
if __name__ == '__main__':
    print("=== Test Détection de Tendances ===")
    
    td = TrendDetection()
    
    # Ajout de quelques points de données
    base_date = datetime.now() - timedelta(days=5)
    for i in range(20):
        date = base_date + timedelta(hours=i*6)
        value = 100 + i * 2 + np.random.normal(0, 3)
        td.add_data_point(date, value, "test_source", "test_category")
    
    # Détection des tendances
    trends = td.detect_trends(category="test_category")
    print(f"Tendances détectées: {len(trends)}")
    
    for trend in trends:
        print(f"- {trend.trend_name}: {trend.direction.value} ({trend.confidence:.3f})")
        print(f"  Force: {trend.strength.value}, Impact: {trend.impact.value}")
        print(f"  Patterns: {len(trend.patterns)}, Alertes: {len(trend.alerts)}")
    
    # Résumé
    summary = td.get_trend_summary()
    print(f"Résumé: {summary['total_trends']} tendances totales")
    
    # Statistiques
    stats = td.get_system_statistics()
    print(f"Statistiques: {stats['total_data_points']} points de données")
    
    print("Test terminé avec succès")

