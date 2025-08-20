import { Component, createSignal, onMount, For, Show } from 'solid-js';
import { ResumeService, CreateResumeRequest } from '../../../../../services/resumeService';
import { userProfileApi } from '../../../../../services/userProfileApi';
import { ResumeImportService } from '../../../../../services/resumeImportService';
import { useSkillBankIntegration } from '../../../../../hooks/useSkillBankIntegration';
import {
  SkillBankToggle,
  SummarySelector,
  ExperienceSelector,
  SkillsSelector,
} from '../../../../../components/SkillBankSelectors';

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

  // Initialize Skill Bank integration
  const skillBank = useSkillBankIntegration(props.userId);

  // State for managing skill bank selections
  const [selectedExperienceIds, setSelectedExperienceIds] = createSignal<string[]>([]);
  const [selectedSkills, setSelectedSkills] = createSignal<string[]>([]);

  // Load existing resume if editing, or populate with profile data for new resume
  onMount(async () => {
    if (props.resumeId) {
      // Editing existing resume
      try {
        const resume = await ResumeService.getResume(props.resumeId, props.userId);
        setFormData(resume);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load resume');
        console.error('Failed to load resume:', err);
      }
    } else {
      // Creating new resume - populate with profile data
      try {
        const profile = await userProfileApi.getProfile(props.userId);
        const resumeData = ResumeImportService.mapProfileToResume(profile, {
          includeContactInfo: true,
          includeSummary: true,
          includeSkills: true,
          includeEducation: true,
          includeExperience: false, // Don't auto-populate work experience
        });

        setFormData(resumeData);
        console.log('Pre-populated resume with profile data:', resumeData);
      } catch (err) {
        // If profile loading fails, just continue with empty form
        console.warn('Could not load profile data for resume:', err);
        // The form already starts with empty data, so no need to do anything
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
      work_experience: [...(prev.work_experience || []), newExperience],
    }));
  };

  const removeWorkExperience = (index: number) => {
    setFormData(prev => ({
      ...prev,
      work_experience: (prev.work_experience || []).filter((_, i) => i !== index),
    }));
  };

  const moveWorkExperienceUp = (index: number) => {
    if (index === 0) return;

    setFormData(prev => {
      const newExperiences = [...(prev.work_experience || [])];
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
      const workExp = prev.work_experience || [];
      if (index === workExp.length - 1) return prev;

      const newExperiences = [...workExp];
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
      work_experience: (prev.work_experience || []).map((exp, i) =>
        i === index ? { ...exp, [field]: value } : exp
      ),
    }));
  };

  const addWorkExperienceAchievement = (experienceIndex: number) => {
    setFormData(prev => ({
      ...prev,
      work_experience: (prev.work_experience || []).map((exp, i) =>
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
      work_experience: (prev.work_experience || []).map((exp, i) =>
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
      work_experience: (prev.work_experience || []).map((exp, i) =>
        i === experienceIndex
          ? {
              ...exp,
              achievements: (exp.achievements || []).filter((_, j) => j !== achievementIndex),
            }
          : exp
      ),
    }));
  };

  // Education Management Functions
  const addEducation = () => {
    const newEducation = {
      institution: '',
      degree: '',
      field_of_study: '',
      location: '',
      start_date: '',
      graduation_date: '',
      gpa: '',
      honors: [],
      relevant_coursework: [],
    };

    setFormData(prev => ({
      ...prev,
      education: [...(prev.education || []), newEducation],
    }));
  };

  const removeEducation = (index: number) => {
    setFormData(prev => ({
      ...prev,
      education: (prev.education || []).filter((_, i) => i !== index),
    }));
  };

  const moveEducationUp = (index: number) => {
    if (index === 0) return;

    setFormData(prev => {
      const newEducation = [...(prev.education || [])];
      [newEducation[index - 1], newEducation[index]] = [
        newEducation[index],
        newEducation[index - 1],
      ];
      return {
        ...prev,
        education: newEducation,
      };
    });
  };

  const moveEducationDown = (index: number) => {
    setFormData(prev => {
      const education = prev.education || [];
      if (index === education.length - 1) return prev;

      const newEducation = [...education];
      [newEducation[index], newEducation[index + 1]] = [
        newEducation[index + 1],
        newEducation[index],
      ];
      return {
        ...prev,
        education: newEducation,
      };
    });
  };

  const updateEducation = (index: number, field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      education: (prev.education || []).map((edu, i) =>
        i === index ? { ...edu, [field]: value } : edu
      ),
    }));
  };

  const addEducationHonor = (educationIndex: number) => {
    setFormData(prev => ({
      ...prev,
      education: (prev.education || []).map((edu, i) =>
        i === educationIndex ? { ...edu, honors: [...(edu.honors || []), ''] } : edu
      ),
    }));
  };

  const updateEducationHonor = (educationIndex: number, honorIndex: number, value: string) => {
    setFormData(prev => ({
      ...prev,
      education: (prev.education || []).map((edu, i) =>
        i === educationIndex
          ? {
              ...edu,
              honors: (edu.honors || []).map((honor, j) => (j === honorIndex ? value : honor)),
            }
          : edu
      ),
    }));
  };

  const removeEducationHonor = (educationIndex: number, honorIndex: number) => {
    setFormData(prev => ({
      ...prev,
      education: (prev.education || []).map((edu, i) =>
        i === educationIndex
          ? {
              ...edu,
              honors: (edu.honors || []).filter((_, j) => j !== honorIndex),
            }
          : edu
      ),
    }));
  };

  const addEducationCourse = (educationIndex: number) => {
    setFormData(prev => ({
      ...prev,
      education: (prev.education || []).map((edu, i) =>
        i === educationIndex
          ? { ...edu, relevant_coursework: [...(edu.relevant_coursework || []), ''] }
          : edu
      ),
    }));
  };

  const updateEducationCourse = (educationIndex: number, courseIndex: number, value: string) => {
    setFormData(prev => ({
      ...prev,
      education: (prev.education || []).map((edu, i) =>
        i === educationIndex
          ? {
              ...edu,
              relevant_coursework: (edu.relevant_coursework || []).map((course, j) =>
                j === courseIndex ? value : course
              ),
            }
          : edu
      ),
    }));
  };

  const removeEducationCourse = (educationIndex: number, courseIndex: number) => {
    setFormData(prev => ({
      ...prev,
      education: (prev.education || []).map((edu, i) =>
        i === educationIndex
          ? {
              ...edu,
              relevant_coursework: (edu.relevant_coursework || []).filter(
                (_, j) => j !== courseIndex
              ),
            }
          : edu
      ),
    }));
  };

  // Skills Management Functions
  const addSkill = () => {
    const newSkill = {
      name: '',
      category: 'Technical Skills',
      proficiency_level: 'Intermediate',
    };

    setFormData(prev => ({
      ...prev,
      skills: [...(prev.skills || []), newSkill],
    }));
  };

  const removeSkill = (index: number) => {
    setFormData(prev => ({
      ...prev,
      skills: (prev.skills || []).filter((_, i) => i !== index),
    }));
  };

  const updateSkill = (index: number, field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      skills: (prev.skills || []).map((skill, i) =>
        i === index ? { ...skill, [field]: value } : skill
      ),
    }));
  };

  const moveSkillUp = (index: number) => {
    if (index === 0) return;

    setFormData(prev => {
      const newSkills = [...(prev.skills || [])];
      [newSkills[index - 1], newSkills[index]] = [newSkills[index], newSkills[index - 1]];
      return {
        ...prev,
        skills: newSkills,
      };
    });
  };

  const moveSkillDown = (index: number) => {
    setFormData(prev => {
      if (index === (prev.skills || []).length - 1) return prev;

      const newSkills = [...(prev.skills || [])];
      [newSkills[index], newSkills[index + 1]] = [newSkills[index + 1], newSkills[index]];
      return {
        ...prev,
        skills: newSkills,
      };
    });
  };

  const getSkillsByCategory = () => {
    const skillsByCategory: Record<
      string,
      Array<{ name: string; category?: string; proficiency_level?: string; originalIndex: number }>
    > = {};

    (formData().skills || []).forEach((skill, index) => {
      const category = skill.category || 'Other';
      if (!skillsByCategory[category]) {
        skillsByCategory[category] = [];
      }
      skillsByCategory[category].push({ ...skill, originalIndex: index });
    });

    return skillsByCategory;
  };

  // ===============================
  // Projects Management Functions
  // ===============================
  const addProject = () => {
    const newProject = {
      name: '',
      description: '',
      technologies: [],
      url: '',
      start_date: '',
      end_date: '',
      achievements: [],
    };

    setFormData(prev => ({
      ...prev,
      projects: [...(prev.projects || []), newProject],
    }));
  };

  const removeProject = (index: number) => {
    setFormData(prev => ({
      ...prev,
      projects: (prev.projects || []).filter((_, i) => i !== index),
    }));
  };

  const updateProject = (index: number, field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      projects: (prev.projects || []).map((project, i) =>
        i === index ? { ...project, [field]: value } : project
      ),
    }));
  };

  const moveProjectUp = (index: number) => {
    if (index === 0) return;

    setFormData(prev => {
      const newProjects = [...(prev.projects || [])];
      [newProjects[index - 1], newProjects[index]] = [newProjects[index], newProjects[index - 1]];
      return {
        ...prev,
        projects: newProjects,
      };
    });
  };

  const moveProjectDown = (index: number) => {
    setFormData(prev => {
      if (index === (prev.projects || []).length - 1) return prev;

      const newProjects = [...(prev.projects || [])];
      [newProjects[index], newProjects[index + 1]] = [newProjects[index + 1], newProjects[index]];
      return {
        ...prev,
        projects: newProjects,
      };
    });
  };

  const addProjectTechnology = (projectIndex: number) => {
    setFormData(prev => ({
      ...prev,
      projects: (prev.projects || []).map((project, i) =>
        i === projectIndex
          ? { ...project, technologies: [...(project.technologies || []), ''] }
          : project
      ),
    }));
  };

  const updateProjectTechnology = (projectIndex: number, techIndex: number, value: string) => {
    setFormData(prev => ({
      ...prev,
      projects: (prev.projects || []).map((project, i) =>
        i === projectIndex
          ? {
              ...project,
              technologies: (project.technologies || []).map((tech, j) =>
                j === techIndex ? value : tech
              ),
            }
          : project
      ),
    }));
  };

  const removeProjectTechnology = (projectIndex: number, techIndex: number) => {
    setFormData(prev => ({
      ...prev,
      projects: (prev.projects || []).map((project, i) =>
        i === projectIndex
          ? {
              ...project,
              technologies: (project.technologies || []).filter((_, j) => j !== techIndex),
            }
          : project
      ),
    }));
  };

  const addProjectAchievement = (projectIndex: number) => {
    setFormData(prev => ({
      ...prev,
      projects: (prev.projects || []).map((project, i) =>
        i === projectIndex
          ? { ...project, achievements: [...(project.achievements || []), ''] }
          : project
      ),
    }));
  };

  const updateProjectAchievement = (
    projectIndex: number,
    achievementIndex: number,
    value: string
  ) => {
    setFormData(prev => ({
      ...prev,
      projects: (prev.projects || []).map((project, i) =>
        i === projectIndex
          ? {
              ...project,
              achievements: (project.achievements || []).map((ach, j) =>
                j === achievementIndex ? value : ach
              ),
            }
          : project
      ),
    }));
  };

  const removeProjectAchievement = (projectIndex: number, achievementIndex: number) => {
    setFormData(prev => ({
      ...prev,
      projects: (prev.projects || []).map((project, i) =>
        i === projectIndex
          ? {
              ...project,
              achievements: (project.achievements || []).filter((_, j) => j !== achievementIndex),
            }
          : project
      ),
    }));
  };

  // ====================================
  // Certifications Management Functions
  // ====================================
  const addCertification = () => {
    const newCertification = {
      name: '',
      issuer: '',
      date_earned: '',
      expiry_date: '',
      credential_id: '',
      verification_url: '',
      status: 'Active',
    };

    setFormData(prev => ({
      ...prev,
      certifications: [...(prev.certifications || []), newCertification],
    }));
  };

  const removeCertification = (index: number) => {
    setFormData(prev => ({
      ...prev,
      certifications: (prev.certifications || []).filter((_, i) => i !== index),
    }));
  };

  const updateCertification = (index: number, field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      certifications: (prev.certifications || []).map((cert, i) =>
        i === index ? { ...cert, [field]: value } : cert
      ),
    }));
  };

  const moveCertificationUp = (index: number) => {
    if (index === 0) return;

    setFormData(prev => {
      const newCertifications = [...(prev.certifications || [])];
      [newCertifications[index - 1], newCertifications[index]] = [
        newCertifications[index],
        newCertifications[index - 1],
      ];
      return {
        ...prev,
        certifications: newCertifications,
      };
    });
  };

  const moveCertificationDown = (index: number) => {
    setFormData(prev => {
      if (index === (prev.certifications || []).length - 1) return prev;

      const newCertifications = [...(prev.certifications || [])];
      [newCertifications[index], newCertifications[index + 1]] = [
        newCertifications[index + 1],
        newCertifications[index],
      ];
      return {
        ...prev,
        certifications: newCertifications,
      };
    });
  };

  const getCertificationStatus = (certification: any) => {
    if (!certification.expiry_date) return 'Active';

    const expiryDate = new Date(certification.expiry_date);
    const today = new Date();
    const thirtyDaysFromNow = new Date(today.getTime() + 30 * 24 * 60 * 60 * 1000);

    if (expiryDate < today) return 'Expired';
    if (expiryDate < thirtyDaysFromNow) return 'Expiring Soon';
    return 'Active';
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
                <div class='flex items-center justify-between mb-4'>
                  <h3 class='text-xl font-semibold'>📝 Professional Summary</h3>
                  <SkillBankToggle
                    label='Use Summary from Skill Bank'
                    description='Choose from your saved professional summaries'
                    isEnabled={skillBank.toggles().summary}
                    onToggle={enabled => skillBank.setToggle('summary', enabled)}
                    icon='📝'
                  />
                </div>

                <Show when={skillBank.toggles().summary && !skillBank.loading()}>
                  <SummarySelector
                    summaryOptions={skillBank.summaries()}
                    selectedSummaryId={null}
                    onSelect={summaryId => {
                      // Find the selected summary option and use its content
                      const selectedOption = skillBank
                        .summaries()
                        .find(opt => opt.id === summaryId);
                      if (selectedOption) {
                        setFormData(prev => ({ ...prev, summary: selectedOption.content }));
                      }
                    }}
                    onUseSelected={summary => {
                      setFormData(prev => ({ ...prev, summary }));
                    }}
                  />
                </Show>

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
                <div class='flex items-center justify-between mb-4'>
                  <h3 class='text-xl font-semibold'>💼 Work Experience</h3>
                  <SkillBankToggle
                    label='Use Experience from Skill Bank'
                    description='Import experiences from your saved work history'
                    isEnabled={skillBank.toggles().experience}
                    onToggle={enabled => skillBank.setToggle('experience', enabled)}
                    icon='💼'
                  />
                </div>

                <Show when={skillBank.toggles().experience && !skillBank.loading()}>
                  <ExperienceSelector
                    experienceOptions={skillBank.experiences()}
                    selectedExperienceIds={selectedExperienceIds()}
                    onToggleSelection={experienceId => {
                      setSelectedExperienceIds(prev =>
                        prev.includes(experienceId)
                          ? prev.filter(id => id !== experienceId)
                          : [...prev, experienceId]
                      );
                    }}
                    onUseSelected={selectedExperiences => {
                      setFormData(prev => ({
                        ...prev,
                        work_experience: [...(prev.work_experience || []), ...selectedExperiences],
                      }));
                      // Clear selections after using
                      setSelectedExperienceIds([]);
                    }}
                  />
                </Show>

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
                              <Show when={index() < (formData().work_experience || []).length - 1}>
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
                  <Show when={(formData().work_experience || []).length === 0}>
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

            {/* Education Section */}
            {activeSection() === 'education' && (
              <div class='space-y-4'>
                <h3 class='text-xl font-semibold mb-4'>🎓 Education</h3>

                <div class='space-y-6'>
                  {/* Add New Education Button */}
                  <div class='flex justify-between items-center'>
                    <p class='text-sm text-base-content/70'>
                      Add your educational background, starting with your most recent degree.
                    </p>
                    <button type='button' class='btn btn-outline btn-sm' onClick={addEducation}>
                      ➕ Add Education
                    </button>
                  </div>

                  {/* Education Entries */}
                  <div class='space-y-6'>
                    <For each={formData().education}>
                      {(education, index) => (
                        <div class='card bg-base-100 border border-base-300 p-6'>
                          {/* Education Header */}
                          <div class='flex justify-between items-center mb-4'>
                            <h4 class='text-lg font-medium'>Education {index() + 1}</h4>
                            <div class='flex space-x-2'>
                              {/* Move Up Button */}
                              <Show when={index() > 0}>
                                <button
                                  type='button'
                                  class='btn btn-ghost btn-sm'
                                  onClick={() => moveEducationUp(index())}
                                  title='Move up'
                                >
                                  ⬆️
                                </button>
                              </Show>

                              {/* Move Down Button */}
                              <Show when={index() < (formData().education || []).length - 1}>
                                <button
                                  type='button'
                                  class='btn btn-ghost btn-sm'
                                  onClick={() => moveEducationDown(index())}
                                  title='Move down'
                                >
                                  ⬇️
                                </button>
                              </Show>

                              {/* Delete Button */}
                              <button
                                type='button'
                                class='btn btn-ghost btn-sm text-error'
                                onClick={() => removeEducation(index())}
                                title='Remove education'
                              >
                                🗑️
                              </button>
                            </div>
                          </div>

                          {/* Education Form Fields */}
                          <div class='grid grid-cols-1 md:grid-cols-2 gap-4'>
                            {/* Institution Name */}
                            <div>
                              <label class='block text-sm font-medium mb-2'>Institution *</label>
                              <input
                                type='text'
                                class='input input-bordered w-full'
                                placeholder='University Name'
                                value={education.institution}
                                onInput={e =>
                                  updateEducation(index(), 'institution', e.target.value)
                                }
                                required
                              />
                            </div>

                            {/* Degree */}
                            <div>
                              <label class='block text-sm font-medium mb-2'>Degree *</label>
                              <select
                                class='select select-bordered w-full'
                                value={education.degree}
                                onChange={e => updateEducation(index(), 'degree', e.target.value)}
                                required
                              >
                                <option value='' disabled>
                                  Select degree type
                                </option>
                                <option value='High School Diploma'>High School Diploma</option>
                                <option value="Associate's Degree">Associate's Degree</option>
                                <option value="Bachelor's Degree">Bachelor's Degree</option>
                                <option value="Master's Degree">Master's Degree</option>
                                <option value='MBA'>MBA</option>
                                <option value='PhD'>PhD</option>
                                <option value='Professional Degree'>Professional Degree</option>
                                <option value='Certificate'>Certificate</option>
                                <option value='Other'>Other</option>
                              </select>
                            </div>

                            {/* Field of Study */}
                            <div>
                              <label class='block text-sm font-medium mb-2'>Field of Study</label>
                              <input
                                type='text'
                                class='input input-bordered w-full'
                                placeholder='Major/Field of Study'
                                value={education.field_of_study || ''}
                                onInput={e =>
                                  updateEducation(index(), 'field_of_study', e.target.value)
                                }
                              />
                            </div>

                            {/* Location */}
                            <div>
                              <label class='block text-sm font-medium mb-2'>Location</label>
                              <input
                                type='text'
                                class='input input-bordered w-full'
                                placeholder='City, State'
                                value={education.location || ''}
                                onInput={e => updateEducation(index(), 'location', e.target.value)}
                              />
                            </div>

                            {/* Start Date */}
                            <div>
                              <label class='block text-sm font-medium mb-2'>Start Date</label>
                              <input
                                type='date'
                                class='input input-bordered w-full'
                                value={education.start_date || ''}
                                onInput={e =>
                                  updateEducation(index(), 'start_date', e.target.value)
                                }
                              />
                            </div>

                            {/* Graduation Date */}
                            <div>
                              <label class='block text-sm font-medium mb-2'>Graduation Date</label>
                              <input
                                type='date'
                                class='input input-bordered w-full'
                                value={education.graduation_date || ''}
                                onInput={e =>
                                  updateEducation(index(), 'graduation_date', e.target.value)
                                }
                              />
                            </div>

                            {/* GPA */}
                            <div>
                              <label class='block text-sm font-medium mb-2'>GPA (Optional)</label>
                              <input
                                type='number'
                                class='input input-bordered w-full'
                                placeholder='3.8'
                                step='0.1'
                                min='0'
                                max='4.0'
                                value={education.gpa || ''}
                                onInput={e => updateEducation(index(), 'gpa', e.target.value)}
                              />
                            </div>
                          </div>

                          {/* Honors and Achievements */}
                          <div class='mt-4'>
                            <label class='block text-sm font-medium mb-2'>
                              Honors & Achievements
                            </label>
                            <div class='space-y-2'>
                              <For each={education.honors || []}>
                                {(honor, honorIndex) => (
                                  <div class='flex space-x-2'>
                                    <input
                                      type='text'
                                      class='input input-bordered flex-1'
                                      placeholder='Honor, award, or achievement'
                                      value={honor}
                                      onInput={e =>
                                        updateEducationHonor(index(), honorIndex(), e.target.value)
                                      }
                                    />
                                    <button
                                      type='button'
                                      class='btn btn-ghost btn-sm text-error'
                                      onClick={() => removeEducationHonor(index(), honorIndex())}
                                    >
                                      ✕
                                    </button>
                                  </div>
                                )}
                              </For>
                              <button
                                type='button'
                                class='btn btn-ghost btn-sm w-full'
                                onClick={() => addEducationHonor(index())}
                              >
                                ➕ Add Honor/Achievement
                              </button>
                            </div>
                          </div>

                          {/* Relevant Coursework */}
                          <div class='mt-4'>
                            <label class='block text-sm font-medium mb-2'>
                              Relevant Coursework
                            </label>
                            <div class='space-y-2'>
                              <For each={education.relevant_coursework || []}>
                                {(course, courseIndex) => (
                                  <div class='flex space-x-2'>
                                    <input
                                      type='text'
                                      class='input input-bordered flex-1'
                                      placeholder='Course name'
                                      value={course}
                                      onInput={e =>
                                        updateEducationCourse(
                                          index(),
                                          courseIndex(),
                                          e.target.value
                                        )
                                      }
                                    />
                                    <button
                                      type='button'
                                      class='btn btn-ghost btn-sm text-error'
                                      onClick={() => removeEducationCourse(index(), courseIndex())}
                                    >
                                      ✕
                                    </button>
                                  </div>
                                )}
                              </For>
                              <button
                                type='button'
                                class='btn btn-ghost btn-sm w-full'
                                onClick={() => addEducationCourse(index())}
                              >
                                ➕ Add Course
                              </button>
                            </div>
                          </div>
                        </div>
                      )}
                    </For>
                  </div>

                  {/* Empty State */}
                  <Show when={(formData().education || []).length === 0}>
                    <div class='text-center py-12 bg-base-100 rounded-lg border-2 border-dashed border-base-300'>
                      <div class='text-4xl mb-2'>🎓</div>
                      <h3 class='text-lg font-medium mb-2'>No education added yet</h3>
                      <p class='text-base-content/70 mb-4'>
                        Add your educational background to showcase your qualifications
                      </p>
                      <button type='button' class='btn btn-primary' onClick={addEducation}>
                        Add Your First Education
                      </button>
                    </div>
                  </Show>
                </div>
              </div>
            )}

            {/* Skills Section */}
            {activeSection() === 'skills' && (
              <div class='space-y-4'>
                <div class='flex items-center justify-between mb-4'>
                  <h3 class='text-xl font-semibold'>🛠️ Skills</h3>
                  <SkillBankToggle
                    label='Use Skills from Skill Bank'
                    description='Import skills from your saved skill categories'
                    isEnabled={skillBank.toggles().skills}
                    onToggle={enabled => skillBank.setToggle('skills', enabled)}
                    icon='🛠️'
                  />
                </div>

                <Show when={skillBank.toggles().skills && !skillBank.loading()}>
                  <SkillsSelector
                    skillsOptions={skillBank.skills()}
                    selectedSkills={selectedSkills()}
                    onToggleSelection={skillName => {
                      setSelectedSkills(prev =>
                        prev.includes(skillName)
                          ? prev.filter(name => name !== skillName)
                          : [...prev, skillName]
                      );
                    }}
                    onUseSelected={selectedSkillsData => {
                      setFormData(prev => ({
                        ...prev,
                        skills: [...(prev.skills || []), ...selectedSkillsData],
                      }));
                      // Clear selections after using
                      setSelectedSkills([]);
                    }}
                  />
                </Show>

                <div class='space-y-6'>
                  {/* Add New Skill Button */}
                  <div class='flex justify-between items-center'>
                    <p class='text-sm text-base-content/70'>
                      Add your skills organized by category with proficiency levels.
                    </p>
                    <button type='button' class='btn btn-outline btn-sm' onClick={addSkill}>
                      ➕ Add Skill
                    </button>
                  </div>

                  {/* Skills organized by Category */}
                  <div class='space-y-6'>
                    <For each={Object.entries(getSkillsByCategory())}>
                      {([category, categorySkills]) => (
                        <div class='card bg-base-100 border border-base-300 p-6'>
                          <div class='mb-4'>
                            <h4 class='text-lg font-medium text-primary'>{category}</h4>
                            <p class='text-sm text-base-content/60 mt-1'>
                              {categorySkills.length} skill{categorySkills.length !== 1 ? 's' : ''}{' '}
                              in this category
                            </p>
                          </div>

                          <div class='space-y-3'>
                            <For each={categorySkills}>
                              {skill => (
                                <div class='grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-base-50 rounded-lg border'>
                                  {/* Skill Name */}
                                  <div>
                                    <label class='block text-sm font-medium mb-2'>
                                      Skill Name *
                                    </label>
                                    <input
                                      type='text'
                                      class='input input-bordered w-full'
                                      placeholder='e.g., JavaScript'
                                      value={skill.name}
                                      onInput={e =>
                                        updateSkill(skill.originalIndex, 'name', e.target.value)
                                      }
                                      required
                                    />
                                  </div>

                                  {/* Category */}
                                  <div>
                                    <label class='block text-sm font-medium mb-2'>Category</label>
                                    <select
                                      class='select select-bordered w-full'
                                      value={skill.category || 'Technical Skills'}
                                      onChange={e =>
                                        updateSkill(skill.originalIndex, 'category', e.target.value)
                                      }
                                    >
                                      <option value='Technical Skills'>Technical Skills</option>
                                      <option value='Programming Languages'>
                                        Programming Languages
                                      </option>
                                      <option value='Frameworks & Libraries'>
                                        Frameworks & Libraries
                                      </option>
                                      <option value='Tools & Software'>Tools & Software</option>
                                      <option value='Soft Skills'>Soft Skills</option>
                                      <option value='Languages'>Languages</option>
                                      <option value='Certifications'>Certifications</option>
                                      <option value='Design'>Design</option>
                                      <option value='Data & Analytics'>Data & Analytics</option>
                                      <option value='Other'>Other</option>
                                    </select>
                                  </div>

                                  {/* Proficiency Level */}
                                  <div>
                                    <label class='block text-sm font-medium mb-2'>
                                      Proficiency
                                    </label>
                                    <div class='flex items-center space-x-2'>
                                      <select
                                        class='select select-bordered flex-1'
                                        value={skill.proficiency_level || 'Intermediate'}
                                        onChange={e =>
                                          updateSkill(
                                            skill.originalIndex,
                                            'proficiency_level',
                                            e.target.value
                                          )
                                        }
                                      >
                                        <option value='Beginner'>Beginner</option>
                                        <option value='Intermediate'>Intermediate</option>
                                        <option value='Advanced'>Advanced</option>
                                        <option value='Expert'>Expert</option>
                                      </select>

                                      {/* Action Buttons */}
                                      <div class='flex space-x-1'>
                                        {/* Move Up */}
                                        <Show when={skill.originalIndex > 0}>
                                          <button
                                            type='button'
                                            class='btn btn-ghost btn-xs'
                                            onClick={() => moveSkillUp(skill.originalIndex)}
                                            title='Move up'
                                          >
                                            ⬆️
                                          </button>
                                        </Show>

                                        {/* Move Down */}
                                        <Show
                                          when={
                                            skill.originalIndex <
                                            (formData().skills || []).length - 1
                                          }
                                        >
                                          <button
                                            type='button'
                                            class='btn btn-ghost btn-xs'
                                            onClick={() => moveSkillDown(skill.originalIndex)}
                                            title='Move down'
                                          >
                                            ⬇️
                                          </button>
                                        </Show>

                                        {/* Delete */}
                                        <button
                                          type='button'
                                          class='btn btn-ghost btn-xs text-error'
                                          onClick={() => removeSkill(skill.originalIndex)}
                                          title='Remove skill'
                                        >
                                          🗑️
                                        </button>
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              )}
                            </For>
                          </div>
                        </div>
                      )}
                    </For>
                  </div>

                  {/* Empty State */}
                  <Show when={(formData().skills || []).length === 0}>
                    <div class='text-center py-12 bg-base-100 rounded-lg border-2 border-dashed border-base-300'>
                      <div class='text-4xl mb-2'>🛠️</div>
                      <h3 class='text-lg font-medium mb-2'>No skills added yet</h3>
                      <p class='text-base-content/70 mb-4'>
                        Add your technical and soft skills to showcase your expertise
                      </p>
                      <button type='button' class='btn btn-primary' onClick={addSkill}>
                        Add Your First Skill
                      </button>
                    </div>
                  </Show>

                  {/* Skills Summary */}
                  <Show when={(formData().skills || []).length > 0}>
                    <div class='bg-info/10 border border-info/20 rounded-lg p-4'>
                      <div class='flex items-start space-x-3'>
                        <div class='text-info text-xl'>💡</div>
                        <div>
                          <h4 class='font-medium text-info-content mb-2'>Skills Summary</h4>
                          <p class='text-sm text-base-content/70'>
                            Total: {(formData().skills || []).length} skills across{' '}
                            {Object.keys(getSkillsByCategory()).length} categories
                          </p>
                          <div class='mt-2 text-xs text-base-content/60'>
                            <strong>Tip:</strong> Focus on skills relevant to your target role. Use
                            specific technologies and tools rather than generic terms.
                          </div>
                        </div>
                      </div>
                    </div>
                  </Show>
                </div>
              </div>
            )}

            {/* Projects Section */}
            {activeSection() === 'projects' && (
              <div class='space-y-4'>
                <h3 class='text-xl font-semibold mb-4'>🚀 Projects</h3>

                <div class='space-y-6'>
                  {/* Add New Project Button */}
                  <div class='flex justify-between items-center'>
                    <p class='text-sm text-base-content/70'>
                      Showcase your projects, starting with your most impressive or recent work.
                    </p>
                    <button type='button' class='btn btn-outline btn-sm' onClick={addProject}>
                      ➕ Add Project
                    </button>
                  </div>

                  {/* Project Entries */}
                  <div class='space-y-6'>
                    <For each={formData().projects}>
                      {(project, index) => (
                        <div class='card bg-base-100 border border-base-300 p-6'>
                          {/* Project Header */}
                          <div class='flex justify-between items-center mb-4'>
                            <h4 class='text-lg font-medium'>Project {index() + 1}</h4>
                            <div class='flex space-x-2'>
                              {/* Move Up Button */}
                              <Show when={index() > 0}>
                                <button
                                  type='button'
                                  class='btn btn-ghost btn-sm'
                                  onClick={() => moveProjectUp(index())}
                                  title='Move up'
                                >
                                  ⬆️
                                </button>
                              </Show>

                              {/* Move Down Button */}
                              <Show when={index() < (formData().projects || []).length - 1}>
                                <button
                                  type='button'
                                  class='btn btn-ghost btn-sm'
                                  onClick={() => moveProjectDown(index())}
                                  title='Move down'
                                >
                                  ⬇️
                                </button>
                              </Show>

                              {/* Delete Button */}
                              <button
                                type='button'
                                class='btn btn-ghost btn-sm text-error'
                                onClick={() => removeProject(index())}
                                title='Remove project'
                              >
                                🗑️
                              </button>
                            </div>
                          </div>

                          {/* Project Form Fields */}
                          <div class='grid grid-cols-1 md:grid-cols-2 gap-4'>
                            {/* Project Name */}
                            <div>
                              <label class='block text-sm font-medium mb-2'>Project Name *</label>
                              <input
                                type='text'
                                class='input input-bordered w-full'
                                placeholder='My Awesome Project'
                                value={project.name}
                                onInput={e => updateProject(index(), 'name', e.target.value)}
                                required
                              />
                            </div>

                            {/* Project URL */}
                            <div>
                              <label class='block text-sm font-medium mb-2'>Project URL</label>
                              <input
                                type='url'
                                class='input input-bordered w-full'
                                placeholder='https://github.com/user/project'
                                value={project.url || ''}
                                onInput={e => updateProject(index(), 'url', e.target.value)}
                              />
                            </div>

                            {/* Start Date */}
                            <div>
                              <label class='block text-sm font-medium mb-2'>Start Date</label>
                              <input
                                type='date'
                                class='input input-bordered w-full'
                                value={project.start_date || ''}
                                onInput={e => updateProject(index(), 'start_date', e.target.value)}
                              />
                            </div>

                            {/* End Date */}
                            <div>
                              <label class='block text-sm font-medium mb-2'>End Date</label>
                              <input
                                type='date'
                                class='input input-bordered w-full'
                                value={project.end_date || ''}
                                onInput={e => updateProject(index(), 'end_date', e.target.value)}
                              />
                            </div>
                          </div>

                          {/* Description */}
                          <div class='mt-4'>
                            <label class='block text-sm font-medium mb-2'>
                              Project Description
                            </label>
                            <textarea
                              class='textarea textarea-bordered w-full h-24'
                              placeholder='Describe what this project does, your role, and key features...'
                              value={project.description || ''}
                              onInput={e => updateProject(index(), 'description', e.target.value)}
                            ></textarea>
                          </div>

                          {/* Technologies */}
                          <div class='mt-4'>
                            <label class='block text-sm font-medium mb-2'>Technologies Used</label>
                            <div class='space-y-2'>
                              <For each={project.technologies || []}>
                                {(tech, techIndex) => (
                                  <div class='flex space-x-2'>
                                    <input
                                      type='text'
                                      class='input input-bordered flex-1'
                                      placeholder='e.g., React, Node.js, MongoDB'
                                      value={tech}
                                      onInput={e =>
                                        updateProjectTechnology(
                                          index(),
                                          techIndex(),
                                          e.target.value
                                        )
                                      }
                                    />
                                    <button
                                      type='button'
                                      class='btn btn-ghost btn-sm text-error'
                                      onClick={() => removeProjectTechnology(index(), techIndex())}
                                    >
                                      ✕
                                    </button>
                                  </div>
                                )}
                              </For>
                              <button
                                type='button'
                                class='btn btn-ghost btn-sm w-full'
                                onClick={() => addProjectTechnology(index())}
                              >
                                ➕ Add Technology
                              </button>
                            </div>
                          </div>

                          {/* Key Achievements */}
                          <div class='mt-4'>
                            <label class='block text-sm font-medium mb-2'>Key Achievements</label>
                            <div class='space-y-2'>
                              <For each={project.achievements || []}>
                                {(achievement, achIndex) => (
                                  <div class='flex space-x-2'>
                                    <input
                                      type='text'
                                      class='input input-bordered flex-1'
                                      placeholder='Key outcome or impact of this project'
                                      value={achievement}
                                      onInput={e =>
                                        updateProjectAchievement(
                                          index(),
                                          achIndex(),
                                          e.target.value
                                        )
                                      }
                                    />
                                    <button
                                      type='button'
                                      class='btn btn-ghost btn-sm text-error'
                                      onClick={() => removeProjectAchievement(index(), achIndex())}
                                    >
                                      ✕
                                    </button>
                                  </div>
                                )}
                              </For>
                              <button
                                type='button'
                                class='btn btn-ghost btn-sm w-full'
                                onClick={() => addProjectAchievement(index())}
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
                  <Show when={(formData().projects || []).length === 0}>
                    <div class='text-center py-12 bg-base-100 rounded-lg border-2 border-dashed border-base-300'>
                      <div class='text-4xl mb-2'>🚀</div>
                      <h3 class='text-lg font-medium mb-2'>No projects added yet</h3>
                      <p class='text-base-content/70 mb-4'>
                        Showcase your projects to demonstrate your skills and experience
                      </p>
                      <button type='button' class='btn btn-primary' onClick={addProject}>
                        Add Your First Project
                      </button>
                    </div>
                  </Show>
                </div>
              </div>
            )}

            {/* Certifications Section */}
            {activeSection() === 'certifications' && (
              <div class='space-y-4'>
                <h3 class='text-xl font-semibold mb-4'>🏆 Certifications</h3>

                <div class='space-y-6'>
                  {/* Add New Certification Button */}
                  <div class='flex justify-between items-center'>
                    <p class='text-sm text-base-content/70'>
                      Add your professional certifications with expiry tracking.
                    </p>
                    <button type='button' class='btn btn-outline btn-sm' onClick={addCertification}>
                      ➕ Add Certification
                    </button>
                  </div>

                  {/* Certification Entries */}
                  <div class='space-y-6'>
                    <For each={formData().certifications}>
                      {(certification, index) => (
                        <div class='card bg-base-100 border border-base-300 p-6'>
                          {/* Certification Header */}
                          <div class='flex justify-between items-center mb-4'>
                            <div class='flex items-center space-x-3'>
                              <h4 class='text-lg font-medium'>Certification {index() + 1}</h4>
                              <div
                                class={`badge ${
                                  getCertificationStatus(certification) === 'Expired'
                                    ? 'badge-error'
                                    : getCertificationStatus(certification) === 'Expiring Soon'
                                    ? 'badge-warning'
                                    : 'badge-success'
                                }`}
                              >
                                {getCertificationStatus(certification)}
                              </div>
                            </div>
                            <div class='flex space-x-2'>
                              {/* Move Up Button */}
                              <Show when={index() > 0}>
                                <button
                                  type='button'
                                  class='btn btn-ghost btn-sm'
                                  onClick={() => moveCertificationUp(index())}
                                  title='Move up'
                                >
                                  ⬆️
                                </button>
                              </Show>

                              {/* Move Down Button */}
                              <Show when={index() < (formData().certifications || []).length - 1}>
                                <button
                                  type='button'
                                  class='btn btn-ghost btn-sm'
                                  onClick={() => moveCertificationDown(index())}
                                  title='Move down'
                                >
                                  ⬇️
                                </button>
                              </Show>

                              {/* Delete Button */}
                              <button
                                type='button'
                                class='btn btn-ghost btn-sm text-error'
                                onClick={() => removeCertification(index())}
                                title='Remove certification'
                              >
                                🗑️
                              </button>
                            </div>
                          </div>

                          {/* Certification Form Fields */}
                          <div class='grid grid-cols-1 md:grid-cols-2 gap-4'>
                            {/* Certification Name */}
                            <div>
                              <label class='block text-sm font-medium mb-2'>
                                Certification Name *
                              </label>
                              <input
                                type='text'
                                class='input input-bordered w-full'
                                placeholder='AWS Certified Solutions Architect'
                                value={certification.name}
                                onInput={e => updateCertification(index(), 'name', e.target.value)}
                                required
                              />
                            </div>

                            {/* Issuing Organization */}
                            <div>
                              <label class='block text-sm font-medium mb-2'>
                                Issuing Organization
                              </label>
                              <input
                                type='text'
                                class='input input-bordered w-full'
                                placeholder='Amazon Web Services'
                                value={certification.issuer || ''}
                                onInput={e =>
                                  updateCertification(index(), 'issuer', e.target.value)
                                }
                              />
                            </div>

                            {/* Date Earned */}
                            <div>
                              <label class='block text-sm font-medium mb-2'>Date Earned</label>
                              <input
                                type='date'
                                class='input input-bordered w-full'
                                value={certification.date_earned || ''}
                                onInput={e =>
                                  updateCertification(index(), 'date_earned', e.target.value)
                                }
                              />
                            </div>

                            {/* Expiry Date */}
                            <div>
                              <label class='block text-sm font-medium mb-2'>Expiry Date</label>
                              <input
                                type='date'
                                class='input input-bordered w-full'
                                value={certification.expiry_date || ''}
                                onInput={e =>
                                  updateCertification(index(), 'expiry_date', e.target.value)
                                }
                              />
                            </div>

                            {/* Credential ID */}
                            <div>
                              <label class='block text-sm font-medium mb-2'>Credential ID</label>
                              <input
                                type='text'
                                class='input input-bordered w-full'
                                placeholder='Certificate number or ID'
                                value={certification.credential_id || ''}
                                onInput={e =>
                                  updateCertification(index(), 'credential_id', e.target.value)
                                }
                              />
                            </div>

                            {/* Verification URL */}
                            <div>
                              <label class='block text-sm font-medium mb-2'>Verification URL</label>
                              <input
                                type='url'
                                class='input input-bordered w-full'
                                placeholder='https://verify.certification.com/...'
                                value={certification.verification_url || ''}
                                onInput={e =>
                                  updateCertification(index(), 'verification_url', e.target.value)
                                }
                              />
                            </div>
                          </div>
                        </div>
                      )}
                    </For>
                  </div>

                  {/* Empty State */}
                  <Show when={(formData().certifications || []).length === 0}>
                    <div class='text-center py-12 bg-base-100 rounded-lg border-2 border-dashed border-base-300'>
                      <div class='text-4xl mb-2'>🏆</div>
                      <h3 class='text-lg font-medium mb-2'>No certifications added yet</h3>
                      <p class='text-base-content/70 mb-4'>
                        Add your professional certifications to boost your credibility
                      </p>
                      <button type='button' class='btn btn-primary' onClick={addCertification}>
                        Add Your First Certification
                      </button>
                    </div>
                  </Show>

                  {/* Certifications Summary */}
                  <Show when={(formData().certifications || []).length > 0}>
                    <div class='bg-warning/10 border border-warning/20 rounded-lg p-4'>
                      <div class='flex items-start space-x-3'>
                        <div class='text-warning text-xl'>⚠️</div>
                        <div>
                          <h4 class='font-medium text-warning-content mb-2'>
                            Certification Status
                          </h4>
                          <p class='text-sm text-base-content/70'>
                            Total: {(formData().certifications || []).length} certifications
                          </p>
                          <div class='mt-2 text-xs text-base-content/60'>
                            <strong>Tip:</strong> Keep track of expiry dates and renew
                            certifications before they expire to maintain their value.
                          </div>
                        </div>
                      </div>
                    </div>
                  </Show>
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
