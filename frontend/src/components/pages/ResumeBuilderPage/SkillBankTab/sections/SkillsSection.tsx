import { Component, createSignal, createMemo, Show, For } from 'solid-js';
import { createStore } from 'solid-js/store';
import { skillBankApiService } from '../../../../../services/skillBankApi';
import type {
  SkillBankResponse,
  EnhancedSkill,
  EnhancedSkillRequest,
} from '../../../../../types/skillBank';
import { SkillLevel, SkillCategory, ContentSource } from '../../../../../types/skillBank';

// Filter types for skills

interface SkillsSectionProps {
  skillBank: SkillBankResponse;
  onUpdate: () => void;
  loading: boolean;
}

interface SkillFormData {
  name: string;
  level: SkillLevel;
  category: SkillCategory;
  subcategory: string;
  years_experience: number | null;
  description: string;
  keywords: string[];
  is_featured: boolean;
}

const skillBankApi = skillBankApiService;

const skillLevels = [
  { value: 'beginner' as const, label: 'Beginner', color: 'badge-secondary' },
  { value: 'intermediate' as const, label: 'Intermediate', color: 'badge-info' },
  { value: 'advanced' as const, label: 'Advanced', color: 'badge-warning' },
  { value: 'expert' as const, label: 'Expert', color: 'badge-success' },
];

const skillCategories = [
  { value: 'technical' as const, label: 'Technical' },
  { value: 'soft' as const, label: 'Soft Skills' },
  { value: 'transferable' as const, label: 'Transferable' },
  { value: 'industry' as const, label: 'Industry' },
  { value: 'tool' as const, label: 'Tools' },
  { value: 'language' as const, label: 'Languages' },
  { value: 'framework' as const, label: 'Frameworks' },
  { value: 'platform' as const, label: 'Platforms' },
  { value: 'methodology' as const, label: 'Methodologies' },
  { value: 'domain' as const, label: 'Domain Knowledge' },
  { value: 'other' as const, label: 'Other' },
];

const initialFormData: SkillFormData = {
  name: '',
  level: SkillLevel.INTERMEDIATE,
  category: SkillCategory.TECHNICAL,
  subcategory: '',
  years_experience: null,
  description: '',
  keywords: [],
  is_featured: false,
};

/**
 * Skills management section with full CRUD operations
 */
export const SkillsSection: Component<SkillsSectionProps> = props => {
  const [showAddForm, setShowAddForm] = createSignal(false);
  const [editingSkill, setEditingSkill] = createSignal<EnhancedSkill | null>(null);
  const [formData, setFormData] = createStore<SkillFormData>(initialFormData);
  const [saving, setSaving] = createSignal(false);
  const [searchTerm, setSearchTerm] = createSignal('');
  const [selectedCategory, setSelectedCategory] = createSignal<string>('all');
  const [currentKeyword, setCurrentKeyword] = createSignal('');

  // Get all skills flattened from categories
  const allSkills = createMemo(() => {
    const skillsMap = props.skillBank?.skills || {};
    return Object.values(skillsMap).flat();
  });

  // Filtered and searched skills
  const filteredSkills = createMemo(() => {
    let skills = allSkills();

    // Filter by search term
    if (searchTerm()) {
      const term = searchTerm().toLowerCase();
      skills = skills.filter(
        skill =>
          skill.name.toLowerCase().includes(term) ||
          skill.description?.toLowerCase().includes(term) ||
          skill.keywords.some(keyword => keyword.toLowerCase().includes(term))
      );
    }

    // Filter by category
    if (selectedCategory() !== 'all') {
      skills = skills.filter(skill => skill.category === selectedCategory());
    }

    return skills.sort((a, b) => {
      // Featured skills first
      if (a.is_featured && !b.is_featured) return -1;
      if (!a.is_featured && b.is_featured) return 1;
      // Then by display order
      return a.display_order - b.display_order;
    });
  });

  // Group skills by category for display
  const groupedSkills = createMemo(() => {
    const skills = filteredSkills();
    const groups: Record<string, EnhancedSkill[]> = {};

    skills.forEach(skill => {
      if (!groups[skill.category]) {
        groups[skill.category] = [];
      }
      groups[skill.category].push(skill);
    });

    return groups;
  });

  const handleAddSkill = () => {
    setFormData(initialFormData);
    setEditingSkill(null);
    setShowAddForm(true);
  };

  const handleEditSkill = (skill: EnhancedSkill) => {
    setFormData({
      name: skill.name,
      level: skill.level,
      category: skill.category,
      subcategory: skill.subcategory || '',
      years_experience: skill.years_experience,
      description: skill.description || '',
      keywords: [...skill.keywords],
      is_featured: skill.is_featured,
    });
    setEditingSkill(skill);
    setShowAddForm(true);
  };

  const handleCancelEdit = () => {
    setShowAddForm(false);
    setEditingSkill(null);
    setFormData(initialFormData);
  };

  const handleFormSubmit = async (e: Event) => {
    e.preventDefault();
    if (!formData.name.trim()) return;

    setSaving(true);
    try {
      const skillRequest: EnhancedSkillRequest = {
        name: formData.name.trim(),
        level: formData.level,
        category: formData.category,
        subcategory: formData.subcategory.trim() || null,
        years_experience: formData.years_experience,
        description: formData.description.trim() || null,
        keywords: formData.keywords.filter(k => k.trim()),
        is_featured: formData.is_featured,
        source: 'manual' as ContentSource,
      };

      if (editingSkill()) {
        // Update existing skill
        await skillBankApi.updateSkill(props.skillBank.user_id, editingSkill()!.id, skillRequest);
      } else {
        // Add new skill
        await skillBankApi.addSkill(props.skillBank.user_id, skillRequest);
      }

      props.onUpdate();
      handleCancelEdit();
    } catch (error) {
      console.error('Error saving skill:', error);
      // You could add toast notifications here
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteSkill = async (skill: EnhancedSkill) => {
    if (!confirm(`Are you sure you want to delete "${skill.name}"?`)) return;

    setSaving(true);
    try {
      await skillBankApi.deleteSkill(props.skillBank.user_id, skill.id);
      props.onUpdate();
    } catch (error) {
      console.error('Error deleting skill:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleAddKeyword = () => {
    const keyword = currentKeyword().trim();
    if (keyword && !formData.keywords.includes(keyword)) {
      setFormData('keywords', [...formData.keywords, keyword]);
      setCurrentKeyword('');
    }
  };

  const handleRemoveKeyword = (keyword: string) => {
    setFormData(
      'keywords',
      formData.keywords.filter(k => k !== keyword)
    );
  };

  const handleKeywordKeyPress = (e: KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddKeyword();
    }
  };

  const getLevelBadgeClass = (level: SkillLevel) => {
    return skillLevels.find(l => l.value === level)?.color || 'badge-neutral';
  };

  const getCategoryLabel = (category: SkillCategory) => {
    return skillCategories.find(c => c.value === category)?.label || category;
  };

  return (
    <div class='space-y-2'>
      {/* Header with Actions */}
      <div class='flex flex-col lg:flex-row justify-between items-start lg:items-center gap-2 m-2 p-2'>
        <div>
          <h2 class='text-2xl font-bold text-base-content flex items-center gap-2 p-2'>
            <svg class='w-6 h-6 text-primary' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
              <path
                stroke-linecap='round'
                stroke-linejoin='round'
                stroke-width='2'
                d='M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z'
              />
            </svg>
            Skills ({allSkills().length})
          </h2>
          <p class='text-base-content/70 p-2'>
            Manage your technical and soft skills with proficiency levels and descriptions
          </p>
        </div>
        <button class='btn btn-primary gap-2 m-2 p-2' onClick={handleAddSkill} disabled={saving()}>
          <svg class='w-4 h-4' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
            <path
              stroke-linecap='round'
              stroke-linejoin='round'
              stroke-width='2'
              d='M12 4v16m8-8H4'
            />
          </svg>
          Add Skill
        </button>
      </div>

      {/* Search and Filter */}
      <div class='flex flex-col sm:flex-row gap-2 m-2 p-2'>
        <div class='form-control flex-1'>
          <input
            type='text'
            placeholder='Search skills...'
            class='input input-bordered w-full m-2 p-2'
            value={searchTerm()}
            onInput={e => setSearchTerm(e.currentTarget.value)}
          />
        </div>
        <select
          class='select select-bordered w-full sm:w-auto m-2 p-2'
          value={selectedCategory()}
          onChange={e => setSelectedCategory(e.currentTarget.value)}
        >
          <option value='all'>All Categories</option>
          <For each={skillCategories}>
            {category => <option value={category.value}>{category.label}</option>}
          </For>
        </select>
        <button class='btn btn-square m-2 p-2'>
          <svg class='w-6 h-6' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
            <path
              stroke-linecap='round'
              stroke-linejoin='round'
              stroke-width='2'
              d='m21 21-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z'
            />
          </svg>
        </button>
      </div>

      {/* Add/Edit Form Modal */}
      <Show when={showAddForm()}>
        <div class='modal modal-open'>
          <div class='modal-box w-11/12 max-w-2xl'>
            <h3 class='font-bold text-lg mb-4'>
              {editingSkill() ? 'Edit Skill' : 'Add New Skill'}
            </h3>

            <form onSubmit={handleFormSubmit} class='space-y-4'>
              {/* Basic Information */}
              <div class='grid grid-cols-1 md:grid-cols-2 gap-4'>
                <div class='form-control'>
                  <label class='label'>
                    <span class='label-text'>Skill Name *</span>
                  </label>
                  <input
                    type='text'
                    placeholder='e.g., JavaScript, Project Management'
                    class='input input-bordered'
                    value={formData.name}
                    onInput={e => setFormData('name', e.currentTarget.value)}
                    required
                  />
                </div>

                <div class='form-control'>
                  <label class='label'>
                    <span class='label-text'>Category</span>
                  </label>
                  <select
                    class='select select-bordered'
                    value={formData.category}
                    onChange={e => setFormData('category', e.currentTarget.value as SkillCategory)}
                  >
                    <For each={skillCategories}>
                      {category => <option value={category.value}>{category.label}</option>}
                    </For>
                  </select>
                </div>

                <div class='form-control'>
                  <label class='label'>
                    <span class='label-text'>Proficiency Level</span>
                  </label>
                  <select
                    class='select select-bordered'
                    value={formData.level}
                    onChange={e => setFormData('level', e.currentTarget.value as SkillLevel)}
                  >
                    <For each={skillLevels}>
                      {level => <option value={level.value}>{level.label}</option>}
                    </For>
                  </select>
                </div>

                <div class='form-control'>
                  <label class='label'>
                    <span class='label-text'>Years of Experience</span>
                  </label>
                  <input
                    type='number'
                    min='0'
                    max='50'
                    class='input input-bordered'
                    value={formData.years_experience || ''}
                    onInput={e =>
                      setFormData(
                        'years_experience',
                        e.currentTarget.value ? parseInt(e.currentTarget.value) : null
                      )
                    }
                  />
                </div>
              </div>

              <div class='form-control'>
                <label class='label'>
                  <span class='label-text'>Subcategory</span>
                </label>
                <input
                  type='text'
                  placeholder='e.g., Frontend, Backend, Machine Learning'
                  class='input input-bordered'
                  value={formData.subcategory}
                  onInput={e => setFormData('subcategory', e.currentTarget.value)}
                />
              </div>

              <div class='form-control'>
                <label class='label'>
                  <span class='label-text'>Description</span>
                </label>
                <textarea
                  class='textarea textarea-bordered h-24'
                  placeholder='Describe your experience with this skill...'
                  value={formData.description}
                  onInput={e => setFormData('description', e.currentTarget.value)}
                />
              </div>

              {/* Keywords */}
              <div class='form-control'>
                <label class='label'>
                  <span class='label-text'>Keywords</span>
                </label>
                <div class='space-y-2'>
                  <div class='flex flex-wrap gap-2'>
                    <For each={formData.keywords}>
                      {keyword => (
                        <div class='badge badge-outline gap-2'>
                          {keyword}
                          <button
                            type='button'
                            class='text-error'
                            onClick={() => handleRemoveKeyword(keyword)}
                          >
                            ×
                          </button>
                        </div>
                      )}
                    </For>
                  </div>
                  <div class='input-group'>
                    <input
                      type='text'
                      placeholder='Add keyword...'
                      class='input input-bordered input-sm flex-1'
                      value={currentKeyword()}
                      onInput={e => setCurrentKeyword(e.currentTarget.value)}
                      onKeyPress={handleKeywordKeyPress}
                    />
                    <button type='button' class='btn btn-sm' onClick={handleAddKeyword}>
                      Add
                    </button>
                  </div>
                </div>
              </div>

              {/* Featured Toggle */}
              <div class='form-control'>
                <label class='label cursor-pointer justify-start gap-4'>
                  <input
                    type='checkbox'
                    class='checkbox'
                    checked={formData.is_featured}
                    onChange={e => setFormData('is_featured', e.currentTarget.checked)}
                  />
                  <div>
                    <span class='label-text font-medium'>Featured Skill</span>
                    <div class='text-sm text-base-content/70'>
                      Featured skills appear prominently in your profiles
                    </div>
                  </div>
                </label>
              </div>

              {/* Form Actions */}
              <div class='modal-action'>
                <button type='button' class='btn' onClick={handleCancelEdit}>
                  Cancel
                </button>
                <button
                  type='submit'
                  class='btn btn-primary'
                  disabled={saving() || !formData.name.trim()}
                >
                  <Show when={saving()} fallback={editingSkill() ? 'Update Skill' : 'Add Skill'}>
                    <span class='loading loading-spinner loading-sm'></span>
                    Saving...
                  </Show>
                </button>
              </div>
            </form>
          </div>
        </div>
      </Show>

      {/* Skills Display */}
      <Show
        when={allSkills().length > 0}
        fallback={
          <div class='text-center py-16'>
            <div class='text-6xl mb-4'>🎯</div>
            <h3 class='text-xl font-semibold mb-2'>No skills added yet</h3>
            <p class='text-base-content/70 mb-6'>
              Start building your skill bank by adding your technical and soft skills
            </p>
            <button class='btn btn-primary' onClick={handleAddSkill}>
              Add Your First Skill
            </button>
          </div>
        }
      >
        <Show when={Object.keys(groupedSkills()).length === 0 && allSkills().length > 0}>
          <div class='text-center py-8'>
            <div class='text-4xl mb-2'>🔍</div>
            <p class='text-base-content/70'>No skills match your current search and filters</p>
          </div>
        </Show>

        <For each={Object.entries(groupedSkills())}>
          {([category, skills]) => (
            <div class='card bg-base-100 shadow-lg'>
              <div class='card-body'>
                <h3 class='card-title text-lg mb-4 flex items-center gap-2'>
                  <div class='w-3 h-3 rounded-full bg-primary'></div>
                  {getCategoryLabel(category as SkillCategory)} ({skills.length})
                </h3>

                <div class='grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4'>
                  <For each={skills}>
                    {skill => (
                      <div class='card bg-base-200 shadow-sm border border-base-300'>
                        <div class='card-body p-4'>
                          <div class='flex items-start justify-between'>
                            <div class='flex-1 min-w-0'>
                              <h4 class='font-semibold text-base truncate flex items-center gap-2'>
                                {skill.name}
                                <Show when={skill.is_featured}>
                                  <div class='badge badge-warning badge-xs'>★</div>
                                </Show>
                              </h4>

                              <div class='flex items-center gap-2 mt-1'>
                                <div class={`badge badge-xs ${getLevelBadgeClass(skill.level)}`}>
                                  {skillLevels.find(l => l.value === skill.level)?.label}
                                </div>
                                <Show when={skill.years_experience}>
                                  <span class='text-xs text-base-content/60'>
                                    {skill.years_experience}y
                                  </span>
                                </Show>
                              </div>

                              <Show when={skill.subcategory}>
                                <div class='text-sm text-base-content/70 mt-1'>
                                  {skill.subcategory}
                                </div>
                              </Show>

                              <Show when={skill.description}>
                                <p class='text-sm text-base-content/80 mt-2 line-clamp-2'>
                                  {skill.description}
                                </p>
                              </Show>

                              <Show when={skill.keywords.length > 0}>
                                <div class='flex flex-wrap gap-1 mt-2'>
                                  <For each={skill.keywords.slice(0, 3)}>
                                    {keyword => (
                                      <div class='badge badge-outline badge-xs'>{keyword}</div>
                                    )}
                                  </For>
                                  <Show when={skill.keywords.length > 3}>
                                    <div class='badge badge-ghost badge-xs'>
                                      +{skill.keywords.length - 3}
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
                                  <button onClick={() => handleEditSkill(skill)}>
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
                                    onClick={() => handleDeleteSkill(skill)}
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
                    )}
                  </For>
                </div>
              </div>
            </div>
          )}
        </For>
      </Show>
    </div>
  );
};

export default SkillsSection;
