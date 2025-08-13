import { Component, For, createEffect } from 'solid-js';
import type { ActivityLogEntry } from '../types';

interface ActivityModalProps {
  activities: () => ActivityLogEntry[];
  isOpen: () => boolean;
  onClose: () => void;
}

const ActivityModal: Component<ActivityModalProps> = (props) => {
  let modalRef: HTMLDialogElement | undefined;

  createEffect(() => {
    if (modalRef) {
      if (props.isOpen()) {
        modalRef.showModal();
      } else {
        modalRef.close();
      }
    }
  });

  const getIcon = (type: string) => {
    switch (type) {
      case 'tool':
        return '🔧';
      case 'error':
        return '❌';
      case 'browser':
        return '🌐';
      default:
        return 'ℹ️';
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'tool':
        return 'bg-blue-50 border-blue-200 text-blue-800';
      case 'error':
        return 'bg-red-50 border-red-200 text-red-800';
      case 'browser':
        return 'bg-green-50 border-green-200 text-green-800';
      default:
        return 'bg-gray-50 border-gray-200 text-gray-800';
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  return (
    <dialog 
      ref={modalRef}
      class="modal"
      onClick={(e) => {
        if (e.target === modalRef) {
          props.onClose();
        }
      }}
    >
      <div class="modal-box w-11/12 max-w-4xl h-[80vh] flex flex-col">
        {/* Header */}
        <div class="flex justify-between items-center pb-4 border-b border-base-300">
          <div class="flex items-center space-x-2">
            <span class="text-2xl">🔍</span>
            <h2 class="text-xl font-bold">Activity Log</h2>
          </div>
          <button 
            class="btn btn-sm btn-circle btn-ghost"
            onClick={() => props.onClose()}
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Stats Summary */}
        <div class="stats shadow w-full my-4">
          <div class="stat">
            <div class="stat-title text-xs">Total Activities</div>
            <div class="stat-value text-lg">{props.activities().length}</div>
          </div>
          <div class="stat">
            <div class="stat-title text-xs">Tools Used</div>
            <div class="stat-value text-lg">
              {props.activities().filter(a => a.type === 'tool').length}
            </div>
          </div>
          <div class="stat">
            <div class="stat-title text-xs">Browser Actions</div>
            <div class="stat-value text-lg">
              {props.activities().filter(a => a.type === 'browser').length}
            </div>
          </div>
          <div class="stat">
            <div class="stat-title text-xs">Errors</div>
            <div class="stat-value text-lg">
              {props.activities().filter(a => a.type === 'error').length}
            </div>
          </div>
        </div>

        {/* Activities List */}
        <div class="flex-1 overflow-y-auto scrollbar-thin pr-2">
          {props.activities().length === 0 ? (
            <div class="text-center text-base-content/60 py-8">
              <div class="mb-4">
                <svg class="w-16 h-16 mx-auto opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <p class="font-medium text-lg">No activities yet</p>
              <p class="text-sm mt-2">Agent actions and events will appear here as they happen</p>
            </div>
          ) : (
            <div class="space-y-3">
              <For each={props.activities()}>
                {(activity) => (
                  <div class={`card card-compact bg-base-200 shadow-sm border-l-4 ${
                    activity.type === 'tool' ? 'border-l-blue-500' :
                    activity.type === 'error' ? 'border-l-red-500' :
                    activity.type === 'browser' ? 'border-l-green-500' :
                    'border-l-gray-400'
                  }`}>
                    <div class="card-body">
                      <div class="flex items-start space-x-3">
                        <span class="text-lg flex-shrink-0 mt-0.5">
                          {getIcon(activity.type)}
                        </span>
                        <div class="flex-1 min-w-0">
                          <div class="text-sm font-medium break-words">
                            {activity.message}
                          </div>
                          <div class="flex items-center justify-between mt-2">
                            <span class={`badge badge-sm ${
                              activity.type === 'tool' ? 'badge-info' :
                              activity.type === 'error' ? 'badge-error' :
                              activity.type === 'browser' ? 'badge-success' :
                              'badge-ghost'
                            }`}>
                              {activity.type}
                            </span>
                            <span class="text-xs opacity-60">
                              {formatTime(activity.timestamp)}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </For>
            </div>
          )}
        </div>

        {/* Footer */}
        <div class="modal-action">
          <button class="btn btn-primary" onClick={() => props.onClose()}>
            Close
          </button>
        </div>
      </div>
    </dialog>
  );
};

export default ActivityModal;
