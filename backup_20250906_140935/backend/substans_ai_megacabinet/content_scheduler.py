"""
Content Scheduler - Système de Planification et Programmation de Publications
Module pour la planification automatisée de contenu sur les réseaux sociaux
Intégré avec le système de génération de contenu et l'intelligence quotidienne
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import hashlib
import os
from dataclasses import dataclass
from enum import Enum

class PublicationStatus(Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Platform(Enum):
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"

@dataclass
class ScheduledContent:
    id: str
    platform: Platform
    content: str
    scheduled_for: datetime
    status: PublicationStatus
    created_at: datetime
    content_type: str
    source_intelligence_id: str
    estimated_metrics: Dict[str, Any]
    retry_count: int = 0
    published_at: Optional[datetime] = None
    error_message: Optional[str] = None

class ContentScheduler:
    def __init__(self):
        self.name = "Content Scheduler"
        self.version = "1.0"
        self.scheduled_content = []
        self.publication_history = []
        self.scheduling_rules = self._initialize_scheduling_rules()
        self.platform_limits = self._initialize_platform_limits()
        
        print(f"🚀 {self.name} v{self.version} initialisé")
        print("✅ Règles de planification configurées")
        print("✅ Limites de plateformes définies")
        print("✅ Système de retry activé")
    
    def _initialize_scheduling_rules(self) -> Dict[str, Any]:
        """Initialise les règles de planification optimales"""
        return {
            "linkedin": {
                "optimal_times": {
                    "monday": ["08:00", "12:00", "17:00"],
                    "tuesday": ["08:00", "12:00", "17:00"],
                    "wednesday": ["08:00", "12:00", "17:00"],
                    "thursday": ["08:00", "12:00", "17:00"],
                    "friday": ["08:00", "12:00"],
                    "saturday": ["10:00"],
                    "sunday": ["19:00"]
                },
                "max_posts_per_day": 3,
                "min_interval_hours": 4,
                "best_days": ["tuesday", "wednesday", "thursday"],
                "avoid_times": ["22:00-06:00"],  # Éviter la nuit
                "content_spacing": {
                    "insight": 24,  # 24h entre insights
                    "market_update": 48,  # 48h entre mises à jour marché
                    "tech_breakthrough": 72  # 72h entre breakthroughs
                }
            },
            
            "twitter": {
                "optimal_times": {
                    "monday": ["09:00", "15:00", "21:00"],
                    "tuesday": ["09:00", "15:00", "21:00"],
                    "wednesday": ["09:00", "15:00", "21:00"],
                    "thursday": ["09:00", "15:00", "21:00"],
                    "friday": ["09:00", "15:00"],
                    "saturday": ["12:00", "17:00"],
                    "sunday": ["14:00", "20:00"]
                },
                "max_posts_per_day": 5,
                "min_interval_hours": 2,
                "best_days": ["tuesday", "wednesday", "thursday", "friday"],
                "avoid_times": ["02:00-07:00"],
                "content_spacing": {
                    "thread": 12,  # 12h entre threads
                    "single_tweet": 2,  # 2h entre tweets simples
                    "quote_tweet": 6  # 6h entre quote tweets
                }
            },
            
            "instagram": {
                "optimal_times": {
                    "monday": ["11:00", "14:00", "17:00"],
                    "tuesday": ["11:00", "14:00", "17:00"],
                    "wednesday": ["11:00", "14:00", "17:00"],
                    "thursday": ["11:00", "14:00", "17:00"],
                    "friday": ["11:00", "14:00"],
                    "saturday": ["12:00", "15:00"],
                    "sunday": ["12:00", "15:00"]
                },
                "max_posts_per_day": 2,
                "min_interval_hours": 6,
                "best_days": ["wednesday", "thursday", "friday", "saturday"],
                "avoid_times": ["23:00-08:00"],
                "content_spacing": {
                    "post": 24,  # 24h entre posts
                    "story": 4,  # 4h entre stories
                    "reel": 48  # 48h entre reels
                }
            },
            
            "facebook": {
                "optimal_times": {
                    "monday": ["09:00", "15:00"],
                    "tuesday": ["09:00", "15:00"],
                    "wednesday": ["09:00", "15:00"],
                    "thursday": ["09:00", "15:00"],
                    "friday": ["09:00", "15:00"],
                    "saturday": ["12:00", "15:00"],
                    "sunday": ["12:00", "15:00"]
                },
                "max_posts_per_day": 2,
                "min_interval_hours": 8,
                "best_days": ["tuesday", "wednesday", "thursday"],
                "avoid_times": ["22:00-08:00"],
                "content_spacing": {
                    "post": 48,  # 48h entre posts
                    "story": 12,  # 12h entre stories
                    "video": 72  # 72h entre vidéos
                }
            }
        }
    
    def _initialize_platform_limits(self) -> Dict[str, Any]:
        """Initialise les limites des plateformes"""
        return {
            "linkedin": {
                "daily_limit": 25,  # Limite API LinkedIn
                "monthly_limit": 500,
                "character_limit": 3000,
                "image_limit": 9,
                "video_limit": 1
            },
            "twitter": {
                "daily_limit": 300,  # Limite API Twitter
                "monthly_limit": 10000,
                "character_limit": 280,
                "image_limit": 4,
                "video_limit": 1
            },
            "instagram": {
                "daily_limit": 25,  # Limite recommandée
                "monthly_limit": 500,
                "character_limit": 2200,
                "image_limit": 10,
                "video_limit": 1
            },
            "facebook": {
                "daily_limit": 25,  # Limite recommandée
                "monthly_limit": 500,
                "character_limit": 63206,
                "image_limit": 10,
                "video_limit": 1
            }
        }
    
    def schedule_content(self, content: Dict[str, Any], 
                        target_datetime: Optional[datetime] = None,
                        auto_optimize: bool = True) -> Dict[str, Any]:
        """Programme un contenu pour publication"""
        
        platform = Platform(content["platform"])
        content_type = content.get("type", "post")
        
        # Optimisation automatique du timing si demandée
        if auto_optimize and target_datetime:
            optimized_datetime = self._optimize_scheduling_time(
                platform, content_type, target_datetime
            )
        elif auto_optimize:
            optimized_datetime = self._find_next_optimal_slot(platform, content_type)
        else:
            optimized_datetime = target_datetime or datetime.now() + timedelta(hours=1)
        
        # Vérification des conflits et limites
        validation_result = self._validate_scheduling(platform, optimized_datetime, content_type)
        
        if not validation_result["valid"]:
            return {
                "success": False,
                "error": validation_result["error"],
                "suggested_times": validation_result.get("suggested_times", [])
            }
        
        # Création de l'objet contenu programmé
        scheduled_content = ScheduledContent(
            id=f"SCHED_{platform.value.upper()}_{int(time.time())}",
            platform=platform,
            content=content["content"],
            scheduled_for=optimized_datetime,
            status=PublicationStatus.SCHEDULED,
            created_at=datetime.now(),
            content_type=content_type,
            source_intelligence_id=content.get("source_intelligence", "unknown"),
            estimated_metrics=content.get("estimated_metrics", {}),
            retry_count=0
        )
        
        self.scheduled_content.append(scheduled_content)
        
        return {
            "success": True,
            "scheduled_id": scheduled_content.id,
            "scheduled_for": optimized_datetime.isoformat(),
            "platform": platform.value,
            "optimization_applied": auto_optimize,
            "message": f"Contenu programmé pour {optimized_datetime.strftime('%d/%m/%Y %H:%M')} sur {platform.value}"
        }
    
    def create_content_calendar(self, intelligence_data_list: List[Dict[str, Any]], 
                              days_ahead: int = 30,
                              platforms: List[str] = None) -> Dict[str, Any]:
        """Crée un calendrier éditorial optimisé"""
        
        if platforms is None:
            platforms = ["linkedin", "twitter", "instagram"]
        
        calendar = {}
        current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Configuration de fréquence par plateforme
        platform_frequency = {
            "linkedin": 1,    # 1 post par jour
            "twitter": 2,     # 2 posts par jour
            "instagram": 0.5, # 1 post tous les 2 jours
            "facebook": 0.33  # 1 post tous les 3 jours
        }
        
        content_counter = 0
        
        for day in range(days_ahead):
            date = current_date + timedelta(days=day)
            date_str = date.strftime("%Y-%m-%d")
            day_name = date.strftime("%A").lower()
            
            calendar[date_str] = {
                "date": date_str,
                "day_of_week": day_name,
                "is_weekend": day_name in ["saturday", "sunday"],
                "content_planned": [],
                "total_posts": 0,
                "platforms_active": []
            }
            
            # Planification pour chaque plateforme
            for platform in platforms:
                frequency = platform_frequency.get(platform, 1)
                
                # Décision de publier ce jour (basée sur la fréquence)
                should_post = (day % max(1, int(1/frequency))) == 0
                
                # Éviter les weekends pour certaines plateformes
                if platform == "linkedin" and calendar[date_str]["is_weekend"]:
                    should_post = False
                
                if should_post and intelligence_data_list:
                    # Sélection de l'intelligence pour ce contenu
                    intelligence_data = intelligence_data_list[content_counter % len(intelligence_data_list)]
                    
                    # Génération du contenu (simulation)
                    content_types = self._get_content_types_for_platform(platform)
                    content_type = content_types[content_counter % len(content_types)]
                    
                    # Calcul du timing optimal
                    optimal_times = self.scheduling_rules[platform]["optimal_times"][day_name]
                    if optimal_times:
                        optimal_time = optimal_times[0]  # Prendre le premier créneau optimal
                        scheduled_datetime = datetime.strptime(f"{date_str} {optimal_time}", "%Y-%m-%d %H:%M")
                        
                        # Création du contenu planifié
                        planned_content = {
                            "id": f"PLANNED_{platform.upper()}_{content_counter}",
                            "platform": platform,
                            "type": content_type,
                            "scheduled_for": scheduled_datetime.isoformat(),
                            "intelligence_source": intelligence_data["id"],
                            "title": f"{content_type.title()} - {intelligence_data['title'][:50]}...",
                            "estimated_engagement": round(0.7 + (content_counter % 3) * 0.1, 2),
                            "estimated_reach": f"{(5000 + content_counter * 1000):,}",
                            "estimated_value": f"€{1500 + content_counter * 500:,}"
                        }
                        
                        calendar[date_str]["content_planned"].append(planned_content)
                        calendar[date_str]["total_posts"] += 1
                        
                        if platform not in calendar[date_str]["platforms_active"]:
                            calendar[date_str]["platforms_active"].append(platform)
                        
                        content_counter += 1
        
        # Statistiques du calendrier
        total_content = sum(day_data["total_posts"] for day_data in calendar.values())
        total_value = sum(
            sum(int(content["estimated_value"].replace("€", "").replace(",", "")) 
                for content in day_data["content_planned"])
            for day_data in calendar.values()
        )
        
        calendar_summary = {
            "calendar": calendar,
            "summary": {
                "total_days": days_ahead,
                "total_content_pieces": total_content,
                "avg_posts_per_day": round(total_content / days_ahead, 1),
                "platforms_covered": platforms,
                "estimated_total_value": f"€{total_value:,}",
                "content_distribution": self._calculate_content_distribution(calendar),
                "peak_days": self._identify_peak_days(calendar),
                "optimization_score": self._calculate_optimization_score(calendar)
            }
        }
        
        return calendar_summary
    
    def _optimize_scheduling_time(self, platform: Platform, content_type: str, 
                                target_datetime: datetime) -> datetime:
        """Optimise le timing de publication"""
        
        rules = self.scheduling_rules[platform.value]
        target_day = target_datetime.strftime("%A").lower()
        
        # Récupération des créneaux optimaux pour ce jour
        optimal_times = rules["optimal_times"].get(target_day, ["12:00"])
        
        # Conversion en datetime
        optimal_datetimes = []
        for time_str in optimal_times:
            hour, minute = map(int, time_str.split(":"))
            optimal_dt = target_datetime.replace(hour=hour, minute=minute, second=0, microsecond=0)
            optimal_datetimes.append(optimal_dt)
        
        # Sélection du créneau le plus proche
        closest_time = min(optimal_datetimes, 
                          key=lambda x: abs((x - target_datetime).total_seconds()))
        
        # Vérification des conflits avec d'autres contenus programmés
        while self._has_scheduling_conflict(platform, closest_time, content_type):
            closest_time += timedelta(hours=rules["min_interval_hours"])
        
        return closest_time
    
    def _find_next_optimal_slot(self, platform: Platform, content_type: str) -> datetime:
        """Trouve le prochain créneau optimal disponible"""
        
        rules = self.scheduling_rules[platform.value]
        current_time = datetime.now()
        
        # Recherche sur les 7 prochains jours
        for day_offset in range(7):
            check_date = current_time + timedelta(days=day_offset)
            day_name = check_date.strftime("%A").lower()
            
            # Vérification si c'est un bon jour pour cette plateforme
            if day_name in rules["best_days"]:
                optimal_times = rules["optimal_times"][day_name]
                
                for time_str in optimal_times:
                    hour, minute = map(int, time_str.split(":"))
                    candidate_time = check_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    
                    # Vérifier que c'est dans le futur
                    if candidate_time <= current_time:
                        continue
                    
                    # Vérifier les conflits
                    if not self._has_scheduling_conflict(platform, candidate_time, content_type):
                        return candidate_time
        
        # Si aucun créneau optimal trouvé, prendre le prochain disponible
        return current_time + timedelta(hours=2)
    
    def _validate_scheduling(self, platform: Platform, scheduled_time: datetime, 
                           content_type: str) -> Dict[str, Any]:
        """Valide la programmation d'un contenu"""
        
        rules = self.scheduling_rules[platform.value]
        limits = self.platform_limits[platform.value]
        
        # Vérification de la limite quotidienne
        same_day_count = len([
            content for content in self.scheduled_content
            if (content.platform == platform and 
                content.scheduled_for.date() == scheduled_time.date() and
                content.status == PublicationStatus.SCHEDULED)
        ])
        
        if same_day_count >= rules["max_posts_per_day"]:
            return {
                "valid": False,
                "error": f"Limite quotidienne atteinte pour {platform.value} ({rules['max_posts_per_day']} posts/jour)",
                "suggested_times": self._suggest_alternative_times(platform, scheduled_time)
            }
        
        # Vérification de l'intervalle minimum
        if self._has_scheduling_conflict(platform, scheduled_time, content_type):
            return {
                "valid": False,
                "error": f"Conflit d'horaire - intervalle minimum de {rules['min_interval_hours']}h requis",
                "suggested_times": self._suggest_alternative_times(platform, scheduled_time)
            }
        
        # Vérification des heures à éviter
        time_str = scheduled_time.strftime("%H:%M")
        for avoid_period in rules.get("avoid_times", []):
            start_time, end_time = avoid_period.split("-")
            if start_time <= time_str <= end_time:
                return {
                    "valid": False,
                    "error": f"Horaire non optimal - éviter {avoid_period}",
                    "suggested_times": self._suggest_alternative_times(platform, scheduled_time)
                }
        
        return {"valid": True}
    
    def _has_scheduling_conflict(self, platform: Platform, scheduled_time: datetime, 
                               content_type: str) -> bool:
        """Vérifie s'il y a un conflit de programmation"""
        
        rules = self.scheduling_rules[platform.value]
        min_interval = timedelta(hours=rules["min_interval_hours"])
        
        # Vérification de l'espacement spécifique au type de contenu
        content_spacing = rules.get("content_spacing", {}).get(content_type, rules["min_interval_hours"])
        content_interval = timedelta(hours=content_spacing)
        
        for existing_content in self.scheduled_content:
            if (existing_content.platform == platform and 
                existing_content.status == PublicationStatus.SCHEDULED):
                
                time_diff = abs((existing_content.scheduled_for - scheduled_time).total_seconds())
                
                # Vérification de l'intervalle minimum général
                if time_diff < min_interval.total_seconds():
                    return True
                
                # Vérification de l'espacement spécifique au type de contenu
                if (existing_content.content_type == content_type and 
                    time_diff < content_interval.total_seconds()):
                    return True
        
        return False
    
    def _suggest_alternative_times(self, platform: Platform, 
                                 original_time: datetime) -> List[str]:
        """Suggère des créneaux alternatifs"""
        
        rules = self.scheduling_rules[platform.value]
        suggestions = []
        
        # Recherche sur les 3 prochains jours
        for day_offset in range(3):
            check_date = original_time + timedelta(days=day_offset)
            day_name = check_date.strftime("%A").lower()
            
            optimal_times = rules["optimal_times"].get(day_name, ["12:00"])
            
            for time_str in optimal_times:
                hour, minute = map(int, time_str.split(":"))
                candidate_time = check_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                if (candidate_time > datetime.now() and 
                    not self._has_scheduling_conflict(platform, candidate_time, "post")):
                    suggestions.append(candidate_time.strftime("%d/%m/%Y %H:%M"))
                
                if len(suggestions) >= 3:
                    break
            
            if len(suggestions) >= 3:
                break
        
        return suggestions
    
    def _get_content_types_for_platform(self, platform: str) -> List[str]:
        """Retourne les types de contenu disponibles pour une plateforme"""
        
        content_types = {
            "linkedin": ["insight", "market_update", "tech_breakthrough"],
            "twitter": ["thread", "single_tweet", "quote_tweet"],
            "instagram": ["post", "story", "reel"],
            "facebook": ["post", "story", "video"]
        }
        
        return content_types.get(platform, ["post"])
    
    def _calculate_content_distribution(self, calendar: Dict[str, Any]) -> Dict[str, int]:
        """Calcule la distribution du contenu par plateforme"""
        
        distribution = {}
        
        for day_data in calendar.values():
            for content in day_data["content_planned"]:
                platform = content["platform"]
                distribution[platform] = distribution.get(platform, 0) + 1
        
        return distribution
    
    def _identify_peak_days(self, calendar: Dict[str, Any]) -> List[str]:
        """Identifie les jours avec le plus de contenu"""
        
        day_counts = [(date, day_data["total_posts"]) 
                     for date, day_data in calendar.items()]
        
        # Trier par nombre de posts décroissant
        day_counts.sort(key=lambda x: x[1], reverse=True)
        
        # Retourner les 3 jours les plus chargés
        return [date for date, count in day_counts[:3] if count > 0]
    
    def _calculate_optimization_score(self, calendar: Dict[str, Any]) -> float:
        """Calcule un score d'optimisation du calendrier"""
        
        total_score = 0
        total_content = 0
        
        for day_data in calendar.values():
            day_name = day_data["day_of_week"]
            
            for content in day_data["content_planned"]:
                platform = content["platform"]
                scheduled_time = datetime.fromisoformat(content["scheduled_for"])
                hour = scheduled_time.hour
                
                # Score basé sur l'heure optimale
                rules = self.scheduling_rules.get(platform, {})
                optimal_times = rules.get("optimal_times", {}).get(day_name, [])
                
                if optimal_times:
                    optimal_hours = [int(t.split(":")[0]) for t in optimal_times]
                    closest_optimal = min(optimal_hours, key=lambda x: abs(x - hour))
                    hour_score = max(0, 1 - abs(hour - closest_optimal) / 12)
                else:
                    hour_score = 0.5
                
                # Score basé sur le jour optimal
                best_days = rules.get("best_days", [])
                day_score = 1.0 if day_name in best_days else 0.7
                
                # Score combiné
                content_score = (hour_score + day_score) / 2
                total_score += content_score
                total_content += 1
        
        return round(total_score / max(total_content, 1), 2)
    
    def execute_scheduled_publications(self) -> Dict[str, Any]:
        """Exécute les publications programmées (simulation)"""
        
        current_time = datetime.now()
        executed = []
        failed = []
        
        for content in self.scheduled_content:
            if (content.status == PublicationStatus.SCHEDULED and 
                content.scheduled_for <= current_time):
                
                # Simulation de publication
                success_rate = 0.95  # 95% de succès
                
                if content.retry_count < 3 and (content.retry_count == 0 or 
                                              time.time() % 10 < success_rate * 10):
                    # Publication réussie
                    content.status = PublicationStatus.PUBLISHED
                    content.published_at = current_time
                    executed.append(content)
                    
                    # Ajout à l'historique
                    self.publication_history.append({
                        "content_id": content.id,
                        "platform": content.platform.value,
                        "published_at": current_time.isoformat(),
                        "estimated_metrics": content.estimated_metrics
                    })
                    
                else:
                    # Échec de publication
                    content.retry_count += 1
                    
                    if content.retry_count >= 3:
                        content.status = PublicationStatus.FAILED
                        content.error_message = "Échec après 3 tentatives"
                        failed.append(content)
                    else:
                        # Reprogrammer pour dans 1 heure
                        content.scheduled_for = current_time + timedelta(hours=1)
        
        return {
            "executed": len(executed),
            "failed": len(failed),
            "pending": len([c for c in self.scheduled_content 
                          if c.status == PublicationStatus.SCHEDULED]),
            "execution_details": {
                "successful_publications": [
                    {
                        "id": c.id,
                        "platform": c.platform.value,
                        "published_at": c.published_at.isoformat() if c.published_at else None
                    } for c in executed
                ],
                "failed_publications": [
                    {
                        "id": c.id,
                        "platform": c.platform.value,
                        "error": c.error_message,
                        "retry_count": c.retry_count
                    } for c in failed
                ]
            }
        }
    
    def get_scheduling_analytics(self) -> Dict[str, Any]:
        """Retourne les analytics de planification"""
        
        total_scheduled = len(self.scheduled_content)
        published = len([c for c in self.scheduled_content if c.status == PublicationStatus.PUBLISHED])
        failed = len([c for c in self.scheduled_content if c.status == PublicationStatus.FAILED])
        pending = len([c for c in self.scheduled_content if c.status == PublicationStatus.SCHEDULED])
        
        # Distribution par plateforme
        platform_distribution = {}
        for content in self.scheduled_content:
            platform = content.platform.value
            platform_distribution[platform] = platform_distribution.get(platform, 0) + 1
        
        # Taux de succès
        success_rate = (published / max(total_scheduled, 1)) * 100
        
        return {
            "total_scheduled": total_scheduled,
            "published": published,
            "failed": failed,
            "pending": pending,
            "success_rate": round(success_rate, 1),
            "platform_distribution": platform_distribution,
            "avg_retry_count": round(
                sum(c.retry_count for c in self.scheduled_content) / max(total_scheduled, 1), 1
            ),
            "next_publications": [
                {
                    "id": c.id,
                    "platform": c.platform.value,
                    "scheduled_for": c.scheduled_for.isoformat(),
                    "content_type": c.content_type
                }
                for c in sorted(
                    [c for c in self.scheduled_content if c.status == PublicationStatus.SCHEDULED],
                    key=lambda x: x.scheduled_for
                )[:5]
            ]
        }

# Test et démonstration
if __name__ == "__main__":
    scheduler = ContentScheduler()
    
    # Test de données d'intelligence
    test_intelligence = [
        {
            "id": "INTEL_001",
            "title": "JUPITER atteint 1 exaflop - Premier supercalculateur exascale européen",
            "summary": "L'Europe franchit une étape historique",
            "sector": "HPC"
        },
        {
            "id": "INTEL_002", 
            "title": "Nvidia annonce Blackwell B200",
            "summary": "Nouvelle génération d'accélérateurs IA",
            "sector": "IA"
        }
    ]
    
    # Test de contenu à programmer
    test_content = {
        "platform": "linkedin",
        "type": "insight",
        "content": "Test de contenu LinkedIn...",
        "source_intelligence": "INTEL_001",
        "estimated_metrics": {"estimated_reach": "10,000", "estimated_value": "€2,500"}
    }
    
    # Test de programmation
    result = scheduler.schedule_content(test_content, auto_optimize=True)
    print("✅ Programmation de contenu:")
    print(f"   Succès: {result['success']}")
    print(f"   ID: {result.get('scheduled_id', 'N/A')}")
    print(f"   Programmé pour: {result.get('scheduled_for', 'N/A')}")
    
    # Test de calendrier éditorial
    calendar = scheduler.create_content_calendar(test_intelligence, 7)
    print(f"\n✅ Calendrier éditorial créé:")
    print(f"   {calendar['summary']['total_content_pieces']} contenus sur {calendar['summary']['total_days']} jours")
    print(f"   Score d'optimisation: {calendar['summary']['optimization_score']}")
    print(f"   Valeur estimée: {calendar['summary']['estimated_total_value']}")
    
    # Test d'exécution
    execution_result = scheduler.execute_scheduled_publications()
    print(f"\n✅ Exécution des publications:")
    print(f"   Exécutées: {execution_result['executed']}")
    print(f"   Échouées: {execution_result['failed']}")
    print(f"   En attente: {execution_result['pending']}")
    
    # Analytics
    analytics = scheduler.get_scheduling_analytics()
    print(f"\n📊 Analytics:")
    print(f"   Taux de succès: {analytics['success_rate']}%")
    print(f"   Distribution: {analytics['platform_distribution']}")
    print(f"   Prochaines publications: {len(analytics['next_publications'])}")

