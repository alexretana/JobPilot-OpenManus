/**
 * Job Card Component
 * Displays an individual job listing in a card format
 */

import { Component, Show } from 'solid-js';
import type { Job } from '../../../../services/jobApi';
import { jobApi } from '../../../../services/jobApi';

interface JobCardProps {
  job: Job;
  onViewDetails?: (jobId: string) => void;
  onSaveJob?: (jobId: string) => void;
  isSaved?: boolean;
}

export const JobCard: Component<JobCardProps> = props => {
  const handleViewDetails = () => {
    props.onViewDetails?.(props.job.id);
  };

  const handleSaveJob = (e: MouseEvent) => {
    e.stopPropagation();
    props.onSaveJob?.(props.job.id);
  };

  const handleVisitJob = (e: MouseEvent) => {
    e.stopPropagation();
    if (props.job.job_url) {
      window.open(props.job.job_url, '_blank');
    }
  };

  return (
    <div
      class='card bg-base-100 shadow-md hover:shadow-lg transition-all duration-200 cursor-pointer border border-base-300 hover:border-primary'
      onClick={handleViewDetails}
    >
      <div class='card-body p-4'>
        {/* Header with title and save button */}
        <div class='flex justify-between items-start mb-2'>
          <h3 class='card-title text-lg font-bold text-base-content line-clamp-2 flex-1 mr-2'>
            {props.job.title}
          </h3>
          <div class='flex gap-1'>
            <button
              class={`btn btn-ghost btn-xs ${props.isSaved ? 'text-warning' : ''}`}
              onClick={handleSaveJob}
              title={props.isSaved ? 'Unsave job' : 'Save job'}
            >
              <svg
                class='w-4 h-4'
                fill={props.isSaved ? 'currentColor' : 'none'}
                stroke='currentColor'
                viewBox='0 0 24 24'
              >
                <path
                  stroke-linecap='round'
                  stroke-linejoin='round'
                  stroke-width='2'
                  d='M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z'
                ></path>
              </svg>
            </button>
          </div>
        </div>

        {/* Company and location */}
        <div class='flex items-center gap-2 text-sm text-base-content/70 mb-3'>
          <span class='font-medium'>{props.job.company}</span>
          <span>•</span>
          <div class='flex items-center gap-1'>
            <span>{jobApi.getRemoteTypeIcon(props.job.remote_type)}</span>
            <span>{props.job.location}</span>
          </div>
        </div>

        {/* Job details row */}
        <div class='flex flex-wrap items-center gap-3 text-sm text-base-content/60 mb-3'>
          <Show when={props.job.job_type}>
            <div class='badge badge-outline badge-sm'>
              {jobApi.getJobTypeLabel(props.job.job_type)}
            </div>
          </Show>

          <Show when={props.job.remote_type}>
            <div class='badge badge-outline badge-sm'>
              {jobApi.getRemoteTypeLabel(props.job.remote_type)}
            </div>
          </Show>

          <Show when={props.job.posted_date}>
            <span class='text-xs opacity-60'>{jobApi.formatPostedDate(props.job)}</span>
          </Show>
        </div>

        {/* Salary */}
        <Show when={props.job.salary_min || props.job.salary_max}>
          <div class='text-sm font-medium text-success mb-3'>
            💰 {jobApi.formatSalary(props.job)}
          </div>
        </Show>

        {/* Skills */}
        <Show when={props.job.skills_required && props.job.skills_required.length > 0}>
          <div class='flex flex-wrap gap-1 mb-3'>
            {props.job.skills_required.slice(0, 4).map(skill => (
              <span class='badge badge-sm bg-base-200 text-base-content/80'>{skill}</span>
            ))}
            <Show when={props.job.skills_required.length > 4}>
              <span class='badge badge-sm bg-base-200 text-base-content/60'>
                +{props.job.skills_required.length - 4} more
              </span>
            </Show>
          </div>
        </Show>

        {/* Description preview */}
        <Show when={props.job.description}>
          <p class='text-sm text-base-content/70 line-clamp-2 mb-3'>{props.job.description}</p>
        </Show>

        {/* Actions */}
        <div class='card-actions justify-between items-center'>
          <Show when={props.job.job_url}>
            <button class='btn btn-outline btn-sm' onClick={handleVisitJob}>
              <svg class='w-4 h-4 mr-1' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
                <path
                  stroke-linecap='round'
                  stroke-linejoin='round'
                  stroke-width='2'
                  d='M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14'
                ></path>
              </svg>
              Visit
            </button>
          </Show>

          <button class='btn btn-primary btn-sm' onClick={handleViewDetails}>
            View Details
            <svg class='w-4 h-4 ml-1' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
              <path
                stroke-linecap='round'
                stroke-linejoin='round'
                stroke-width='2'
                d='M9 5l7 7-7 7'
              ></path>
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};
