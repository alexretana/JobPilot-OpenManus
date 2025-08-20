import { Component, createSignal, createMemo, Show, For } from 'solid-js';
import { createStore } from 'solid-js/store';
import { skillBankApiService } from '../../../../../services/skillBankApi';
import type {
  SkillBankResponse,
  ProjectEntry,
  ProjectEntryRequest,
} from '../../../../../types/skillBank';

interface ProjectsSectionProps {
  skillBank: SkillBankResponse;
  onUpdate: () => void;
  loading: boolean;
}

interface ProjectFormData {
  name: string;
  url: string;
  github_url: string;
  start_date: string;
  end_date: string;
  default_description: string;
  default_achievements: string[];
  technologies: string[];
}

const skillBankApi = skillBankApiService;

const initialFormData: ProjectFormData = {
  name: '',
  url: '',
  github_url: '',
  start_date: '',
  end_date: '',
  default_description: '',
  default_achievements: [],
  technologies: [],
};

/**
 * Projects management section
 */
export const ProjectsSection: Component<ProjectsSectionProps> = props => {
  const [showAddForm, setShowAddForm] = createSignal(false);
  const [editingProject, setEditingProject] = createSignal<ProjectEntry | null>(null);
  const [formData, setFormData] = createStore<ProjectFormData>(initialFormData);
  const [saving, setSaving] = createSignal(false);
  // const [expandedProject, setExpandedProject] = createSignal<string | null>(null);

  const projects = () => props.skillBank?.projects || [];

  const sortedProjects = createMemo(() => {
    return [...projects()].sort((a, b) => {
      const aDate = a.start_date ? new Date(a.start_date).getTime() : 0;
      const bDate = b.start_date ? new Date(b.start_date).getTime() : 0;
      return bDate - aDate;
    });
  });

  const handleAddProject = () => {
    setFormData(initialFormData);
    setEditingProject(null);
    setShowAddForm(true);
  };

  const handleEditProject = (project: ProjectEntry) => {
    setFormData({
      name: project.name,
      url: project.url || '',
      github_url: project.github_url || '',
      start_date: project.start_date || '',
      end_date: project.end_date || '',
      default_description: project.default_description || '',
      default_achievements: [...project.default_achievements],
      technologies: [...project.technologies],
    });
    setEditingProject(project);
    setShowAddForm(true);
  };

  const handleCancelEdit = () => {
    setShowAddForm(false);
    setEditingProject(null);
    setFormData(initialFormData);
  };

  const handleFormSubmit = async (e: Event) => {
    e.preventDefault();
    if (!formData.name.trim() || !formData.start_date) return;

    setSaving(true);
    try {
      const projectRequest: ProjectEntryRequest = {
        name: formData.name.trim(),
        url: formData.url.trim() || null,
        github_url: formData.github_url.trim() || null,
        start_date: formData.start_date,
        end_date: formData.end_date || null,
        default_description: formData.default_description.trim() || null,
        default_achievements: formData.default_achievements.filter(a => a.trim()),
        technologies: formData.technologies.filter(t => t.trim()),
      };

      if (editingProject()) {
        await skillBankApi.updateProject(
          props.skillBank.user_id,
          editingProject()!.id,
          projectRequest
        );
      } else {
        await skillBankApi.addProject(props.skillBank.user_id, projectRequest);
      }

      props.onUpdate();
      handleCancelEdit();
    } catch (error) {
      console.error('Error saving project:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteProject = async (project: ProjectEntry) => {
    if (!confirm(`Are you sure you want to delete "${project.name}"?`)) return;

    setSaving(true);
    try {
      await skillBankApi.deleteProject(props.skillBank.user_id, project.id);
      props.onUpdate();
    } catch (error) {
      console.error('Error deleting project:', error);
    } finally {
      setSaving(false);
    }
  };

  // const toggleProjectExpansion = (projectId: string) => {
  //   setExpandedProject(expandedProject() === projectId ? null : projectId);
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
                d='M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10'
              ></path>
            </svg>
            Projects ({projects().length})
          </h2>
          <p class='text-base-content/70'>Showcase your projects and technical accomplishments.</p>
        </div>
        <button class='btn btn-primary gap-2' onClick={handleAddProject} disabled={saving()}>
          <svg class='w-4 h-4' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
            <path
              stroke-linecap='round'
              stroke-linejoin='round'
              stroke-width='2'
              d='M12 4v16m8-8H4'
            ></path>
          </svg>
          Add Project
        </button>
      </div>

      {/* Add/Edit Form Modal */}
      <Show when={showAddForm()}>
        <div class='modal modal-open'>
          <div class='modal-box w-11/12 max-w-4xl max-h-screen overflow-y-auto'>
            <h3 class='font-bold text-lg mb-4'>
              {editingProject() ? 'Edit Project' : 'Add Project'}
            </h3>

            <form onSubmit={handleFormSubmit} class='space-y-4'>
              {/* Basic Information */}
              <div class='grid grid-cols-1 md:grid-cols-2 gap-4'>
                <div class='form-control md:col-span-2'>
                  <label class='label'>
                    <span class='label-text'>Project Name *</span>
                  </label>
                  <input
                    type='text'
                    placeholder='e.g., My Awesome Project'
                    class='input input-bordered'
                    value={formData.name}
                    onInput={e => setFormData('name', e.currentTarget.value)}
                    required
                  />
                </div>

                <div class='form-control'>
                  <label class='label'>
                    <span class='label-text'>Project URL</span>
                  </label>
                  <input
                    type='url'
                    placeholder='https://my-project.com'
                    class='input input-bordered'
                    value={formData.url}
                    onInput={e => setFormData('url', e.currentTarget.value)}
                  />
                </div>

                <div class='form-control'>
                  <label class='label'>
                    <span class='label-text'>GitHub URL</span>
                  </label>
                  <input
                    type='url'
                    placeholder='https://github.com/user/repo'
                    class='input input-bordered'
                    value={formData.github_url}
                    onInput={e => setFormData('github_url', e.currentTarget.value)}
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
                  placeholder='Describe your project, its goals, and your role...'
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
                  disabled={saving() || !formData.name.trim() || !formData.start_date}
                >
                  <Show
                    when={saving()}
                    fallback={editingProject() ? 'Update Project' : 'Add Project'}
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

      {/* Projects List */}
      <Show
        when={projects().length > 0}
        fallback={
          <div class='text-center py-16'>
            <div class='text-6xl mb-4'>🚀</div>
            <h3 class='text-xl font-semibold mb-2'>No projects added yet</h3>
            <p class='text-base-content/70 mb-6'>
              Add your projects to showcase your skills and experience.
            </p>
            <button class='btn btn-primary' onClick={handleAddProject}>
              Add Your First Project
            </button>
          </div>
        }
      >
        <div class='space-y-4'>
          <For each={sortedProjects()}>
            {project => {
              // const isExpanded = () => expandedProject() === project.id;

              return (
                <div class='card bg-base-100 shadow-lg border border-base-300'>
                  <div class='card-body'>
                    <div class='flex items-start justify-between'>
                      <div class='flex-1 min-w-0'>
                        <h3 class='card-title text-lg'>{project.name}</h3>
                        <div class='flex flex-wrap items-center gap-2 mt-2 text-sm text-base-content/70'>
                          <div class='flex items-center gap-1'>
                            {formatDate(project.start_date || '')} -{' '}
                            {formatDate(project.end_date || '')}
                          </div>
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
                            <button onClick={() => handleEditProject(project)}>Edit</button>
                          </li>
                          <li>
                            <button class='text-error' onClick={() => handleDeleteProject(project)}>
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

export default ProjectsSection;
