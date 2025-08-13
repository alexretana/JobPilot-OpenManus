import { Component, createSignal, onMount, onCleanup, createEffect } from 'solid-js';
import { apiService } from '../services/api';
import { webSocketService } from '../services/websocket';
import type { HealthCheckResponse } from '../types';

interface StatusPanelProps {
  onQuickAction: (query: string) => void;
  isProcessing: () => boolean;
  isOpen: () => boolean;
  onClose: () => void;
}

const StatusPanel: Component<StatusPanelProps> = (props) => {
  const [health, setHealth] = createSignal<HealthCheckResponse | null>(null);
  const [lastHealthCheck, setLastHealthCheck] = createSignal<Date | null>(null);
  
  let healthCheckInterval: number | undefined;

  const checkHealth = async () => {
    try {
      const healthData = await apiService.healthCheck();
      setHealth(healthData);
      setLastHealthCheck(new Date());
    } catch (error) {
      console.error('Health check failed:', error);
      setHealth(null);
    }
  };

  onMount(() => {
    checkHealth();
    healthCheckInterval = window.setInterval(checkHealth, 30000); // Check every 30 seconds
  });

  onCleanup(() => {
    if (healthCheckInterval) {
      clearInterval(healthCheckInterval);
    }
  });

  const quickActions = [
    {
      icon: '🐍',
      label: 'Python Jobs',
      query: 'Show me remote Python developer jobs',
      color: 'btn-primary'
    },
    {
      icon: '📊',
      label: 'Data Science',
      query: 'Data science jobs for 5 years experience',
      color: 'btn-secondary'
    },
    {
      icon: '🤖',
      label: 'AI/ML Jobs',
      query: 'Machine learning engineer positions remote',
      color: 'btn-accent'
    },
    {
      icon: '📄',
      label: 'Resume Help',
      query: 'Help me optimize my resume for tech roles',
      color: 'btn-info'
    },
    {
      icon: '📈',
      label: 'Market Trends',
      query: 'What are the current trends in AI/ML job market?',
      color: 'btn-success'
    },
    {
      icon: '✍️',
      label: 'Cover Letter',
      query: 'Generate a cover letter template for software engineering',
      color: 'btn-warning'
    }
  ];

  const formatTime = (date: Date | null) => {
    if (!date) return 'Never';
    return date.toLocaleTimeString('en-US', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <>
      {/* Drawer Overlay */}
      {props.isOpen() && (
        <div 
          class="fixed inset-0 bg-black bg-opacity-50 z-40"
          onClick={() => props.onClose()}
        />
      )}
      
      {/* Right Drawer */}
      <div class={`fixed top-0 right-0 h-full w-80 bg-base-100 shadow-xl z-50 transform transition-transform duration-300 ease-in-out flex flex-col ${
        props.isOpen() ? 'translate-x-0' : 'translate-x-full'
      }`}>
        {/* Header */}
        <div class="flex items-center justify-between p-4 border-b border-base-200">
          <div class="flex items-center space-x-2">
            <span class="text-xl">⚡</span>
            <h2 class="text-lg font-bold">System Status</h2>
          </div>
          <button 
            class="btn btn-sm btn-circle btn-ghost"
            onClick={() => props.onClose()}
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        {/* Scrollable Content */}
        <div class="flex-1 overflow-y-auto p-4 space-y-6">
          {/* System Status */}
          <div>
            <h3 class="text-sm font-medium mb-3 flex items-center">
              <span class="mr-2">📊</span>
              Connection Status
            </h3>
            <div class="stats stats-vertical shadow w-full">
              <div class="stat">
                <div class="stat-figure text-primary">
                  <div class={`avatar placeholder ${webSocketService.getIsConnected()() ? 'online' : 'offline'}`}>
                    <div class="bg-neutral text-neutral-content rounded-full w-8">
                      <span class="text-xs">WS</span>
                    </div>
                  </div>
                </div>
                <div class="stat-title text-xs">WebSocket</div>
                <div class="stat-value text-sm">
                  {webSocketService.getIsConnected()() ? 'Connected' : 'Disconnected'}
                </div>
              </div>
              
              <div class="stat">
                <div class="stat-figure text-secondary">
                  <div class={`avatar placeholder ${health() ? 'online' : 'offline'}`}>
                    <div class="bg-neutral text-neutral-content rounded-full w-8">
                      <span class="text-xs">API</span>
                    </div>
                  </div>
                </div>
                <div class="stat-title text-xs">Backend</div>
                <div class="stat-value text-sm">
                  {health()?.status || 'Unknown'}
                </div>
              </div>
            </div>
          </div>

          {/* Detailed Status */}
          <div>
            <h3 class="text-sm font-medium mb-3 flex items-center">
              <span class="mr-2">🔧</span>
              System Details
            </h3>
            <div class="card bg-base-200 p-3">
              <div class="text-sm space-y-2">
                <div class="flex justify-between">
                  <span>🟢 Status:</span>
                  <span class="font-medium">{health() ? 'Healthy' : 'Checking...'}</span>
                </div>
                <div class="flex justify-between">
                  <span>🧠 Service:</span>
                  <span class="font-medium text-right">{health()?.service || 'JobPilot-OpenManus'}</span>
                </div>
                <div class="flex justify-between">
                  <span>🔧 Tools:</span>
                  <span class="font-medium text-right">Job Search, Browser, Analysis</span>
                </div>
                <div class="flex justify-between">
                  <span>🖥️ Browser:</span>
                  <span class="font-medium text-right">Non-headless (Visible)</span>
                </div>
                <div class="flex justify-between">
                  <span>🕒 Last Check:</span>
                  <span class="font-medium text-right">{formatTime(lastHealthCheck())}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div>
            <h3 class="text-sm font-medium mb-3 flex items-center">
              <span class="mr-2">🎯</span>
              Quick Actions
            </h3>
            <div class="grid grid-cols-1 gap-2">
              {quickActions.map((action) => (
                <button
                  class={`btn btn-sm ${action.color} btn-outline normal-case justify-start`}
                  onClick={() => props.onQuickAction(action.query)}
                  disabled={props.isProcessing()}
                  title={action.query}
                >
                  <span class="mr-2">{action.icon}</span>
                  {action.label}
                </button>
              ))}
            </div>
          </div>

          {/* Additional Actions */}
          <div>
            <h3 class="text-sm font-medium mb-3 flex items-center">
              <span class="mr-2">⚙️</span>
              System Actions
            </h3>
            <div class="space-y-2">
              <button 
                class="btn btn-outline btn-sm w-full justify-start"
                onClick={checkHealth}
                disabled={props.isProcessing()}
              >
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Refresh Status
              </button>
              <button 
                class="btn btn-outline btn-sm w-full justify-start"
                onClick={() => webSocketService.connect()}
                disabled={webSocketService.getIsConnected()()}
              >
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0" />
                </svg>
                Reconnect WebSocket
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default StatusPanel;
