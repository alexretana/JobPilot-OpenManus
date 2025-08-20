/**
 * Saved Job List Component
 * Displays a list of saved jobs with filtering and management capabilities
 */

import { Component, createSignal, createEffect, For, Show } from 'solid-js';
import { JobCard } from './JobCard';
import { jobApi } from '../../../../services/jobApi';
import type { SavedJob } from '../../../../services/jobApi';

interface SavedJobListProps {
  onJobSelect?: (jobId: string) => void;
}

export const SavedJobList: Component<SavedJobListProps> = props => {
  const [savedJobs, setSavedJobs] = createSignal<SavedJob[]>([]);
  const [loading, setLoading] = createSignal(false);
  const [error, setError] = createSignal<string | null>(null);

  // Load saved jobs when component mounts or filter changes
  createEffect(() => {
    loadSavedJobs();
  });

  const loadSavedJobs = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await jobApi.getSavedJobs();
      setSavedJobs(response);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load saved jobs';
      setError(errorMessage);
      console.error('Error loading saved jobs:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    loadSavedJobs();
  };

  const handleJobSelect = (jobId: string) => {
    props.onJobSelect?.(jobId);
  };

  const handleUnsaveJob = async (jobId: string) => {
    try {
      await jobApi.unsaveJob(jobId);
      // Refresh the list to reflect the change
      loadSavedJobs();
    } catch (err) {
      console.error('Failed to unsave job:', err);
      // TODO: Show error toast
    }
  };

  const filteredJobs = () => {
    const jobs = savedJobs();
    // For now, just return all jobs since we don't have status filtering
    return jobs;
  };

  return (
    <div class='w-full'>
      {/* Header */}
      <div class='flex items-center justify-between mb-4'>
        <div class='flex items-center gap-2'>
          <h2 class='text-xl font-bold text-base-content'>Saved Jobs</h2>
          <Show when={!loading()}>
            <div class='badge badge-outline'>{filteredJobs().length} saved</div>
          </Show>
        </div>

        <div class='flex items-center gap-2'>
          {/* Filter Tabs - Simplified for now */}

          {/* Refresh Button */}
          <button
            class='btn btn-ghost btn-sm'
            onClick={handleRefresh}
            disabled={loading()}
            title='Refresh saved jobs'
          >
            <svg
              class={`w-4 h-4 ${loading() ? 'animate-spin' : ''}`}
              fill='none'
              stroke='currentColor'
              viewBox='0 0 24 24'
            >
              <path
                stroke-linecap='round'
                stroke-linejoin='round'
                stroke-width='2'
                d='M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15'
              />
            </svg>
          </button>
        </div>
      </div>

      {/* Loading State */}
      <Show when={loading()}>
        <div class='flex flex-col items-center justify-center py-8'>
          <div class='loading loading-spinner loading-lg text-primary'></div>
          <p class='text-base-content/60 mt-3'>Loading saved jobs...</p>
        </div>
      </Show>

      {/* Error State */}
      <Show when={error()}>
        <div class='alert alert-error mb-4'>
          <svg class='w-6 h-6' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
            <path
              stroke-linecap='round'
              stroke-linejoin='round'
              stroke-width='2'
              d='M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
            ></path>
          </svg>
          <span>{error()}</span>
          <button class='btn btn-sm' onClick={handleRefresh}>
            Try Again
          </button>
        </div>
      </Show>

      {/* Empty State */}
      <Show when={!loading() && !error() && filteredJobs().length === 0}>
        <div class='flex flex-col items-center justify-center py-8'>
          <div class='text-6xl mb-4'>💾</div>
          <h3 class='text-lg font-medium text-base-content mb-2'>No saved jobs yet</h3>
          <p class='text-base-content/60 text-center max-w-md mb-4'>
            Start saving jobs that interest you to keep track of them here. You can save jobs by
            clicking the bookmark icon on any job card or in the job details.
          </p>
        </div>
      </Show>

      {/* Saved Jobs Grid */}
      <Show when={!loading() && !error() && filteredJobs().length > 0}>
        <div class='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4'>
          <For each={filteredJobs()}>
            {savedJob => (
              <div class='relative'>
                <JobCard
                  job={savedJob}
                  onViewDetails={handleJobSelect}
                  onSaveJob={() => {}} // Already saved, so no-op
                  isSaved={true}
                />

                {/* Saved Job Actions Overlay */}
                <div class='absolute top-2 right-2 flex gap-1'>
                  {/* Unsave Button */}
                  <button
                    class='btn btn-ghost btn-xs btn-square bg-base-100/90 hover:bg-error hover:text-error-content'
                    onClick={() => handleUnsaveJob(savedJob.id)}
                    title='Remove from saved jobs'
                  >
                    <svg class='w-3 h-3' fill='currentColor' viewBox='0 0 20 20'>
                      <path d='M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z' />
                    </svg>
                  </button>
                </div>

                {/* Saved Job Metadata */}
                <div class='card-body p-2 pt-0'>
                  <div class='flex items-center gap-2 text-xs text-base-content/60'>
                    <span>Saved {new Date(savedJob.saved_date).toLocaleDateString()}</span>
                    <Show when={savedJob.notes}>
                      <div class='badge badge-sm badge-outline' title={savedJob.notes || undefined}>
                        📝 Notes
                      </div>
                    </Show>
                    <Show when={savedJob.tags && savedJob.tags.length > 0}>
                      <div class='badge badge-sm badge-outline'>
                        🏷️ {savedJob.tags!.length} tag{savedJob.tags!.length > 1 ? 's' : ''}
                      </div>
                    </Show>
                  </div>
                </div>
              </div>
            )}
          </For>
        </div>

        {/* Summary Stats */}
        <div class='mt-6 stats stats-horizontal shadow'>
          <div class='stat'>
            <div class='stat-title'>Total Saved</div>
            <div class='stat-value text-primary'>{savedJobs().length}</div>
          </div>
          <div class='stat'>
            <div class='stat-title'>This Month</div>
            <div class='stat-value text-success'>
              {
                savedJobs().filter(j => {
                  const savedDate = new Date(j.saved_date);
                  const now = new Date();
                  return (
                    savedDate.getMonth() === now.getMonth() &&
                    savedDate.getFullYear() === now.getFullYear()
                  );
                }).length
              }
            </div>
          </div>
          <div class='stat'>
            <div class='stat-title'>With Notes</div>
            <div class='stat-value text-info'>{savedJobs().filter(j => j.notes).length}</div>
          </div>
        </div>
      </Show>
    </div>
  );
};
