// =============================================================================
// ENUMS
// =============================================================================

export enum ContentFocusType {
  TECHNICAL = 'technical',
  LEADERSHIP = 'leadership',
  RESULTS = 'results',
  GENERAL = 'general',
  CREATIVE = 'creative',
  CONCISE = 'concise',
  DETAILED = 'detailed',
}

export enum SkillCategory {
  TECHNICAL = 'technical',
  SOFT = 'soft',
  TRANSFERABLE = 'transferable',
  INDUSTRY = 'industry',
  TOOL = 'tool',
  LANGUAGE = 'language',
  FRAMEWORK = 'framework',
  PLATFORM = 'platform',
  METHODOLOGY = 'methodology',
  DOMAIN = 'domain',
  OTHER = 'other',
}

export enum SkillLevel {
  BEGINNER = 'beginner',
  INTERMEDIATE = 'intermediate',
  ADVANCED = 'advanced',
  EXPERT = 'expert',
}

export enum ContentSource {
  MANUAL = 'manual',
  EXTRACTED = 'extracted',
  GENERATED = 'generated',
  IMPORTED = 'imported',
}

export enum ExperienceType {
  FULL_TIME = 'full_time',
  PART_TIME = 'part_time',
  CONTRACT = 'contract',
  FREELANCE = 'freelance',
  INTERNSHIP = 'internship',
  VOLUNTEER = 'volunteer',
}

// =============================================================================
// CONTENT VARIATION MODELS
// =============================================================================

export interface ContentVariation {
  id: string;
  title: string;
  content: string;
  target_industries: string[];
  target_roles: string[];
  keywords_emphasized: string[];
  created_at: string;
  last_used: string | null;
  usage_count: number;
  source: ContentSource;
}

export interface SummaryVariation extends ContentVariation {
  tone: string;
  length: string;
  focus: ContentFocusType;
}

export interface ExperienceContentVariation extends ContentVariation {
  experience_id: string;
  focus: ContentFocusType;
  achievements: string[];
  skills_highlighted: string[];
}

export interface EducationContentVariation extends ContentVariation {
  education_id: string;
  focus: ContentFocusType;
  highlights: string[];
  relevant_coursework: string[];
}

export interface ProjectContentVariation extends ContentVariation {
  project_id: string;
  focus: ContentFocusType;
  achievements: string[];
  technologies_highlighted: string[];
}

// =============================================================================
// MASTER ENTRY MODELS
// =============================================================================

export interface ExperienceEntry {
  id: string;
  company: string;
  position: string;
  location: string | null;
  start_date: string; // ISO date string
  end_date: string | null; // ISO date string
  is_current: boolean;
  experience_type: ExperienceType;
  default_description: string | null;
  default_achievements: string[];
  skills_used: string[];
  technologies: string[];
  has_variations: boolean;
  default_variation_id: string | null;
}

export interface EducationEntry {
  id: string;
  institution: string;
  degree: string;
  field_of_study: string | null;
  location: string | null;
  start_date: string | null; // ISO date string
  end_date: string | null; // ISO date string
  gpa: number | null;
  honors: string[];
  relevant_coursework: string[];
  default_description: string | null;
  has_variations: boolean;
  default_variation_id: string | null;
}

export interface ProjectEntry {
  id: string;
  name: string;
  url: string | null;
  github_url: string | null;
  start_date: string | null; // ISO date string
  end_date: string | null; // ISO date string
  default_description: string | null;
  default_achievements: string[];
  technologies: string[];
  has_variations: boolean;
  default_variation_id: string | null;
}

export interface EnhancedSkill {
  id: string;
  name: string;
  level: SkillLevel;
  category: SkillCategory;
  subcategory: string | null;
  years_experience: number | null;
  proficiency_score: number | null; // 0.0-1.0
  description: string | null;
  keywords: string[];
  is_featured: boolean;
  display_order: number;
  source: ContentSource;
  confidence: number; // 0.0-1.0
  last_used: string | null; // ISO datetime string
  usage_count: number;
}

export interface Certification {
  id: string;
  name: string;
  issuer: string;
  issue_date: string | null; // ISO date string
  expiry_date: string | null; // ISO date string
  credential_id: string | null;
  url: string | null;
  description: string | null;
}

// =============================================================================
// COMPLETE SKILL BANK MODEL
// =============================================================================

export interface SkillBankResponse {
  id: string;
  user_id: string;
  skills: Record<string, EnhancedSkill[]>;
  skill_categories: string[];
  default_summary: string | null;
  summary_variations: SummaryVariation[];
  work_experiences: ExperienceEntry[];
  education_entries: EducationEntry[];
  projects: ProjectEntry[];
  certifications: Certification[];
  experience_content_variations: Record<string, ExperienceContentVariation[]>;
  education_content_variations: Record<string, EducationContentVariation[]>;
  project_content_variations: Record<string, ProjectContentVariation[]>;
  created_at: string; // ISO datetime string
  updated_at: string; // ISO datetime string
}

// =============================================================================
// REQUEST MODELS
// =============================================================================

export interface SkillBankUpdateRequest {
  default_summary?: string | null;
  skill_categories?: string[];
}

export interface EnhancedSkillRequest {
  name: string;
  level?: SkillLevel;
  category?: SkillCategory;
  subcategory?: string | null;
  years_experience?: number | null;
  proficiency_score?: number | null; // 0.0-1.0
  description?: string | null;
  keywords?: string[];
  is_featured?: boolean;
  display_order?: number;
  source?: ContentSource;
}

export interface SkillUpdateRequest {
  name?: string;
  level?: SkillLevel;
  category?: SkillCategory;
  subcategory?: string | null;
  years_experience?: number | null;
  proficiency_score?: number | null; // 0.0-1.0
  description?: string | null;
  keywords?: string[];
  is_featured?: boolean;
  display_order?: number;
}

export interface SummaryVariationRequest {
  title: string;
  content: string;
  tone?: string;
  length?: string;
  focus?: ContentFocusType;
  target_industries?: string[];
  target_roles?: string[];
  keywords_emphasized?: string[];
}

export interface ExperienceEntryRequest {
  company: string;
  position: string;
  location?: string | null;
  start_date: string; // ISO date string
  end_date?: string | null; // ISO date string
  is_current?: boolean;
  experience_type?: ExperienceType;
  default_description?: string | null;
  default_achievements?: string[];
  skills_used?: string[];
  technologies?: string[];
}

export interface ExperienceContentVariationRequest {
  experience_id: string;
  title: string;
  content: string;
  focus?: ContentFocusType;
  achievements?: string[];
  skills_highlighted?: string[];
  target_industries?: string[];
  target_roles?: string[];
  keywords_emphasized?: string[];
}

export interface EducationEntryRequest {
  institution: string;
  degree: string;
  field_of_study?: string | null;
  location?: string | null;
  start_date?: string | null; // ISO date string
  end_date?: string | null; // ISO date string
  gpa?: number | null;
  honors?: string[];
  relevant_coursework?: string[];
  default_description?: string | null;
}

export interface ProjectEntryRequest {
  name: string;
  url?: string | null;
  github_url?: string | null;
  start_date?: string | null; // ISO date string
  end_date?: string | null; // ISO date string
  default_description?: string | null;
  default_achievements?: string[];
  technologies?: string[];
}

export interface CertificationRequest {
  name: string;
  issuer: string;
  issue_date?: string | null; // ISO date string
  expiry_date?: string | null; // ISO date string
  credential_id?: string | null;
  url?: string | null;
  description?: string | null;
}

// =============================================================================
// UTILITY TYPES
// =============================================================================

export interface SkillBankStats {
  total_skills: number;
  skills_by_category: Record<string, number>;
  total_summary_variations: number;
  total_work_experiences: number;
  total_education_entries: number;
  total_projects: number;
  total_certifications: number;
  last_updated: string; // ISO datetime string
  created_at: string; // ISO datetime string
}
