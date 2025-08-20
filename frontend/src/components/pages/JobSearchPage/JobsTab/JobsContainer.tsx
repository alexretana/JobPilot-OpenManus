/**
 * Jobs Container Component
 * Container with tabs for Recent Jobs and Saved Jobs views
 */

import { Component, createSignal, Show } from 'solid-js';
import { JobList } from './JobList';
import { SavedJobList } from './SavedJobList';

interface JobsContainerProps {
  onJobSelect?: (jobId: string) => void;
  onJobSave?: (jobId: string) => void;
}

type JobsTab = 'recent' | 'saved';

export const JobsContainer: Component<JobsContainerProps> = props => {
  const [activeTab, setActiveTab] = createSignal<JobsTab>('recent');

  const handleJobSelect = (jobId: string) => {
    props.onJobSelect?.(jobId);
  };

  const handleJobSave = (jobId: string) => {
    props.onJobSave?.(jobId);
  };

  return (
    <div class='container w-full h-full flex flex-col mx-auto'>
      {/* Tab Navigation */}
      <div class='tabs tabs-boxed justify-start mb-4'>
        <button
          class={`tab tab-lg gap-2 ${activeTab() === 'recent' ? 'tab-active' : ''}`}
          onClick={() => setActiveTab('recent')}
        >
          <svg class='w-4 h-4' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
            <path
              stroke-linecap='round'
              stroke-linejoin='round'
              stroke-width='2'
              d='M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z'
            />
          </svg>
          Recent Jobs
        </button>
        <button
          class={`tab tab-lg gap-2 ${activeTab() === 'saved' ? 'tab-active' : ''}`}
          onClick={() => setActiveTab('saved')}
        >
          <svg class='w-4 h-4' fill='currentColor' viewBox='0 0 20 20'>
            <path d='M5 4a2 2 0 012-2h6a2 2 0 012 2v14l-5-2.5L5 18V4z' />
          </svg>
          Saved Jobs
        </button>
      </div>

      {/* Tab Content */}
      <div class='flex-1 min-h-0'>
        <Show when={activeTab() === 'recent'}>
          <JobList onJobSelect={handleJobSelect} onJobSave={handleJobSave} />
        </Show>

        <Show when={activeTab() === 'saved'}>
          <SavedJobList onJobSelect={handleJobSelect} />
        </Show>
      </div>
    </div>
  );
};
