import json
import os

class MethodologyManager:
    def __init__(self, config_path=
        '/home/ubuntu/substans_ai_megacabinet/methodology_system/methodology_config.json'):
        self.config_path = config_path
        self.methodology = self.load_methodology()

    def load_methodology(self):
        with open(self.config_path, 'r') as f:
            return json.load(f)

    def save_methodology(self):
        with open(self.config_path, 'w') as f:
            json.dump(self.methodology, f, indent=2)

    def get_phase(self, phase_id):
        for phase in self.methodology['phases']:
            if phase['id'] == phase_id:
                return phase
        return None

    def update_phase(self, phase_id, new_data):
        for i, phase in enumerate(self.methodology['phases']):
            if phase['id'] == phase_id:
                self.methodology['phases'][i].update(new_data)
                self.save_methodology()
                return True
        return False

    def add_phase(self, new_phase_data):
        new_phase_id = max([p['id'] for p in self.methodology['phases']]) + 1
        new_phase_data['id'] = new_phase_id
        self.methodology['phases'].append(new_phase_data)
        self.save_methodology()
        return new_phase_id

    def get_mission_workflow(self):
        workflow = []
        for phase in self.methodology['phases']:
            workflow.append({
                'phase': phase['nom'],
                'agents': phase['agents_principaux'],
                'livrables': phase['livrables']
            })
        return workflow

    def display_methodology(self):
        print(f"Méthodologie: {self.methodology['nom']} (Version {self.methodology['version']})")
        for phase in self.methodology["phases"]:
            print(f"  Phase {phase['id']}: {phase['nom']} ({phase['duree_estimee_pct']}%)")
            print(f"    Livrables: {', '.join(phase['livrables'])}")
            print(f"    Agents: {', '.join(phase['agents_principaux'])}")

    def normalize_durations(self):
        total_duration = sum(p["duree_estimee_pct"] for p in self.methodology["phases"])
        if total_duration != 100:
            factor = 100 / total_duration
            for phase in self.methodology["phases"]:
                phase["duree_estimee_pct"] = round(phase["duree_estimee_pct"] * factor)
            self.save_methodology()


