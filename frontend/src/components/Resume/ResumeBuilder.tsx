import { Component, createSignal, onMount, For, Show } from 'solid-js';
import { ResumeService, CreateResumeRequest } from '../../services/resumeService';

interface ResumeBuilderProps {
  resumeId?: string; // undefined for new resume, string for editing existing
  userId: string;
  onSave: (resumeId: string) => void;
  onCancel: () => void;
}

const ResumeBuilder: Component<ResumeBuilderProps> = props => {
  // Form state
  const [formData, setFormData] = createSignal<CreateResumeRequest>({
    title: '',
    contact_info: {
      full_name: '',
      email: '',
      phone: '',
      location: '',
      linkedin_url: '',
      github_url: '',
      website_url: '',
    },
    summary: '',
    work_experience: [],
    education: [],
    skills: [],
    projects: [],
    certifications: [],
  });

  const [saving, setSaving] = createSignal(false);
  const [error, setError] = createSignal<string | null>(null);
  const [activeSection, setActiveSection] = createSignal<string>('contact');

  // Load existing resume if editing
  onMount(async () => {
    if (props.resumeId) {
      try {
        const resume = await ResumeService.getResume(props.resumeId, props.userId);
        setFormData(resume);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load resume');
        console.error('Failed to load resume:', err);
      }
    }
  });

  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);

      const data = formData();

      if (!data.title.trim()) {
        throw new Error('Resume title is required');
      }

      if (!data.contact_info.full_name.trim()) {
        throw new Error('Full name is required');
      }

      if (!data.contact_info.email.trim()) {
        throw new Error('Email is required');
      }

      let result;
      if (props.resumeId) {
        result = await ResumeService.updateResume(props.resumeId, data, props.userId);
        // For update, the backend returns { message: string, version: number }
        // We use the existing resumeId
        props.onSave(props.resumeId);
      } else {
        result = await ResumeService.createResume(data, props.userId);
        // For create, the backend returns { message: string, resume_id: string, id: string }
        const resumeId = result.resume_id || result.id;
        if (!resumeId) {
          throw new Error('No resume ID returned from server');
        }
        props.onSave(resumeId);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save resume');
      console.error('Failed to save resume:', err);
    } finally {
      setSaving(false);
    }
  };

  const updateContactInfo = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      contact_info: {
        ...prev.contact_info,
        [field]: value,
      },
    }));
  };

  // Work Experience Management Functions
  const addWorkExperience = () => {
    const newExperience = {
      company: '',
      position: '',
      location: '',
      start_date: '',
      end_date: '',
      is_current: false,
      description: '',
      achievements: [],
    };

    setFormData(prev => ({
      ...prev,
      work_experience: [...prev.work_experience, newExperience],
    }));
  };

  const removeWorkExperience = (index: number) => {
    setFormData(prev => ({
      ...prev,
      work_experience: prev.work_experience.filter((_, i) => i !== index),
    }));
  };

  const moveWorkExperienceUp = (index: number) => {
    if (index === 0) return;

    setFormData(prev => {
      const newExperiences = [...prev.work_experience];
      [newExperiences[index - 1], newExperiences[index]] = [
        newExperiences[index],
        newExperiences[index - 1],
      ];
      return {
        ...prev,
        work_experience: newExperiences,
      };
    });
  };

  const moveWorkExperienceDown = (index: number) => {
    setFormData(prev => {
      if (index === prev.work_experience.length - 1) return prev;

      const newExperiences = [...prev.work_experience];
      [newExperiences[index], newExperiences[index + 1]] = [
        newExperiences[index + 1],
        newExperiences[index],
      ];
      return {
        ...prev,
        work_experience: newExperiences,
      };
    });
  };

  const updateWorkExperience = (index: number, field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      work_experience: prev.work_experience.map((exp, i) =>
        i === index ? { ...exp, [field]: value } : exp
      ),
    }));
  };

  const addWorkExperienceAchievement = (experienceIndex: number) => {
    setFormData(prev => ({
      ...prev,
      work_experience: prev.work_experience.map((exp, i) =>
        i === experienceIndex ? { ...exp, achievements: [...(exp.achievements || []), ''] } : exp
      ),
    }));
  };

  const updateWorkExperienceAchievement = (
    experienceIndex: number,
    achievementIndex: number,
    value: string
  ) => {
    setFormData(prev => ({
      ...prev,
      work_experience: prev.work_experience.map((exp, i) =>
        i === experienceIndex
          ? {
              ...exp,
              achievements: (exp.achievements || []).map((ach, j) =>
                j === achievementIndex ? value : ach
              ),
            }
          : exp
      ),
    }));
  };

  const removeWorkExperienceAchievement = (experienceIndex: number, achievementIndex: number) => {
    setFormData(prev => ({
      ...prev,
      work_experience: prev.work_experience.map((exp, i) =>
        i === experienceIndex
          ? {
              ...exp,
              achievements: (exp.achievements || []).filter((_, j) => j !== achievementIndex),
            }
          : exp
      ),
    }));
  };

  const sections = [
    { key: 'contact', label: 'Contact Info', icon: '👤' },
    { key: 'summary', label: 'Summary', icon: '📝' },
    { key: 'experience', label: 'Experience', icon: '💼' },
    { key: 'education', label: 'Education', icon: '🎓' },
    { key: 'skills', label: 'Skills', icon: '🛠️' },
    { key: 'projects', label: 'Projects', icon: '🚀' },
    { key: 'certifications', label: 'Certifications', icon: '🏆' },
  ];

  return (
    <div class='h-full flex flex-col'>
      {/* Header */}
      <div class='bg-base-100 border-b px-6 py-4'>
        <div class='flex justify-between items-center'>
          <div>
            <h2 class='text-2xl font-bold'>
              {props.resumeId ? '✏️ Edit Resume' : '✨ Create New Resume'}
            </h2>
            <p class='text-base-content/70'>
              {props.resumeId ? 'Update your resume information' : 'Build your professional resume'}
            </p>
          </div>
          <div class='flex space-x-2'>
            <button class='btn btn-outline' onClick={props.onCancel} disabled={saving()}>
              Cancel
            </button>
            <button class='btn btn-primary' onClick={handleSave} disabled={saving()}>
              {saving() ? (
                <>
                  <span class='loading loading-spinner loading-sm'></span>
                  Saving...
                </>
              ) : (
                'Save Resume'
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Error Alert */}
      {error() && (
        <div class='alert alert-error mx-6 mt-4'>
          <svg class='w-6 h-6' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
            <path
              stroke-linecap='round'
              stroke-linejoin='round'
              stroke-width='2'
              d='M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 15.5c-.77.833.192 2.5 1.732 2.5z'
            ></path>
          </svg>
          <span>{error()}</span>
        </div>
      )}

      <div class='flex-1 flex overflow-hidden'>
        {/* Sidebar Navigation */}
        <div class='w-64 bg-base-200 border-r overflow-y-auto'>
          <div class='p-4'>
            <h3 class='font-semibold text-sm uppercase tracking-wide text-base-content/60 mb-3'>
              Resume Sections
            </h3>
            <ul class='space-y-1'>
              {sections.map(section => (
                <li>
                  <button
                    class={`w-full text-left px-3 py-2 rounded-lg flex items-center space-x-3 transition-colors ${
                      activeSection() === section.key
                        ? 'bg-primary text-primary-content'
                        : 'hover:bg-base-300'
                    }`}
                    onClick={() => setActiveSection(section.key)}
                  >
                    <span class='text-lg'>{section.icon}</span>
                    <span class='font-medium'>{section.label}</span>
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Main Content Area */}
        <div class='flex-1 overflow-y-auto'>
          <div class='p-6 max-w-4xl'>
            {/* Resume Title */}
            <div class='mb-6'>
              <label class='block text-sm font-medium mb-2'>Resume Title *</label>
              <input
                type='text'
                class='input input-bordered w-full'
                placeholder='e.g., Software Engineer Resume - 2024'
                value={formData().title}
                onInput={e => setFormData(prev => ({ ...prev, title: e.target.value }))}
              />
            </div>

            {/* Contact Information Section */}
            {activeSection() === 'contact' && (
              <div class='space-y-4'>
                <h3 class='text-xl font-semibold mb-4'>👤 Contact Information</h3>

                <div class='grid grid-cols-1 md:grid-cols-2 gap-4'>
                  <div>
                    <label class='block text-sm font-medium mb-2'>Full Name *</label>
                    <input
                      type='text'
                      class='input input-bordered w-full'
                      placeholder='John Doe'
                      value={formData().contact_info.full_name}
                      onInput={e => updateContactInfo('full_name', e.target.value)}
                    />
                  </div>

                  <div>
                    <label class='block text-sm font-medium mb-2'>Email Address *</label>
                    <input
                      type='email'
                      class='input input-bordered w-full'
                      placeholder='john.doe@email.com'
                      value={formData().contact_info.email}
                      onInput={e => updateContactInfo('email', e.target.value)}
                    />
                  </div>

                  <div>
                    <label class='block text-sm font-medium mb-2'>Phone Number</label>
                    <input
                      type='tel'
                      class='input input-bordered w-full'
                      placeholder='+1 (555) 123-4567'
                      value={formData().contact_info.phone}
                      onInput={e => updateContactInfo('phone', e.target.value)}
                    />
                  </div>

                  <div>
                    <label class='block text-sm font-medium mb-2'>Location</label>
                    <input
                      type='text'
                      class='input input-bordered w-full'
                      placeholder='San Francisco, CA'
                      value={formData().contact_info.location}
                      onInput={e => updateContactInfo('location', e.target.value)}
                    />
                  </div>

                  <div>
                    <label class='block text-sm font-medium mb-2'>LinkedIn URL</label>
                    <input
                      type='url'
                      class='input input-bordered w-full'
                      placeholder='https://linkedin.com/in/johndoe'
                      value={formData().contact_info.linkedin_url}
                      onInput={e => updateContactInfo('linkedin_url', e.target.value)}
                    />
                  </div>

                  <div>
                    <label class='block text-sm font-medium mb-2'>GitHub URL</label>
                    <input
                      type='url'
                      class='input input-bordered w-full'
                      placeholder='https://github.com/johndoe'
                      value={formData().contact_info.github_url}
                      onInput={e => updateContactInfo('github_url', e.target.value)}
                    />
                  </div>
                </div>

                <div>
                  <label class='block text-sm font-medium mb-2'>Website/Portfolio</label>
                  <input
                    type='url'
                    class='input input-bordered w-full'
                    placeholder='https://johndoe.com'
                    value={formData().contact_info.website_url}
                    onInput={e => updateContactInfo('website_url', e.target.value)}
                  />
                </div>
              </div>
            )}

            {/* Professional Summary Section */}
            {activeSection() === 'summary' && (
              <div class='space-y-4'>
                <h3 class='text-xl font-semibold mb-4'>📝 Professional Summary</h3>
                <div>
                  <label class='block text-sm font-medium mb-2'>Summary</label>
                  <textarea
                    class='textarea textarea-bordered w-full h-32'
                    placeholder='Write a compelling professional summary that highlights your key skills and experience...'
                    value={formData().summary}
                    onInput={e => setFormData(prev => ({ ...prev, summary: e.target.value }))}
                  ></textarea>
                  <div class='text-sm text-base-content/60 mt-1'>
                    Tip: Keep it concise (2-3 sentences) and focus on your strongest qualifications.
                  </div>
                </div>
              </div>
            )}

            {/* Work Experience Section */}
            {activeSection() === 'experience' && (
              <div class='space-y-4'>
                <h3 class='text-xl font-semibold mb-4'>💼 Work Experience</h3>

                <div class='space-y-6'>
                  {/* Add New Experience Button */}
                  <div class='flex justify-between items-center'>
                    <p class='text-sm text-base-content/70'>
                      Add your work experience, starting with your most recent position.
                    </p>
                    <button
                      type='button'
                      class='btn btn-outline btn-sm'
                      onClick={addWorkExperience}
                    >
                      ➕ Add Experience
                    </button>
                  </div>

                  {/* Work Experience Entries */}
                  <div class='space-y-6'>
                    <For each={formData().work_experience}>
                      {(experience, index) => (
                        <div class='card bg-base-100 border border-base-300 p-6'>
                          {/* Experience Header */}
                          <div class='flex justify-between items-center mb-4'>
                            <h4 class='text-lg font-medium'>Experience {index() + 1}</h4>
                            <div class='flex space-x-2'>
                              {/* Move Up Button */}
                              <Show when={index() > 0}>
                                <button
                                  type='button'
                                  class='btn btn-ghost btn-sm'
                                  onClick={() => moveWorkExperienceUp(index())}
                                  title='Move up'
                                >
                                  ⬆️
                                </button>
                              </Show>

                              {/* Move Down Button */}
                              <Show when={index() < formData().work_experience.length - 1}>
                                <button
                                  type='button'
                                  class='btn btn-ghost btn-sm'
                                  onClick={() => moveWorkExperienceDown(index())}
                                  title='Move down'
                                >
                                  ⬇️
                                </button>
                              </Show>

                              {/* Delete Button */}
                              <button
                                type='button'
                                class='btn btn-ghost btn-sm text-error'
                                onClick={() => removeWorkExperience(index())}
                                title='Remove experience'
                              >
                                🗑️
                              </button>
                            </div>
                          </div>

                          {/* Experience Form Fields */}
                          <div class='grid grid-cols-1 md:grid-cols-2 gap-4'>
                            {/* Company Name */}
                            <div>
                              <label class='block text-sm font-medium mb-2'>Company *</label>
                              <input
                                type='text'
                                class='input input-bordered w-full'
                                placeholder='Company Name'
                                value={experience.company}
                                onInput={e =>
                                  updateWorkExperience(index(), 'company', e.target.value)
                                }
                                required
                              />
                            </div>

                            {/* Position */}
                            <div>
                              <label class='block text-sm font-medium mb-2'>Position *</label>
                              <input
                                type='text'
                                class='input input-bordered w-full'
                                placeholder='Job Title'
                                value={experience.position}
                                onInput={e =>
                                  updateWorkExperience(index(), 'position', e.target.value)
                                }
                                required
                              />
                            </div>

                            {/* Location */}
                            <div>
                              <label class='block text-sm font-medium mb-2'>Location</label>
                              <input
                                type='text'
                                class='input input-bordered w-full'
                                placeholder='City, State'
                                value={experience.location || ''}
                                onInput={e =>
                                  updateWorkExperience(index(), 'location', e.target.value)
                                }
                              />
                            </div>

                            {/* Current Position Checkbox */}
                            <div class='flex items-center space-x-2 pt-8'>
                              <input
                                type='checkbox'
                                class='checkbox'
                                checked={experience.is_current || false}
                                onChange={e =>
                                  updateWorkExperience(index(), 'is_current', e.target.checked)
                                }
                              />
                              <label class='text-sm'>I currently work here</label>
                            </div>

                            {/* Start Date */}
                            <div>
                              <label class='block text-sm font-medium mb-2'>Start Date *</label>
                              <input
                                type='date'
                                class='input input-bordered w-full'
                                value={experience.start_date}
                                onInput={e =>
                                  updateWorkExperience(index(), 'start_date', e.target.value)
                                }
                                required
                              />
                            </div>

                            {/* End Date */}
                            <div>
                              <label class='block text-sm font-medium mb-2'>
                                End Date {experience.is_current ? '(Current)' : '*'}
                              </label>
                              <input
                                type='date'
                                class='input input-bordered w-full'
                                value={experience.end_date || ''}
                                onInput={e =>
                                  updateWorkExperience(index(), 'end_date', e.target.value)
                                }
                                disabled={experience.is_current}
                                required={!experience.is_current}
                              />
                            </div>
                          </div>

                          {/* Description */}
                          <div class='mt-4'>
                            <label class='block text-sm font-medium mb-2'>Job Description</label>
                            <textarea
                              class='textarea textarea-bordered w-full h-24'
                              placeholder='Describe your role, responsibilities, and key contributions...'
                              value={experience.description || ''}
                              onInput={e =>
                                updateWorkExperience(index(), 'description', e.target.value)
                              }
                            ></textarea>
                          </div>

                          {/* Achievements */}
                          <div class='mt-4'>
                            <label class='block text-sm font-medium mb-2'>Key Achievements</label>
                            <div class='space-y-2'>
                              <For each={experience.achievements || []}>
                                {(achievement, achIndex) => (
                                  <div class='flex space-x-2'>
                                    <input
                                      type='text'
                                      class='input input-bordered flex-1'
                                      placeholder='Key achievement or accomplishment'
                                      value={achievement}
                                      onInput={e =>
                                        updateWorkExperienceAchievement(
                                          index(),
                                          achIndex(),
                                          e.target.value
                                        )
                                      }
                                    />
                                    <button
                                      type='button'
                                      class='btn btn-ghost btn-sm text-error'
                                      onClick={() =>
                                        removeWorkExperienceAchievement(index(), achIndex())
                                      }
                                    >
                                      ✕
                                    </button>
                                  </div>
                                )}
                              </For>
                              <button
                                type='button'
                                class='btn btn-ghost btn-sm w-full'
                                onClick={() => addWorkExperienceAchievement(index())}
                              >
                                ➕ Add Achievement
                              </button>
                            </div>
                          </div>
                        </div>
                      )}
                    </For>
                  </div>

                  {/* Empty State */}
                  <Show when={formData().work_experience.length === 0}>
                    <div class='text-center py-12 bg-base-100 rounded-lg border-2 border-dashed border-base-300'>
                      <div class='text-4xl mb-2'>💼</div>
                      <h3 class='text-lg font-medium mb-2'>No work experience added yet</h3>
                      <p class='text-base-content/70 mb-4'>
                        Add your work experience to showcase your professional background
                      </p>
                      <button type='button' class='btn btn-primary' onClick={addWorkExperience}>
                        Add Your First Experience
                      </button>
                    </div>
                  </Show>
                </div>
              </div>
            )}

            {/* Other Sections Placeholder */}
            {['education', 'skills', 'projects', 'certifications'].includes(activeSection()) && (
              <div class='space-y-4'>
                <h3 class='text-xl font-semibold mb-4'>
                  {sections.find(s => s.key === activeSection())?.icon}{' '}
                  {sections.find(s => s.key === activeSection())?.label}
                </h3>
                <div class='text-center py-8 bg-base-200 rounded-lg'>
                  <div class='text-4xl mb-2'>🚧</div>
                  <p class='text-base-content/70'>
                    This section is under development. Coming soon!
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResumeBuilder;
