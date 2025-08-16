import { Component } from 'solid-js';
import type { BrowserState } from '../types';

interface BrowserViewportProps {
  browserState: () => BrowserState;
}

const BrowserViewport: Component<BrowserViewportProps> = props => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Active':
      case 'Browsing':
        return 'badge-success';
      case 'Initializing':
        return 'badge-warning';
      default:
        return 'badge-ghost';
    }
  };

  const formatContent = (content: string) => {
    if (!content || content === 'Waiting for browser activity...') {
      return content;
    }

    // Truncate content and add ellipsis
    return content.length > 1000 ? content.substring(0, 1000) + '...' : content;
  };

  return (
    <div class='card bg-base-100 shadow-xl h-full flex flex-col'>
      <div class='card-header bg-neutral text-neutral-content p-2 rounded-t-xl'>
        <div class='flex justify-between items-center w-full'>
          <div class='flex items-center space-x-2'>
            <span class='text-xl'>🌐</span>
            <h2 class='card-title'>Browser Viewport (Live)</h2>
          </div>
          <div class={`badge ${getStatusColor(props.browserState().status)}`}>
            {props.browserState().status}
          </div>
        </div>
      </div>

      <div class='p-2 border-b border-base-200'>
        <div class='mockup-browser bg-base-300 border'>
          <div class='mockup-browser-toolbar'>
            <div class='input border border-base-300 bg-base-100'>
              {props.browserState().url || 'No active browsing session'}
            </div>
          </div>
        </div>
      </div>

      <div class='flex-1 p-2 min-h-0'>
        <div
          class={`h-full rounded-lg ${
            props.browserState().status === 'Active' || props.browserState().status === 'Browsing'
              ? 'bg-base-100 border-2 border-dashed border-base-300'
              : 'bg-base-200 flex items-center justify-center'
          }`}
        >
          {props.browserState().status === 'Active' ||
          props.browserState().status === 'Browsing' ? (
            <div class='p-2 h-full overflow-auto scrollbar-thin'>
              <pre class='text-xs whitespace-pre-wrap font-mono break-words'>
                {formatContent(props.browserState().content)}
              </pre>
            </div>
          ) : (
            <div class='text-center text-base-content/60'>
              <div class='mb-4'>
                <svg
                  class='w-16 h-16 mx-auto opacity-50'
                  fill='none'
                  stroke='currentColor'
                  viewBox='0 0 24 24'
                >
                  <path
                    stroke-linecap='round'
                    stroke-linejoin='round'
                    stroke-width='2'
                    d='M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 0l-3-3m3 3l-3 3'
                  />
                </svg>
              </div>
              <p class='font-medium'>Waiting for browser activity...</p>
              <p class='text-sm mt-2'>
                When JobPilot starts browsing job sites,
                <br />
                you'll see the live content here.
              </p>
            </div>
          )}
        </div>
      </div>

      {props.browserState().status === 'Browsing' && (
        <div class='p-2 border-t border-base-200'>
          <div class='flex items-center space-x-2 text-sm'>
            <span class='loading loading-dots loading-sm'></span>
            <span>JobPilot is actively browsing and analyzing this page...</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default BrowserViewport;
