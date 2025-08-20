import { Component, For, Show, createSignal } from 'solid-js';

// =============================================================================
// SKILL BANK TOGGLE COMPONENT
// =============================================================================

interface SkillBankToggleProps {
  label: string;
  description?: string;
  isEnabled: boolean;
  onToggle: (enabled: boolean) => void;
  disabled?: boolean;
  icon?: string;
}

export const SkillBankToggle: Component<SkillBankToggleProps> = props => {
  return (
    <div class='bg-primary/5 border border-primary/20 rounded-lg p-4 mb-4'>
      <div class='flex items-center justify-between'>
        <div class='flex items-center space-x-3'>
          <div class='w-10 h-10 bg-primary/20 rounded-lg flex items-center justify-center'>
            <span class='text-lg'>{props.icon || '🏦'}</span>
          </div>
          <div>
            <h4 class='font-medium text-primary-content'>{props.label}</h4>
            {props.description && <p class='text-sm text-base-content/70'>{props.description}</p>}
          </div>
        </div>
        <div class='form-control'>
          <label class='label cursor-pointer space-x-3'>
            <span class='label-text font-medium'>Use from Skill Bank</span>
            <input
              type='checkbox'
              class='toggle toggle-primary'
              checked={props.isEnabled}
              disabled={props.disabled}
              onChange={e => props.onToggle(e.target.checked)}
            />
          </label>
        </div>
      </div>
    </div>
  );
};

// =============================================================================
// SUMMARY SELECTOR
// =============================================================================

interface SummaryOption {
  id: string;
  title: string;
  content: string;
}

interface SummarySelectorProps {
  summaryOptions: SummaryOption[];
  selectedSummaryId: string | null;
  onSelect: (summaryId: string) => void;
  onUseSelected: (summary: string) => void;
}

export const SummarySelector: Component<SummarySelectorProps> = props => {
  const [previewExpanded, setPreviewExpanded] = createSignal<string | null>(null);

  return (
    <div class='space-y-4'>
      <h5 class='font-medium'>Available Summary Options</h5>

      <Show when={props.summaryOptions.length === 0}>
        <div class='text-center py-8 bg-base-200 rounded-lg'>
          <div class='text-4xl mb-2'>📝</div>
          <p class='text-base-content/70'>No summaries found in your Skill Bank</p>
          <p class='text-sm text-base-content/50 mt-1'>
            Go to the Skill Bank tab to add professional summaries
          </p>
        </div>
      </Show>

      <div class='space-y-3'>
        <For each={props.summaryOptions}>
          {option => (
            <div class='card bg-base-100 border border-base-300'>
              <div class='card-body p-4'>
                <div class='flex items-center justify-between'>
                  <div class='flex items-center space-x-3'>
                    <input
                      type='radio'
                      name='summary-option'
                      class='radio radio-primary'
                      checked={props.selectedSummaryId === option.id}
                      onChange={() => props.onSelect(option.id)}
                    />
                    <div>
                      <h6 class='font-medium'>{option.title}</h6>
                      <p class='text-sm text-base-content/70 truncate max-w-md'>
                        {option.content.slice(0, 100)}
                        {option.content.length > 100 && '...'}
                      </p>
                    </div>
                  </div>
                  <div class='flex space-x-2'>
                    <button
                      type='button'
                      class='btn btn-ghost btn-sm'
                      onClick={() =>
                        setPreviewExpanded(previewExpanded() === option.id ? null : option.id)
                      }
                    >
                      {previewExpanded() === option.id ? 'Hide' : 'Preview'}
                    </button>
                    <Show when={props.selectedSummaryId === option.id}>
                      <button
                        type='button'
                        class='btn btn-primary btn-sm'
                        onClick={() => props.onUseSelected(option.content)}
                      >
                        Use This
                      </button>
                    </Show>
                  </div>
                </div>

                <Show when={previewExpanded() === option.id}>
                  <div class='mt-3 p-3 bg-base-200 rounded-lg'>
                    <p class='text-sm whitespace-pre-wrap'>{option.content}</p>
                  </div>
                </Show>
              </div>
            </div>
          )}
        </For>
      </div>
    </div>
  );
};

// =============================================================================
// EXPERIENCE SELECTOR
// =============================================================================

interface ExperienceOption {
  id: string;
  company: string;
  position: string;
  location?: string | null;
  start_date: string;
  end_date?: string | null;
  is_current: boolean;
  description: string;
  achievements: string[];
  hasVariations?: boolean;
  variations?: any[];
}

interface ExperienceSelectorProps {
  experienceOptions: ExperienceOption[];
  selectedExperienceIds: string[];
  onToggleSelection: (experienceId: string) => void;
  onUseSelected: (experiences: any[]) => void;
}

export const ExperienceSelector: Component<ExperienceSelectorProps> = props => {
  const handleUseSelected = () => {
    const selectedExperiences = props.experienceOptions
      .filter(exp => props.selectedExperienceIds.includes(exp.id))
      .map(exp => {
        return {
          company: exp.company,
          position: exp.position,
          location: exp.location || '',
          start_date: exp.start_date,
          end_date: exp.end_date || '',
          is_current: exp.is_current,
          description: exp.description,
          achievements: exp.achievements,
        };
      });

    props.onUseSelected(selectedExperiences);
  };

  return (
    <div class='space-y-4'>
      <div class='flex items-center justify-between'>
        <h5 class='font-medium'>Available Experience ({props.experienceOptions.length})</h5>
        <Show when={props.selectedExperienceIds.length > 0}>
          <button type='button' class='btn btn-primary btn-sm' onClick={handleUseSelected}>
            Use Selected ({props.selectedExperienceIds.length})
          </button>
        </Show>
      </div>

      <Show when={props.experienceOptions.length === 0}>
        <div class='text-center py-8 bg-base-200 rounded-lg'>
          <div class='text-4xl mb-2'>💼</div>
          <p class='text-base-content/70'>No work experience found in your Skill Bank</p>
          <p class='text-sm text-base-content/50 mt-1'>
            Go to the Skill Bank tab to add work experience
          </p>
        </div>
      </Show>

      <div class='space-y-3 max-h-96 overflow-y-auto'>
        <For each={props.experienceOptions}>
          {option => (
            <div
              class={`card border-2 ${
                props.selectedExperienceIds.includes(option.id)
                  ? 'border-primary bg-primary/5'
                  : 'border-base-300 bg-base-100'
              }`}
            >
              <div class='card-body p-4'>
                <div class='flex items-start justify-between'>
                  <div class='flex items-start space-x-3 flex-1'>
                    <input
                      type='checkbox'
                      class='checkbox checkbox-primary mt-1'
                      checked={props.selectedExperienceIds.includes(option.id)}
                      onChange={() => props.onToggleSelection(option.id)}
                    />
                    <div class='flex-1'>
                      <h6 class='font-semibold'>{option.position}</h6>
                      <p class='text-sm font-medium text-base-content/80'>{option.company}</p>
                      <p class='text-sm text-base-content/60'>
                        {option.location && `${option.location} • `}
                        {option.start_date} -{' '}
                        {option.is_current ? 'Present' : option.end_date || 'N/A'}
                      </p>

                      <Show when={option.description}>
                        <p class='text-sm text-base-content/70 mt-2 line-clamp-2'>
                          {option.description}
                        </p>
                      </Show>

                      <Show when={option.achievements && option.achievements.length > 0}>
                        <div class='mt-2'>
                          <p class='text-xs font-medium text-base-content/60'>Key Achievements:</p>
                          <ul class='text-xs text-base-content/60 list-disc list-inside'>
                            <For each={option.achievements.slice(0, 2)}>
                              {achievement => <li>{achievement}</li>}
                            </For>
                            <Show when={option.achievements.length > 2}>
                              <li class='text-base-content/50'>
                                +{option.achievements.length - 2} more...
                              </li>
                            </Show>
                          </ul>
                        </div>
                      </Show>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </For>
      </div>
    </div>
  );
};

// =============================================================================
// SKILLS SELECTOR
// =============================================================================

interface SkillOption {
  name: string;
  category: string;
  proficiency_level: string;
  years_experience?: number;
  description?: string;
}

interface SkillsSelectorProps {
  skillsOptions: SkillOption[];
  selectedSkills: string[];
  onToggleSelection: (skillName: string) => void;
  onUseSelected: (skills: SkillOption[]) => void;
}

export const SkillsSelector: Component<SkillsSelectorProps> = props => {
  const handleUseSelected = () => {
    const selectedSkillsData = props.skillsOptions.filter(skill =>
      props.selectedSkills.includes(skill.name)
    );
    props.onUseSelected(selectedSkillsData);
  };

  // Group skills by category
  const skillsByCategory = () => {
    const grouped: Record<string, SkillOption[]> = {};
    props.skillsOptions.forEach(skill => {
      if (!grouped[skill.category]) {
        grouped[skill.category] = [];
      }
      grouped[skill.category].push(skill);
    });
    return grouped;
  };

  return (
    <div class='space-y-4'>
      <div class='flex items-center justify-between'>
        <h5 class='font-medium'>Available Skills ({props.skillsOptions.length})</h5>
        <Show when={props.selectedSkills.length > 0}>
          <button type='button' class='btn btn-primary btn-sm' onClick={handleUseSelected}>
            Use Selected ({props.selectedSkills.length})
          </button>
        </Show>
      </div>

      <Show when={props.skillsOptions.length === 0}>
        <div class='text-center py-8 bg-base-200 rounded-lg'>
          <div class='text-4xl mb-2'>🛠️</div>
          <p class='text-base-content/70'>No skills found in your Skill Bank</p>
          <p class='text-sm text-base-content/50 mt-1'>Go to the Skill Bank tab to add skills</p>
        </div>
      </Show>

      <div class='space-y-4 max-h-96 overflow-y-auto'>
        <For each={Object.entries(skillsByCategory())}>
          {([category, categorySkills]) => (
            <div class='card bg-base-100 border border-base-300'>
              <div class='card-body p-4'>
                <h6 class='font-semibold text-primary mb-3'>{category}</h6>
                <div class='grid grid-cols-1 sm:grid-cols-2 gap-2'>
                  <For each={categorySkills}>
                    {skill => (
                      <label class='flex items-center space-x-2 p-2 rounded-lg hover:bg-base-200 cursor-pointer'>
                        <input
                          type='checkbox'
                          class='checkbox checkbox-primary checkbox-sm'
                          checked={props.selectedSkills.includes(skill.name)}
                          onChange={() => props.onToggleSelection(skill.name)}
                        />
                        <div class='flex-1'>
                          <span class='font-medium text-sm'>{skill.name}</span>
                          <span class='text-xs text-base-content/60 ml-2'>
                            ({skill.proficiency_level})
                          </span>
                        </div>
                      </label>
                    )}
                  </For>
                </div>
              </div>
            </div>
          )}
        </For>
      </div>
    </div>
  );
};
