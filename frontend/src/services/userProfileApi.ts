/**
 * User Profile API Service
 * Service for interacting with user profile endpoints
 */

// Enums matching backend
export type JobType =
  | 'Full-time'
  | 'Part-time'
  | 'Contract'
  | 'Freelance'
  | 'Internship'
  | 'Temporary';

export type RemoteType = 'On-site' | 'Remote' | 'Hybrid';

export interface UserProfile {
  id: string;
  first_name?: string;
  last_name?: string;
  email?: string;
  phone?: string;
  city?: string;
  state?: string;
  linkedin_url?: string;
  portfolio_url?: string;
  current_title?: string;
  experience_years?: number;
  skills: string[];
  education?: string;
  bio?: string;
  preferred_locations: string[];
  preferred_job_types: JobType[];
  preferred_remote_types: RemoteType[];
  desired_salary_min?: number;
  desired_salary_max?: number;
  created_at: string;
  updated_at: string;
}

export interface UserProfileCreate {
  first_name?: string;
  last_name: string; // Required
  email: string; // Required (EmailStr)
  phone?: string;
  city?: string;
  state?: string;
  linkedin_url?: string;
  portfolio_url?: string;
  current_title?: string;
  experience_years?: number;
  skills: string[]; // Required (non-empty)
  education?: string;
  bio?: string;
  preferred_locations?: string[];
  preferred_job_types: JobType[]; // Required (non-empty)
  preferred_remote_types: RemoteType[]; // Required (non-empty)
  desired_salary_min?: number;
  desired_salary_max?: number;
}

export interface UserProfileUpdate {
  first_name?: string;
  last_name?: string;
  email?: string;
  phone?: string;
  city?: string;
  state?: string;
  linkedin_url?: string;
  portfolio_url?: string;
  current_title?: string;
  experience_years?: number;
  skills?: string[];
  education?: string;
  bio?: string;
  preferred_locations?: string[];
  preferred_job_types?: JobType[];
  preferred_remote_types?: RemoteType[];
  desired_salary_min?: number;
  desired_salary_max?: number;
}

export interface ProfileCompleteness {
  overall_score: number; // 0-100
  missing_fields: string[];
  suggestions: string[];
  sections: {
    personal: number;
    professional: number;
    preferences: number;
  };
}

class UserProfileApiService {
  private baseUrl = window.location.origin;

  /**
   * Create a new user profile
   */
  async createProfile(profileData: UserProfileCreate): Promise<UserProfile> {
    const response = await fetch(`${this.baseUrl}/api/users`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(profileData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || `Failed to create profile: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get user profile by ID
   */
  async getProfile(userId: string): Promise<UserProfile> {
    const response = await fetch(`${this.baseUrl}/api/users/${userId}`);

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('User profile not found');
      }
      throw new Error(`Failed to fetch profile: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get default user profile (for single-user mode)
   */
  async getDefaultProfile(): Promise<UserProfile> {
    const response = await fetch(`${this.baseUrl}/api/users/default`);

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Default user profile not found');
      }
      throw new Error(`Failed to fetch default profile: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Alias for getProfile - for backward compatibility
   */
  async getProfileById(userId: string): Promise<UserProfile> {
    return this.getProfile(userId);
  }

  /**
   * Update user profile
   */
  async updateProfile(userId: string, updates: UserProfileUpdate): Promise<UserProfile> {
    const response = await fetch(`${this.baseUrl}/api/users/${userId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updates),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || `Failed to update profile: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * List all user profiles (with pagination)
   */
  async listProfiles(limit: number = 20, offset: number = 0): Promise<UserProfile[]> {
    const response = await fetch(`${this.baseUrl}/api/users?limit=${limit}&offset=${offset}`);

    if (!response.ok) {
      throw new Error(`Failed to list profiles: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get user profile by email
   */
  async getProfileByEmail(email: string): Promise<UserProfile> {
    const response = await fetch(
      `${this.baseUrl}/api/users/search/by-email?email=${encodeURIComponent(email)}`
    );

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('User profile not found');
      }
      throw new Error(`Failed to find profile by email: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Delete user profile
   */
  async deleteProfile(userId: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}/api/users/${userId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('User profile not found');
      }
      throw new Error(`Failed to delete profile: ${response.statusText}`);
    }
  }

  /**
   * Calculate profile completeness score
   */
  calculateCompleteness(profile: UserProfile): ProfileCompleteness {
    const requiredFields = {
      personal: ['first_name', 'last_name', 'email'],
      professional: ['current_title', 'experience_years', 'bio'], // Removed 'skills' - now handled by Skill Bank
      preferences: ['preferred_locations', 'preferred_job_types', 'preferred_remote_types'],
    };

    const optionalFields = [
      'phone',
      'city',
      'state',
      'linkedin_url',
      'portfolio_url',
      'education',
      'desired_salary_min',
      'desired_salary_max',
    ];

    let totalFields = 0;
    let completedFields = 0;
    const missing: string[] = [];
    const suggestions: string[] = [];

    // Calculate section scores
    const sectionScores = {
      personal: 0,
      professional: 0,
      preferences: 0,
    };

    // Personal section
    const personalTotal = requiredFields.personal.length;
    let personalCompleted = 0;
    for (const field of requiredFields.personal) {
      const value = profile[field as keyof UserProfile];
      if (value && (typeof value === 'string' ? value.trim() : true)) {
        personalCompleted++;
        completedFields++;
      } else {
        missing.push(this.getFieldDisplayName(field));
      }
      totalFields++;
    }
    sectionScores.personal = Math.round((personalCompleted / personalTotal) * 100);

    // Professional section
    const professionalTotal = requiredFields.professional.length;
    let professionalCompleted = 0;
    for (const field of requiredFields.professional) {
      const value = profile[field as keyof UserProfile];
      if (value && (typeof value === 'string' ? value.trim() : true)) {
        professionalCompleted++;
        completedFields++;
      } else {
        missing.push(this.getFieldDisplayName(field));
      }
      totalFields++;
    }
    sectionScores.professional = Math.round((professionalCompleted / professionalTotal) * 100);

    // Preferences section
    const preferencesTotal = requiredFields.preferences.length;
    let preferencesCompleted = 0;
    for (const field of requiredFields.preferences) {
      const value = profile[field as keyof UserProfile];
      if (Array.isArray(value) && value.length > 0) {
        preferencesCompleted++;
        completedFields++;
      } else {
        missing.push(this.getFieldDisplayName(field));
      }
      totalFields++;
    }
    sectionScores.preferences = Math.round((preferencesCompleted / preferencesTotal) * 100);

    // Check optional fields for suggestions
    for (const field of optionalFields) {
      const value = profile[field as keyof UserProfile];
      if (!value || (typeof value === 'string' && !value.trim())) {
        suggestions.push(
          `Consider adding ${this.getFieldDisplayName(field)} to strengthen your profile`
        );
      }
    }

    // Additional suggestions based on profile state
    if (!profile.skills || profile.skills.length < 3) {
      suggestions.push(
        'Visit the Skill Bank to add and manage your skills for better job matching'
      );
    }

    if (!profile.bio || profile.bio.length < 50) {
      suggestions.push('Write a more detailed professional summary (at least 50 characters)');
    }

    if (profile.preferred_locations && profile.preferred_locations.length === 0) {
      suggestions.push('Specify preferred job locations to find relevant opportunities');
    }

    const overallScore = Math.round((completedFields / totalFields) * 100);

    return {
      overall_score: overallScore,
      missing_fields: missing,
      suggestions,
      sections: sectionScores,
    };
  }

  /**
   * Get display name for field
   */
  private getFieldDisplayName(field: string): string {
    const displayNames: Record<string, string> = {
      first_name: 'First Name',
      last_name: 'Last Name',
      email: 'Email Address',
      phone: 'Phone Number',
      city: 'City',
      state: 'State',
      linkedin_url: 'LinkedIn Profile',
      portfolio_url: 'Portfolio URL',
      current_title: 'Current Job Title',
      experience_years: 'Years of Experience',
      skills: 'Skills',
      education: 'Education',
      bio: 'Professional Summary',
      preferred_locations: 'Preferred Locations',
      preferred_job_types: 'Preferred Job Types',
      preferred_remote_types: 'Remote Work Preferences',
      desired_salary_min: 'Minimum Desired Salary',
      desired_salary_max: 'Maximum Desired Salary',
    };

    return displayNames[field] || field;
  }

  /**
   * Get default job types for dropdowns
   */
  getJobTypes(): JobType[] {
    return ['Full-time', 'Part-time', 'Contract', 'Freelance', 'Internship', 'Temporary'];
  }

  /**
   * Get default remote types for dropdowns
   */
  getRemoteTypes(): RemoteType[] {
    return ['On-site', 'Remote', 'Hybrid'];
  }

  /**
   * Format salary range for display
   */
  formatSalaryRange(min?: number, max?: number): string {
    if (!min && !max) return 'Not specified';

    if (min && max) {
      return `$${min.toLocaleString()} - $${max.toLocaleString()}`;
    }

    if (min) {
      return `$${min.toLocaleString()}+`;
    }

    if (max) {
      return `Up to $${max.toLocaleString()}`;
    }

    return 'Not specified';
  }

  /**
   * Validate email format
   */
  isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  /**
   * Validate profile data before submission
   */
  validateProfile(profile: UserProfileCreate): string[] {
    const errors: string[] = [];

    // Required fields
    if (!profile.last_name?.trim()) {
      errors.push('Last name is required');
    }

    if (!profile.email?.trim()) {
      errors.push('Email is required');
    } else if (!this.isValidEmail(profile.email)) {
      errors.push('Please enter a valid email address');
    }

    // Skills are now managed through the Skill Bank feature
    // Keep backward compatibility but don't require skills in profile creation/update

    if (!profile.preferred_job_types || profile.preferred_job_types.length === 0) {
      errors.push('At least one preferred job type is required');
    }

    if (!profile.preferred_remote_types || profile.preferred_remote_types.length === 0) {
      errors.push('At least one remote work preference is required');
    }

    // Optional validation
    if (
      profile.experience_years &&
      (profile.experience_years < 0 || profile.experience_years > 50)
    ) {
      errors.push('Experience years must be between 0 and 50');
    }

    if (
      profile.desired_salary_min &&
      profile.desired_salary_max &&
      profile.desired_salary_min > profile.desired_salary_max
    ) {
      errors.push('Minimum salary cannot be higher than maximum salary');
    }

    return errors;
  }
}

// Export singleton instance
export const userProfileApi = new UserProfileApiService();
