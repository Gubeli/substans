"""
Gestionnaire de fichiers pour les missions substans.ai
Intègre le traitement de fichiers dans le workflow des missions
"""

import os
import json
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional
from file_processor import FileProcessor

class MissionFileHandler:
    """
    Gestionnaire de fichiers pour les missions
    Traite les fichiers joints et les intègre dans le workflow
    """
    
    def __init__(self, missions_path="/home/ubuntu/substans_ai_megacabinet/missions"):
        self.missions_path = missions_path
        self.file_processor = FileProcessor()
        
        # Créer le répertoire des missions
        os.makedirs(self.missions_path, exist_ok=True)
        
    def create_mission_directory(self, mission_id: str) -> str:
        """Crée un répertoire pour une mission"""
        mission_dir = os.path.join(self.missions_path, f"mission_{mission_id}")
        os.makedirs(mission_dir, exist_ok=True)
        
        # Créer les sous-répertoires
        os.makedirs(os.path.join(mission_dir, "documents"), exist_ok=True)
        os.makedirs(os.path.join(mission_dir, "analyses"), exist_ok=True)
        os.makedirs(os.path.join(mission_dir, "livrables"), exist_ok=True)
        
        return mission_dir
    
    def save_uploaded_files(self, mission_id: str, files: List[Any]) -> List[Dict[str, Any]]:
        """Sauvegarde les fichiers uploadés pour une mission"""
        
        mission_dir = self.create_mission_directory(mission_id)
        documents_dir = os.path.join(mission_dir, "documents")
        
        saved_files = []
        
        for file in files:
            # Générer un nom de fichier sécurisé
            safe_filename = self.generate_safe_filename(file.name)
            file_path = os.path.join(documents_dir, safe_filename)
            
            try:
                # Sauvegarder le fichier (simulation - en réalité il faudrait file.save())
                # file.save(file_path)
                
                # Pour la simulation, créer un fichier vide
                with open(file_path, 'w') as f:
                    f.write(f"Simulation du fichier: {file.name}")
                
                file_info = {
                    'original_name': file.name,
                    'safe_filename': safe_filename,
                    'file_path': file_path,
                    'file_size': getattr(file, 'size', 0),
                    'upload_time': datetime.now().isoformat(),
                    'mission_id': mission_id
                }
                
                saved_files.append(file_info)
                
            except Exception as e:
                print(f"Erreur sauvegarde fichier {file.name}: {str(e)}")
        
        return saved_files
    
    def process_mission_files(self, mission_id: str, files_info: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Traite tous les fichiers d'une mission"""
        
        processing_results = {
            'mission_id': mission_id,
            'processed_files': [],
            'analysis_summary': {},
            'knowledge_base_entries': [],
            'errors': []
        }
        
        for file_info in files_info:
            try:
                # Traiter le fichier
                result = self.file_processor.process_file(
                    file_info['file_path'], 
                    mission_id=mission_id
                )
                
                if 'error' not in result:
                    processing_results['processed_files'].append(result)
                    
                    # Ajouter à la base de connaissances
                    processing_results['knowledge_base_entries'].append({
                        'file_name': result['file_name'],
                        'file_type': result['file_type'],
                        'content_summary': self.file_processor.generate_content_summary(result)
                    })
                else:
                    processing_results['errors'].append({
                        'file_name': file_info['original_name'],
                        'error': result['error']
                    })
                    
            except Exception as e:
                processing_results['errors'].append({
                    'file_name': file_info['original_name'],
                    'error': str(e)
                })
        
        # Générer un résumé d'analyse
        processing_results['analysis_summary'] = self.generate_analysis_summary(
            processing_results['processed_files']
        )
        
        # Sauvegarder les résultats
        self.save_processing_results(mission_id, processing_results)
        
        return processing_results
    
    def generate_analysis_summary(self, processed_files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Génère un résumé d'analyse des fichiers traités"""
        
        summary = {
            'total_files': len(processed_files),
            'file_types': {},
            'total_content_size': 0,
            'key_insights': [],
            'recommended_actions': []
        }
        
        for file_data in processed_files:
            # Compter les types de fichiers
            file_type = file_data.get('file_type', 'unknown')
            summary['file_types'][file_type] = summary['file_types'].get(file_type, 0) + 1
            
            # Calculer la taille totale du contenu
            word_count = file_data.get('word_count', 0)
            summary['total_content_size'] += word_count
        
        # Générer des insights basés sur les types de fichiers
        if 'pdf' in summary['file_types']:
            summary['key_insights'].append("Documents PDF détectés - Analyse de contenu structuré disponible")
            
        if 'excel' in summary['file_types']:
            summary['key_insights'].append("Données Excel détectées - Analyse quantitative possible")
            summary['recommended_actions'].append("Activer l'Agent d'Analyse de Données (AAD)")
            
        if 'powerpoint' in summary['file_types']:
            summary['key_insights'].append("Présentations détectées - Contexte stratégique disponible")
            
        if summary['total_content_size'] > 10000:
            summary['recommended_actions'].append("Volume important de contenu - Activer l'Agent de Gestion des Connaissances (AGC)")
        
        return summary
    
    def save_processing_results(self, mission_id: str, results: Dict[str, Any]):
        """Sauvegarde les résultats de traitement"""
        
        mission_dir = os.path.join(self.missions_path, f"mission_{mission_id}")
        results_file = os.path.join(mission_dir, "file_processing_results.json")
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
    
    def get_mission_files_summary(self, mission_id: str) -> Dict[str, Any]:
        """Récupère le résumé des fichiers d'une mission"""
        
        results_file = os.path.join(
            self.missions_path, 
            f"mission_{mission_id}", 
            "file_processing_results.json"
        )
        
        if os.path.exists(results_file):
            with open(results_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {}
    
    def generate_safe_filename(self, filename: str) -> str:
        """Génère un nom de fichier sécurisé"""
        
        # Remplacer les caractères dangereux
        safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_"
        safe_filename = ''.join(c if c in safe_chars else '_' for c in filename)
        
        # Ajouter un timestamp pour éviter les conflits
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name, ext = os.path.splitext(safe_filename)
        
        return f"{timestamp}_{name}{ext}"
    
    def create_mission_brief_with_files(self, mission_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crée un brief de mission enrichi avec l'analyse des fichiers"""
        
        enhanced_brief = {
            'mission_id': mission_data.get('id'),
            'original_brief': mission_data.get('brief', ''),
            'files_analysis': {},
            'enhanced_context': '',
            'recommended_approach': []
        }
        
        # Si des fichiers sont présents
        if 'fichiers' in mission_data and mission_data['fichiers']:
            
            # Simuler le traitement des fichiers
            files_info = self.save_uploaded_files(
                mission_data['id'], 
                mission_data['fichiers']
            )
            
            # Traiter les fichiers
            processing_results = self.process_mission_files(
                mission_data['id'], 
                files_info
            )
            
            enhanced_brief['files_analysis'] = processing_results['analysis_summary']
            
            # Enrichir le contexte
            if processing_results['processed_files']:
                enhanced_brief['enhanced_context'] = self.generate_enhanced_context(
                    mission_data['brief'],
                    processing_results
                )
                
                # Recommandations d'approche
                enhanced_brief['recommended_approach'] = self.generate_approach_recommendations(
                    mission_data,
                    processing_results
                )
        
        return enhanced_brief
    
    def generate_enhanced_context(self, original_brief: str, processing_results: Dict[str, Any]) -> str:
        """Génère un contexte enrichi basé sur l'analyse des fichiers"""
        
        enhanced_context = f"Brief original: {original_brief}\n\n"
        enhanced_context += "Contexte enrichi par l'analyse des documents joints:\n"
        
        # Ajouter les insights des fichiers
        for insight in processing_results['analysis_summary']['key_insights']:
            enhanced_context += f"• {insight}\n"
        
        # Ajouter un résumé du contenu
        if processing_results['processed_files']:
            enhanced_context += f"\nDocuments analysés: {len(processing_results['processed_files'])} fichiers\n"
            enhanced_context += f"Volume de contenu: {processing_results['analysis_summary']['total_content_size']} mots\n"
        
        return enhanced_context
    
    def generate_approach_recommendations(self, mission_data: Dict[str, Any], processing_results: Dict[str, Any]) -> List[str]:
        """Génère des recommandations d'approche basées sur les fichiers"""
        
        recommendations = []
        
        # Recommandations basées sur le secteur
        secteur = mission_data.get('secteur', '')
        if secteur == 'Digital, Data, IA':
            recommendations.append("Activer l'Expert Digital, Data, IA (EDDI) en priorité")
        
        # Recommandations basées sur les types de fichiers
        file_types = processing_results['analysis_summary']['file_types']
        
        if 'excel' in file_types:
            recommendations.append("Prioriser l'analyse quantitative avec l'Agent d'Analyse de Données")
            
        if 'pdf' in file_types:
            recommendations.append("Extraire les insights stratégiques des documents PDF")
            
        if 'powerpoint' in file_types:
            recommendations.append("Analyser le contexte stratégique des présentations")
        
        # Recommandations générales
        recommendations.extend(processing_results['analysis_summary']['recommended_actions'])
        
        return recommendations

# Test du gestionnaire
if __name__ == '__main__':
    handler = MissionFileHandler()
    
    print("=== Gestionnaire de Fichiers Missions ===")
    print(f"Répertoire missions: {handler.missions_path}")
    
    # Test de création de mission
    test_mission = {
        'id': 'test_001',
        'nom': 'Test Mission avec Fichiers',
        'secteur': 'Digital, Data, IA',
        'brief': 'Mission de test pour valider le traitement de fichiers',
        'fichiers': []  # Simulation de fichiers
    }
    
    enhanced_brief = handler.create_mission_brief_with_files(test_mission)
    print(f"Brief enrichi créé pour mission: {enhanced_brief['mission_id']}")
    print(f"Contexte enrichi: {len(enhanced_brief['enhanced_context'])} caractères")

