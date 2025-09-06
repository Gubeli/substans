"""
Social Media Content System - Système de Génération de Contenu pour Réseaux Sociaux
Module spécialisé pour la création automatisée de contenu LinkedIn, Twitter, Instagram, etc.
Intégré avec le système d'intelligence quotidienne pour un contenu pertinent et engageant.
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import hashlib
import os
import re

class SocialMediaContentSystem:
    def __init__(self):
        self.name = "Social Media Content System"
        self.version = "1.0"
        self.platforms = self._initialize_platforms()
        self.content_calendar = []
        self.published_content = []
        self.engagement_analytics = {}
        
        print(f"🚀 {self.name} v{self.version} initialisé")
        print("✅ Plateformes configurées: LinkedIn, Twitter, Instagram, Facebook")
        print("✅ Calendrier éditorial activé")
        print("✅ Analytics d'engagement intégrées")
    
    def _initialize_platforms(self) -> Dict[str, Any]:
        """Initialise la configuration des plateformes sociales"""
        return {
            "linkedin": {
                "name": "LinkedIn",
                "character_limit": 3000,
                "optimal_post_length": 1300,
                "hashtag_limit": 5,
                "image_formats": ["JPG", "PNG", "GIF"],
                "video_formats": ["MP4", "MOV"],
                "best_posting_times": {
                    "monday": ["08:00", "12:00", "17:00"],
                    "tuesday": ["08:00", "12:00", "17:00"], 
                    "wednesday": ["08:00", "12:00", "17:00"],
                    "thursday": ["08:00", "12:00", "17:00"],
                    "friday": ["08:00", "12:00"],
                    "saturday": ["10:00"],
                    "sunday": ["19:00"]
                },
                "content_types": ["post", "article", "video", "carousel", "poll"],
                "audience_segments": ["IT Professionals", "C-Level", "Entrepreneurs", "Analysts"],
                "engagement_factors": {
                    "professional_tone": 0.25,
                    "industry_insights": 0.30,
                    "data_driven": 0.20,
                    "call_to_action": 0.15,
                    "visual_content": 0.10
                }
            },
            
            "twitter": {
                "name": "Twitter/X",
                "character_limit": 280,
                "thread_limit": 25,
                "hashtag_limit": 3,
                "image_formats": ["JPG", "PNG", "GIF", "WEBP"],
                "video_formats": ["MP4", "MOV"],
                "best_posting_times": {
                    "monday": ["09:00", "15:00", "21:00"],
                    "tuesday": ["09:00", "15:00", "21:00"],
                    "wednesday": ["09:00", "15:00", "21:00"],
                    "thursday": ["09:00", "15:00", "21:00"],
                    "friday": ["09:00", "15:00"],
                    "saturday": ["12:00", "17:00"],
                    "sunday": ["14:00", "20:00"]
                },
                "content_types": ["tweet", "thread", "retweet", "quote_tweet", "poll"],
                "audience_segments": ["Tech Community", "Startup Ecosystem", "Developers", "Innovators"],
                "engagement_factors": {
                    "trending_topics": 0.30,
                    "real_time_news": 0.25,
                    "community_interaction": 0.20,
                    "visual_content": 0.15,
                    "hashtag_usage": 0.10
                }
            },
            
            "instagram": {
                "name": "Instagram",
                "character_limit": 2200,
                "hashtag_limit": 30,
                "image_formats": ["JPG", "PNG"],
                "video_formats": ["MP4", "MOV"],
                "aspect_ratios": {
                    "feed": "1:1",
                    "stories": "9:16",
                    "reels": "9:16",
                    "igtv": "9:16"
                },
                "best_posting_times": {
                    "monday": ["11:00", "14:00", "17:00"],
                    "tuesday": ["11:00", "14:00", "17:00"],
                    "wednesday": ["11:00", "14:00", "17:00"],
                    "thursday": ["11:00", "14:00", "17:00"],
                    "friday": ["11:00", "14:00"],
                    "saturday": ["12:00", "15:00"],
                    "sunday": ["12:00", "15:00"]
                },
                "content_types": ["post", "story", "reel", "igtv", "carousel"],
                "audience_segments": ["Young Professionals", "Creatives", "Entrepreneurs", "Tech Enthusiasts"],
                "engagement_factors": {
                    "visual_quality": 0.40,
                    "storytelling": 0.25,
                    "hashtag_strategy": 0.15,
                    "user_interaction": 0.12,
                    "trending_audio": 0.08
                }
            },
            
            "facebook": {
                "name": "Facebook",
                "character_limit": 63206,
                "optimal_post_length": 250,
                "hashtag_limit": 5,
                "image_formats": ["JPG", "PNG", "GIF"],
                "video_formats": ["MP4", "MOV", "AVI"],
                "best_posting_times": {
                    "monday": ["09:00", "15:00"],
                    "tuesday": ["09:00", "15:00"],
                    "wednesday": ["09:00", "15:00"],
                    "thursday": ["09:00", "15:00"],
                    "friday": ["09:00", "15:00"],
                    "saturday": ["12:00", "15:00"],
                    "sunday": ["12:00", "15:00"]
                },
                "content_types": ["post", "story", "video", "event", "poll"],
                "audience_segments": ["Business Owners", "General Public", "Industry Groups", "Local Communities"],
                "engagement_factors": {
                    "community_focus": 0.30,
                    "shareability": 0.25,
                    "emotional_connection": 0.20,
                    "visual_content": 0.15,
                    "local_relevance": 0.10
                }
            }
        }
    
    def generate_linkedin_post(self, intelligence_data: Dict[str, Any], 
                             post_type: str = "insight") -> Dict[str, Any]:
        """Génère un post LinkedIn optimisé"""
        
        platform_config = self.platforms["linkedin"]
        
        # Templates spécialisés LinkedIn
        templates = {
            "insight": {
                "structure": """🔍 {hook}

{main_insight}

📊 Données clés :
{key_data}

💡 Ce que cela signifie pour vous :
{implications}

🎯 Actions recommandées :
{actions}

Qu'en pensez-vous ? Partagez votre expérience en commentaire 👇

#{hashtag1} #{hashtag2} #{hashtag3} #Innovation #DigitalTransformation""",
                "hooks": [
                    "Nouvelle tendance détectée par nos algorithmes d'IA",
                    "Analyse exclusive : ce que révèlent les dernières données",
                    "Insight stratégique : l'opportunité que vous ne devez pas manquer",
                    "Décryptage : pourquoi cette évolution va transformer votre secteur"
                ]
            },
            
            "market_update": {
                "structure": """📈 MISE À JOUR MARCHÉ - {title}

{market_summary}

🔢 Chiffres marquants :
• {metric1}
• {metric2}  
• {metric3}

🎯 Impact sur votre business :
{business_impact}

🚀 Opportunités identifiées :
{opportunities}

💬 Votre avis ? Comment votre entreprise se positionne-t-elle face à ces évolutions ?

#{hashtag1} #{hashtag2} #{hashtag3} #MarketTrends #BusinessStrategy""",
                "hooks": [
                    "Le marché évolue plus vite que prévu",
                    "Nouvelle donne concurrentielle en vue",
                    "Les chiffres parlent : voici ce qui change",
                    "Mise à jour stratégique : ce qu'il faut retenir"
                ]
            },
            
            "tech_breakthrough": {
                "structure": """⚡ BREAKTHROUGH TECHNOLOGIQUE

{breakthrough_description}

🔬 Pourquoi c'est révolutionnaire :
{revolutionary_aspects}

📊 Impact prévu :
{impact_metrics}

🏢 Applications business :
{business_applications}

🔮 Vision 2025 :
{future_vision}

Prêt pour cette révolution ? Dites-nous comment vous vous préparez 🚀

#{hashtag1} #{hashtag2} #{hashtag3} #TechInnovation #FutureTech""",
                "hooks": [
                    "La technologie vient de franchir un cap historique",
                    "Révolution en cours : ce qui va changer la donne",
                    "Breakthrough confirmé : l'innovation qui change tout",
                    "Nouvelle ère technologique : êtes-vous prêt ?"
                ]
            }
        }
        
        template = templates.get(post_type, templates["insight"])
        
        # Génération du contenu
        content_data = self._extract_linkedin_content_data(intelligence_data, post_type)
        
        # Sélection du hook
        import random
        hook = random.choice(template["hooks"])
        
        # Assemblage du post
        formatted_data = content_data.copy()
        formatted_data["hook"] = hook
        
        post_content = template["structure"].format(**formatted_data)
        
        # Optimisation de la longueur
        if len(post_content) > platform_config["character_limit"]:
            post_content = self._optimize_post_length(post_content, platform_config["character_limit"])
        
        # Calcul du score d'engagement
        engagement_score = self._calculate_linkedin_engagement(post_content, platform_config["engagement_factors"])
        
        # Estimation des métriques
        estimated_metrics = self._estimate_linkedin_metrics(engagement_score, intelligence_data.get("sector", "Technology"))
        
        result = {
            "id": f"LINKEDIN_{int(time.time())}",
            "platform": "linkedin",
            "type": post_type,
            "content": post_content,
            "status": "draft",
            "created_at": datetime.now().isoformat(),
            "scheduled_for": None,
            "engagement_score": engagement_score,
            "estimated_metrics": estimated_metrics,
            "hashtags": content_data.get("hashtags", []),
            "target_audience": platform_config["audience_segments"],
            "optimal_posting_time": self._get_optimal_posting_time("linkedin"),
            "content_quality_score": min(0.95, engagement_score + 0.05),
            "source_intelligence": intelligence_data.get("id", "unknown")
        }
        
        return result
    
    def generate_twitter_thread(self, intelligence_data: Dict[str, Any], 
                              thread_length: int = 7) -> Dict[str, Any]:
        """Génère un thread Twitter optimisé"""
        
        platform_config = self.platforms["twitter"]
        
        # Structure du thread
        thread_structure = {
            1: "🧵 THREAD - {title}\n\n{hook}",
            2: "📊 {data_point}",
            3: "💡 {key_insight}",
            4: "🎯 {implication}",
            5: "🔮 {prediction}",
            6: "📈 {opportunity}",
            7: "🎬 {conclusion}\n\nVous avez aimé ce thread ?\n🔄 RT pour partager\n❤️ Like si utile\n💬 Vos thoughts ?"
        }
        
        # Génération du contenu pour chaque tweet
        tweets = []
        content_data = self._extract_twitter_content_data(intelligence_data)
        
        for i in range(1, min(thread_length + 1, len(thread_structure) + 1)):
            if i in thread_structure:
                tweet_content = thread_structure[i].format(**content_data)
                
                # Vérification de la limite de caractères
                if len(tweet_content) > platform_config["character_limit"]:
                    tweet_content = self._optimize_tweet_length(tweet_content, platform_config["character_limit"])
                
                tweets.append({
                    "position": i,
                    "content": tweet_content,
                    "character_count": len(tweet_content)
                })
        
        # Calcul du score d'engagement pour le thread
        thread_text = " ".join([tweet["content"] for tweet in tweets])
        engagement_score = self._calculate_twitter_engagement(thread_text, platform_config["engagement_factors"])
        
        # Estimation des métriques
        estimated_metrics = self._estimate_twitter_metrics(engagement_score, len(tweets))
        
        result = {
            "id": f"TWITTER_THREAD_{int(time.time())}",
            "platform": "twitter",
            "type": "thread",
            "tweets": tweets,
            "thread_length": len(tweets),
            "status": "draft",
            "created_at": datetime.now().isoformat(),
            "scheduled_for": None,
            "engagement_score": engagement_score,
            "estimated_metrics": estimated_metrics,
            "hashtags": content_data.get("hashtags", []),
            "target_audience": platform_config["audience_segments"],
            "optimal_posting_time": self._get_optimal_posting_time("twitter"),
            "content_quality_score": min(0.92, engagement_score + 0.02),
            "source_intelligence": intelligence_data.get("id", "unknown")
        }
        
        return result
    
    def generate_instagram_content(self, intelligence_data: Dict[str, Any], 
                                 content_type: str = "post") -> Dict[str, Any]:
        """Génère du contenu Instagram optimisé"""
        
        platform_config = self.platforms["instagram"]
        
        # Templates Instagram
        templates = {
            "post": {
                "structure": """🚀 {title}

{visual_description}

{main_message}

💡 {key_takeaway}

🔥 {call_to_action}

.
.
.
{hashtag_string}""",
                "visual_suggestions": [
                    "Infographie moderne avec données clés",
                    "Carousel explicatif en 3 slides",
                    "Quote inspirante sur fond tech",
                    "Schéma conceptuel coloré"
                ]
            },
            
            "story": {
                "structure": """📱 {hook}

{quick_insight}

👆 Swipe up pour en savoir plus

#{hashtag1} #{hashtag2}""",
                "duration": "15 seconds",
                "interactive_elements": ["poll", "question", "quiz", "slider"]
            },
            
            "reel": {
                "structure": """🎬 REEL SCRIPT - {title}

INTRO (0-3s): {hook}
DÉVELOPPEMENT (3-12s): {main_content}
CONCLUSION (12-15s): {call_to_action}

Musique suggérée: {music_suggestion}
Effets: {effects_suggestion}""",
                "optimal_duration": "15-30 seconds",
                "trending_formats": ["before/after", "tutorial", "behind_scenes", "data_visualization"]
            }
        }
        
        template = templates.get(content_type, templates["post"])
        content_data = self._extract_instagram_content_data(intelligence_data, content_type)
        
        # Génération des hashtags Instagram (jusqu'à 30)
        hashtags = self._generate_instagram_hashtags(intelligence_data.get("sector", "technology"))
        hashtag_string = " ".join([f"#{tag}" for tag in hashtags])
        
        # Ajout du hashtag_string aux données de contenu
        content_data["hashtag_string"] = hashtag_string
        
        # Génération du contenu
        if content_type == "reel":
            content = template["structure"].format(**content_data)
        else:
            content = template["structure"].format(**content_data)
        
        # Calcul du score d'engagement
        engagement_score = self._calculate_instagram_engagement(content, platform_config["engagement_factors"])
        
        # Estimation des métriques
        estimated_metrics = self._estimate_instagram_metrics(engagement_score, content_type)
        
        result = {
            "id": f"INSTAGRAM_{content_type.upper()}_{int(time.time())}",
            "platform": "instagram",
            "type": content_type,
            "content": content,
            "hashtags": hashtags,
            "visual_suggestions": template.get("visual_suggestions", []),
            "status": "draft",
            "created_at": datetime.now().isoformat(),
            "scheduled_for": None,
            "engagement_score": engagement_score,
            "estimated_metrics": estimated_metrics,
            "target_audience": platform_config["audience_segments"],
            "optimal_posting_time": self._get_optimal_posting_time("instagram"),
            "content_quality_score": min(0.90, engagement_score),
            "source_intelligence": intelligence_data.get("id", "unknown")
        }
        
        return result
    
    def create_content_calendar(self, intelligence_data_list: List[Dict[str, Any]], 
                              days_ahead: int = 30) -> Dict[str, Any]:
        """Crée un calendrier éditorial pour les réseaux sociaux"""
        
        calendar = {}
        current_date = datetime.now()
        
        # Répartition du contenu sur les jours
        content_per_day = {
            "linkedin": 1,  # 1 post LinkedIn par jour
            "twitter": 2,   # 2 tweets/threads par jour
            "instagram": 1, # 1 post Instagram par jour
            "facebook": 0.5 # 1 post Facebook tous les 2 jours
        }
        
        for day in range(days_ahead):
            date = current_date + timedelta(days=day)
            date_str = date.strftime("%Y-%m-%d")
            
            calendar[date_str] = {
                "date": date_str,
                "day_of_week": date.strftime("%A").lower(),
                "content_planned": [],
                "total_posts": 0
            }
            
            # Planification du contenu pour chaque plateforme
            for platform, posts_per_day in content_per_day.items():
                if day % (1/posts_per_day) == 0:  # Fréquence de publication
                    
                    # Sélection des données d'intelligence pour ce jour
                    if intelligence_data_list:
                        intelligence_data = intelligence_data_list[day % len(intelligence_data_list)]
                        
                        # Génération du contenu selon la plateforme
                        if platform == "linkedin":
                            content = self.generate_linkedin_post(intelligence_data)
                        elif platform == "twitter":
                            content = self.generate_twitter_thread(intelligence_data)
                        elif platform == "instagram":
                            content = self.generate_instagram_content(intelligence_data)
                        
                        # Programmation à l'heure optimale
                        optimal_times = self.platforms[platform]["best_posting_times"][calendar[date_str]["day_of_week"]]
                        scheduled_time = f"{date_str} {optimal_times[0]}:00"
                        content["scheduled_for"] = scheduled_time
                        
                        calendar[date_str]["content_planned"].append(content)
                        calendar[date_str]["total_posts"] += 1
        
        # Statistiques du calendrier
        total_content = sum(day_data["total_posts"] for day_data in calendar.values())
        
        calendar_summary = {
            "calendar": calendar,
            "summary": {
                "total_days": days_ahead,
                "total_content_pieces": total_content,
                "avg_posts_per_day": round(total_content / days_ahead, 1),
                "platforms_covered": list(content_per_day.keys()),
                "estimated_total_value": f"€{total_content * 2500:,}"
            }
        }
        
        self.content_calendar = calendar_summary
        return calendar_summary
    
    def get_platform_analytics(self, platform: str = "all") -> Dict[str, Any]:
        """Retourne les analytics pour une plateforme ou toutes"""
        
        if platform == "all":
            analytics = {}
            for platform_name in self.platforms.keys():
                analytics[platform_name] = self._calculate_platform_analytics(platform_name)
            return analytics
        else:
            return self._calculate_platform_analytics(platform)
    
    def _extract_linkedin_content_data(self, intelligence_data: Dict[str, Any], post_type: str) -> Dict[str, Any]:
        """Extrait et formate les données pour LinkedIn"""
        
        sector = intelligence_data.get("sector", "Technology")
        
        # Génération des hashtags LinkedIn
        hashtags = self._generate_linkedin_hashtags(sector)
        
        return {
            "title": intelligence_data.get("title", "Nouvelle Tendance Technologique"),
            "main_insight": intelligence_data.get("summary", "Nos algorithmes d'IA ont identifié une opportunité stratégique majeure."),
            "key_data": self._format_key_data(intelligence_data),
            "implications": self._generate_business_implications(intelligence_data),
            "actions": self._generate_action_items(intelligence_data),
            "hashtag1": hashtags[0] if len(hashtags) > 0 else "Innovation",
            "hashtag2": hashtags[1] if len(hashtags) > 1 else "Technology", 
            "hashtag3": hashtags[2] if len(hashtags) > 2 else "Business",
            "hashtags": hashtags,
            "market_summary": intelligence_data.get("summary", "Évolution significative du marché détectée"),
            "metric1": f"Croissance: {intelligence_data.get('growth_rate', '+45%')}",
            "metric2": f"Marché: {intelligence_data.get('market_size', '€127B')}",
            "metric3": f"Adoption: {intelligence_data.get('adoption_rate', '78%')}",
            "business_impact": "Transformation des processus métier et nouvelles opportunités de revenus",
            "opportunities": "• Automatisation intelligente\n• Nouveaux modèles économiques\n• Avantage concurrentiel durable",
            "breakthrough_description": intelligence_data.get("summary", "Innovation technologique majeure"),
            "revolutionary_aspects": "• Performance 10x supérieure\n• Coûts réduits de 40%\n• Nouvelles capacités inédites",
            "impact_metrics": f"ROI estimé: +{intelligence_data.get('roi_estimate', '150')}%",
            "business_applications": "• Optimisation des processus\n• Nouveaux produits/services\n• Transformation digitale",
            "future_vision": "Adoption massive d'ici 2026 avec impact transformationnel sur l'industrie"
        }
    
    def _extract_twitter_content_data(self, intelligence_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrait et formate les données pour Twitter"""
        
        hashtags = self._generate_twitter_hashtags(intelligence_data.get("sector", "tech"))
        
        return {
            "title": intelligence_data.get("title", "Tech Breakthrough")[:50] + "...",
            "hook": "🚨 Alerte tendance : " + intelligence_data.get("summary", "Innovation majeure détectée")[:180],
            "data_point": f"📊 Les chiffres : {intelligence_data.get('growth_rate', '+45%')} de croissance, marché de {intelligence_data.get('market_size', '€127B')}",
            "key_insight": "💡 L'insight clé : Cette évolution va redéfinir les règles du jeu dans les 18 prochains mois",
            "implication": "🎯 Impact : Transformation des modèles économiques et nouvelles opportunités business",
            "prediction": "🔮 Prédiction : Adoption massive d'ici 2025, les early adopters prendront l'avantage",
            "opportunity": "📈 Opportunité : Fenêtre de 12 mois pour se positionner avant la concurrence",
            "conclusion": "🎬 Conclusion : Le futur se dessine maintenant. Qui sera prêt ?",
            "hashtags": hashtags,
            "hashtag1": hashtags[0] if len(hashtags) > 0 else "innovation",
            "hashtag2": hashtags[1] if len(hashtags) > 1 else "tech"
        }
    
    def _extract_instagram_content_data(self, intelligence_data: Dict[str, Any], content_type: str) -> Dict[str, Any]:
        """Extrait et formate les données pour Instagram"""
        
        return {
            "title": intelligence_data.get("title", "Innovation Alert")[:30] + "...",
            "visual_description": "[Image: Infographie moderne montrant l'évolution technologique]",
            "main_message": intelligence_data.get("summary", "Le futur de la tech se dessine maintenant")[:100],
            "key_takeaway": "💡 Retenez : Cette innovation va transformer votre secteur",
            "call_to_action": "🔥 Suivez @substans.ai pour plus d'insights tech !",
            "hook": "🚨 " + intelligence_data.get("title", "Tech News")[:40],
            "quick_insight": intelligence_data.get("summary", "Innovation majeure")[:80],
            "main_content": "Données exclusives révélant l'impact de cette technologie",
            "music_suggestion": "Trending tech/innovation audio",
            "effects_suggestion": "Transitions dynamiques, texte animé"
        }
    
    def _generate_linkedin_hashtags(self, sector: str) -> List[str]:
        """Génère des hashtags optimisés pour LinkedIn"""
        
        hashtag_sets = {
            "HPC": ["HPC", "Supercomputing", "HighPerformanceComputing", "Exascale", "Innovation"],
            "IA": ["AI", "ArtificialIntelligence", "MachineLearning", "DeepLearning", "Innovation"],
            "Finance": ["Fintech", "Banking", "DigitalPayments", "Innovation", "Finance"],
            "Technology": ["Technology", "Innovation", "DigitalTransformation", "TechTrends", "Future"],
            "Cloud": ["Cloud", "CloudComputing", "AWS", "Azure", "Infrastructure"]
        }
        
        return hashtag_sets.get(sector, hashtag_sets["Technology"])
    
    def _generate_twitter_hashtags(self, sector: str) -> List[str]:
        """Génère des hashtags optimisés pour Twitter"""
        
        hashtag_sets = {
            "HPC": ["HPC", "supercomputing", "exascale"],
            "IA": ["AI", "ML", "innovation"],
            "Finance": ["fintech", "banking", "payments"],
            "Technology": ["tech", "innovation", "future"],
            "Cloud": ["cloud", "devops", "infrastructure"]
        }
        
        return hashtag_sets.get(sector, hashtag_sets["Technology"])[:3]  # Max 3 pour Twitter
    
    def _generate_instagram_hashtags(self, sector: str) -> List[str]:
        """Génère des hashtags optimisés pour Instagram (jusqu'à 30)"""
        
        base_hashtags = ["innovation", "technology", "future", "business", "startup", "entrepreneur", 
                        "digitaltransformation", "tech", "ai", "data", "insights", "trends"]
        
        sector_hashtags = {
            "HPC": ["hpc", "supercomputing", "computing", "performance", "exascale", "research"],
            "IA": ["artificialintelligence", "machinelearning", "deeplearning", "automation", "robots"],
            "Finance": ["fintech", "banking", "payments", "blockchain", "cryptocurrency", "finance"],
            "Technology": ["techtrends", "innovation", "digital", "software", "hardware", "coding"],
            "Cloud": ["cloud", "cloudcomputing", "devops", "infrastructure", "saas", "platform"]
        }
        
        specific_hashtags = sector_hashtags.get(sector, sector_hashtags["Technology"])
        
        # Combinaison des hashtags (max 30 pour Instagram)
        all_hashtags = base_hashtags + specific_hashtags
        return all_hashtags[:30]
    
    def _format_key_data(self, intelligence_data: Dict[str, Any]) -> str:
        """Formate les données clés pour l'affichage"""
        
        data_points = []
        
        if "growth_rate" in intelligence_data:
            data_points.append(f"• Croissance: {intelligence_data['growth_rate']}")
        
        if "market_size" in intelligence_data:
            data_points.append(f"• Taille marché: {intelligence_data['market_size']}")
        
        if "confidence" in intelligence_data:
            confidence_pct = int(intelligence_data["confidence"] * 100)
            data_points.append(f"• Niveau de confiance: {confidence_pct}%")
        
        return "\n".join(data_points) if data_points else "• Données en cours d'analyse"
    
    def _generate_business_implications(self, intelligence_data: Dict[str, Any]) -> str:
        """Génère les implications business"""
        
        implications = [
            "• Nouvelles opportunités de revenus identifiées",
            "• Transformation des processus métier nécessaire", 
            "• Avantage concurrentiel temporaire disponible",
            "• Impact sur la stratégie technologique à prévoir"
        ]
        
        return "\n".join(implications[:3])
    
    def _generate_action_items(self, intelligence_data: Dict[str, Any]) -> str:
        """Génère les actions recommandées"""
        
        actions = [
            "• Évaluer l'impact sur votre roadmap",
            "• Identifier les partenariats stratégiques",
            "• Planifier les investissements nécessaires",
            "• Former les équipes aux nouvelles compétences"
        ]
        
        return "\n".join(actions[:3])
    
    def _optimize_post_length(self, content: str, max_length: int) -> str:
        """Optimise la longueur d'un post"""
        
        if len(content) <= max_length:
            return content
        
        # Troncature intelligente
        truncated = content[:max_length-50]  # Marge pour "..."
        
        # Trouve le dernier point ou saut de ligne
        last_period = truncated.rfind('.')
        last_newline = truncated.rfind('\n')
        
        cut_point = max(last_period, last_newline)
        
        if cut_point > max_length * 0.8:  # Si on peut garder 80% du contenu
            return truncated[:cut_point] + "\n\n[Suite en commentaire]"
        else:
            return truncated + "..."
    
    def _optimize_tweet_length(self, content: str, max_length: int) -> str:
        """Optimise la longueur d'un tweet"""
        
        if len(content) <= max_length:
            return content
        
        # Troncature pour Twitter
        truncated = content[:max_length-4]  # Marge pour "..."
        
        # Trouve le dernier espace
        last_space = truncated.rfind(' ')
        
        if last_space > max_length * 0.8:
            return truncated[:last_space] + "..."
        else:
            return truncated + "..."
    
    def _calculate_linkedin_engagement(self, content: str, engagement_factors: Dict[str, float]) -> float:
        """Calcule le score d'engagement LinkedIn"""
        
        score = 0.5  # Score de base
        
        # Facteur ton professionnel
        professional_words = ["stratégique", "business", "opportunité", "analyse", "données"]
        if any(word in content.lower() for word in professional_words):
            score += engagement_factors["professional_tone"]
        
        # Facteur insights industrie
        if any(word in content.lower() for word in ["marché", "secteur", "industrie", "tendance"]):
            score += engagement_factors["industry_insights"]
        
        # Facteur data-driven
        if re.search(r'\d+%|\d+€|\d+B|\d+M', content):
            score += engagement_factors["data_driven"]
        
        # Facteur call to action
        if any(word in content.lower() for word in ["pensez-vous", "partagez", "commentaire", "avis"]):
            score += engagement_factors["call_to_action"]
        
        # Facteur contenu visuel (émojis comme proxy)
        emoji_count = len(re.findall(r'[😀-🿿]', content))
        if emoji_count > 0:
            score += engagement_factors["visual_content"]
        
        return min(score, 1.0)
    
    def _calculate_twitter_engagement(self, content: str, engagement_factors: Dict[str, float]) -> float:
        """Calcule le score d'engagement Twitter"""
        
        score = 0.4  # Score de base plus bas pour Twitter
        
        # Facteur trending topics (hashtags comme proxy)
        hashtag_count = content.count('#')
        if hashtag_count >= 2:
            score += engagement_factors["trending_topics"]
        
        # Facteur real-time news
        if any(word in content.lower() for word in ["alerte", "breaking", "maintenant", "urgent"]):
            score += engagement_factors["real_time_news"]
        
        # Facteur interaction communauté
        if any(word in content.lower() for word in ["rt", "thoughts", "avis", "?"]):
            score += engagement_factors["community_interaction"]
        
        # Facteur contenu visuel
        emoji_count = len(re.findall(r'[😀-🿿]', content))
        if emoji_count > 0:
            score += engagement_factors["visual_content"]
        
        # Facteur usage hashtags
        if hashtag_count > 0:
            score += engagement_factors["hashtag_usage"]
        
        return min(score, 1.0)
    
    def _calculate_instagram_engagement(self, content: str, engagement_factors: Dict[str, float]) -> float:
        """Calcule le score d'engagement Instagram"""
        
        score = 0.3  # Score de base
        
        # Facteur qualité visuelle (description visuelle comme proxy)
        if "[image:" in content.lower() or "visual" in content.lower():
            score += engagement_factors["visual_quality"]
        
        # Facteur storytelling
        if any(word in content.lower() for word in ["histoire", "découvrez", "révèle", "transformation"]):
            score += engagement_factors["storytelling"]
        
        # Facteur stratégie hashtags
        hashtag_count = content.count('#')
        if hashtag_count >= 5:
            score += engagement_factors["hashtag_strategy"]
        
        # Facteur interaction utilisateur
        if any(word in content.lower() for word in ["suivez", "commentez", "partagez", "tag"]):
            score += engagement_factors["user_interaction"]
        
        return min(score, 1.0)
    
    def _estimate_linkedin_metrics(self, engagement_score: float, sector: str) -> Dict[str, Any]:
        """Estime les métriques LinkedIn"""
        
        base_reach = {"Technology": 15000, "Finance": 12000, "HPC": 8000, "IA": 20000}
        sector_reach = base_reach.get(sector, 10000)
        
        estimated_reach = int(sector_reach * engagement_score)
        estimated_likes = int(estimated_reach * 0.05)
        estimated_comments = int(estimated_likes * 0.15)
        estimated_shares = int(estimated_likes * 0.08)
        
        return {
            "estimated_reach": f"{estimated_reach:,}",
            "estimated_likes": estimated_likes,
            "estimated_comments": estimated_comments,
            "estimated_shares": estimated_shares,
            "estimated_value": f"€{int(2500 * engagement_score):,}"
        }
    
    def _estimate_twitter_metrics(self, engagement_score: float, thread_length: int) -> Dict[str, Any]:
        """Estime les métriques Twitter"""
        
        base_reach = 5000 * thread_length  # Plus de reach pour les threads
        estimated_reach = int(base_reach * engagement_score)
        estimated_likes = int(estimated_reach * 0.08)
        estimated_retweets = int(estimated_likes * 0.25)
        estimated_replies = int(estimated_likes * 0.12)
        
        return {
            "estimated_reach": f"{estimated_reach:,}",
            "estimated_likes": estimated_likes,
            "estimated_retweets": estimated_retweets,
            "estimated_replies": estimated_replies,
            "estimated_value": f"€{int(1500 * engagement_score * thread_length):,}"
        }
    
    def _estimate_instagram_metrics(self, engagement_score: float, content_type: str) -> Dict[str, Any]:
        """Estime les métriques Instagram"""
        
        type_multiplier = {"post": 1.0, "story": 0.6, "reel": 2.5}
        multiplier = type_multiplier.get(content_type, 1.0)
        
        base_reach = int(8000 * multiplier)
        estimated_reach = int(base_reach * engagement_score)
        estimated_likes = int(estimated_reach * 0.07)
        estimated_comments = int(estimated_likes * 0.10)
        estimated_saves = int(estimated_likes * 0.05)
        
        return {
            "estimated_reach": f"{estimated_reach:,}",
            "estimated_likes": estimated_likes,
            "estimated_comments": estimated_comments,
            "estimated_saves": estimated_saves,
            "estimated_value": f"€{int(1800 * engagement_score * multiplier):,}"
        }
    
    def _get_optimal_posting_time(self, platform: str) -> str:
        """Retourne le meilleur moment pour publier sur une plateforme"""
        
        now = datetime.now()
        day_name = now.strftime("%A").lower()
        
        optimal_times = self.platforms[platform]["best_posting_times"]
        times = optimal_times.get(day_name, ["12:00"])
        
        return f"{day_name.capitalize()} {times[0]}"
    
    def _calculate_platform_analytics(self, platform: str) -> Dict[str, Any]:
        """Calcule les analytics pour une plateforme"""
        
        # Simulation d'analytics (à remplacer par de vraies données)
        return {
            "total_posts": 45,
            "avg_engagement_rate": "7.2%",
            "total_reach": "125K",
            "best_performing_content": "Tech insights",
            "optimal_posting_frequency": "1-2 posts/day",
            "audience_growth": "+15.3%",
            "estimated_monthly_value": "€12,500"
        }

# Test et démonstration
if __name__ == "__main__":
    system = SocialMediaContentSystem()
    
    # Test de génération de contenu
    test_intelligence = {
        "id": "INTEL_001",
        "title": "JUPITER atteint 1 exaflop - Premier supercalculateur exascale européen",
        "summary": "L'Europe franchit une étape historique avec JUPITER, premier supercalculateur exascale européen",
        "sector": "HPC",
        "confidence": 0.95,
        "market_size": "€2.3B",
        "growth_rate": "+180%",
        "expert": "Expert Semi-conducteurs (ESS)"
    }
    
    # Test LinkedIn
    linkedin_post = system.generate_linkedin_post(test_intelligence, "tech_breakthrough")
    print("✅ Post LinkedIn généré")
    print(f"📊 Score d'engagement: {linkedin_post['engagement_score']:.2f}")
    print(f"👥 Portée estimée: {linkedin_post['estimated_metrics']['estimated_reach']}")
    
    # Test Twitter Thread
    twitter_thread = system.generate_twitter_thread(test_intelligence, 5)
    print(f"\n✅ Thread Twitter généré ({twitter_thread['thread_length']} tweets)")
    print(f"📊 Score d'engagement: {twitter_thread['engagement_score']:.2f}")
    
    # Test Instagram
    instagram_post = system.generate_instagram_content(test_intelligence, "post")
    print(f"\n✅ Post Instagram généré")
    print(f"📊 Score d'engagement: {instagram_post['engagement_score']:.2f}")
    print(f"#️⃣ Hashtags: {len(instagram_post['hashtags'])}")
    
    # Test calendrier éditorial
    calendar = system.create_content_calendar([test_intelligence], 7)
    print(f"\n✅ Calendrier éditorial créé")
    print(f"📅 {calendar['summary']['total_content_pieces']} contenus sur {calendar['summary']['total_days']} jours")
    print(f"💰 Valeur estimée: {calendar['summary']['estimated_total_value']}")

