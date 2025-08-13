import { Component, createSignal, onMount } from 'solid-js';

const Header: Component = () => {
  const [currentTheme, setCurrentTheme] = createSignal('corporate');

  const themes = [
    'light', 'dark', 'cupcake', 'bumblebee', 'emerald', 'corporate',
    'synthwave', 'retro', 'cyberpunk', 'valentine', 'halloween', 'garden',
    'forest', 'aqua', 'lofi', 'pastel', 'fantasy', 'wireframe', 'black',
    'luxury', 'dracula', 'cmyk', 'autumn', 'business', 'acid', 'lemonade',
    'night', 'coffee', 'winter'
  ];

  onMount(() => {
    const savedTheme = localStorage.getItem('theme') || 'corporate';
    setCurrentTheme(savedTheme);
    document.documentElement.setAttribute('data-theme', savedTheme);
  });

  const changeTheme = (theme: string) => {
    setCurrentTheme(theme);
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
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
      
      <div class="navbar-end">
        <div class="dropdown dropdown-end">
          <div tabindex="0" role="button" class="btn btn-ghost">
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
