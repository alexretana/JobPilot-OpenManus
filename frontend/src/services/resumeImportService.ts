/**
 * Resume Import Service
 * Handles the mapping of user profile data to resume structure
 * for the "Create Resume from Profile" workflow
 */

import { UserProfile } from './userProfileApi';
import { CreateResumeRequest } from './resumeService';

export interface ResumeImportOptions {
  includeContactInfo?: boolean;
  includeSummary?: boolean;
  includeSkills?: boolean;
  includeEducation?: boolean;
  includeExperience?: boolean;
  templateTitle?: string;
}

export interface ResumeImportPreview {
  resumeData: CreateResumeRequest;
  mappedFields: {
    contactInfo: string[];
    summary: boolean;
    skills: number;
    education: number;
    experience: number;
  };
  missingFields: string[];
  warnings: string[];
}

export class ResumeImportService {
  /**
   * Maps user profile data to resume structure
   */
  static mapProfileToResume(
    profile: UserProfile,
    options: ResumeImportOptions = {}
  ): CreateResumeRequest {
    const {
      includeContactInfo = true,
      includeSummary = true,
      includeSkills = true,
      includeEducation = true,
      includeExperience = true,
      templateTitle,
    } = options;

    // Generate resume title
    const resumeTitle = 
      templateTitle ||
      this.generateResumeTitle(profile) ||
      'My Professional Resume';

    const resumeData: CreateResumeRequest = {
      title: resumeTitle,
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
    };

    // Map contact information
    if (includeContactInfo) {
      resumeData.contact_info = this.mapContactInfo(profile);
    }

    // Map professional summary
    if (includeSummary && profile.bio) {
      resumeData.summary = profile.bio;
    }

    // Map skills
    if (includeSkills && profile.skills && profile.skills.length > 0) {
      resumeData.skills = this.mapSkills(profile.skills);
    }

    // Map education (if available in profile)
    if (includeEducation && profile.education) {
      resumeData.education = this.mapEducation(profile);
    }

    // Note: Work experience mapping would require additional profile fields
    // that aren't currently in the UserProfile interface
    if (includeExperience) {
      // This would be implemented when work experience is added to UserProfile
      resumeData.work_experience = [];
    }

    return resumeData;
  }

  /**
   * Creates a preview of the import with detailed information about what will be mapped
   */
  static createImportPreview(
    profile: UserProfile,
    options: ResumeImportOptions = {}
  ): ResumeImportPreview {
    const resumeData = this.mapProfileToResume(profile, options);
    const mappedFields = this.analyzeMappedFields(profile, resumeData);
    const missingFields = this.identifyMissingFields(profile);
    const warnings = this.generateWarnings(profile, options);

    return {
      resumeData,
      mappedFields,
      missingFields,
      warnings,
    };
  }

  /**
   * Maps profile contact information to resume format
   */
  private static mapContactInfo(profile: UserProfile) {
    const fullName = [profile.first_name, profile.last_name]
      .filter(Boolean)
      .join(' ') || 'Your Name';

    return {
      full_name: fullName,
      email: profile.email || '',
      phone: profile.phone || '',
      location: profile.preferred_locations?.[0] || '',
      linkedin_url: profile.linkedin_url || '',
      github_url: profile.github_url || '',
      website_url: profile.website_url || '',
    };
  }

  /**
   * Maps profile skills to resume skills format
   */
  private static mapSkills(profileSkills: string[]) {
    return profileSkills.map((skillName) => ({
      name: skillName,
      category: this.categorizeSkill(skillName),
      proficiency_level: 'Intermediate', // Default level, user can adjust
    }));
  }

  /**
   * Maps profile education to resume format
   */
  private static mapEducation(profile: UserProfile) {
    if (!profile.education) return [];

    // Simple mapping - in a real implementation, this might parse structured education data
    return [
      {
        institution: 'Educational Institution',
        degree: profile.education,
        field_of_study: '',
        location: '',
        start_date: '',
        graduation_date: '',
        gpa: '',
        honors: [],
        relevant_coursework: [],
      },
    ];
  }

  /**
   * Attempts to categorize a skill based on common patterns
   */
  private static categorizeSkill(skillName: string): string {
    const skill = skillName.toLowerCase();
    
    // Programming languages
    const programmingLangs = [
      'javascript', 'python', 'java', 'c++', 'c#', 'ruby', 'php', 'go', 
      'rust', 'typescript', 'swift', 'kotlin', 'scala', 'r', 'matlab'
    ];
    
    // Frameworks and libraries
    const frameworks = [
      'react', 'angular', 'vue', 'node', 'express', 'django', 'flask', 
      'spring', 'rails', 'laravel', 'nextjs', 'nuxt', 'solid'
    ];
    
    // Tools and software
    const tools = [
      'git', 'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'jenkins', 
      'terraform', 'ansible', 'linux', 'windows', 'macos'
    ];
    
    // Data and analytics
    const dataTools = [
      'sql', 'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch', 
      'tableau', 'powerbi', 'excel', 'pandas', 'numpy'
    ];

    if (programmingLangs.some(lang => skill.includes(lang))) {
      return 'Programming Languages';
    }
    if (frameworks.some(fw => skill.includes(fw))) {
      return 'Frameworks & Libraries';
    }
    if (tools.some(tool => skill.includes(tool))) {
      return 'Tools & Software';
    }
    if (dataTools.some(tool => skill.includes(tool))) {
      return 'Data & Analytics';
    }
    
    // Default category
    return 'Technical Skills';
  }

  /**
   * Generates a resume title based on profile information
   */
  private static generateResumeTitle(profile: UserProfile): string {
    const name = [profile.first_name, profile.last_name].filter(Boolean).join(' ');
    const title = profile.current_title;
    const year = new Date().getFullYear();

    if (name && title) {
      return `${name} - ${title} Resume ${year}`;
    }
    if (name) {
      return `${name} Resume ${year}`;
    }
    if (title) {
      return `${title} Resume ${year}`;
    }
    
    return `Professional Resume ${year}`;
  }

  /**
   * Analyzes what fields were successfully mapped
   */
  private static analyzeMappedFields(profile: UserProfile, resumeData: CreateResumeRequest) {
    const contactFields: string[] = [];
    
    if (resumeData.contact_info.full_name) contactFields.push('Full Name');
    if (resumeData.contact_info.email) contactFields.push('Email');
    if (resumeData.contact_info.phone) contactFields.push('Phone');
    if (resumeData.contact_info.location) contactFields.push('Location');
    if (resumeData.contact_info.linkedin_url) contactFields.push('LinkedIn');
    if (resumeData.contact_info.github_url) contactFields.push('GitHub');
    if (resumeData.contact_info.website_url) contactFields.push('Website');

    return {
      contactInfo: contactFields,
      summary: !!resumeData.summary,
      skills: resumeData.skills?.length || 0,
      education: resumeData.education?.length || 0,
      experience: resumeData.work_experience?.length || 0,
    };
  }

  /**
   * Identifies fields that are missing from the profile
   */
  private static identifyMissingFields(profile: UserProfile): string[] {
    const missing: string[] = [];

    if (!profile.first_name && !profile.last_name) missing.push('Full Name');
    if (!profile.email) missing.push('Email Address');
    if (!profile.bio) missing.push('Professional Summary');
    if (!profile.skills || profile.skills.length === 0) missing.push('Skills');
    if (!profile.current_title) missing.push('Current Job Title');
    if (!profile.phone) missing.push('Phone Number');

    return missing;
  }

  /**
   * Generates warnings about the import process
   */
  private static generateWarnings(profile: UserProfile, options: ResumeImportOptions): string[] {
    const warnings: string[] = [];

    if (!profile.bio) {
      warnings.push('No professional summary found. Consider adding a bio to your profile.');
    }

    if (!profile.skills || profile.skills.length === 0) {
      warnings.push('No skills found in profile. You\'ll need to add skills manually.');
    }

    if (profile.skills && profile.skills.length < 5) {
      warnings.push('Limited skills found. Consider adding more skills to your profile.');
    }

    if (!profile.linkedin_url && !profile.github_url) {
      warnings.push('No professional social links found. Consider adding LinkedIn or GitHub URLs.');
    }

    if (!profile.phone) {
      warnings.push('Phone number not provided. This may be required for some applications.');
    }

    return warnings;
  }

  /**
   * Validates if a profile has minimum required data for resume creation
   */
  static validateProfileForImport(profile: UserProfile): { 
    isValid: boolean; 
    errors: string[]; 
    warnings: string[]; 
  } {
    const errors: string[] = [];
    const warnings: string[] = [];

    // Required fields
    if (!profile.first_name && !profile.last_name) {
      errors.push('Name is required for resume creation');
    }

    if (!profile.email) {
      errors.push('Email address is required for resume creation');
    }

    // Recommended fields
    if (!profile.bio) {
      warnings.push('Professional summary recommended');
    }

    if (!profile.current_title) {
      warnings.push('Current job title recommended');
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings: [...warnings, ...this.generateWarnings(profile, {})],
    };
  }
}

export default ResumeImportService;
