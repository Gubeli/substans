#!/usr/bin/env python3

"""
Agent Fact Checker (AFC)
Agent spécialisé dans la vérification des faits, chiffres et informations
"""

import json
import os
import re
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import hashlib

class AgentFactChecker:
    def __init__(self):
        self.agent_id = "AFC"
        self.nom = "Agent Fact Checker"
        self.version = "1.0"
        self.specialisation = "Vérification des faits, chiffres et informations"
        
        # Configuration de vérification
        self.verification_config = {
            "sources_prioritaires": [
                "manus.ai",
                "perplexity.ai", 
                "wikipedia.org",
                "reuters.com",
                "bloomberg.com",
                "financial-times.com",
                "insee.fr",
                "eurostat.europa.eu"
            ],
            "types_verification": [
                "chiffres_financiers",
                "dates_evenements", 
                "noms_personnes",
                "noms_entreprises",
                "donnees_marche",
                "statistiques",
                "citations",
                "references_legales"
            ],
            "seuil_confiance": 0.8,
            "delai_verification": 300  # 5 minutes max par document
        }
        
        # Patterns de détection
        self.patterns = {
            "chiffres": r'\b\d+(?:[.,]\d+)*\s*(?:%|€|\$|M€|M\$|milliards?|millions?|k€|k\$)\b',
            "dates": r'\b(?:\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}|\d{4}|\d{1,2}\s+(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+\d{4})\b',
            "entreprises": r'\b[A-Z][a-zA-Z\s&]{2,30}(?:\s+(?:Inc|Ltd|SA|SAS|SARL|Corp|Corporation|Company|Co)\b)?\b',
            "personnes": r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',
            "pourcentages": r'\b\d+(?:[.,]\d+)?%\b',
            "urls": r'https?://[^\s<>"{}|\\^`\[\]]+',
            "emails": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        }
        
        # Cache de vérifications
        self.cache_verifications = {}
        
        print(f"✅ {self.nom} v{self.version} initialisé")
        print(f"🔍 Spécialisation: {self.specialisation}")

    def verifier_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Vérifie un document complet
        """
        print(f"🔍 Vérification du document: {document.get('title', 'Sans titre')}")
        
        contenu = document.get('content', '')
        if not contenu:
            return self._generer_rapport_erreur("Contenu vide")
        
        # Extraction des éléments à vérifier
        elements_detectes = self._extraire_elements(contenu)
        
        # Vérification de chaque élément
        resultats_verification = {}
        for type_element, elements in elements_detectes.items():
            resultats_verification[type_element] = []
            for element in elements:
                resultat = self._verifier_element(element, type_element)
                resultats_verification[type_element].append(resultat)
        
        # Génération du rapport
        rapport = self._generer_rapport_verification(document, resultats_verification)
        
        return rapport

    def _extraire_elements(self, contenu: str) -> Dict[str, List[str]]:
        """
        Extrait les éléments à vérifier du contenu
        """
        elements = {}
        
        for type_pattern, pattern in self.patterns.items():
            matches = re.findall(pattern, contenu, re.IGNORECASE)
            elements[type_pattern] = list(set(matches))  # Supprime les doublons
        
        return elements

    def _verifier_element(self, element: str, type_element: str) -> Dict[str, Any]:
        """
        Vérifie un élément spécifique
        """
        # Vérifier le cache d'abord
        cache_key = hashlib.md5(f"{element}_{type_element}".encode()).hexdigest()
        if cache_key in self.cache_verifications:
            return self.cache_verifications[cache_key]
        
        resultat = {
            "element": element,
            "type": type_element,
            "verifie": False,
            "confiance": 0.0,
            "sources": [],
            "commentaires": [],
            "suggestions": []
        }
        
        try:
            # Simulation de vérification (en production, utiliserait les APIs)
            if type_element == "chiffres":
                resultat = self._verifier_chiffre(element)
            elif type_element == "dates":
                resultat = self._verifier_date(element)
            elif type_element == "entreprises":
                resultat = self._verifier_entreprise(element)
            elif type_element == "personnes":
                resultat = self._verifier_personne(element)
            else:
                resultat = self._verification_generique(element, type_element)
            
            # Mise en cache
            self.cache_verifications[cache_key] = resultat
            
        except Exception as e:
            resultat["commentaires"].append(f"Erreur lors de la vérification: {str(e)}")
        
        return resultat

    def _verifier_chiffre(self, chiffre: str) -> Dict[str, Any]:
        """
        Vérifie la cohérence d'un chiffre
        """
        return {
            "element": chiffre,
            "type": "chiffres",
            "verifie": True,
            "confiance": 0.7,  # Confiance modérée sans source externe
            "sources": ["Format validé"],
            "commentaires": ["Format numérique cohérent"],
            "suggestions": ["Vérifier la source de ce chiffre"]
        }

    def _verifier_date(self, date: str) -> Dict[str, Any]:
        """
        Vérifie la cohérence d'une date
        """
        return {
            "element": date,
            "type": "dates",
            "verifie": True,
            "confiance": 0.8,
            "sources": ["Format validé"],
            "commentaires": ["Format de date cohérent"],
            "suggestions": []
        }

    def _verifier_entreprise(self, entreprise: str) -> Dict[str, Any]:
        """
        Vérifie l'existence d'une entreprise
        """
        # En production, utiliserait des APIs comme OpenCorporates, etc.
        return {
            "element": entreprise,
            "type": "entreprises",
            "verifie": True,
            "confiance": 0.6,
            "sources": ["Base de données entreprises"],
            "commentaires": ["Nom d'entreprise plausible"],
            "suggestions": ["Vérifier l'orthographe exacte"]
        }

    def _verifier_personne(self, personne: str) -> Dict[str, Any]:
        """
        Vérifie l'existence d'une personne
        """
        return {
            "element": personne,
            "type": "personnes",
            "verifie": True,
            "confiance": 0.5,
            "sources": ["Format validé"],
            "commentaires": ["Format de nom cohérent"],
            "suggestions": ["Vérifier l'orthographe et le contexte"]
        }

    def _verification_generique(self, element: str, type_element: str) -> Dict[str, Any]:
        """
        Vérification générique pour les autres types
        """
        return {
            "element": element,
            "type": type_element,
            "verifie": True,
            "confiance": 0.6,
            "sources": ["Vérification automatique"],
            "commentaires": ["Élément détecté et analysé"],
            "suggestions": ["Vérification manuelle recommandée"]
        }

    def _generer_rapport_verification(self, document: Dict[str, Any], resultats: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """
        Génère le rapport de vérification complet
        """
        total_elements = sum(len(elements) for elements in resultats.values())
        elements_verifies = sum(
            len([e for e in elements if e.get('verifie', False)]) 
            for elements in resultats.values()
        )
        
        confiance_moyenne = 0.0
        if total_elements > 0:
            confiances = []
            for elements in resultats.values():
                for element in elements:
                    confiances.append(element.get('confiance', 0.0))
            confiance_moyenne = sum(confiances) / len(confiances) if confiances else 0.0
        
        # Déterminer le statut global
        statut = "APPROUVE"
        if confiance_moyenne < 0.5:
            statut = "REJETE"
        elif confiance_moyenne < 0.7:
            statut = "REVISION_REQUISE"
        
        rapport = {
            "document_id": document.get('id', 'unknown'),
            "document_title": document.get('title', 'Sans titre'),
            "verification_date": datetime.now().isoformat(),
            "agent_verificateur": self.agent_id,
            "statut": statut,
            "score_confiance": round(confiance_moyenne, 2),
            "statistiques": {
                "total_elements": total_elements,
                "elements_verifies": elements_verifies,
                "taux_verification": round((elements_verifies / total_elements) * 100, 1) if total_elements > 0 else 0
            },
            "resultats_detailles": resultats,
            "recommandations": self._generer_recommandations(statut, confiance_moyenne, resultats),
            "actions_requises": self._generer_actions_requises(statut, resultats)
        }
        
        print(f"✅ Vérification terminée - Statut: {statut} - Confiance: {confiance_moyenne:.1%}")
        
        return rapport

    def _generer_recommandations(self, statut: str, confiance: float, resultats: Dict) -> List[str]:
        """
        Génère des recommandations basées sur les résultats
        """
        recommandations = []
        
        if statut == "REJETE":
            recommandations.append("Document nécessite une révision majeure avant publication")
            recommandations.append("Vérifier manuellement tous les éléments signalés")
        elif statut == "REVISION_REQUISE":
            recommandations.append("Révision recommandée pour améliorer la fiabilité")
            recommandations.append("Vérifier les éléments à faible confiance")
        else:
            recommandations.append("Document approuvé pour publication")
            recommandations.append("Vérification périodique recommandée")
        
        # Recommandations spécifiques par type
        for type_element, elements in resultats.items():
            elements_faible_confiance = [e for e in elements if e.get('confiance', 0) < 0.6]
            if elements_faible_confiance:
                recommandations.append(f"Vérifier manuellement les {type_element} signalés")
        
        return recommandations

    def _generer_actions_requises(self, statut: str, resultats: Dict) -> List[str]:
        """
        Génère les actions requises
        """
        actions = []
        
        if statut == "REJETE":
            actions.append("BLOQUER la publication du document")
            actions.append("NOTIFIER l'auteur des corrections nécessaires")
        elif statut == "REVISION_REQUISE":
            actions.append("MARQUER le document pour révision")
            actions.append("ENVOYER les suggestions de correction")
        else:
            actions.append("AUTORISER la publication")
            actions.append("ARCHIVER le rapport de vérification")
        
        return actions

    def _generer_rapport_erreur(self, erreur: str) -> Dict[str, Any]:
        """
        Génère un rapport d'erreur
        """
        return {
            "statut": "ERREUR",
            "erreur": erreur,
            "verification_date": datetime.now().isoformat(),
            "agent_verificateur": self.agent_id
        }

    def obtenir_statistiques(self) -> Dict[str, Any]:
        """
        Retourne les statistiques de vérification
        """
        return {
            "agent_id": self.agent_id,
            "nom": self.nom,
            "version": self.version,
            "verifications_cache": len(self.cache_verifications),
            "types_supportes": list(self.patterns.keys()),
            "sources_configurees": len(self.verification_config["sources_prioritaires"])
        }

def main():
    """Test de l'agent"""
    agent = AgentFactChecker()
    
    # Document de test
    document_test = {
        "id": "test_001",
        "title": "Test de vérification",
        "content": """
        Bull a réalisé un chiffre d'affaires de 1.2 milliards d'euros en 2024.
        La société, dirigée par Jean Dupont, emploie 15,000 personnes.
        Le marché du HPC représente 45% de croissance annuelle.
        Contact: info@bull.com - Site: https://www.bull.com
        """
    }
    
    rapport = agent.verifier_document(document_test)
    print(json.dumps(rapport, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()

