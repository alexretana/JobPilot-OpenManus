import { Component, createSignal, Show, For } from 'solid-js';
import { createStore } from 'solid-js/store';
import { skillBankApiService } from '../../../../../services/skillBankApi';
import type {
  SkillBankResponse,
  SummaryVariation,
  SummaryVariationRequest,
} from '../../../../../types/skillBank';
import { ContentFocusType } from '../../../../../types/skillBank';

interface SummariesSectionProps {
  skillBank: SkillBankResponse;
  onUpdate: () => void;
  loading: boolean;
}

interface SummaryFormData {
  title: string;
  content: string;
  tone: string;
  length: string;
  focus: ContentFocusType;
  target_industries: string[];
  target_roles: string[];
  keywords_emphasized: string[];
}

const skillBankApi = skillBankApiService;

const contentFocusOptions = [
  { value: 'technical' as const, label: 'Technical Focus', color: 'badge-info' },
  { value: 'leadership' as const, label: 'Leadership Focus', color: 'badge-warning' },
  { value: 'results' as const, label: 'Results-Oriented', color: 'badge-success' },
  { value: 'general' as const, label: 'General Overview', color: 'badge-neutral' },
  { value: 'creative' as const, label: 'Creative Focus', color: 'badge-secondary' },
  { value: 'concise' as const, label: 'Concise & Direct', color: 'badge-accent' },
  { value: 'detailed' as const, label: 'Detailed Description', color: 'badge-primary' },
];

const toneOptions = [
  'Professional',
  'Confident',
  'Friendly',
  'Dynamic',
  'Strategic',
  'Technical',
  'Creative',
  'Results-driven',
  'Collaborative',
  'Innovative',
];

const lengthOptions = [
  'Brief (2-3 sentences)',
  'Standard (4-5 sentences)',
  'Extended (6-8 sentences)',
  'Detailed (paragraph)',
];

const initialFormData: SummaryFormData = {
  title: '',
  content: '',
  tone: 'Professional',
  length: 'Standard (4-5 sentences)',
  focus: ContentFocusType.GENERAL,
  target_industries: [],
  target_roles: [],
  keywords_emphasized: [],
};

/**
 * Professional summaries management section
 */
export const SummariesSection: Component<SummariesSectionProps> = props => {
  const [showAddForm, setShowAddForm] = createSignal(false);
  const [editingSummary, setEditingSummary] = createSignal<SummaryVariation | null>(null);
  const [formData, setFormData] = createStore<SummaryFormData>(initialFormData);
  const [saving, setSaving] = createSignal(false);
  const [expandedSummary, setExpandedSummary] = createSignal<string | null>(null);
  const [currentTag, setCurrentTag] = createSignal('');
  const [currentTagType, setCurrentTagType] = createSignal<'industries' | 'roles' | 'keywords'>(
    'industries'
  );

  const summaries = () => props.skillBank?.summary_variations || [];

  const handleAddSummary = () => {
    setFormData(initialFormData);
    setEditingSummary(null);
    setShowAddForm(true);
  };

  const handleEditSummary = (summary: SummaryVariation) => {
    setFormData({
      title: summary.title,
      content: summary.content,
      tone: summary.tone,
      length: summary.length,
      focus: summary.focus,
      target_industries: [...summary.target_industries],
      target_roles: [...summary.target_roles],
      keywords_emphasized: [...summary.keywords_emphasized],
    });
    setEditingSummary(summary);
    setShowAddForm(true);
  };

  const handleCancelEdit = () => {
    setShowAddForm(false);
    setEditingSummary(null);
    setFormData(initialFormData);
  };

  const handleFormSubmit = async (e: Event) => {
    e.preventDefault();
    if (!formData.title.trim() || !formData.content.trim()) return;

    setSaving(true);
    try {
      const summaryRequest: SummaryVariationRequest = {
        title: formData.title.trim(),
        content: formData.content.trim(),
        tone: formData.tone,
        length: formData.length,
        focus: formData.focus,
        target_industries: formData.target_industries.filter(i => i.trim()),
        target_roles: formData.target_roles.filter(r => r.trim()),
        keywords_emphasized: formData.keywords_emphasized.filter(k => k.trim()),
      };

      if (editingSummary()) {
        await skillBankApi.updateSummaryVariation(
          props.skillBank.user_id,
          editingSummary()!.id,
          summaryRequest
        );
      } else {
        await skillBankApi.addSummaryVariation(props.skillBank.user_id, summaryRequest);
      }

      props.onUpdate();
      handleCancelEdit();
    } catch (error) {
      console.error('Error saving summary:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteSummary = async (summary: SummaryVariation) => {
    if (!confirm(`Are you sure you want to delete "${summary.title}"?`)) return;

    setSaving(true);
    try {
      await skillBankApi.deleteSummaryVariation(props.skillBank.user_id, summary.id);
      props.onUpdate();
    } catch (error) {
      console.error('Error deleting summary:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleAddTag = () => {
    const tag = currentTag().trim();
    if (!tag) return;

    const field =
      currentTagType() === 'industries'
        ? 'target_industries'
        : currentTagType() === 'roles'
        ? 'target_roles'
        : 'keywords_emphasized';

    if (!formData[field].includes(tag)) {
      setFormData(field, [...formData[field], tag]);
      setCurrentTag('');
    }
  };

  const handleRemoveTag = (
    field: 'target_industries' | 'target_roles' | 'keywords_emphasized',
    tag: string
  ) => {
    setFormData(
      field,
      formData[field].filter(t => t !== tag)
    );
  };

  const handleTagKeyPress = (e: KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddTag();
    }
  };

  const toggleSummaryExpansion = (summaryId: string) => {
    setExpandedSummary(expandedSummary() === summaryId ? null : summaryId);
  };

  const getWordCount = (text: string) => {
    return text
      .trim()
      .split(/\s+/)
      .filter(word => word.length > 0).length;
  };

  const getFocusBadgeClass = (focus: ContentFocusType) => {
    return contentFocusOptions.find(f => f.value === focus)?.color || 'badge-neutral';
  };

  const getFocusLabel = (focus: ContentFocusType) => {
    return contentFocusOptions.find(f => f.value === focus)?.label || focus;
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
                d='M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z'
              />
            </svg>
            Professional Summaries ({summaries().length})
          </h2>
          <p class='text-base-content/70'>
            Create tailored professional summaries for different job targets and industries
          </p>
        </div>
        <button class='btn btn-primary gap-2' onClick={handleAddSummary} disabled={saving()}>
          <svg class='w-4 h-4' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
            <path
              stroke-linecap='round'
              stroke-linejoin='round'
              stroke-width='2'
              d='M12 4v16m8-8H4'
            />
          </svg>
          Add Summary
        </button>
      </div>

      {/* Add/Edit Form Modal */}
      <Show when={showAddForm()}>
        <div class='modal modal-open'>
          <div class='modal-box w-11/12 max-w-4xl'>
            <h3 class='font-bold text-lg mb-4'>
              {editingSummary() ? 'Edit Professional Summary' : 'Add Professional Summary'}
            </h3>

            <form onSubmit={handleFormSubmit} class='space-y-4'>
              {/* Title and Basic Info */}
              <div class='grid grid-cols-1 md:grid-cols-2 gap-4'>
                <div class='form-control'>
                  <label class='label'>
                    <span class='label-text'>Summary Title *</span>
                  </label>
                  <input
                    type='text'
                    placeholder='e.g., Senior Developer - Tech Focus'
                    class='input input-bordered'
                    value={formData.title}
                    onInput={e => setFormData('title', e.currentTarget.value)}
                    required
                  />
                </div>

                <div class='form-control'>
                  <label class='label'>
                    <span class='label-text'>Content Focus</span>
                  </label>
                  <select
                    class='select select-bordered'
                    value={formData.focus}
                    onChange={e => setFormData('focus', e.currentTarget.value as ContentFocusType)}
                  >
                    <For each={contentFocusOptions}>
                      {option => <option value={option.value}>{option.label}</option>}
                    </For>
                  </select>
                </div>

                <div class='form-control'>
                  <label class='label'>
                    <span class='label-text'>Tone</span>
                  </label>
                  <select
                    class='select select-bordered'
                    value={formData.tone}
                    onChange={e => setFormData('tone', e.currentTarget.value)}
                  >
                    <For each={toneOptions}>{tone => <option value={tone}>{tone}</option>}</For>
                  </select>
                </div>

                <div class='form-control'>
                  <label class='label'>
                    <span class='label-text'>Length</span>
                  </label>
                  <select
                    class='select select-bordered'
                    value={formData.length}
                    onChange={e => setFormData('length', e.currentTarget.value)}
                  >
                    <For each={lengthOptions}>
                      {length => <option value={length}>{length}</option>}
                    </For>
                  </select>
                </div>
              </div>

              {/* Content */}
              <div class='form-control'>
                <label class='label'>
                  <span class='label-text'>Summary Content *</span>
                  <span class='label-text-alt'>{getWordCount(formData.content)} words</span>
                </label>
                <textarea
                  class='textarea textarea-bordered h-32'
                  placeholder='Write your professional summary here. Focus on your key achievements, skills, and value proposition...'
                  value={formData.content}
                  onInput={e => setFormData('content', e.currentTarget.value)}
                  required
                />
              </div>

              {/* Tags Section */}
              <div class='form-control'>
                <label class='label'>
                  <span class='label-text'>Target Industries, Roles & Keywords</span>
                </label>

                {/* Tag Input */}
                <div class='flex gap-2 mb-3'>
                  <select
                    class='select select-bordered select-sm'
                    value={currentTagType()}
                    onChange={e => setCurrentTagType(e.currentTarget.value as any)}
                  >
                    <option value='industries'>Industries</option>
                    <option value='roles'>Roles</option>
                    <option value='keywords'>Keywords</option>
                  </select>
                  <input
                    type='text'
                    placeholder={`Add ${currentTagType().replace('_', ' ')}...`}
                    class='input input-bordered input-sm flex-1'
                    value={currentTag()}
                    onInput={e => setCurrentTag(e.currentTarget.value)}
                    onKeyPress={handleTagKeyPress}
                  />
                  <button type='button' class='btn btn-sm' onClick={handleAddTag}>
                    Add
                  </button>
                </div>

                {/* Tags Display */}
                <div class='space-y-3'>
                  <Show when={formData.target_industries.length > 0}>
                    <div>
                      <div class='text-sm font-medium mb-1'>Target Industries:</div>
                      <div class='flex flex-wrap gap-2'>
                        <For each={formData.target_industries}>
                          {industry => (
                            <div class='badge badge-info gap-2'>
                              {industry}
                              <button
                                type='button'
                                class='text-info-content'
                                onClick={() => handleRemoveTag('target_industries', industry)}
                              >
                                ×
                              </button>
                            </div>
                          )}
                        </For>
                      </div>
                    </div>
                  </Show>

                  <Show when={formData.target_roles.length > 0}>
                    <div>
                      <div class='text-sm font-medium mb-1'>Target Roles:</div>
                      <div class='flex flex-wrap gap-2'>
                        <For each={formData.target_roles}>
                          {role => (
                            <div class='badge badge-warning gap-2'>
                              {role}
                              <button
                                type='button'
                                class='text-warning-content'
                                onClick={() => handleRemoveTag('target_roles', role)}
                              >
                                ×
                              </button>
                            </div>
                          )}
                        </For>
                      </div>
                    </div>
                  </Show>

                  <Show when={formData.keywords_emphasized.length > 0}>
                    <div>
                      <div class='text-sm font-medium mb-1'>Emphasized Keywords:</div>
                      <div class='flex flex-wrap gap-2'>
                        <For each={formData.keywords_emphasized}>
                          {keyword => (
                            <div class='badge badge-accent gap-2'>
                              {keyword}
                              <button
                                type='button'
                                class='text-accent-content'
                                onClick={() => handleRemoveTag('keywords_emphasized', keyword)}
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
                  disabled={saving() || !formData.title.trim() || !formData.content.trim()}
                >
                  <Show
                    when={saving()}
                    fallback={editingSummary() ? 'Update Summary' : 'Add Summary'}
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

      {/* Summaries Display */}
      <Show
        when={summaries().length > 0}
        fallback={
          <div class='text-center py-16'>
            <div class='text-6xl mb-4'>📝</div>
            <h3 class='text-xl font-semibold mb-2'>No professional summaries yet</h3>
            <p class='text-base-content/70 mb-6'>
              Create tailored professional summaries for different job applications and industries
            </p>
            <button class='btn btn-primary' onClick={handleAddSummary}>
              Create Your First Summary
            </button>
          </div>
        }
      >
        <div class='grid gap-6'>
          <For each={summaries()}>
            {summary => {
              const isExpanded = () => expandedSummary() === summary.id;
              const wordCount = () => getWordCount(summary.content);

              return (
                <div class='card bg-base-100 shadow-lg border border-base-300'>
                  <div class='card-body'>
                    <div class='flex items-start justify-between'>
                      <div class='flex-1 min-w-0'>
                        <div class='flex items-center gap-3 mb-2'>
                          <h3 class='card-title text-lg'>{summary.title}</h3>
                          <div class={`badge ${getFocusBadgeClass(summary.focus)}`}>
                            {getFocusLabel(summary.focus)}
                          </div>
                        </div>

                        <div class='flex flex-wrap gap-2 mb-3 text-sm text-base-content/70'>
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
                                d='M7 4V2a1 1 0 011-1h8a1 1 0 011 1v2h4a1 1 0 110 2h-1v12a2 2 0 01-2 2H6a2 2 0 01-2-2V6H3a1 1 0 110-2h4z'
                              />
                            </svg>
                            {summary.tone}
                          </div>
                          <span>•</span>
                          <div>{summary.length}</div>
                          <span>•</span>
                          <div>{wordCount()} words</div>
                          <Show when={summary.usage_count > 0}>
                            <span>•</span>
                            <div>
                              Used {summary.usage_count} time{summary.usage_count !== 1 ? 's' : ''}
                            </div>
                          </Show>
                        </div>

                        <div
                          class={`prose prose-sm max-w-none ${
                            !isExpanded() && summary.content.length > 300 ? 'line-clamp-3' : ''
                          }`}
                        >
                          <p class='text-base-content/90'>{summary.content}</p>
                        </div>

                        <Show when={summary.content.length > 300}>
                          <button
                            class='btn btn-ghost btn-xs mt-2'
                            onClick={() => toggleSummaryExpansion(summary.id)}
                          >
                            {isExpanded() ? 'Show less' : 'Show more'}
                          </button>
                        </Show>

                        {/* Tags */}
                        <Show
                          when={
                            isExpanded() &&
                            (summary.target_industries.length > 0 ||
                              summary.target_roles.length > 0 ||
                              summary.keywords_emphasized.length > 0)
                          }
                        >
                          <div class='mt-4 space-y-2'>
                            <Show when={summary.target_industries.length > 0}>
                              <div>
                                <span class='text-sm font-medium text-base-content/70 mr-2'>
                                  Industries:
                                </span>
                                <For each={summary.target_industries.slice(0, 3)}>
                                  {industry => (
                                    <span class='badge badge-info badge-sm mr-1'>{industry}</span>
                                  )}
                                </For>
                                <Show when={summary.target_industries.length > 3}>
                                  <span class='badge badge-ghost badge-sm'>
                                    +{summary.target_industries.length - 3}
                                  </span>
                                </Show>
                              </div>
                            </Show>

                            <Show when={summary.target_roles.length > 0}>
                              <div>
                                <span class='text-sm font-medium text-base-content/70 mr-2'>
                                  Roles:
                                </span>
                                <For each={summary.target_roles.slice(0, 3)}>
                                  {role => (
                                    <span class='badge badge-warning badge-sm mr-1'>{role}</span>
                                  )}
                                </For>
                                <Show when={summary.target_roles.length > 3}>
                                  <span class='badge badge-ghost badge-sm'>
                                    +{summary.target_roles.length - 3}
                                  </span>
                                </Show>
                              </div>
                            </Show>

                            <Show when={summary.keywords_emphasized.length > 0}>
                              <div>
                                <span class='text-sm font-medium text-base-content/70 mr-2'>
                                  Keywords:
                                </span>
                                <For each={summary.keywords_emphasized.slice(0, 5)}>
                                  {keyword => (
                                    <span class='badge badge-accent badge-sm mr-1'>{keyword}</span>
                                  )}
                                </For>
                                <Show when={summary.keywords_emphasized.length > 5}>
                                  <span class='badge badge-ghost badge-sm'>
                                    +{summary.keywords_emphasized.length - 5}
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
                            <button onClick={() => handleEditSummary(summary)}>
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
                              class='text-info'
                              onClick={() => navigator.clipboard?.writeText(summary.content)}
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
                                  d='M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z'
                                />
                              </svg>
                              Copy
                            </button>
                          </li>
                          <li>
                            <button class='text-error' onClick={() => handleDeleteSummary(summary)}>
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

export default SummariesSection;
