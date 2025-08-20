import { Component } from 'solid-js';
import type { TimelineEvent } from '../../types';

interface TimelineEventCardProps {
  event: TimelineEvent;
  onDelete?: (eventId: string) => void;
  onUpdate?: () => void;
}

export const TimelineEventCard: Component<TimelineEventCardProps> = props => {
  return (
    <div class='card bg-base-100 shadow-sm border border-base-300 mb-2'>
      <div class='card-body p-4'>
        <div class='flex justify-between items-start'>
          <div>
            <h4 class='font-semibold'>{props.event.title}</h4>
            <p class='text-sm text-base-content/70 mt-1'>{props.event.description}</p>
            <p class='text-xs text-base-content/60 mt-2'>
              {new Date(props.event.event_date).toLocaleDateString()}
            </p>
          </div>
          {props.onDelete && (
            <button
              class='btn btn-ghost btn-xs text-error'
              onClick={() => props.onDelete?.(props.event.id)}
            >
              Delete
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default TimelineEventCard;
