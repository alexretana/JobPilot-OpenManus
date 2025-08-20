/**
 * Job Details Modal Component
 * Displays detailed job information in a modal dialog
 */

import { Component, createSignal, createEffect, Show, For } from 'solid-js';
import { jobApi, type JobDetails } from '../../../../services/jobApi';
import { ApplicationTimeline } from '../ApplicationsTab/ApplicationTimeline';

interface JobDetailsModalProps {
  jobId: string | null;
  isOpen: boolean;
  onClose: () => void;
}

export const JobDetailsModal: Component<JobDetailsModalProps> = props => {
  const [job, setJob] = createSignal<JobDetails | null>(null);
  const [loading, setLoading] = createSignal(false);
  const [error, setError] = createSignal<string | null>(null);
  const [isSaved, setIsSaved] = createSignal(false);
  const [saving, setSaving] = createSignal(false);
  const [activeTab, setActiveTab] = createSignal<'details' | 'timeline'>('details');

  // Load job details when jobId changes
  createEffect(() => {
    if (props.jobId && props.isOpen) {
      loadJobDetails(props.jobId);
    }
  });

  const loadJobDetails = async (jobId: string) => {
    try {
      setLoading(true);
      setError(null);
      const [jobDetails, savedStatus] = await Promise.all([
        jobApi.getJobDetails(jobId),
        checkIfJobSaved(jobId),
      ]);
      setJob(jobDetails);
      setIsSaved(savedStatus);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load job details';
      setError(errorMessage);
      console.error('Error loading job details:', err);
    } finally {
      setLoading(false);
    }
  };

  const checkIfJobSaved = async (jobId: string): Promise<boolean> => {
    try {
      return await jobApi.isJobSaved(jobId);
    } catch (err) {
      console.error('Error checking if job is saved:', err);
      return false;
    }
  };

  const handleSaveJob = async () => {
    const currentJob = job();
    if (!currentJob) return;

    try {
      setSaving(true);

      if (isSaved()) {
        // Unsave the job
        await jobApi.unsaveJob(currentJob.id);
        setIsSaved(false);
        console.log('Job unsaved successfully');
      } else {
        // Save the job
        await jobApi.saveJob({
          job_id: currentJob.id,
          notes: undefined,
          tags: [],
        });
        setIsSaved(true);
        console.log('Job saved successfully');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to save job';
      console.error('Error saving job:', err);
      // You could show a toast notification here
      alert(errorMessage);
    } finally {
      setSaving(false);
    }
  };

  const handleClose = () => {
    props.onClose();
    // Clear data after modal closes
    setTimeout(() => {
      setJob(null);
      setError(null);
      setActiveTab('details'); // Reset to details tab
    }, 300); // Wait for close animation
  };

  const handleBackdropClick = (e: MouseEvent) => {
    if (e.target === e.currentTarget) {
      handleClose();
    }
  };

  const formatSalary = (min?: number | null, max?: number | null, currency?: string | null) => {
    if (!min && !max) return null;
    const curr = currency || 'USD';
    if (min && max) {
      return `$${min.toLocaleString()} - $${max.toLocaleString()} ${curr}`;
    }
    if (min) return `$${min.toLocaleString()}+ ${curr}`;
    if (max) return `Up to $${max.toLocaleString()} ${curr}`;
    return null;
  };

  const formatDate = (dateString?: string | null) => {
    if (!dateString) return 'Not specified';
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      });
    } catch {
      return 'Invalid date';
    }
  };

  return (
    <Show when={props.isOpen}>
      <div
        class='fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-2'
        onClick={handleBackdropClick}
      >
        <div class='bg-base-100 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden'>
          {/* Modal Header */}
          <div class='flex items-center justify-between p-4 border-b border-base-300'>
            <h2 class='text-2xl font-bold text-base-content'>
              <Show when={!loading() && job()} fallback='Job Details'>
                {job()?.title}
              </Show>
            </h2>
            <button
              class='btn btn-ghost btn-sm btn-circle'
              onClick={handleClose}
              aria-label='Close modal'
            >
              <svg class='w-6 h-6' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
                <path
                  stroke-linecap='round'
                  stroke-linejoin='round'
                  stroke-width='2'
                  d='M6 18L18 6M6 6l12 12'
                ></path>
              </svg>
            </button>
          </div>

          {/* Tab Navigation */}
          <Show when={!loading() && !error() && job()}>
            <div class='px-4 pt-2'>
              <div class='tabs tabs-boxed justify-start'>
                <button
                  class={`tab tab-md gap-2 ${activeTab() === 'details' ? 'tab-active' : ''}`}
                  onClick={() => setActiveTab('details')}
                >
                  <svg class='w-4 h-4' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
                    <path
                      stroke-linecap='round'
                      stroke-linejoin='round'
                      stroke-width='2'
                      d='M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z'
                    />
                  </svg>
                  Job Details
                </button>
                <button
                  class={`tab tab-md gap-2 ${activeTab() === 'timeline' ? 'tab-active' : ''}`}
                  onClick={() => setActiveTab('timeline')}
                >
                  <svg class='w-4 h-4' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
                    <path
                      stroke-linecap='round'
                      stroke-linejoin='round'
                      stroke-width='2'
                      d='M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z'
                    />
                  </svg>
                  Timeline
                </button>
              </div>
            </div>
          </Show>

          {/* Modal Content */}
          <div class='p-4 overflow-y-auto max-h-[calc(90vh-180px)]'>
            <Show when={loading()}>
              <div class='flex flex-col items-center justify-center py-12'>
                <div class='loading loading-spinner loading-lg text-primary'></div>
                <p class='text-base-content/60 mt-3'>Loading job details...</p>
              </div>
            </Show>

            <Show when={error()}>
              <div class='alert alert-error'>
                <svg class='w-6 h-6' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
                  <path
                    stroke-linecap='round'
                    stroke-linejoin='round'
                    stroke-width='2'
                    d='M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
                  ></path>
                </svg>
                <span>{error()}</span>
                <button
                  class='btn btn-sm'
                  onClick={() => props.jobId && loadJobDetails(props.jobId)}
                >
                  Try Again
                </button>
              </div>
            </Show>

            <Show when={!loading() && !error() && job()}>
              {/* Details Tab Content */}
              <Show when={activeTab() === 'details'}>
                <div class='space-y-6'>
                  {/* Job Header Info */}
                  <div class='flex flex-wrap gap-4 items-start'>
                    <div class='flex-1 min-w-0'>
                      <h3 class='text-xl font-semibold text-primary mb-1'>{job()?.company}</h3>
                      <div class='flex flex-wrap gap-2 text-sm text-base-content/70 mb-2'>
                        <span>📍 {job()?.location}</span>
                        <Show when={job()?.job_type}>
                          <span>💼 {job()?.job_type?.replace('_', ' ')}</span>
                        </Show>
                        <Show when={job()?.remote_type}>
                          <span>🌐 {job()?.remote_type?.replace('_', ' ')}</span>
                        </Show>
                        <Show when={job()?.experience_level}>
                          <span>📊 {job()?.experience_level?.replace('_', ' ')}</span>
                        </Show>
                      </div>
                    </div>

                    <Show
                      when={formatSalary(
                        job()?.salary_min,
                        job()?.salary_max,
                        job()?.salary_currency
                      )}
                    >
                      <div class='text-right'>
                        <div class='text-lg font-bold text-success'>
                          {formatSalary(
                            job()?.salary_min,
                            job()?.salary_max,
                            job()?.salary_currency
                          )}
                        </div>
                        <div class='text-sm text-base-content/60'>Annual salary</div>
                      </div>
                    </Show>
                  </div>

                  {/* Description */}
                  <Show when={job()?.description}>
                    <div>
                      <h4 class='text-lg font-semibold mb-2'>Job Description</h4>
                      <div class='prose max-w-none'>
                        <p class='whitespace-pre-wrap text-base-content/80'>{job()?.description}</p>
                      </div>
                    </div>
                  </Show>

                  {/* Requirements & Responsibilities */}
                  <div class='grid md:grid-cols-2 gap-6'>
                    <Show when={job()?.requirements}>
                      <div>
                        <h4 class='text-lg font-semibold mb-2'>Requirements</h4>
                        <div class='bg-base-200 rounded-lg p-3'>
                          <pre class='whitespace-pre-wrap text-sm text-base-content/80 font-sans'>
                            {job()?.requirements}
                          </pre>
                        </div>
                      </div>
                    </Show>

                    <Show when={job()?.responsibilities}>
                      <div>
                        <h4 class='text-lg font-semibold mb-2'>Responsibilities</h4>
                        <div class='bg-base-200 rounded-lg p-3'>
                          <pre class='whitespace-pre-wrap text-sm text-base-content/80 font-sans'>
                            {job()?.responsibilities}
                          </pre>
                        </div>
                      </div>
                    </Show>
                  </div>

                  {/* Skills */}
                  <div class='grid md:grid-cols-2 gap-6'>
                    <Show
                      when={job()?.skills_required && (job()?.skills_required?.length ?? 0) > 0}
                    >
                      <div>
                        <h4 class='text-lg font-semibold mb-2'>Required Skills</h4>
                        <div class='flex flex-wrap gap-2'>
                          <For each={job()?.skills_required}>
                            {skill => <span class='badge badge-primary'>{skill}</span>}
                          </For>
                        </div>
                      </div>
                    </Show>

                    <Show
                      when={job()?.skills_preferred && (job()?.skills_preferred?.length ?? 0) > 0}
                    >
                      <div>
                        <h4 class='text-lg font-semibold mb-2'>Preferred Skills</h4>
                        <div class='flex flex-wrap gap-2'>
                          <For each={job()?.skills_preferred}>
                            {skill => <span class='badge badge-outline'>{skill}</span>}
                          </For>
                        </div>
                      </div>
                    </Show>
                  </div>

                  {/* Benefits */}
                  <Show when={job()?.benefits && (job()?.benefits?.length ?? 0) > 0}>
                    <div>
                      <h4 class='text-lg font-semibold mb-2'>Benefits</h4>
                      <div class='flex flex-wrap gap-2'>
                        <For each={job()?.benefits}>
                          {benefit => (
                            <span class='badge badge-success badge-outline'>{benefit}</span>
                          )}
                        </For>
                      </div>
                    </div>
                  </Show>

                  {/* Company & Additional Info */}
                  <div class='grid md:grid-cols-2 gap-6'>
                    <Show when={job()?.company_size || job()?.industry}>
                      <div>
                        <h4 class='text-lg font-semibold mb-2'>Company Info</h4>
                        <div class='space-y-2'>
                          <Show when={job()?.company_size}>
                            <div class='flex items-center gap-2'>
                              <span class='w-4 h-4'>👥</span>
                              <span>{job()?.company_size} employees</span>
                            </div>
                          </Show>
                          <Show when={job()?.industry}>
                            <div class='flex items-center gap-2'>
                              <span class='w-4 h-4'>🏢</span>
                              <span>{job()?.industry}</span>
                            </div>
                          </Show>
                        </div>
                      </div>
                    </Show>

                    <div>
                      <h4 class='text-lg font-semibold mb-2'>Job Info</h4>
                      <div class='space-y-2'>
                        <div class='flex items-center gap-2'>
                          <span class='w-4 h-4'>📅</span>
                          <span>Posted: {formatDate(job()?.posted_date)}</span>
                        </div>
                        <Show when={job()?.job_url}>
                          <div class='flex items-center gap-2'>
                            <span class='w-4 h-4'>🔗</span>
                            <a
                              href={job()!.job_url!}
                              target='_blank'
                              rel='noopener noreferrer'
                              class='link link-primary'
                            >
                              View Original Posting
                            </a>
                          </div>
                        </Show>
                      </div>
                    </div>
                  </div>
                </div>
              </Show>

              {/* Timeline Tab Content */}
              <Show when={activeTab() === 'timeline'}>
                <ApplicationTimeline
                  applicationId={job()?.id || 'unknown'}
                  jobTitle={job()?.title}
                  companyName={job()?.company}
                  className='min-h-[400px]'
                  compact={false}
                />
              </Show>
            </Show>
          </div>

          {/* Modal Footer */}
          <Show when={!loading() && !error() && job()}>
            <div class='flex items-center justify-end gap-2 p-4 border-t border-base-300'>
              <button class='btn btn-ghost' onClick={handleClose}>
                Close
              </button>
              <button
                class={`btn ${isSaved() ? 'btn-error' : 'btn-success'}`}
                onClick={handleSaveJob}
                disabled={saving()}
              >
                <Show when={saving()}>
                  <span class='loading loading-spinner loading-xs'></span>
                </Show>
                <Show when={!saving()}>{isSaved() ? '❌ Unsave Job' : '💾 Save Job'}</Show>
              </button>
              <Show when={job()?.job_url}>
                <a
                  href={job()!.job_url!}
                  target='_blank'
                  rel='noopener noreferrer'
                  class='btn btn-primary'
                >
                  🔗 Apply Now
                </a>
              </Show>
            </div>
          </Show>
        </div>
      </div>
    </Show>
  );
};
