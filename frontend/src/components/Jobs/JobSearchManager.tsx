import { Component, createSignal, onMount, Show } from 'solid-js';
import { JobsContainer } from './JobsContainer';
import ApplicationsManager from '../Applications/ApplicationsManager';
import LeadsManager from '../Shared/LeadsManager';

interface JobSearchManagerProps {
  onJobSelect?: (jobId: string) => void;
  onJobSave?: (jobId: string) => void;
  className?: string;
}

type JobSearchTab = 'jobs' | 'applications' | 'leads';

export const JobSearchManager: Component<JobSearchManagerProps> = props => {
  const [activeTab, setActiveTab] = createSignal<JobSearchTab>('jobs');

  // Session storage key for remembering the active tab
  const STORAGE_KEY = 'jobSearchManager_activeTab';

  // Load the last selected tab from session storage on mount
  onMount(() => {
    const savedTab = sessionStorage.getItem(STORAGE_KEY) as JobSearchTab;
    if (savedTab && ['jobs', 'applications', 'leads'].includes(savedTab)) {
      setActiveTab(savedTab);
    }
  });

  // Save tab selection to session storage when it changes
  const handleTabChange = (tab: JobSearchTab) => {
    setActiveTab(tab);
    sessionStorage.setItem(STORAGE_KEY, tab);
  };

  const handleJobSelect = (jobId: string) => {
    props.onJobSelect?.(jobId);
  };

  const handleJobSave = (jobId: string) => {
    props.onJobSave?.(jobId);
  };

  return (
    <div class={`w-full h-full flex flex-col ${props.className || ''}`}>
      {/* Tab Navigation with Quick Stats */}
      <div class='flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-4'>
        <div class='tabs tabs-boxed justify-start'>
          <button
            class={`tab tab-lg gap-2 ${activeTab() === 'jobs' ? 'tab-active' : ''}`}
            onClick={() => handleTabChange('jobs')}
          >
            <svg
              xmlns='http://www.w3.org/2000/svg'
              class='h-5 w-5'
              fill='none'
              viewBox='0 0 24 24'
              stroke='currentColor'
            >
              <path
                stroke-linecap='round'
                stroke-linejoin='round'
                stroke-width='2'
                d='M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2-2v2m8 0H8m8 0v2a2 2 0 01-2 2H10a2 2 0 01-2-2V6m8 0H8'
              />
            </svg>
            Jobs
          </button>
          <button
            class={`tab tab-lg gap-2 ${activeTab() === 'applications' ? 'tab-active' : ''}`}
            onClick={() => handleTabChange('applications')}
          >
            <svg
              xmlns='http://www.w3.org/2000/svg'
              class='h-5 w-5'
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
            Applications
          </button>
          <button
            class={`tab tab-lg gap-2 ${activeTab() === 'leads' ? 'tab-active' : ''}`}
            onClick={() => handleTabChange('leads')}
          >
            <svg
              xmlns='http://www.w3.org/2000/svg'
              class='h-5 w-5'
              fill='none'
              viewBox='0 0 24 24'
              stroke='currentColor'
            >
              <path
                stroke-linecap='round'
                stroke-linejoin='round'
                stroke-width='2'
                d='M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z'
              />
            </svg>
            Leads
          </button>
        </div>

        {/* Quick Stats */}
        <div class='stats stats-horizontal shadow bg-base-100'>
          <div class='stat place-items-center'>
            <div class='stat-title text-xs'>Jobs</div>
            <div class='stat-value text-sm'>—</div>
          </div>
          <div class='stat place-items-center'>
            <div class='stat-title text-xs'>Applications</div>
            <div class='stat-value text-sm'>—</div>
          </div>
          <div class='stat place-items-center'>
            <div class='stat-title text-xs'>Leads</div>
            <div class='stat-value text-sm'>—</div>
          </div>
        </div>
      </div>

      {/* Tab Content */}
      <div class='flex-1 min-h-0'>
        <Show when={activeTab() === 'jobs'}>
          <div class='h-full bg-base-100 rounded-lg p-4 overflow-y-auto'>
            <JobsContainer onJobSelect={handleJobSelect} onJobSave={handleJobSave} />
          </div>
        </Show>

        <Show when={activeTab() === 'applications'}>
          <div class='h-full bg-base-100 rounded-lg overflow-y-auto'>
            <ApplicationsManager />
          </div>
        </Show>

        <Show when={activeTab() === 'leads'}>
          <div class='h-full bg-base-100 rounded-lg overflow-y-auto'>
            <LeadsManager />
          </div>
        </Show>
      </div>
    </div>
  );
};

export default JobSearchManager;
