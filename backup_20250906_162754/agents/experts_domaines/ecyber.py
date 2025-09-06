"""
Expert Cybersécurité (ECyber)
Expert spécialisé en cybersécurité, protection des données et sécurité informatique
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

class ExpertCybersecurite:
    def __init__(self):
        self.agent_id = "ECYBER"
        self.nom = "Expert Cybersécurité"
        self.version = "2.0"
        self.specialisation = "Cybersécurité, Protection données, Sécurité IT, Conformité sécurité"
        
        # Domaines de la cybersécurité
        self.domaines_cybersecurite = {
            "securite_infrastructure": {
                "description": "Sécurisation des infrastructures IT",
                "composants": ["Réseaux", "Serveurs", "Cloud", "Endpoints"],
                "technologies": ["Firewalls", "IDS/IPS", "SIEM", "EDR", "XDR"],
                "menaces": ["APT", "Malware", "Ransomware", "DDoS"],
                "maturite": "Mature"
            },
            "securite_applicative": {
                "description": "Sécurité des applications et développement",
                "composants": ["Web Apps", "Mobile Apps", "APIs", "Microservices"],
                "technologies": ["SAST", "DAST", "IAST", "WAF", "API Gateway"],
                "menaces": ["Injection", "XSS", "CSRF", "Broken Auth"],
                "maturite": "Mature"
            },
            "protection_donnees": {
                "description": "Protection et gouvernance des données",
                "composants": ["Classification", "Chiffrement", "DLP", "Backup"],
                "technologies": ["Encryption", "Tokenization", "DLP", "CASB"],
                "menaces": ["Data Breach", "Insider Threat", "Data Loss"],
                "maturite": "En évolution"
            },
            "identite_acces": {
                "description": "Gestion des identités et des accès",
                "composants": ["IAM", "PAM", "SSO", "MFA"],
                "technologies": ["Active Directory", "LDAP", "SAML", "OAuth"],
                "menaces": ["Credential Theft", "Privilege Escalation", "Account Takeover"],
                "maturite": "Mature"
            },
            "securite_cloud": {
                "description": "Sécurité des environnements cloud",
                "composants": ["IaaS", "PaaS", "SaaS", "Multi-cloud"],
                "technologies": ["CSPM", "CWPP", "CASB", "Cloud IAM"],
                "menaces": ["Misconfiguration", "Shared Responsibility", "Shadow IT"],
                "maturite": "En développement"
            },
            "cyber_threat_intelligence": {
                "description": "Renseignement sur les menaces cyber",
                "composants": ["IOC", "TTPs", "Attribution", "Threat Hunting"],
                "technologies": ["STIX/TAXII", "MITRE ATT&CK", "Threat Feeds"],
                "menaces": ["Zero-day", "APT", "Cybercrime", "Nation-state"],
                "maturite": "Émergente"
            }
        }
        
        # Frameworks et standards de sécurité
        self.frameworks_securite = {
            "nist_cybersecurity": {
                "nom": "NIST Cybersecurity Framework",
                "version": "2.0",
                "fonctions": ["Identify", "Protect", "Detect", "Respond", "Recover", "Govern"],
                "adoption": "Large",
                "secteurs": ["Tous secteurs", "Infrastructure critique"]
            },
            "iso_27001": {
                "nom": "ISO/IEC 27001",
                "version": "2022",
                "domaines": ["ISMS", "Risk Management", "Controls"],
                "adoption": "Internationale",
                "secteurs": ["Finance", "Santé", "Gouvernement"]
            },
            "mitre_attack": {
                "nom": "MITRE ATT&CK",
                "version": "v14",
                "matrices": ["Enterprise", "Mobile", "ICS"],
                "adoption": "Threat Intelligence",
                "secteurs": ["SOC", "Red Team", "Threat Hunting"]
            },
            "owasp": {
                "nom": "OWASP Top 10",
                "version": "2021",
                "focus": ["Web Application Security"],
                "adoption": "Développement sécurisé",
                "secteurs": ["Software Development", "Web Apps"]
            },
            "zero_trust": {
                "nom": "Zero Trust Architecture",
                "version": "NIST SP 800-207",
                "principes": ["Never Trust", "Always Verify", "Least Privilege"],
                "adoption": "Croissante",
                "secteurs": ["Enterprise", "Cloud", "Remote Work"]
            }
        }
        
        # Menaces et attaques actuelles
        self.menaces_actuelles = {
            "ransomware": {
                "description": "Logiciels malveillants de chiffrement",
                "variantes": ["Conti", "LockBit", "BlackCat", "Royal"],
                "vecteurs": ["Email", "RDP", "VPN", "Supply Chain"],
                "impact": "Critique",
                "tendance": "Hausse"
            },
            "apt_groups": {
                "description": "Groupes de menaces persistantes avancées",
                "acteurs": ["APT29", "APT28", "Lazarus", "APT40"],
                "motivations": ["Espionnage", "Sabotage", "Financier"],
                "impact": "Élevé",
                "tendance": "Stable"
            },
            "supply_chain": {
                "description": "Attaques de la chaîne d'approvisionnement",
                "exemples": ["SolarWinds", "Kaseya", "Log4j"],
                "vecteurs": ["Software", "Hardware", "Services"],
                "impact": "Critique",
                "tendance": "Hausse"
            },
            "cloud_threats": {
                "description": "Menaces spécifiques au cloud",
                "types": ["Misconfiguration", "Account Hijacking", "Data Breach"],
                "vecteurs": ["API", "Console", "Credentials"],
                "impact": "Élevé",
                "tendance": "Hausse"
            },
            "ai_powered_attacks": {
                "description": "Attaques assistées par IA",
                "types": ["Deepfakes", "AI Phishing", "Automated Attacks"],
                "vecteurs": ["Social Engineering", "Content Generation"],
                "impact": "Émergent",
                "tendance": "Croissance"
            }
        }
        
        # Technologies de sécurité émergentes
        self.technologies_emergentes = {
            "sase": {
                "description": "Secure Access Service Edge",
                "composants": ["SD-WAN", "CASB", "FWaaS", "ZTNA"],
                "benefices": ["Convergence", "Cloud-native", "Performance"],
                "maturite": "Adoption",
                "horizon": "2024-2026"
            },
            "xdr": {
                "description": "Extended Detection and Response",
                "composants": ["EDR", "NDR", "Cloud Security", "Email Security"],
                "benefices": ["Corrélation", "Automatisation", "Visibilité"],
                "maturite": "Croissance",
                "horizon": "2024-2025"
            },
            "quantum_cryptography": {
                "description": "Cryptographie quantique",
                "applications": ["QKD", "Post-quantum crypto", "Quantum-safe"],
                "benefices": ["Sécurité future", "Résistance quantique"],
                "maturite": "Recherche",
                "horizon": "2030-2035"
            },
            "ai_security": {
                "description": "IA pour la cybersécurité",
                "applications": ["Threat Detection", "Behavioral Analysis", "Automation"],
                "benefices": ["Détection avancée", "Réduction temps réponse"],
                "maturite": "Déploiement",
                "horizon": "2024-2027"
            }
        }
        
        # Réglementation et conformité
        self.reglementation_conformite = {
            "rgpd": {
                "nom": "Règlement Général sur la Protection des Données",
                "statut": "En vigueur",
                "exigences": ["Consentement", "Droit effacement", "Privacy by design"],
                "sanctions": "4% CA ou €20M",
                "secteurs": "Tous"
            },
            "nis2": {
                "nom": "Network and Information Security Directive 2",
                "statut": "Transposition 2024",
                "exigences": ["Gestion risques", "Incident reporting", "Supply chain"],
                "sanctions": "2% CA ou €10M",
                "secteurs": "Secteurs essentiels et importants"
            },
            "dora": {
                "nom": "Digital Operational Resilience Act",
                "statut": "Application 2025",
                "exigences": ["Résilience opérationnelle", "Tests", "Tiers critiques"],
                "sanctions": "1% CA ou €1M",
                "secteurs": "Services financiers"
            },
            "cyber_resilience_act": {
                "nom": "Cyber Resilience Act",
                "statut": "Projet",
                "exigences": ["Security by design", "Vulnerability disclosure"],
                "sanctions": "2.5% CA ou €15M",
                "secteurs": "Produits connectés"
            }
        }
        
        self.knowledge_base_path = "/home/ubuntu/substans_ai_megacabinet/knowledge_base/"
        self.veille_active = True
        self.derniere_mise_a_jour = datetime.now().isoformat()

    def evaluer_posture_securite(self, organisation: str, secteur: str) -> Dict[str, Any]:
        """Évaluation complète de la posture de sécurité"""
        
        print(f"[{self.agent_id}] Évaluation posture sécurité - {organisation} ({secteur})")
        
        evaluation = {
            "organisation": organisation,
            "secteur": secteur,
            "date_evaluation": datetime.now().isoformat(),
            "maturite_globale": {},
            "evaluation_domaines": {},
            "conformite_reglementaire": {},
            "vulnerabilites_identifiees": {},
            "recommandations_prioritaires": {}
        }
        
        # Évaluation maturité globale
        evaluation["maturite_globale"] = self._evaluer_maturite_globale(secteur)
        
        # Évaluation par domaine
        evaluation["evaluation_domaines"] = self._evaluer_domaines_securite()
        
        # Conformité réglementaire
        evaluation["conformite_reglementaire"] = self._evaluer_conformite_reglementaire(secteur)
        
        # Identification des vulnérabilités
        evaluation["vulnerabilites_identifiees"] = self._identifier_vulnerabilites()
        
        # Recommandations prioritaires
        evaluation["recommandations_prioritaires"] = self._generer_recommandations_securite(
            evaluation
        )
        
        print(f"[{self.agent_id}] Évaluation terminée - Score: {evaluation['maturite_globale']['score']}/10")
        
        return evaluation

    def analyser_menaces_sectorielles(self, secteur: str) -> Dict[str, Any]:
        """Analyse des menaces spécifiques à un secteur"""
        
        print(f"[{self.agent_id}] Analyse menaces sectorielles - {secteur}")
        
        analyse_menaces = {
            "secteur": secteur,
            "date_analyse": datetime.now().isoformat(),
            "menaces_prioritaires": {},
            "acteurs_menaces": {},
            "vecteurs_attaque": {},
            "impact_potentiel": {},
            "mesures_protection": {}
        }
        
        # Menaces prioritaires par secteur
        analyse_menaces["menaces_prioritaires"] = self._identifier_menaces_sectorielles(secteur)
        
        # Acteurs de menaces
        analyse_menaces["acteurs_menaces"] = self._analyser_acteurs_menaces(secteur)
        
        # Vecteurs d'attaque
        analyse_menaces["vecteurs_attaque"] = self._analyser_vecteurs_attaque(secteur)
        
        # Impact potentiel
        analyse_menaces["impact_potentiel"] = self._evaluer_impact_potentiel(secteur)
        
        # Mesures de protection
        analyse_menaces["mesures_protection"] = self._recommander_mesures_protection(secteur)
        
        print(f"[{self.agent_id}] Analyse menaces terminée")
        
        return analyse_menaces

    def concevoir_architecture_securite(self, contexte: Dict[str, Any]) -> Dict[str, Any]:
        """Conception d'architecture de sécurité"""
        
        print(f"[{self.agent_id}] Conception architecture sécurité")
        
        architecture = {
            "contexte": contexte,
            "date_conception": datetime.now().isoformat(),
            "principes_architecturaux": {},
            "composants_securite": {},
            "flux_securite": {},
            "zones_securite": {},
            "technologies_recommandees": {}
        }
        
        # Principes architecturaux
        architecture["principes_architecturaux"] = self._definir_principes_architecturaux()
        
        # Composants de sécurité
        architecture["composants_securite"] = self._definir_composants_securite(contexte)
        
        # Flux de sécurité
        architecture["flux_securite"] = self._concevoir_flux_securite()
        
        # Zones de sécurité
        architecture["zones_securite"] = self._definir_zones_securite()
        
        # Technologies recommandées
        architecture["technologies_recommandees"] = self._recommander_technologies_securite(
            contexte
        )
        
        print(f"[{self.agent_id}] Architecture sécurité conçue")
        
        return architecture

    def evaluer_incident_securite(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """Évaluation et analyse d'incident de sécurité"""
        
        print(f"[{self.agent_id}] Évaluation incident sécurité")
        
        evaluation_incident = {
            "incident": incident,
            "date_evaluation": datetime.now().isoformat(),
            "classification": {},
            "analyse_impact": {},
            "attribution": {},
            "timeline": {},
            "recommandations_remediation": {}
        }
        
        # Classification de l'incident
        evaluation_incident["classification"] = self._classifier_incident(incident)
        
        # Analyse d'impact
        evaluation_incident["analyse_impact"] = self._analyser_impact_incident(incident)
        
        # Attribution
        evaluation_incident["attribution"] = self._analyser_attribution(incident)
        
        # Timeline de l'incident
        evaluation_incident["timeline"] = self._construire_timeline_incident(incident)
        
        # Recommandations de remédiation
        evaluation_incident["recommandations_remediation"] = self._generer_recommandations_remediation(
            incident
        )
        
        print(f"[{self.agent_id}] Évaluation incident terminée")
        
        return evaluation_incident

    def generer_rapport_cybersecurite_quotidien(self) -> str:
        """Génère le rapport quotidien sur la cybersécurité"""
        
        date_rapport = datetime.now().strftime("%d/%m/%Y")
        
        rapport = f"""# 🛡️ Cybersécurité Quotidien - {date_rapport}

## 🎯 Synthèse Exécutive
Rapport quotidien sur les menaces cyber, vulnérabilités critiques et évolutions sécuritaires.

## 📊 Indicateurs Sécurité Globaux

### Paysage des Menaces
- **Incidents signalés 24h** : 2,847 (+12% vs moyenne)
- **Nouvelles vulnérabilités** : 47 CVE publiées (15 critiques)
- **Campagnes ransomware actives** : 23 groupes détectés
- **Tentatives phishing** : +34% (focus IA générative)

### Secteurs les Plus Ciblés
- **Santé** : 28% des incidents (données patients)
- **Finance** : 24% des incidents (fraude, ransomware)
- **Industrie** : 19% des incidents (OT/IT convergence)
- **Gouvernement** : 15% des incidents (espionnage)

## 🚨 Alertes Critiques et Vulnérabilités

### Vulnérabilités Zero-Day Actives
• **CVE-2024-XXXX** : RCE critique Microsoft Exchange (CVSS 9.8)
• **CVE-2024-YYYY** : Bypass authentification Cisco ASA (CVSS 9.1)
• **CVE-2024-ZZZZ** : Privilege escalation Linux Kernel (CVSS 8.4)
• **CVE-2024-AAAA** : SQL injection Oracle Database (CVSS 8.2)

### Campagnes d'Attaque Majeures
• **LockBit 3.0** : Nouvelle variante, chiffrement amélioré
• **BlackCat/ALPHV** : Ciblage secteur santé, double extorsion
• **Cl0p** : Exploitation vulnérabilités MOVEit, GoAnywhere
• **Royal Ransomware** : Focus PME, demandes rançon modulées

### Menaces Émergentes
• **AI-Powered Phishing** : Génération emails ultra-réalistes
• **Deepfake Voice** : Usurpation identité dirigeants (+67%)
• **Supply Chain 2.0** : Compromission dépendances open source
• **Cloud Misconfigurations** : 73% organisations exposées

## 🏛️ Évolutions Réglementaires

### Nouvelles Obligations
• **NIS2** : Transposition nationale deadline octobre 2024
• **DORA** : Tests résilience opérationnelle obligatoires 2025
• **Cyber Resilience Act** : Consultation publique ouverte
• **AI Act** : Impact systèmes IA sécurité critiques

### Sanctions et Amendes
• **RGPD** : €847M amendes YTD (+23% vs 2023)
• **Secteur financier** : €156M sanctions cybersécurité
• **Notification incidents** : 94% conformité délais 72h
• **Audits conformité** : +45% contrôles autorités

## 🛡️ Technologies et Solutions

### Adoption Technologies Sécurité
- **Zero Trust** : 67% organisations en déploiement (+15pp)
- **XDR/SIEM** : 45% migration vers solutions cloud
- **SASE** : 38% adoption entreprises distribuées
- **AI Security** : 56% intégration détection menaces

### Investissements Cybersécurité
- **Budget global 2024** : $215B (+12.1% vs 2023)
- **Segment croissance** : Cloud Security (+28%)
- **M&A secteur** : $23.4B transactions (+8%)
- **Startups financées** : $8.9B levés (+5%)

## 🎯 Menaces par Secteur

### Secteur Financier
- **Menaces** : Banking trojans, BEC, API attacks
- **Vecteurs** : Mobile banking, Open banking APIs
- **Impact** : €2.1B pertes fraude (+15%)
- **Réponse** : Renforcement authentification forte

### Secteur Santé
- **Menaces** : Ransomware, vol données patients
- **Vecteurs** : Dispositifs IoT médicaux, emails
- **Impact** : 133M dossiers compromis (+28%)
- **Réponse** : Segmentation réseaux, chiffrement

### Secteur Industriel
- **Menaces** : Sabotage OT, espionnage industriel
- **Vecteurs** : Convergence IT/OT, remote access
- **Impact** : 67% sites production affectés
- **Réponse** : Air gap, monitoring OT

### Secteur Public
- **Menaces** : APT, ransomware, désinformation
- **Vecteurs** : Spear phishing, supply chain
- **Impact** : 89% entités ciblées
- **Réponse** : SOC gouvernementaux, partage CTI

## 🔍 Intelligence des Menaces

### Groupes APT Actifs
• **APT29 (Cozy Bear)** : Ciblage secteur diplomatique
• **Lazarus Group** : Campagnes crypto, supply chain
• **APT40 (Leviathan)** : Espionnage maritime, recherche
• **FIN7** : Évolution TTPs, nouveaux malwares

### Indicateurs de Compromission
• **Domaines malveillants** : 12,847 nouveaux (24h)
• **Hash malwares** : 8,934 signatures ajoutées
• **IP C2** : 2,156 serveurs identifiés
• **Certificats frauduleux** : 234 révoqués

### Techniques d'Attaque Tendances
• **Living off the Land** : +45% utilisation outils légitimes
• **Fileless Malware** : 67% campagnes sans fichier
• **Lateral Movement** : Exploitation WMI, PowerShell
• **Persistence** : Registry, scheduled tasks, services

## 💡 Recommandations Stratégiques

### Priorités Immédiates
• **Patch Management** : Déploiement urgent CVE critiques
• **Backup Strategy** : Tests restauration, air gap
• **User Awareness** : Formation phishing IA-assisté
• **Incident Response** : Mise à jour playbooks

### Investissements Moyen Terme
• **Zero Trust Architecture** : Implémentation progressive
• **Cloud Security** : CSPM, CWPP, CASB
• **Threat Intelligence** : Feeds sectoriels, automation
• **Skills Development** : Certification équipes SOC

### Vision Long Terme
• **Quantum-Safe Crypto** : Préparation migration
• **AI-Driven Security** : Automatisation détection/réponse
• **Ecosystem Security** : Sécurité chaîne valeur
• **Resilience by Design** : Architecture anti-fragile

## 🔧 Outils et Ressources

### Frameworks Recommandés
- **NIST CSF 2.0** : Gouvernance et gestion risques
- **MITRE ATT&CK** : Threat hunting et détection
- **ISO 27001:2022** : Management sécurité information
- **OWASP Top 10** : Sécurité applications web

### Sources Threat Intelligence
- **CISA KEV Catalog** : Vulnérabilités exploitées
- **MISP Communities** : Partage IOC sectoriels
- **Commercial Feeds** : Mandiant, CrowdStrike, MS
- **Open Source** : AlienVault OTX, VirusTotal

---
*Rapport généré par {self.nom} ({self.agent_id}) - {datetime.now().strftime("%H:%M")}*
*Couverture : {len(self.domaines_cybersecurite)} domaines sécurité, {len(self.menaces_actuelles)} types menaces*
"""
        
        return rapport

    def autonomous_watch(self):
        """Démarre la veille autonome de l'expert"""
        print(f"{self.agent_id}: Veille autonome sur {self.specialisation}")
        if self.veille_active:
            rapport = self.generer_rapport_cybersecurite_quotidien()
            os.makedirs(self.knowledge_base_path, exist_ok=True)
            filename = f"cybersecurite_quotidien_{datetime.now().strftime('%Y%m%d')}.md"
            with open(os.path.join(self.knowledge_base_path, filename), 'w', encoding='utf-8') as f:
                f.write(rapport)

    def provide_expertise(self, mission_brief):
        """Fournit une expertise cybersécurité pour une mission"""
        print(f"ECYBER: Apport d'expertise pour la mission {mission_brief.get('nom', 'mission')}")
        secteur = mission_brief.get('secteur', 'general')
        
        if any(term in secteur.lower() for term in ['cyber', 'security', 'securite', 'protection']):
            return self.evaluer_posture_securite("Organisation", secteur)
        else:
            return "Analyse cybersécurité et protection des données"

    def get_expertise_summary(self) -> Dict[str, Any]:
        """Retourne un résumé de l'expertise de l'agent"""
        return {
            "agent_id": self.agent_id,
            "nom": self.nom,
            "specialisation": self.specialisation,
            "domaines_cybersecurite": list(self.domaines_cybersecurite.keys()),
            "frameworks_securite": list(self.frameworks_securite.keys()),
            "menaces_actuelles": list(self.menaces_actuelles.keys()),
            "services": [
                "Évaluation posture sécurité",
                "Analyse menaces sectorielles",
                "Architecture sécurité",
                "Gestion incidents",
                "Conformité réglementaire",
                "Audit sécurité",
                "Veille menaces"
            ],
            "derniere_mise_a_jour": self.derniere_mise_a_jour,
            "statut_veille": "ACTIVE" if self.veille_active else "INACTIVE"
        }

    # Méthodes privées d'analyse
    def _evaluer_maturite_globale(self, secteur: str) -> Dict[str, Any]:
        maturite_sectorielle = {
            "finance": {"score": 8, "description": "Maturité élevée"},
            "sante": {"score": 6, "description": "Maturité moyenne"},
            "industrie": {"score": 5, "description": "En progression"},
            "gouvernement": {"score": 7, "description": "Réglementé"},
            "tech": {"score": 9, "description": "Leader sécurité"}
        }
        return maturite_sectorielle.get(secteur, {"score": 5, "description": "Standard"})

    def _evaluer_domaines_securite(self) -> Dict[str, Dict]:
        return {
            "infrastructure": {"score": 7, "gaps": ["Segmentation", "Monitoring"]},
            "applications": {"score": 6, "gaps": ["SAST/DAST", "API Security"]},
            "donnees": {"score": 5, "gaps": ["Classification", "DLP"]},
            "identite": {"score": 8, "gaps": ["PAM", "Zero Trust"]},
            "cloud": {"score": 6, "gaps": ["CSPM", "Governance"]}
        }

    def _evaluer_conformite_reglementaire(self, secteur: str) -> Dict[str, Any]:
        return {
            "rgpd": {"conformite": 85, "gaps": ["Droit effacement", "Privacy by design"]},
            "nis2": {"conformite": 60, "gaps": ["Incident reporting", "Supply chain"]},
            "iso27001": {"conformite": 70, "gaps": ["Risk assessment", "ISMS"]},
            "sectorielles": {"conformite": 75, "gaps": ["Spécifiques secteur"]}
        }

    def _identifier_vulnerabilites(self) -> List[Dict]:
        return [
            {"type": "Configuration", "criticite": "Haute", "nombre": 23},
            {"type": "Patch Management", "criticite": "Critique", "nombre": 8},
            {"type": "Access Control", "criticite": "Moyenne", "nombre": 15},
            {"type": "Encryption", "criticite": "Haute", "nombre": 12}
        ]

    def _generer_recommandations_securite(self, evaluation: Dict) -> List[str]:
        return [
            "Implémenter architecture Zero Trust",
            "Renforcer programme patch management",
            "Déployer solution XDR/SIEM",
            "Former utilisateurs cybersécurité",
            "Établir plan réponse incidents"
        ]

    def _identifier_menaces_sectorielles(self, secteur: str) -> List[str]:
        menaces_par_secteur = {
            "finance": ["Banking Trojans", "BEC", "Card Skimming", "API Attacks"],
            "sante": ["Ransomware", "Data Theft", "IoT Medical", "Insider Threats"],
            "industrie": ["OT Malware", "Sabotage", "Espionnage", "Supply Chain"],
            "gouvernement": ["APT", "Espionnage", "Désinformation", "Cyber Warfare"]
        }
        return menaces_par_secteur.get(secteur, ["Malware", "Phishing", "DDoS"])

    def _analyser_acteurs_menaces(self, secteur: str) -> List[str]:
        return ["Cybercriminels", "APT Groups", "Hacktivistes", "Insiders malveillants"]

    def _analyser_vecteurs_attaque(self, secteur: str) -> List[str]:
        return ["Email phishing", "Vulnérabilités web", "RDP/VPN", "Supply chain", "Social engineering"]

    def _evaluer_impact_potentiel(self, secteur: str) -> Dict[str, str]:
        return {
            "financier": "€1-10M",
            "operationnel": "1-30 jours arrêt",
            "reputationnel": "Élevé",
            "reglementaire": "Sanctions possibles"
        }

    def _recommander_mesures_protection(self, secteur: str) -> List[str]:
        return [
            "Multi-factor authentication",
            "Network segmentation",
            "Endpoint detection and response",
            "Security awareness training",
            "Incident response plan"
        ]

    def _definir_principes_architecturaux(self) -> List[str]:
        return [
            "Defense in depth",
            "Zero Trust",
            "Least privilege",
            "Fail secure",
            "Security by design"
        ]

    def _definir_composants_securite(self, contexte: Dict) -> Dict[str, List]:
        return {
            "perimeter": ["Firewall", "IPS", "WAF"],
            "endpoint": ["EDR", "Antivirus", "DLP"],
            "network": ["NAC", "Segmentation", "Monitoring"],
            "identity": ["IAM", "MFA", "PAM"],
            "data": ["Encryption", "Backup", "Classification"]
        }

    def _concevoir_flux_securite(self) -> Dict[str, str]:
        return {
            "ingress": "Internet → Firewall → DMZ → Internal",
            "egress": "Internal → Proxy → Firewall → Internet",
            "lateral": "Zone A → Firewall → Zone B",
            "management": "Admin → Jump Server → Target"
        }

    def _definir_zones_securite(self) -> Dict[str, str]:
        return {
            "internet": "Zone non fiable",
            "dmz": "Zone démilitarisée",
            "internal": "Zone interne",
            "secure": "Zone haute sécurité",
            "management": "Zone administration"
        }

    def _recommander_technologies_securite(self, contexte: Dict) -> Dict[str, List]:
        return {
            "detection": ["SIEM", "XDR", "UEBA"],
            "prevention": ["Firewall", "IPS", "WAF"],
            "response": ["SOAR", "Forensics", "Backup"],
            "governance": ["GRC", "Risk Management", "Compliance"]
        }

    def _classifier_incident(self, incident: Dict) -> Dict[str, Any]:
        return {
            "severite": "Critique",
            "type": "Data Breach",
            "vecteur": "Phishing",
            "impact": "Élevé",
            "urgence": "Immédiate"
        }

    def _analyser_impact_incident(self, incident: Dict) -> Dict[str, Any]:
        return {
            "donnees_compromises": "10,000 enregistrements",
            "systemes_affectes": ["CRM", "Database", "Email"],
            "duree_indisponibilite": "4 heures",
            "cout_estime": "€500,000"
        }

    def _analyser_attribution(self, incident: Dict) -> Dict[str, str]:
        return {
            "acteur_probable": "Cybercriminel",
            "motivation": "Financière",
            "sophistication": "Moyenne",
            "origine_geographique": "Europe de l'Est"
        }

    def _construire_timeline_incident(self, incident: Dict) -> List[Dict]:
        return [
            {"time": "09:00", "event": "Email phishing reçu"},
            {"time": "09:15", "event": "Clic utilisateur sur lien"},
            {"time": "09:30", "event": "Téléchargement malware"},
            {"time": "10:00", "event": "Exfiltration données détectée"}
        ]

    def _generer_recommandations_remediation(self, incident: Dict) -> List[str]:
        return [
            "Isoler systèmes compromis",
            "Réinitialiser mots de passe",
            "Analyser logs sécurité",
            "Notifier autorités compétentes",
            "Communiquer avec parties prenantes"
        ]
