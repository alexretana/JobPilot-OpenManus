import { Component, createSignal, onMount } from 'solid-js';
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
  const [currentTheme, setCurrentTheme] = createSignal('business');
  const themes = [
    { name: 'business', label: 'Business' },
    { name: 'dark', label: 'Dark' },
    { name: 'dim', label: 'Dim' },
    { name: 'emerald', label: 'Emerald' },
    { name: 'lemonade', label: 'Lemonade' },
    { name: 'nord', label: 'Nord' },
  ];

  const changeTheme = (theme: string) => {
    setCurrentTheme(theme);
    document.documentElement.setAttribute('data-theme', theme);
    // Save to localStorage to persist between sessions
    localStorage.setItem('jobpilot-theme', theme);
  };

  // Load saved theme on mount
  onMount(() => {
    const savedTheme = localStorage.getItem('jobpilot-theme') || 'business';
    setCurrentTheme(savedTheme);
    document.documentElement.setAttribute('data-theme', savedTheme);
  });

  return (
    <div class='navbar bg-base-300 border-b border-base-content/10 px-4'>
      <div class='navbar-start flex items-center gap-3'>
        <img src='/JobPilotIcon-Alpha.png' alt='JobPilot Icon' class='w-8 h-8' />
        <h1 class='text-xl font-bold text-primary text-ai-gradient'>JobPilot</h1>
      </div>

      <div class='navbar-center'>
        <div class='tabs tabs-boxed'>
          <button
            class={`tab ${
              props.activeTab() === 'chat' ? 'tab-active bg-ai-color-gradient text-white' : ''
            }`}
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

      <div class='navbar-end'>
        <div class='dropdown dropdown-end'>
          <div tabindex='0' role='button' class='btn btn-ghost btn-sm'>
            Theme
            <svg
              width='12px'
              height='12px'
              class='inline-block h-2 w-2 fill-current opacity-60'
              xmlns='http://www.w3.org/2000/svg'
              viewBox='0 0 2048 2048'
            >
              <path d='M1799 349l242 241-1017 1017L7 590l242-241 775 775 775-775z'></path>
            </svg>
          </div>
          <ul
            tabindex='0'
            class='dropdown-content bg-base-300 rounded-box z-[1] w-52 p-2 shadow-2xl'
          >
            {themes.map(theme => (
              <li>
                <input
                  type='radio'
                  name='theme-dropdown'
                  class='theme-controller btn btn-sm btn-block btn-ghost justify-start'
                  aria-label={theme.label}
                  value={theme.name}
                  checked={currentTheme() === theme.name}
                  onChange={() => changeTheme(theme.name)}
                />
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Header;
