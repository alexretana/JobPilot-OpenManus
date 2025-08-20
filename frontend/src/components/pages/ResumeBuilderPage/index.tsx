import { Component, createSignal, onMount, Show } from 'solid-js';
import { ProfileDashboard } from './UserProfileTab';
import { ResumeDashboard } from './ResumeTab';
import SkillBankDashboard from './SkillBankTab';

interface ResumeBuilderProps {
  userId?: string;
  shouldCreateNewResume?: boolean;
  onCreateNewHandled?: () => void;
  onProfileChange?: (profile: any) => void;
  className?: string;
}

type ResumeTab = 'profile' | 'skillbank' | 'resume';

export const ResumeBuilderPage: Component<ResumeBuilderProps> = props => {
  const [activeTab, setActiveTab] = createSignal<ResumeTab>('profile');
  const [shouldCreateNewResume, setShouldCreateNewResume] = createSignal(false);

  // Session storage key for remembering the active tab
  const STORAGE_KEY = 'resumeBuilder_activeTab';

  const userId = () => props.userId || 'demo-user-123';

  // Load the last selected tab from session storage on mount
  onMount(() => {
    const savedTab = sessionStorage.getItem(STORAGE_KEY) as ResumeTab;
    if (savedTab && ['profile', 'skillbank', 'resume'].includes(savedTab)) {
      setActiveTab(savedTab);
    }

    // Handle external signal to create new resume
    if (props.shouldCreateNewResume) {
      setActiveTab('resume');
      setShouldCreateNewResume(true);
      props.onCreateNewHandled?.();
    }
  });

  // Save tab selection to session storage when it changes
  const handleTabChange = (tab: ResumeTab) => {
    setActiveTab(tab);
    sessionStorage.setItem(STORAGE_KEY, tab);
  };

  const handleNavigateToResume = () => {
    setShouldCreateNewResume(true);
    handleTabChange('resume');
  };

  const handleProfileChange = (profile: any) => {
    props.onProfileChange?.(profile);
  };

  const handleCreateNewHandled = () => {
    setShouldCreateNewResume(false);
  };

  return (
    <div class={`w-full h-full flex flex-col ${props.className || ''}`}>
      {/* Tab Navigation with Quick Actions */}
      <div class='flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-4'>
        <div class='tabs tabs-boxed justify-start'>
          <button
            class={`tab tab-lg gap-2 ${activeTab() === 'profile' ? 'tab-active' : ''}`}
            onClick={() => handleTabChange('profile')}
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
                d='M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z'
              />
            </svg>
            User Profile
          </button>
          <button
            class={`tab tab-lg gap-2 ${activeTab() === 'skillbank' ? 'tab-active' : ''}`}
            onClick={() => handleTabChange('skillbank')}
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
                d='M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z'
              />
            </svg>
            Skill Bank
          </button>
          <button
            class={`tab tab-lg gap-2 ${activeTab() === 'resume' ? 'tab-active' : ''}`}
            onClick={() => handleTabChange('resume')}
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
            Resume Builder
          </button>
        </div>

        {/* Quick Actions */}
        <div class='flex gap-2'>
          <Show when={activeTab() === 'profile'}>
            <button class='btn btn-primary btn-sm gap-2' onClick={handleNavigateToResume}>
              <div class='flex items-center gap-1'>
                <svg
                  xmlns='http://www.w3.org/2000/svg'
                  class='h-3 w-3'
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
              </div>
              Create Resume
            </button>
          </Show>
          <Show when={activeTab() === 'resume'}>
            <button class='btn btn-outline btn-sm gap-2' onClick={() => handleTabChange('profile')}>
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
                  d='M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z'
                />
              </svg>
              Edit Profile
            </button>
          </Show>
        </div>
      </div>

      {/* Tab Content */}
      <div class='flex-1 min-h-0'>
        <Show when={activeTab() === 'profile'}>
          <div class='h-full bg-base-100 rounded-lg p-4 overflow-y-auto'>
            <ProfileDashboard
              userId={userId()}
              onProfileChange={handleProfileChange}
              onNavigateToResume={handleNavigateToResume}
            />
          </div>
        </Show>

        <Show when={activeTab() === 'skillbank'}>
          <div class='h-full bg-base-100 rounded-lg p-4 overflow-y-auto'>
            <SkillBankDashboard userId={userId()} />
          </div>
        </Show>

        <Show when={activeTab() === 'resume'}>
          <div class='h-full bg-base-100 rounded-lg p-4 overflow-y-auto'>
            <ResumeDashboard
              userId={userId()}
              shouldCreateNew={shouldCreateNewResume()}
              onCreateNewHandled={handleCreateNewHandled}
            />
          </div>
        </Show>
      </div>

      {/* Context Indicator */}
      <Show when={activeTab() === 'resume' && shouldCreateNewResume()}>
        <div class='alert alert-info mt-4'>
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
              d='M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
            />
          </svg>
          <div>
            <h3 class='font-bold'>Creating Resume from Profile</h3>
            <div class='text-xs'>
              Your profile information will be automatically imported into the new resume.
            </div>
          </div>
        </div>
      </Show>
    </div>
  );
};

export default ResumeBuilderPage;
