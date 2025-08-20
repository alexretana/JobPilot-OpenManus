import { createSignal, createEffect, For, Show } from 'solid-js';
import type { TimelineEvent } from '../../../../types';
import { TimelineEventType } from '../../../../types';
import { timelineApi } from '../../../../services/timelineApi';
import { TimelineEventCard } from '../../../Timeline/TimelineEventCard';

interface ApplicationTimelineProps {
  applicationId: string;
  jobTitle?: string;
  companyName?: string;
  className?: string;
  compact?: boolean;
}

export function ApplicationTimeline(props: ApplicationTimelineProps) {
  const [events, setEvents] = createSignal<TimelineEvent[]>([]);
  const [loading, setLoading] = createSignal(true);
  const [error, setError] = createSignal<string | null>(null);

  // Load timeline events for this application
  const loadApplicationTimeline = async () => {
    try {
      setLoading(true);
      setError(null);

      const appEvents = await timelineApi.getApplicationTimeline(props.applicationId, {
        limit: 50,
      });

      setEvents(appEvents);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load application timeline');
    } finally {
      setLoading(false);
    }
  };

  createEffect(() => {
    loadApplicationTimeline();
  });

  const handleEventDeleted = (eventId: string) => {
    setEvents(events().filter(e => e.id !== eventId));
  };

  const handleEventUpdated = () => {
    loadApplicationTimeline(); // Refresh the timeline
  };

  // Get application status from latest status change event
  const getApplicationStatus = () => {
    const statusEvents = events().filter(e => e.event_type === TimelineEventType.STATUS_CHANGED);
    if (statusEvents.length > 0) {
      // Get the most recent status change
      const latestStatus = statusEvents.sort(
        (a, b) => new Date(b.event_date).getTime() - new Date(a.event_date).getTime()
      )[0];
      return latestStatus.event_data.new_status || 'Unknown';
    }

    // Infer status from event types
    if (events().some(e => e.event_type === TimelineEventType.OFFER_ACCEPTED))
      return 'Offer Accepted';
    if (events().some(e => e.event_type === TimelineEventType.OFFER_DECLINED))
      return 'Offer Declined';
    if (events().some(e => e.event_type === TimelineEventType.OFFER_RECEIVED))
      return 'Offer Received';
    if (events().some(e => e.event_type === TimelineEventType.INTERVIEW_COMPLETED))
      return 'Interview Completed';
    if (events().some(e => e.event_type === TimelineEventType.INTERVIEW_SCHEDULED))
      return 'Interview Scheduled';
    if (events().some(e => e.event_type === TimelineEventType.APPLICATION_SUBMITTED))
      return 'Applied';

    return 'Unknown';
  };

  // Get status badge styling
  const getStatusStyle = (status: string) => {
    const lowerStatus = status.toLowerCase();
    if (lowerStatus.includes('accepted') || lowerStatus.includes('hired')) return 'badge-success';
    if (lowerStatus.includes('declined') || lowerStatus.includes('rejected')) return 'badge-error';
    if (lowerStatus.includes('offer')) return 'badge-success';
    if (lowerStatus.includes('interview')) return 'badge-warning';
    if (lowerStatus.includes('applied') || lowerStatus.includes('submitted'))
      return 'badge-primary';
    return 'badge-neutral';
  };

  if (loading()) {
    return (
      <div class={`application-timeline ${props.className || ''}`}>
        <div class='flex justify-center py-12'>
          <span class='loading loading-spinner loading-lg'></span>
        </div>
      </div>
    );
  }

  if (error()) {
    return (
      <div class={`application-timeline ${props.className || ''}`}>
        <div class='alert alert-error'>
          <svg
            xmlns='http://www.w3.org/2000/svg'
            class='stroke-current shrink-0 h-6 w-6'
            fill='none'
            viewBox='0 0 24 24'
          >
            <path
              stroke-linecap='round'
              stroke-linejoin='round'
              stroke-width='2'
              d='M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z'
            />
          </svg>
          <span>{error()}</span>
          <div>
            <button class='btn btn-sm btn-outline' onClick={loadApplicationTimeline}>
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div class={`application-timeline ${props.className || ''}`}>
      {/* Header */}
      <Show when={!props.compact}>
        <div class='mb-6'>
          <div class='flex items-start justify-between gap-4'>
            <div>
              <h2 class='text-xl font-bold text-base-content'>Application Timeline</h2>
              <Show when={props.jobTitle || props.companyName}>
                <p class='text-sm text-base-content/70 mt-1'>
                  <Show when={props.jobTitle}>
                    <span class='font-medium'>{props.jobTitle}</span>
                  </Show>
                  <Show when={props.companyName}>
                    <span>
                      {props.jobTitle ? ' at ' : ''}
                      {props.companyName}
                    </span>
                  </Show>
                </p>
              </Show>
            </div>

            {/* Application Status */}
            <Show when={events().length > 0}>
              <div class='text-right'>
                <div class='text-sm text-base-content/60 mb-1'>Current Status</div>
                <div class={`badge ${getStatusStyle(getApplicationStatus())} badge-lg`}>
                  {getApplicationStatus()}
                </div>
              </div>
            </Show>
          </div>

          {/* Application ID */}
          <div class='text-xs text-base-content/50 mt-2'>Application ID: {props.applicationId}</div>
        </div>
      </Show>

      {/* Timeline Events */}
      <Show
        when={events().length > 0}
        fallback={
          <div class='text-center py-12'>
            <div class='text-6xl mb-4'>📋</div>
            <h3 class='text-lg font-medium text-base-content/70 mb-2'>No Timeline Events</h3>
            <p class='text-sm text-base-content/50'>
              This application doesn't have any timeline events yet.
            </p>
          </div>
        }
      >
        <div class={props.compact ? 'space-y-2' : 'space-y-4'}>
          <For each={events()}>
            {event => (
              <div class={props.compact ? 'scale-95' : ''}>
                <TimelineEventCard
                  event={event}
                  onDelete={handleEventDeleted}
                  onUpdate={handleEventUpdated}
                />
              </div>
            )}
          </For>
        </div>

        {/* Timeline Stats */}
        <Show when={!props.compact && events().length > 0}>
          <div class='stats shadow mt-6'>
            <div class='stat'>
              <div class='stat-title'>Total Events</div>
              <div class='stat-value text-primary'>{events().length}</div>
            </div>

            <div class='stat'>
              <div class='stat-title'>Milestones</div>
              <div class='stat-value text-secondary'>
                {events().filter(e => e.is_milestone).length}
              </div>
            </div>

            <div class='stat'>
              <div class='stat-title'>Latest Activity</div>
              <div class='stat-value text-xs'>
                {events().length > 0
                  ? new Date(
                      events().sort(
                        (a, b) =>
                          new Date(b.event_date).getTime() - new Date(a.event_date).getTime()
                      )[0].event_date
                    ).toLocaleDateString()
                  : 'N/A'}
              </div>
            </div>
          </div>
        </Show>
      </Show>
    </div>
  );
}
