import { createSignal, Show, createEffect } from 'solid-js';
import { TimelineEventType } from '../types';
import { timelineApi } from '../services/timelineApi';

interface CreateEventModalProps {
  userProfileId: string;
  onClose: () => void;
  onEventCreated: () => void;
}

export function CreateEventModal(props: CreateEventModalProps) {
  const [eventType, setEventType] = createSignal<TimelineEventType>(TimelineEventType.CUSTOM_EVENT);
  const [title, setTitle] = createSignal('');
  const [description, setDescription] = createSignal('');
  const [jobId, setJobId] = createSignal('');
  const [applicationId, setApplicationId] = createSignal('');
  const [eventDate, setEventDate] = createSignal('');
  const [isMilestone, setIsMilestone] = createSignal(false);
  const [isSubmitting, setIsSubmitting] = createSignal(false);
  const [errors, setErrors] = createSignal<Record<string, string>>({});

  // Set default event date to now
  createEffect(() => {
    if (!eventDate()) {
      const now = new Date();
      // Format for datetime-local input
      const year = now.getFullYear();
      const month = String(now.getMonth() + 1).padStart(2, '0');
      const day = String(now.getDate()).padStart(2, '0');
      const hours = String(now.getHours()).padStart(2, '0');
      const minutes = String(now.getMinutes()).padStart(2, '0');
      setEventDate(`${year}-${month}-${day}T${hours}:${minutes}`);
    }
  });

  // Auto-generate titles based on event type
  const suggestTitle = (type: TimelineEventType) => {
    switch (type) {
      case TimelineEventType.JOB_SAVED:
        return 'Saved interesting job position';
      case TimelineEventType.APPLICATION_SUBMITTED:
        return 'Submitted job application';
      case TimelineEventType.INTERVIEW_SCHEDULED:
        return 'Interview scheduled';
      case TimelineEventType.INTERVIEW_COMPLETED:
        return 'Completed interview';
      case TimelineEventType.STATUS_CHANGED:
        return 'Application status updated';
      case TimelineEventType.OFFER_RECEIVED:
        return 'Received job offer';
      case TimelineEventType.OFFER_ACCEPTED:
        return 'Accepted job offer';
      case TimelineEventType.OFFER_DECLINED:
        return 'Declined job offer';
      case TimelineEventType.CUSTOM_EVENT:
        return 'Custom timeline event';
      default:
        return '';
    }
  };

  // Update title when event type changes (if title is empty or default)
  createEffect(() => {
    const currentTitle = title().trim();
    const suggested = suggestTitle(eventType());

    if (!currentTitle || Object.values(TimelineEventType).some(type =>
      currentTitle === suggestTitle(type)
    )) {
      setTitle(suggested);
    }
  });

  // Auto-set milestone for certain event types
  createEffect(() => {
    const milestoneTypes: TimelineEventType[] = [
      TimelineEventType.APPLICATION_SUBMITTED,
      TimelineEventType.INTERVIEW_SCHEDULED,
      TimelineEventType.INTERVIEW_COMPLETED,
      TimelineEventType.OFFER_RECEIVED,
      TimelineEventType.OFFER_ACCEPTED,
      TimelineEventType.OFFER_DECLINED
    ];

    setIsMilestone(milestoneTypes.includes(eventType()));
  });

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!title().trim()) {
      newErrors.title = 'Title is required';
    }

    if (!eventDate()) {
      newErrors.eventDate = 'Event date is required';
    }

    // Validate job-related fields for certain event types
    const jobRelatedTypes = ['JOB_SAVED', 'APPLICATION_SUBMITTED', 'INTERVIEW_SCHEDULED', 'INTERVIEW_COMPLETED', 'STATUS_CHANGED'];
    if (jobRelatedTypes.includes(eventType()) && !jobId().trim()) {
      newErrors.jobId = 'Job ID is required for this event type';
    }

    // Validate application-related fields
    const appRelatedTypes = ['APPLICATION_SUBMITTED', 'INTERVIEW_SCHEDULED', 'INTERVIEW_COMPLETED', 'STATUS_CHANGED', 'OFFER_RECEIVED', 'OFFER_ACCEPTED', 'OFFER_DECLINED'];
    if (appRelatedTypes.includes(eventType()) && !applicationId().trim()) {
      newErrors.applicationId = 'Application ID is required for this event type';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: Event) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);

    try {
      await timelineApi.createCustomEvent(props.userProfileId, {
        title: title().trim(),
        description: description().trim() || undefined,
        job_id: jobId().trim() || undefined,
        application_id: applicationId().trim() || undefined,
        event_date: eventDate() || undefined,
        is_milestone: isMilestone(),
      });

      props.onEventCreated();
    } catch (error) {
      alert('Failed to create event: ' + (error instanceof Error ? error.message : 'Unknown error'));
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    if (isSubmitting()) return;
    props.onClose();
  };

  const getEventTypeOptions = () => [
    { value: 'CUSTOM_EVENT', label: '📝 Custom Event' },
    { value: 'JOB_SAVED', label: '💾 Job Saved' },
    { value: 'APPLICATION_SUBMITTED', label: '📤 Application Submitted' },
    { value: 'INTERVIEW_SCHEDULED', label: '📅 Interview Scheduled' },
    { value: 'INTERVIEW_COMPLETED', label: '✅ Interview Completed' },
    { value: 'STATUS_CHANGED', label: '🔄 Status Changed' },
    { value: 'OFFER_RECEIVED', label: '🎉 Offer Received' },
    { value: 'OFFER_ACCEPTED', label: '🎊 Offer Accepted' },
    { value: 'OFFER_DECLINED', label: '❌ Offer Declined' },
  ];

  return (
    <div class="modal modal-open">
      <div class="modal-box w-11/12 max-w-2xl">
        <form onSubmit={handleSubmit}>
          {/* Header */}
          <div class="flex justify-between items-start mb-6">
            <div>
              <h3 class="font-bold text-lg">Create Timeline Event</h3>
              <p class="text-sm text-base-content/70 mt-1">
                Add a new event to your job search timeline
              </p>
            </div>
            <button
              type="button"
              class="btn btn-sm btn-circle btn-ghost"
              onClick={handleClose}
              disabled={isSubmitting()}
            >
              ✕
            </button>
          </div>

          <div class="space-y-4">
            {/* Event Type */}
            <div class="form-control">
              <label class="label">
                <span class="label-text font-medium">Event Type</span>
              </label>
              <select
                class={`select select-bordered ${errors().eventType ? 'select-error' : ''}`}
                value={eventType()}
                onChange={(e) => setEventType(e.currentTarget.value as TimelineEventType)}
                disabled={isSubmitting()}
              >
                {getEventTypeOptions().map(option => (
                  <option value={option.value}>{option.label}</option>
                ))}
              </select>
              <Show when={errors().eventType}>
                <label class="label">
                  <span class="label-text-alt text-error">{errors().eventType}</span>
                </label>
              </Show>
            </div>

            {/* Title */}
            <div class="form-control">
              <label class="label">
                <span class="label-text font-medium">Title*</span>
              </label>
              <input
                type="text"
                class={`input input-bordered ${errors().title ? 'input-error' : ''}`}
                value={title()}
                onInput={(e) => setTitle(e.currentTarget.value)}
                placeholder="Enter event title..."
                disabled={isSubmitting()}
              />
              <Show when={errors().title}>
                <label class="label">
                  <span class="label-text-alt text-error">{errors().title}</span>
                </label>
              </Show>
            </div>

            {/* Description */}
            <div class="form-control">
              <label class="label">
                <span class="label-text font-medium">Description</span>
              </label>
              <textarea
                class="textarea textarea-bordered h-20"
                value={description()}
                onInput={(e) => setDescription(e.currentTarget.value)}
                placeholder="Optional description or notes..."
                disabled={isSubmitting()}
              />
            </div>

            {/* Event Date */}
            <div class="form-control">
              <label class="label">
                <span class="label-text font-medium">Event Date*</span>
              </label>
              <input
                type="datetime-local"
                class={`input input-bordered ${errors().eventDate ? 'input-error' : ''}`}
                value={eventDate()}
                onInput={(e) => setEventDate(e.currentTarget.value)}
                disabled={isSubmitting()}
              />
              <Show when={errors().eventDate}>
                <label class="label">
                  <span class="label-text-alt text-error">{errors().eventDate}</span>
                </label>
              </Show>
            </div>

            {/* Job ID - shown for job-related events */}
            <Show when={['JOB_SAVED', 'APPLICATION_SUBMITTED', 'INTERVIEW_SCHEDULED', 'INTERVIEW_COMPLETED', 'STATUS_CHANGED'].includes(eventType())}>
              <div class="form-control">
                <label class="label">
                  <span class="label-text font-medium">Job ID</span>
                </label>
                <input
                  type="text"
                  class={`input input-bordered ${errors().jobId ? 'input-error' : ''}`}
                  value={jobId()}
                  onInput={(e) => setJobId(e.currentTarget.value)}
                  placeholder="Enter job ID (e.g., job_123)"
                  disabled={isSubmitting()}
                />
                <label class="label">
                  <span class="label-text-alt">Required for job-related events</span>
                </label>
                <Show when={errors().jobId}>
                  <label class="label">
                    <span class="label-text-alt text-error">{errors().jobId}</span>
                  </label>
                </Show>
              </div>
            </Show>

            {/* Application ID - shown for application-related events */}
            <Show when={['APPLICATION_SUBMITTED', 'INTERVIEW_SCHEDULED', 'INTERVIEW_COMPLETED', 'STATUS_CHANGED', 'OFFER_RECEIVED', 'OFFER_ACCEPTED', 'OFFER_DECLINED'].includes(eventType())}>
              <div class="form-control">
                <label class="label">
                  <span class="label-text font-medium">Application ID</span>
                </label>
                <input
                  type="text"
                  class={`input input-bordered ${errors().applicationId ? 'input-error' : ''}`}
                  value={applicationId()}
                  onInput={(e) => setApplicationId(e.currentTarget.value)}
                  placeholder="Enter application ID (e.g., app_456)"
                  disabled={isSubmitting()}
                />
                <label class="label">
                  <span class="label-text-alt">Required for application-related events</span>
                </label>
                <Show when={errors().applicationId}>
                  <label class="label">
                    <span class="label-text-alt text-error">{errors().applicationId}</span>
                  </label>
                </Show>
              </div>
            </Show>

            {/* Milestone Toggle */}
            <div class="form-control">
              <label class="label cursor-pointer justify-start gap-3">
                <input
                  type="checkbox"
                  class="checkbox checkbox-primary"
                  checked={isMilestone()}
                  onChange={(e) => setIsMilestone(e.currentTarget.checked)}
                  disabled={isSubmitting()}
                />
                <div>
                  <div class="label-text font-medium">Mark as milestone</div>
                  <div class="label-text-alt">Important events that represent significant progress</div>
                </div>
              </label>
            </div>
          </div>

          {/* Footer */}
          <div class="modal-action">
            <button
              type="button"
              class="btn btn-ghost"
              onClick={handleClose}
              disabled={isSubmitting()}
            >
              Cancel
            </button>
            <button
              type="submit"
              class="btn btn-primary"
              disabled={isSubmitting()}
            >
              <Show when={isSubmitting()}>
                <span class="loading loading-spinner loading-sm"></span>
              </Show>
              {isSubmitting() ? 'Creating...' : 'Create Event'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
