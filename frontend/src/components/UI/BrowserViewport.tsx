import { Component } from 'solid-js';
import type { BrowserState } from '../../types';

interface BrowserViewportProps {
  browserState: () => BrowserState;
}

const BrowserViewport: Component<BrowserViewportProps> = props => {
  return (
    <div class='h-full flex flex-col bg-base-100 border border-base-300 rounded-lg'>
      <div class='bg-base-200 px-4 py-2 border-b border-base-300 flex items-center gap-2'>
        <div class='text-sm font-medium'>Browser Viewport</div>
        <div
          class={`badge badge-sm ${
            props.browserState().status === 'Active'
              ? 'badge-success'
              : props.browserState().status === 'Idle'
              ? 'badge-neutral'
              : 'badge-warning'
          }`}
        >
          {props.browserState().status}
        </div>
      </div>

      <div class='flex-1 p-4 overflow-y-auto'>
        <div class='text-xs text-base-content/60 mb-2'>URL: {props.browserState().url}</div>
        <div class='text-sm whitespace-pre-wrap'>{props.browserState().content}</div>
      </div>
    </div>
  );
};

export default BrowserViewport;
