/**
 * Job API Service
 * Service for interacting with job-related API endpoints
 */

export interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  job_type: string | null;
  remote_type: string | null;
  salary_min: number | null;
  salary_max: number | null;
  salary_currency: string | null;
  skills_required: string[];
  posted_date: string | null;
  description: string | null;
  job_url: string | null;
}

export interface JobDetails extends Job {
  experience_level: string | null;
  requirements: string | null;
  responsibilities: string | null;
  skills_preferred: string[];
  benefits: string[];
  company_size: string | null;
  industry: string | null;
  source: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface JobSearchResponse {
  jobs: Job[];
  total: number;
  timestamp: string;
}

export interface JobSearchFilters {
  query?: string;
  job_types?: string;
  locations?: string;
  limit?: number;
}

export interface SavedJob {
  // Job details (flattened from backend response)
  id: string;
  title: string;
  company: string;
  location: string;
  job_type: string | null;
  remote_type: string | null;
  salary_min: number | null;
  salary_max: number | null;
  salary_currency: string | null;
  skills_required: string[];
  posted_date: string | null;
  description: string | null;
  job_url: string | null;

  // Saved job metadata
  saved_date: string;
  notes: string | null;
  tags: string[];
  saved_job_id: string;
}

export interface SaveJobRequest {
  job_id: string;
  notes?: string;
  tags?: string[];
}

export interface SavedJobsResponse {
  jobs: SavedJob[];
  total: number;
  user_id: string;
  timestamp: string;
}

class JobApiService {
  private baseUrl = window.location.origin;

  /**
   * Get recent jobs
   */
  async getRecentJobs(limit: number = 20): Promise<JobSearchResponse> {
    const response = await fetch(`${this.baseUrl}/api/jobs/recent?limit=${limit}`);

    if (!response.ok) {
      throw new Error(`Failed to fetch recent jobs: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get detailed job information
   */
  async getJobDetails(jobId: string): Promise<JobDetails> {
    const response = await fetch(`${this.baseUrl}/api/jobs/${jobId}`);

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Job not found');
      }
      throw new Error(`Failed to fetch job details: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Search jobs with filters
   */
  async searchJobs(filters: JobSearchFilters = {}): Promise<JobSearchResponse> {
    const params = new URLSearchParams();

    if (filters.query) params.append('query', filters.query);
    if (filters.job_types) params.append('job_types', filters.job_types);
    if (filters.locations) params.append('locations', filters.locations);
    if (filters.limit) params.append('limit', filters.limit.toString());

    const response = await fetch(`${this.baseUrl}/api/jobs/search?${params}`);

    if (!response.ok) {
      throw new Error(`Failed to search jobs: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Format salary range for display
   */
  formatSalary(job: Job): string {
    if (!job.salary_min && !job.salary_max) {
      return 'Salary not specified';
    }

    const currency = job.salary_currency || '$';

    if (job.salary_min && job.salary_max) {
      return `${currency}${job.salary_min.toLocaleString()} - ${currency}${job.salary_max.toLocaleString()}`;
    }

    if (job.salary_min) {
      return `${currency}${job.salary_min.toLocaleString()}+`;
    }

    if (job.salary_max) {
      return `Up to ${currency}${job.salary_max.toLocaleString()}`;
    }

    return 'Salary not specified';
  }

  /**
   * Format posted date for display
   */
  formatPostedDate(job: Job): string {
    if (!job.posted_date) {
      return 'Date not specified';
    }

    const date = new Date(job.posted_date);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 1) {
      return '1 day ago';
    } else if (diffDays < 7) {
      return `${diffDays} days ago`;
    } else if (diffDays < 30) {
      const weeks = Math.floor(diffDays / 7);
      return weeks === 1 ? '1 week ago' : `${weeks} weeks ago`;
    } else {
      return date.toLocaleDateString();
    }
  }

  /**
   * Get job type display label
   */
  getJobTypeLabel(jobType: string | null): string {
    if (!jobType) return 'Not specified';

    const labels: Record<string, string> = {
      'Full-time': 'Full-time',
      'Part-time': 'Part-time',
      'Contract': 'Contract',
      'Temporary': 'Temporary',
      'Internship': 'Internship',
      'Volunteer': 'Volunteer'
    };

    return labels[jobType] || jobType;
  }

  /**
   * Get remote type display label
   */
  getRemoteTypeLabel(remoteType: string | null): string {
    if (!remoteType) return 'Not specified';

    const labels: Record<string, string> = {
      'Remote': 'Remote',
      'On-site': 'On-site',
      'Hybrid': 'Hybrid'
    };

    return labels[remoteType] || remoteType;
  }

  /**
   * Get remote type icon
   */
  getRemoteTypeIcon(remoteType: string | null): string {
    const icons: Record<string, string> = {
      'Remote': '🏠',
      'On-site': '🏢',
      'Hybrid': '🔄'
    };

    return icons[remoteType || ''] || '📍';
  }

  // =====================================
  // Saved Jobs API Methods
  // =====================================

  /**
   * Save a job
   */
  async saveJob(request: SaveJobRequest): Promise<void> {
    const response = await fetch(`${this.baseUrl}/api/jobs/${request.job_id}/save`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`Failed to save job: ${response.statusText}`);
    }
  }

  /**
   * Unsave a job
   */
  async unsaveJob(jobId: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}/api/jobs/${jobId}/save`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error(`Failed to unsave job: ${response.statusText}`);
    }
  }

  /**
   * Check if a job is saved
   */
  async isJobSaved(jobId: string): Promise<boolean> {
    const response = await fetch(`${this.baseUrl}/api/jobs/${jobId}/saved`);

    if (!response.ok) {
      throw new Error(`Failed to check if job is saved: ${response.statusText}`);
    }

    const result = await response.json();
    return result.is_saved;
  }

  /**
   * Get all saved jobs
   */
  async getSavedJobs(limit: number = 20): Promise<SavedJob[]> {
    const response = await fetch(`${this.baseUrl}/api/saved-jobs?limit=${limit}`);

    if (!response.ok) {
      throw new Error(`Failed to fetch saved jobs: ${response.statusText}`);
    }

    const data = await response.json();
    return data.jobs; // Return just the jobs array, not the full response
  }

  /**
   * Update saved job notes and tags
   */
  async updateSavedJob(jobId: string, request: SaveJobRequest): Promise<void> {
    const response = await fetch(`${this.baseUrl}/api/jobs/${jobId}/save`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`Failed to update saved job: ${response.statusText}`);
    }
  }

  /**
   * Format saved date for display
   */
  formatSavedDate(savedDate: string): string {
    const date = new Date(savedDate);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 0) {
      return 'Saved today';
    } else if (diffDays === 1) {
      return 'Saved yesterday';
    } else if (diffDays < 7) {
      return `Saved ${diffDays} days ago`;
    } else if (diffDays < 30) {
      const weeks = Math.floor(diffDays / 7);
      return weeks === 1 ? 'Saved 1 week ago' : `Saved ${weeks} weeks ago`;
    } else {
      return `Saved on ${date.toLocaleDateString()}`;
    }
  }
}

// Export singleton instance
export const jobApi = new JobApiService();
