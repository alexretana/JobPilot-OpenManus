import { Component } from 'solid-js';
import type { ActivityLogEntry } from '../../types';

interface TimelineModalProps {
  activities: () => ActivityLogEntry[];
  isOpen: () => boolean;
  onClose: () => void;
  userProfileId: string;
}

const TimelineModal: Component<TimelineModalProps> = props => {
  if (!props.isOpen()) return null;

  return (
    <div class='modal modal-open'>
      <div class='modal-box max-w-4xl'>
        <div class='flex justify-between items-center mb-4'>
          <h3 class='text-lg font-bold'>Activity Timeline</h3>
          <button class='btn btn-ghost btn-sm' onClick={props.onClose}>
            ✕
          </button>
        </div>

        <div class='space-y-2 max-h-96 overflow-y-auto'>
          {props.activities().map(activity => (
            <div class='card bg-base-100 shadow-sm border'>
              <div class='card-body p-3'>
                <div class='flex justify-between items-start'>
                  <div>
                    <div
                      class={`badge badge-sm ${
                        activity.type === 'error'
                          ? 'badge-error'
                          : activity.type === 'tool'
                          ? 'badge-info'
                          : activity.type === 'browser'
                          ? 'badge-warning'
                          : 'badge-neutral'
                      }`}
                    >
                      {activity.type}
                    </div>
                    <p class='text-sm mt-1'>{activity.message}</p>
                  </div>
                  <div class='text-xs text-base-content/60'>
                    {activity.timestamp.toLocaleTimeString()}
                  </div>
                </div>
              </div>
            </div>
          ))}

          {props.activities().length === 0 && (
            <div class='text-center py-8 text-base-content/60'>No activities yet</div>
          )}
        </div>

        <div class='modal-action'>
          <button class='btn' onClick={props.onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default TimelineModal;
