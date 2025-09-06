import json
import os
from methodology_manager import MethodologyManager

class ContinuousImprovementSystem:
    def __init__(self):
        self.methodology_manager = MethodologyManager()
        self.feedback_data_path = "/home/ubuntu/substans_ai_megacabinet/methodology_system/feedback_data.json"
        self.feedback_data = self.load_feedback_data()

    def load_feedback_data(self):
        if os.path.exists(self.feedback_data_path):
            with open(self.feedback_data_path, 'r') as f:
                return json.load(f)
        return []

    def save_feedback_data(self):
        with open(self.feedback_data_path, 'w') as f:
            json.dump(self.feedback_data, f, indent=2)

    def collect_feedback(self, mission_id, phase_id, feedback):
        """Collecte le feedback sur une phase de mission"""
        feedback_entry = {
            "mission_id": mission_id,
            "phase_id": phase_id,
            "feedback": feedback, # ex: {"duree_reelle_pct": 12, "qualite_livrables": 4.5, "efficacite_agents": 4.2}
            "timestamp": self.get_current_timestamp()
        }
        self.feedback_data.append(feedback_entry)
        self.save_feedback_data()
        print(f"[CIS] Feedback collecté pour la mission {mission_id}, phase {phase_id}")

    def analyze_feedback(self):
        """Analyse le feedback collecté pour identifier des améliorations"""
        if not self.feedback_data:
            print("[CIS] Aucune donnée de feedback à analyser.")
            return None

        # Analyse simple : moyenne des durées réelles par phase
        phase_durations = {}
        for feedback in self.feedback_data:
            phase_id = feedback["phase_id"]
            duree_reelle = feedback["feedback"].get("duree_reelle_pct")
            if duree_reelle is not None:
                if phase_id not in phase_durations:
                    phase_durations[phase_id] = []
                phase_durations[phase_id].append(duree_reelle)

        improvements = []
        for phase_id, durations in phase_durations.items():
            avg_duration = sum(durations) / len(durations)
            current_phase = self.methodology_manager.get_phase(phase_id)
            if current_phase:
                current_duration = current_phase["duree_estimee_pct"]
                if abs(avg_duration - current_duration) > 2: # Seuil de 2%
                    improvement = {
                        "type": "ajustement_duree",
                        "phase_id": phase_id,
                        "ancienne_duree": current_duration,
                        "nouvelle_duree_suggeree": round(avg_duration, 1)
                    }
                    improvements.append(improvement)
        
        print(f"[CIS] Analyse terminée. {len(improvements)} améliorations suggérées.")
        return improvements

    def apply_improvements(self, improvements):
        """Applique automatiquement les améliorations suggérées"""
        if not improvements:
            print("[CIS] Aucune amélioration à appliquer.")
            return

        for improvement in improvements:
            if improvement["type"] == "ajustement_duree":
                phase_id = improvement["phase_id"]
                new_duration = improvement["nouvelle_duree_suggeree"]
                
                # Mise à jour de la durée de la phase
                phase = self.methodology_manager.get_phase(phase_id)
                if phase:
                    phase["duree_estimee_pct"] = new_duration
                    self.methodology_manager.update_phase(phase_id, phase)
                    print(f"[CIS] Amélioration appliquée: Durée de la phase {phase_id} ajustée à {new_duration}%")

        # Normaliser les durées pour que le total soit 100%
        self.methodology_manager.normalize_durations()
        print("[CIS] Durées des phases normalisées.")

    def run_improvement_cycle(self):
        """Exécute un cycle complet d'amélioration continue"""
        print("\n--- Démarrage du Cycle d'Amélioration Continue ---")
        improvements = self.analyze_feedback()
        if improvements:
            self.apply_improvements(improvements)
        print("--- Fin du Cycle d'Amélioration Continue ---")

    def get_current_timestamp(self):
        from datetime import datetime
        return datetime.now().isoformat()

# Test du système d'amélioration continue
if __name__ == '__main__':
    cis = ContinuousImprovementSystem()

    # Simulation de collecte de feedback
    cis.collect_feedback("mission_001", 1, {"duree_reelle_pct": 12, "qualite_livrables": 4.8, "efficacite_agents": 4.5})
    cis.collect_feedback("mission_002", 1, {"duree_reelle_pct": 13, "qualite_livrables": 4.2, "efficacite_agents": 4.0})
    cis.collect_feedback("mission_001", 2, {"duree_reelle_pct": 28, "qualite_livrables": 4.5, "efficacite_agents": 4.3})
    cis.collect_feedback("mission_002", 2, {"duree_reelle_pct": 26, "qualite_livrables": 4.6, "efficacite_agents": 4.4})

    # Exécution du cycle d'amélioration
    cis.run_improvement_cycle()

    # Affichage de la méthodologie mise à jour
    print("\n=== Méthodologie Mise à Jour ===")
    cis.methodology_manager.display_methodology()


