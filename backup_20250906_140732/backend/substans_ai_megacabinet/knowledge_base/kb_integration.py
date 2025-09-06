"""
Intégration de la Base de Connaissances dans l'Architecture Substans.ai
"""

import os
import json
import sys
from datetime import datetime

# Ajout du chemin vers les modules substans.ai
sys.path.append('/home/ubuntu/substans_ai_megacabinet')

from kb_system import KnowledgeBase

class SubstansKnowledgeIntegration:
    """
    Classe d'intégration de la base de connaissances avec l'architecture substans.ai
    """
    
    def __init__(self):
        self.kb = KnowledgeBase('/home/ubuntu/substans_ai_megacabinet/knowledge_base')
        self.sources_catalog = self.load_sources_catalog()
        
    def load_sources_catalog(self):
        """Charge le catalogue des sources de veille"""
        catalog_path = '/home/ubuntu/substans_ai_megacabinet/knowledge_base/sources_veille/sources_web_catalog.json'
        with open(catalog_path, 'r') as f:
            return json.load(f)
    
    def get_sources_for_agent(self, agent_type, agent_id):
        """
        Retourne les sources de veille pertinentes pour un agent spécifique
        
        Args:
            agent_type: 'experts_metiers' ou 'experts_domaines'
            agent_id: identifiant de l'agent (ex: 'ebf', 'eia')
        """
        sources = []
        
        if agent_type in self.sources_catalog:
            for category, data in self.sources_catalog[agent_type].items():
                if 'agents_utilisateurs' in data and agent_id in data['agents_utilisateurs']:
                    sources.extend(data.get('sources_specialisees', []))
        
        # Ajout des sources transversales
        if 'sources_transversales' in self.sources_catalog:
            for category, transversal_sources in self.sources_catalog['sources_transversales'].items():
                sources.extend(transversal_sources)
                
        return sources
    
    def search_knowledge_for_mission(self, mission_context):
        """
        Recherche dans la base de connaissances pour une mission spécifique
        
        Args:
            mission_context: dict avec secteur, domaines, mots_cles
        """
        results = []
        
        # Recherche par secteur
        if 'secteur' in mission_context:
            secteur_results = self.kb.search(mission_context['secteur'])
            results.extend(secteur_results)
        
        # Recherche par domaines
        if 'domaines' in mission_context:
            for domaine in mission_context['domaines']:
                domaine_results = self.kb.search(domaine)
                results.extend(domaine_results)
        
        # Recherche par mots-clés
        if 'mots_cles' in mission_context:
            for mot_cle in mission_context['mots_cles']:
                keyword_results = self.kb.search(mot_cle)
                results.extend(keyword_results)
        
        # Déduplication et tri par pertinence
        unique_results = {doc['id']: doc for doc in results}
        return list(unique_results.values())
    
    def populate_knowledge_base(self):
        """
        Peuple la base de connaissances avec tous les documents substans existants
        """
        print("🔄 Population de la base de connaissances...")
        
        # Documents de construction substans
        construction_docs = [
            ('/home/ubuntu/rapport_final_substans.md', {
                'titre': 'Rapport Final d\'Analyse Substans.ai',
                'categorie_principale': 'CONSTRUCTION_SUBSTANS',
                'sous_categorie': 'documentation',
                'type_document': 'rapport',
                'secteurs_concernes': ['tous'],
                'domaines_concernes': ['strategie', 'ia', 'transformation_digitale'],
                'agents_utilisateurs': ['senior_advisor', 'avs', 'aad', 'arr'],
                'mots_cles': ['analyse', 'substans', 'architecture', 'agents']
            }),
            ('/home/ubuntu/architecture_matricielle_substans.md', {
                'titre': 'Architecture Matricielle Substans.ai',
                'categorie_principale': 'CONSTRUCTION_SUBSTANS',
                'sous_categorie': 'architecture',
                'type_document': 'specification',
                'secteurs_concernes': ['tous'],
                'domaines_concernes': ['ia', 'architecture_systeme'],
                'agents_utilisateurs': ['senior_advisor'],
                'mots_cles': ['architecture', 'matricielle', 'agents', 'experts']
            }),
            ('/home/ubuntu/plan_developpement_substans.md', {
                'titre': 'Plan de Développement Substans.ai Phase 1',
                'categorie_principale': 'CONSTRUCTION_SUBSTANS',
                'sous_categorie': 'planification',
                'type_document': 'plan_strategique',
                'secteurs_concernes': ['tous'],
                'domaines_concernes': ['strategie', 'gestion_projet'],
                'agents_utilisateurs': ['senior_advisor', 'asm'],
                'mots_cles': ['developpement', 'phase1', 'roadmap', 'manus']
            })
        ]
        
        for doc_path, metadata in construction_docs:
            if os.path.exists(doc_path):
                self.kb.add_document(doc_path, metadata)
                print(f"✅ Ajouté: {metadata['titre']}")
        
        # Documents de code source
        code_files = [
            '/home/ubuntu/substans_ai_megacabinet/main.py',
            '/home/ubuntu/substans_ai_megacabinet/senior_advisor/senior_advisor.py',
            '/home/ubuntu/substans_ai_megacabinet/interactions_inter_agents.py',
            '/home/ubuntu/substans_ai_megacabinet/machine_learning_global.py'
        ]
        
        for code_file in code_files:
            if os.path.exists(code_file):
                filename = os.path.basename(code_file)
                metadata = {
                    'titre': f'Code Source - {filename}',
                    'categorie_principale': 'CONSTRUCTION_SUBSTANS',
                    'sous_categorie': 'code_source',
                    'type_document': 'code',
                    'secteurs_concernes': ['tous'],
                    'domaines_concernes': ['ia', 'developpement'],
                    'agents_utilisateurs': ['senior_advisor'],
                    'mots_cles': ['python', 'substans', 'agents', 'code']
                }
                self.kb.add_document(code_file, metadata)
                print(f"✅ Ajouté: {metadata['titre']}")
        
        print(f"📊 Base de connaissances peuplée avec {len(self.kb.documents)} documents")
    
    def create_agent_knowledge_interface(self):
        """
        Crée l'interface de connaissances pour les agents
        """
        interface_code = '''
class AgentKnowledgeInterface:
    """Interface de connaissances pour les agents substans.ai"""
    
    def __init__(self, agent_id, agent_type):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.kb_integration = SubstansKnowledgeIntegration()
    
    def get_relevant_sources(self):
        """Obtient les sources de veille pertinentes pour cet agent"""
        return self.kb_integration.get_sources_for_agent(self.agent_type, self.agent_id)
    
    def search_knowledge(self, query, mission_context=None):
        """Recherche dans la base de connaissances"""
        if mission_context:
            return self.kb_integration.search_knowledge_for_mission(mission_context)
        else:
            return self.kb_integration.kb.search(query)
    
    def add_new_knowledge(self, content, metadata):
        """Ajoute de nouvelles connaissances à la base"""
        # Créer un fichier temporaire avec le contenu
        temp_file = f"/tmp/knowledge_{self.agent_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(temp_file, 'w') as f:
            f.write(content)
        
        # Enrichir les métadonnées avec l'agent source
        metadata['agent_source'] = self.agent_id
        metadata['date_ajout'] = datetime.now().isoformat()
        
        # Ajouter à la base de connaissances
        self.kb_integration.kb.add_document(temp_file, metadata)
        
        return temp_file
'''
        
        interface_path = '/home/ubuntu/substans_ai_megacabinet/knowledge_base/agent_knowledge_interface.py'
        with open(interface_path, 'w') as f:
            f.write(interface_code)
        
        print(f"✅ Interface agent créée: {interface_path}")
    
    def integrate_with_agents(self):
        """
        Intègre la base de connaissances avec les agents existants
        """
        print("🔗 Intégration avec les agents substans.ai...")
        
        # Mise à jour du Senior Advisor
        senior_advisor_path = '/home/ubuntu/substans_ai_megacabinet/senior_advisor/senior_advisor.py'
        if os.path.exists(senior_advisor_path):
            with open(senior_advisor_path, 'r') as f:
                content = f.read()
            
            # Ajout de l'import de la base de connaissances
            if 'from knowledge_base.kb_integration import SubstansKnowledgeIntegration' not in content:
                import_line = "from knowledge_base.kb_integration import SubstansKnowledgeIntegration\\n"
                content = import_line + content
                
                # Ajout de l'initialisation dans la classe
                if 'self.knowledge_base = SubstansKnowledgeIntegration()' not in content:
                    content = content.replace(
                        'def __init__(self):',
                        'def __init__(self):\\n        self.knowledge_base = SubstansKnowledgeIntegration()'
                    )
                
                with open(senior_advisor_path, 'w') as f:
                    f.write(content)
                
                print("✅ Senior Advisor mis à jour avec accès à la base de connaissances")
        
        print("🎯 Intégration terminée avec succès!")

def main():
    """Fonction principale d'intégration"""
    print("🚀 Démarrage de l'intégration de la base de connaissances")
    
    integration = SubstansKnowledgeIntegration()
    
    # Population de la base
    integration.populate_knowledge_base()
    
    # Création de l'interface agent
    integration.create_agent_knowledge_interface()
    
    # Intégration avec les agents
    integration.integrate_with_agents()
    
    print("✅ Intégration de la base de connaissances terminée!")
    
    # Test de recherche
    print("\\n🔍 Test de recherche:")
    results = integration.kb.search('substans')
    print(f"Trouvé {len(results)} documents contenant 'substans'")
    for result in results[:3]:
        print(f"- {result['titre']}")

if __name__ == '__main__':
    main()

