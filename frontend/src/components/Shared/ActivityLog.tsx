import { Component, For } from 'solid-js';
import type { ActivityLogEntry } from '../../types';

interface ActivityLogProps {
  activities: () => ActivityLogEntry[];
}

const ActivityLog: Component<ActivityLogProps> = props => {
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

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  return (
    <div class='card bg-base-100 shadow-xl h-full flex flex-col'>
      <div class='card-header bg-info text-info-content p-2 rounded-t-xl'>
        <div class='flex items-center space-x-2'>
          <span class='text-xl'>🔍</span>
          <h2 class='card-title'>Activity Log</h2>
        </div>
      </div>

      <div class='flex-1 p-2 overflow-y-auto scrollbar-thin min-h-0' style='max-height: 300px;'>
        {props.activities().length === 0 ? (
          <div class='text-center text-base-content/60 py-2'>
            <div class='mb-4'>
              <svg
                class='w-12 h-12 mx-auto opacity-50'
                fill='none'
                stroke='currentColor'
                viewBox='0 0 24 24'
              >
                <path
                  stroke-linecap='round'
                  stroke-linejoin='round'
                  stroke-width='2'
                  d='M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z'
                />
              </svg>
            </div>
            <p class='font-medium'>No activity yet</p>
            <p class='text-sm mt-1'>Agent actions will appear here</p>
          </div>
        ) : (
          <div class='space-y-2'>
            <For each={props.activities()}>
              {activity => (
                <div class={`activity-item ${activity.type} p-2 rounded-lg`}>
                  <div class='flex items-start space-x-2'>
                    <span class='text-sm flex-shrink-0 mt-0.5'>{getIcon(activity.type)}</span>
                    <div class='flex-1 min-w-0'>
                      <div class='text-sm break-words'>{activity.message}</div>
                      <div class='text-xs opacity-60 mt-1'>[{formatTime(activity.timestamp)}]</div>
                    </div>
                  </div>
                </div>
              )}
            </For>
          </div>
        )}
      </div>

      {props.activities().length > 0 && (
        <div class='p-2 border-t border-base-200'>
          <div class='stats shadow w-full'>
            <div class='stat'>
              <div class='stat-title text-xs'>Total Activities</div>
              <div class='stat-value text-lg'>{props.activities().length}</div>
            </div>
            <div class='stat'>
              <div class='stat-title text-xs'>Tools Used</div>
              <div class='stat-value text-lg'>
                {props.activities().filter(a => a.type === 'tool').length}
              </div>
            </div>
            <div class='stat'>
              <div class='stat-title text-xs'>Errors</div>
              <div class='stat-value text-lg'>
                {props.activities().filter(a => a.type === 'error').length}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ActivityLog;
