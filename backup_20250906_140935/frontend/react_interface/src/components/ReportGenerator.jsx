import React, { useState } from 'react';

const ReportGenerator = () => {
  const [reportType, setReportType] = useState('market_analysis');
  const [outputFormat, setOutputFormat] = useState('pdf');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedReport, setGeneratedReport] = useState(null);
  const [reportData, setReportData] = useState('');

  const reportTemplates = {
    market_analysis: {
      name: "Analyse de Marché",
      formats: ["pdf", "docx"],
      placeholder: `{
  "topic": "IA Générative",
  "summary": "Le marché de l'IA générative est en pleine expansion.",
  "trends": ["Adoption par les entreprises", "Modèles multimodaux"],
  "competitors": [{"name": "OpenAI", "market_share": 45}, {"name": "Google", "market_share": 30}]
}`
    },
    competitive_intelligence: {
      name: "Veille Concurrentielle",
      formats: ["pdf", "docx", "xlsx"],
      placeholder: `{
  "competitor": "OpenAI",
  "profile": {"name": "OpenAI", "sector": "IA", "revenue": "$2B"}
}`
    },
    financial_report: {
      name: "Rapport Financier",
      formats: ["pdf", "xlsx"],
      placeholder: `{
  "company": "TechCorp",
  "financial_summary": {
    "revenue": "$5B",
    "net_profit": "$1.2B",
    "gross_margin": 65
  }
}`
    }
  };

  const generateReport = async () => {
    setIsGenerating(true);
    // Simulate API call to generate report
    await new Promise(resolve => setTimeout(resolve, 2000));

    try {
      const data = JSON.parse(reportData);
      const reportPath = `/home/ubuntu/substans_ai_megacabinet/reports/report_${reportType}_${Date.now()}.${outputFormat}`;
      setGeneratedReport({
        path: reportPath,
        type: reportType,
        format: outputFormat
      });
    } catch (error) {
      alert("Données JSON invalides");
    }

    setIsGenerating(false);
  };

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-blue-600 to-green-500 text-white rounded-lg p-6">
        <h2 className="text-2xl font-bold">📄 Générateur de Rapports</h2>
        <p className="text-blue-100 mt-1">Créez des rapports commerciaux professionnels en quelques clics</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Configuration */}
        <div className="bg-white rounded-lg border p-6">
          <h3 className="text-lg font-semibold mb-4">⚙️ Configuration du Rapport</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Type de Rapport</label>
              <select 
                value={reportType}
                onChange={(e) => setReportType(e.target.value)}
                className="w-full border rounded-lg px-3 py-2"
              >
                {Object.entries(reportTemplates).map(([key, template]) => (
                  <option key={key} value={key}>{template.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Format de Sortie</label>
              <div className="flex space-x-2">
                {reportTemplates[reportType].formats.map(format => (
                  <button 
                    key={format}
                    onClick={() => setOutputFormat(format)}
                    className={`px-4 py-2 rounded-lg border ${outputFormat === format ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}>
                    {format.toUpperCase()}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Données (JSON)</label>
              <textarea 
                value={reportData}
                onChange={(e) => setReportData(e.target.value)}
                placeholder={reportTemplates[reportType].placeholder}
                className="w-full h-48 border rounded-lg p-2 font-mono text-sm"
              />
            </div>

            <button
              onClick={generateReport}
              disabled={isGenerating}
              className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {isGenerating ? 'Génération en cours...' : 'Générer le Rapport'}
            </button>
          </div>
        </div>

        {/* Résultat */}
        <div className="bg-white rounded-lg border p-6">
          <h3 className="text-lg font-semibold mb-4">✅ Résultat</h3>
          {generatedReport ? (
            <div>
              <p>Rapport généré avec succès !</p>
              <p className="font-mono bg-gray-100 p-2 rounded mt-2">{generatedReport.path}</p>
              <button className="mt-4 px-4 py-2 bg-green-500 text-white rounded-lg">Télécharger</button>
            </div>
          ) : (
            <div className="text-center text-gray-500 py-8">
              <p>Le rapport généré apparaîtra ici.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ReportGenerator;

