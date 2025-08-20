import { Component, createSignal, createResource, Show, For } from 'solid-js';
import { createStore } from 'solid-js/store';
import {
  userProfileApi,
  UserProfile,
  ProfileCompleteness,
} from '../../../../services/userProfileApi';
import ProfileEditModal from './ProfileEditModal';
import ProfileCompletenessComponent from './ProfileCompleteness';

interface ProfileDashboardProps {
  userId?: string; // If not provided, will attempt to get current user
  onProfileChange?: (profile: UserProfile) => void;
  onNavigateToResume?: (resumeData?: any) => void; // Callback for navigation
}

const ProfileDashboard: Component<ProfileDashboardProps> = props => {
  const [showEditModal, setShowEditModal] = createSignal(false);
  const [completenessData, setCompletenessData] = createStore<ProfileCompleteness>({
    overall_score: 0,
    sections: {
      personal: 0,
      professional: 0,
      preferences: 0,
    },
    missing_fields: [],
    suggestions: [],
  });

  // Fetch user profile - use specific user ID or default profile for single-user mode
  const [profile, { refetch: refetchProfile }] = createResource(async () => {
    try {
      let userProfile: UserProfile;

      if (props.userId) {
        // Use specific user ID if provided
        userProfile = await userProfileApi.getProfile(props.userId);
      } else {
        // Use default profile for single-user mode
        userProfile = await userProfileApi.getDefaultProfile();
      }

      // Calculate completeness when profile loads
      const completeness = userProfileApi.calculateCompleteness(userProfile);
      setCompletenessData(completeness);
      return userProfile;
    } catch (error) {
      console.error('Error fetching profile:', error);
      throw error;
    }
  });

  const handleProfileUpdate = async (updatedProfile: UserProfile) => {
    // Recalculate completeness
    const completeness = userProfileApi.calculateCompleteness(updatedProfile);
    setCompletenessData(completeness);

    // Notify parent component
    props.onProfileChange?.(updatedProfile);

    // Refresh the profile data
    refetchProfile();
    setShowEditModal(false);
  };

  const handleEditProfile = () => {
    setShowEditModal(true);
  };

  const getExperienceDisplay = (years?: number): string => {
    if (!years) return 'Not specified';
    if (years === 1) return '1 year';
    return `${years} years`;
  };

  return (
    <div class='container mx-auto p-4 max-w-6xl'>
      {/* Header */}
      <div class='flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4 mb-6'>
        <div>
          <h1 class='text-3xl font-bold text-base-content'>Profile Dashboard</h1>
          <p class='text-base-content/70 mt-1'>
            Manage your professional profile and job preferences
          </p>
        </div>
        <div class='flex gap-2'>
          <button class='btn btn-primary' onClick={handleEditProfile} disabled={profile.loading}>
            <svg class='w-4 h-4 mr-2' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
              <path
                stroke-linecap='round'
                stroke-linejoin='round'
                stroke-width='2'
                d='M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z'
              />
            </svg>
            Edit Profile
          </button>
        </div>
      </div>

      <Show when={profile.loading}>
        <div class='flex justify-center items-center py-12'>
          <span class='loading loading-spinner loading-lg'></span>
        </div>
      </Show>

      <Show when={profile.error}>
        <div class='alert alert-error mb-6'>
          <svg class='stroke-current shrink-0 h-6 w-6' fill='none' viewBox='0 0 24 24'>
            <path
              stroke-linecap='round'
              stroke-linejoin='round'
              stroke-width='2'
              d='M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z'
            />
          </svg>
          <span>Error loading profile: {profile.error.message}</span>
          <div>
            <button class='btn btn-sm btn-outline' onClick={() => refetchProfile()}>
              Retry
            </button>
          </div>
        </div>
      </Show>

      <Show when={profile() && !profile.loading}>
        <div class='grid grid-cols-1 lg:grid-cols-3 gap-6'>
          {/* Profile Completeness Card */}
          <div class='lg:col-span-3'>
            <ProfileCompletenessComponent
              completeness={completenessData}
              onSectionFocus={() => {}}
            />
          </div>

          {/* Personal Information */}
          <div class='card bg-base-100 shadow-xl'>
            <div class='card-body'>
              <h2 class='card-title flex items-center gap-2'>
                <svg class='w-5 h-5' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
                  <path
                    stroke-linecap='round'
                    stroke-linejoin='round'
                    stroke-width='2'
                    d='M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z'
                  />
                </svg>
                Personal Information
              </h2>

              <div class='space-y-4'>
                <div>
                  <div class='text-sm font-medium text-base-content/70'>Full Name</div>
                  <div class='text-lg'>
                    {[profile()?.first_name, profile()?.last_name].filter(Boolean).join(' ') ||
                      'Not provided'}
                  </div>
                </div>

                <div>
                  <div class='text-sm font-medium text-base-content/70'>Email</div>
                  <div class='text-base'>{profile()?.email || 'Not provided'}</div>
                </div>

                <Show when={profile()?.phone}>
                  <div>
                    <div class='text-sm font-medium text-base-content/70'>Phone</div>
                    <div class='text-base'>{profile()?.phone}</div>
                  </div>
                </Show>

                <Show when={profile()?.city || profile()?.state}>
                  <div>
                    <div class='text-sm font-medium text-base-content/70'>Location</div>
                    <div class='text-base'>
                      {[profile()?.city, profile()?.state].filter(Boolean).join(', ') ||
                        'Not provided'}
                    </div>
                  </div>
                </Show>

                <Show when={profile()?.linkedin_url}>
                  <div>
                    <div class='text-sm font-medium text-base-content/70'>LinkedIn</div>
                    <div class='text-base'>
                      <a
                        href={profile()?.linkedin_url}
                        target='_blank'
                        rel='noopener noreferrer'
                        class='link link-primary'
                      >
                        {profile()?.linkedin_url}
                      </a>
                    </div>
                  </div>
                </Show>

                <Show when={profile()?.portfolio_url}>
                  <div>
                    <div class='text-sm font-medium text-base-content/70'>Portfolio</div>
                    <div class='text-base'>
                      <a
                        href={profile()?.portfolio_url}
                        target='_blank'
                        rel='noopener noreferrer'
                        class='link link-primary'
                      >
                        {profile()?.portfolio_url}
                      </a>
                    </div>
                  </div>
                </Show>
              </div>
            </div>
          </div>

          {/* Professional Information */}
          <div class='card bg-base-100 shadow-xl'>
            <div class='card-body'>
              <h2 class='card-title flex items-center gap-2'>
                <svg class='w-5 h-5' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
                  <path
                    stroke-linecap='round'
                    stroke-linejoin='round'
                    stroke-width='2'
                    d='M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2-2v2m8 0V6a2 2 0 012 2v6a2 2 0 01-2 2H6a2 2 0 01-2-2V8a2 2 0 012-2V6z'
                  />
                </svg>
                Professional Details
              </h2>

              <div class='space-y-4'>
                <div>
                  <div class='text-sm font-medium text-base-content/70'>Current Title</div>
                  <div class='text-base'>{profile()?.current_title || 'Not specified'}</div>
                </div>

                <div>
                  <div class='text-sm font-medium text-base-content/70'>Experience</div>
                  <div class='text-base'>{getExperienceDisplay(profile()?.experience_years)}</div>
                </div>

                <Show when={profile()?.education}>
                  <div>
                    <div class='text-sm font-medium text-base-content/70'>Education</div>
                    <div class='text-base'>{profile()?.education}</div>
                  </div>
                </Show>

                <Show when={profile()?.bio}>
                  <div>
                    <div class='text-sm font-medium text-base-content/70'>Professional Summary</div>
                    <div class='text-sm text-base-content/80 bg-base-200 p-3 rounded-lg mt-1 line-clamp-3'>
                      {profile()?.bio}
                    </div>
                  </div>
                </Show>
              </div>
            </div>
          </div>

          {/* Job Preferences */}
          <div class='card bg-base-100 shadow-xl'>
            <div class='card-body'>
              <h2 class='card-title flex items-center gap-2'>
                <svg class='w-5 h-5' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
                  <path
                    stroke-linecap='round'
                    stroke-linejoin='round'
                    stroke-width='2'
                    d='M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4'
                  />
                </svg>
                Job Preferences
              </h2>

              <div class='space-y-4'>
                <div>
                  <div class='text-sm font-medium text-base-content/70 mb-2'>
                    Preferred Job Types
                  </div>
                  <Show
                    when={
                      profile()?.preferred_job_types &&
                      (profile()?.preferred_job_types?.length ?? 0) > 0
                    }
                    fallback={<div class='text-base-content/50'>No preferences set</div>}
                  >
                    <div class='flex flex-wrap gap-2'>
                      <For each={profile()?.preferred_job_types}>
                        {jobType => <div class='badge badge-secondary'>{jobType}</div>}
                      </For>
                    </div>
                  </Show>
                </div>

                <div>
                  <div class='text-sm font-medium text-base-content/70 mb-2'>Remote Work</div>
                  <Show
                    when={
                      profile()?.preferred_remote_types &&
                      (profile()?.preferred_remote_types?.length ?? 0) > 0
                    }
                    fallback={<div class='text-base-content/50'>No preferences set</div>}
                  >
                    <div class='flex flex-wrap gap-2'>
                      <For each={profile()?.preferred_remote_types}>
                        {remoteType => <div class='badge badge-accent'>{remoteType}</div>}
                      </For>
                    </div>
                  </Show>
                </div>

                <div>
                  <div class='text-sm font-medium text-base-content/70 mb-2'>
                    Preferred Locations
                  </div>
                  <Show
                    when={
                      profile()?.preferred_locations &&
                      (profile()?.preferred_locations?.length ?? 0) > 0
                    }
                    fallback={<div class='text-base-content/50'>No locations specified</div>}
                  >
                    <div class='flex flex-wrap gap-2'>
                      <For each={profile()?.preferred_locations?.slice(0, 3) || []}>
                        {location => <div class='badge badge-info badge-outline'>{location}</div>}
                      </For>
                      <Show when={(profile()?.preferred_locations?.length || 0) > 3}>
                        <div class='badge badge-ghost'>
                          +{(profile()?.preferred_locations?.length || 0) - 3} more
                        </div>
                      </Show>
                    </div>
                  </Show>
                </div>

                <div>
                  <div class='text-sm font-medium text-base-content/70'>Salary Range</div>
                  <div class='text-base'>
                    {userProfileApi.formatSalaryRange(
                      profile()?.desired_salary_min,
                      profile()?.desired_salary_max
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Show>

      {/* Edit Profile Modal */}
      <ProfileEditModal
        isOpen={showEditModal()}
        profile={profile() || undefined}
        onSave={handleProfileUpdate}
        onClose={() => setShowEditModal(false)}
      />
    </div>
  );
};

export default ProfileDashboard;
