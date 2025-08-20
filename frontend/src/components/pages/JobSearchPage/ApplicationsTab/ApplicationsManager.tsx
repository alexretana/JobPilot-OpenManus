import { createSignal, createResource, For, Show } from 'solid-js';
import { createStore } from 'solid-js/store';

interface Application {
  id: string;
  job_id: string;
  user_profile_id: string;
  status:
    | 'not_applied'
    | 'applied'
    | 'interview_scheduled'
    | 'interview_completed'
    | 'offer_received'
    | 'offer_accepted'
    | 'offer_declined'
    | 'rejected'
    | 'withdrawn';
  applied_date?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
  job_title?: string;
  company?: string;
}

interface CreateApplicationRequest {
  job_id: string;
  status: Application['status'];
  notes?: string;
}

const ApplicationsManager = () => {
  const [selectedStatus, setSelectedStatus] = createSignal<Application['status'] | 'all'>('all');
  const [showCreateModal, setShowCreateModal] = createSignal(false);
  const [editingApplication, setEditingApplication] = createSignal<Application | null>(null);

  // Store for the create/edit form
  const [applicationForm, setApplicationForm] = createStore<CreateApplicationRequest>({
    job_id: '',
    status: 'not_applied',
    notes: '',
  });

  // Fetch applications
  const [applications, { refetch: refetchApplications }] = createResource(
    () => selectedStatus(),
    async status => {
      const params = new URLSearchParams();
      if (status !== 'all') {
        params.set('status', status);
      }
      const response = await fetch(`/api/applications/?${params.toString()}`);
      const data = await response.json();
      return data.applications as Application[];
    }
  );

  // Get available jobs for creating applications
  const [availableJobs] = createResource(async () => {
    const response = await fetch('/api/jobs/recent?limit=50');
    const data = await response.json();
    return data.jobs;
  });

  const statusOptions: Array<{ value: Application['status'] | 'all'; label: string }> = [
    { value: 'all', label: 'All Applications' },
    { value: 'not_applied', label: 'Not Applied' },
    { value: 'applied', label: 'Applied' },
    { value: 'interview_scheduled', label: 'Interview Scheduled' },
    { value: 'interview_completed', label: 'Interview Completed' },
    { value: 'offer_received', label: 'Offer Received' },
    { value: 'offer_accepted', label: 'Offer Accepted' },
    { value: 'offer_declined', label: 'Offer Declined' },
    { value: 'rejected', label: 'Rejected' },
    { value: 'withdrawn', label: 'Withdrawn' },
  ];

  const getStatusBadgeClass = (status: Application['status']) => {
    const baseClass = 'badge badge-sm';
    switch (status) {
      case 'not_applied':
        return `${baseClass} badge-neutral`;
      case 'applied':
        return `${baseClass} badge-info`;
      case 'interview_scheduled':
        return `${baseClass} badge-warning`;
      case 'interview_completed':
        return `${baseClass} badge-warning`;
      case 'offer_received':
        return `${baseClass} badge-success`;
      case 'offer_accepted':
        return `${baseClass} badge-success`;
      case 'offer_declined':
        return `${baseClass} badge-error`;
      case 'rejected':
        return `${baseClass} badge-error`;
      case 'withdrawn':
        return `${baseClass} badge-ghost`;
      default:
        return `${baseClass} badge-neutral`;
    }
  };

  const handleCreateApplication = async () => {
    try {
      const response = await fetch('/api/applications/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(applicationForm),
      });

      if (!response.ok) {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
        return;
      }

      // Reset form and close modal
      setApplicationForm({
        job_id: '',
        status: 'not_applied',
        notes: '',
      });
      setShowCreateModal(false);

      // Refresh applications
      refetchApplications();
    } catch (error) {
      alert(`Error creating application: ${error}`);
    }
  };

  const handleUpdateApplication = async (applicationId: string, updates: Partial<Application>) => {
    try {
      const params = new URLSearchParams();
      if (updates.status) params.set('status', updates.status);
      if (updates.notes) params.set('notes', updates.notes);

      const response = await fetch(`/api/applications/${applicationId}?${params.toString()}`, {
        method: 'PUT',
      });

      if (!response.ok) {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
        return;
      }

      // Refresh applications
      refetchApplications();
      setEditingApplication(null);
    } catch (error) {
      alert(`Error updating application: ${error}`);
    }
  };

  const handleDeleteApplication = async (applicationId: string) => {
    if (!confirm('Are you sure you want to delete this application?')) {
      return;
    }

    try {
      const response = await fetch(`/api/applications/${applicationId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
        return;
      }

      // Refresh applications
      refetchApplications();
    } catch (error) {
      alert(`Error deleting application: ${error}`);
    }
  };

  return (
    <div class='container mx-auto p-4'>
      <div class='flex flex-col gap-4'>
        {/* Header */}
        <div class='flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between'>
          <h1 class='text-3xl font-bold'>Job Applications</h1>
          <button class='btn btn-primary' onClick={() => setShowCreateModal(true)}>
            + New Application
          </button>
        </div>

        {/* Filters */}
        <div class='flex flex-wrap gap-4 items-center'>
          <div class='form-control'>
            <label class='label'>
              <span class='label-text'>Filter by Status:</span>
            </label>
            <select
              class='select select-bordered'
              value={selectedStatus()}
              onChange={e => setSelectedStatus(e.target.value as Application['status'] | 'all')}
            >
              <For each={statusOptions}>
                {option => <option value={option.value}>{option.label}</option>}
              </For>
            </select>
          </div>

          <div class='stats stats-horizontal shadow'>
            <div class='stat'>
              <div class='stat-title'>Total Applications</div>
              <div class='stat-value text-2xl'>{applications()?.length || 0}</div>
            </div>
          </div>
        </div>

        {/* Applications List */}
        <div class='grid gap-4'>
          <Show
            when={!applications.loading}
            fallback={
              <div class='flex justify-center p-8'>
                <span class='loading loading-spinner loading-lg'></span>
              </div>
            }
          >
            <Show
              when={applications() && applications()!.length > 0}
              fallback={
                <div class='card bg-base-100 shadow-xl'>
                  <div class='card-body text-center'>
                    <h2 class='card-title justify-center'>No Applications Found</h2>
                    <p>You haven't created any job applications yet.</p>
                    <div class='card-actions justify-center'>
                      <button class='btn btn-primary' onClick={() => setShowCreateModal(true)}>
                        Create Your First Application
                      </button>
                    </div>
                  </div>
                </div>
              }
            >
              <For each={applications()}>
                {application => (
                  <div class='card bg-base-100 shadow-xl'>
                    <div class='card-body'>
                      <div class='flex flex-col sm:flex-row justify-between items-start gap-4'>
                        <div class='flex-1'>
                          <h2 class='card-title'>
                            {application.job_title || 'Unknown Position'}
                            <div class={getStatusBadgeClass(application.status)}>
                              {application.status.replace('_', ' ')}
                            </div>
                          </h2>
                          <p class='text-base-content/60'>
                            at {application.company || 'Unknown Company'}
                          </p>
                          <Show when={application.applied_date}>
                            <p class='text-sm text-base-content/40'>
                              Applied: {new Date(application.applied_date!).toLocaleDateString()}
                            </p>
                          </Show>
                          <Show when={application.notes}>
                            <div class='mt-2'>
                              <p class='text-sm font-medium'>Notes:</p>
                              <p class='text-sm text-base-content/60'>{application.notes}</p>
                            </div>
                          </Show>
                        </div>

                        <div class='flex gap-2'>
                          <button
                            class='btn btn-sm btn-ghost'
                            onClick={() => setEditingApplication(application)}
                          >
                            Edit
                          </button>
                          <button
                            class='btn btn-sm btn-error btn-outline'
                            onClick={() => handleDeleteApplication(application.id)}
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </For>
            </Show>
          </Show>
        </div>
      </div>

      {/* Create Application Modal */}
      <Show when={showCreateModal()}>
        <div class='modal modal-open'>
          <div class='modal-box'>
            <h3 class='font-bold text-lg'>Create New Application</h3>

            <div class='form-control w-full max-w-xs mt-4'>
              <label class='label'>
                <span class='label-text'>Select Job</span>
              </label>
              <select
                class='select select-bordered'
                value={applicationForm.job_id}
                onChange={e => setApplicationForm('job_id', e.target.value)}
              >
                <option value=''>Choose a job...</option>
                <For each={availableJobs()}>
                  {(job: any) => (
                    <option value={job.id}>
                      {job.title} at {job.company}
                    </option>
                  )}
                </For>
              </select>
            </div>

            <div class='form-control w-full max-w-xs mt-4'>
              <label class='label'>
                <span class='label-text'>Status</span>
              </label>
              <select
                class='select select-bordered'
                value={applicationForm.status}
                onChange={e =>
                  setApplicationForm('status', e.target.value as Application['status'])
                }
              >
                <For each={statusOptions.slice(1)}>
                  {option => <option value={option.value}>{option.label}</option>}
                </For>
              </select>
            </div>

            <div class='form-control w-full mt-4'>
              <label class='label'>
                <span class='label-text'>Notes (Optional)</span>
              </label>
              <textarea
                class='textarea textarea-bordered h-24'
                placeholder='Add notes about this application...'
                value={applicationForm.notes}
                onInput={e => setApplicationForm('notes', e.target.value)}
              />
            </div>

            <div class='modal-action'>
              <button class='btn' onClick={() => setShowCreateModal(false)}>
                Cancel
              </button>
              <button
                class='btn btn-primary'
                disabled={!applicationForm.job_id}
                onClick={handleCreateApplication}
              >
                Create Application
              </button>
            </div>
          </div>
        </div>
      </Show>

      {/* Edit Application Modal */}
      <Show when={editingApplication()}>
        <div class='modal modal-open'>
          <div class='modal-box'>
            <h3 class='font-bold text-lg'>Edit Application</h3>

            <div class='mt-4'>
              <h4 class='font-medium'>{editingApplication()?.job_title}</h4>
              <p class='text-sm text-base-content/60'>at {editingApplication()?.company}</p>
            </div>

            <div class='form-control w-full max-w-xs mt-4'>
              <label class='label'>
                <span class='label-text'>Status</span>
              </label>
              <select
                class='select select-bordered'
                value={editingApplication()?.status}
                onChange={e => {
                  const app = editingApplication();
                  if (app) {
                    handleUpdateApplication(app.id, {
                      status: e.target.value as Application['status'],
                    });
                  }
                }}
              >
                <For each={statusOptions.slice(1)}>
                  {option => <option value={option.value}>{option.label}</option>}
                </For>
              </select>
            </div>

            <div class='form-control w-full mt-4'>
              <label class='label'>
                <span class='label-text'>Notes</span>
              </label>
              <textarea
                class='textarea textarea-bordered h-24'
                placeholder='Add notes about this application...'
                value={editingApplication()?.notes || ''}
                onBlur={e => {
                  const app = editingApplication();
                  if (app) {
                    handleUpdateApplication(app.id, { notes: e.target.value });
                  }
                }}
              />
            </div>

            <div class='modal-action'>
              <button class='btn' onClick={() => setEditingApplication(null)}>
                Close
              </button>
            </div>
          </div>
        </div>
      </Show>
    </div>
  );
};

export default ApplicationsManager;
