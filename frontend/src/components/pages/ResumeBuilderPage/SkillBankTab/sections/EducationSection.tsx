import { Component, createSignal, createMemo, Show, For } from 'solid-js';
import { createStore } from 'solid-js/store';
import { skillBankApiService } from '../../../../../services/skillBankApi';
import type {
  SkillBankResponse,
  EducationEntry,
  EducationEntryRequest,
} from '../../../../../types/skillBank';

interface EducationSectionProps {
  skillBank: SkillBankResponse;
  onUpdate: () => void;
  loading: boolean;
}

interface EducationFormData {
  institution: string;
  degree: string;
  field_of_study: string;
  location: string;
  start_date: string;
  end_date: string;
  gpa: number | null;
  honors: string[];
  relevant_coursework: string[];
  default_description: string;
}

const skillBankApi = skillBankApiService;

const initialFormData: EducationFormData = {
  institution: '',
  degree: '',
  field_of_study: '',
  location: '',
  start_date: '',
  end_date: '',
  gpa: null,
  honors: [],
  relevant_coursework: [],
  default_description: '',
};

/**
 * Education management section
 */
export const EducationSection: Component<EducationSectionProps> = props => {
  const [showAddForm, setShowAddForm] = createSignal(false);
  const [editingEducation, setEditingEducation] = createSignal<EducationEntry | null>(null);
  const [formData, setFormData] = createStore<EducationFormData>(initialFormData);
  const [saving, setSaving] = createSignal(false);
  // const [expandedEducation, setExpandedEducation] = createSignal<string | null>(null);

  const educationEntries = () => props.skillBank?.education_entries || [];

  const sortedEducation = createMemo(() => {
    return [...educationEntries()].sort((a, b) => {
      const aDate = a.start_date ? new Date(a.start_date).getTime() : 0;
      const bDate = b.start_date ? new Date(b.start_date).getTime() : 0;
      return bDate - aDate;
    });
  });

  const handleAddEducation = () => {
    setFormData(initialFormData);
    setEditingEducation(null);
    setShowAddForm(true);
  };

  const handleEditEducation = (education: EducationEntry) => {
    setFormData({
      institution: education.institution,
      degree: education.degree,
      field_of_study: education.field_of_study || '',
      location: education.location || '',
      start_date: education.start_date || '',
      end_date: education.end_date || '',
      gpa: education.gpa,
      honors: [...education.honors],
      relevant_coursework: [...education.relevant_coursework],
      default_description: education.default_description || '',
    });
    setEditingEducation(education);
    setShowAddForm(true);
  };

  const handleCancelEdit = () => {
    setShowAddForm(false);
    setEditingEducation(null);
    setFormData(initialFormData);
  };

  const handleFormSubmit = async (e: Event) => {
    e.preventDefault();
    if (!formData.institution.trim() || !formData.degree.trim() || !formData.start_date) return;

    setSaving(true);
    try {
      const educationRequest: EducationEntryRequest = {
        institution: formData.institution.trim(),
        degree: formData.degree.trim(),
        field_of_study: formData.field_of_study.trim() || null,
        location: formData.location.trim() || null,
        start_date: formData.start_date,
        end_date: formData.end_date || null,
        gpa: formData.gpa,
        honors: formData.honors.filter(h => h.trim()),
        relevant_coursework: formData.relevant_coursework.filter(c => c.trim()),
        default_description: formData.default_description.trim() || null,
      };

      if (editingEducation()) {
        await skillBankApi.updateEducation(
          props.skillBank.user_id,
          editingEducation()!.id,
          educationRequest
        );
      } else {
        await skillBankApi.addEducation(props.skillBank.user_id, educationRequest);
      }

      props.onUpdate();
      handleCancelEdit();
    } catch (error) {
      console.error('Error saving education:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteEducation = async (education: EducationEntry) => {
    if (
      !confirm(`Are you sure you want to delete "${education.degree} at ${education.institution}"?`)
    )
      return;

    setSaving(true);
    try {
      await skillBankApi.deleteEducation(props.skillBank.user_id, education.id);
      props.onUpdate();
    } catch (error) {
      console.error('Error deleting education:', error);
    } finally {
      setSaving(false);
    }
  };

  // const toggleEducationExpansion = (educationId: string) => {
  //   setExpandedEducation(expandedEducation() === educationId ? null : educationId);
  // };

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
                d='M12 14l9-5-9-5-9 5 9 5z'
              ></path>
              <path
                stroke-linecap='round'
                stroke-linejoin='round'
                stroke-width='2'
                d='M12 14l6.16-3.422A12.083 12.083 0 0121 18.782V12M4.84 10.578A12.083 12.083 0 003 12v6.782'
              ></path>
              <path
                stroke-linecap='round'
                stroke-linejoin='round'
                stroke-width='2'
                d='M12 21v-7'
              ></path>
            </svg>
            Education ({educationEntries().length})
          </h2>
          <p class='text-base-content/70'>Manage your academic background and qualifications.</p>
        </div>
        <button class='btn btn-primary gap-2' onClick={handleAddEducation} disabled={saving()}>
          <svg class='w-4 h-4' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
            <path
              stroke-linecap='round'
              stroke-linejoin='round'
              stroke-width='2'
              d='M12 4v16m8-8H4'
            ></path>
          </svg>
          Add Education
        </button>
      </div>

      {/* Add/Edit Form Modal */}
      <Show when={showAddForm()}>
        <div class='modal modal-open'>
          <div class='modal-box w-11/12 max-w-4xl max-h-screen overflow-y-auto'>
            <h3 class='font-bold text-lg mb-4'>
              {editingEducation() ? 'Edit Education' : 'Add Education'}
            </h3>

            <form onSubmit={handleFormSubmit} class='space-y-4'>
              {/* Basic Information */}
              <div class='grid grid-cols-1 md:grid-cols-2 gap-4'>
                <div class='form-control'>
                  <label class='label'>
                    <span class='label-text'>Institution *</span>
                  </label>
                  <input
                    type='text'
                    placeholder='e.g., University of California, Berkeley'
                    class='input input-bordered'
                    value={formData.institution}
                    onInput={e => setFormData('institution', e.currentTarget.value)}
                    required
                  />
                </div>

                <div class='form-control'>
                  <label class='label'>
                    <span class='label-text'>Degree *</span>
                  </label>
                  <input
                    type='text'
                    placeholder='e.g., Bachelor of Science'
                    class='input input-bordered'
                    value={formData.degree}
                    onInput={e => setFormData('degree', e.currentTarget.value)}
                    required
                  />
                </div>

                <div class='form-control'>
                  <label class='label'>
                    <span class='label-text'>Field of Study</span>
                  </label>
                  <input
                    type='text'
                    placeholder='e.g., Computer Science'
                    class='input input-bordered'
                    value={formData.field_of_study}
                    onInput={e => setFormData('field_of_study', e.currentTarget.value)}
                  />
                </div>

                <div class='form-control'>
                  <label class='label'>
                    <span class='label-text'>Location</span>
                  </label>
                  <input
                    type='text'
                    placeholder='e.g., Berkeley, CA'
                    class='input input-bordered'
                    value={formData.location}
                    onInput={e => setFormData('location', e.currentTarget.value)}
                  />
                </div>

                <div class='form-control'>
                  <label class='label'>
                    <span class='label-text'>Start Date *</span>
                  </label>
                  <input
                    type='month'
                    class='input input-bordered'
                    value={formData.start_date}
                    onChange={e => setFormData('start_date', e.currentTarget.value)}
                    required
                  />
                </div>

                <div class='form-control'>
                  <label class='label'>
                    <span class='label-text'>End Date</span>
                  </label>
                  <input
                    type='month'
                    class='input input-bordered'
                    value={formData.end_date}
                    onChange={e => setFormData('end_date', e.currentTarget.value)}
                  />
                </div>
              </div>
              <div class='form-control'>
                <label class='label'>
                  <span class='label-text'>Description</span>
                </label>
                <textarea
                  class='textarea textarea-bordered h-24'
                  placeholder='Describe your education, relevant coursework, and honors...'
                  value={formData.default_description}
                  onInput={e => setFormData('default_description', e.currentTarget.value)}
                />
              </div>
              <div class='modal-action'>
                <button type='button' class='btn' onClick={handleCancelEdit}>
                  Cancel
                </button>
                <button
                  type='submit'
                  class='btn btn-primary'
                  disabled={
                    saving() ||
                    !formData.institution.trim() ||
                    !formData.degree.trim() ||
                    !formData.start_date
                  }
                >
                  <Show
                    when={saving()}
                    fallback={editingEducation() ? 'Update Education' : 'Add Education'}
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

      {/* Education List */}
      <Show
        when={educationEntries().length > 0}
        fallback={
          <div class='text-center py-16'>
            <div class='text-6xl mb-4'>🎓</div>
            <h3 class='text-xl font-semibold mb-2'>No education added yet</h3>
            <p class='text-base-content/70 mb-6'>
              Add your educational background to build your skill bank.
            </p>
            <button class='btn btn-primary' onClick={handleAddEducation}>
              Add Your First Education Entry
            </button>
          </div>
        }
      >
        <div class='space-y-4'>
          <For each={sortedEducation()}>
            {education => {
              // const isExpanded = () => expandedEducation() === education.id;

              return (
                <div class='card bg-base-100 shadow-lg border border-base-300'>
                  <div class='card-body'>
                    <div class='flex items-start justify-between'>
                      <div class='flex-1 min-w-0'>
                        <div class='flex items-center gap-3 mb-2'>
                          <h3 class='card-title text-lg'>{education.degree}</h3>
                        </div>
                        <p class='text-primary font-medium text-base'>{education.institution}</p>
                        <div class='flex flex-wrap items-center gap-2 mt-2 text-sm text-base-content/70'>
                          <div class='flex items-center gap-1'>
                            {formatDate(education.start_date || '')} -{' '}
                            {formatDate(education.end_date || '')}
                          </div>
                          <Show when={education.location}>
                            <span>•</span>
                            <div class='flex items-center gap-1'>{education.location}</div>
                          </Show>
                        </div>
                      </div>
                      <div class='dropdown dropdown-end'>
                        <label tabindex='0' class='btn btn-ghost btn-xs'>
                          <svg
                            class='w-4 h-4'
                            fill='none'
                            stroke='currentColor'
                            viewBox='0 0 24 24'
                          >
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
                            <button onClick={() => handleEditEducation(education)}>Edit</button>
                          </li>
                          <li>
                            <button
                              class='text-error'
                              onClick={() => handleDeleteEducation(education)}
                            >
                              Delete
                            </button>
                          </li>
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              );
            }}
          </For>
        </div>
      </Show>
    </div>
  );
};

export default EducationSection;
