import { Component, createSignal, createEffect, Show, createResource } from 'solid-js';
import { createStore } from 'solid-js/store';
import type { SkillBankResponse } from '../../../../../types/skillBank';
import { userProfileApi } from '../../../../../services/userProfileApi';
import type { UserProfileUpdate } from '../../../../../services/userProfileApi';

interface ContactInfoSectionProps {
  skillBank: SkillBankResponse;
  onUpdate: () => void;
  loading: boolean;
}

interface ContactFormData {
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  city: string;
  state: string;
  country: string;
  linkedin_url: string;
  portfolio_url: string;
  github_url: string;
}

const initialFormData: ContactFormData = {
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  city: '',
  state: '',
  country: '',
  linkedin_url: '',
  portfolio_url: '',
  github_url: '',
};

/**
 * Contact information management section
 */
export const ContactInfoSection: Component<ContactInfoSectionProps> = props => {
  const [formData, setFormData] = createStore<ContactFormData>(initialFormData);
  const [saving, setSaving] = createSignal(false);
  const [hasChanges, setHasChanges] = createSignal(false);

  // Load user profile data
  const [userProfile] = createResource(
    () => props.skillBank?.user_id,
    async userId => {
      if (!userId) return null;
      try {
        // Try to get the specific user profile
        return await userProfileApi.getProfile(userId);
      } catch (error) {
        console.warn('Could not load user profile, trying default:', error);
        try {
          // Fall back to demo user default if specific user not found
          return await userProfileApi.getProfile('demo-user-123');
        } catch (fallbackError) {
          console.error('Could not load any user profile:', fallbackError);
          return null;
        }
      }
    }
  );

  // Initialize form data when user profile loads
  createEffect(() => {
    const profile = userProfile();
    if (profile) {
      setFormData({
        first_name: profile.first_name || '',
        last_name: profile.last_name || '',
        email: profile.email || '',
        phone: profile.phone || '',
        city: profile.city || '',
        state: profile.state || '',
        country: 'United States', // Default country since backend doesn't store this
        linkedin_url: profile.linkedin_url || '',
        portfolio_url: profile.portfolio_url || '',
        github_url: '', // GitHub URL not in current UserProfile model
      });
      setHasChanges(false);
    }
  });

  const handleInputChange = (field: keyof ContactFormData, value: string) => {
    setFormData(field, value);
    setHasChanges(true);
  };

  const validateUrl = (url: string) => {
    if (!url) return true;
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  };

  const validateEmail = (email: string) => {
    if (!email) return true;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const handleSave = async () => {
    if (!hasChanges()) return;

    // Validate form
    if (!formData.first_name.trim() || !formData.last_name.trim()) {
      alert('First name and last name are required.');
      return;
    }

    if (formData.email && !validateEmail(formData.email)) {
      alert('Please enter a valid email address.');
      return;
    }

    if (formData.linkedin_url && !validateUrl(formData.linkedin_url)) {
      alert('Please enter a valid LinkedIn URL.');
      return;
    }

    if (formData.portfolio_url && !validateUrl(formData.portfolio_url)) {
      alert('Please enter a valid portfolio URL.');
      return;
    }

    if (formData.github_url && !validateUrl(formData.github_url)) {
      alert('Please enter a valid GitHub URL.');
      return;
    }

    setSaving(true);
    try {
      // Update user profile with contact info changes
      const updateData: UserProfileUpdate = {
        first_name: formData.first_name.trim(),
        last_name: formData.last_name.trim(),
        email: formData.email.trim() || undefined,
        phone: formData.phone.trim() || undefined,
        city: formData.city.trim() || undefined,
        state: formData.state.trim() || undefined,
        linkedin_url: formData.linkedin_url.trim() || undefined,
        portfolio_url: formData.portfolio_url.trim() || undefined,
      };

      // Use the user ID from skill bank or fall back to demo user
      const userId = props.skillBank.user_id || 'demo-user-123';
      await userProfileApi.updateProfile(userId, updateData);

      console.log('Contact info updated successfully:', updateData);
      setHasChanges(false);
      props.onUpdate();
    } catch (error) {
      console.error('Error saving contact info:', error);
      alert('Failed to save contact information. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    // Reset form to original profile values
    const profile = userProfile();
    if (profile) {
      setFormData({
        first_name: profile.first_name || '',
        last_name: profile.last_name || '',
        email: profile.email || '',
        phone: profile.phone || '',
        city: profile.city || '',
        state: profile.state || '',
        country: 'United States', // Default country
        linkedin_url: profile.linkedin_url || '',
        portfolio_url: profile.portfolio_url || '',
        github_url: '', // GitHub URL not in current UserProfile model
      });
      setHasChanges(false);
    }
  };

  return (
    <div class='space-y-6'>
      {/* Header */}
      <div class='flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4'>
        <div>
          <h2 class='text-2xl font-bold text-base-content flex items-center gap-2'>
            <svg class='w-6 h-6 text-primary' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
              <path
                stroke-linecap='round'
                stroke-linejoin='round'
                stroke-width='2'
                d='M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z'
              ></path>
            </svg>
            Contact Information
          </h2>
          <p class='text-base-content/70'>Manage your contact details and professional links.</p>
        </div>

        <Show when={hasChanges()}>
          <div class='flex gap-2'>
            <button class='btn btn-ghost' onClick={handleCancel} disabled={saving()}>
              Cancel
            </button>
            <button class='btn btn-primary' onClick={handleSave} disabled={saving()}>
              <Show when={saving()} fallback='Save Changes'>
                <span class='loading loading-spinner loading-sm'></span>
                Saving...
              </Show>
            </button>
          </div>
        </Show>
      </div>

      {/* Loading State */}
      <Show when={userProfile.loading}>
        <div class='card bg-base-100 shadow-lg border border-base-300'>
          <div class='card-body'>
            <div class='flex flex-col items-center justify-center py-12'>
              <span class='loading loading-spinner loading-lg text-primary mb-4'></span>
              <p class='text-base-content/70'>Loading your contact information...</p>
            </div>
          </div>
        </div>
      </Show>

      {/* Error State */}
      <Show when={userProfile.error}>
        <div class='alert alert-error'>
          <svg class='stroke-current shrink-0 h-6 w-6' fill='none' viewBox='0 0 24 24'>
            <path
              stroke-linecap='round'
              stroke-linejoin='round'
              stroke-width='2'
              d='M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z'
            />
          </svg>
          <span>Error loading contact information: {userProfile.error?.message}</span>
        </div>
      </Show>

      {/* Contact Form */}
      <Show when={userProfile() && !userProfile.loading}>
        <div class='card bg-base-100 shadow-lg border border-base-300'>
          <div class='card-body'>
            <div class='space-y-6'>
              {/* Basic Information */}
              <div>
                <h3 class='text-lg font-semibold mb-4'>Basic Information</h3>
                <div class='grid grid-cols-1 md:grid-cols-2 gap-4'>
                  <div class='form-control'>
                    <label class='label'>
                      <span class='label-text'>First Name *</span>
                    </label>
                    <input
                      type='text'
                      placeholder='First name'
                      class='input input-bordered'
                      value={formData.first_name}
                      onInput={e => handleInputChange('first_name', e.currentTarget.value)}
                    />
                  </div>

                  <div class='form-control'>
                    <label class='label'>
                      <span class='label-text'>Last Name *</span>
                    </label>
                    <input
                      type='text'
                      placeholder='Last name'
                      class='input input-bordered'
                      value={formData.last_name}
                      onInput={e => handleInputChange('last_name', e.currentTarget.value)}
                    />
                  </div>

                  <div class='form-control'>
                    <label class='label'>
                      <span class='label-text'>Email</span>
                    </label>
                    <input
                      type='email'
                      placeholder='email@example.com'
                      class='input input-bordered'
                      value={formData.email}
                      onInput={e => handleInputChange('email', e.currentTarget.value)}
                    />
                  </div>

                  <div class='form-control'>
                    <label class='label'>
                      <span class='label-text'>Phone</span>
                    </label>
                    <input
                      type='tel'
                      placeholder='(555) 123-4567'
                      class='input input-bordered'
                      value={formData.phone}
                      onInput={e => handleInputChange('phone', e.currentTarget.value)}
                    />
                  </div>
                </div>
              </div>

              {/* Location Information */}
              <div>
                <h3 class='text-lg font-semibold mb-4'>Location</h3>
                <div class='grid grid-cols-1 md:grid-cols-3 gap-4'>
                  <div class='form-control'>
                    <label class='label'>
                      <span class='label-text'>City</span>
                    </label>
                    <input
                      type='text'
                      placeholder='City'
                      class='input input-bordered'
                      value={formData.city}
                      onInput={e => handleInputChange('city', e.currentTarget.value)}
                    />
                  </div>

                  <div class='form-control'>
                    <label class='label'>
                      <span class='label-text'>State/Province</span>
                    </label>
                    <input
                      type='text'
                      placeholder='State or Province'
                      class='input input-bordered'
                      value={formData.state}
                      onInput={e => handleInputChange('state', e.currentTarget.value)}
                    />
                  </div>

                  <div class='form-control'>
                    <label class='label'>
                      <span class='label-text'>Country</span>
                    </label>
                    <input
                      type='text'
                      placeholder='Country'
                      class='input input-bordered'
                      value={formData.country}
                      onInput={e => handleInputChange('country', e.currentTarget.value)}
                    />
                  </div>
                </div>
              </div>

              {/* Professional Links */}
              <div>
                <h3 class='text-lg font-semibold mb-4'>Professional Links</h3>
                <div class='space-y-4'>
                  <div class='form-control'>
                    <label class='label'>
                      <span class='label-text'>LinkedIn URL</span>
                    </label>
                    <input
                      type='url'
                      placeholder='https://linkedin.com/in/username'
                      class='input input-bordered'
                      value={formData.linkedin_url}
                      onInput={e => handleInputChange('linkedin_url', e.currentTarget.value)}
                    />
                  </div>

                  <div class='form-control'>
                    <label class='label'>
                      <span class='label-text'>Portfolio URL</span>
                    </label>
                    <input
                      type='url'
                      placeholder='https://yourportfolio.com'
                      class='input input-bordered'
                      value={formData.portfolio_url}
                      onInput={e => handleInputChange('portfolio_url', e.currentTarget.value)}
                    />
                  </div>

                  <div class='form-control'>
                    <label class='label'>
                      <span class='label-text'>GitHub URL</span>
                    </label>
                    <input
                      type='url'
                      placeholder='https://github.com/username'
                      class='input input-bordered'
                      value={formData.github_url}
                      onInput={e => handleInputChange('github_url', e.currentTarget.value)}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Show>

      {/* Save prompt at bottom */}
      <Show when={hasChanges()}>
        <div class='alert alert-info'>
          <svg
            xmlns='http://www.w3.org/2000/svg'
            fill='none'
            viewBox='0 0 24 24'
            class='stroke-current shrink-0 w-6 h-6'
          >
            <path
              stroke-linecap='round'
              stroke-linejoin='round'
              stroke-width='2'
              d='M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
            ></path>
          </svg>
          <span>You have unsaved changes. Don't forget to save your updates!</span>
          <div class='flex gap-2'>
            <button class='btn btn-sm btn-ghost' onClick={handleCancel}>
              Cancel
            </button>
            <button class='btn btn-sm btn-primary' onClick={handleSave} disabled={saving()}>
              Save Changes
            </button>
          </div>
        </div>
      </Show>
    </div>
  );
};

export default ContactInfoSection;
