/**
 * Resume Service
 * Handles all API communications with the backend resume endpoints
 */

const API_BASE_URL = 'http://localhost:8080';

export interface ResumeData {
  id: string;
  user_id: string;
  title: string;
  status: string;
  resume_type: string;
  created_at: string;
  updated_at: string;
  version: number;
  completeness_score?: number;
}

export interface CreateResumeRequest {
  title: string;
  contact_info: {
    full_name: string;
    email: string;
    phone?: string;
    location?: string;
    linkedin_url?: string;
    github_url?: string;
    website_url?: string;
  };
  summary?: string;
  work_experience?: Array<{
    company: string;
    position: string;
    start_date: string;
    end_date?: string;
    description?: string;
    achievements?: string[];
  }>;
  education?: Array<{
    institution: string;
    degree: string;
    field_of_study?: string;
    graduation_date?: string;
    gpa?: string;
  }>;
  skills?: Array<{
    name: string;
    category?: string;
    proficiency_level?: string;
  }>;
  projects?: Array<{
    name: string;
    description?: string;
    technologies?: string[];
    url?: string;
  }>;
  certifications?: Array<{
    name: string;
    issuer?: string;
    date_earned?: string;
    expiry_date?: string;
  }>;
}

export class ResumeService {
  private static async request(endpoint: string, options: RequestInit = {}) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      let errorMessage;
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.message || 'Unknown error';
      } catch {
        errorMessage = await response.text();
      }
      throw new Error(`Resume API Error: ${response.status} - ${errorMessage}`);
    }

    return response.json();
  }

  /**
   * Get all resumes for a user
   */
  static async getUserResumes(userId: string, status?: string, page = 1, perPage = 10) {
    const params = new URLSearchParams({
      user_id: userId,
      page: page.toString(),
      per_page: perPage.toString(),
    });

    if (status) {
      params.append('status', status);
    }

    return this.request(`/api/resumes/?${params.toString()}`);
  }

  /**
   * Get a specific resume by ID
   */
  static async getResume(resumeId: string, userId: string) {
    const params = new URLSearchParams({ user_id: userId });
    return this.request(`/api/resumes/${resumeId}?${params.toString()}`);
  }

  /**
   * Create a new resume
   */
  static async createResume(resumeData: CreateResumeRequest, userId: string) {
    const params = new URLSearchParams({ user_id: userId });
    return this.request(`/api/resumes/?${params.toString()}`, {
      method: 'POST',
      body: JSON.stringify(resumeData),
    });
  }

  /**
   * Update an existing resume
   */
  static async updateResume(
    resumeId: string,
    updates: Partial<CreateResumeRequest>,
    userId: string
  ) {
    const params = new URLSearchParams({ user_id: userId });
    return this.request(`/api/resumes/${resumeId}?${params.toString()}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  }

  /**
   * Delete a resume
   */
  static async deleteResume(resumeId: string, userId: string) {
    const params = new URLSearchParams({ user_id: userId });
    return this.request(`/api/resumes/${resumeId}?${params.toString()}`, {
      method: 'DELETE',
    });
  }

  /**
   * Export resume in various formats
   */
  static async exportResume(
    resumeId: string,
    userId: string,
    options: {
      export_format: 'pdf' | 'json' | 'yaml' | 'txt';
      template_name?: string;
      filename?: string;
      theme_options?: Record<string, any>;
    }
  ) {
    const params = new URLSearchParams({ user_id: userId });
    return this.request(`/api/resumes/${resumeId}/export?${params.toString()}`, {
      method: 'POST',
      body: JSON.stringify({
        export_format: options.export_format,
        template_name: options.template_name || 'moderncv',
        filename: options.filename,
        theme_options: options.theme_options,
      }),
    });
  }

  /**
   * Generate PDF for a resume (legacy method for backward compatibility)
   */
  static async generatePDF(
    resumeId: string,
    userId: string,
    templateName = 'moderncv',
    filename?: string
  ) {
    return this.exportResume(resumeId, userId, {
      export_format: 'pdf',
      template_name: templateName,
      filename: filename,
    });
  }

  /**
   * Get resume analytics
   */
  static async getResumeAnalytics(resumeId: string, userId: string) {
    const params = new URLSearchParams({ user_id: userId });
    return this.request(`/api/resumes/${resumeId}/analytics?${params.toString()}`);
  }

  /**
   * Get available resume templates
   */
  static async getTemplates() {
    return this.request('/api/resumes/templates');
  }

  /**
   * Get export templates and formats
   */
  static async getExportTemplates() {
    return this.request('/api/resumes/export/templates');
  }

  /**
   * AI-generate resume content (if implemented)
   */
  static async aiGenerateResume(
    request: {
      generation_type: 'create' | 'optimize' | 'enhance';
      base_resume_id?: string;
      job_id?: string;
      job_description?: string;
      target_role?: string;
      target_industry?: string;
      optimization_level?: 'light' | 'moderate' | 'aggressive';
    },
    userId: string
  ) {
    const params = new URLSearchParams({ user_id: userId });
    return this.request(`/api/resumes/ai/generate?${params.toString()}`, {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }
}
