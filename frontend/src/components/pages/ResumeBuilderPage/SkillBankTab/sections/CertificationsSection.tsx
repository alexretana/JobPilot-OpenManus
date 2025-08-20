import { Component, createSignal, createMemo, Show, For } from 'solid-js';
import { createStore } from 'solid-js/store';
import { skillBankApiService } from '../../../../../services/skillBankApi';
import type {
  SkillBankResponse,
  Certification,
  CertificationRequest,
} from '../../../../../types/skillBank';

interface CertificationsSectionProps {
  skillBank: SkillBankResponse;
  onUpdate: () => void;
  loading: boolean;
}

interface CertificationFormData {
  name: string;
  issuer: string;
  issue_date: string;
  expiry_date: string;
  credential_id: string;
  url: string;
  description: string;
}

const skillBankApi = skillBankApiService;

const initialFormData: CertificationFormData = {
  name: '',
  issuer: '',
  issue_date: '',
  expiry_date: '',
  credential_id: '',
  url: '',
  description: '',
};

/**
 * Certifications management section
 */
export const CertificationsSection: Component<CertificationsSectionProps> = props => {
  const [showAddForm, setShowAddForm] = createSignal(false);
  const [editingCertification, setEditingCertification] = createSignal<Certification | null>(null);
  const [formData, setFormData] = createStore<CertificationFormData>(initialFormData);
  const [saving, setSaving] = createSignal(false);

  const certifications = () => props.skillBank?.certifications || [];

  const sortedCertifications = createMemo(() => {
    return [...certifications()].sort((a, b) => {
      const aDate = a.issue_date ? new Date(a.issue_date).getTime() : 0;
      const bDate = b.issue_date ? new Date(b.issue_date).getTime() : 0;
      return bDate - aDate;
    });
  });

  const handleAddCertification = () => {
    setFormData(initialFormData);
    setEditingCertification(null);
    setShowAddForm(true);
  };

  const handleEditCertification = (certification: Certification) => {
    setFormData({
      name: certification.name,
      issuer: certification.issuer,
      issue_date: certification.issue_date || '',
      expiry_date: certification.expiry_date || '',
      credential_id: certification.credential_id || '',
      url: certification.url || '',
      description: certification.description || '',
    });
    setEditingCertification(certification);
    setShowAddForm(true);
  };

  const handleCancelEdit = () => {
    setShowAddForm(false);
    setEditingCertification(null);
    setFormData(initialFormData);
  };

  const handleFormSubmit = async (e: Event) => {
    e.preventDefault();
    if (!formData.name.trim() || !formData.issuer.trim()) return;

    setSaving(true);
    try {
      const certificationRequest: CertificationRequest = {
        name: formData.name.trim(),
        issuer: formData.issuer.trim(),
        issue_date: formData.issue_date || null,
        expiry_date: formData.expiry_date || null,
        credential_id: formData.credential_id.trim() || null,
        url: formData.url.trim() || null,
        description: formData.description.trim() || null,
      };

      if (editingCertification()) {
        await skillBankApi.updateCertification(
          props.skillBank.user_id,
          editingCertification()!.id,
          certificationRequest
        );
      } else {
        await skillBankApi.addCertification(props.skillBank.user_id, certificationRequest);
      }

      props.onUpdate();
      handleCancelEdit();
    } catch (error) {
      console.error('Error saving certification:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteCertification = async (certification: Certification) => {
    if (!confirm(`Are you sure you want to delete "${certification.name}"?`)) return;

    setSaving(true);
    try {
      await skillBankApi.deleteCertification(props.skillBank.user_id, certification.id);
      props.onUpdate();
    } catch (error) {
      console.error('Error deleting certification:', error);
    } finally {
      setSaving(false);
    }
  };

  const formatDate = (dateStr: string) => {
    if (!dateStr) return '';
    try {
      const date = new Date(dateStr + '-01');
      return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long' });
    } catch {
      return dateStr;
    }
  };

  return (
    <div class='space-y-6'>
      {/* Header with Actions */}
      <div class='flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4'>
        <div>
          <h2 class='text-2xl font-bold text-base-content flex items-center gap-2'>
            <svg class='w-6 h-6 text-primary' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
              <path
                stroke-linecap='round'
                stroke-linejoin='round'
                stroke-width='2'
                d='M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z'
              ></path>
            </svg>
            Certifications ({certifications().length})
          </h2>
          <p class='text-base-content/70'>List your professional certifications and credentials.</p>
        </div>
        <button class='btn btn-primary gap-2' onClick={handleAddCertification} disabled={saving()}>
          <svg class='w-4 h-4' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
            <path
              stroke-linecap='round'
              stroke-linejoin='round'
              stroke-width='2'
              d='M12 4v16m8-8H4'
            ></path>
          </svg>
          Add Certification
        </button>
      </div>

      {/* Add/Edit Form Modal */}
      <Show when={showAddForm()}>
        <div class='modal modal-open'>
          <div class='modal-box w-11/12 max-w-4xl max-h-screen overflow-y-auto'>
            <h3 class='font-bold text-lg mb-4'>
              {editingCertification() ? 'Edit Certification' : 'Add Certification'}
            </h3>

            <form onSubmit={handleFormSubmit} class='space-y-4'>
              {/* Basic Information */}
              <div class='grid grid-cols-1 md:grid-cols-2 gap-4'>
                <div class='form-control'>
                  <label class='label'>
                    <span class='label-text'>Certification Name *</span>
                  </label>
                  <input
                    type='text'
                    placeholder='e.g., Certified Kubernetes Administrator'
                    class='input input-bordered'
                    value={formData.name}
                    onInput={e => setFormData('name', e.currentTarget.value)}
                    required
                  />
                </div>

                <div class='form-control'>
                  <label class='label'>
                    <span class='label-text'>Issuer *</span>
                  </label>
                  <input
                    type='text'
                    placeholder='e.g., The Linux Foundation'
                    class='input input-bordered'
                    value={formData.issuer}
                    onInput={e => setFormData('issuer', e.currentTarget.value)}
                    required
                  />
                </div>

                <div class='form-control'>
                  <label class='label'>
                    <span class='label-text'>Issue Date</span>
                  </label>
                  <input
                    type='month'
                    class='input input-bordered'
                    value={formData.issue_date}
                    onChange={e => setFormData('issue_date', e.currentTarget.value)}
                  />
                </div>

                <div class='form-control'>
                  <label class='label'>
                    <span class='label-text'>Expiration Date</span>
                  </label>
                  <input
                    type='month'
                    class='input input-bordered'
                    value={formData.expiry_date}
                    onChange={e => setFormData('expiry_date', e.currentTarget.value)}
                  />
                </div>

                <div class='form-control'>
                  <label class='label'>
                    <span class='label-text'>Credential ID</span>
                  </label>
                  <input
                    type='text'
                    placeholder='e.g., LF-123456'
                    class='input input-bordered'
                    value={formData.credential_id}
                    onInput={e => setFormData('credential_id', e.currentTarget.value)}
                  />
                </div>

                <div class='form-control'>
                  <label class='label'>
                    <span class='label-text'>Credential URL</span>
                  </label>
                  <input
                    type='url'
                    placeholder='https://example.com/credential'
                    class='input input-bordered'
                    value={formData.url}
                    onInput={e => setFormData('url', e.currentTarget.value)}
                  />
                </div>
              </div>
              <div class='form-control'>
                <label class='label'>
                  <span class='label-text'>Description</span>
                </label>
                <textarea
                  class='textarea textarea-bordered h-24'
                  placeholder='Describe the certification...'
                  value={formData.description}
                  onInput={e => setFormData('description', e.currentTarget.value)}
                />
              </div>
              <div class='modal-action'>
                <button type='button' class='btn' onClick={handleCancelEdit}>
                  Cancel
                </button>
                <button
                  type='submit'
                  class='btn btn-primary'
                  disabled={saving() || !formData.name.trim() || !formData.issuer.trim()}
                >
                  <Show
                    when={saving()}
                    fallback={editingCertification() ? 'Update Certification' : 'Add Certification'}
                  >
                    <span class='loading loading-spinner loading-sm'></span>
                    Saving...
                  </Show>
                </button>
              </div>
            </form>
          </div>
        </div>
      </Show>

      {/* Certifications List */}
      <Show
        when={certifications().length > 0}
        fallback={
          <div class='text-center py-16'>
            <div class='text-6xl mb-4'>📜</div>
            <h3 class='text-xl font-semibold mb-2'>No certifications added yet</h3>
            <p class='text-base-content/70 mb-6'>
              Add your certifications to showcase your qualifications.
            </p>
            <button class='btn btn-primary' onClick={handleAddCertification}>
              Add Your First Certification
            </button>
          </div>
        }
      >
        <div class='space-y-4'>
          <For each={sortedCertifications()}>
            {certification => (
              <div class='card bg-base-100 shadow-lg border border-base-300'>
                <div class='card-body'>
                  <div class='flex items-start justify-between'>
                    <div class='flex-1 min-w-0'>
                      <h3 class='card-title text-lg'>{certification.name}</h3>
                      <p class='text-primary font-medium text-base'>{certification.issuer}</p>
                      <div class='flex flex-wrap items-center gap-2 mt-2 text-sm text-base-content/70'>
                        <div class='flex items-center gap-1'>
                          Issued: {formatDate(certification.issue_date || '')}
                        </div>
                        <Show when={certification.expiry_date}>
                          <span>•</span>
                          <div class='flex items-center gap-1'>
                            Expires: {formatDate(certification.expiry_date || '')}
                          </div>
                        </Show>
                      </div>
                    </div>
                    <div class='dropdown dropdown-end'>
                      <label tabindex='0' class='btn btn-ghost btn-xs'>
                        <svg class='w-4 h-4' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
                          <path
                            stroke-linecap='round'
                            stroke-linejoin='round'
                            stroke-width='2'
                            d='M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z'
                          ></path>
                        </svg>
                      </label>
                      <ul
                        tabindex='0'
                        class='dropdown-content menu p-2 shadow bg-base-100 rounded-box w-52 z-10'
                      >
                        <li>
                          <button onClick={() => handleEditCertification(certification)}>
                            Edit
                          </button>
                        </li>
                        <li>
                          <button
                            class='text-error'
                            onClick={() => handleDeleteCertification(certification)}
                          >
                            Delete
                          </button>
                        </li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </For>
        </div>
      </Show>
    </div>
  );
};

export default CertificationsSection;
