import React, { useState, useEffect } from 'react';
import { skillBankApiService } from '../../services/skillBankApi';
import type {
  SkillBankResponse,
  EnhancedSkill,
  EnhancedSkillRequest,
  SummaryVariationRequest,
} from '../../types';
import { SkillCategory, SkillLevel } from '../../types';

interface SkillBankExampleProps {
  userId: string;
}

/**
 * Example component demonstrating Skill Bank API usage
 * This component shows basic CRUD operations for skills and summary variations
 */
export const SkillBankExample: React.FC<SkillBankExampleProps> = ({ userId }) => {
  const [skillBank, setSkillBank] = useState<SkillBankResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load skill bank on component mount
  useEffect(() => {
    loadSkillBank();
  }, [userId]);

  const loadSkillBank = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await skillBankApiService.getSkillBank(userId);
      setSkillBank(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load skill bank');
    } finally {
      setLoading(false);
    }
  };

  const addSampleSkill = async () => {
    try {
      const skillRequest: EnhancedSkillRequest = {
        name: 'React',
        level: SkillLevel.ADVANCED,
        category: SkillCategory.TECHNICAL,
        subcategory: 'Frontend Frameworks',
        years_experience: 3,
        proficiency_score: 0.85,
        description: 'Experienced in building modern React applications with hooks and context',
        keywords: ['JavaScript', 'Frontend', 'UI', 'Components'],
        is_featured: true,
        display_order: 1,
      };

      await skillBankApiService.addSkill(userId, skillRequest);
      await loadSkillBank(); // Reload to show the new skill
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add skill');
    }
  };

  const addSampleSummary = async () => {
    try {
      const summaryRequest: SummaryVariationRequest = {
        title: 'Technical Focus',
        content:
          'Senior software developer with expertise in React, Node.js, and cloud technologies. Passionate about building scalable web applications and leading technical teams.',
        tone: 'professional',
        length: 'standard',
        target_industries: ['Technology', 'Software'],
        target_roles: ['Senior Developer', 'Tech Lead'],
        keywords_emphasized: ['React', 'Node.js', 'Leadership'],
      };

      await skillBankApiService.addSummaryVariation(userId, summaryRequest);
      await loadSkillBank(); // Reload to show the new summary
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add summary variation');
    }
  };

  const deleteSkill = async (skillId: string) => {
    try {
      await skillBankApiService.deleteSkill(userId, skillId);
      await loadSkillBank(); // Reload to reflect the deletion
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete skill');
    }
  };

  if (loading) {
    return (
      <div className='p-6'>
        <div className='animate-pulse'>Loading skill bank...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className='p-6'>
        <div className='bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded'>
          Error: {error}
        </div>
        <button
          onClick={loadSkillBank}
          className='mt-4 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded'
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className='p-6 max-w-4xl mx-auto'>
      <div className='bg-white shadow-lg rounded-lg'>
        <div className='px-6 py-4 border-b border-gray-200'>
          <h1 className='text-2xl font-bold text-gray-900'>Skill Bank</h1>
          <p className='text-gray-600'>User ID: {userId}</p>
        </div>

        <div className='p-6'>
          {/* Action Buttons */}
          <div className='mb-6 space-x-4'>
            <button
              onClick={addSampleSkill}
              className='bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded'
            >
              Add Sample Skill
            </button>
            <button
              onClick={addSampleSummary}
              className='bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded'
            >
              Add Sample Summary
            </button>
            <button
              onClick={loadSkillBank}
              className='bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded'
            >
              Refresh
            </button>
          </div>

          {/* Default Summary */}
          {skillBank?.default_summary && (
            <div className='mb-6'>
              <h2 className='text-lg font-semibold text-gray-800 mb-2'>Default Summary</h2>
              <p className='text-gray-700 bg-gray-50 p-3 rounded'>{skillBank.default_summary}</p>
            </div>
          )}

          {/* Summary Variations */}
          {skillBank?.summary_variations && skillBank.summary_variations.length > 0 && (
            <div className='mb-6'>
              <h2 className='text-lg font-semibold text-gray-800 mb-2'>Summary Variations</h2>
              <div className='space-y-3'>
                {skillBank.summary_variations.map(variation => (
                  <div key={variation.id} className='bg-blue-50 p-3 rounded'>
                    <div className='font-medium text-blue-800'>{variation.title}</div>
                    <p className='text-gray-700 text-sm mt-1'>{variation.content}</p>
                    <div className='text-xs text-gray-500 mt-2'>
                      Focus: {variation.focus} | Tone: {variation.tone} | Length: {variation.length}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Skills by Category */}
          {skillBank?.skills && Object.keys(skillBank.skills).length > 0 ? (
            <div className='mb-6'>
              <h2 className='text-lg font-semibold text-gray-800 mb-2'>Skills</h2>
              {Object.entries(skillBank.skills).map(([category, skills]) => (
                <div key={category} className='mb-4'>
                  <h3 className='font-medium text-gray-700 mb-2'>{category}</h3>
                  <div className='grid gap-3 md:grid-cols-2 lg:grid-cols-3'>
                    {skills.map((skill: EnhancedSkill) => (
                      <div key={skill.id} className='bg-gray-50 p-3 rounded border'>
                        <div className='flex justify-between items-start'>
                          <div>
                            <div className='font-medium text-gray-800'>{skill.name}</div>
                            <div className='text-sm text-gray-600'>
                              Level: {skill.level} | Category: {skill.category}
                            </div>
                            {skill.years_experience && (
                              <div className='text-sm text-gray-600'>
                                Experience: {skill.years_experience} years
                              </div>
                            )}
                            {skill.proficiency_score && (
                              <div className='text-sm text-gray-600'>
                                Proficiency: {Math.round(skill.proficiency_score * 100)}%
                              </div>
                            )}
                            {skill.description && (
                              <p className='text-sm text-gray-700 mt-1'>{skill.description}</p>
                            )}
                            {skill.keywords.length > 0 && (
                              <div className='text-xs text-gray-500 mt-1'>
                                Keywords: {skill.keywords.join(', ')}
                              </div>
                            )}
                          </div>
                          <button
                            onClick={() => deleteSkill(skill.id)}
                            className='text-red-500 hover:text-red-700 text-sm font-medium'
                            title='Delete skill'
                          >
                            ×
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className='mb-6'>
              <h2 className='text-lg font-semibold text-gray-800 mb-2'>Skills</h2>
              <p className='text-gray-500'>
                No skills added yet. Click "Add Sample Skill" to get started.
              </p>
            </div>
          )}

          {/* Work Experience */}
          {skillBank?.work_experiences && skillBank.work_experiences.length > 0 && (
            <div className='mb-6'>
              <h2 className='text-lg font-semibold text-gray-800 mb-2'>Work Experience</h2>
              <div className='space-y-3'>
                {skillBank.work_experiences.map(experience => (
                  <div key={experience.id} className='bg-gray-50 p-3 rounded'>
                    <div className='font-medium text-gray-800'>
                      {experience.position} at {experience.company}
                    </div>
                    <div className='text-sm text-gray-600'>
                      {experience.start_date} -{' '}
                      {experience.is_current ? 'Present' : experience.end_date || 'Unknown'}
                      {experience.location && ` | ${experience.location}`}
                    </div>
                    {experience.default_description && (
                      <p className='text-sm text-gray-700 mt-1'>{experience.default_description}</p>
                    )}
                    {experience.technologies.length > 0 && (
                      <div className='text-xs text-gray-500 mt-1'>
                        Technologies: {experience.technologies.join(', ')}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Metadata */}
          <div className='text-xs text-gray-500 border-t pt-4'>
            <p>Created: {new Date(skillBank?.created_at || '').toLocaleString()}</p>
            <p>Updated: {new Date(skillBank?.updated_at || '').toLocaleString()}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SkillBankExample;
