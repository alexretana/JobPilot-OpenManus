# Skill Bank Frontend Service Layer

This document describes the implementation of the Skill Bank frontend service layer for the JobPilot application.

## Overview

The Skill Bank service layer provides TypeScript-based API clients and type definitions for interacting with the
JobPilot Skill Bank backend. It includes comprehensive CRUD operations, type safety, and error handling for all skill
bank operations.

## Files Structure

```
frontend/src/
├── services/
│   └── skillBankApi.ts          # Main API service class
├── types/
│   └── skillBank.ts             # TypeScript type definitions
├── types.ts                     # Main types file (re-exports skill bank types)
└── components/SkillBank/
    └── SkillBankExample.tsx     # Example React component
```

## API Service (`skillBankApi.ts`)

### Class: `SkillBankApiService`

The main service class provides methods for all Skill Bank operations:

#### Main Operations

- `getSkillBank(userId: string)` - Get user's complete skill bank
- `updateSkillBank(userId: string, updates: SkillBankUpdateRequest)` - Update basic information

#### Skills Management

- `addSkill(userId: string, skill: EnhancedSkillRequest)` - Add a new skill
- `getSkills(userId: string, category?: string)` - Get all skills, optionally filtered
- `updateSkill(userId: string, skillId: string, updates: SkillUpdateRequest)` - Update skill
- `deleteSkill(userId: string, skillId: string)` - Delete a skill

#### Summary Variations

- `addSummaryVariation(userId: string, variation: SummaryVariationRequest)` - Add summary variation
- `updateSummaryVariation(userId: string, variationId: string, updates: SummaryVariationRequest)` - Update variation
- `deleteSummaryVariation(userId: string, variationId: string)` - Delete variation

#### Experience Management

- `addExperience(userId: string, experience: ExperienceEntryRequest)` - Add work experience
- `updateExperience(userId: string, experienceId: string, updates: ExperienceEntryRequest)` - Update experience
- `deleteExperience(userId: string, experienceId: string)` - Delete experience
- `addExperienceContentVariation(userId: string, experienceId: string, variation: ExperienceContentVariationRequest)` -
  Add content variation

#### Utility Operations

- `migrateFromUserProfile(userId: string)` - Migrate data from UserProfile
- `getSkillCategories(userId: string)` - Get all skill categories
- `getSkillBankStats(userId: string)` - Get statistics

### Usage Example

```typescript
import { skillBankApiService } from '../services/skillBankApi';
import { SkillLevel, SkillCategory } from '../types';

// Get skill bank
const skillBank = await skillBankApiService.getSkillBank('user-123');

// Add a new skill
const newSkill = await skillBankApiService.addSkill('user-123', {
  name: 'React',
  level: SkillLevel.ADVANCED,
  category: SkillCategory.TECHNICAL,
  description: 'Advanced React development',
  keywords: ['JavaScript', 'Frontend'],
  is_featured: true,
});
```

## Type Definitions (`skillBank.ts`)

### Enums

- `ContentFocusType` - Types of content focus (technical, leadership, results, etc.)
- `SkillCategory` - Skill categories (technical, soft, transferable, etc.)
- `SkillLevel` - Skill levels (beginner, intermediate, advanced, expert)
- `ContentSource` - Content sources (manual, extracted, generated, imported)
- `ExperienceType` - Experience types (full_time, part_time, contract, etc.)

### Core Interfaces

#### `SkillBankResponse`

Complete skill bank data structure returned by the API:

```typescript
interface SkillBankResponse {
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
  // ... content variations and metadata
}
```

#### `EnhancedSkill`

Detailed skill information with metadata:

```typescript
interface EnhancedSkill {
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
  // ... additional metadata
}
```

#### Request Models

- `EnhancedSkillRequest` - For creating/updating skills
- `SkillUpdateRequest` - For partial skill updates
- `SummaryVariationRequest` - For creating summary variations
- `ExperienceEntryRequest` - For creating work experience entries
- And more...

## Error Handling

The service includes comprehensive error handling:

```typescript
try {
  const skillBank = await skillBankApiService.getSkillBank(userId);
  // Handle success
} catch (error) {
  if (error instanceof Error) {
    console.error('Skill Bank API Error:', error.message);
    // Handle specific error types
  }
}
```

## React Integration

### Example Component

The `SkillBankExample.tsx` component demonstrates:

- Loading skill bank data
- Error handling and loading states
- CRUD operations (Create, Read, Update, Delete)
- Real-time updates after operations
- TypeScript integration

### Key Features

1. **Type Safety**: Full TypeScript support with comprehensive type definitions
2. **Error Handling**: Proper error handling with user-friendly messages
3. **Loading States**: Built-in loading and error state management
4. **API Consistency**: Matches backend API structure exactly
5. **Extensible**: Easy to add new operations or modify existing ones

### Usage in Components

```tsx
import React, { useState, useEffect } from 'react';
import { skillBankApiService } from '../../services/skillBankApi';
import type { SkillBankResponse } from '../../types';

const MySkillBankComponent: React.FC = () => {
  const [skillBank, setSkillBank] = useState<SkillBankResponse | null>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await skillBankApiService.getSkillBank('user-id');
        setSkillBank(data);
      } catch (error) {
        console.error('Failed to load skill bank:', error);
      }
    };

    loadData();
  }, []);

  // Render component...
};
```

## API Endpoint Mapping

The service maps to these backend endpoints:

- `GET /api/skill-bank/{user_id}` - Get skill bank
- `PUT /api/skill-bank/{user_id}` - Update skill bank
- `POST /api/skill-bank/{user_id}/skills` - Add skill
- `GET /api/skill-bank/{user_id}/skills` - Get skills
- `PUT /api/skill-bank/{user_id}/skills/{skill_id}` - Update skill
- `DELETE /api/skill-bank/{user_id}/skills/{skill_id}` - Delete skill
- `POST /api/skill-bank/{user_id}/summaries` - Add summary variation
- And more...

## Development Notes

1. **Date Handling**: All dates are handled as ISO strings in the API
2. **Enums**: Use regular imports (not type-only) for enums that are used as values
3. **Optional Fields**: Many fields are optional to support flexible data entry
4. **Validation**: Client-side validation should complement backend validation
5. **Caching**: Consider implementing caching for frequently accessed data

## Next Steps

1. Add React hooks for common operations (`useSkillBank`, `useSkills`, etc.)
2. Implement optimistic updates for better UX
3. Add form validation utilities
4. Create specialized components for different skill bank sections
5. Add tests for the service layer
