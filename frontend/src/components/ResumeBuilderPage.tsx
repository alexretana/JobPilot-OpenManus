import { Component, createSignal, onMount, Show } from 'solid-js';
import { ProfileDashboard } from './UserProfile';
import { ResumeDashboard } from './Resume';
import Breadcrumb, { type BreadcrumbItem } from './Breadcrumb';

interface ResumeBuilderProps {
  userId?: string;
  shouldCreateNewResume?: boolean;
  onCreateNewHandled?: () => void;
  onProfileChange?: (profile: any) => void;
  className?: string;
}

type ResumeTab = 'profile' | 'resume';

export const ResumeBuilderPage: Component<ResumeBuilderProps> = props => {
  const [activeTab, setActiveTab] = createSignal<ResumeTab>('profile');
  const [shouldCreateNewResume, setShouldCreateNewResume] = createSignal(false);

  // Session storage key for remembering the active tab
  const STORAGE_KEY = 'resumeBuilder_activeTab';

  const userId = () => props.userId || 'demo-user-123';

  // Load the last selected tab from session storage on mount
  onMount(() => {
    const savedTab = sessionStorage.getItem(STORAGE_KEY) as ResumeTab;
    if (savedTab && ['profile', 'resume'].includes(savedTab)) {
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

  // Breadcrumb navigation
  const getBreadcrumbItems = (): BreadcrumbItem[] => {
    const items: BreadcrumbItem[] = [];

    if (activeTab() === 'profile') {
      items.push({
        label: 'User Profile',
        icon: '👤',
        isActive: true,
      });
    } else if (activeTab() === 'resume') {
      items.push({
        label: 'User Profile',
        icon: '👤',
        onClick: () => handleTabChange('profile'),
      });

      if (shouldCreateNewResume()) {
        items.push({
          label: 'Create Resume',
          icon: '✨',
          isActive: true,
        });
      } else {
        items.push({
          label: 'Resumes',
          icon: '📄',
          isActive: true,
        });
      }
    }

    return items;
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
            Resume
          </button>
        </div>

        {/* Quick Actions */}
        <div class='flex gap-2'>
          <Show when={activeTab() === 'profile'}>
            <button class='btn btn-primary btn-sm gap-2' onClick={handleNavigateToResume}>
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
                  d='M12 4v16m8-8H4'
                />
              </svg>
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

      {/* Breadcrumb Navigation */}
      <div class='bg-base-100/50 rounded-lg px-4 py-2 mb-2'>
        <Breadcrumb
          items={getBreadcrumbItems()}
          showHome={false}
          separator='→'
          className='text-base-content/70'
        />
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

      {/* Breadcrumb / Context Indicator */}
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
