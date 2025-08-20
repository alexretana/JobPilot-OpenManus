import { Component, createSignal, createMemo, Show, For } from 'solid-js';
import { createStore } from 'solid-js/store';
import { skillBankApiService } from '../../../../../services/skillBankApi';
import type {
  SkillBankResponse,
  ExperienceEntry,
  ExperienceEntryRequest,
} from '../../../../../types/skillBank';
import { ExperienceType } from '../../../../../types/skillBank';

interface ExperienceSectionProps {
  skillBank: SkillBankResponse;
  onUpdate: () => void;
  loading: boolean;
}

interface ExperienceFormData {
  company: string;
  position: string;
  location: string;
  start_date: string;
  end_date: string;
  is_current: boolean;
  experience_type: ExperienceType;
  default_description: string;
  default_achievements: string[];
  skills_used: string[];
  technologies: string[];
}

const skillBankApi = skillBankApiService;

const experienceTypes = [
  { value: 'full_time' as const, label: 'Full Time', color: 'badge-primary' },
  { value: 'part_time' as const, label: 'Part Time', color: 'badge-secondary' },
  { value: 'contract' as const, label: 'Contract', color: 'badge-info' },
  { value: 'freelance' as const, label: 'Freelance', color: 'badge-warning' },
  { value: 'internship' as const, label: 'Internship', color: 'badge-accent' },
  { value: 'volunteer' as const, label: 'Volunteer', color: 'badge-success' },
];

const initialFormData: ExperienceFormData = {
  company: '',
  position: '',
  location: '',
  start_date: '',
  end_date: '',
  is_current: false,
  experience_type: ExperienceType.FULL_TIME,
  default_description: '',
  default_achievements: [],
  skills_used: [],
  technologies: [],
};

/**
 * Work experience management section
 */
export const ExperienceSection: Component<ExperienceSectionProps> = props => {
  const [showAddForm, setShowAddForm] = createSignal(false);
  const [editingExperience, setEditingExperience] = createSignal<ExperienceEntry | null>(null);
  const [formData, setFormData] = createStore<ExperienceFormData>(initialFormData);
  const [saving, setSaving] = createSignal(false);
  const [expandedExperience, setExpandedExperience] = createSignal<string | null>(null);
  const [currentListItem, setCurrentListItem] = createSignal('');
  const [currentListType, setCurrentListType] = createSignal<
    'achievements' | 'skills' | 'technologies'
  >('achievements');

  const experiences = () => props.skillBank?.work_experiences || [];

  // Sort experiences by start date (most recent first)
  const sortedExperiences = createMemo(() => {
    return [...experiences()].sort(
      (a, b) => new Date(b.start_date).getTime() - new Date(a.start_date).getTime()
    );
  });

  const handleAddExperience = () => {
    setFormData(initialFormData);
    setEditingExperience(null);
    setShowAddForm(true);
  };

  const handleEditExperience = (experience: ExperienceEntry) => {
    setFormData({
      company: experience.company,
      position: experience.position,
      location: experience.location || '',
      start_date: experience.start_date,
      end_date: experience.end_date || '',
      is_current: experience.is_current,
      experience_type: experience.experience_type,
      default_description: experience.default_description || '',
      default_achievements: [...experience.default_achievements],
      skills_used: [...experience.skills_used],
      technologies: [...experience.technologies],
    });
    setEditingExperience(experience);
    setShowAddForm(true);
  };

  const handleCancelEdit = () => {
    setShowAddForm(false);
    setEditingExperience(null);
    setFormData(initialFormData);
  };

  const handleFormSubmit = async (e: Event) => {
    e.preventDefault();
    if (!formData.company.trim() || !formData.position.trim() || !formData.start_date) return;

    setSaving(true);
    try {
      const experienceRequest: ExperienceEntryRequest = {
        company: formData.company.trim(),
        position: formData.position.trim(),
        location: formData.location.trim() || null,
        start_date: formData.start_date,
        end_date: formData.is_current ? null : formData.end_date || null,
        is_current: formData.is_current,
        experience_type: formData.experience_type,
        default_description: formData.default_description.trim() || null,
        default_achievements: formData.default_achievements.filter(a => a.trim()),
        skills_used: formData.skills_used.filter(s => s.trim()),
        technologies: formData.technologies.filter(t => t.trim()),
      };

      if (editingExperience()) {
        await skillBankApi.updateExperience(
          props.skillBank.user_id,
          editingExperience()!.id,
          experienceRequest
        );
      } else {
        await skillBankApi.addExperience(props.skillBank.user_id, experienceRequest);
      }

      props.onUpdate();
      handleCancelEdit();
    } catch (error) {
      console.error('Error saving experience:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteExperience = async (experience: ExperienceEntry) => {
    if (
      !confirm(`Are you sure you want to delete "${experience.position} at ${experience.company}"?`)
    )
      return;

    setSaving(true);
    try {
      await skillBankApi.deleteExperience(props.skillBank.user_id, experience.id);
      props.onUpdate();
    } catch (error) {
      console.error('Error deleting experience:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleAddListItem = () => {
    const item = currentListItem().trim();
    if (!item) return;

    const field =
      currentListType() === 'achievements'
        ? 'default_achievements'
        : currentListType() === 'skills'
        ? 'skills_used'
        : 'technologies';

    if (!formData[field].includes(item)) {
      setFormData(field, [...formData[field], item]);
      setCurrentListItem('');
    }
  };

  const handleRemoveListItem = (
    field: 'default_achievements' | 'skills_used' | 'technologies',
    item: string
  ) => {
    setFormData(
      field,
      formData[field].filter(i => i !== item)
    );
  };

  const handleListItemKeyPress = (e: KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddListItem();
    }
  };

  const toggleExperienceExpansion = (experienceId: string) => {
    setExpandedExperience(expandedExperience() === experienceId ? null : experienceId);
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

  const calculateDuration = (start: string, end: string | null) => {
    if (!start) return '';

    try {
      const startDate = new Date(start + '-01');
      const endDate = end ? new Date(end + '-01') : new Date();

      const months =
        (endDate.getFullYear() - startDate.getFullYear()) * 12 +
        (endDate.getMonth() - startDate.getMonth());

      if (months < 1) return '1 month';
      if (months < 12) return `${months} month${months !== 1 ? 's' : ''}`;

      const years = Math.floor(months / 12);
      const remainingMonths = months % 12;

      let duration = `${years} year${years !== 1 ? 's' : ''}`;
      if (remainingMonths > 0) {
        duration += ` ${remainingMonths} month${remainingMonths !== 1 ? 's' : ''}`;
      }

      return duration;
    } catch {
      return '';
    }
  };

  const getExperienceTypeBadge = (type: ExperienceType) => {
    const typeConfig = experienceTypes.find(t => t.value === type);
    return { label: typeConfig?.label || type, color: typeConfig?.color || 'badge-neutral' };
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
                d='M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2-2v2m8 0V6a2 2 0 012 2v6a2 2 0 01-2 2H6a2 2 0 01-2-2V8a2 2 0 012-2V6z'
              />
            </svg>
            Work Experience ({experiences().length})
          </h2>
          <p class='text-base-content/70'>
            Manage your professional work history and create content variations
          </p>
        </div>
        <button class='btn btn-primary gap-2' onClick={handleAddExperience} disabled={saving()}>
          <svg class='w-4 h-4' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
            <path
              stroke-linecap='round'
              stroke-linejoin='round'
              stroke-width='2'
              d='M12 4v16m8-8H4'
            />
          </svg>
          Add Experience
        </button>
      </div>

      {/* Add/Edit Form Modal */}
      <Show when={showAddForm()}>
        <div class='modal modal-open'>
          <div class='modal-box w-11/12 max-w-4xl max-h-screen overflow-y-auto'>
            <h3 class='font-bold text-lg mb-4'>
              {editingExperience() ? 'Edit Work Experience' : 'Add Work Experience'}
            </h3>

            <form onSubmit={handleFormSubmit} class='space-y-4'>
              {/* Basic Information */}
              <div class='grid grid-cols-1 md:grid-cols-2 gap-4'>
                <div class='form-control'>
                  <label class='label'>
                    <span class='label-text'>Company *</span>
                  </label>
                  <input
                    type='text'
                    placeholder='e.g., Google, Microsoft, Acme Corp'
                    class='input input-bordered'
                    value={formData.company}
                    onInput={e => setFormData('company', e.currentTarget.value)}
                    required
                  />
                </div>

                <div class='form-control'>
                  <label class='label'>
                    <span class='label-text'>Job Title *</span>
                  </label>
                  <input
                    type='text'
                    placeholder='e.g., Senior Software Engineer'
                    class='input input-bordered'
                    value={formData.position}
                    onInput={e => setFormData('position', e.currentTarget.value)}
                    required
                  />
                </div>

                <div class='form-control'>
                  <label class='label'>
                    <span class='label-text'>Location</span>
                  </label>
                  <input
                    type='text'
                    placeholder='e.g., San Francisco, CA or Remote'
                    class='input input-bordered'
                    value={formData.location}
                    onInput={e => setFormData('location', e.currentTarget.value)}
                  />
                </div>

                <div class='form-control'>
                  <label class='label'>
                    <span class='label-text'>Employment Type</span>
                  </label>
                  <select
                    class='select select-bordered'
                    value={formData.experience_type}
                    onChange={e =>
                      setFormData('experience_type', e.currentTarget.value as ExperienceType)
                    }
                  >
                    <For each={experienceTypes}>
                      {type => <option value={type.value}>{type.label}</option>}
                    </For>
                  </select>
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
                    disabled={formData.is_current}
                  />
                </div>
              </div>

              {/* Current Position Toggle */}
              <div class='form-control'>
                <label class='label cursor-pointer justify-start gap-4'>
                  <input
                    type='checkbox'
                    class='checkbox'
                    checked={formData.is_current}
                    onChange={e => setFormData('is_current', e.currentTarget.checked)}
                  />
                  <div>
                    <span class='label-text font-medium'>I currently work here</span>
                    <div class='text-sm text-base-content/70'>
                      This will automatically set the end date to present
                    </div>
                  </div>
                </label>
              </div>

              {/* Description */}
              <div class='form-control'>
                <label class='label'>
                  <span class='label-text'>Job Description</span>
                </label>
                <textarea
                  class='textarea textarea-bordered h-24'
                  placeholder='Describe your role and responsibilities...'
                  value={formData.default_description}
                  onInput={e => setFormData('default_description', e.currentTarget.value)}
                />
              </div>

              {/* Dynamic Lists Section */}
              <div class='form-control'>
                <label class='label'>
                  <span class='label-text'>Achievements, Skills & Technologies</span>
                </label>

                {/* List Input */}
                <div class='flex gap-2 mb-3'>
                  <select
                    class='select select-bordered select-sm'
                    value={currentListType()}
                    onChange={e => setCurrentListType(e.currentTarget.value as any)}
                  >
                    <option value='achievements'>Achievements</option>
                    <option value='skills'>Skills</option>
                    <option value='technologies'>Technologies</option>
                  </select>
                  <input
                    type='text'
                    placeholder={`Add ${currentListType()}...`}
                    class='input input-bordered input-sm flex-1'
                    value={currentListItem()}
                    onInput={e => setCurrentListItem(e.currentTarget.value)}
                    onKeyPress={handleListItemKeyPress}
                  />
                  <button type='button' class='btn btn-sm' onClick={handleAddListItem}>
                    Add
                  </button>
                </div>

                {/* Lists Display */}
                <div class='space-y-3'>
                  <Show when={formData.default_achievements.length > 0}>
                    <div>
                      <div class='text-sm font-medium mb-2'>Key Achievements:</div>
                      <div class='space-y-2'>
                        <For each={formData.default_achievements}>
                          {(achievement, index) => (
                            <div class='flex items-center gap-2'>
                              <input
                                type='text'
                                class='input input-bordered input-sm flex-1'
                                value={achievement}
                                onInput={e => {
                                  const newAchievements = [...formData.default_achievements];
                                  newAchievements[index()] = e.currentTarget.value;
                                  setFormData('default_achievements', newAchievements);
                                }}
                                placeholder='Describe a key achievement...'
                              />
                              <button
                                type='button'
                                class='btn btn-ghost btn-xs text-error'
                                onClick={() =>
                                  handleRemoveListItem('default_achievements', achievement)
                                }
                              >
                                🗑️
                              </button>
                            </div>
                          )}
                        </For>
                      </div>
                    </div>
                  </Show>

                  <Show when={formData.skills_used.length > 0}>
                    <div>
                      <div class='text-sm font-medium mb-1'>Skills Used:</div>
                      <div class='flex flex-wrap gap-2'>
                        <For each={formData.skills_used}>
                          {skill => (
                            <div class='badge badge-info gap-2'>
                              {skill}
                              <button
                                type='button'
                                class='text-info-content'
                                onClick={() => handleRemoveListItem('skills_used', skill)}
                              >
                                ×
                              </button>
                            </div>
                          )}
                        </For>
                      </div>
                    </div>
                  </Show>

                  <Show when={formData.technologies.length > 0}>
                    <div>
                      <div class='text-sm font-medium mb-1'>Technologies:</div>
                      <div class='flex flex-wrap gap-2'>
                        <For each={formData.technologies}>
                          {tech => (
                            <div class='badge badge-success gap-2'>
                              {tech}
                              <button
                                type='button'
                                class='text-success-content'
                                onClick={() => handleRemoveListItem('technologies', tech)}
                              >
                                ×
                              </button>
                            </div>
                          )}
                        </For>
                      </div>
                    </div>
                  </Show>
                </div>
              </div>

              {/* Form Actions */}
              <div class='modal-action'>
                <button type='button' class='btn' onClick={handleCancelEdit}>
                  Cancel
                </button>
                <button
                  type='submit'
                  class='btn btn-primary'
                  disabled={
                    saving() ||
                    !formData.company.trim() ||
                    !formData.position.trim() ||
                    !formData.start_date
                  }
                >
                  <Show
                    when={saving()}
                    fallback={editingExperience() ? 'Update Experience' : 'Add Experience'}
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

      {/* Experience List */}
      <Show
        when={experiences().length > 0}
        fallback={
          <div class='text-center py-16'>
            <div class='text-6xl mb-4'>💼</div>
            <h3 class='text-xl font-semibold mb-2'>No work experience added yet</h3>
            <p class='text-base-content/70 mb-6'>
              Add your professional work experience to build your skill bank
            </p>
            <button class='btn btn-primary' onClick={handleAddExperience}>
              Add Your First Experience
            </button>
          </div>
        }
      >
        <div class='space-y-4'>
          <For each={sortedExperiences()}>
            {experience => {
              const isExpanded = () => expandedExperience() === experience.id;
              const duration = () => calculateDuration(experience.start_date, experience.end_date);
              const typeBadge = () => getExperienceTypeBadge(experience.experience_type);

              return (
                <div class='card bg-base-100 shadow-lg border border-base-300'>
                  <div class='card-body'>
                    <div class='flex items-start justify-between'>
                      <div class='flex-1 min-w-0'>
                        <div class='flex items-center gap-3 mb-2'>
                          <h3 class='card-title text-lg'>{experience.position}</h3>
                          <Show when={experience.is_current}>
                            <div class='badge badge-success'>Current</div>
                          </Show>
                          <div class={`badge ${typeBadge().color}`}>{typeBadge().label}</div>
                        </div>

                        <p class='text-primary font-medium text-base'>{experience.company}</p>

                        <div class='flex flex-wrap items-center gap-2 mt-2 text-sm text-base-content/70'>
                          <div class='flex items-center gap-1'>
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
                                d='M8 7V3a1 1 0 011-1h6a1 1 0 011 1v4h3a1 1 0 110 2h-1v9a2 2 0 01-2 2H8a2 2 0 01-2-2V9H5a1 1 0 110-2h3z'
                              />
                            </svg>
                            {formatDate(experience.start_date)} -{' '}
                            {experience.is_current
                              ? 'Present'
                              : formatDate(experience.end_date || '')}
                          </div>
                          <Show when={duration()}>
                            <span>•</span>
                            <span>{duration()}</span>
                          </Show>
                          <Show when={experience.location}>
                            <span>•</span>
                            <div class='flex items-center gap-1'>
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
                                  d='M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z'
                                />
                                <path
                                  stroke-linecap='round'
                                  stroke-linejoin='round'
                                  stroke-width='2'
                                  d='M15 11a3 3 0 11-6 0 3 3 0 016 0z'
                                />
                              </svg>
                              {experience.location}
                            </div>
                          </Show>
                        </div>

                        <Show when={experience.default_description}>
                          <div class='mt-3'>
                            <p
                              class={`text-base-content/80 leading-relaxed ${
                                !isExpanded() && (experience.default_description?.length || 0) > 200
                                  ? 'line-clamp-3'
                                  : ''
                              }`}
                            >
                              {experience.default_description}
                            </p>
                            <Show when={(experience.default_description?.length || 0) > 200}>
                              <button
                                class='btn btn-ghost btn-xs mt-2'
                                onClick={() => toggleExperienceExpansion(experience.id)}
                              >
                                {isExpanded() ? 'Show less' : 'Show more'}
                              </button>
                            </Show>
                          </div>
                        </Show>

                        {/* Achievements (only when expanded) */}
                        <Show when={isExpanded() && experience.default_achievements.length > 0}>
                          <div class='mt-4'>
                            <h4 class='text-sm font-medium text-base-content/70 mb-2'>
                              Key Achievements:
                            </h4>
                            <ul class='list-disc list-inside space-y-1 text-sm text-base-content/80'>
                              <For each={experience.default_achievements}>
                                {achievement => <li>{achievement}</li>}
                              </For>
                            </ul>
                          </div>
                        </Show>

                        {/* Skills and Technologies */}
                        <Show
                          when={
                            experience.skills_used.length > 0 || experience.technologies.length > 0
                          }
                        >
                          <div class='mt-3 space-y-2'>
                            <Show when={experience.skills_used.length > 0}>
                              <div>
                                <span class='text-sm font-medium text-base-content/70 mr-2'>
                                  Skills:
                                </span>
                                <For
                                  each={experience.skills_used.slice(
                                    0,
                                    isExpanded() ? undefined : 3
                                  )}
                                >
                                  {skill => (
                                    <span class='badge badge-info badge-sm mr-1'>{skill}</span>
                                  )}
                                </For>
                                <Show when={!isExpanded() && experience.skills_used.length > 3}>
                                  <span class='badge badge-ghost badge-sm'>
                                    +{experience.skills_used.length - 3}
                                  </span>
                                </Show>
                              </div>
                            </Show>

                            <Show when={experience.technologies.length > 0}>
                              <div>
                                <span class='text-sm font-medium text-base-content/70 mr-2'>
                                  Technologies:
                                </span>
                                <For
                                  each={experience.technologies.slice(
                                    0,
                                    isExpanded() ? undefined : 3
                                  )}
                                >
                                  {tech => (
                                    <span class='badge badge-success badge-sm mr-1'>{tech}</span>
                                  )}
                                </For>
                                <Show when={!isExpanded() && experience.technologies.length > 3}>
                                  <span class='badge badge-ghost badge-sm'>
                                    +{experience.technologies.length - 3}
                                  </span>
                                </Show>
                              </div>
                            </Show>
                          </div>
                        </Show>
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
                            />
                          </svg>
                        </label>
                        <ul
                          tabindex='0'
                          class='dropdown-content menu p-2 shadow bg-base-100 rounded-box w-52 z-10'
                        >
                          <li>
                            <button onClick={() => handleEditExperience(experience)}>
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
                                  d='M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z'
                                />
                              </svg>
                              Edit
                            </button>
                          </li>
                          <li>
                            <button
                              class='text-error'
                              onClick={() => handleDeleteExperience(experience)}
                            >
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
                                  d='M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16'
                                />
                              </svg>
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

export default ExperienceSection;
