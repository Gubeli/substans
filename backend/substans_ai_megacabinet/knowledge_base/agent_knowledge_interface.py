
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
