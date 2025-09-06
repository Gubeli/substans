import React, { useState, useEffect } from 'react';

const IntelligenceTab = () => {
  const [activeView, setActiveView] = useState('dashboard');
  const [intelligenceData, setIntelligenceData] = useState(null);
  const [selectedContent, setSelectedContent] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);

  // Simulation des données d'intelligence
  useEffect(() => {
    const mockData = {
      dashboard: {
        alerts: [
          {
            priority: "Haute",
            title: "JUPITER atteint 1 exaflop - Premier supercalculateur exascale européen",
            summary: "Impact estimé : 95%",
            action_required: true,
            timestamp: new Date().toISOString(),
            expert: "Expert Semi-conducteurs"
          },
          {
            priority: "Haute", 
            title: "Nvidia annonce la nouvelle architecture Blackwell pour l'IA",
            summary: "Impact estimé : 90%",
            action_required: true,
            timestamp: new Date().toISOString(),
            expert: "Expert Digital Data IA"
          },
          {
            priority: "Moyenne",
            title: "La BCE lance l'euro numérique en phase pilote",
            summary: "Impact estimé : 85%",
            action_required: false,
            timestamp: new Date().toISOString(),
            expert: "Expert Banque Finance"
          }
        ],
        trends: [
          {
            trend: "IA Générative en Entreprise",
            growth_rate: "+45%",
            confidence: 0.92,
            time_horizon: "6-12 mois",
            impact_sectors: ["Finance", "Retail", "Manufacturing"]
          },
          {
            trend: "Edge Computing",
            growth_rate: "+35%",
            confidence: 0.87,
            time_horizon: "12-18 mois", 
            impact_sectors: ["IoT", "Automobile", "Télécoms"]
          }
        ],
        metrics: {
          total_discoveries: 75,
          high_impact: 12,
          experts_active: 24,
          intelligence_score: 0.84
        }
      },
      content_library: [
        {
          type: "linkedin_post",
          title: "Post LinkedIn - Innovation JUPITER",
          content: "🚀 JUPITER atteint 1 exaflop - Premier supercalculateur exascale européen\n\nNotre expert Semi-conducteurs a identifié une évolution majeure...",
          status: "Prêt",
          estimated_reach: "500-2000 vues",
          generated_at: new Date().toISOString()
        },
        {
          type: "executive_briefing",
          title: "Briefing Exécutif - Évolutions HPC",
          content: "# BRIEFING EXÉCUTIF - 02/09/2025\n## Évolutions Stratégiques - HPC...",
          status: "Prêt",
          target_audience: "C-Level",
          generated_at: new Date().toISOString()
        },
        {
          type: "market_report",
          title: "Rapport de Marché - Semi-conducteurs Q3",
          content: "# RAPPORT DE MARCHÉ - Semi-conducteurs\n## Période : Q3 2025...",
          status: "Prêt",
          pricing_tier: "Premium",
          estimated_value: "3500€",
          generated_at: new Date().toISOString()
        }
      ]
    };
    setIntelligenceData(mockData);
  }, []);

  const generateContent = async (type) => {
    setIsGenerating(true);
    
    // Simulation de génération
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    const newContent = {
      type: type,
      title: `Nouveau ${type} - ${new Date().toLocaleDateString()}`,
      content: `Contenu généré automatiquement pour ${type}...`,
      status: "Prêt",
      generated_at: new Date().toISOString()
    };
    
    setIntelligenceData(prev => ({
      ...prev,
      content_library: [newContent, ...prev.content_library]
    }));
    
    setIsGenerating(false);
  };

  const downloadContent = (content, format) => {
    // Simulation de téléchargement
    const blob = new Blob([content.content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${content.title}.${format}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (!intelligenceData) {
    return <div className="p-6">Chargement des données d'intelligence...</div>;
  }

  return (
    <div className="p-6 space-y-6">
      {/* Navigation secondaire */}
      <div className="flex space-x-4 border-b">
        <button
          onClick={() => setActiveView('dashboard')}
          className={`pb-2 px-1 ${activeView === 'dashboard' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-500'}`}
        >
          Dashboard Intelligence
        </button>
        <button
          onClick={() => setActiveView('content')}
          className={`pb-2 px-1 ${activeView === 'content' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-500'}`}
        >
          Bibliothèque de Contenu
        </button>
        <button
          onClick={() => setActiveView('generator')}
          className={`pb-2 px-1 ${activeView === 'generator' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-500'}`}
        >
          Générateur de Contenu
        </button>
      </div>

      {/* Dashboard Intelligence */}
      {activeView === 'dashboard' && (
        <div className="space-y-6">
          {/* Métriques globales */}
          <div className="grid grid-cols-4 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{intelligenceData.dashboard.metrics.total_discoveries}</div>
              <div className="text-sm text-gray-600">Découvertes Totales</div>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-green-600">{intelligenceData.dashboard.metrics.high_impact}</div>
              <div className="text-sm text-gray-600">Fort Impact</div>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">{intelligenceData.dashboard.metrics.experts_active}</div>
              <div className="text-sm text-gray-600">Experts Actifs</div>
            </div>
            <div className="bg-orange-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-orange-600">{(intelligenceData.dashboard.metrics.intelligence_score * 100).toFixed(0)}%</div>
              <div className="text-sm text-gray-600">Score Intelligence</div>
            </div>
          </div>

          {/* Alertes prioritaires */}
          <div className="bg-white rounded-lg border p-6">
            <h3 className="text-lg font-semibold mb-4">🚨 Alertes Prioritaires</h3>
            <div className="space-y-3">
              {intelligenceData.dashboard.alerts.map((alert, index) => (
                <div key={index} className={`p-4 rounded-lg border-l-4 ${
                  alert.priority === 'Haute' ? 'border-red-500 bg-red-50' : 'border-yellow-500 bg-yellow-50'
                }`}>
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          alert.priority === 'Haute' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {alert.priority}
                        </span>
                        {alert.action_required && (
                          <span className="px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800">
                            Action Requise
                          </span>
                        )}
                      </div>
                      <h4 className="font-medium mt-2">{alert.title}</h4>
                      <p className="text-sm text-gray-600 mt-1">{alert.summary}</p>
                      <p className="text-xs text-gray-500 mt-1">Source: {alert.expert}</p>
                    </div>
                    <button className="text-blue-600 hover:text-blue-800 text-sm">
                      Voir détails →
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Tendances émergentes */}
          <div className="bg-white rounded-lg border p-6">
            <h3 className="text-lg font-semibold mb-4">📈 Tendances Émergentes</h3>
            <div className="space-y-4">
              {intelligenceData.dashboard.trends.map((trend, index) => (
                <div key={index} className="p-4 bg-gray-50 rounded-lg">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h4 className="font-medium">{trend.trend}</h4>
                      <div className="flex items-center space-x-4 mt-2 text-sm text-gray-600">
                        <span>Croissance: <span className="font-medium text-green-600">{trend.growth_rate}</span></span>
                        <span>Confiance: <span className="font-medium">{(trend.confidence * 100).toFixed(0)}%</span></span>
                        <span>Horizon: <span className="font-medium">{trend.time_horizon}</span></span>
                      </div>
                      <div className="mt-2">
                        <span className="text-sm text-gray-600">Secteurs impactés: </span>
                        {trend.impact_sectors.map((sector, i) => (
                          <span key={i} className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded mr-1">
                            {sector}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Bibliothèque de contenu */}
      {activeView === 'content' && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold">📚 Bibliothèque de Contenu</h3>
            <div className="flex space-x-2">
              <select className="border rounded px-3 py-1 text-sm">
                <option>Tous les types</option>
                <option>Posts LinkedIn</option>
                <option>Briefings Exécutifs</option>
                <option>Rapports de Marché</option>
                <option>Stories Sociales</option>
                <option>Newsletters</option>
              </select>
              <select className="border rounded px-3 py-1 text-sm">
                <option>Tous les statuts</option>
                <option>Prêt</option>
                <option>Brouillon</option>
                <option>Publié</option>
              </select>
            </div>
          </div>

          <div className="grid gap-4">
            {intelligenceData.content_library.map((content, index) => (
              <div key={index} className="bg-white border rounded-lg p-6">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        content.type === 'linkedin_post' ? 'bg-blue-100 text-blue-800' :
                        content.type === 'executive_briefing' ? 'bg-purple-100 text-purple-800' :
                        content.type === 'market_report' ? 'bg-green-100 text-green-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {content.type.replace('_', ' ').toUpperCase()}
                      </span>
                      <span className="px-2 py-1 rounded text-xs font-medium bg-green-100 text-green-800">
                        {content.status}
                      </span>
                    </div>
                    <h4 className="font-medium">{content.title}</h4>
                    <p className="text-sm text-gray-600 mt-2 line-clamp-2">{content.content}</p>
                    <div className="flex items-center space-x-4 mt-3 text-xs text-gray-500">
                      <span>Généré le {new Date(content.generated_at).toLocaleDateString()}</span>
                      {content.estimated_reach && <span>Portée: {content.estimated_reach}</span>}
                      {content.estimated_value && <span>Valeur: {content.estimated_value}</span>}
                    </div>
                  </div>
                  <div className="flex space-x-2 ml-4">
                    <button 
                      onClick={() => setSelectedContent(content)}
                      className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
                    >
                      👁️ Voir
                    </button>
                    <div className="relative group">
                      <button className="px-3 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700">
                        ⬇️ Télécharger
                      </button>
                      <div className="absolute right-0 mt-1 w-32 bg-white border rounded shadow-lg opacity-0 group-hover:opacity-100 transition-opacity z-10">
                        <button 
                          onClick={() => downloadContent(content, 'md')}
                          className="block w-full text-left px-3 py-2 text-sm hover:bg-gray-100"
                        >
                          📄 Markdown
                        </button>
                        <button 
                          onClick={() => downloadContent(content, 'pdf')}
                          className="block w-full text-left px-3 py-2 text-sm hover:bg-gray-100"
                        >
                          📕 PDF
                        </button>
                        <button 
                          onClick={() => downloadContent(content, 'docx')}
                          className="block w-full text-left px-3 py-2 text-sm hover:bg-gray-100"
                        >
                          📘 Word
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Générateur de contenu */}
      {activeView === 'generator' && (
        <div className="space-y-6">
          <h3 className="text-lg font-semibold">🎯 Générateur de Contenu</h3>
          
          <div className="grid grid-cols-2 gap-6">
            {/* Usage Personnel */}
            <div className="bg-white border rounded-lg p-6">
              <h4 className="font-medium mb-4">👤 Usage Personnel</h4>
              <div className="space-y-3">
                <button 
                  onClick={() => generateContent('dashboard_alert')}
                  disabled={isGenerating}
                  className="w-full p-3 text-left border rounded hover:bg-gray-50 disabled:opacity-50"
                >
                  <div className="font-medium">🚨 Alertes Prioritaires</div>
                  <div className="text-sm text-gray-600">Notifications ciblées selon vos missions</div>
                </button>
                <button 
                  onClick={() => generateContent('trend_analysis')}
                  disabled={isGenerating}
                  className="w-full p-3 text-left border rounded hover:bg-gray-50 disabled:opacity-50"
                >
                  <div className="font-medium">📈 Analyse de Tendances</div>
                  <div className="text-sm text-gray-600">Graphiques d'évolution par domaine</div>
                </button>
                <button 
                  onClick={() => generateContent('search_report')}
                  disabled={isGenerating}
                  className="w-full p-3 text-left border rounded hover:bg-gray-50 disabled:opacity-50"
                >
                  <div className="font-medium">🔍 Rapport de Recherche</div>
                  <div className="text-sm text-gray-600">Interrogation intelligente de la veille</div>
                </button>
              </div>
            </div>

            {/* Promotion */}
            <div className="bg-white border rounded-lg p-6">
              <h4 className="font-medium mb-4">📱 Fins Promotionnelles</h4>
              <div className="space-y-3">
                <button 
                  onClick={() => generateContent('linkedin_post')}
                  disabled={isGenerating}
                  className="w-full p-3 text-left border rounded hover:bg-gray-50 disabled:opacity-50"
                >
                  <div className="font-medium">💼 Post LinkedIn</div>
                  <div className="text-sm text-gray-600">Posts prêts à publier avec hashtags</div>
                </button>
                <button 
                  onClick={() => generateContent('social_story')}
                  disabled={isGenerating}
                  className="w-full p-3 text-left border rounded hover:bg-gray-50 disabled:opacity-50"
                >
                  <div className="font-medium">📱 Stories Visuelles</div>
                  <div className="text-sm text-gray-600">Infographies pour réseaux sociaux</div>
                </button>
                <button 
                  onClick={() => generateContent('newsletter')}
                  disabled={isGenerating}
                  className="w-full p-3 text-left border rounded hover:bg-gray-50 disabled:opacity-50"
                >
                  <div className="font-medium">📧 Newsletter</div>
                  <div className="text-sm text-gray-600">Synthèse hebdomadaire expertise</div>
                </button>
              </div>
            </div>

            {/* Produits Commerciaux */}
            <div className="bg-white border rounded-lg p-6 col-span-2">
              <h4 className="font-medium mb-4">💰 Produits Commerciaux</h4>
              <div className="grid grid-cols-3 gap-3">
                <button 
                  onClick={() => generateContent('market_report')}
                  disabled={isGenerating}
                  className="p-3 text-left border rounded hover:bg-gray-50 disabled:opacity-50"
                >
                  <div className="font-medium">📊 Rapport Sectoriel</div>
                  <div className="text-sm text-gray-600">Études de marché premium</div>
                  <div className="text-xs text-green-600 mt-1">2500-5000€</div>
                </button>
                <button 
                  onClick={() => generateContent('executive_briefing')}
                  disabled={isGenerating}
                  className="p-3 text-left border rounded hover:bg-gray-50 disabled:opacity-50"
                >
                  <div className="font-medium">💼 Briefing Exécutif</div>
                  <div className="text-sm text-gray-600">Synthèses C-Level</div>
                  <div className="text-xs text-green-600 mt-1">1000-2000€</div>
                </button>
                <button 
                  onClick={() => generateContent('predictive_analysis')}
                  disabled={isGenerating}
                  className="p-3 text-left border rounded hover:bg-gray-50 disabled:opacity-50"
                >
                  <div className="font-medium">🔮 Analyse Prédictive</div>
                  <div className="text-sm text-gray-600">Tendances futures</div>
                  <div className="text-xs text-green-600 mt-1">3000-7000€</div>
                </button>
              </div>
            </div>
          </div>

          {isGenerating && (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <p className="mt-2 text-gray-600">Génération en cours...</p>
            </div>
          )}
        </div>
      )}

      {/* Modal de visualisation */}
      {selectedContent && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg max-w-4xl max-h-[80vh] overflow-hidden">
            <div className="p-6 border-b flex justify-between items-center">
              <h3 className="text-lg font-semibold">{selectedContent.title}</h3>
              <button 
                onClick={() => setSelectedContent(null)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>
            <div className="p-6 overflow-y-auto max-h-[60vh]">
              <pre className="whitespace-pre-wrap text-sm">{selectedContent.content}</pre>
            </div>
            <div className="p-6 border-t flex justify-end space-x-3">
              <button 
                onClick={() => downloadContent(selectedContent, 'md')}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Télécharger
              </button>
              <button 
                onClick={() => setSelectedContent(null)}
                className="px-4 py-2 border rounded hover:bg-gray-50"
              >
                Fermer
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default IntelligenceTab;

