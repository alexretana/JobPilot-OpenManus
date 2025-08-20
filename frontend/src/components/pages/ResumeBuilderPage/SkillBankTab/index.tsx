import { Component, createSignal, createResource, Show, createMemo } from 'solid-js';
import { skillBankApiService } from '../../../../services/skillBankApi';
import SkillsSection from './sections/SkillsSection';
import SummariesSection from './sections/SummariesSection';
import ExperienceSection from './sections/ExperienceSection';
import EducationSection from './sections/EducationSection';
import ProjectsSection from './sections/ProjectsSection';
import CertificationsSection from './sections/CertificationsSection';
import ContactInfoSection from './sections/ContactInfoSection';

interface SkillBankProps {
  userId?: string;
}

const skillBankApi = skillBankApiService;

/**
 * Skill Bank Dashboard - Complete Solid.js Version with DaisyUI styling
 * Manages skills, professional summaries, and work experience
 */
const SkillBankDashboard: Component<SkillBankProps> = props => {
  const [activeTab, setActiveTab] = createSignal<
    'contact' | 'skills' | 'summaries' | 'experience' | 'education' | 'projects' | 'certifications'
  >('contact');
  const [refreshTrigger, setRefreshTrigger] = createSignal(0);

  const userId = () => props.userId || 'demo-user-123';

  // Create resource for skill bank data with refresh capability
  const [skillBank] = createResource(
    () => [userId(), refreshTrigger()],
    async ([userId]) => {
      try {
        return await skillBankApi.getSkillBank(String(userId));
      } catch (error) {
        console.error('Failed to load skill bank:', error);
        // Return empty skill bank structure on error
        return {
          id: '',
          user_id: String(userId),
          skills: {},
          skill_categories: [],
          default_summary: null,
          summary_variations: [],
          work_experiences: [],
          education_entries: [],
          projects: [],
          certifications: [],
          experience_content_variations: {},
          education_content_variations: {},
          project_content_variations: {},
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        };
      }
    }
  );

  // Computed values for tab counts
  const tabCounts = createMemo(() => {
    const data = skillBank();
    if (!data)
      return {
        skills: 0,
        summaries: 0,
        experiences: 0,
        education: 0,
        projects: 0,
        certifications: 0,
      };

    const skillsCount = Object.values(data.skills).reduce(
      (total, skillArray) => total + skillArray.length,
      0
    );

    return {
      skills: skillsCount,
      summaries: data.summary_variations?.length || 0,
      experiences: data.work_experiences?.length || 0,
      education: data.education_entries?.length || 0,
      projects: data.projects?.length || 0,
      certifications: data.certifications?.length || 0,
    };
  });

  const handleTabChange = (
    tab:
      | 'contact'
      | 'skills'
      | 'summaries'
      | 'experience'
      | 'education'
      | 'projects'
      | 'certifications'
  ) => {
    setActiveTab(tab);
  };

  const handleRefresh = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  return (
    <div class='w-full h-full flex flex-col space-y-2'>
      {/* Loading State */}
      <Show when={skillBank.loading}>
        <div class='flex flex-col items-center justify-center py-20 m-2 p-2'>
          <span class='loading loading-spinner loading-lg text-primary mb-4'></span>
          <p class='text-base-content/70'>Loading your skill bank...</p>
        </div>
      </Show>

      {/* Error State */}
      <Show when={skillBank.error}>
        <div class='alert alert-error m-2 p-2'>
          <svg class='stroke-current shrink-0 h-6 w-6' fill='none' viewBox='0 0 24 24'>
            <path
              stroke-linecap='round'
              stroke-linejoin='round'
              stroke-width='2'
              d='M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z'
            />
          </svg>
          <div>
            <h3 class='font-bold'>Error Loading Skill Bank</h3>
            <div class='text-xs'>{skillBank.error?.message}</div>
          </div>
          <button class='btn btn-sm m-2 p-2' onClick={handleRefresh}>
            Try Again
          </button>
        </div>
      </Show>

      {/* Main Content */}
      <Show when={skillBank() && !skillBank.loading}>
        <div class='flex-1 flex gap-2 m-2'>
          {/* Left Sidebar with Title and Menu */}
          <div class='w-64 flex flex-col gap-2'>
            {/* Title */}
            <h1 class='text-3xl font-bold text-base-content flex items-center gap-3 p-2'>
              <div class='w-10 h-10 bg-primary/20 rounded-lg flex items-center justify-center'>
                <svg
                  class='w-6 h-6 text-primary'
                  fill='none'
                  stroke='currentColor'
                  viewBox='0 0 24 24'
                >
                  <path
                    stroke-linecap='round'
                    stroke-linejoin='round'
                    stroke-width='2'
                    d='M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.781 0-2.674-2.153-1.415-3.414l5-5A2 2 0 009 9.172V5L8 4z'
                  />
                </svg>
              </div>
              Skill Bank
            </h1>

            {/* Menu */}
            <ul class='menu bg-base-200 rounded-box p-2 h-fit sticky top-0'>
              <li>
                <button
                  class={activeTab() === 'contact' ? 'active' : ''}
                  onClick={() => handleTabChange('contact')}
                >
                  <svg class='h-5 w-5' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
                    <path
                      stroke-linecap='round'
                      stroke-linejoin='round'
                      stroke-width='2'
                      d='M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z'
                    ></path>
                  </svg>
                  Contact Info
                </button>
              </li>

              <li>
                <button
                  class={activeTab() === 'skills' ? 'active' : ''}
                  onClick={() => handleTabChange('skills')}
                >
                  <svg class='h-5 w-5' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
                    <path
                      stroke-linecap='round'
                      stroke-linejoin='round'
                      stroke-width='2'
                      d='M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z'
                    />
                  </svg>
                  Skills
                  <div class='badge badge-primary badge-sm ml-auto'>{tabCounts().skills}</div>
                </button>
              </li>

              <li>
                <button
                  class={activeTab() === 'summaries' ? 'active' : ''}
                  onClick={() => handleTabChange('summaries')}
                >
                  <svg class='h-5 w-5' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
                    <path
                      stroke-linecap='round'
                      stroke-linejoin='round'
                      stroke-width='2'
                      d='M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z'
                    />
                  </svg>
                  Professional Summaries
                  <div class='badge badge-secondary badge-sm ml-auto'>{tabCounts().summaries}</div>
                </button>
              </li>

              <li>
                <button
                  class={activeTab() === 'experience' ? 'active' : ''}
                  onClick={() => handleTabChange('experience')}
                >
                  <svg class='h-5 w-5' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
                    <path
                      stroke-linecap='round'
                      stroke-linejoin='round'
                      stroke-width='2'
                      d='M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2-2v2m8 0V6a2 2 0 012 2v6a2 2 0 01-2 2H6a2 2 0 01-2-2V8a2 2 0 012-2V6z'
                    />
                  </svg>
                  Work Experience
                  <div class='badge badge-accent badge-sm ml-auto'>{tabCounts().experiences}</div>
                </button>
              </li>

              <li>
                <button
                  class={activeTab() === 'education' ? 'active' : ''}
                  onClick={() => handleTabChange('education')}
                >
                  <svg class='h-5 w-5' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
                    <path
                      stroke-linecap='round'
                      stroke-linejoin='round'
                      stroke-width='2'
                      d='M12 14l9-5-9-5-9 5 9 5z'
                    ></path>
                    <path
                      stroke-linecap='round'
                      stroke-linejoin='round'
                      stroke-width='2'
                      d='M12 14l6.16-3.422A12.083 12.083 0 0121 18.782V12M4.84 10.578A12.083 12.083 0 003 12v6.782'
                    ></path>
                    <path
                      stroke-linecap='round'
                      stroke-linejoin='round'
                      stroke-width='2'
                      d='M12 21v-7'
                    ></path>
                  </svg>
                  Education
                  <div class='badge badge-info badge-sm ml-auto'>{tabCounts().education}</div>
                </button>
              </li>

              <li>
                <button
                  class={activeTab() === 'projects' ? 'active' : ''}
                  onClick={() => handleTabChange('projects')}
                >
                  <svg class='h-5 w-5' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
                    <path
                      stroke-linecap='round'
                      stroke-linejoin='round'
                      stroke-width='2'
                      d='M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10'
                    ></path>
                  </svg>
                  Projects
                  <div class='badge badge-info badge-sm ml-auto'>{tabCounts().projects}</div>
                </button>
              </li>

              <li>
                <button
                  class={activeTab() === 'certifications' ? 'active' : ''}
                  onClick={() => handleTabChange('certifications')}
                >
                  <svg class='h-5 w-5' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
                    <path
                      stroke-linecap='round'
                      stroke-linejoin='round'
                      stroke-width='2'
                      d='M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z'
                    ></path>
                  </svg>
                  Certifications
                  <div class='badge badge-info badge-sm ml-auto'>{tabCounts().certifications}</div>
                </button>
              </li>
            </ul>
          </div>

          {/* Main Content Area with Scrolling */}
          <div class='flex-1 flex flex-col min-h-0 m-2'>
            {/* Tab Content - Scrollable */}
            <div class='flex-1 overflow-y-auto pr-2 p-2'>
              <Show when={activeTab() === 'contact'}>
                <ContactInfoSection
                  skillBank={skillBank()!}
                  onUpdate={handleRefresh}
                  loading={skillBank.loading}
                />
              </Show>

              <Show when={activeTab() === 'skills'}>
                <SkillsSection
                  skillBank={skillBank()!}
                  onUpdate={handleRefresh}
                  loading={skillBank.loading}
                />
              </Show>

              <Show when={activeTab() === 'summaries'}>
                <SummariesSection
                  skillBank={skillBank()!}
                  onUpdate={handleRefresh}
                  loading={skillBank.loading}
                />
              </Show>

              <Show when={activeTab() === 'experience'}>
                <ExperienceSection
                  skillBank={skillBank()!}
                  onUpdate={handleRefresh}
                  loading={skillBank.loading}
                />
              </Show>

              <Show when={activeTab() === 'education'}>
                <EducationSection
                  skillBank={skillBank()!}
                  onUpdate={handleRefresh}
                  loading={skillBank.loading}
                />
              </Show>

              <Show when={activeTab() === 'projects'}>
                <ProjectsSection
                  skillBank={skillBank()!}
                  onUpdate={handleRefresh}
                  loading={skillBank.loading}
                />
              </Show>

              <Show when={activeTab() === 'certifications'}>
                <CertificationsSection
                  skillBank={skillBank()!}
                  onUpdate={handleRefresh}
                  loading={skillBank.loading}
                />
              </Show>
            </div>

            {/* Footer - Empty now that stats are moved to header */}
          </div>
        </div>
      </Show>
    </div>
  );
};

export default SkillBankDashboard;
