import { Component, createSignal, onMount, onCleanup } from 'solid-js';
import type { ActivityLogEntry } from '../types';

interface HeaderProps {
  activities?: () => ActivityLogEntry[];
  onShowActivityLog?: () => void;
  onShowStatusPanel?: () => void;
  systemHealthy?: () => boolean;
}

const Header: Component<HeaderProps> = (props) => {
  const [currentTheme, setCurrentTheme] = createSignal('corporate');
  const [isThemeDropdownOpen, setIsThemeDropdownOpen] = createSignal(false);
  let dropdownRef: HTMLDivElement | undefined;

  const themes = [
    'light', 'dark', 'cupcake', 'bumblebee', 'emerald', 'corporate',
    'synthwave', 'retro', 'cyberpunk', 'valentine', 'halloween', 'garden',
    'forest', 'aqua', 'lofi', 'pastel', 'fantasy', 'wireframe', 'black',
    'luxury', 'dracula', 'cmyk', 'autumn', 'business', 'acid', 'lemonade',
    'night', 'coffee', 'winter'
  ];

  // Handle click outside to close dropdown
  const handleClickOutside = (event: MouseEvent) => {
    if (dropdownRef && !dropdownRef.contains(event.target as Node) && isThemeDropdownOpen()) {
      setIsThemeDropdownOpen(false);
    }
  };

  onMount(() => {
    const savedTheme = localStorage.getItem('theme') || 'corporate';
    setCurrentTheme(savedTheme);
    // Set the theme on the document element
    document.documentElement.setAttribute('data-theme', savedTheme);
    
    // Add click outside listener
    document.addEventListener('click', handleClickOutside);
  });

  onCleanup(() => {
    document.removeEventListener('click', handleClickOutside);
  });

  const changeTheme = (theme: string) => {
    setCurrentTheme(theme);
    // Use DaisyUI's method: set data-theme on html element
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    
    // Close dropdown after selecting theme
    setIsThemeDropdownOpen(false);
    
    // Trigger a custom event to notify other components if needed
    window.dispatchEvent(new CustomEvent('themeChanged', { detail: theme }));
  };

  const toggleThemeDropdown = () => {
    setIsThemeDropdownOpen(!isThemeDropdownOpen());
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
        
        <div ref={dropdownRef} class={`dropdown dropdown-end ${isThemeDropdownOpen() ? 'dropdown-open' : ''}`}>
          <div tabindex="0" role="button" class="btn btn-ghost" onClick={toggleThemeDropdown}>
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zM21 5a2 2 0 00-2-2h-4a2 2 0 00-2 2v12a4 4 0 004 4h4a2 2 0 002-2V5z" />
            </svg>
            Theme
          </div>
          <ul tabindex="0" class="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-52 max-h-96 overflow-y-auto">
            {themes.map((theme) => (
              <li>
                <button 
                  class={`capitalize ${currentTheme() === theme ? 'active' : ''}`}
                  onClick={() => changeTheme(theme)}
                >
                  {theme}
                </button>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </header>
  );
};

export default Header;
