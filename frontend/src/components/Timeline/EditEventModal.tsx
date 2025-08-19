import { createSignal, Show, createEffect } from 'solid-js';
import type { TimelineEvent } from '../../types';
import { TimelineEventType } from '../../types';
import { timelineApi } from '../../services/timelineApi';

interface EditEventModalProps {
  event: TimelineEvent;
  onClose: () => void;
  onEventUpdated: () => void;
}

export function EditEventModal(props: EditEventModalProps) {
  const [eventType] = createSignal<TimelineEventType>(props.event.event_type);
  const [title, setTitle] = createSignal(props.event.title);
  const [description, setDescription] = createSignal(props.event.description || '');
  const [eventDate, setEventDate] = createSignal('');
  const [isMilestone, setIsMilestone] = createSignal(props.event.is_milestone);
  const [isSubmitting, setIsSubmitting] = createSignal(false);
  const [errors, setErrors] = createSignal<Record<string, string>>({});

  // Initialize event date from the existing event
  createEffect(() => {
    const date = new Date(props.event.event_date);
    // Format for datetime-local input
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    setEventDate(`${year}-${month}-${day}T${hours}:${minutes}`);
  });

  // Auto-set milestone for certain event types
  createEffect(() => {
    if (eventType() !== props.event.event_type) {
      const milestoneTypes: TimelineEventType[] = [
        TimelineEventType.APPLICATION_SUBMITTED,
        TimelineEventType.INTERVIEW_SCHEDULED,
        TimelineEventType.INTERVIEW_COMPLETED,
        TimelineEventType.OFFER_RECEIVED,
        TimelineEventType.OFFER_ACCEPTED,
        TimelineEventType.OFFER_DECLINED,
      ];

      setIsMilestone(milestoneTypes.includes(eventType()));
    }
  });

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!title().trim()) {
      newErrors.title = 'Title is required';
    }

    if (!eventDate()) {
      newErrors.eventDate = 'Event date is required';
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
      await timelineApi.updateTimelineEvent(props.event.id, {
        title: title().trim(),
        description: description().trim() || undefined,
        event_date: eventDate() || undefined,
        is_milestone: isMilestone(),
        // Note: We don't allow changing event_data, job_id, or application_id in edit
        // as these are typically set when the event is created
      });

      props.onEventUpdated();
    } catch (error) {
      alert(
        'Failed to update event: ' + (error instanceof Error ? error.message : 'Unknown error')
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    if (isSubmitting()) return;
    props.onClose();
  };

  const getEventTypeOptions = () => [
    { value: TimelineEventType.CUSTOM_EVENT, label: '📝 Custom Event' },
    { value: TimelineEventType.JOB_SAVED, label: '💾 Job Saved' },
    { value: TimelineEventType.APPLICATION_SUBMITTED, label: '📤 Application Submitted' },
    { value: TimelineEventType.INTERVIEW_SCHEDULED, label: '📅 Interview Scheduled' },
    { value: TimelineEventType.INTERVIEW_COMPLETED, label: '✅ Interview Completed' },
    { value: TimelineEventType.STATUS_CHANGED, label: '🔄 Status Changed' },
    { value: TimelineEventType.OFFER_RECEIVED, label: '🎉 Offer Received' },
    { value: TimelineEventType.OFFER_ACCEPTED, label: '🎊 Offer Accepted' },
    { value: TimelineEventType.OFFER_DECLINED, label: '❌ Offer Declined' },
  ];

  const hasChanges = () => {
    return (
      eventType() !== props.event.event_type ||
      title() !== props.event.title ||
      description() !== (props.event.description || '') ||
      isMilestone() !== props.event.is_milestone ||
      eventDate() !== '' // Always consider changed if date is set
    );
  };

  return (
    <div class='modal modal-open'>
      <div class='modal-box w-11/12 max-w-2xl'>
        <form onSubmit={handleSubmit}>
          {/* Header */}
          <div class='flex justify-between items-start mb-6'>
            <div>
              <h3 class='font-bold text-lg'>Edit Timeline Event</h3>
              <p class='text-sm text-base-content/70 mt-1'>Update your job search timeline event</p>
            </div>
            <button
              type='button'
              class='btn btn-sm btn-circle btn-ghost'
              onClick={handleClose}
              disabled={isSubmitting()}
            >
              ✕
            </button>
          </div>

          <div class='space-y-4'>
            {/* Event Type - Disabled for editing to maintain data integrity */}
            <div class='form-control'>
              <label class='label'>
                <span class='label-text font-medium'>Event Type</span>
              </label>
              <select
                class='select select-bordered select-disabled'
                value={eventType()}
                disabled={true}
              >
                {getEventTypeOptions().map(option => (
                  <option value={option.value} selected={option.value === eventType()}>
                    {option.label}
                  </option>
                ))}
              </select>
              <label class='label'>
                <span class='label-text-alt'>Event type cannot be changed after creation</span>
              </label>
            </div>

            {/* Title */}
            <div class='form-control'>
              <label class='label'>
                <span class='label-text font-medium'>Title*</span>
              </label>
              <input
                type='text'
                class={`input input-bordered ${errors().title ? 'input-error' : ''}`}
                value={title()}
                onInput={e => setTitle(e.currentTarget.value)}
                placeholder='Enter event title...'
                disabled={isSubmitting()}
              />
              <Show when={errors().title}>
                <label class='label'>
                  <span class='label-text-alt text-error'>{errors().title}</span>
                </label>
              </Show>
            </div>

            {/* Description */}
            <div class='form-control'>
              <label class='label'>
                <span class='label-text font-medium'>Description</span>
              </label>
              <textarea
                class='textarea textarea-bordered h-20'
                value={description()}
                onInput={e => setDescription(e.currentTarget.value)}
                placeholder='Optional description or notes...'
                disabled={isSubmitting()}
              />
            </div>

            {/* Event Date */}
            <div class='form-control'>
              <label class='label'>
                <span class='label-text font-medium'>Event Date*</span>
              </label>
              <input
                type='datetime-local'
                class={`input input-bordered ${errors().eventDate ? 'input-error' : ''}`}
                value={eventDate()}
                onInput={e => setEventDate(e.currentTarget.value)}
                disabled={isSubmitting()}
              />
              <Show when={errors().eventDate}>
                <label class='label'>
                  <span class='label-text-alt text-error'>{errors().eventDate}</span>
                </label>
              </Show>
            </div>

            {/* Job ID and Application ID - Show as read-only info */}
            <Show when={props.event.job_id || props.event.application_id}>
              <div class='bg-base-200 rounded-lg p-4'>
                <h4 class='text-sm font-medium text-base-content/80 mb-2'>Linked Resources</h4>
                <div class='space-y-2 text-xs'>
                  <Show when={props.event.job_id}>
                    <div>
                      <span class='font-medium'>Job ID:</span> {props.event.job_id}
                    </div>
                  </Show>
                  <Show when={props.event.application_id}>
                    <div>
                      <span class='font-medium'>Application ID:</span> {props.event.application_id}
                    </div>
                  </Show>
                </div>
                <div class='text-xs text-base-content/60 mt-2'>
                  Linked resources cannot be changed after event creation
                </div>
              </div>
            </Show>

            {/* Milestone Toggle */}
            <div class='form-control'>
              <label class='label cursor-pointer justify-start gap-3'>
                <input
                  type='checkbox'
                  class='checkbox checkbox-primary'
                  checked={isMilestone()}
                  onChange={e => setIsMilestone(e.currentTarget.checked)}
                  disabled={isSubmitting()}
                />
                <div>
                  <div class='label-text font-medium'>Mark as milestone</div>
                  <div class='label-text-alt'>
                    Important events that represent significant progress
                  </div>
                </div>
              </label>
            </div>

            {/* Show changes indicator */}
            <Show when={hasChanges()}>
              <div class='alert alert-info'>
                <svg
                  xmlns='http://www.w3.org/2000/svg'
                  fill='none'
                  viewBox='0 0 24 24'
                  class='stroke-current shrink-0 w-6 h-6'
                >
                  <path
                    stroke-linecap='round'
                    stroke-linejoin='round'
                    stroke-width='2'
                    d='M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
                  ></path>
                </svg>
                <span>You have unsaved changes</span>
              </div>
            </Show>
          </div>

          {/* Footer */}
          <div class='modal-action'>
            <button
              type='button'
              class='btn btn-ghost'
              onClick={handleClose}
              disabled={isSubmitting()}
            >
              Cancel
            </button>
            <button
              type='submit'
              class='btn btn-primary'
              disabled={isSubmitting() || !hasChanges()}
            >
              <Show when={isSubmitting()}>
                <span class='loading loading-spinner loading-sm'></span>
              </Show>
              {isSubmitting() ? 'Updating...' : 'Update Event'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
