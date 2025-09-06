import os
import json
import hashlib
from datetime import datetime

class KnowledgeBase:
    def __init__(self, base_path):
        self.base_path = base_path
        self.index_path = os.path.join(base_path, 'index', 'main_index.json')
        self.documents = self.load_index()

    def load_index(self):
        if os.path.exists(self.index_path):
            with open(self.index_path, 'r') as f:
                return json.load(f)
        return {}

    def save_index(self):
        with open(self.index_path, 'w') as f:
            json.dump(self.documents, f, indent=2)

    def add_document(self, file_path, metadata):
        doc_id = self.generate_doc_id(file_path)
        if doc_id in self.documents:
            print(f"Document {file_path} already exists.")
            return

        full_metadata = self.enrich_metadata(file_path, metadata)
        self.documents[doc_id] = full_metadata
        self.save_index()
        print(f"Document {file_path} added to the knowledge base.")

    def generate_doc_id(self, file_path):
        return hashlib.md5(file_path.encode()).hexdigest()

    def enrich_metadata(self, file_path, metadata):
        stat = os.stat(file_path)
        base_metadata = {
            'id': self.generate_doc_id(file_path),
            'file_path': file_path,
            'size': stat.st_size,
            'date_creation': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'date_modification': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'checksum': self.calculate_checksum(file_path)
        }
        base_metadata.update(metadata)
        return base_metadata

    def calculate_checksum(self, file_path):
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            buf = f.read()
            hasher.update(buf)
        return hasher.hexdigest()

    def search(self, query, filters=None):
        results = []
        for doc_id, metadata in self.documents.items():
            # Simple text search in title and keywords
            if query.lower() in metadata.get('titre', '').lower() or \
               any(query.lower() in keyword.lower() for keyword in metadata.get('mots_cles', [])):
                if self.apply_filters(metadata, filters):
                    results.append(metadata)
        return results

    def apply_filters(self, metadata, filters):
        if not filters:
            return True
        for key, value in filters.items():
            if key in metadata:
                if isinstance(metadata[key], list):
                    if value not in metadata[key]:
                        return False
                elif metadata[key] != value:
                    return False
            else:
                return False
        return True

# Example Usage
if __name__ == '__main__':
    kb = KnowledgeBase('/home/ubuntu/substans_ai_megacabinet/knowledge_base')

    # Add a document
    doc_path = '/home/ubuntu/substans_ai_megacabinet/knowledge_base/inventaire_documents.md'
    metadata = {
        'titre': 'Inventaire Complet des Documents',
        'categorie_principale': 'CONSTRUCTION_SUBSTANS',
        'sous_categorie': 'documentation',
        'type_document': 'documentation',
        'auteur': 'substans.ai',
        'mots_cles': ['inventaire', 'documents', 'base de connaissances']
    }
    kb.add_document(doc_path, metadata)

    # Search for documents
    search_results = kb.search('inventaire')
    print("\nSearch Results for 'inventaire':")
    for result in search_results:
        print(f"- {result['titre']} ({result['file_path']})")


