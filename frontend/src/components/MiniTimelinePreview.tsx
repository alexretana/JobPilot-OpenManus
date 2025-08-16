import { createSignal, createEffect, For, Show } from 'solid-js';
import type { TimelineEvent } from '../types';
import { TimelineEventType } from '../types';
import { timelineApi } from '../services/timelineApi';

interface MiniTimelinePreviewProps {
  jobId: string;
  userProfileId: string;
  maxEvents?: number;
  className?: string;
}

export function MiniTimelinePreview(props: MiniTimelinePreviewProps) {
  const [events, setEvents] = createSignal<TimelineEvent[]>([]);
  const [loading, setLoading] = createSignal(true);
  const [error, setError] = createSignal<string | null>(null);

  const maxEvents = () => props.maxEvents || 3;

  // Load timeline events for this job
  const loadJobTimeline = async () => {
    try {
      setLoading(true);
      setError(null);

      const jobEvents = await timelineApi.getJobTimeline(props.jobId, {
        user_profile_id: props.userProfileId,
        limit: maxEvents(),
      });

      setEvents(jobEvents);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load timeline');
    } finally {
      setLoading(false);
    }
  };

  createEffect(() => {
    loadJobTimeline();
  });

  // Get event type icon (smaller versions)
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

  // Format relative time (shorter format for mini preview)
  const formatRelativeTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 0) {
      return 'Today';
    } else if (diffDays === 1) {
      return 'Yesterday';
    } else if (diffDays < 7) {
      return `${diffDays}d ago`;
    } else if (diffDays < 30) {
      return `${Math.floor(diffDays / 7)}w ago`;
    } else {
      return `${Math.floor(diffDays / 30)}m ago`;
    }
  };

  if (loading()) {
    return (
      <div class={`mini-timeline-preview ${props.className || ''}`}>
        <div class='flex items-center gap-2 text-xs text-base-content/60'>
          <span class='loading loading-spinner loading-xs'></span>
          <span>Loading timeline...</span>
        </div>
      </div>
    );
  }

  if (error()) {
    return (
      <div class={`mini-timeline-preview ${props.className || ''}`}>
        <div class='text-xs text-error'>Timeline unavailable</div>
      </div>
    );
  }

  if (events().length === 0) {
    return (
      <div class={`mini-timeline-preview ${props.className || ''}`}>
        <div class='text-xs text-base-content/50'>No timeline events</div>
      </div>
    );
  }

  return (
    <div class={`mini-timeline-preview ${props.className || ''}`}>
      <div class='space-y-1'>
        <For each={events().slice(0, maxEvents())}>
          {event => (
            <div class='flex items-center gap-2 text-xs'>
              {/* Event icon */}
              <span class='text-sm flex-shrink-0'>{getEventTypeIcon(event.event_type)}</span>

              {/* Event details */}
              <div class='flex-1 min-w-0'>
                <div class='flex items-center gap-1'>
                  <span class='truncate'>{event.title}</span>
                  <Show when={event.is_milestone}>
                    <div class='badge badge-primary badge-xs'>★</div>
                  </Show>
                </div>
              </div>

              {/* Time and status */}
              <div class='flex-shrink-0 flex items-center gap-1'>
                <span class='text-base-content/60'>{formatRelativeTime(event.event_date)}</span>
                <div class={`badge ${getEventTypeStyle(event.event_type)} badge-xs`}></div>
              </div>
            </div>
          )}
        </For>

        {/* Show count if there are more events */}
        <Show when={events().length > maxEvents()}>
          <div class='text-xs text-base-content/50 pt-1 border-t border-base-300'>
            +{events().length - maxEvents()} more events
          </div>
        </Show>
      </div>
    </div>
  );
}
