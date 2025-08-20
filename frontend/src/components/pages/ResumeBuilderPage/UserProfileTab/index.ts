export { default as ProfileDashboard } from './ProfileDashboard';
export { default as ProfileEditForm } from './ProfileEditForm';
export { default as ProfileEditModal } from './ProfileEditModal';
export { default as ProfileCompleteness } from './ProfileCompleteness';

// Re-export types from the service layer
export type {
  UserProfile,
  UserProfileCreate,
  UserProfileUpdate,
  ProfileCompleteness as ProfileCompletenessType,
  JobType,
  RemoteType,
} from '../../../../services/userProfileApi';
