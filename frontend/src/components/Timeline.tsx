import { createSignal, createEffect, For, Show } from 'solid-js';
import type { TimelineEvent } from '../types';
import { TimelineEventType } from '../types';
import { timelineApi } from '../services/timelineApi';
import { TimelineEventCard } from './TimelineEventCard';
import { CreateEventModal } from './CreateEventModal';

interface TimelineProps {
  userProfileId: string;
  className?: string;
}

export function Timeline(props: TimelineProps) {
  const [events, setEvents] = createSignal<TimelineEvent[]>([]);
  const [milestones, setMilestones] = createSignal<TimelineEvent[]>([]);
  const [upcomingEvents, setUpcomingEvents] = createSignal<TimelineEvent[]>([]);
  const [loading, setLoading] = createSignal(true);
  const [error, setError] = createSignal<string | null>(null);
  const [activeTab, setActiveTab] = createSignal<'timeline' | 'milestones' | 'upcoming'>('timeline');
  const [showCreateModal, setShowCreateModal] = createSignal(false);
  const [filterDays, setFilterDays] = createSignal<number>(30);
  const [selectedEventTypes] = createSignal<TimelineEventType[]>([]);

  // Load timeline data
  const loadTimelineData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [timelineEvents, milestoneEvents, upcomingEventsData] = await Promise.all([
        timelineApi.getUserTimeline(props.userProfileId, {
          limit: 50,
          days_back: filterDays(),
          event_types: selectedEventTypes().length > 0 ? selectedEventTypes() : undefined,
        }),
        timelineApi.getUserMilestones(props.userProfileId, {
          limit: 20,
          days_back: 90,
        }),
        timelineApi.getUpcomingEvents(props.userProfileId, {
          days_ahead: 14,
          limit: 10,
        })
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

  // Load data on mount and when filters change
  createEffect(() => {
    loadTimelineData();
  });

  createEffect(() => {
    // Reload when filters change
    if (filterDays() || selectedEventTypes().length >= 0) {
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
      default:
        return 'No timeline events found';
    }
  };

  return (
    <div class={`timeline-container ${props.className || ''}`}>
      {/* Header */}
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <div>
          <h2 class="text-2xl font-bold text-base-content">Job Search Timeline</h2>
          <p class="text-sm text-base-content/70 mt-1">Track your job search progress and milestones</p>
        </div>

        <div class="flex flex-col sm:flex-row gap-2">
          {/* Filter Controls */}
          <div class="dropdown dropdown-end">
            <div tabindex={0} role="button" class="btn btn-outline btn-sm">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707v4.586l-4-2v-2.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
              </svg>
              Filters
            </div>
            <div tabindex={0} class="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-80">
              <div class="form-control">
                <label class="label">
                  <span class="label-text">Time Range</span>
                </label>
                <select
                  class="select select-bordered select-sm"
                  value={filterDays()}
                  onChange={(e) => setFilterDays(parseInt(e.currentTarget.value))}
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
          <button
            class="btn btn-primary btn-sm"
            onClick={() => setShowCreateModal(true)}
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            Add Event
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div class="tabs tabs-boxed mb-6">
        <button
          class={`tab ${activeTab() === 'timeline' ? 'tab-active' : ''}`}
          onClick={() => setActiveTab('timeline')}
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Timeline ({events().length})
        </button>
        <button
          class={`tab ${activeTab() === 'milestones' ? 'tab-active' : ''}`}
          onClick={() => setActiveTab('milestones')}
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3l14 9-14 9V3z" />
          </svg>
          Milestones ({milestones().length})
        </button>
        <button
          class={`tab ${activeTab() === 'upcoming' ? 'tab-active' : ''}`}
          onClick={() => setActiveTab('upcoming')}
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Upcoming ({upcomingEvents().length})
        </button>
      </div>

      {/* Content */}
      <Show when={loading()}>
        <div class="flex justify-center py-12">
          <span class="loading loading-spinner loading-lg"></span>
        </div>
      </Show>

      <Show when={error()}>
        <div class="alert alert-error mb-6">
          <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>{error()}</span>
          <div>
            <button class="btn btn-sm btn-outline" onClick={loadTimelineData}>
              Retry
            </button>
          </div>
        </div>
      </Show>

      <Show when={!loading() && !error()}>
        <Show
          when={getCurrentEvents().length > 0}
          fallback={
            <div class="text-center py-12">
              <div class="text-6xl mb-4">📅</div>
              <h3 class="text-lg font-medium text-base-content/70 mb-2">{getEmptyMessage()}</h3>
              <p class="text-sm text-base-content/50 mb-4">
                {activeTab() === 'timeline'
                  ? 'Start tracking your job search by creating your first timeline event!'
                  : activeTab() === 'milestones'
                  ? 'Milestones will appear here as you reach important job search goals.'
                  : 'Upcoming interviews and events will be shown here.'}
              </p>
              <Show when={activeTab() === 'timeline'}>
                <button
                  class="btn btn-primary btn-sm"
                  onClick={() => setShowCreateModal(true)}
                >
                  Create First Event
                </button>
              </Show>
            </div>
          }
        >
          <div class="space-y-4">
            <For each={getCurrentEvents()}>
              {(event) => (
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

      {/* Create Event Modal */}
      <Show when={showCreateModal()}>
        <CreateEventModal
          userProfileId={props.userProfileId}
          onClose={() => setShowCreateModal(false)}
          onEventCreated={handleEventCreated}
        />
      </Show>
    </div>
  );
}
