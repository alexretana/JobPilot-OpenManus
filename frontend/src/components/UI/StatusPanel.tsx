import { Component } from 'solid-js';

interface StatusPanelProps {
  onQuickAction: (action: string) => void;
  isProcessing: () => boolean;
  isOpen: () => boolean;
  onClose: () => void;
}

const StatusPanel: Component<StatusPanelProps> = props => {
  if (!props.isOpen()) return null;

  return (
    <div class='drawer drawer-end open'>
      <div class='drawer-overlay' onClick={props.onClose}></div>
      <div class='drawer-side'>
        <div class='min-h-full w-80 bg-base-200 p-4'>
          <div class='flex justify-between items-center mb-4'>
            <h3 class='text-lg font-bold'>Status Panel</h3>
            <button class='btn btn-ghost btn-sm' onClick={props.onClose}>
              ✕
            </button>
          </div>

          <div class='space-y-4'>
            <div class='card bg-base-100 shadow'>
              <div class='card-body p-4'>
                <h4 class='font-semibold'>System Status</h4>
                <div class={`badge ${props.isProcessing() ? 'badge-warning' : 'badge-success'}`}>
                  {props.isProcessing() ? 'Processing' : 'Ready'}
                </div>
              </div>
            </div>

            <div class='card bg-base-100 shadow'>
              <div class='card-body p-4'>
                <h4 class='font-semibold mb-2'>Quick Actions</h4>
                <div class='space-y-2'>
                  <button
                    class='btn btn-sm w-full'
                    onClick={() => props.onQuickAction('search for jobs')}
                    disabled={props.isProcessing()}
                  >
                    Search Jobs
                  </button>
                  <button
                    class='btn btn-sm w-full'
                    onClick={() => props.onQuickAction('help me with my resume')}
                    disabled={props.isProcessing()}
                  >
                    Resume Help
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StatusPanel;
