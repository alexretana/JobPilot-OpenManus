import { createSignal, createResource, For, Show } from 'solid-js';
import { createStore } from 'solid-js/store';

interface Lead {
  id: string;
  user_profile_id: string;
  name: string;
  title?: string;
  company?: string;
  email?: string;
  phone?: string;
  linkedin_url?: string;
  lead_type: 'recruiter' | 'hiring_manager' | 'employee' | 'referral' | 'networking' | 'other';
  status:
    | 'new'
    | 'contacted'
    | 'responded'
    | 'meeting_scheduled'
    | 'follow_up_needed'
    | 'closed_won'
    | 'closed_lost';
  source?: string;
  notes?: string;
  last_contacted?: string;
  follow_up_date?: string;
  created_at: string;
  updated_at: string;
}

interface CreateLeadRequest {
  name: string;
  title?: string;
  company?: string;
  email?: string;
  phone?: string;
  linkedin_url?: string;
  lead_type: Lead['lead_type'];
  status: Lead['status'];
  source?: string;
  notes?: string;
  follow_up_date?: string;
}

interface LeadStats {
  total_leads: number;
  status_breakdown: Record<string, number>;
  type_breakdown: Record<string, number>;
  follow_ups_due: number;
}

const LeadsManager = () => {
  const [selectedStatus, setSelectedStatus] = createSignal<Lead['status'] | 'all'>('all');
  const [selectedType, setSelectedType] = createSignal<Lead['lead_type'] | 'all'>('all');
  const [showCreateModal, setShowCreateModal] = createSignal(false);
  const [editingLead, setEditingLead] = createSignal<Lead | null>(null);
  const [showStatsModal, setShowStatsModal] = createSignal(false);

  // Store for the create/edit form
  const [leadForm, setLeadForm] = createStore<CreateLeadRequest>({
    name: '',
    title: '',
    company: '',
    email: '',
    phone: '',
    linkedin_url: '',
    lead_type: 'other',
    status: 'new',
    source: '',
    notes: '',
    follow_up_date: '',
  });

  // Fetch leads
  const [leads, { refetch: refetchLeads }] = createResource(
    () => ({ status: selectedStatus(), type: selectedType() }),
    async filters => {
      const params = new URLSearchParams();
      if (filters.status !== 'all') {
        params.set('status', filters.status);
      }
      if (filters.type !== 'all') {
        params.set('lead_type', filters.type);
      }
      const response = await fetch(`/api/leads/?${params.toString()}`);
      const data = await response.json();
      return data.leads as Lead[];
    }
  );

  // Fetch lead statistics
  const [stats, { refetch: refetchStats }] = createResource(async () => {
    const response = await fetch('/api/leads/stats/summary');
    const data = await response.json();
    return data as LeadStats;
  });

  const statusOptions: Array<{ value: Lead['status'] | 'all'; label: string }> = [
    { value: 'all', label: 'All Statuses' },
    { value: 'new', label: 'New' },
    { value: 'contacted', label: 'Contacted' },
    { value: 'responded', label: 'Responded' },
    { value: 'meeting_scheduled', label: 'Meeting Scheduled' },
    { value: 'follow_up_needed', label: 'Follow-up Needed' },
    { value: 'closed_won', label: 'Closed Won' },
    { value: 'closed_lost', label: 'Closed Lost' },
  ];

  const typeOptions: Array<{ value: Lead['lead_type'] | 'all'; label: string }> = [
    { value: 'all', label: 'All Types' },
    { value: 'recruiter', label: 'Recruiter' },
    { value: 'hiring_manager', label: 'Hiring Manager' },
    { value: 'employee', label: 'Employee' },
    { value: 'referral', label: 'Referral' },
    { value: 'networking', label: 'Networking' },
    { value: 'other', label: 'Other' },
  ];

  const getStatusBadgeClass = (status: Lead['status']) => {
    const baseClass = 'badge badge-sm';
    switch (status) {
      case 'new':
        return `${baseClass} badge-neutral`;
      case 'contacted':
        return `${baseClass} badge-info`;
      case 'responded':
        return `${baseClass} badge-success`;
      case 'meeting_scheduled':
        return `${baseClass} badge-warning`;
      case 'follow_up_needed':
        return `${baseClass} badge-accent`;
      case 'closed_won':
        return `${baseClass} badge-success`;
      case 'closed_lost':
        return `${baseClass} badge-error`;
      default:
        return `${baseClass} badge-neutral`;
    }
  };

  const getTypeBadgeClass = (type: Lead['lead_type']) => {
    const baseClass = 'badge badge-outline badge-sm';
    switch (type) {
      case 'recruiter':
        return `${baseClass} badge-primary`;
      case 'hiring_manager':
        return `${baseClass} badge-secondary`;
      case 'employee':
        return `${baseClass} badge-accent`;
      case 'referral':
        return `${baseClass} badge-success`;
      case 'networking':
        return `${baseClass} badge-info`;
      default:
        return `${baseClass} badge-ghost`;
    }
  };

  const resetForm = () => {
    setLeadForm({
      name: '',
      title: '',
      company: '',
      email: '',
      phone: '',
      linkedin_url: '',
      lead_type: 'other',
      status: 'new',
      source: '',
      notes: '',
      follow_up_date: '',
    });
  };

  const handleCreateLead = async () => {
    try {
      // Prepare the request body, filtering out empty strings
      const requestBody = {
        ...leadForm,
        title: leadForm.title || undefined,
        company: leadForm.company || undefined,
        email: leadForm.email || undefined,
        phone: leadForm.phone || undefined,
        linkedin_url: leadForm.linkedin_url || undefined,
        source: leadForm.source || undefined,
        notes: leadForm.notes || undefined,
        follow_up_date: leadForm.follow_up_date || undefined,
      };

      const response = await fetch('/api/leads/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
        return;
      }

      // Reset form and close modal
      resetForm();
      setShowCreateModal(false);

      // Refresh leads and stats
      refetchLeads();
      refetchStats();
    } catch (error) {
      alert(`Error creating lead: ${error}`);
    }
  };

  const handleUpdateLead = async (leadId: string, updates: Partial<Lead>) => {
    try {
      const response = await fetch(`/api/leads/${leadId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updates),
      });

      if (!response.ok) {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
        return;
      }

      // Refresh leads and stats
      refetchLeads();
      refetchStats();
      setEditingLead(null);
    } catch (error) {
      alert(`Error updating lead: ${error}`);
    }
  };

  const handleDeleteLead = async (leadId: string) => {
    if (!confirm('Are you sure you want to delete this lead?')) {
      return;
    }

    try {
      const response = await fetch(`/api/leads/${leadId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const error = await response.json();
        alert(`Error: ${error.detail}`);
        return;
      }

      // Refresh leads and stats
      refetchLeads();
      refetchStats();
    } catch (error) {
      alert(`Error deleting lead: ${error}`);
    }
  };

  const formatDate = (dateString: string | undefined) => {
    if (!dateString) return null;
    return new Date(dateString).toLocaleDateString();
  };

  const isFollowUpOverdue = (lead: Lead) => {
    if (!lead.follow_up_date) return false;
    return new Date(lead.follow_up_date) < new Date();
  };

  return (
    <div class='container mx-auto p-4'>
      <div class='flex flex-col gap-4'>
        {/* Header */}
        <div class='flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between'>
          <h1 class='text-3xl font-bold'>Lead Management</h1>
          <div class='flex gap-2'>
            <button class='btn btn-outline btn-info' onClick={() => setShowStatsModal(true)}>
              📊 Statistics
            </button>
            <button class='btn btn-primary' onClick={() => setShowCreateModal(true)}>
              + New Lead
            </button>
          </div>
        </div>

        {/* Quick Stats */}
        <div class='stats stats-horizontal shadow'>
          <div class='stat'>
            <div class='stat-title'>Total Leads</div>
            <div class='stat-value text-2xl'>{stats()?.total_leads || 0}</div>
          </div>
          <div class='stat'>
            <div class='stat-title'>Follow-ups Due</div>
            <div class='stat-value text-xl text-warning'>{stats()?.follow_ups_due || 0}</div>
          </div>
          <div class='stat'>
            <div class='stat-title'>Response Rate</div>
            <div class='stat-value text-lg'>
              {stats()
                ? Math.round(
                    ((stats()!.status_breakdown.responded || 0) /
                      Math.max(stats()!.total_leads, 1)) *
                      100
                  )
                : 0}
              %
            </div>
          </div>
        </div>

        {/* Filters */}
        <div class='flex flex-wrap gap-4 items-center'>
          <div class='form-control'>
            <label class='label'>
              <span class='label-text'>Filter by Status:</span>
            </label>
            <select
              class='select select-bordered select-sm'
              value={selectedStatus()}
              onChange={e => setSelectedStatus(e.target.value as Lead['status'] | 'all')}
            >
              <For each={statusOptions}>
                {option => <option value={option.value}>{option.label}</option>}
              </For>
            </select>
          </div>

          <div class='form-control'>
            <label class='label'>
              <span class='label-text'>Filter by Type:</span>
            </label>
            <select
              class='select select-bordered select-sm'
              value={selectedType()}
              onChange={e => setSelectedType(e.target.value as Lead['lead_type'] | 'all')}
            >
              <For each={typeOptions}>
                {option => <option value={option.value}>{option.label}</option>}
              </For>
            </select>
          </div>
        </div>

        {/* Leads List */}
        <div class='grid gap-4'>
          <Show
            when={!leads.loading}
            fallback={
              <div class='flex justify-center p-8'>
                <span class='loading loading-spinner loading-lg'></span>
              </div>
            }
          >
            <Show
              when={leads() && leads()!.length > 0}
              fallback={
                <div class='card bg-base-100 shadow-xl'>
                  <div class='card-body text-center'>
                    <h2 class='card-title justify-center'>No Leads Found</h2>
                    <p>You haven't added any leads yet. Start building your network!</p>
                    <div class='card-actions justify-center'>
                      <button class='btn btn-primary' onClick={() => setShowCreateModal(true)}>
                        Add Your First Lead
                      </button>
                    </div>
                  </div>
                </div>
              }
            >
              <For each={leads()}>
                {lead => (
                  <div
                    class={`card bg-base-100 shadow-xl ${
                      isFollowUpOverdue(lead) ? 'ring-2 ring-warning' : ''
                    }`}
                  >
                    <div class='card-body'>
                      <div class='flex flex-col lg:flex-row justify-between items-start gap-4'>
                        <div class='flex-1'>
                          <div class='flex flex-wrap items-center gap-2 mb-2'>
                            <h2 class='card-title text-lg'>{lead.name}</h2>
                            <div class={getStatusBadgeClass(lead.status)}>
                              {lead.status.replace('_', ' ')}
                            </div>
                            <div class={getTypeBadgeClass(lead.lead_type)}>
                              {lead.lead_type.replace('_', ' ')}
                            </div>
                            {isFollowUpOverdue(lead) && (
                              <div class='badge badge-warning badge-sm'>⚠️ Overdue</div>
                            )}
                          </div>

                          {lead.title && (
                            <p class='text-base-content/80 font-medium'>{lead.title}</p>
                          )}
                          {lead.company && <p class='text-base-content/60'>at {lead.company}</p>}

                          <div class='flex flex-wrap gap-4 mt-3 text-sm'>
                            {lead.email && (
                              <a href={`mailto:${lead.email}`} class='link link-info'>
                                📧 {lead.email}
                              </a>
                            )}
                            {lead.phone && (
                              <a href={`tel:${lead.phone}`} class='link link-info'>
                                📞 {lead.phone}
                              </a>
                            )}
                            {lead.linkedin_url && (
                              <a
                                href={lead.linkedin_url}
                                target='_blank'
                                rel='noopener noreferrer'
                                class='link link-info'
                              >
                                💼 LinkedIn
                              </a>
                            )}
                          </div>

                          {lead.source && (
                            <div class='mt-2'>
                              <span class='text-sm text-base-content/40'>
                                Source: {lead.source}
                              </span>
                            </div>
                          )}

                          {lead.follow_up_date && (
                            <div class='mt-2'>
                              <span class='text-sm text-base-content/40'>
                                Follow-up: {formatDate(lead.follow_up_date)}
                                {isFollowUpOverdue(lead) && (
                                  <span class='text-warning ml-1'>⚠️</span>
                                )}
                              </span>
                            </div>
                          )}

                          {lead.last_contacted && (
                            <div class='mt-1'>
                              <span class='text-sm text-base-content/40'>
                                Last contacted: {formatDate(lead.last_contacted)}
                              </span>
                            </div>
                          )}

                          {lead.notes && (
                            <div class='mt-3'>
                              <p class='text-sm font-medium'>Notes:</p>
                              <p class='text-sm text-base-content/60 whitespace-pre-wrap'>
                                {lead.notes}
                              </p>
                            </div>
                          )}
                        </div>

                        <div class='flex gap-2'>
                          <button class='btn btn-sm btn-ghost' onClick={() => setEditingLead(lead)}>
                            Edit
                          </button>
                          <button
                            class='btn btn-sm btn-error btn-outline'
                            onClick={() => handleDeleteLead(lead.id)}
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

      {/* Create Lead Modal */}
      <Show when={showCreateModal()}>
        <div class='modal modal-open'>
          <div class='modal-box max-w-2xl'>
            <h3 class='font-bold text-lg'>Add New Lead</h3>

            <div class='grid grid-cols-1 md:grid-cols-2 gap-4 mt-4'>
              <div class='form-control'>
                <label class='label'>
                  <span class='label-text'>Name *</span>
                </label>
                <input
                  type='text'
                  class='input input-bordered'
                  placeholder='Full name'
                  value={leadForm.name}
                  onInput={e => setLeadForm('name', e.target.value)}
                />
              </div>

              <div class='form-control'>
                <label class='label'>
                  <span class='label-text'>Job Title</span>
                </label>
                <input
                  type='text'
                  class='input input-bordered'
                  placeholder='e.g., Senior Software Engineer'
                  value={leadForm.title}
                  onInput={e => setLeadForm('title', e.target.value)}
                />
              </div>

              <div class='form-control'>
                <label class='label'>
                  <span class='label-text'>Company</span>
                </label>
                <input
                  type='text'
                  class='input input-bordered'
                  placeholder='Company name'
                  value={leadForm.company}
                  onInput={e => setLeadForm('company', e.target.value)}
                />
              </div>

              <div class='form-control'>
                <label class='label'>
                  <span class='label-text'>Email</span>
                </label>
                <input
                  type='email'
                  class='input input-bordered'
                  placeholder='email@company.com'
                  value={leadForm.email}
                  onInput={e => setLeadForm('email', e.target.value)}
                />
              </div>

              <div class='form-control'>
                <label class='label'>
                  <span class='label-text'>Phone</span>
                </label>
                <input
                  type='tel'
                  class='input input-bordered'
                  placeholder='+1 (555) 123-4567'
                  value={leadForm.phone}
                  onInput={e => setLeadForm('phone', e.target.value)}
                />
              </div>

              <div class='form-control'>
                <label class='label'>
                  <span class='label-text'>LinkedIn URL</span>
                </label>
                <input
                  type='url'
                  class='input input-bordered'
                  placeholder='https://linkedin.com/in/...'
                  value={leadForm.linkedin_url}
                  onInput={e => setLeadForm('linkedin_url', e.target.value)}
                />
              </div>

              <div class='form-control'>
                <label class='label'>
                  <span class='label-text'>Lead Type</span>
                </label>
                <select
                  class='select select-bordered'
                  value={leadForm.lead_type}
                  onChange={e => setLeadForm('lead_type', e.target.value as Lead['lead_type'])}
                >
                  <For each={typeOptions.slice(1)}>
                    {option => <option value={option.value}>{option.label}</option>}
                  </For>
                </select>
              </div>

              <div class='form-control'>
                <label class='label'>
                  <span class='label-text'>Status</span>
                </label>
                <select
                  class='select select-bordered'
                  value={leadForm.status}
                  onChange={e => setLeadForm('status', e.target.value as Lead['status'])}
                >
                  <For each={statusOptions.slice(1)}>
                    {option => <option value={option.value}>{option.label}</option>}
                  </For>
                </select>
              </div>

              <div class='form-control'>
                <label class='label'>
                  <span class='label-text'>Source</span>
                </label>
                <input
                  type='text'
                  class='input input-bordered'
                  placeholder='e.g., LinkedIn, Networking Event'
                  value={leadForm.source}
                  onInput={e => setLeadForm('source', e.target.value)}
                />
              </div>

              <div class='form-control'>
                <label class='label'>
                  <span class='label-text'>Follow-up Date</span>
                </label>
                <input
                  type='date'
                  class='input input-bordered'
                  value={leadForm.follow_up_date}
                  onInput={e => setLeadForm('follow_up_date', e.target.value)}
                />
              </div>
            </div>

            <div class='form-control mt-4'>
              <label class='label'>
                <span class='label-text'>Notes</span>
              </label>
              <textarea
                class='textarea textarea-bordered h-24'
                placeholder='Add notes about this lead...'
                value={leadForm.notes}
                onInput={e => setLeadForm('notes', e.target.value)}
              />
            </div>

            <div class='modal-action'>
              <button
                class='btn'
                onClick={() => {
                  setShowCreateModal(false);
                  resetForm();
                }}
              >
                Cancel
              </button>
              <button class='btn btn-primary' disabled={!leadForm.name} onClick={handleCreateLead}>
                Add Lead
              </button>
            </div>
          </div>
        </div>
      </Show>

      {/* Edit Lead Modal */}
      <Show when={editingLead()}>
        <div class='modal modal-open'>
          <div class='modal-box max-w-2xl'>
            <h3 class='font-bold text-lg'>Edit Lead</h3>

            <div class='mt-4'>
              <h4 class='font-medium text-lg'>{editingLead()?.name}</h4>
              {editingLead()?.company && (
                <p class='text-sm text-base-content/60'>at {editingLead()?.company}</p>
              )}
            </div>

            <div class='grid grid-cols-1 md:grid-cols-2 gap-4 mt-6'>
              <div class='form-control'>
                <label class='label'>
                  <span class='label-text'>Lead Type</span>
                </label>
                <select
                  class='select select-bordered'
                  value={editingLead()?.lead_type}
                  onChange={e => {
                    const lead = editingLead();
                    if (lead) {
                      handleUpdateLead(lead.id, { lead_type: e.target.value as Lead['lead_type'] });
                    }
                  }}
                >
                  <For each={typeOptions.slice(1)}>
                    {option => <option value={option.value}>{option.label}</option>}
                  </For>
                </select>
              </div>

              <div class='form-control'>
                <label class='label'>
                  <span class='label-text'>Status</span>
                </label>
                <select
                  class='select select-bordered'
                  value={editingLead()?.status}
                  onChange={e => {
                    const lead = editingLead();
                    if (lead) {
                      handleUpdateLead(lead.id, { status: e.target.value as Lead['status'] });
                    }
                  }}
                >
                  <For each={statusOptions.slice(1)}>
                    {option => <option value={option.value}>{option.label}</option>}
                  </For>
                </select>
              </div>

              <div class='form-control'>
                <label class='label'>
                  <span class='label-text'>Follow-up Date</span>
                </label>
                <input
                  type='date'
                  class='input input-bordered'
                  value={editingLead()?.follow_up_date?.split('T')[0] || ''}
                  onBlur={e => {
                    const lead = editingLead();
                    if (lead) {
                      handleUpdateLead(lead.id, { follow_up_date: e.target.value || undefined });
                    }
                  }}
                />
              </div>

              <div class='form-control'>
                <label class='label'>
                  <span class='label-text'>Source</span>
                </label>
                <input
                  type='text'
                  class='input input-bordered'
                  placeholder='e.g., LinkedIn, Networking Event'
                  value={editingLead()?.source || ''}
                  onBlur={e => {
                    const lead = editingLead();
                    if (lead) {
                      handleUpdateLead(lead.id, { source: e.target.value || undefined });
                    }
                  }}
                />
              </div>
            </div>

            <div class='form-control mt-4'>
              <label class='label'>
                <span class='label-text'>Notes</span>
              </label>
              <textarea
                class='textarea textarea-bordered h-24'
                placeholder='Add notes about this lead...'
                value={editingLead()?.notes || ''}
                onBlur={e => {
                  const lead = editingLead();
                  if (lead) {
                    handleUpdateLead(lead.id, { notes: e.target.value || undefined });
                  }
                }}
              />
            </div>

            <div class='modal-action'>
              <button class='btn' onClick={() => setEditingLead(null)}>
                Close
              </button>
            </div>
          </div>
        </div>
      </Show>

      {/* Statistics Modal */}
      <Show when={showStatsModal()}>
        <div class='modal modal-open'>
          <div class='modal-box'>
            <h3 class='font-bold text-lg'>Lead Statistics</h3>

            <Show when={stats()}>
              <div class='grid gap-4 mt-4'>
                <div class='stats shadow'>
                  <div class='stat'>
                    <div class='stat-title'>Total Leads</div>
                    <div class='stat-value'>{stats()!.total_leads}</div>
                  </div>
                </div>

                <div>
                  <h4 class='font-semibold mb-2'>Status Breakdown</h4>
                  <div class='grid grid-cols-2 gap-2'>
                    <For each={Object.entries(stats()!.status_breakdown)}>
                      {([status, count]) => (
                        <div class='flex justify-between p-2 bg-base-200 rounded'>
                          <span class='capitalize'>{status.replace('_', ' ')}</span>
                          <span class='font-semibold'>{count}</span>
                        </div>
                      )}
                    </For>
                  </div>
                </div>

                <div>
                  <h4 class='font-semibold mb-2'>Type Breakdown</h4>
                  <div class='grid grid-cols-2 gap-2'>
                    <For each={Object.entries(stats()!.type_breakdown)}>
                      {([type, count]) => (
                        <div class='flex justify-between p-2 bg-base-200 rounded'>
                          <span class='capitalize'>{type.replace('_', ' ')}</span>
                          <span class='font-semibold'>{count}</span>
                        </div>
                      )}
                    </For>
                  </div>
                </div>
              </div>
            </Show>

            <div class='modal-action'>
              <button class='btn' onClick={() => setShowStatsModal(false)}>
                Close
              </button>
            </div>
          </div>
        </div>
      </Show>
    </div>
  );
};

export default LeadsManager;
