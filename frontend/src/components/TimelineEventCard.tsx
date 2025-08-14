import { createSignal, Show, For } from 'solid-js';
import type { TimelineEvent } from '../types';
import { TimelineEventType } from '../types';
import { timelineApi } from '../services/timelineApi';
import { EditEventModal } from './EditEventModal';

interface TimelineEventCardProps {
  event: TimelineEvent;
  onDelete: (eventId: string) => void;
  onUpdate: () => void;
}

export function TimelineEventCard(props: TimelineEventCardProps) {
  const [showDetails, setShowDetails] = createSignal(false);
  const [showEditModal, setShowEditModal] = createSignal(false);
  const [deleting, setDeleting] = createSignal(false);

  // Format date for display
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) {
      return `Today at ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
    } else if (diffDays === 1) {
      return `Yesterday at ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
    } else if (diffDays < 7) {
      return `${diffDays} days ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  // Get event type styling
  const getEventTypeStyle = (eventType: TimelineEventType) => {
    switch (eventType) {
      case TimelineEventType.JOB_SAVED:
        return 'badge-info';
      case TimelineEventType.APPLICATION_SUBMITTED:
        return 'badge-primary';
      case TimelineEventType.INTERVIEW_SCHEDULED:
        return 'badge-warning';
      case TimelineEventType.INTERVIEW_COMPLETED:
        return 'badge-warning';
      case TimelineEventType.STATUS_CHANGED:
        return 'badge-neutral';
      case TimelineEventType.OFFER_RECEIVED:
        return 'badge-success';
      case TimelineEventType.OFFER_ACCEPTED:
        return 'badge-success';
      case TimelineEventType.OFFER_DECLINED:
        return 'badge-error';
      case TimelineEventType.CUSTOM_EVENT:
        return 'badge-ghost';
      default:
        return 'badge-ghost';
    }
  };

  // Get event type icon
  const getEventTypeIcon = (eventType: TimelineEventType) => {
    switch (eventType) {
      case TimelineEventType.JOB_SAVED:
        return '💾';
      case TimelineEventType.APPLICATION_SUBMITTED:
        return '📤';
      case TimelineEventType.INTERVIEW_SCHEDULED:
        return '📅';
      case TimelineEventType.INTERVIEW_COMPLETED:
        return '✅';
      case TimelineEventType.STATUS_CHANGED:
        return '🔄';
      case TimelineEventType.OFFER_RECEIVED:
        return '🎉';
      case TimelineEventType.OFFER_ACCEPTED:
        return '🎊';
      case TimelineEventType.OFFER_DECLINED:
        return '❌';
      case TimelineEventType.CUSTOM_EVENT:
        return '📝';
      default:
        return '📋';
    }
  };

  // Format event type for display
  const formatEventType = (eventType: TimelineEventType) => {
    return eventType.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
    ).join(' ');
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this timeline event?')) {
      return;
    }

    try {
      setDeleting(true);
      await timelineApi.deleteTimelineEvent(props.event.id);
      props.onDelete(props.event.id);
    } catch (error) {
      alert('Failed to delete event: ' + (error instanceof Error ? error.message : 'Unknown error'));
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div class={`card bg-base-100 shadow-sm border border-base-300 hover:shadow-md transition-shadow ${props.event.is_milestone ? 'ring-2 ring-primary ring-opacity-20' : ''}`}>
      <div class="card-body p-4">
        {/* Header */}
        <div class="flex items-start justify-between gap-3">
          <div class="flex items-start gap-3 flex-1 min-w-0">
            {/* Icon */}
            <div class="text-2xl flex-shrink-0 mt-1">
              {getEventTypeIcon(props.event.event_type)}
            </div>
            
            {/* Content */}
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-1">
                <h3 class="font-medium text-base-content truncate">{props.event.title}</h3>
                <Show when={props.event.is_milestone}>
                  <div class="badge badge-primary badge-xs">milestone</div>
                </Show>
              </div>
              
              <div class="flex items-center gap-2 mb-2">
                <span class={`badge ${getEventTypeStyle(props.event.event_type)} badge-sm`}>
                  {formatEventType(props.event.event_type)}
                </span>
                <span class="text-xs text-base-content/60">
                  {formatDate(props.event.event_date)}
                </span>
              </div>

              <Show when={props.event.description}>
                <p class="text-sm text-base-content/70 mb-2 line-clamp-2">
                  {props.event.description}
                </p>
              </Show>

              {/* Job/Company Info from event_data */}
              <Show when={props.event.event_data.company_name || props.event.event_data.job_title}>
                <div class="text-xs text-base-content/60 mb-2">
                  <Show when={props.event.event_data.job_title}>
                    <span class="font-medium">{props.event.event_data.job_title}</span>
                  </Show>
                  <Show when={props.event.event_data.company_name}>
                    <span>
                      {props.event.event_data.job_title ? ' at ' : ''}
                      {props.event.event_data.company_name}
                    </span>
                  </Show>
                </div>
              </Show>
            </div>
          </div>

          {/* Actions */}
          <div class="dropdown dropdown-end">
            <div tabindex={0} role="button" class="btn btn-ghost btn-xs btn-circle">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
              </svg>
            </div>
            <ul tabindex={0} class="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-36">
              <li>
                <button 
                  class="text-xs"
                  onClick={() => setShowDetails(!showDetails())}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  {showDetails() ? 'Hide' : 'Show'} Details
                </button>
              </li>
              <li>
                <button 
                  class="text-xs"
                  onClick={() => setShowEditModal(true)}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                  Edit Event
                </button>
              </li>
              <div class="divider my-1"></div>
              <li>
                <button 
                  class="text-xs text-error"
                  onClick={handleDelete}
                  disabled={deleting()}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                  {deleting() ? 'Deleting...' : 'Delete'}
                </button>
              </li>
            </ul>
          </div>
        </div>

        {/* Expandable Details */}
        <Show when={showDetails()}>
          <div class="divider my-3"></div>
          <div class="space-y-3">
            {/* Event Data */}
            <Show when={Object.keys(props.event.event_data).length > 0}>
              <div>
                <h4 class="text-sm font-medium text-base-content/80 mb-2">Event Details</h4>
                <div class="bg-base-200 rounded-lg p-3 text-xs">
                  <For each={Object.entries(props.event.event_data)}>
                    {([key, value]) => (
                      <div class="flex justify-between py-1">
                        <span class="font-medium capitalize">
                          {key.replace(/_/g, ' ')}:
                        </span>
                        <span class="text-base-content/70">
                          {Array.isArray(value) ? value.join(', ') : String(value)}
                        </span>
                      </div>
                    )}
                  </For>
                </div>
              </div>
            </Show>

            {/* IDs for debugging/reference */}
            <div class="text-xs text-base-content/50 space-y-1">
              <div>Event ID: {props.event.id}</div>
              <Show when={props.event.job_id}>
                <div>Job ID: {props.event.job_id}</div>
              </Show>
              <Show when={props.event.application_id}>
                <div>Application ID: {props.event.application_id}</div>
              </Show>
              <div>Created: {new Date(props.event.created_at).toLocaleString()}</div>
              <Show when={props.event.created_at !== props.event.updated_at}>
                <div>Updated: {new Date(props.event.updated_at).toLocaleString()}</div>
              </Show>
            </div>
          </div>
        </Show>
      </div>

      {/* Edit Event Modal */}
      <Show when={showEditModal()}>
        <EditEventModal
          event={props.event}
          onClose={() => setShowEditModal(false)}
          onEventUpdated={() => {
            setShowEditModal(false);
            props.onUpdate();
          }}
        />
      </Show>
    </div>
  );
}
