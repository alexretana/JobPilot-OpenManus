import { Component, createSignal, Show, For } from 'solid-js';
import { ProfileDashboard, ProfileEditModal, ProfileCompleteness } from '.';
import { userProfileApi, UserProfile } from '../../services/userProfileApi';

const ProfileSystemDemo: Component = () => {
  const [currentView, setCurrentView] = createSignal<
    'dashboard' | 'modal-test' | 'completeness-test'
  >('dashboard');
  const [showEditModal, setShowEditModal] = createSignal(false);
  const [mockProfile, setMockProfile] = createSignal<UserProfile>({
    id: 'demo-user-123',
    first_name: 'John',
    last_name: 'Doe',
    email: 'john.doe@example.com',
    phone: '+1 (555) 123-4567',
    current_title: 'Senior Software Engineer',
    experience_years: 8,
    skills: ['JavaScript', 'TypeScript', 'React', 'Node.js', 'Python'],
    education: 'BS Computer Science, MIT',
    bio: 'Experienced software engineer with a passion for building scalable web applications. Specializing in full-stack development with modern JavaScript frameworks.',
    preferred_locations: ['San Francisco, CA', 'New York, NY', 'Remote'],
    preferred_job_types: ['Full-time', 'Contract'],
    preferred_remote_types: ['Remote', 'Hybrid'],
    desired_salary_min: 120000,
    desired_salary_max: 180000,
    created_at: '2024-01-15T10:00:00Z',
    updated_at: '2024-01-20T15:30:00Z',
  });

  const [incompleteProfile, setIncompleteProfile] = createSignal<UserProfile>({
    id: 'incomplete-user-456',
    first_name: 'Jane',
    last_name: '',
    email: '',
    phone: '',
    current_title: '',
    experience_years: undefined,
    skills: [],
    education: '',
    bio: '',
    preferred_locations: [],
    preferred_job_types: [],
    preferred_remote_types: [],
    desired_salary_min: undefined,
    desired_salary_max: undefined,
    created_at: '2024-01-15T10:00:00Z',
    updated_at: '2024-01-20T15:30:00Z',
  });

  const handleProfileSave = (updatedProfile: UserProfile) => {
    setMockProfile(updatedProfile);
    setShowEditModal(false);
    console.log('Profile updated:', updatedProfile);
  };

  const completenessData = () => userProfileApi.calculateCompleteness(mockProfile());
  const incompleteData = () => userProfileApi.calculateCompleteness(incompleteProfile());

  const viewOptions = [
    {
      key: 'dashboard',
      label: 'Full Dashboard',
      description: 'Complete profile dashboard with all features',
    },
    { key: 'modal-test', label: 'Edit Modal Test', description: 'Test the profile editing modal' },
    {
      key: 'completeness-test',
      label: 'Completeness Test',
      description: 'Compare complete vs incomplete profiles',
    },
  ] as const;

  return (
    <div class='min-h-screen bg-base-200'>
      {/* Header */}
      <div class='bg-base-100 shadow-sm border-b'>
        <div class='container mx-auto p-4'>
          <h1 class='text-3xl font-bold mb-4'>User Profile Management System Demo</h1>
          <p class='text-base-content/70 mb-6'>
            This demo showcases the complete user profile management system including dashboard,
            editing forms, completeness tracking, and modal interactions.
          </p>

          {/* View Selector */}
          <div class='tabs tabs-boxed bg-base-200'>
            <For each={viewOptions}>
              {option => (
                <button
                  class={`tab ${currentView() === option.key ? 'tab-active' : ''}`}
                  onClick={() => setCurrentView(option.key)}
                >
                  {option.label}
                </button>
              )}
            </For>
          </div>

          {/* Current View Description */}
          <div class='mt-4 p-4 bg-info/10 rounded-lg'>
            <p class='text-sm text-info-content/80'>
              {viewOptions.find(v => v.key === currentView())?.description}
            </p>
          </div>
        </div>
      </div>

      {/* Content */}
      <div class='container mx-auto p-4'>
        <Show when={currentView() === 'dashboard'}>
          <div>
            <h2 class='text-2xl font-semibold mb-4'>Complete Profile Dashboard</h2>
            <ProfileDashboard
              userId='demo-user-123'
              onProfileChange={profile => {
                console.log('Profile changed in dashboard:', profile);
                setMockProfile(profile);
              }}
            />
          </div>
        </Show>

        <Show when={currentView() === 'modal-test'}>
          <div>
            <h2 class='text-2xl font-semibold mb-4'>Edit Modal Testing</h2>

            <div class='grid grid-cols-1 md:grid-cols-2 gap-6 mb-6'>
              <div class='card bg-base-100 shadow-xl'>
                <div class='card-body'>
                  <h3 class='card-title'>Current Profile Data</h3>
                  <div class='space-y-2 text-sm'>
                    <div>
                      <strong>Name:</strong> {mockProfile().first_name} {mockProfile().last_name}
                    </div>
                    <div>
                      <strong>Email:</strong> {mockProfile().email}
                    </div>
                    <div>
                      <strong>Title:</strong> {mockProfile().current_title}
                    </div>
                    <div>
                      <strong>Skills:</strong> {mockProfile().skills.join(', ')}
                    </div>
                    <div>
                      <strong>Job Types:</strong> {mockProfile().preferred_job_types.join(', ')}
                    </div>
                    <div>
                      <strong>Remote:</strong> {mockProfile().preferred_remote_types.join(', ')}
                    </div>
                  </div>
                </div>
              </div>

              <div class='card bg-base-100 shadow-xl'>
                <div class='card-body'>
                  <h3 class='card-title'>Profile Completeness</h3>
                  <ProfileCompleteness
                    completeness={completenessData()}
                    onSectionFocus={section => console.log('Focus on:', section)}
                  />
                </div>
              </div>
            </div>

            <div class='flex gap-4'>
              <button class='btn btn-primary' onClick={() => setShowEditModal(true)}>
                <svg class='w-4 h-4 mr-2' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
                  <path
                    stroke-linecap='round'
                    stroke-linejoin='round'
                    stroke-width='2'
                    d='M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z'
                  />
                </svg>
                Open Edit Modal
              </button>

              <button
                class='btn btn-outline'
                onClick={() => {
                  // Reset to incomplete profile for testing
                  setMockProfile({
                    ...incompleteProfile(),
                    id: mockProfile().id,
                  });
                }}
              >
                Test with Incomplete Profile
              </button>

              <button
                class='btn btn-outline'
                onClick={() => {
                  // Reset to complete profile
                  setMockProfile({
                    id: 'demo-user-123',
                    first_name: 'John',
                    last_name: 'Doe',
                    email: 'john.doe@example.com',
                    phone: '+1 (555) 123-4567',
                    current_title: 'Senior Software Engineer',
                    experience_years: 8,
                    skills: ['JavaScript', 'TypeScript', 'React', 'Node.js', 'Python'],
                    education: 'BS Computer Science, MIT',
                    bio: 'Experienced software engineer with a passion for building scalable web applications.',
                    preferred_locations: ['San Francisco, CA', 'New York, NY', 'Remote'],
                    preferred_job_types: ['Full-time', 'Contract'],
                    preferred_remote_types: ['Remote', 'Hybrid'],
                    desired_salary_min: 120000,
                    desired_salary_max: 180000,
                    created_at: '2024-01-15T10:00:00Z',
                    updated_at: '2024-01-20T15:30:00Z',
                  });
                }}
              >
                Reset to Complete Profile
              </button>
            </div>
          </div>
        </Show>

        <Show when={currentView() === 'completeness-test'}>
          <div>
            <h2 class='text-2xl font-semibold mb-4'>Profile Completeness Comparison</h2>

            <div class='grid grid-cols-1 lg:grid-cols-2 gap-6'>
              {/* Complete Profile */}
              <div class='card bg-base-100 shadow-xl'>
                <div class='card-body'>
                  <h3 class='card-title text-success'>Complete Profile Example</h3>
                  <ProfileCompleteness
                    completeness={completenessData()}
                    onSectionFocus={section => console.log('Complete profile focus:', section)}
                  />

                  <div class='divider'></div>

                  <div class='space-y-2 text-sm'>
                    <h4 class='font-semibold'>Profile Data:</h4>
                    <div>
                      <strong>Name:</strong> John Doe
                    </div>
                    <div>
                      <strong>Email:</strong> john.doe@example.com
                    </div>
                    <div>
                      <strong>Phone:</strong> +1 (555) 123-4567
                    </div>
                    <div>
                      <strong>Title:</strong> Senior Software Engineer
                    </div>
                    <div>
                      <strong>Experience:</strong> 8 years
                    </div>
                    <div>
                      <strong>Skills:</strong> 5 skills added
                    </div>
                    <div>
                      <strong>Education:</strong> BS Computer Science, MIT
                    </div>
                    <div>
                      <strong>Bio:</strong> {mockProfile().bio?.slice(0, 50)}...
                    </div>
                    <div>
                      <strong>Locations:</strong> 3 preferred locations
                    </div>
                    <div>
                      <strong>Job Types:</strong> 2 preferred types
                    </div>
                    <div>
                      <strong>Remote:</strong> 2 preferences
                    </div>
                    <div>
                      <strong>Salary:</strong> $120,000 - $180,000
                    </div>
                  </div>
                </div>
              </div>

              {/* Incomplete Profile */}
              <div class='card bg-base-100 shadow-xl'>
                <div class='card-body'>
                  <h3 class='card-title text-warning'>Incomplete Profile Example</h3>
                  <ProfileCompleteness
                    completeness={incompleteData()}
                    onSectionFocus={section => console.log('Incomplete profile focus:', section)}
                  />

                  <div class='divider'></div>

                  <div class='space-y-2 text-sm'>
                    <h4 class='font-semibold'>Profile Data:</h4>
                    <div>
                      <strong>Name:</strong> Jane (No last name)
                    </div>
                    <div class='text-error'>
                      <strong>Email:</strong> Missing
                    </div>
                    <div class='text-error'>
                      <strong>Phone:</strong> Missing
                    </div>
                    <div class='text-error'>
                      <strong>Title:</strong> Missing
                    </div>
                    <div class='text-error'>
                      <strong>Experience:</strong> Missing
                    </div>
                    <div class='text-error'>
                      <strong>Skills:</strong> None added
                    </div>
                    <div class='text-error'>
                      <strong>Education:</strong> Missing
                    </div>
                    <div class='text-error'>
                      <strong>Bio:</strong> Missing
                    </div>
                    <div class='text-error'>
                      <strong>Locations:</strong> None specified
                    </div>
                    <div class='text-error'>
                      <strong>Job Types:</strong> None selected
                    </div>
                    <div class='text-error'>
                      <strong>Remote:</strong> None selected
                    </div>
                    <div class='text-error'>
                      <strong>Salary:</strong> Not specified
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class='mt-6 card bg-base-100 shadow-xl'>
              <div class='card-body'>
                <h3 class='card-title'>Completeness Analysis</h3>
                <div class='overflow-x-auto'>
                  <table class='table'>
                    <thead>
                      <tr>
                        <th>Metric</th>
                        <th>Complete Profile</th>
                        <th>Incomplete Profile</th>
                        <th>Difference</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td class='font-semibold'>Overall Score</td>
                        <td class='text-success'>{completenessData().overall_score}%</td>
                        <td class='text-error'>{incompleteData().overall_score}%</td>
                        <td class='text-info'>
                          +{completenessData().overall_score - incompleteData().overall_score}%
                        </td>
                      </tr>
                      <tr>
                        <td class='font-semibold'>Personal Section</td>
                        <td class='text-success'>{completenessData().sections.personal}%</td>
                        <td class='text-error'>{incompleteData().sections.personal}%</td>
                        <td class='text-info'>
                          +
                          {completenessData().sections.personal -
                            incompleteData().sections.personal}
                          %
                        </td>
                      </tr>
                      <tr>
                        <td class='font-semibold'>Professional Section</td>
                        <td class='text-success'>{completenessData().sections.professional}%</td>
                        <td class='text-error'>{incompleteData().sections.professional}%</td>
                        <td class='text-info'>
                          +
                          {completenessData().sections.professional -
                            incompleteData().sections.professional}
                          %
                        </td>
                      </tr>
                      <tr>
                        <td class='font-semibold'>Preferences Section</td>
                        <td class='text-success'>{completenessData().sections.preferences}%</td>
                        <td class='text-error'>{incompleteData().sections.preferences}%</td>
                        <td class='text-info'>
                          +
                          {completenessData().sections.preferences -
                            incompleteData().sections.preferences}
                          %
                        </td>
                      </tr>
                      <tr>
                        <td class='font-semibold'>Missing Fields</td>
                        <td class='text-success'>{completenessData().missing_fields.length}</td>
                        <td class='text-error'>{incompleteData().missing_fields.length}</td>
                        <td class='text-warning'>
                          {incompleteData().missing_fields.length -
                            completenessData().missing_fields.length}{' '}
                          more
                        </td>
                      </tr>
                      <tr>
                        <td class='font-semibold'>Suggestions</td>
                        <td class='text-success'>{completenessData().suggestions.length}</td>
                        <td class='text-error'>{incompleteData().suggestions.length}</td>
                        <td class='text-warning'>
                          {incompleteData().suggestions.length -
                            completenessData().suggestions.length}{' '}
                          more
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </Show>
      </div>

      {/* Edit Modal */}
      <ProfileEditModal
        isOpen={showEditModal()}
        profile={mockProfile()}
        onSave={handleProfileSave}
        onClose={() => setShowEditModal(false)}
      />
    </div>
  );
};

export default ProfileSystemDemo;
