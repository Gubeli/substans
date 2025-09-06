
class InteractionsInterAgents:
    def __init__(self, senior_advisor):
        self.senior_advisor = senior_advisor

    def avs_to_aad(self, data):
        print("Interaction AVS -> AAD: Transmission des données collectées pour analyse")
        self.senior_advisor.agents_consultants["aad"].analyze_data(data)

    def aad_to_arr(self, analysis):
        print("Interaction AAD -> ARR: Transmission de l'analyse pour rédaction du rapport")
        self.senior_advisor.agents_consultants["arr"].write_report(analysis)

    def experts_to_avs(self, mission_brief):
        print("Interaction Experts -> AVS: Enrichissement du brief de collecte de données")
        # Les experts fournissent des mots-clés, des sources, etc.
        pass

    def experts_to_aad(self, data):
        print("Interaction Experts -> AAD: Contextualisation des données pour l'analyse")
        # Les experts fournissent des insights pour interpréter les données
        pass


