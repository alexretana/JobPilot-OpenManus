import { Component, createSignal, createEffect, For, Show } from 'solid-js';
import type { TimelineEvent, ActivityLogEntry } from '../types';
import { TimelineEventType } from '../types';
import { timelineApi } from '../services/timelineApi';
import { TimelineEventCard } from './TimelineEventCard';
import { CreateEventModal } from './CreateEventModal';

interface TimelineModalProps {
  activities: () => ActivityLogEntry[];
  isOpen: () => boolean;
  onClose: () => void;
  userProfileId?: string;
  className?: string;
}

type TimelineTab = 'timeline' | 'milestones' | 'upcoming' | 'system-logs';

export const TimelineModal: Component<TimelineModalProps> = props => {
  let modalRef: HTMLDialogElement | undefined;

  // Timeline state
  const [events, setEvents] = createSignal<TimelineEvent[]>([]);
  const [milestones, setMilestones] = createSignal<TimelineEvent[]>([]);
  const [upcomingEvents, setUpcomingEvents] = createSignal<TimelineEvent[]>([]);
  const [loading, setLoading] = createSignal(true);
  const [error, setError] = createSignal<string | null>(null);
  const [activeTab, setActiveTab] = createSignal<TimelineTab>('timeline');
  const [showCreateModal, setShowCreateModal] = createSignal(false);
  const [filterDays, setFilterDays] = createSignal<number>(30);
  const [selectedEventTypes] = createSignal<TimelineEventType[]>([]);

  const userProfileId = () => props.userProfileId || 'demo-user-123';

  // Modal management
  createEffect(() => {
    if (modalRef) {
      if (props.isOpen()) {
        modalRef.showModal();
      } else {
        modalRef.close();
      }
    }
  });

  // Load timeline data
  const loadTimelineData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [timelineEvents, milestoneEvents, upcomingEventsData] = await Promise.all([
        timelineApi.getUserTimeline(userProfileId(), {
          limit: 50,
          days_back: filterDays(),
          event_types: selectedEventTypes().length > 0 ? selectedEventTypes() : undefined,
        }),
        timelineApi.getUserMilestones(userProfileId(), {
          limit: 20,
          days_back: 90,
        }),
        timelineApi.getUpcomingEvents(userProfileId(), {
          days_ahead: 14,
          limit: 10,
        }),
      ]);

      setEvents(timelineEvents);
      setMilestones(milestoneEvents);
      setUpcomingEvents(upcomingEventsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load timeline data');
    } finally {
      setLoading(false);
    }
  };

  // Load data when modal opens
  createEffect(() => {
    if (props.isOpen()) {
      loadTimelineData();
    }
  });

  createEffect(() => {
    // Reload when filters change
    if (props.isOpen() && (filterDays() || selectedEventTypes().length >= 0)) {
      loadTimelineData();
    }
  });

  const handleEventCreated = () => {
    setShowCreateModal(false);
    loadTimelineData(); // Refresh the timeline
  };

  const handleEventDeleted = (eventId: string) => {
    // Remove the event from the current view
    setEvents(events().filter(e => e.id !== eventId));
    setMilestones(milestones().filter(e => e.id !== eventId));
    setUpcomingEvents(upcomingEvents().filter(e => e.id !== eventId));
  };

  const getCurrentEvents = () => {
    switch (activeTab()) {
      case 'milestones':
        return milestones();
      case 'upcoming':
        return upcomingEvents();
      case 'timeline':
        return events();
      case 'system-logs':
        return []; // System logs don't use timeline events
      default:
        return events();
    }
  };

  const getEmptyMessage = () => {
    switch (activeTab()) {
      case 'milestones':
        return 'No milestones found';
      case 'upcoming':
        return 'No upcoming events';
      case 'system-logs':
        return 'No system activities found';
      default:
        return 'No timeline events found';
    }
  };

  // System Logs tab utilities
  const getActivityIcon = (type: string) => {
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
    <dialog
      ref={modalRef}
      class='modal'
      onClick={e => {
        if (e.target === modalRef) {
          props.onClose();
        }
      }}
    >
      <div class='modal-box w-11/12 max-w-6xl h-[85vh] flex flex-col'>
        {/* Header */}
        <div class='flex justify-between items-center pb-4 border-b border-base-300'>
          <div class='flex items-center space-x-3'>
            <span class='text-2xl'>📅</span>
            <div>
              <h2 class='text-2xl font-bold text-base-content'>Timeline</h2>
              <p class='text-sm text-base-content/70'>
                Track your job search progress, milestones, and system activity
              </p>
            </div>
          </div>

          <div class='flex items-center gap-2'>
            <Show when={activeTab() === 'timeline'}>
              {/* Filter Controls */}
              <div class='dropdown dropdown-end'>
                <div tabindex={0} role='button' class='btn btn-outline btn-sm'>
                  <svg
                    xmlns='http://www.w3.org/2000/svg'
                    class='h-4 w-4'
                    fill='none'
                    viewBox='0 0 24 24'
                    stroke='currentColor'
                  >
                    <path
                      stroke-linecap='round'
                      stroke-linejoin='round'
                      stroke-width='2'
                      d='M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707v4.586l-4-2v-2.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z'
                    />
                  </svg>
                  Filters
                </div>
                <div
                  tabindex={0}
                  class='dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-80'
                >
                  <div class='form-control'>
                    <label class='label'>
                      <span class='label-text'>Time Range</span>
                    </label>
                    <select
                      class='select select-bordered select-sm'
                      value={filterDays()}
                      onChange={e => setFilterDays(parseInt(e.currentTarget.value))}
                    >
                      <option value={7}>Last 7 days</option>
                      <option value={30}>Last 30 days</option>
                      <option value={90}>Last 90 days</option>
                      <option value={365}>Last year</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Create Event Button */}
              <button class='btn btn-primary btn-sm' onClick={() => setShowCreateModal(true)}>
                <svg
                  xmlns='http://www.w3.org/2000/svg'
                  class='h-4 w-4'
                  fill='none'
                  viewBox='0 0 24 24'
                  stroke='currentColor'
                >
                  <path
                    stroke-linecap='round'
                    stroke-linejoin='round'
                    stroke-width='2'
                    d='M12 4v16m8-8H4'
                  />
                </svg>
                Add Event
              </button>
            </Show>

            <button class='btn btn-sm btn-circle btn-ghost' onClick={() => props.onClose()}>
              <svg class='w-5 h-5' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
                <path
                  stroke-linecap='round'
                  stroke-linejoin='round'
                  stroke-width='2'
                  d='M6 18L18 6M6 6l12 12'
                />
              </svg>
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div class='flex-shrink-0 py-4'>
          <div class='tabs tabs-boxed justify-start'>
            <button
              class={`tab tab-lg gap-2 ${activeTab() === 'timeline' ? 'tab-active' : ''}`}
              onClick={() => setActiveTab('timeline')}
            >
              <svg
                xmlns='http://www.w3.org/2000/svg'
                class='h-4 w-4'
                fill='none'
                viewBox='0 0 24 24'
                stroke='currentColor'
              >
                <path
                  stroke-linecap='round'
                  stroke-linejoin='round'
                  stroke-width='2'
                  d='M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z'
                />
              </svg>
              Timeline ({events().length})
            </button>
            <button
              class={`tab tab-lg gap-2 ${activeTab() === 'milestones' ? 'tab-active' : ''}`}
              onClick={() => setActiveTab('milestones')}
            >
              <svg
                xmlns='http://www.w3.org/2000/svg'
                class='h-4 w-4'
                fill='none'
                viewBox='0 0 24 24'
                stroke='currentColor'
              >
                <path
                  stroke-linecap='round'
                  stroke-linejoin='round'
                  stroke-width='2'
                  d='M5 3l14 9-14 9V3z'
                />
              </svg>
              Milestones ({milestones().length})
            </button>
            <button
              class={`tab tab-lg gap-2 ${activeTab() === 'upcoming' ? 'tab-active' : ''}`}
              onClick={() => setActiveTab('upcoming')}
            >
              <svg
                xmlns='http://www.w3.org/2000/svg'
                class='h-4 w-4'
                fill='none'
                viewBox='0 0 24 24'
                stroke='currentColor'
              >
                <path
                  stroke-linecap='round'
                  stroke-linejoin='round'
                  stroke-width='2'
                  d='M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
                />
              </svg>
              Upcoming ({upcomingEvents().length})
            </button>
            <button
              class={`tab tab-lg gap-2 ${activeTab() === 'system-logs' ? 'tab-active' : ''}`}
              onClick={() => setActiveTab('system-logs')}
            >
              <svg
                xmlns='http://www.w3.org/2000/svg'
                class='h-4 w-4'
                fill='none'
                viewBox='0 0 24 24'
                stroke='currentColor'
              >
                <path
                  stroke-linecap='round'
                  stroke-linejoin='round'
                  stroke-width='2'
                  d='M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z'
                />
              </svg>
              System Logs ({props.activities().length})
            </button>
          </div>
        </div>

        {/* Content */}
        <div class='flex-1 overflow-y-auto'>
          <Show when={activeTab() === 'system-logs'}>
            {/* System Logs Content */}
            <div class='space-y-4'>
              {/* Stats Summary for System Logs */}
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
                  <div class='stat-title text-xs'>Browser Actions</div>
                  <div class='stat-value text-lg'>
                    {props.activities().filter(a => a.type === 'browser').length}
                  </div>
                </div>
                <div class='stat'>
                  <div class='stat-title text-xs'>Errors</div>
                  <div class='stat-value text-lg'>
                    {props.activities().filter(a => a.type === 'error').length}
                  </div>
                </div>
              </div>

              {/* System Activities List */}
              <div class='space-y-3'>
                <Show
                  when={props.activities().length > 0}
                  fallback={
                    <div class='text-center text-base-content/60 py-8'>
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
                            d='M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z'
                          />
                        </svg>
                      </div>
                      <p class='font-medium text-lg'>No system activities yet</p>
                      <p class='text-sm mt-2'>
                        Agent actions and events will appear here as they happen
                      </p>
                    </div>
                  }
                >
                  <For each={props.activities()}>
                    {activity => (
                      <div
                        class={`card card-compact bg-base-200 shadow-sm border-l-4 ${
                          activity.type === 'tool'
                            ? 'border-l-blue-500'
                            : activity.type === 'error'
                            ? 'border-l-red-500'
                            : activity.type === 'browser'
                            ? 'border-l-green-500'
                            : 'border-l-gray-400'
                        }`}
                      >
                        <div class='card-body'>
                          <div class='flex items-start space-x-3'>
                            <span class='text-lg flex-shrink-0 mt-0.5'>
                              {getActivityIcon(activity.type)}
                            </span>
                            <div class='flex-1 min-w-0'>
                              <div class='text-sm font-medium break-words'>{activity.message}</div>
                              <div class='flex items-center justify-between mt-2'>
                                <span
                                  class={`badge badge-sm ${
                                    activity.type === 'tool'
                                      ? 'badge-info'
                                      : activity.type === 'error'
                                      ? 'badge-error'
                                      : activity.type === 'browser'
                                      ? 'badge-success'
                                      : 'badge-ghost'
                                  }`}
                                >
                                  {activity.type}
                                </span>
                                <span class='text-xs opacity-60'>
                                  {formatTime(activity.timestamp)}
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </For>
                </Show>
              </div>
            </div>
          </Show>

          <Show when={activeTab() !== 'system-logs'}>
            {/* Timeline Content */}
            <Show when={loading()}>
              <div class='flex justify-center py-12'>
                <span class='loading loading-spinner loading-lg'></span>
              </div>
            </Show>

            <Show when={error()}>
              <div class='alert alert-error mb-6'>
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
                  <button class='btn btn-sm btn-outline' onClick={loadTimelineData}>
                    Retry
                  </button>
                </div>
              </div>
            </Show>

            <Show when={!loading() && !error()}>
              <Show
                when={getCurrentEvents().length > 0}
                fallback={
                  <div class='text-center py-12'>
                    <div class='text-6xl mb-4'>📅</div>
                    <h3 class='text-lg font-medium text-base-content/70 mb-2'>
                      {getEmptyMessage()}
                    </h3>
                    <p class='text-sm text-base-content/50 mb-4'>
                      {activeTab() === 'timeline'
                        ? 'Start tracking your job search by creating your first timeline event!'
                        : activeTab() === 'milestones'
                        ? 'Milestones will appear here as you reach important job search goals.'
                        : 'Upcoming interviews and events will be shown here.'}
                    </p>
                    <Show when={activeTab() === 'timeline'}>
                      <button
                        class='btn btn-primary btn-sm'
                        onClick={() => setShowCreateModal(true)}
                      >
                        Create First Event
                      </button>
                    </Show>
                  </div>
                }
              >
                <div class='space-y-4'>
                  <For each={getCurrentEvents()}>
                    {event => (
                      <TimelineEventCard
                        event={event}
                        onDelete={handleEventDeleted}
                        onUpdate={loadTimelineData}
                      />
                    )}
                  </For>
                </div>
              </Show>
            </Show>
          </Show>
        </div>

        {/* Modal Footer */}
        <div class='modal-action pt-4 border-t border-base-300'>
          <button class='btn btn-primary' onClick={() => props.onClose()}>
            Close
          </button>
        </div>
      </div>

      {/* Create Event Modal */}
      <Show when={showCreateModal()}>
        <CreateEventModal
          userProfileId={userProfileId()}
          onClose={() => setShowCreateModal(false)}
          onEventCreated={handleEventCreated}
        />
      </Show>
    </dialog>
  );
};

export default TimelineModal;
