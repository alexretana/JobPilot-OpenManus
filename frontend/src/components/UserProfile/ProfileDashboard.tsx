import { Component, createSignal, createResource, Show, For, onMount } from 'solid-js';
import { createStore } from 'solid-js/store';
import { userProfileApi, UserProfile, ProfileCompleteness } from '../../services/userProfileApi';
import ProfileEditModal from './ProfileEditModal';
import ProfileCompletenessComponent from './ProfileCompleteness';

interface ProfileDashboardProps {
  userId?: string; // If not provided, will attempt to get current user
  onProfileChange?: (profile: UserProfile) => void;
}

const ProfileDashboard: Component<ProfileDashboardProps> = props => {
  const [showEditModal, setShowEditModal] = createSignal(false);
  const [selectedSection, setSelectedSection] = createSignal<
    'personal' | 'professional' | 'preferences'
  >('personal');
  const [completenessData, setCompletenessData] = createStore<ProfileCompleteness | null>(null);

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

  const getSkillsPreview = (
    skills: string[],
    maxShow = 5
  ): { displayed: string[]; remaining: number } => {
    if (skills.length <= maxShow) {
      return { displayed: skills, remaining: 0 };
    }
    return {
      displayed: skills.slice(0, maxShow),
      remaining: skills.length - maxShow,
    };
  };

  return (
    <div class="container mx-auto p-4 max-w-6xl">
      {/* Header */}
      <div class="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4 mb-6">
        <div>
          <h1 class="text-3xl font-bold text-base-content">Profile Dashboard</h1>
          <p class="text-base-content/70 mt-1">
            Manage your professional profile and job preferences
          </p>
        </div>
        <button class="btn btn-primary" onClick={handleEditProfile} disabled={profile.loading}>
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
            />
          </svg>
          Edit Profile
        </button>
      </div>

      <Show when={profile.loading}>
        <div class="flex justify-center items-center py-12">
          <span class="loading loading-spinner loading-lg"></span>
        </div>
      </Show>

      <Show when={profile.error}>
        <div class="alert alert-error mb-6">
          <svg class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <span>Error loading profile: {profile.error.message}</span>
          <div>
            <button class="btn btn-sm btn-outline" onClick={() => refetchProfile()}>
              Retry
            </button>
          </div>
        </div>
      </Show>

      <Show when={profile() && !profile.loading}>
        {currentProfile => (
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Profile Completeness Card */}
            <div class="lg:col-span-3">
              <Show when={completenessData}>
                {data => (
                  <ProfileCompletenessComponent
                    completeness={data}
                    onSectionFocus={section => setSelectedSection(section)}
                  />
                )}
              </Show>
            </div>

            {/* Personal Information */}
            <div class="card bg-base-100 shadow-xl">
              <div class="card-body">
                <h2 class="card-title flex items-center gap-2">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                    />
                  </svg>
                  Personal Information
                </h2>

                <div class="space-y-4">
                  <div>
                    <div class="text-sm font-medium text-base-content/70">Full Name</div>
                    <div class="text-lg">
                      {[currentProfile().first_name, currentProfile().last_name]
                        .filter(Boolean)
                        .join(' ') || 'Not provided'}
                    </div>
                  </div>

                  <div>
                    <div class="text-sm font-medium text-base-content/70">Email</div>
                    <div class="text-base">{currentProfile().email || 'Not provided'}</div>
                  </div>

                  <Show when={currentProfile().phone}>
                    <div>
                      <div class="text-sm font-medium text-base-content/70">Phone</div>
                      <div class="text-base">{currentProfile().phone}</div>
                    </div>
                  </Show>
                </div>
              </div>
            </div>

            {/* Professional Information */}
            <div class="card bg-base-100 shadow-xl">
              <div class="card-body">
                <h2 class="card-title flex items-center gap-2">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2-2v2m8 0V6a2 2 0 012 2v6a2 2 0 01-2 2H6a2 2 0 01-2-2V8a2 2 0 012-2V6z"
                    />
                  </svg>
                  Professional Details
                </h2>

                <div class="space-y-4">
                  <div>
                    <div class="text-sm font-medium text-base-content/70">Current Title</div>
                    <div class="text-base">{currentProfile().current_title || 'Not specified'}</div>
                  </div>

                  <div>
                    <div class="text-sm font-medium text-base-content/70">Experience</div>
                    <div class="text-base">
                      {getExperienceDisplay(currentProfile().experience_years)}
                    </div>
                  </div>

                  <Show when={currentProfile().education}>
                    <div>
                      <div class="text-sm font-medium text-base-content/70">Education</div>
                      <div class="text-base">{currentProfile().education}</div>
                    </div>
                  </Show>

                  <div>
                    <div class="text-sm font-medium text-base-content/70 mb-2">Skills</div>
                    <Show
                      when={currentProfile().skills && currentProfile().skills.length > 0}
                      fallback={<div class="text-base-content/50">No skills added</div>}
                    >
                      {() => {
                        const { displayed, remaining } = getSkillsPreview(
                          currentProfile().skills,
                          5
                        );
                        return (
                          <div class="flex flex-wrap gap-2">
                            <For each={displayed}>
                              {skill => <div class="badge badge-primary">{skill}</div>}
                            </For>
                            <Show when={remaining > 0}>
                              <div class="badge badge-ghost">+{remaining} more</div>
                            </Show>
                          </div>
                        );
                      }}
                    </Show>
                  </div>

                  <Show when={currentProfile().bio}>
                    <div>
                      <div class="text-sm font-medium text-base-content/70">
                        Professional Summary
                      </div>
                      <div class="text-sm text-base-content/80 bg-base-200 p-3 rounded-lg mt-1 line-clamp-3">
                        {currentProfile().bio}
                      </div>
                    </div>
                  </Show>
                </div>
              </div>
            </div>

            {/* Job Preferences */}
            <div class="card bg-base-100 shadow-xl">
              <div class="card-body">
                <h2 class="card-title flex items-center gap-2">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4"
                    />
                  </svg>
                  Job Preferences
                </h2>

                <div class="space-y-4">
                  <div>
                    <div class="text-sm font-medium text-base-content/70 mb-2">
                      Preferred Job Types
                    </div>
                    <Show
                      when={
                        currentProfile().preferred_job_types &&
                        currentProfile().preferred_job_types.length > 0
                      }
                      fallback={<div class="text-base-content/50">No preferences set</div>}
                    >
                      <div class="flex flex-wrap gap-2">
                        <For each={currentProfile().preferred_job_types}>
                          {jobType => <div class="badge badge-secondary">{jobType}</div>}
                        </For>
                      </div>
                    </Show>
                  </div>

                  <div>
                    <div class="text-sm font-medium text-base-content/70 mb-2">Remote Work</div>
                    <Show
                      when={
                        currentProfile().preferred_remote_types &&
                        currentProfile().preferred_remote_types.length > 0
                      }
                      fallback={<div class="text-base-content/50">No preferences set</div>}
                    >
                      <div class="flex flex-wrap gap-2">
                        <For each={currentProfile().preferred_remote_types}>
                          {remoteType => <div class="badge badge-accent">{remoteType}</div>}
                        </For>
                      </div>
                    </Show>
                  </div>

                  <div>
                    <div class="text-sm font-medium text-base-content/70 mb-2">
                      Preferred Locations
                    </div>
                    <Show
                      when={
                        currentProfile().preferred_locations &&
                        currentProfile().preferred_locations.length > 0
                      }
                      fallback={<div class="text-base-content/50">No locations specified</div>}
                    >
                      <div class="flex flex-wrap gap-2">
                        <For each={currentProfile().preferred_locations.slice(0, 3)}>
                          {location => <div class="badge badge-info badge-outline">{location}</div>}
                        </For>
                        <Show when={currentProfile().preferred_locations.length > 3}>
                          <div class="badge badge-ghost">
                            +{currentProfile().preferred_locations.length - 3} more
                          </div>
                        </Show>
                      </div>
                    </Show>
                  </div>

                  <div>
                    <div class="text-sm font-medium text-base-content/70">Salary Range</div>
                    <div class="text-base">
                      {userProfileApi.formatSalaryRange(
                        currentProfile().desired_salary_min,
                        currentProfile().desired_salary_max
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div class="lg:col-span-3">
              <div class="card bg-base-100 shadow-xl">
                <div class="card-body">
                  <h2 class="card-title">Quick Actions</h2>
                  <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <button class="btn btn-outline flex flex-col gap-2 h-auto py-4">
                      <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                        />
                      </svg>
                      <span class="text-sm">Generate Resume</span>
                    </button>

                    <button class="btn btn-outline flex flex-col gap-2 h-auto py-4">
                      <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                        />
                      </svg>
                      <span class="text-sm">Find Jobs</span>
                    </button>

                    <button class="btn btn-outline flex flex-col gap-2 h-auto py-4">
                      <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                        />
                      </svg>
                      <span class="text-sm">View Analytics</span>
                    </button>

                    <button class="btn btn-outline flex flex-col gap-2 h-auto py-4">
                      <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M12 6v6m0 0v6m0-6h6m-6 0H6"
                        />
                      </svg>
                      <span class="text-sm">Add Skills</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
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
