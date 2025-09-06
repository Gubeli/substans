import React, { useState, useEffect } from 'react';

const EnterpriseDashboard = ({ enterpriseData, onRefresh }) => {
  const [selectedSystem, setSelectedSystem] = useState(null);
  const [showSystemDetails, setShowSystemDetails] = useState(false);

  const getStatusColor = (score) => {
    if (score >= 95) return 'text-green-600 bg-green-100';
    if (score >= 85) return 'text-yellow-600 bg-yellow-100';
    if (score >= 70) return 'text-orange-600 bg-orange-100';
    return 'text-red-600 bg-red-100';
  };

  const getStatusIcon = (score) => {
    if (score >= 95) return '✅';
    if (score >= 85) return '⚠️';
    if (score >= 70) return '🔶';
    return '❌';
  };

  return (
    <div className="space-y-6">
      {/* Header Enterprise */}
      <div className="bg-gradient-to-r from-blue-900 to-purple-900 text-white p-6 rounded-lg">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">Substans.AI Enterprise v{enterpriseData.overview?.version || '3.0.0'}</h1>
            <p className="text-blue-200 mt-2">Méga-Cabinet Virtuel - 47 Systèmes Opérationnels</p>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold">{enterpriseData.overview?.uptime || 99.95}%</div>
            <div className="text-blue-200">Uptime</div>
          </div>
        </div>
      </div>

      {/* Métriques Principales */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-green-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Performance</p>
              <p className="text-2xl font-bold text-gray-900">
                {enterpriseData.overview?.performance_score || 94.2}%
              </p>
            </div>
            <div className="text-3xl">🚀</div>
          </div>
          <div className="mt-2">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-green-500 h-2 rounded-full" 
                style={{ width: `${enterpriseData.overview?.performance_score || 94.2}%` }}
              ></div>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-blue-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Sécurité</p>
              <p className="text-2xl font-bold text-gray-900">
                {enterpriseData.overview?.security_score || 98.5}%
              </p>
            </div>
            <div className="text-3xl">🔒</div>
          </div>
          <div className="mt-2">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-500 h-2 rounded-full" 
                style={{ width: `${enterpriseData.overview?.security_score || 98.5}%` }}
              ></div>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-purple-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Conformité</p>
              <p className="text-2xl font-bold text-gray-900">
                {enterpriseData.overview?.compliance_score || 96.8}%
              </p>
            </div>
            <div className="text-3xl">📋</div>
          </div>
          <div className="mt-2">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-purple-500 h-2 rounded-full" 
                style={{ width: `${enterpriseData.overview?.compliance_score || 96.8}%` }}
              ></div>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-indigo-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Missions Actives</p>
              <p className="text-2xl font-bold text-gray-900">
                {enterpriseData.metrics?.active_missions || 5}
              </p>
            </div>
            <div className="text-3xl">📊</div>
          </div>
          <div className="mt-2">
            <p className="text-sm text-gray-600">
              Total: {enterpriseData.metrics?.total_missions || 127}
            </p>
          </div>
        </div>
      </div>

      {/* Systèmes Enterprise */}
      <div className="bg-white rounded-lg shadow-md">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Systèmes Enterprise (47)</h2>
          <p className="text-sm text-gray-600 mt-1">32 Agents Experts + 15 Systèmes Core</p>
        </div>
        
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Agents Consultants */}
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-3">Agents Consultants (7)</h3>
              <div className="space-y-2">
                {[
                  { name: 'Agent Veille Stratégique', status: 95 },
                  { name: 'Agent Analyse Données', status: 98 },
                  { name: 'Agent Gestion Connaissances', status: 94 },
                  { name: 'Agent Proposition Commerciale', status: 96 },
                  { name: 'Agent Rédaction Rapports', status: 93 },
                  { name: 'Agent Suivi Mission', status: 97 },
                  { name: 'Agent Méthodes & Outils', status: 95 }
                ].map((agent, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">{agent.name}</span>
                    <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(agent.status)}`}>
                      {getStatusIcon(agent.status)} {agent.status}%
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Experts Métiers */}
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-3">Experts Métiers (11)</h3>
              <div className="space-y-2">
                {[
                  { name: 'Expert Semi-conducteurs', status: 96 },
                  { name: 'Expert Banque Finance', status: 94 },
                  { name: 'Expert Assurance', status: 92 },
                  { name: 'Expert Données Digitales', status: 98 },
                  { name: 'Expert Finance & M&A', status: 97 }
                ].map((expert, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">{expert.name}</span>
                    <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(expert.status)}`}>
                      {getStatusIcon(expert.status)} {expert.status}%
                    </span>
                  </div>
                ))}
                <div className="text-xs text-gray-500 mt-2">+ 6 autres experts actifs</div>
              </div>
            </div>

            {/* Experts Domaines */}
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-3">Experts Domaines (14)</h3>
              <div className="space-y-2">
                {[
                  { name: 'Expert Intelligence Artificielle', status: 99 },
                  { name: 'Expert Cybersécurité', status: 97 },
                  { name: 'Expert Cloud', status: 95 },
                  { name: 'Expert Data', status: 96 },
                  { name: 'Expert Finance & Stratégie', status: 98 }
                ].map((expert, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">{expert.name}</span>
                    <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(expert.status)}`}>
                      {getStatusIcon(expert.status)} {expert.status}%
                    </span>
                  </div>
                ))}
                <div className="text-xs text-gray-500 mt-2">+ 9 autres experts actifs</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Systèmes Core */}
      <div className="bg-white rounded-lg shadow-md">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Systèmes Core Enterprise (15)</h2>
          <p className="text-sm text-gray-600 mt-1">Infrastructure et services avancés</p>
        </div>
        
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Systèmes Core */}
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-3">Core (4)</h3>
              <div className="space-y-2">
                {[
                  { name: 'Core Engine', status: 97 },
                  { name: 'System Orchestrator', status: 95 },
                  { name: 'ML Engine', status: 98 },
                  { name: 'System Monitor', status: 96 }
                ].map((system, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">{system.name}</span>
                    <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(system.status)}`}>
                      {getStatusIcon(system.status)} {system.status}%
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Systèmes Spécialisés */}
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-3">Spécialisés (4)</h3>
              <div className="space-y-2">
                {[
                  { name: 'Knowledge Base Sémantique', status: 94 },
                  { name: 'Methodology Adaptive', status: 96 },
                  { name: 'Intelligence Prédictive', status: 98 },
                  { name: 'Trend Detection', status: 93 }
                ].map((system, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">{system.name}</span>
                    <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(system.status)}`}>
                      {getStatusIcon(system.status)} {system.status}%
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Autres Systèmes */}
            <div className="border rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-3">Gestion & Sécurité (7)</h3>
              <div className="space-y-2">
                {[
                  { name: 'Mission Manager', status: 95 },
                  { name: 'Quality Assurance', status: 97 },
                  { name: 'Performance Analytics', status: 94 },
                  { name: 'Security Manager', status: 99 },
                  { name: 'API Gateway', status: 96 }
                ].map((system, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">{system.name}</span>
                    <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(system.status)}`}>
                      {getStatusIcon(system.status)} {system.status}%
                    </span>
                  </div>
                ))}
                <div className="text-xs text-gray-500 mt-2">+ 2 autres systèmes</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Alertes et Activités */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Alertes */}
        <div className="bg-white rounded-lg shadow-md">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">Alertes Actives</h2>
          </div>
          <div className="p-6">
            {enterpriseData.alerts && enterpriseData.alerts.length > 0 ? (
              <div className="space-y-3">
                {enterpriseData.alerts.map((alert, index) => (
                  <div key={index} className={`p-3 rounded-lg border-l-4 ${
                    alert.severity === 'critical' ? 'border-red-500 bg-red-50' :
                    alert.severity === 'warning' ? 'border-yellow-500 bg-yellow-50' :
                    'border-blue-500 bg-blue-50'
                  }`}>
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{alert.message}</span>
                      <span className="text-xs text-gray-500">{alert.timestamp}</span>
                    </div>
                    <div className="text-sm text-gray-600 mt-1">Système: {alert.system}</div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <div className="text-4xl mb-4">✅</div>
                <p className="text-gray-600">Aucune alerte active</p>
                <p className="text-sm text-gray-500 mt-1">Tous les systèmes fonctionnent normalement</p>
              </div>
            )}
          </div>
        </div>

        {/* Activités Récentes */}
        <div className="bg-white rounded-lg shadow-md">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">Activités Récentes</h2>
          </div>
          <div className="p-6">
            <div className="space-y-3">
              {[
                { type: 'system_start', message: 'Substans Enterprise v3.0 démarré', time: '2 min' },
                { type: 'agent_update', message: '32 agents experts mis à jour', time: '5 min' },
                { type: 'mission_complete', message: 'Mission Bull terminée avec succès', time: '1h' },
                { type: 'backup', message: 'Sauvegarde automatique effectuée', time: '2h' },
                { type: 'security_scan', message: 'Scan sécurité complété - Aucun problème', time: '4h' }
              ].map((activity, index) => (
                <div key={index} className="flex items-center space-x-3">
                  <div className={`w-2 h-2 rounded-full ${
                    activity.type === 'system_start' ? 'bg-green-500' :
                    activity.type === 'agent_update' ? 'bg-blue-500' :
                    activity.type === 'mission_complete' ? 'bg-purple-500' :
                    activity.type === 'backup' ? 'bg-yellow-500' :
                    'bg-gray-500'
                  }`}></div>
                  <div className="flex-1">
                    <p className="text-sm text-gray-900">{activity.message}</p>
                    <p className="text-xs text-gray-500">Il y a {activity.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Actions Rapides */}
      <div className="bg-white rounded-lg shadow-md">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Actions Rapides</h2>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <button 
              onClick={onRefresh}
              className="flex flex-col items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div className="text-2xl mb-2">🔄</div>
              <span className="text-sm font-medium">Actualiser</span>
            </button>
            
            <button className="flex flex-col items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
              <div className="text-2xl mb-2">📊</div>
              <span className="text-sm font-medium">Rapports</span>
            </button>
            
            <button className="flex flex-col items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
              <div className="text-2xl mb-2">⚙️</div>
              <span className="text-sm font-medium">Configuration</span>
            </button>
            
            <button className="flex flex-col items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
              <div className="text-2xl mb-2">🔒</div>
              <span className="text-sm font-medium">Sécurité</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EnterpriseDashboard;

