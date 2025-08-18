import { Component, createSignal, onMount } from 'solid-js';
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

            {/* Other Sections Placeholder */}
            {['experience', 'education', 'skills', 'projects', 'certifications'].includes(
              activeSection()
            ) && (
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
