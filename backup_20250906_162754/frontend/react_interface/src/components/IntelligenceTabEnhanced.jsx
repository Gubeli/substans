import React, { useState, useEffect } from 'react';

const IntelligenceTabEnhanced = () => {
  const [activeView, setActiveView] = useState('dashboard');
  const [intelligenceData, setIntelligenceData] = useState(null);
  const [selectedContent, setSelectedContent] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [realTimeData, setRealTimeData] = useState({});
  const [filterOptions, setFilterOptions] = useState({
    priority: 'all',
    timeframe: '24h',
    expert: 'all',
    sector: 'all'
  });

  // Simulation des données d'intelligence enrichies
  useEffect(() => {
    const mockData = {
      dashboard: {
        summary: {
          total_alerts: 47,
          high_priority: 12,
          trends_detected: 8,
          content_generated: 23,
          intelligence_score: 94
        },
        alerts: [
          {
            id: "ALERT_001",
            priority: "Critique",
            title: "JUPITER atteint 1 exaflop - Premier supercalculateur exascale européen",
            summary: "Impact estimé : 95% - Révolution dans le calcul haute performance",
            action_required: true,
            timestamp: new Date().toISOString(),
            expert: "Expert Semi-conducteurs (ESS)",
            sector: "HPC",
            confidence: 0.98,
            sources: ["HPCwire", "Top500.org", "Eviden.com"],
            impact_analysis: {
              market_size: "€2.3B",
              growth_potential: "+180%",
              competitive_advantage: "Très élevé"
            },
            recommended_actions: [
              "Analyser les implications pour Bull Sequana",
              "Évaluer les opportunités de partenariat",
              "Préparer une stratégie de positionnement"
            ]
          },
          {
            id: "ALERT_002",
            priority: "Haute", 
            title: "Nvidia annonce Blackwell B200 - 20x plus puissant que H100",
            summary: "Impact estimé : 92% - Nouvelle génération d'accélérateurs IA",
            action_required: true,
            timestamp: new Date(Date.now() - 3600000).toISOString(),
            expert: "Expert Digital Data IA (EDDI)",
            sector: "IA",
            confidence: 0.95,
            sources: ["Nvidia.com", "AnandTech", "IEEE Spectrum"],
            impact_analysis: {
              market_size: "€45B",
              growth_potential: "+250%",
              competitive_advantage: "Critique"
            },
            recommended_actions: [
              "Évaluer l'impact sur nos solutions IA",
              "Analyser les besoins d'adaptation",
              "Planifier la roadmap technologique"
            ]
          },
          {
            id: "ALERT_003",
            priority: "Moyenne",
            title: "La BCE lance l'euro numérique en phase pilote",
            summary: "Impact estimé : 78% - Transformation du système financier européen",
            action_required: false,
            timestamp: new Date(Date.now() - 7200000).toISOString(),
            expert: "Expert Banque Finance (EBF)",
            sector: "Finance",
            confidence: 0.89,
            sources: ["ECB.europa.eu", "Financial Times", "Reuters"],
            impact_analysis: {
              market_size: "€1.2T",
              growth_potential: "+85%",
              competitive_advantage: "Modéré"
            },
            recommended_actions: [
              "Surveiller les développements réglementaires",
              "Identifier les opportunités fintech",
              "Préparer les adaptations nécessaires"
            ]
          }
        ],
        trends: [
          {
            id: "TREND_001",
            trend: "IA Générative en Entreprise",
            growth_rate: "+45%",
            confidence: 0.92,
            time_horizon: "6-12 mois",
            impact_sectors: ["Finance", "Retail", "Manufacturing", "Healthcare"],
            market_value: "€127B",
            key_drivers: ["Productivité", "Automatisation", "Innovation"],
            risk_factors: ["Régulation", "Sécurité", "Éthique"],
            opportunities: [
              "Solutions d'automatisation intelligente",
              "Plateformes de génération de contenu",
              "Outils d'aide à la décision"
            ]
          },
          {
            trend: "Edge Computing Quantique",
            growth_rate: "+67%",
            confidence: 0.87,
            time_horizon: "12-24 mois",
            impact_sectors: ["Télécoms", "IoT", "Automotive", "Industry 4.0"],
            market_value: "€89B",
            key_drivers: ["Latence", "Sécurité", "Efficacité énergétique"],
            risk_factors: ["Complexité technique", "Coûts", "Standards"],
            opportunities: [
              "Infrastructure edge quantique",
              "Solutions de calcul distribué",
              "Sécurité quantique"
            ]
          },
          {
            trend: "Sustainability Tech",
            growth_rate: "+38%",
            confidence: 0.94,
            time_horizon: "3-6 mois",
            impact_sectors: ["Energy", "Manufacturing", "Transport", "Construction"],
            market_value: "€156B",
            key_drivers: ["Régulation ESG", "Coûts énergétiques", "Image de marque"],
            risk_factors: ["Investissements", "Changement culturel", "Mesure ROI"],
            opportunities: [
              "Solutions d'optimisation énergétique",
              "Plateformes de monitoring ESG",
              "Technologies de décarbonation"
            ]
          }
        ],
        real_time_metrics: {
          intelligence_velocity: "47 insights/h",
          processing_efficiency: "94%",
          prediction_accuracy: "91%",
          content_generation_rate: "12 items/h",
          system_health: "Excellent"
        }
      },
      content_library: [
        {
          id: "CONTENT_001",
          type: "linkedin_post",
          title: "🚀 L'Europe entre dans l'ère de l'exascale avec JUPITER",
          content: "🚀 JUPITER franchit la barre symbolique de l'exaflop ! Premier supercalculateur européen à atteindre cette performance...",
          status: "Prêt",
          generated_at: new Date().toISOString(),
          estimated_reach: "15K-25K vues",
          estimated_value: "€2,500",
          engagement_prediction: "8.5%",
          target_audience: "Décideurs IT, Ingénieurs HPC",
          hashtags: ["#HPC", "#Innovation", "#Europe", "#Exascale"],
          expert_source: "ESS",
          content_quality_score: 0.94
        },
        {
          id: "CONTENT_002",
          type: "executive_briefing",
          title: "Briefing Exécutif - Révolution Blackwell de Nvidia",
          content: "# BRIEFING EXÉCUTIF - Architecture Blackwell B200\n\n## Synthèse Stratégique\nNvidia révolutionne...",
          status: "Brouillon",
          generated_at: new Date(Date.now() - 1800000).toISOString(),
          estimated_reach: "C-Level, VP Technology",
          estimated_value: "€8,500",
          target_audience: "Direction Générale, CTO",
          expert_source: "EDDI",
          content_quality_score: 0.91
        },
        {
          id: "CONTENT_003",
          type: "market_report",
          title: "Rapport de Marché - Euro Numérique et Fintech",
          content: "# ANALYSE DE MARCHÉ - Euro Numérique\n\n## Impact sur l'écosystème fintech européen...",
          status: "Publié",
          generated_at: new Date(Date.now() - 3600000).toISOString(),
          estimated_reach: "Analystes financiers",
          estimated_value: "€12,000",
          target_audience: "Secteur bancaire, Fintech",
          expert_source: "EBF",
          content_quality_score: 0.96
        }
      ],
      analytics: {
        content_performance: {
          total_generated: 156,
          published: 89,
          avg_engagement: "7.2%",
          total_reach: "2.3M",
          estimated_value: "€145K"
        },
        intelligence_metrics: {
          sources_monitored: 247,
          insights_generated: 1834,
          accuracy_rate: "91%",
          response_time: "< 2min"
        }
      }
    };
    
    setIntelligenceData(mockData);
    
    // Simulation de données temps réel
    const interval = setInterval(() => {
      setRealTimeData({
        timestamp: new Date().toISOString(),
        active_monitoring: Math.floor(Math.random() * 50) + 200,
        new_insights: Math.floor(Math.random() * 5) + 1,
        processing_queue: Math.floor(Math.random() * 10) + 2
      });
    }, 5000);
    
    return () => clearInterval(interval);
  }, []);

  const generateContent = async (type, topic) => {
    setIsGenerating(true);
    // Simulation de génération de contenu
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    const newContent = {
      id: `CONTENT_${Date.now()}`,
      type: type,
      title: `Nouveau ${type} sur ${topic}`,
      content: `Contenu généré automatiquement pour ${topic}...`,
      status: "Brouillon",
      generated_at: new Date().toISOString(),
      estimated_reach: "10K-20K",
      estimated_value: "€3,000",
      expert_source: "Auto-généré",
      content_quality_score: 0.88
    };
    
    setIntelligenceData(prev => ({
      ...prev,
      content_library: [newContent, ...prev.content_library]
    }));
    
    setIsGenerating(false);
  };

  const filteredAlerts = intelligenceData?.dashboard.alerts.filter(alert => {
    if (filterOptions.priority !== 'all' && alert.priority !== filterOptions.priority) return false;
    if (filterOptions.expert !== 'all' && !alert.expert.includes(filterOptions.expert)) return false;
    if (filterOptions.sector !== 'all' && alert.sector !== filterOptions.sector) return false;
    return true;
  }) || [];

  if (!intelligenceData) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Chargement des données d'intelligence...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* En-tête avec métriques temps réel */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg p-6">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold">🧠 Intelligence Center</h2>
            <p className="text-blue-100 mt-1">Système de veille et génération de contenu automatisé</p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold">{intelligenceData.dashboard.summary.intelligence_score}%</div>
            <div className="text-blue-100 text-sm">Score d'Intelligence</div>
          </div>
        </div>
        
        <div className="grid grid-cols-5 gap-4 mt-6">
          <div className="text-center">
            <div className="text-2xl font-bold">{intelligenceData.dashboard.summary.total_alerts}</div>
            <div className="text-blue-100 text-sm">Alertes Totales</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-200">{intelligenceData.dashboard.summary.high_priority}</div>
            <div className="text-blue-100 text-sm">Haute Priorité</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{intelligenceData.dashboard.summary.trends_detected}</div>
            <div className="text-blue-100 text-sm">Tendances</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{intelligenceData.dashboard.summary.content_generated}</div>
            <div className="text-blue-100 text-sm">Contenus Générés</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{realTimeData.active_monitoring || 247}</div>
            <div className="text-blue-100 text-sm">Sources Actives</div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
        {[
          { id: 'dashboard', label: '📊 Dashboard', icon: '📊' },
          { id: 'alerts', label: '🚨 Alertes', icon: '🚨' },
          { id: 'trends', label: '📈 Tendances', icon: '📈' },
          { id: 'content', label: '📚 Contenu', icon: '📚' },
          { id: 'analytics', label: '📊 Analytics', icon: '📊' },
          { id: 'generator', label: '🤖 Générateur', icon: '🤖' }
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveView(tab.id)}
            className={`flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeView === tab.id
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Dashboard principal */}
      {activeView === 'dashboard' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Métriques temps réel */}
          <div className="bg-white rounded-lg border p-6">
            <h3 className="text-lg font-semibold mb-4">⚡ Métriques Temps Réel</h3>
            <div className="space-y-4">
              {Object.entries(intelligenceData.dashboard.real_time_metrics).map(([key, value]) => (
                <div key={key} className="flex justify-between items-center">
                  <span className="text-gray-600 capitalize">{key.replace('_', ' ')}</span>
                  <span className="font-medium text-green-600">{value}</span>
                </div>
              ))}
              {realTimeData.timestamp && (
                <div className="text-xs text-gray-500 mt-4">
                  Dernière mise à jour: {new Date(realTimeData.timestamp).toLocaleTimeString()}
                </div>
              )}
            </div>
          </div>

          {/* Alertes critiques */}
          <div className="bg-white rounded-lg border p-6">
            <h3 className="text-lg font-semibold mb-4">🚨 Alertes Critiques</h3>
            <div className="space-y-3">
              {intelligenceData.dashboard.alerts
                .filter(alert => alert.priority === 'Critique' || alert.priority === 'Haute')
                .slice(0, 3)
                .map((alert, index) => (
                <div key={index} className="p-3 bg-red-50 border-l-4 border-red-400 rounded">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h4 className="font-medium text-red-800">{alert.title}</h4>
                      <p className="text-sm text-red-600 mt-1">{alert.summary}</p>
                      <div className="flex items-center space-x-2 mt-2 text-xs text-red-500">
                        <span>Confiance: {(alert.confidence * 100).toFixed(0)}%</span>
                        <span>•</span>
                        <span>{alert.expert}</span>
                      </div>
                    </div>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      alert.priority === 'Critique' ? 'bg-red-100 text-red-800' : 'bg-orange-100 text-orange-800'
                    }`}>
                      {alert.priority}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Vue Alertes détaillées */}
      {activeView === 'alerts' && (
        <div className="space-y-6">
          {/* Filtres */}
          <div className="bg-white rounded-lg border p-4">
            <div className="flex flex-wrap gap-4">
              <select 
                value={filterOptions.priority}
                onChange={(e) => setFilterOptions(prev => ({...prev, priority: e.target.value}))}
                className="border rounded px-3 py-2"
              >
                <option value="all">Toutes priorités</option>
                <option value="Critique">Critique</option>
                <option value="Haute">Haute</option>
                <option value="Moyenne">Moyenne</option>
              </select>
              
              <select 
                value={filterOptions.expert}
                onChange={(e) => setFilterOptions(prev => ({...prev, expert: e.target.value}))}
                className="border rounded px-3 py-2"
              >
                <option value="all">Tous experts</option>
                <option value="ESS">Expert Semi-conducteurs</option>
                <option value="EDDI">Expert Digital Data IA</option>
                <option value="EBF">Expert Banque Finance</option>
              </select>
              
              <select 
                value={filterOptions.sector}
                onChange={(e) => setFilterOptions(prev => ({...prev, sector: e.target.value}))}
                className="border rounded px-3 py-2"
              >
                <option value="all">Tous secteurs</option>
                <option value="HPC">HPC</option>
                <option value="IA">IA</option>
                <option value="Finance">Finance</option>
              </select>
            </div>
          </div>

          {/* Liste des alertes */}
          <div className="space-y-4">
            {filteredAlerts.map((alert, index) => (
              <div key={index} className="bg-white border rounded-lg p-6">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        alert.priority === 'Critique' ? 'bg-red-100 text-red-800' :
                        alert.priority === 'Haute' ? 'bg-orange-100 text-orange-800' :
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {alert.priority}
                      </span>
                      <span className="text-xs text-gray-500">{alert.sector}</span>
                      <span className="text-xs text-gray-500">Confiance: {(alert.confidence * 100).toFixed(0)}%</span>
                    </div>
                    <h4 className="font-semibold text-lg">{alert.title}</h4>
                    <p className="text-gray-600 mt-2">{alert.summary}</p>
                  </div>
                </div>

                {/* Analyse d'impact */}
                <div className="grid grid-cols-3 gap-4 mb-4 p-4 bg-gray-50 rounded-lg">
                  <div className="text-center">
                    <div className="font-semibold text-green-600">{alert.impact_analysis.market_size}</div>
                    <div className="text-xs text-gray-600">Taille de marché</div>
                  </div>
                  <div className="text-center">
                    <div className="font-semibold text-blue-600">{alert.impact_analysis.growth_potential}</div>
                    <div className="text-xs text-gray-600">Potentiel de croissance</div>
                  </div>
                  <div className="text-center">
                    <div className="font-semibold text-purple-600">{alert.impact_analysis.competitive_advantage}</div>
                    <div className="text-xs text-gray-600">Avantage concurrentiel</div>
                  </div>
                </div>

                {/* Actions recommandées */}
                <div className="mb-4">
                  <h5 className="font-medium mb-2">🎯 Actions Recommandées:</h5>
                  <ul className="space-y-1">
                    {alert.recommended_actions.map((action, i) => (
                      <li key={i} className="text-sm text-gray-700 flex items-center">
                        <span className="w-2 h-2 bg-blue-400 rounded-full mr-2"></span>
                        {action}
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Sources et métadonnées */}
                <div className="flex justify-between items-center text-sm text-gray-500 border-t pt-3">
                  <div>
                    <span className="font-medium">{alert.expert}</span>
                    <span className="mx-2">•</span>
                    <span>Sources: {alert.sources.join(', ')}</span>
                  </div>
                  <div>
                    {new Date(alert.timestamp).toLocaleString()}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Vue Tendances */}
      {activeView === 'trends' && (
        <div className="space-y-6">
          {intelligenceData.dashboard.trends.map((trend, index) => (
            <div key={index} className="bg-white border rounded-lg p-6">
              <div className="flex justify-between items-start mb-4">
                <div className="flex-1">
                  <h3 className="text-xl font-semibold">{trend.trend}</h3>
                  <div className="flex items-center space-x-4 mt-2">
                    <span className="text-green-600 font-medium">{trend.growth_rate}</span>
                    <span className="text-gray-600">Confiance: {(trend.confidence * 100).toFixed(0)}%</span>
                    <span className="text-gray-600">Horizon: {trend.time_horizon}</span>
                    <span className="text-blue-600 font-medium">{trend.market_value}</span>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {/* Secteurs impactés */}
                <div>
                  <h4 className="font-medium mb-2">🎯 Secteurs Impactés</h4>
                  <div className="space-y-1">
                    {trend.impact_sectors.map((sector, i) => (
                      <span key={i} className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded mr-1 mb-1">
                        {sector}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Moteurs clés */}
                <div>
                  <h4 className="font-medium mb-2">🚀 Moteurs Clés</h4>
                  <ul className="space-y-1">
                    {trend.key_drivers.map((driver, i) => (
                      <li key={i} className="text-sm text-gray-700 flex items-center">
                        <span className="w-1.5 h-1.5 bg-green-400 rounded-full mr-2"></span>
                        {driver}
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Facteurs de risque */}
                <div>
                  <h4 className="font-medium mb-2">⚠️ Risques</h4>
                  <ul className="space-y-1">
                    {trend.risk_factors.map((risk, i) => (
                      <li key={i} className="text-sm text-gray-700 flex items-center">
                        <span className="w-1.5 h-1.5 bg-red-400 rounded-full mr-2"></span>
                        {risk}
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Opportunités */}
                <div>
                  <h4 className="font-medium mb-2">💡 Opportunités</h4>
                  <ul className="space-y-1">
                    {trend.opportunities.map((opportunity, i) => (
                      <li key={i} className="text-sm text-gray-700 flex items-center">
                        <span className="w-1.5 h-1.5 bg-purple-400 rounded-full mr-2"></span>
                        {opportunity}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Vue Bibliothèque de contenu */}
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
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        content.status === 'Prêt' ? 'bg-green-100 text-green-800' :
                        content.status === 'Brouillon' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-blue-100 text-blue-800'
                      }`}>
                        {content.status}
                      </span>
                      <span className="text-xs text-gray-500">
                        Score: {(content.content_quality_score * 100).toFixed(0)}%
                      </span>
                    </div>
                    <h4 className="font-medium">{content.title}</h4>
                    <p className="text-sm text-gray-600 mt-2 line-clamp-2">{content.content}</p>
                    
                    {/* Métriques de performance */}
                    <div className="grid grid-cols-3 gap-4 mt-3 p-3 bg-gray-50 rounded">
                      <div className="text-center">
                        <div className="text-sm font-medium">{content.estimated_reach}</div>
                        <div className="text-xs text-gray-600">Portée estimée</div>
                      </div>
                      <div className="text-center">
                        <div className="text-sm font-medium text-green-600">{content.estimated_value}</div>
                        <div className="text-xs text-gray-600">Valeur estimée</div>
                      </div>
                      <div className="text-center">
                        <div className="text-sm font-medium">{content.engagement_prediction || 'N/A'}</div>
                        <div className="text-xs text-gray-600">Engagement prévu</div>
                      </div>
                    </div>

                    <div className="flex items-center space-x-4 mt-3 text-xs text-gray-500">
                      <span>Généré le {new Date(content.generated_at).toLocaleDateString()}</span>
                      <span>Source: {content.expert_source}</span>
                      {content.target_audience && <span>Audience: {content.target_audience}</span>}
                    </div>
                  </div>
                  <div className="flex space-x-2 ml-4">
                    <button 
                      onClick={() => setSelectedContent(content)}
                      className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
                    >
                      👁️ Voir
                    </button>
                    <button className="px-3 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700">
                      📤 Publier
                    </button>
                    <button className="px-3 py-1 bg-gray-600 text-white rounded text-sm hover:bg-gray-700">
                      ✏️ Éditer
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Vue Analytics */}
      {activeView === 'analytics' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Performance du contenu */}
            <div className="bg-white rounded-lg border p-6">
              <h3 className="text-lg font-semibold mb-4">📊 Performance du Contenu</h3>
              <div className="space-y-4">
                {Object.entries(intelligenceData.analytics.content_performance).map(([key, value]) => (
                  <div key={key} className="flex justify-between items-center">
                    <span className="text-gray-600 capitalize">{key.replace('_', ' ')}</span>
                    <span className="font-medium">{value}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Métriques d'intelligence */}
            <div className="bg-white rounded-lg border p-6">
              <h3 className="text-lg font-semibold mb-4">🧠 Métriques d'Intelligence</h3>
              <div className="space-y-4">
                {Object.entries(intelligenceData.analytics.intelligence_metrics).map(([key, value]) => (
                  <div key={key} className="flex justify-between items-center">
                    <span className="text-gray-600 capitalize">{key.replace('_', ' ')}</span>
                    <span className="font-medium">{value}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Vue Générateur */}
      {activeView === 'generator' && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg border p-6">
            <h3 className="text-lg font-semibold mb-4">🤖 Générateur de Contenu Automatisé</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-4">
                <h4 className="font-medium">Type de contenu</h4>
                <select className="w-full border rounded px-3 py-2">
                  <option value="linkedin_post">Post LinkedIn</option>
                  <option value="executive_briefing">Briefing Exécutif</option>
                  <option value="market_report">Rapport de Marché</option>
                  <option value="social_story">Story Sociale</option>
                  <option value="newsletter">Newsletter</option>
                </select>
              </div>
              
              <div className="space-y-4">
                <h4 className="font-medium">Sujet/Tendance</h4>
                <select className="w-full border rounded px-3 py-2">
                  <option>IA Générative en Entreprise</option>
                  <option>Edge Computing Quantique</option>
                  <option>Sustainability Tech</option>
                  <option>Supercalcul Exascale</option>
                  <option>Euro Numérique</option>
                </select>
              </div>
              
              <div className="space-y-4">
                <h4 className="font-medium">Audience cible</h4>
                <select className="w-full border rounded px-3 py-2">
                  <option>Décideurs IT</option>
                  <option>Direction Générale</option>
                  <option>Analystes financiers</option>
                  <option>Ingénieurs</option>
                  <option>Grand public tech</option>
                </select>
              </div>
            </div>
            
            <div className="mt-6">
              <button 
                onClick={() => generateContent('linkedin_post', 'IA Générative')}
                disabled={isGenerating}
                className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {isGenerating ? '🔄 Génération en cours...' : '🚀 Générer le contenu'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de visualisation de contenu */}
      {selectedContent && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg max-w-4xl max-h-[80vh] overflow-y-auto p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">{selectedContent.title}</h3>
              <button 
                onClick={() => setSelectedContent(null)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>
            <div className="prose max-w-none">
              <pre className="whitespace-pre-wrap">{selectedContent.content}</pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default IntelligenceTabEnhanced;

