# Base de Connaissances Substans.ai - Mode d'Emploi

## 1. Introduction

Ce document décrit le fonctionnement et l'utilisation de la base de connaissances (Knowledge Base - KB) de Substans.ai. La KB est le cerveau collectif de l'organisation, centralisant toutes les informations, documents, et sources de recherche.

## 2. Architecture de la Base de Connaissances

La KB est structurée en 4 catégories principales :

- **CONSTRUCTION_SUBSTANS** : Documents liés au développement de substans.ai
- **PRODUCTIONS_PASSEES** : Livrables des missions antérieures
- **SOURCES_VEILLE** : Ressources externes pour la veille
- **UGPU_GPU_CLOUD** : Corpus spécialisé sur les technologies GPU et cloud

Chaque document est enrichi de métadonnées détaillées pour faciliter la recherche et la classification.

## 3. Accès à la Base de Connaissances

### 3.1. Accès pour les Agents

Les agents accèdent à la KB via l'interface `AgentKnowledgeInterface` qui leur fournit des méthodes pour :

- **`get_relevant_sources()`** : Obtenir les sources de veille pertinentes pour leur profil.
- **`search_knowledge(query, mission_context)`** : Rechercher dans la KB.
- **`add_new_knowledge(content, metadata)`** : Ajouter de nouvelles connaissances.

### 3.2. Accès pour les Utilisateurs

L'interface "Chef de Substans.ai" intégrera un onglet "Base de Connaissances" pour permettre la recherche et la consultation directe de la KB.

## 4. Processus de Mise à Jour

La KB est mise à jour en continu :

- **Automatiquement** : Les nouvelles productions des agents sont automatiquement ajoutées.
- **Manuellement** : Vous pouvez ajouter des documents via l'interface d'administration.

## 5. Bonnes Pratiques

- **Enrichir les métadonnées** : Des métadonnées précises améliorent la pertinence des recherches.
- **Valider les sources** : S'assurer de la fiabilité des sources externes ajoutées.
- **Partager les connaissances** : Utiliser la KB comme outil principal de partage d'informations.

Pour toute question, veuillez contacter le Senior Advisor.

