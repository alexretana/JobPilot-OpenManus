# User Profile Management System

A complete user profile management system built with SolidJS and DaisyUI, designed for the JobPilot-OpenManus project.
This system provides comprehensive profile creation, editing, and management capabilities with real-time completeness
tracking.

## Overview

The User Profile Management System consists of several interconnected components that work together to provide a
seamless user experience:

- **ProfileDashboard**: Main dashboard displaying user profile information
- **ProfileEditForm**: Comprehensive form for editing all profile fields
- **ProfileEditModal**: Modal wrapper for the edit form
- **ProfileCompleteness**: Visual component showing profile completion status
- **ProfileSystemDemo**: Full demonstration of all components

## Components

### ProfileDashboard

The main dashboard component that displays user profile information in a clean, organized layout.

**Features:**

- Displays personal, professional, and preference information
- Real-time profile completeness tracking
- Quick action buttons for common tasks
- Responsive design with mobile support
- Loading and error states

**Props:**

```typescript
interface ProfileDashboardProps {
  userId?: string; // User ID (defaults to demo user)
  onProfileChange?: (profile: UserProfile) => void; // Callback for profile updates
}
```

### ProfileEditForm

A comprehensive tabbed form for editing all profile fields.

**Features:**

- Three-tab interface (Personal, Professional, Preferences)
- Skills management with add/remove functionality
- Location management
- Job type and remote work preferences
- Form validation with error display
- Real-time character counting
- Salary range inputs

**Props:**

```typescript
interface ProfileEditFormProps {
  profile?: UserProfile; // Existing profile data
  onSave: (profile: UserProfile) => void; // Save callback
  onCancel: () => void; // Cancel callback
}
```

### ProfileEditModal

Modal wrapper for the ProfileEditForm with backdrop click handling.

**Props:**

```typescript
interface ProfileEditModalProps {
  isOpen: boolean; // Modal visibility
  profile?: UserProfile; // Profile data
  onSave: (profile: UserProfile) => void; // Save callback
  onClose: () => void; // Close callback
}
```

### ProfileCompleteness

Visual component displaying profile completion statistics and suggestions.

**Features:**

- Overall completion score with color-coded status
- Section-specific completion percentages
- Missing fields alerts
- Improvement suggestions
- Interactive section focusing

**Props:**

```typescript
interface ProfileCompletenessProps {
  completeness: ProfileCompleteness; // Completeness data
  onSectionFocus?: (section: 'personal' | 'professional' | 'preferences') => void;
}
```

## Service Layer

### userProfileApi

The service layer handles all API interactions and business logic:

**Key Methods:**

- `createProfile(data)` - Create new user profile
- `getProfile(userId)` - Get profile by ID
- `updateProfile(userId, updates)` - Update existing profile
- `calculateCompleteness(profile)` - Calculate completion score
- `validateProfile(data)` - Validate profile data

**Types:**

- `UserProfile` - Complete profile interface
- `UserProfileCreate` - Profile creation data
- `UserProfileUpdate` - Profile update data
- `ProfileCompleteness` - Completion tracking data
- `JobType` - Available job types enum
- `RemoteType` - Remote work preferences enum

## Usage Examples

### Basic Profile Dashboard

```tsx
import { ProfileDashboard } from '../components/UserProfile';

const MyComponent = () => {
  return <ProfileDashboard userId='user-123' onProfileChange={profile => console.log('Updated:', profile)} />;
};
```

### Standalone Edit Modal

```tsx
import { ProfileEditModal } from '../components/UserProfile';
import { createSignal } from 'solid-js';

const MyComponent = () => {
  const [showModal, setShowModal] = createSignal(false);
  const [profile, setProfile] = createSignal(null);

  return (
    <>
      <button onClick={() => setShowModal(true)}>Edit Profile</button>

      <ProfileEditModal
        isOpen={showModal()}
        profile={profile()}
        onSave={updated => {
          setProfile(updated);
          setShowModal(false);
        }}
        onClose={() => setShowModal(false)}
      />
    </>
  );
};
```

### Profile Completeness Tracking

```tsx
import { ProfileCompleteness } from '../components/UserProfile';
import { userProfileApi } from '../services/userProfileApi';

const MyComponent = () => {
  const completeness = userProfileApi.calculateCompleteness(profile());

  return <ProfileCompleteness completeness={completeness} onSectionFocus={section => focusSection(section)} />;
};
```

## Data Models

### User Profile Structure

```typescript
interface UserProfile {
  id: string;

  // Personal Information
  first_name?: string;
  last_name?: string;
  email?: string;
  phone?: string;

  // Professional Information
  current_title?: string;
  experience_years?: number;
  skills: string[];
  education?: string;
  bio?: string;

  // Job Preferences
  preferred_locations: string[];
  preferred_job_types: JobType[];
  preferred_remote_types: RemoteType[];
  desired_salary_min?: number;
  desired_salary_max?: number;

  // System Fields
  created_at: string;
  updated_at: string;
}
```

## Backend Integration

The system integrates with the following backend endpoints:

- `POST /api/users` - Create new profile
- `GET /api/users/{id}` - Get profile by ID
- `PUT /api/users/{id}` - Update profile
- `GET /api/users/search/by-email` - Find profile by email
- `GET /api/users` - List profiles (paginated)
- `DELETE /api/users/{id}` - Delete profile

## Validation Rules

### Required Fields (Create)

- `last_name` - User's last name
- `email` - Valid email address
- `skills` - At least one skill
- `preferred_job_types` - At least one job type
- `preferred_remote_types` - At least one remote preference

### Optional Fields

- `first_name`, `phone`, `current_title`, `experience_years`
- `education`, `bio`, `preferred_locations`
- `desired_salary_min`, `desired_salary_max`

### Validation Logic

- Email format validation
- Experience years range (0-50)
- Salary range validation (min ≤ max)
- Skill and preference array validation

## Completeness Calculation

The system calculates profile completeness based on three sections:

**Personal Section (33%):**

- First name, last name, email

**Professional Section (33%):**

- Current title, experience years, skills, bio

**Preferences Section (33%):**

- Preferred locations, job types, remote types

**Scoring:**

- Each section is scored independently
- Overall score is the average of all sections
- Missing required fields reduce section scores
- Optional fields generate suggestions but don't affect scores

## Styling and Theming

The components use DaisyUI classes for consistent styling:

- **Cards**: `card bg-base-100 shadow-xl`
- **Forms**: `form-control`, `input input-bordered`
- **Buttons**: `btn btn-primary`, `btn btn-outline`
- **Badges**: `badge badge-primary`, `badge badge-secondary`
- **Alerts**: `alert alert-error`, `alert alert-info`
- **Progress**: `progress progress-success`

## Error Handling

The system includes comprehensive error handling:

- **Network errors**: API connection failures
- **Validation errors**: Form field validation
- **Not found errors**: Missing profile data
- **Permission errors**: Unauthorized access
- **Loading states**: Skeleton loaders and spinners

## Accessibility

All components are built with accessibility in mind:

- Proper ARIA labels and roles
- Keyboard navigation support
- Screen reader compatibility
- High contrast color schemes
- Focus management in modals

## Testing

The system can be tested using the included demo component:

```tsx
import { ProfileSystemDemo } from '../components/UserProfile';

// Comprehensive demo with all features
<ProfileSystemDemo />;
```

The demo includes:

- Full dashboard testing
- Modal interaction testing
- Completeness comparison
- Complete vs incomplete profile examples

## Future Enhancements

Planned improvements for the system:

1. **Photo Upload**: Profile picture management
2. **Resume Integration**: Link to resume builder
3. **Skills Autocomplete**: Suggest skills based on job market data
4. **Location Search**: Geographic location picker
5. **Social Links**: LinkedIn, GitHub, portfolio links
6. **Privacy Settings**: Control profile visibility
7. **Profile Export**: Download profile data
8. **Bulk Import**: Import from LinkedIn/resume

This system provides a solid foundation for user profile management and can be easily extended to meet future
requirements.
