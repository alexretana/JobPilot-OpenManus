import { createSignal, createResource, createMemo } from 'solid-js';
import { skillBankApiService } from '../services/skillBankApi';
import type {
  SkillBankResponse,
  EnhancedSkill,
  ExperienceEntry,
  EducationEntry,
  ProjectEntry,
  Certification,
  SummaryVariation,
} from '../types';

/**
 * Hook to manage Skill Bank integration for Resume Builder sections
 * Provides data and utility functions for each resume section
 */
export function useSkillBankIntegration(userId: string) {
  const [useSkillBankForContact, setUseSkillBankForContact] = createSignal(false);
  const [useSkillBankForSummary, setUseSkillBankForSummary] = createSignal(false);
  const [useSkillBankForExperience, setUseSkillBankForExperience] = createSignal(false);
  const [useSkillBankForEducation, setUseSkillBankForEducation] = createSignal(false);
  const [useSkillBankForProjects, setUseSkillBankForProjects] = createSignal(false);
  const [useSkillBankForSkills, setUseSkillBankForSkills] = createSignal(false);
  const [useSkillBankForCertifications, setUseSkillBankForCertifications] = createSignal(false);

  // Load Skill Bank data
  const [skillBankData] = createResource(
    () => userId,
    async id => {
      try {
        return await skillBankApiService.getSkillBank(id);
      } catch (error) {
        console.warn('Failed to load skill bank data:', error);
        return null;
      }
    }
  );

  // Contact Info from Skill Bank (derived from User Profile)
  const skillBankContactInfo = createMemo(() => {
    const data = skillBankData();
    if (!data) return null;

    // Note: Contact info is typically stored in UserProfile, not directly in Skill Bank
    // This would need to be fetched from UserProfile or added to Skill Bank response
    return {
      full_name: '', // Would come from user profile
      email: '', // Would come from user profile
      phone: '', // Would come from user profile
      location: '', // Would come from user profile
      linkedin_url: '', // Would come from user profile
      github_url: '', // Would come from user profile
      website_url: '', // Would come from user profile
    };
  });

  // Summary Options from Skill Bank
  const skillBankSummaryOptions = createMemo(() => {
    const data = skillBankData();
    if (!data) return [];

    const options = [];

    // Add default summary if exists
    if (data.default_summary) {
      options.push({
        id: 'default',
        title: 'Default Summary',
        content: data.default_summary,
      });
    }

    // Add summary variations
    data.summary_variations.forEach(variation => {
      options.push({
        id: variation.id,
        title: variation.title,
        content: variation.content,
      });
    });

    return options;
  });

  // Experience Options from Skill Bank
  const skillBankExperienceOptions = createMemo(() => {
    const data = skillBankData();
    if (!data) return [];

    return data.work_experiences.map(exp => ({
      id: exp.id,
      company: exp.company,
      position: exp.position,
      location: exp.location,
      start_date: exp.start_date,
      end_date: exp.end_date,
      is_current: exp.is_current,
      description: exp.default_description || '',
      achievements: exp.default_achievements || [],
      // Add content variations info
      hasVariations: exp.has_variations,
      variations: data.experience_content_variations[exp.id] || [],
    }));
  });

  // Education Options from Skill Bank
  const skillBankEducationOptions = createMemo(() => {
    const data = skillBankData();
    if (!data) return [];

    return data.education_entries.map(edu => ({
      id: edu.id,
      institution: edu.institution,
      degree: edu.degree,
      field_of_study: edu.field_of_study,
      location: edu.location,
      start_date: edu.start_date,
      end_date: edu.end_date,
      graduation_date: edu.end_date, // Map end_date to graduation_date
      gpa: edu.gpa?.toString() || '',
      honors: edu.honors || [],
      relevant_coursework: edu.relevant_coursework || [],
      // Add content variations info
      hasVariations: edu.has_variations,
      variations: data.education_content_variations[edu.id] || [],
    }));
  });

  // Projects Options from Skill Bank
  const skillBankProjectOptions = createMemo(() => {
    const data = skillBankData();
    if (!data) return [];

    return data.projects.map(project => ({
      id: project.id,
      name: project.name,
      description: project.default_description || '',
      technologies: project.technologies || [],
      url: project.url || '',
      start_date: project.start_date,
      end_date: project.end_date,
      achievements: project.default_achievements || [],
      // Add content variations info
      hasVariations: project.has_variations,
      variations: data.project_content_variations[project.id] || [],
    }));
  });

  // Skills Options from Skill Bank
  const skillBankSkillsOptions = createMemo(() => {
    const data = skillBankData();
    if (!data) return [];

    const skills: any[] = [];

    // Flatten skills from all categories
    Object.entries(data.skills).forEach(([category, categorySkills]) => {
      categorySkills.forEach(skill => {
        skills.push({
          name: skill.name,
          category: skill.category,
          proficiency_level: skill.level, // Map level to proficiency_level
          years_experience: skill.years_experience,
          description: skill.description,
        });
      });
    });

    return skills;
  });

  // Certifications Options from Skill Bank
  const skillBankCertificationsOptions = createMemo(() => {
    const data = skillBankData();
    if (!data) return [];

    return data.certifications.map(cert => ({
      id: cert.id,
      name: cert.name,
      issuer: cert.issuer,
      date_earned: cert.issue_date,
      expiry_date: cert.expiry_date,
      credential_id: cert.credential_id || '',
      verification_url: cert.url || '',
      status: 'Active', // Default status
      description: cert.description,
    }));
  });

  // Utility functions to convert Skill Bank data to Resume format
  const convertSkillBankSummaryToResume = (summaryOption: any) => {
    return summaryOption.content;
  };

  const convertSkillBankExperienceToResume = (experienceOption: any, variationId?: string) => {
    const baseExp = {
      company: experienceOption.company,
      position: experienceOption.position,
      location: experienceOption.location || '',
      start_date: experienceOption.start_date,
      end_date: experienceOption.end_date || '',
      is_current: experienceOption.is_current || false,
      description: experienceOption.description,
      achievements: experienceOption.achievements,
    };

    // If variation is requested, override content
    if (variationId && experienceOption.variations) {
      const variation = experienceOption.variations.find((v: any) => v.id === variationId);
      if (variation) {
        baseExp.description = variation.content;
        baseExp.achievements = variation.achievements || experienceOption.achievements;
      }
    }

    return baseExp;
  };

  const convertSkillBankEducationToResume = (educationOption: any) => {
    return {
      institution: educationOption.institution,
      degree: educationOption.degree,
      field_of_study: educationOption.field_of_study || '',
      location: educationOption.location || '',
      start_date: educationOption.start_date || '',
      graduation_date: educationOption.graduation_date || '',
      gpa: educationOption.gpa,
      honors: educationOption.honors,
      relevant_coursework: educationOption.relevant_coursework,
    };
  };

  const convertSkillBankProjectToResume = (projectOption: any, variationId?: string) => {
    const baseProject = {
      name: projectOption.name,
      description: projectOption.description,
      technologies: projectOption.technologies,
      url: projectOption.url,
      start_date: projectOption.start_date || '',
      end_date: projectOption.end_date || '',
      achievements: projectOption.achievements,
    };

    // If variation is requested, override content
    if (variationId && projectOption.variations) {
      const variation = projectOption.variations.find((v: any) => v.id === variationId);
      if (variation) {
        baseProject.description = variation.content;
        baseProject.achievements = variation.achievements || projectOption.achievements;
      }
    }

    return baseProject;
  };

  const convertSkillBankSkillsToResume = (selectedSkills: any[]) => {
    return selectedSkills.map(skill => ({
      name: skill.name,
      category: skill.category,
      proficiency_level: skill.proficiency_level,
    }));
  };

  const convertSkillBankCertificationsToResume = (certificationOptions: any[]) => {
    return certificationOptions.map(cert => ({
      name: cert.name,
      issuer: cert.issuer,
      date_earned: cert.date_earned || '',
      expiry_date: cert.expiry_date || '',
      credential_id: cert.credential_id,
      verification_url: cert.verification_url,
      status: cert.status,
    }));
  };

  return {
    // Toggle states
    useSkillBankForContact,
    setUseSkillBankForContact,
    useSkillBankForSummary,
    setUseSkillBankForSummary,
    useSkillBankForExperience,
    setUseSkillBankForExperience,
    useSkillBankForEducation,
    setUseSkillBankForEducation,
    useSkillBankForProjects,
    setUseSkillBankForProjects,
    useSkillBankForSkills,
    setUseSkillBankForSkills,
    useSkillBankForCertifications,
    setUseSkillBankForCertifications,

    // Data
    skillBankData,
    skillBankContactInfo,
    skillBankSummaryOptions,
    skillBankExperienceOptions,
    skillBankEducationOptions,
    skillBankProjectOptions,
    skillBankSkillsOptions,
    skillBankCertificationsOptions,

    // Conversion utilities
    convertSkillBankSummaryToResume,
    convertSkillBankExperienceToResume,
    convertSkillBankEducationToResume,
    convertSkillBankProjectToResume,
    convertSkillBankSkillsToResume,
    convertSkillBankCertificationsToResume,

    // Loading states
    isLoading: () => skillBankData.loading,
    hasError: () => skillBankData.error,
  };
}
