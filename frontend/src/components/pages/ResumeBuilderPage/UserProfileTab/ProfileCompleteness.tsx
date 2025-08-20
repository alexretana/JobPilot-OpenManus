import { Component, For, Show } from 'solid-js';
import { ProfileCompleteness } from '../../../../services/userProfileApi';

interface ProfileCompletenessProps {
  completeness: ProfileCompleteness;
  onSectionFocus?: (section: 'personal' | 'professional' | 'preferences') => void;
}

const ProfileCompletenessComponent: Component<ProfileCompletenessProps> = props => {
  // Defensive check to ensure completeness data is valid
  const isValidCompleteness = () => {
    return (
      props.completeness &&
      props.completeness.sections &&
      typeof props.completeness.overall_score === 'number'
    );
  };

  const getScoreColor = (score: number): string => {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'error';
  };

  const getScoreDescription = (score: number): string => {
    if (score >= 90) return 'Excellent - Your profile is comprehensive!';
    if (score >= 80) return 'Great - Your profile is well-detailed';
    if (score >= 60) return 'Good - Your profile has most key information';
    if (score >= 40) return 'Fair - Consider adding more details';
    return 'Needs Improvement - Please complete key sections';
  };

  return (
    <Show
      when={isValidCompleteness()}
      fallback={
        <div class='card bg-gradient-to-r from-primary/10 to-secondary/10 shadow-xl'>
          <div class='card-body'>
            <div class='flex justify-center items-center py-8'>
              <span class='loading loading-spinner loading-lg'></span>
              <span class='ml-2'>Loading profile analysis...</span>
            </div>
          </div>
        </div>
      }
    >
      <div class='card bg-gradient-to-r from-primary/10 to-secondary/10 shadow-xl'>
        <div class='card-body'>
          <div class='flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6'>
            {/* Overall Score */}
            <div class='flex items-center gap-4'>
              <div class='relative'>
                <div
                  class={`radial-progress text-${getScoreColor(props.completeness.overall_score)}`}
                  style={`--value: ${props.completeness.overall_score}; --size: 4rem; --thickness: 4px;`}
                  role='progressbar'
                >
                  <span class='text-lg font-bold'>{props.completeness.overall_score}%</span>
                </div>
              </div>
              <div>
                <h3 class='text-xl font-semibold'>Profile Completeness</h3>
                <p class='text-sm text-base-content/70'>
                  {getScoreDescription(props.completeness.overall_score)}
                </p>
              </div>
            </div>

            {/* Section Breakdown */}
            <div class='grid grid-cols-3 gap-4 w-full lg:w-auto'>
              <div
                class='text-center p-3 rounded-lg bg-base-100/50 cursor-pointer hover:bg-base-100/80 transition-colors'
                onClick={() => props.onSectionFocus?.('personal')}
              >
                <div class='text-xs font-medium text-base-content/60 mb-1'>Personal</div>
                <div
                  class={`text-lg font-bold text-${getScoreColor(
                    props.completeness.sections.personal
                  )}`}
                >
                  {props.completeness.sections.personal}%
                </div>
              </div>

              <div
                class='text-center p-3 rounded-lg bg-base-100/50 cursor-pointer hover:bg-base-100/80 transition-colors'
                onClick={() => props.onSectionFocus?.('professional')}
              >
                <div class='text-xs font-medium text-base-content/60 mb-1'>Professional</div>
                <div
                  class={`text-lg font-bold text-${getScoreColor(
                    props.completeness.sections.professional
                  )}`}
                >
                  {props.completeness.sections.professional}%
                </div>
              </div>

              <div
                class='text-center p-3 rounded-lg bg-base-100/50 cursor-pointer hover:bg-base-100/80 transition-colors'
                onClick={() => props.onSectionFocus?.('preferences')}
              >
                <div class='text-xs font-medium text-base-content/60 mb-1'>Preferences</div>
                <div
                  class={`text-lg font-bold text-${getScoreColor(
                    props.completeness.sections.preferences
                  )}`}
                >
                  {props.completeness.sections.preferences}%
                </div>
              </div>
            </div>
          </div>

          {/* Missing Fields Alert */}
          <Show when={props.completeness.missing_fields.length > 0}>
            <div class='alert alert-warning mt-4'>
              <svg class='stroke-current shrink-0 w-6 h-6' fill='none' viewBox='0 0 24 24'>
                <path
                  stroke-linecap='round'
                  stroke-linejoin='round'
                  stroke-width='2'
                  d='M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L5.268 15.5c-.77.833.192 2.5 1.732 2.5z'
                />
              </svg>
              <div class='flex-1'>
                <h3 class='font-medium'>Missing Required Information</h3>
                <div class='text-sm mt-1'>
                  Please complete: {props.completeness.missing_fields.join(', ')}
                </div>
              </div>
            </div>
          </Show>

          {/* Suggestions */}
          <Show when={props.completeness.suggestions.length > 0}>
            <details class='collapse collapse-plus bg-base-100/30 mt-4'>
              <summary class='collapse-title text-sm font-medium'>
                💡 {props.completeness.suggestions.length} Suggestions to Improve Your Profile
              </summary>
              <div class='collapse-content'>
                <ul class='space-y-2 mt-2'>
                  <For each={props.completeness.suggestions}>
                    {suggestion => (
                      <li class='flex items-start gap-2 text-sm'>
                        <svg
                          class='w-4 h-4 text-info shrink-0 mt-0.5'
                          fill='none'
                          stroke='currentColor'
                          viewBox='0 0 24 24'
                        >
                          <path
                            stroke-linecap='round'
                            stroke-linejoin='round'
                            stroke-width='2'
                            d='M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
                          />
                        </svg>
                        <span>{suggestion}</span>
                      </li>
                    )}
                  </For>
                </ul>
              </div>
            </details>
          </Show>

          {/* Profile Strength Benefits */}
          <Show when={props.completeness.overall_score >= 80}>
            <div class='alert alert-success mt-4'>
              <svg class='stroke-current shrink-0 w-6 h-6' fill='none' viewBox='0 0 24 24'>
                <path
                  stroke-linecap='round'
                  stroke-linejoin='round'
                  stroke-width='2'
                  d='M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z'
                />
              </svg>
              <div>
                <h3 class='font-medium'>Excellent Profile! 🎉</h3>
                <div class='text-sm mt-1'>
                  Your complete profile will help you get better job matches and resume generation
                  results.
                </div>
              </div>
            </div>
          </Show>

          <Show
            when={props.completeness.overall_score >= 60 && props.completeness.overall_score < 80}
          >
            <div class='alert alert-info mt-4'>
              <svg class='stroke-current shrink-0 w-6 h-6' fill='none' viewBox='0 0 24 24'>
                <path
                  stroke-linecap='round'
                  stroke-linejoin='round'
                  stroke-width='2'
                  d='M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
                />
              </svg>
              <div>
                <h3 class='font-medium'>Good Progress! 👍</h3>
                <div class='text-sm mt-1'>
                  Complete a few more sections to unlock better job matching and resume features.
                </div>
              </div>
            </div>
          </Show>
        </div>
      </div>
    </Show>
  );
};

export default ProfileCompletenessComponent;
