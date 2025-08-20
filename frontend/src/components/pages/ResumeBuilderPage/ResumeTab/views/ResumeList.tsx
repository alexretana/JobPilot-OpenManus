import { Component, createSignal, onMount, For, Show } from 'solid-js';
import { ResumeService, ResumeData } from '../../../../../services/resumeService';

interface ResumeListProps {
  userId: string;
  onCreateNew: () => void;
  onEditResume: (resumeId: string) => void;
  onViewResume: (resumeId: string) => void;
}

const ResumeList: Component<ResumeListProps> = props => {
  const [resumes, setResumes] = createSignal<ResumeData[]>([]);
  const [loading, setLoading] = createSignal(true);
  const [error, setError] = createSignal<string | null>(null);
  const [deletingId, setDeletingId] = createSignal<string | null>(null);

  const loadResumes = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await ResumeService.getUserResumes(props.userId);
      setResumes(response.resumes || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load resumes');
      console.error('Failed to load resumes:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (resumeId: string, title: string) => {
    if (!confirm(`Are you sure you want to delete "${title}"? This action cannot be undone.`)) {
      return;
    }

    try {
      setDeletingId(resumeId);
      await ResumeService.deleteResume(resumeId, props.userId);
      // Remove from local state
      setResumes(prev => prev.filter(r => r.id !== resumeId));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete resume');
      console.error('Failed to delete resume:', err);
    } finally {
      setDeletingId(null);
    }
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString();
  };

  const getStatusBadgeClass = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'badge-success';
      case 'draft':
        return 'badge-warning';
      case 'in_progress':
        return 'badge-info';
      default:
        return 'badge-neutral';
    }
  };

  onMount(() => {
    loadResumes();
  });

  return (
    <div class='space-y-4'>
      {/* Header */}
      <div class='flex justify-between items-center'>
        <div>
          <h2 class='text-2xl font-bold'>📝 My Resumes</h2>
          <p class='text-base-content/70'>Manage your professional resumes</p>
        </div>
        <button class='btn btn-primary' onClick={props.onCreateNew}>
          ✨ Create New Resume
        </button>
      </div>

      {/* Loading State */}
      <Show when={loading()}>
        <div class='flex justify-center items-center py-8'>
          <span class='loading loading-spinner loading-lg'></span>
        </div>
      </Show>

      {/* Error State */}
      <Show when={error()}>
        <div class='alert alert-error'>
          <svg class='w-6 h-6' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
            <path
              stroke-linecap='round'
              stroke-linejoin='round'
              stroke-width='2'
              d='M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 15.5c-.77.833.192 2.5 1.732 2.5z'
            ></path>
          </svg>
          <span>{error()}</span>
          <div class='flex-none'>
            <button class='btn btn-sm btn-ghost' onClick={loadResumes}>
              Retry
            </button>
          </div>
        </div>
      </Show>

      {/* Empty State */}
      <Show when={!loading() && !error() && resumes().length === 0}>
        <div class='text-center py-12'>
          <div class='text-6xl mb-4'>📄</div>
          <h3 class='text-xl font-semibold mb-2'>No resumes yet</h3>
          <p class='text-base-content/70 mb-4'>
            Get started by creating your first professional resume
          </p>
          <button class='btn btn-primary btn-lg' onClick={props.onCreateNew}>
            Create Your First Resume
          </button>
        </div>
      </Show>

      {/* Resume Grid */}
      <Show when={!loading() && !error() && resumes().length > 0}>
        <div class='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4'>
          <For each={resumes()}>
            {resume => (
              <div class='card bg-base-100 shadow-md border'>
                <div class='card-body'>
                  <div class='flex justify-between items-start'>
                    <h3 class='card-title text-lg'>{resume.title}</h3>
                    <div class='dropdown dropdown-end'>
                      <div tabindex='0' role='button' class='btn btn-ghost btn-sm btn-circle'>
                        <svg class='w-4 h-4' fill='currentColor' viewBox='0 0 24 24'>
                          <path d='M12 8c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm0 2c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z' />
                        </svg>
                      </div>
                      <ul
                        tabindex='0'
                        class='dropdown-content menu bg-base-100 rounded-box z-[1] w-32 p-2 shadow'
                      >
                        <li>
                          <a onClick={() => props.onEditResume(resume.id)}>✏️ Edit</a>
                        </li>
                        <li>
                          <a onClick={() => props.onViewResume(resume.id)}>👁️ View</a>
                        </li>
                        <li>
                          <a>📄 Duplicate</a>
                        </li>
                        <li class='border-t pt-1 mt-1'>
                          <a
                            class='text-error'
                            onClick={() => handleDelete(resume.id, resume.title)}
                          >
                            {deletingId() === resume.id ? '⏳ Deleting...' : '🗑️ Delete'}
                          </a>
                        </li>
                      </ul>
                    </div>
                  </div>

                  {/* Status Badge */}
                  <div class='flex justify-between items-center mt-2'>
                    <span class={`badge ${getStatusBadgeClass(resume.status)}`}>
                      {resume.status.replace('_', ' ')}
                    </span>
                    <span class='text-xs text-base-content/50'>v{resume.version}</span>
                  </div>

                  {/* Completeness Score */}
                  <Show when={resume.completeness_score !== undefined}>
                    <div class='w-full'>
                      <div class='flex justify-between text-xs'>
                        <span>Completeness</span>
                        <span>{Math.round((resume.completeness_score || 0) * 100)}%</span>
                      </div>
                      <progress
                        class='progress progress-primary w-full'
                        value={(resume.completeness_score || 0) * 100}
                        max='100'
                      ></progress>
                    </div>
                  </Show>

                  {/* Dates */}
                  <div class='text-xs text-base-content/50 space-y-1'>
                    <div>Created: {formatDate(resume.created_at)}</div>
                    <div>Updated: {formatDate(resume.updated_at)}</div>
                  </div>

                  {/* Action Buttons */}
                  <div class='card-actions justify-end mt-4'>
                    <button
                      class='btn btn-sm btn-outline'
                      onClick={() => props.onViewResume(resume.id)}
                    >
                      View
                    </button>
                    <button
                      class='btn btn-sm btn-primary'
                      onClick={() => props.onEditResume(resume.id)}
                    >
                      Edit
                    </button>
                  </div>
                </div>
              </div>
            )}
          </For>
        </div>
      </Show>
    </div>
  );
};

export default ResumeList;
