import { Component, createSignal, onMount, onCleanup } from 'solid-js';
import { apiService } from '../services/api';
import { webSocketService } from '../services/websocket';
import type { HealthCheckResponse } from '../types';

interface StatusPanelProps {
  onQuickAction: (query: string) => void;
  isProcessing: () => boolean;
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
    <div class="card bg-base-100 shadow-xl h-full flex flex-col">
      <div class="card-header bg-success text-success-content p-4 rounded-t-xl">
        <div class="flex items-center space-x-2">
          <span class="text-xl">⚡</span>
          <h2 class="card-title">System Status</h2>
        </div>
      </div>
      
      <div class="p-4 space-y-4">
        {/* System Status */}
        <div class="stats shadow w-full">
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

        {/* Detailed Status */}
        <div class="card bg-base-200 p-3">
          <div class="text-sm space-y-2">
            <div class="flex justify-between">
              <span>🟢 Status:</span>
              <span class="font-medium">{health() ? 'Healthy' : 'Checking...'}</span>
            </div>
            <div class="flex justify-between">
              <span>🧠 Service:</span>
              <span class="font-medium">{health()?.service || 'JobPilot-OpenManus'}</span>
            </div>
            <div class="flex justify-between">
              <span>🔧 Tools:</span>
              <span class="font-medium">Job Search, Browser, Analysis</span>
            </div>
            <div class="flex justify-between">
              <span>🖥️ Browser:</span>
              <span class="font-medium">Non-headless (Visible)</span>
            </div>
            <div class="flex justify-between">
              <span>🕒 Last Check:</span>
              <span class="font-medium">{formatTime(lastHealthCheck())}</span>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div>
          <div class="text-sm font-medium mb-3 flex items-center">
            <span class="mr-2">🎯</span>
            Quick Actions
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {quickActions.map((action) => (
              <button
                class={`btn btn-sm ${action.color} btn-outline normal-case`}
                onClick={() => props.onQuickAction(action.query)}
                disabled={props.isProcessing()}
                title={action.query}
              >
                <span class="mr-1">{action.icon}</span>
                {action.label}
              </button>
            ))}
          </div>
        </div>

        {/* Additional Actions */}
        <div class="divider text-xs">Actions</div>
        <div class="join w-full">
          <button 
            class="btn btn-outline btn-sm join-item flex-1"
            onClick={checkHealth}
            disabled={props.isProcessing()}
          >
            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh
          </button>
          <button 
            class="btn btn-outline btn-sm join-item flex-1"
            onClick={() => webSocketService.connect()}
            disabled={webSocketService.getIsConnected()()}
          >
            <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0" />
            </svg>
            Reconnect
          </button>
        </div>
      </div>
    </div>
  );
};

export default StatusPanel;
