import { Component, createSignal, Show, For, onMount } from 'solid-js';
import { createStore } from 'solid-js/store';
import {
  userProfileApi,
  UserProfile,
  UserProfileCreate,
  UserProfileUpdate,
  JobType,
  RemoteType,
} from '../../../../services/userProfileApi';

interface ProfileEditFormProps {
  profile?: UserProfile; // If editing existing profile
  onSave: (profile: UserProfile) => void;
  onCancel: () => void;
}

const ProfileEditForm: Component<ProfileEditFormProps> = props => {
  const [isSubmitting, setIsSubmitting] = createSignal(false);
  const [errors, setErrors] = createStore<string[]>([]);
  const [activeTab, setActiveTab] = createSignal<'personal' | 'professional' | 'preferences'>(
    'personal'
  );

  // Form data
  const [formData, setFormData] = createStore<UserProfileCreate>({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    city: '',
    state: '',
    linkedin_url: '',
    portfolio_url: '',
    current_title: '',
    experience_years: undefined,
    skills: [], // Keep for backward compatibility with API, but don't manage in form
    education: '',
    bio: '',
    preferred_locations: [],
    preferred_job_types: [],
    preferred_remote_types: [],
    desired_salary_min: undefined,
    desired_salary_max: undefined,
  });

  // Location input management (for preferences)
  const [locationInput, setLocationInput] = createSignal('');

  // Initialize form with existing profile data
  onMount(() => {
    if (props.profile) {
      setFormData({
        first_name: props.profile.first_name || '',
        last_name: props.profile.last_name || '',
        email: props.profile.email || '',
        phone: props.profile.phone || '',
        city: props.profile.city || '',
        state: props.profile.state || '',
        linkedin_url: props.profile.linkedin_url || '',
        portfolio_url: props.profile.portfolio_url || '',
        current_title: props.profile.current_title || '',
        experience_years: props.profile.experience_years,
        skills: props.profile.skills || [], // Keep existing skills but don't allow editing
        education: props.profile.education || '',
        bio: props.profile.bio || '',
        preferred_locations: [...(props.profile.preferred_locations || [])],
        preferred_job_types: [...(props.profile.preferred_job_types || [])],
        preferred_remote_types: [...(props.profile.preferred_remote_types || [])],
        desired_salary_min: props.profile.desired_salary_min,
        desired_salary_max: props.profile.desired_salary_max,
      });
    }
  });

  const handleAddLocation = () => {
    const location = locationInput().trim();
    if (location && !(formData.preferred_locations || []).includes(location)) {
      setFormData('preferred_locations', [...(formData.preferred_locations || []), location]);
      setLocationInput('');
    }
  };

  const handleRemoveLocation = (locationToRemove: string) => {
    setFormData(
      'preferred_locations',
      (formData.preferred_locations || []).filter(loc => loc !== locationToRemove)
    );
  };

  const handleLocationKeyPress = (e: KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddLocation();
    }
  };

  const handleJobTypeToggle = (jobType: JobType) => {
    const isSelected = formData.preferred_job_types.includes(jobType);
    if (isSelected) {
      setFormData(
        'preferred_job_types',
        formData.preferred_job_types.filter(type => type !== jobType)
      );
    } else {
      setFormData('preferred_job_types', [...formData.preferred_job_types, jobType]);
    }
  };

  const handleRemoteTypeToggle = (remoteType: RemoteType) => {
    const isSelected = formData.preferred_remote_types.includes(remoteType);
    if (isSelected) {
      setFormData(
        'preferred_remote_types',
        formData.preferred_remote_types.filter(type => type !== remoteType)
      );
    } else {
      setFormData('preferred_remote_types', [...formData.preferred_remote_types, remoteType]);
    }
  };

  const handleSubmit = async (e: Event) => {
    e.preventDefault();
    setIsSubmitting(true);
    setErrors([]);

    try {
      // Validate form data
      const validationErrors = userProfileApi.validateProfile(formData);
      if (validationErrors.length > 0) {
        setErrors(validationErrors);
        setIsSubmitting(false);
        return;
      }

      let savedProfile: UserProfile;

      if (props.profile) {
        // Update existing profile
        const updates: UserProfileUpdate = { ...formData };
        savedProfile = await userProfileApi.updateProfile(props.profile.id, updates);
      } else {
        // Create new profile
        savedProfile = await userProfileApi.createProfile(formData);
      }

      props.onSave(savedProfile);
    } catch (error) {
      console.error('Error saving profile:', error);
      setErrors([
        error instanceof Error ? error.message : 'An error occurred while saving the profile',
      ]);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} class='space-y-6'>
      {/* Header */}
      <div class='flex justify-between items-center'>
        <h3 class='text-2xl font-bold'>{props.profile ? 'Edit Profile' : 'Create Profile'}</h3>
        <button type='button' class='btn btn-ghost btn-circle' onClick={props.onCancel}>
          <svg class='w-6 h-6' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
            <path
              stroke-linecap='round'
              stroke-linejoin='round'
              stroke-width='2'
              d='M6 18L18 6M6 6l12 12'
            />
          </svg>
        </button>
      </div>

      {/* Error Display */}
      <Show when={errors.length > 0}>
        <div class='alert alert-error'>
          <svg class='stroke-current shrink-0 w-6 h-6' fill='none' viewBox='0 0 24 24'>
            <path
              stroke-linecap='round'
              stroke-linejoin='round'
              stroke-width='2'
              d='M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z'
            />
          </svg>
          <div>
            <h3 class='font-medium'>Please fix the following errors:</h3>
            <ul class='list-disc list-inside text-sm mt-1'>
              <For each={errors}>{error => <li>{error}</li>}</For>
            </ul>
          </div>
        </div>
      </Show>

      {/* Tabs */}
      <div class='tabs tabs-boxed'>
        <button
          type='button'
          class={`tab ${activeTab() === 'personal' ? 'tab-active' : ''}`}
          onClick={() => setActiveTab('personal')}
        >
          Personal Information
        </button>
        <button
          type='button'
          class={`tab ${activeTab() === 'professional' ? 'tab-active' : ''}`}
          onClick={() => setActiveTab('professional')}
        >
          Professional Details
        </button>
        <button
          type='button'
          class={`tab ${activeTab() === 'preferences' ? 'tab-active' : ''}`}
          onClick={() => setActiveTab('preferences')}
        >
          Job Preferences
        </button>
      </div>

      {/* Personal Information Tab */}
      <Show when={activeTab() === 'personal'}>
        <div class='grid grid-cols-1 md:grid-cols-2 gap-4'>
          <div class='form-control'>
            <label class='label'>
              <span class='label-text'>First Name</span>
            </label>
            <input
              type='text'
              class='input input-bordered'
              value={formData.first_name}
              onInput={e => setFormData('first_name', e.currentTarget.value)}
              placeholder='Your first name'
            />
          </div>

          <div class='form-control'>
            <label class='label'>
              <span class='label-text'>Last Name *</span>
            </label>
            <input
              type='text'
              class='input input-bordered'
              value={formData.last_name}
              onInput={e => setFormData('last_name', e.currentTarget.value)}
              placeholder='Your last name'
              required
            />
          </div>

          <div class='form-control'>
            <label class='label'>
              <span class='label-text'>Email Address *</span>
            </label>
            <input
              type='email'
              class='input input-bordered'
              value={formData.email}
              onInput={e => setFormData('email', e.currentTarget.value)}
              placeholder='your.email@example.com'
              required
            />
          </div>

          <div class='form-control'>
            <label class='label'>
              <span class='label-text'>Phone Number</span>
            </label>
            <input
              type='tel'
              class='input input-bordered'
              value={formData.phone}
              onInput={e => setFormData('phone', e.currentTarget.value)}
              placeholder='+1 (555) 123-4567'
            />
          </div>

          <div class='form-control'>
            <label class='label'>
              <span class='label-text'>City</span>
            </label>
            <input
              type='text'
              class='input input-bordered'
              value={formData.city}
              onInput={e => setFormData('city', e.currentTarget.value)}
              placeholder='e.g., San Francisco'
            />
          </div>

          <div class='form-control'>
            <label class='label'>
              <span class='label-text'>State</span>
            </label>
            <input
              type='text'
              class='input input-bordered'
              value={formData.state}
              onInput={e => setFormData('state', e.currentTarget.value)}
              placeholder='e.g., CA'
            />
          </div>

          <div class='form-control'>
            <label class='label'>
              <span class='label-text'>LinkedIn Profile</span>
            </label>
            <input
              type='url'
              class='input input-bordered'
              value={formData.linkedin_url}
              onInput={e => setFormData('linkedin_url', e.currentTarget.value)}
              placeholder='https://linkedin.com/in/your-profile'
            />
          </div>

          <div class='form-control'>
            <label class='label'>
              <span class='label-text'>Portfolio URL</span>
            </label>
            <input
              type='url'
              class='input input-bordered'
              value={formData.portfolio_url}
              onInput={e => setFormData('portfolio_url', e.currentTarget.value)}
              placeholder='https://your-portfolio.com'
            />
          </div>
        </div>
      </Show>

      {/* Professional Information Tab */}
      <Show when={activeTab() === 'professional'}>
        <div class='space-y-4'>
          <div class='grid grid-cols-1 md:grid-cols-2 gap-4'>
            <div class='form-control'>
              <label class='label'>
                <span class='label-text'>Current Job Title</span>
              </label>
              <input
                type='text'
                class='input input-bordered'
                value={formData.current_title}
                onInput={e => setFormData('current_title', e.currentTarget.value)}
                placeholder='e.g., Software Engineer'
              />
            </div>

            <div class='form-control'>
              <label class='label'>
                <span class='label-text'>Years of Experience</span>
              </label>
              <input
                type='number'
                class='input input-bordered'
                value={formData.experience_years || ''}
                onInput={e =>
                  setFormData(
                    'experience_years',
                    e.currentTarget.value ? parseInt(e.currentTarget.value) : undefined
                  )
                }
                placeholder='5'
                min='0'
                max='50'
              />
            </div>
          </div>

          <div class='form-control'>
            <label class='label'>
              <span class='label-text'>Education</span>
            </label>
            <input
              type='text'
              class='input input-bordered'
              value={formData.education}
              onInput={e => setFormData('education', e.currentTarget.value)}
              placeholder="e.g., Bachelor's in Computer Science"
            />
          </div>

          <div class='form-control'>
            <label class='label'>
              <span class='label-text'>Professional Summary</span>
            </label>
            <textarea
              class='textarea textarea-bordered h-24'
              value={formData.bio}
              onInput={e => setFormData('bio', e.currentTarget.value)}
              placeholder='Write a brief professional summary highlighting your experience and achievements...'
            />
            <div class='label'>
              <span class='label-text-alt'>{(formData.bio || '').length} characters</span>
            </div>
          </div>
        </div>
      </Show>

      {/* Job Preferences Tab */}
      <Show when={activeTab() === 'preferences'}>
        <div class='space-y-6'>
          {/* Job Types */}
          <div class='form-control'>
            <label class='label'>
              <span class='label-text'>Preferred Job Types *</span>
              <span class='label-text-alt'>{formData.preferred_job_types.length} selected</span>
            </label>
            <div class='grid grid-cols-2 md:grid-cols-3 gap-2'>
              <For each={userProfileApi.getJobTypes()}>
                {jobType => (
                  <label class='label cursor-pointer justify-start gap-2'>
                    <input
                      type='checkbox'
                      class='checkbox'
                      checked={formData.preferred_job_types.includes(jobType)}
                      onChange={() => handleJobTypeToggle(jobType)}
                    />
                    <span class='label-text'>{jobType}</span>
                  </label>
                )}
              </For>
            </div>
          </div>

          {/* Remote Types */}
          <div class='form-control'>
            <label class='label'>
              <span class='label-text'>Remote Work Preferences *</span>
              <span class='label-text-alt'>{formData.preferred_remote_types.length} selected</span>
            </label>
            <div class='grid grid-cols-3 gap-2'>
              <For each={userProfileApi.getRemoteTypes()}>
                {remoteType => (
                  <label class='label cursor-pointer justify-start gap-2'>
                    <input
                      type='checkbox'
                      class='checkbox'
                      checked={formData.preferred_remote_types.includes(remoteType)}
                      onChange={() => handleRemoteTypeToggle(remoteType)}
                    />
                    <span class='label-text'>{remoteType}</span>
                  </label>
                )}
              </For>
            </div>
          </div>

          {/* Locations */}
          <div class='form-control'>
            <label class='label'>
              <span class='label-text'>Preferred Locations</span>
              <span class='label-text-alt'>
                {(formData.preferred_locations || []).length} locations
              </span>
            </label>

            <div class='flex gap-2 mb-2'>
              <input
                type='text'
                class='input input-bordered flex-1'
                value={locationInput()}
                onInput={e => setLocationInput(e.currentTarget.value)}
                onKeyPress={handleLocationKeyPress}
                placeholder='Type a city/state and press Enter'
              />
              <button
                type='button'
                class='btn btn-secondary'
                onClick={handleAddLocation}
                disabled={!locationInput().trim()}
              >
                Add
              </button>
            </div>

            <Show when={(formData.preferred_locations || []).length > 0}>
              <div class='flex flex-wrap gap-2'>
                <For each={formData.preferred_locations || []}>
                  {location => (
                    <div class='badge badge-info gap-2'>
                      {location}
                      <button
                        type='button'
                        class='btn btn-ghost btn-circle btn-xs'
                        onClick={() => handleRemoveLocation(location)}
                      >
                        <svg class='w-3 h-3' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
                          <path
                            stroke-linecap='round'
                            stroke-linejoin='round'
                            stroke-width='2'
                            d='M6 18L18 6M6 6l12 12'
                          />
                        </svg>
                      </button>
                    </div>
                  )}
                </For>
              </div>
            </Show>
          </div>

          {/* Salary Range */}
          <div class='form-control'>
            <label class='label'>
              <span class='label-text'>Desired Salary Range (USD)</span>
            </label>
            <div class='grid grid-cols-2 gap-4'>
              <div>
                <input
                  type='number'
                  class='input input-bordered w-full'
                  value={formData.desired_salary_min || ''}
                  onInput={e =>
                    setFormData(
                      'desired_salary_min',
                      e.currentTarget.value ? parseInt(e.currentTarget.value) : undefined
                    )
                  }
                  placeholder='Minimum'
                  min='0'
                  step='1000'
                />
                <div class='label'>
                  <span class='label-text-alt'>Minimum salary</span>
                </div>
              </div>
              <div>
                <input
                  type='number'
                  class='input input-bordered w-full'
                  value={formData.desired_salary_max || ''}
                  onInput={e =>
                    setFormData(
                      'desired_salary_max',
                      e.currentTarget.value ? parseInt(e.currentTarget.value) : undefined
                    )
                  }
                  placeholder='Maximum'
                  min='0'
                  step='1000'
                />
                <div class='label'>
                  <span class='label-text-alt'>Maximum salary</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Show>

      {/* Form Actions */}
      <div class='flex justify-end gap-4 pt-4 border-t'>
        <button
          type='button'
          class='btn btn-ghost'
          onClick={props.onCancel}
          disabled={isSubmitting()}
        >
          Cancel
        </button>
        <button type='submit' class='btn btn-primary' disabled={isSubmitting()}>
          <Show
            when={isSubmitting()}
            fallback={props.profile ? 'Update Profile' : 'Create Profile'}
          >
            <span class='loading loading-spinner loading-sm mr-2'></span>
            Saving...
          </Show>
        </button>
      </div>
    </form>
  );
};

export default ProfileEditForm;
