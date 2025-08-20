import { Component } from 'solid-js';
import type { ActivityLogEntry } from '../../types';

interface HeaderProps {
  activities: () => ActivityLogEntry[];
  onShowTimeline: () => void;
  onShowStatusPanel: () => void;
  systemHealthy: () => boolean;
  activeTab: () => 'chat' | 'job-search' | 'resume-builder';
  onTabChange: (tab: 'chat' | 'job-search' | 'resume-builder') => void;
}

const Header: Component<HeaderProps> = props => {
  return (
    <div class='navbar bg-base-300 border-b border-base-content/10 px-4'>
      <div class='navbar-start'>
        <h1 class='text-xl font-bold text-primary'>JobPilot</h1>
      </div>

      <div class='navbar-center'>
        <div class='tabs tabs-boxed'>
          <button
            class={`tab ${props.activeTab() === 'chat' ? 'tab-active' : ''}`}
            onClick={() => props.onTabChange('chat')}
          >
            AI Chat
          </button>
          <button
            class={`tab ${props.activeTab() === 'job-search' ? 'tab-active' : ''}`}
            onClick={() => props.onTabChange('job-search')}
          >
            Job Search
          </button>
          <button
            class={`tab ${props.activeTab() === 'resume-builder' ? 'tab-active' : ''}`}
            onClick={() => props.onTabChange('resume-builder')}
          >
            Resume Builder
          </button>
        </div>
      </div>

      <div class='navbar-end gap-2'>
        <button class='btn btn-ghost btn-sm' onClick={props.onShowTimeline}>
          Timeline
        </button>
        <button class='btn btn-ghost btn-sm' onClick={props.onShowStatusPanel}>
          Status
        </button>
        <div class={`badge ${props.systemHealthy() ? 'badge-success' : 'badge-error'}`}>
          {props.systemHealthy() ? 'Online' : 'Offline'}
        </div>
      </div>
    </div>
  );
};

export default Header;
