/**
 * Job List Component
 * Displays a list of job cards with loading and error states
 */

import { Component, createSignal, createEffect, For, Show } from 'solid-js';
import { JobCard } from './JobCard';
import { jobApi } from '../../../../services/jobApi';
import type { Job, JobSearchFilters } from '../../../../services/jobApi';

interface JobListProps {
  filters?: JobSearchFilters;
  onJobSelect?: (jobId: string) => void;
  onJobSave?: (jobId: string) => void;
}

export const JobList: Component<JobListProps> = props => {
  const [jobs, setJobs] = createSignal<Job[]>([]);
  const [loading, setLoading] = createSignal(false);
  const [error, setError] = createSignal<string | null>(null);
  const [total, setTotal] = createSignal(0);

  // Load jobs when component mounts or filters change
  createEffect(() => {
    loadJobs();
  });

  const loadJobs = async () => {
    try {
      setLoading(true);
      setError(null);

      let response;
      if (
        props.filters &&
        (props.filters.query || props.filters.job_types || props.filters.locations)
      ) {
        response = await jobApi.searchJobs(props.filters);
      } else {
        response = await jobApi.getRecentJobs(props.filters?.limit || 20);
      }

      setJobs(response.jobs);
      setTotal(response.total);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load jobs';
      setError(errorMessage);
      console.error('Error loading jobs:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    loadJobs();
  };

  const handleJobSelect = (jobId: string) => {
    props.onJobSelect?.(jobId);
  };

  const handleJobSave = (jobId: string) => {
    props.onJobSave?.(jobId);
    // TODO: Show toast notification
  };

  return (
    <div class='w-full'>
      {/* Header */}
      <div class='flex items-center justify-between mb-2'>
        <div class='flex items-center gap-2'>
          <h2 class='text-xl font-bold text-base-content'>
            <Show when={props.filters?.query} fallback='Recent Jobs'>
              Search Results
            </Show>
          </h2>
          <Show when={!loading()}>
            <div class='badge badge-outline'>
              {total()} job{total() !== 1 ? 's' : ''}
            </div>
          </Show>
        </div>

        <button
          class='btn btn-ghost btn-sm'
          onClick={handleRefresh}
          disabled={loading()}
          title='Refresh jobs'
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

      {/* Loading State */}
      <Show when={loading()}>
        <div class='flex flex-col items-center justify-center py-8'>
          <div class='loading loading-spinner loading-lg text-primary'></div>
          <p class='text-base-content/60 mt-3'>Loading jobs...</p>
        </div>
      </Show>

      {/* Error State */}
      <Show when={error()}>
        <div class='alert alert-error mb-2'>
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
      <Show when={!loading() && !error() && jobs().length === 0}>
        <div class='flex flex-col items-center justify-center py-8'>
          <div class='text-6xl mb-2'>🔍</div>
          <h3 class='text-lg font-medium text-base-content mb-2'>No jobs found</h3>
          <p class='text-base-content/60 text-center max-w-md mb-2'>
            <Show
              when={props.filters?.query}
              fallback='Try adjusting your search criteria or check back later for new opportunities.'
            >
              No jobs match your search criteria. Try broadening your search or using different
              keywords.
            </Show>
          </p>
          <button class='btn btn-primary' onClick={handleRefresh}>
            Refresh Jobs
          </button>
        </div>
      </Show>

      {/* Job Cards Grid */}
      <Show when={!loading() && !error() && jobs().length > 0}>
        <div class='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2'>
          <For each={jobs()}>
            {job => <JobCard job={job} onViewDetails={handleJobSelect} onSaveJob={handleJobSave} />}
          </For>
        </div>

        {/* Load More Button (placeholder for future pagination) */}
        <Show when={jobs().length >= (props.filters?.limit || 20)}>
          <div class='flex justify-center mt-4'>
            <button class='btn btn-outline' disabled>
              Load More Jobs
              <span class='text-xs opacity-60'>(Coming Soon)</span>
            </button>
          </div>
        </Show>
      </Show>
    </div>
  );
};
