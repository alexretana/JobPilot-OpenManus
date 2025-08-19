import { Component, For, Show } from 'solid-js';

export interface BreadcrumbItem {
  label: string;
  href?: string;
  onClick?: () => void;
  isActive?: boolean;
  icon?: string;
}

interface BreadcrumbProps {
  items: BreadcrumbItem[];
  className?: string;
  separator?: string;
  showHome?: boolean;
  homeLabel?: string;
  onHomeClick?: () => void;
}

export const Breadcrumb: Component<BreadcrumbProps> = props => {
  const separator = () => props.separator || '>';
  const showHome = () => props.showHome !== false; // Default to true
  const homeLabel = () => props.homeLabel || 'Home';

  const handleItemClick = (item: BreadcrumbItem, event: Event) => {
    if (item.onClick) {
      event.preventDefault();
      item.onClick();
    }
  };

  const renderBreadcrumbItem = (item: BreadcrumbItem, index: number) => {
    const isLast = index === props.items.length - 1;
    const isActive = item.isActive || isLast;

    return (
      <div class='flex items-center'>
        <Show when={index > 0 || showHome()}>
          <span class='mx-2 text-base-content/40 select-none'>{separator()}</span>
        </Show>

        <div class='flex items-center'>
          <Show when={item.icon}>
            <span class='mr-1 text-sm'>{item.icon}</span>
          </Show>

          <Show
            when={!isActive && (item.href || item.onClick)}
            fallback={
              <span
                class={`text-sm font-medium ${
                  isActive ? 'text-base-content' : 'text-base-content/60'
                }`}
              >
                {item.label}
              </span>
            }
          >
            <Show
              when={item.href}
              fallback={
                <button
                  class='text-sm font-medium text-primary hover:text-primary/80 hover:underline transition-colors'
                  onClick={e => handleItemClick(item, e)}
                >
                  {item.label}
                </button>
              }
            >
              <a
                href={item.href}
                class='text-sm font-medium text-primary hover:text-primary/80 hover:underline transition-colors'
                onClick={e => handleItemClick(item, e)}
              >
                {item.label}
              </a>
            </Show>
          </Show>
        </div>
      </div>
    );
  };

  return (
    <nav
      class={`breadcrumb flex items-center py-2 text-sm ${props.className || ''}`}
      aria-label='Breadcrumb navigation'
    >
      <div class='flex items-center flex-wrap'>
        <Show when={showHome()}>
          <div class='flex items-center'>
            <Show
              when={props.onHomeClick}
              fallback={
                <span class='text-sm font-medium text-base-content/60 flex items-center'>
                  <svg
                    xmlns='http://www.w3.org/2000/svg'
                    class='h-4 w-4 mr-1'
                    fill='none'
                    viewBox='0 0 24 24'
                    stroke='currentColor'
                  >
                    <path
                      stroke-linecap='round'
                      stroke-linejoin='round'
                      stroke-width='2'
                      d='M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6'
                    />
                  </svg>
                  {homeLabel()}
                </span>
              }
            >
              <button
                class='text-sm font-medium text-primary hover:text-primary/80 hover:underline transition-colors flex items-center'
                onClick={() => props.onHomeClick?.()}
              >
                <svg
                  xmlns='http://www.w3.org/2000/svg'
                  class='h-4 w-4 mr-1'
                  fill='none'
                  viewBox='0 0 24 24'
                  stroke='currentColor'
                >
                  <path
                    stroke-linecap='round'
                    stroke-linejoin='round'
                    stroke-width='2'
                    d='M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6'
                  />
                </svg>
                {homeLabel()}
              </button>
            </Show>
          </div>
        </Show>

        <For each={props.items}>{(item, index) => renderBreadcrumbItem(item, index())}</For>
      </div>
    </nav>
  );
};

export default Breadcrumb;
