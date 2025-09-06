# Système de Structuration et Catégorisation - Base de Connaissances Substans.ai

## 1. Taxonomie Principale

### 1.1 Catégories de Premier Niveau

#### A. CONSTRUCTION_SUBSTANS
Documents liés à la création, développement et évolution de substans.ai
- **Architecture** : Conceptions système, diagrammes, spécifications techniques
- **Code Source** : Implémentations, agents, interfaces, intégrations
- **Documentation** : Modes d'emploi, guides, spécifications fonctionnelles
- **Planification** : Roadmaps, phases de développement, analyses stratégiques

#### B. PRODUCTIONS_PASSEES
Livrables et résultats des missions substans antérieures
- **Études Marché** : Analyses sectorielles, positionnement concurrentiel
- **Analyses Concurrentielles** : Benchmarks, comparatifs, études de cas
- **Rapports Techniques** : Évaluations technologiques, recommandations
- **Méthodologies** : Processus, frameworks, bonnes pratiques

#### C. SOURCES_VEILLE
Ressources externes pour la veille et recherche continue
- **Experts Métiers** : Sources spécialisées par secteur d'activité
- **Experts Domaines** : Sources transversales par domaine d'expertise
- **Sites Web** : Portails, blogs, médias spécialisés
- **APIs Données** : Sources de données structurées, flux temps réel

#### D. UGPU_GPU_CLOUD
Corpus spécialisé sur les technologies GPU et cloud computing
- **Études Techniques** : Architectures, performances, spécifications
- **Analyses Marché** : Fournisseurs, pricing, tendances
- **Benchmarks** : Tests de performance, comparatifs
- **Sources Fournisseurs** : Documentation officielle, whitepapers

## 2. Métadonnées et Indexation

### 2.1 Schéma de Métadonnées Standard

```json
{
  "id": "unique_identifier",
  "titre": "Titre du document",
  "categorie_principale": "CONSTRUCTION_SUBSTANS|PRODUCTIONS_PASSEES|SOURCES_VEILLE|UGPU_GPU_CLOUD",
  "sous_categorie": "architecture|code_source|documentation|...",
  "type_document": "rapport|code|specification|source_web|api|...",
  "date_creation": "YYYY-MM-DD",
  "date_modification": "YYYY-MM-DD",
  "auteur": "substans.ai|expert_externe|fournisseur|...",
  "secteurs_concernes": ["banque", "assurance", "retail", "..."],
  "domaines_concernes": ["ia", "cloud", "data", "cybersecurite", "..."],
  "agents_utilisateurs": ["avs", "aad", "arr", "ebf", "eia", "..."],
  "mots_cles": ["tag1", "tag2", "tag3", "..."],
  "niveau_confidentialite": "public|interne|confidentiel",
  "langue": "fr|en|...",
  "format": "md|pdf|json|py|jsx|...",
  "taille": "bytes",
  "checksum": "hash_md5",
  "relations": {
    "derives_de": ["doc_id1", "doc_id2"],
    "reference_par": ["doc_id3", "doc_id4"],
    "version_precedente": "doc_id_previous",
    "version_suivante": "doc_id_next"
  },
  "qualite": {
    "score_pertinence": 0.95,
    "score_actualite": 0.87,
    "score_fiabilite": 0.92,
    "derniere_verification": "YYYY-MM-DD"
  }
}
```

### 2.2 Indexation Sémantique

#### Vecteurs de Contenu
- **Embeddings** : Représentation vectorielle du contenu textuel
- **Similarité** : Calcul de proximité sémantique entre documents
- **Clustering** : Regroupement automatique par thématiques

#### Index Spécialisés
- **Index Secteurs** : Accès rapide par secteur d'activité
- **Index Domaines** : Accès rapide par domaine d'expertise
- **Index Agents** : Documents pertinents par agent
- **Index Temporel** : Évolution chronologique des connaissances

## 3. Système de Classification Automatique

### 3.1 Règles de Classification

#### Par Extension de Fichier
```python
CLASSIFICATION_EXTENSIONS = {
    '.md': 'documentation',
    '.py': 'code_source',
    '.jsx': 'code_source',
    '.json': 'configuration',
    '.pdf': 'rapport',
    '.png': 'diagramme',
    '.webp': 'capture_ecran'
}
```

#### Par Mots-Clés dans le Titre
```python
CLASSIFICATION_MOTS_CLES = {
    'architecture': 'construction_substans/architecture',
    'rapport': 'productions_passees/rapports_techniques',
    'analyse': 'productions_passees/analyses_concurrentielles',
    'gpu': 'ugpu_gpu_cloud/etudes_techniques',
    'cloud': 'ugpu_gpu_cloud/analyses_marche',
    'veille': 'sources_veille/experts_domaines'
}
```

#### Par Contenu Sémantique
- **Analyse NLP** : Extraction d'entités nommées, concepts clés
- **Classification ML** : Modèles entraînés sur le corpus existant
- **Validation Humaine** : Vérification et correction des classifications

### 3.2 Processus de Catégorisation

1. **Analyse Initiale**
   - Extraction des métadonnées de base
   - Identification du type de document
   - Détection de la langue

2. **Classification Automatique**
   - Application des règles par extension
   - Analyse des mots-clés dans le titre
   - Classification sémantique du contenu

3. **Enrichissement**
   - Extraction des entités (secteurs, domaines, technologies)
   - Identification des agents concernés
   - Calcul des scores de qualité

4. **Validation et Indexation**
   - Vérification de la cohérence
   - Création des liens entre documents
   - Mise à jour des index

## 4. Gestion des Relations entre Documents

### 4.1 Types de Relations

#### Relations Hiérarchiques
- **Parent/Enfant** : Document source → Document dérivé
- **Version** : Document v1 → Document v2
- **Partie/Tout** : Chapitre → Rapport complet

#### Relations Sémantiques
- **Référence** : Document A cite Document B
- **Complément** : Documents traitant du même sujet
- **Contradiction** : Documents avec des conclusions opposées

#### Relations Temporelles
- **Précédent/Suivant** : Ordre chronologique
- **Mise à jour** : Nouvelle version d'une information
- **Obsolescence** : Document remplacé par un plus récent

### 4.2 Graphe de Connaissances

```python
GRAPHE_RELATIONS = {
    "noeuds": {
        "doc_id": {
            "type": "document|concept|entite",
            "proprietes": {...}
        }
    },
    "aretes": {
        "relation_id": {
            "source": "doc_id_1",
            "cible": "doc_id_2",
            "type": "reference|derive|complement|...",
            "poids": 0.85,
            "metadonnees": {...}
        }
    }
}
```

## 5. Système de Recherche Multi-Modal

### 5.1 Types de Recherche

#### Recherche Textuelle
- **Mots-clés** : Recherche classique par termes
- **Phrases** : Recherche par expressions exactes
- **Booléenne** : Opérateurs AND, OR, NOT

#### Recherche Sémantique
- **Similarité vectorielle** : Recherche par proximité sémantique
- **Concepts** : Recherche par idées plutôt que par mots
- **Contexte** : Prise en compte du contexte de la requête

#### Recherche Facettée
- **Filtres** : Par catégorie, secteur, domaine, agent
- **Plages temporelles** : Par date de création/modification
- **Qualité** : Par scores de pertinence/fiabilité

### 5.2 Interface de Recherche

#### Pour les Agents
```python
def recherche_agent(agent_id, requete, contexte_mission=None):
    """
    Recherche optimisée pour un agent spécifique
    - Priorise les documents pertinents pour l'agent
    - Intègre le contexte de la mission en cours
    - Retourne les résultats avec scores de pertinence
    """
```

#### Pour les Utilisateurs
```python
def recherche_utilisateur(requete, filtres=None, tri="pertinence"):
    """
    Recherche générale avec interface conviviale
    - Support de requêtes en langage naturel
    - Suggestions automatiques
    - Résultats avec extraits pertinents
    """
```

## 6. Mécanismes de Mise à Jour

### 6.1 Mise à Jour Automatique

#### Surveillance des Répertoires
- **Nouveaux fichiers** : Détection et intégration automatique
- **Modifications** : Mise à jour des métadonnées et index
- **Suppressions** : Nettoyage des références orphelines

#### Veille Web
- **Flux RSS** : Surveillance des sources d'information
- **APIs** : Collecte automatique de nouvelles données
- **Scraping** : Extraction de contenu web pertinent

### 6.2 Mise à Jour Manuelle

#### Interface d'Administration
- **Ajout de documents** : Upload et classification
- **Modification de métadonnées** : Correction et enrichissement
- **Gestion des relations** : Création/suppression de liens

#### Validation Qualité
- **Vérification de contenu** : Contrôle de la pertinence
- **Mise à jour des scores** : Réévaluation de la qualité
- **Archivage** : Gestion des documents obsolètes

Cette structure de catégorisation garantit une organisation logique, une recherche efficace et une maintenance aisée de la base de connaissances substans.ai.

