import { Component, createSignal, onMount } from 'solid-js';
import type { ActivityLogEntry } from '../types';

interface HeaderProps {
  activities?: () => ActivityLogEntry[];
  onShowActivityLog?: () => void;
  onShowStatusPanel?: () => void;
  systemHealthy?: () => boolean;
}

const Header: Component<HeaderProps> = (props) => {
  const [currentTheme, setCurrentTheme] = createSignal('corporate');
  const themes = [
    { value: 'dark', label: 'Dark' },
    { value: 'emerald', label: 'Emerald' },
    { value: 'corporate', label: 'Corporate' },
    { value: 'business', label: 'Business' },
    { value: 'night', label: 'Night' },
    { value: 'lemonade', label: 'Lemonade' }
  ];

  onMount(() => {
    const savedTheme = localStorage.getItem('theme') || 'corporate';
    setCurrentTheme(savedTheme);
    // Set the theme on the document element
    document.documentElement.setAttribute('data-theme', savedTheme);
  });

  const changeTheme = (theme: string) => {
    setCurrentTheme(theme);
    // Use DaisyUI's method: set data-theme on html element
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);

    // Trigger a custom event to notify other components if needed
    window.dispatchEvent(new CustomEvent('themeChanged', { detail: theme }));
  };

  return (
    <header class="navbar bg-base-100 shadow-lg sticky top-0 z-50">
      <div class="navbar-start">
        <div class="dropdown">
          <div tabindex="0" role="button" class="btn btn-ghost lg:hidden">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h8m-8 6h16" />
            </svg>
          </div>
        </div>
        <div class="flex items-center space-x-2">
          <span class="text-2xl">🚀</span>
          <div>
            <div class="text-xl font-bold text-primary">JobPilot-OpenManus</div>
            <div class="text-sm opacity-70">AI-Powered Job Hunting Assistant</div>
          </div>
        </div>
      </div>

      <div class="navbar-center hidden lg:flex">
        <ul class="menu menu-horizontal px-1">
          <li><a class="text-base-content/70">Transparent AI Job Search</a></li>
        </ul>
      </div>

      <div class="navbar-end space-x-2">
        {/* Activity Log Notification Button */}
        <div class="indicator">
          {props.activities && props.activities().length > 0 && (
            <span class="indicator-item badge badge-primary badge-sm">
              {props.activities().length}
            </span>
          )}
          <button
            class="btn btn-ghost btn-circle"
            onClick={() => props.onShowActivityLog?.()}
            title="View Activity Log"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-5 5v-5zM4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>

        {/* Status Panel Button */}
        <button
          class="btn btn-ghost"
          onClick={() => props.onShowStatusPanel?.()}
          title="System Status & Quick Actions"
        >
          <div class="flex items-center space-x-2">
            <span class="text-lg">
              {props.systemHealthy?.() ? '🟢' : '🔴'}
            </span>
            <span class="text-sm font-medium">Status</span>
          </div>
        </button>

        {/* Theme Selector using DaisyUI template */}
        <div class="dropdown dropdown-end">
          <div tabindex="0" role="button" class="btn m-1">
            Theme
            <svg
              width="12px"
              height="12px"
              class="inline-block h-2 w-2 fill-current opacity-60"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 2048 2048"
            >
              <path d="M1799 349l242 241-1017 1017L7 590l242-241 775 775 775-775z"></path>
            </svg>
          </div>
          <ul tabindex="0" class="dropdown-content bg-base-300 rounded-box z-[1] w-52 p-2 shadow-2xl">
            {themes.map((theme) => (
              <li>
                <input
                  type="radio"
                  name="theme-dropdown"
                  class="theme-controller w-full btn btn-sm btn-block btn-ghost justify-start"
                  aria-label={theme.label}
                  value={theme.value}
                  checked={currentTheme() === theme.value}
                  onChange={(e) => {
                    if (e.currentTarget.checked) {
                      changeTheme(theme.value);
                    }
                  }}
                />
              </li>
            ))}
          </ul>
        </div>
      </div>
    </header>
  );
};

export default Header;
