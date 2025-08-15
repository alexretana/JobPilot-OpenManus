import { Component } from 'solid-js';
import { ProfileDashboard } from '../components/UserProfile';

const ProfileTestPage: Component = () => {
  const handleProfileChange = (profile: any) => {
    console.log('Profile updated:', profile);
  };

  return (
    <div class="min-h-screen bg-base-200">
      <ProfileDashboard userId="demo-user-123" onProfileChange={handleProfileChange} />
    </div>
  );
};

export default ProfileTestPage;
