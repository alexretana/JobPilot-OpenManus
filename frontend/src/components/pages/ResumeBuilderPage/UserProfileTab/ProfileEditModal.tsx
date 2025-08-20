import { Component, Show } from 'solid-js';
import { UserProfile } from '../../../../services/userProfileApi';
import ProfileEditForm from './ProfileEditForm';

interface ProfileEditModalProps {
  isOpen: boolean;
  profile?: UserProfile; // If editing existing profile
  onSave: (profile: UserProfile) => void;
  onClose: () => void;
}

const ProfileEditModal: Component<ProfileEditModalProps> = props => {
  const handleBackdropClick = (e: MouseEvent) => {
    if (e.target === e.currentTarget) {
      props.onClose();
    }
  };

  return (
    <Show when={props.isOpen}>
      <div class='modal modal-open' onClick={handleBackdropClick}>
        <div class='modal-box max-w-4xl w-full max-h-[90vh] overflow-auto'>
          <ProfileEditForm
            profile={props.profile}
            onSave={profile => {
              props.onSave(profile);
              props.onClose();
            }}
            onCancel={props.onClose}
          />
        </div>
      </div>
    </Show>
  );
};

export default ProfileEditModal;
