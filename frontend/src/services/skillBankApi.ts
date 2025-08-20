import type {
  SkillBankResponse,
  SkillBankUpdateRequest,
  EnhancedSkill,
  EnhancedSkillRequest,
  SkillUpdateRequest,
  SummaryVariation,
  SummaryVariationRequest,
  ExperienceEntry,
  ExperienceEntryRequest,
  ExperienceContentVariation,
  ExperienceContentVariationRequest,
  SkillBankStats,
} from '../types';

const API_BASE_URL = '/api/skill-bank';

class SkillBankApiService {
  private async fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`Skill Bank API Error: ${response.status} ${response.statusText}`);
    }

    // Handle 204 No Content responses
    if (response.status === 204) {
      return {} as T;
    }

    return response.json();
  }

  // =============================================================================
  // MAIN SKILL BANK OPERATIONS
  // =============================================================================

  /**
   * Get user's complete skill bank
   */
  async getSkillBank(userId: string): Promise<SkillBankResponse> {
    return this.fetchApi<SkillBankResponse>(`/${userId}`);
  }

  /**
   * Update skill bank basic information
   */
  async updateSkillBank(
    userId: string,
    updates: SkillBankUpdateRequest
  ): Promise<SkillBankResponse> {
    return this.fetchApi<SkillBankResponse>(`/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  }

  // =============================================================================
  // SKILLS MANAGEMENT
  // =============================================================================

  /**
   * Add a new skill to the skill bank
   */
  async addSkill(userId: string, skill: EnhancedSkillRequest): Promise<EnhancedSkill> {
    return this.fetchApi<EnhancedSkill>(`/${userId}/skills`, {
      method: 'POST',
      body: JSON.stringify(skill),
    });
  }

  /**
   * Get all skills for a user, optionally filtered by category
   */
  async getSkills(userId: string, category?: string): Promise<EnhancedSkill[]> {
    const params = category ? `?category=${encodeURIComponent(category)}` : '';
    return this.fetchApi<EnhancedSkill[]>(`/${userId}/skills${params}`);
  }

  /**
   * Update an existing skill
   */
  async updateSkill(
    userId: string,
    skillId: string,
    updates: SkillUpdateRequest
  ): Promise<EnhancedSkill> {
    return this.fetchApi<EnhancedSkill>(`/${userId}/skills/${skillId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  }

  /**
   * Delete a skill from the skill bank
   */
  async deleteSkill(userId: string, skillId: string): Promise<void> {
    await this.fetchApi<void>(`/${userId}/skills/${skillId}`, {
      method: 'DELETE',
    });
  }

  // =============================================================================
  // SUMMARY VARIATIONS
  // =============================================================================

  /**
   * Add a new summary variation
   */
  async addSummaryVariation(
    userId: string,
    variation: SummaryVariationRequest
  ): Promise<SummaryVariation> {
    return this.fetchApi<SummaryVariation>(`/${userId}/summaries`, {
      method: 'POST',
      body: JSON.stringify(variation),
    });
  }

  /**
   * Update a summary variation
   */
  async updateSummaryVariation(
    userId: string,
    variationId: string,
    updates: SummaryVariationRequest
  ): Promise<SummaryVariation> {
    return this.fetchApi<SummaryVariation>(`/${userId}/summaries/${variationId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  }

  /**
   * Delete a summary variation
   */
  async deleteSummaryVariation(userId: string, variationId: string): Promise<void> {
    await this.fetchApi<void>(`/${userId}/summaries/${variationId}`, {
      method: 'DELETE',
    });
  }

  // =============================================================================
  // EXPERIENCE MANAGEMENT
  // =============================================================================

  /**
   * Add a new work experience entry
   */
  async addExperience(
    userId: string,
    experience: ExperienceEntryRequest
  ): Promise<ExperienceEntry> {
    return this.fetchApi<ExperienceEntry>(`/${userId}/experience`, {
      method: 'POST',
      body: JSON.stringify(experience),
    });
  }

  /**
   * Update a work experience entry
   */
  async updateExperience(
    userId: string,
    experienceId: string,
    updates: ExperienceEntryRequest
  ): Promise<ExperienceEntry> {
    return this.fetchApi<ExperienceEntry>(`/${userId}/experience/${experienceId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  }

  /**
   * Delete a work experience entry
   */
  async deleteExperience(userId: string, experienceId: string): Promise<void> {
    await this.fetchApi<void>(`/${userId}/experience/${experienceId}`, {
      method: 'DELETE',
    });
  }

  /**
   * Add a content variation to a work experience entry
   */
  async addExperienceContentVariation(
    userId: string,
    experienceId: string,
    variation: ExperienceContentVariationRequest
  ): Promise<ExperienceContentVariation> {
    return this.fetchApi<ExperienceContentVariation>(
      `/${userId}/experience/${experienceId}/content`,
      {
        method: 'POST',
        body: JSON.stringify(variation),
      }
    );
  }

  // =============================================================================
  // DATA MIGRATION
  // =============================================================================

  /**
   * Migrate skills data from UserProfile to SkillBank
   */
  async migrateFromUserProfile(userId: string): Promise<SkillBankResponse> {
    return this.fetchApi<SkillBankResponse>(`/${userId}/migrate`, {
      method: 'POST',
    });
  }

  // =============================================================================
  // UTILITY OPERATIONS
  // =============================================================================

  /**
   * Get all skill categories for a user
   */
  async getSkillCategories(userId: string): Promise<string[]> {
    return this.fetchApi<string[]>(`/${userId}/categories`);
  }

  /**
   * Get skill bank statistics
   */
  async getSkillBankStats(userId: string): Promise<SkillBankStats> {
    return this.fetchApi<SkillBankStats>(`/${userId}/stats`);
  }
}

export const skillBankApiService = new SkillBankApiService();
