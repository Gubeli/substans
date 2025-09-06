import React, { useState, useEffect } from 'react';

const ReportingSystem = () => {
  const [activeReportTab, setActiveReportTab] = useState('overview');
  const [reportData, setReportData] = useState({
    overview: {
      total_reports: 156,
      generated_today: 8,
      scheduled_reports: 12,
      report_types: 7
    },
    performance: {
      system_performance: 94.2,
      agent_performance: 96.8,
      mission_success_rate: 98.5,
      user_satisfaction: 9.2
    },
    analytics: {
      missions_completed: 127,
      agents_active: 32,
      systems_operational: 47,
      uptime_percentage: 99.95
    }
  });

  const [selectedReport, setSelectedReport] = useState(null);
  const [showReportDialog, setShowReportDialog] = useState(false);

  const reportTypes = [
    {
      id: 'performance',
      name: 'Rapport de Performance',
      description: 'Analyse complète des performances système et agents',
      icon: '📊',
      frequency: 'Quotidien',
      lastGenerated: '2024-01-15 09:30',
      status: 'Actif'
    },
    {
      id: 'security',
      name: 'Rapport de Sécurité',
      description: 'Audit sécurité et conformité enterprise',
      icon: '🔒',
      frequency: 'Hebdomadaire',
      lastGenerated: '2024-01-14 18:00',
      status: 'Actif'
    },
    {
      id: 'missions',
      name: 'Rapport Missions',
      description: 'Analyse des missions et livrables',
      icon: '📋',
      frequency: 'Quotidien',
      lastGenerated: '2024-01-15 08:00',
      status: 'Actif'
    },
    {
      id: 'intelligence',
      name: 'Intelligence Quotidienne',
      description: 'Synthèse de veille des 32 agents experts',
      icon: '🧠',
      frequency: 'Quotidien',
      lastGenerated: '2024-01-15 06:00',
      status: 'Actif'
    },
    {
      id: 'financial',
      name: 'Rapport Financier',
      description: 'Analyse financière et ROI des missions',
      icon: '💰',
      frequency: 'Mensuel',
      lastGenerated: '2024-01-01 09:00',
      status: 'Programmé'
    },
    {
      id: 'quality',
      name: 'Rapport Qualité',
      description: 'Assurance qualité et métriques de satisfaction',
      icon: '⭐',
      frequency: 'Hebdomadaire',
      lastGenerated: '2024-01-14 16:30',
      status: 'Actif'
    },
    {
      id: 'trends',
      name: 'Analyse des Tendances',
      description: 'Détection de tendances et prédictions',
      icon: '📈',
      frequency: 'Hebdomadaire',
      lastGenerated: '2024-01-14 14:00',
      status: 'Actif'
    }
  ];

  const handleGenerateReport = (reportType) => {
    setSelectedReport(reportType);
    setShowReportDialog(true);
  };

  const handleDownloadReport = (format) => {
    // Simuler le téléchargement
    const reportName = `${selectedReport.name}_${new Date().toISOString().split('T')[0]}`;
    console.log(`Téléchargement du rapport: ${reportName}.${format}`);
    setShowReportDialog(false);
  };

  return (
    <div className="space-y-6">
      {/* Header Reporting */}
      <div className="bg-gradient-to-r from-indigo-900 to-blue-900 text-white p-6 rounded-lg">
        <h1 className="text-3xl font-bold">Système de Reporting Enterprise</h1>
        <p className="text-indigo-200 mt-2">Analytics avancés et rapports automatisés</p>
      </div>

      {/* Onglets Reporting */}
      <div className="bg-white rounded-lg shadow-md">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {[
              { id: 'overview', name: 'Vue d\'ensemble', icon: '📊' },
              { id: 'reports', name: 'Rapports', icon: '📋' },
              { id: 'analytics', name: 'Analytics', icon: '📈' },
              { id: 'schedule', name: 'Planification', icon: '⏰' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveReportTab(tab.id)}
                className={`py-4 px-2 border-b-2 font-medium text-sm ${
                  activeReportTab === tab.id
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.name}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {/* Vue d'ensemble */}
          {activeReportTab === 'overview' && (
            <div className="space-y-6">
              {/* Métriques Principales */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="bg-gradient-to-r from-blue-500 to-blue-600 text-white p-6 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-blue-100">Rapports Générés</p>
                      <p className="text-3xl font-bold">{reportData.overview.total_reports}</p>
                    </div>
                    <div className="text-4xl opacity-80">📊</div>
                  </div>
                </div>

                <div className="bg-gradient-to-r from-green-500 to-green-600 text-white p-6 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-green-100">Aujourd'hui</p>
                      <p className="text-3xl font-bold">{reportData.overview.generated_today}</p>
                    </div>
                    <div className="text-4xl opacity-80">📈</div>
                  </div>
                </div>

                <div className="bg-gradient-to-r from-purple-500 to-purple-600 text-white p-6 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-purple-100">Programmés</p>
                      <p className="text-3xl font-bold">{reportData.overview.scheduled_reports}</p>
                    </div>
                    <div className="text-4xl opacity-80">⏰</div>
                  </div>
                </div>

                <div className="bg-gradient-to-r from-orange-500 to-orange-600 text-white p-6 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-orange-100">Types Disponibles</p>
                      <p className="text-3xl font-bold">{reportData.overview.report_types}</p>
                    </div>
                    <div className="text-4xl opacity-80">📋</div>
                  </div>
                </div>
              </div>

              {/* Performance Globale */}
              <div className="bg-white border rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Globale</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-blue-600">{reportData.performance.system_performance}%</div>
                    <div className="text-sm text-gray-600 mt-1">Performance Système</div>
                    <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                      <div className="bg-blue-600 h-2 rounded-full" style={{ width: `${reportData.performance.system_performance}%` }}></div>
                    </div>
                  </div>

                  <div className="text-center">
                    <div className="text-3xl font-bold text-green-600">{reportData.performance.agent_performance}%</div>
                    <div className="text-sm text-gray-600 mt-1">Performance Agents</div>
                    <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                      <div className="bg-green-600 h-2 rounded-full" style={{ width: `${reportData.performance.agent_performance}%` }}></div>
                    </div>
                  </div>

                  <div className="text-center">
                    <div className="text-3xl font-bold text-purple-600">{reportData.performance.mission_success_rate}%</div>
                    <div className="text-sm text-gray-600 mt-1">Taux de Succès</div>
                    <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                      <div className="bg-purple-600 h-2 rounded-full" style={{ width: `${reportData.performance.mission_success_rate}%` }}></div>
                    </div>
                  </div>

                  <div className="text-center">
                    <div className="text-3xl font-bold text-orange-600">{reportData.performance.user_satisfaction}/10</div>
                    <div className="text-sm text-gray-600 mt-1">Satisfaction Client</div>
                    <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                      <div className="bg-orange-600 h-2 rounded-full" style={{ width: `${reportData.performance.user_satisfaction * 10}%` }}></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Rapports */}
          {activeReportTab === 'reports' && (
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold text-gray-900">Types de Rapports Disponibles</h3>
                <button className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors">
                  Nouveau Rapport
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {reportTypes.map((report) => (
                  <div key={report.id} className="border rounded-lg p-6 hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between mb-4">
                      <div className="text-3xl">{report.icon}</div>
                      <span className={`px-2 py-1 rounded-full text-xs ${
                        report.status === 'Actif' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {report.status}
                      </span>
                    </div>
                    
                    <h4 className="font-semibold text-gray-900 mb-2">{report.name}</h4>
                    <p className="text-sm text-gray-600 mb-4">{report.description}</p>
                    
                    <div className="space-y-2 text-sm text-gray-500">
                      <div className="flex justify-between">
                        <span>Fréquence:</span>
                        <span>{report.frequency}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Dernière génération:</span>
                        <span>{report.lastGenerated}</span>
                      </div>
                    </div>
                    
                    <div className="mt-4 flex space-x-2">
                      <button 
                        onClick={() => handleGenerateReport(report)}
                        className="flex-1 bg-indigo-600 text-white px-3 py-2 rounded text-sm hover:bg-indigo-700 transition-colors"
                      >
                        Générer
                      </button>
                      <button className="flex-1 border border-gray-300 text-gray-700 px-3 py-2 rounded text-sm hover:bg-gray-50 transition-colors">
                        Configurer
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Analytics */}
          {activeReportTab === 'analytics' && (
            <div className="space-y-6">
              <h3 className="text-lg font-semibold text-gray-900">Analytics Temps Réel</h3>
              
              {/* Graphiques et métriques */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="border rounded-lg p-6">
                  <h4 className="font-semibold text-gray-900 mb-4">Évolution des Missions</h4>
                  <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
                    <div className="text-center text-gray-500">
                      <div className="text-4xl mb-2">📈</div>
                      <p>Graphique des missions</p>
                      <p className="text-sm">127 missions terminées</p>
                    </div>
                  </div>
                </div>

                <div className="border rounded-lg p-6">
                  <h4 className="font-semibold text-gray-900 mb-4">Performance des Agents</h4>
                  <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
                    <div className="text-center text-gray-500">
                      <div className="text-4xl mb-2">🤖</div>
                      <p>Performance agents</p>
                      <p className="text-sm">32 agents actifs</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Métriques détaillées */}
              <div className="border rounded-lg p-6">
                <h4 className="font-semibold text-gray-900 mb-4">Métriques Détaillées</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">{reportData.analytics.missions_completed}</div>
                    <div className="text-sm text-gray-600">Missions Terminées</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-600">{reportData.analytics.agents_active}</div>
                    <div className="text-sm text-gray-600">Agents Actifs</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-600">{reportData.analytics.systems_operational}</div>
                    <div className="text-sm text-gray-600">Systèmes Opérationnels</div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Planification */}
          {activeReportTab === 'schedule' && (
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-semibold text-gray-900">Rapports Programmés</h3>
                <button className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors">
                  Nouveau Planning
                </button>
              </div>

              <div className="border rounded-lg">
                <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
                  <div className="grid grid-cols-5 gap-4 text-sm font-medium text-gray-700">
                    <div>Rapport</div>
                    <div>Fréquence</div>
                    <div>Prochaine Exécution</div>
                    <div>Statut</div>
                    <div>Actions</div>
                  </div>
                </div>
                
                <div className="divide-y divide-gray-200">
                  {reportTypes.filter(r => r.status === 'Actif').map((report) => (
                    <div key={report.id} className="px-6 py-4">
                      <div className="grid grid-cols-5 gap-4 items-center text-sm">
                        <div className="flex items-center">
                          <span className="mr-2">{report.icon}</span>
                          {report.name}
                        </div>
                        <div>{report.frequency}</div>
                        <div>Demain 09:00</div>
                        <div>
                          <span className="px-2 py-1 rounded-full text-xs bg-green-100 text-green-800">
                            Actif
                          </span>
                        </div>
                        <div className="flex space-x-2">
                          <button className="text-indigo-600 hover:text-indigo-800">Modifier</button>
                          <button className="text-red-600 hover:text-red-800">Suspendre</button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Dialog de génération de rapport */}
      {showReportDialog && selectedReport && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Générer {selectedReport.name}</h3>
              <button 
                onClick={() => setShowReportDialog(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            
            <div className="mb-6">
              <p className="text-sm text-gray-600 mb-4">{selectedReport.description}</p>
              
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Période
                  </label>
                  <select className="w-full border border-gray-300 rounded-lg px-3 py-2">
                    <option>Dernières 24h</option>
                    <option>Dernière semaine</option>
                    <option>Dernier mois</option>
                    <option>Personnalisé</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Format de sortie
                  </label>
                  <div className="flex space-x-2">
                    <button 
                      onClick={() => handleDownloadReport('pdf')}
                      className="flex-1 bg-red-600 text-white px-3 py-2 rounded text-sm hover:bg-red-700 transition-colors"
                    >
                      PDF
                    </button>
                    <button 
                      onClick={() => handleDownloadReport('xlsx')}
                      className="flex-1 bg-green-600 text-white px-3 py-2 rounded text-sm hover:bg-green-700 transition-colors"
                    >
                      Excel
                    </button>
                    <button 
                      onClick={() => handleDownloadReport('docx')}
                      className="flex-1 bg-blue-600 text-white px-3 py-2 rounded text-sm hover:bg-blue-700 transition-colors"
                    >
                      Word
                    </button>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="flex space-x-3">
              <button 
                onClick={() => setShowReportDialog(false)}
                className="flex-1 border border-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Annuler
              </button>
              <button className="flex-1 bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors">
                Générer Maintenant
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ReportingSystem;

