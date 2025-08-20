import { Component, createSignal, onMount, Show } from 'solid-js';
import { ResumeService } from '../../../../../services/resumeService';

interface ResumePreviewProps {
  resumeId: string;
  userId: string;
  onEdit: () => void;
  onClose: () => void;
}

const ResumePreview: Component<ResumePreviewProps> = props => {
  const [resumeData, setResumeData] = createSignal<any>(null);
  const [loading, setLoading] = createSignal(true);
  const [error, setError] = createSignal<string | null>(null);
  const [generatingPDF, setGeneratingPDF] = createSignal(false);

  const loadResume = async () => {
    try {
      setLoading(true);
      setError(null);
      const resume = await ResumeService.getResume(props.resumeId, props.userId);
      setResumeData(resume);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load resume');
      console.error('Failed to load resume:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleGeneratePDF = async () => {
    try {
      setGeneratingPDF(true);
      const result = await ResumeService.generatePDF(
        props.resumeId,
        props.userId,
        'moderncv',
        `${resumeData()?.title || 'resume'}.pdf`
      );

      // The backend returns a mock response with download_url
      // In a real implementation, this would either:
      // 1. Return a blob/buffer to download directly, or
      // 2. Return a URL to download the file from

      // For now, show success message since PDF generation is mock
      if (result.message) {
        // Create a temporary success notification
        const successDiv = document.createElement('div');
        successDiv.className = 'toast toast-top toast-end z-50';
        successDiv.innerHTML = `
          <div class="alert alert-success">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <span>PDF export requested successfully!</span>
          </div>
        `;
        document.body.appendChild(successDiv);
        setTimeout(() => {
          document.body.removeChild(successDiv);
        }, 3000);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate PDF');
      console.error('Failed to generate PDF:', err);
    } finally {
      setGeneratingPDF(false);
    }
  };

  onMount(() => {
    loadResume();
  });

  return (
    <div class='h-full flex flex-col bg-white'>
      {/* Header */}
      <div class='bg-base-100 border-b px-6 py-4 flex justify-between items-center'>
        <div>
          <h2 class='text-2xl font-bold'>👁️ Resume Preview</h2>
          <p class='text-base-content/70'>
            {resumeData() ? resumeData().title : 'Loading resume...'}
          </p>
        </div>
        <div class='flex space-x-2'>
          <button class='btn btn-outline' onClick={props.onEdit} disabled={loading()}>
            ✏️ Edit
          </button>
          <button
            class='btn btn-primary'
            onClick={handleGeneratePDF}
            disabled={loading() || generatingPDF()}
          >
            {generatingPDF() ? (
              <>
                <span class='loading loading-spinner loading-sm'></span>
                Generating PDF...
              </>
            ) : (
              '📄 Download PDF'
            )}
          </button>
          <button class='btn btn-ghost' onClick={props.onClose}>
            ✕ Close
          </button>
        </div>
      </div>

      {/* Error Alert */}
      <Show when={error()}>
        <div class='alert alert-error mx-6 mt-4'>
          <svg class='w-6 h-6' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
            <path
              stroke-linecap='round'
              stroke-linejoin='round'
              stroke-width='2'
              d='M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 15.5c-.77.833.192 2.5 1.732 2.5z'
            ></path>
          </svg>
          <span>{error()}</span>
        </div>
      </Show>

      {/* Loading State */}
      <Show when={loading()}>
        <div class='flex-1 flex justify-center items-center'>
          <div class='text-center'>
            <span class='loading loading-spinner loading-lg'></span>
            <p class='mt-4 text-base-content/70'>Loading resume...</p>
          </div>
        </div>
      </Show>

      {/* Resume Content */}
      <Show when={!loading() && resumeData()}>
        <div class='flex-1 overflow-y-auto'>
          <div class='max-w-4xl mx-auto p-8'>
            {/* Resume Paper Simulation */}
            <div class='bg-white shadow-lg border rounded-lg p-12 space-y-8'>
              {/* Header with Contact Info */}
              <div class='text-center border-b pb-6'>
                <h1 class='text-3xl font-bold text-gray-900 mb-2'>
                  {resumeData()?.contact_info?.full_name || 'Full Name'}
                </h1>

                <div class='flex flex-wrap justify-center gap-4 text-gray-600 text-sm'>
                  {resumeData()?.contact_info?.email && (
                    <span>📧 {resumeData().contact_info.email}</span>
                  )}
                  {resumeData()?.contact_info?.phone && (
                    <span>📱 {resumeData().contact_info.phone}</span>
                  )}
                  {resumeData()?.contact_info?.location && (
                    <span>📍 {resumeData().contact_info.location}</span>
                  )}
                </div>

                <div class='flex flex-wrap justify-center gap-4 mt-2 text-gray-600 text-sm'>
                  {resumeData()?.contact_info?.linkedin_url && (
                    <a
                      href={resumeData().contact_info.linkedin_url}
                      class='text-blue-600 hover:underline'
                    >
                      🔗 LinkedIn
                    </a>
                  )}
                  {resumeData()?.contact_info?.github_url && (
                    <a
                      href={resumeData().contact_info.github_url}
                      class='text-blue-600 hover:underline'
                    >
                      💻 GitHub
                    </a>
                  )}
                  {resumeData()?.contact_info?.website_url && (
                    <a
                      href={resumeData().contact_info.website_url}
                      class='text-blue-600 hover:underline'
                    >
                      🌐 Portfolio
                    </a>
                  )}
                </div>
              </div>

              {/* Professional Summary */}
              <Show when={resumeData()?.summary}>
                <div>
                  <h2 class='text-xl font-semibold text-gray-900 mb-3 border-b border-gray-200 pb-1'>
                    Professional Summary
                  </h2>
                  <p class='text-gray-700 leading-relaxed'>{resumeData().summary}</p>
                </div>
              </Show>

              {/* Work Experience */}
              <Show when={resumeData()?.work_experience?.length > 0}>
                <div>
                  <h2 class='text-xl font-semibold text-gray-900 mb-3 border-b border-gray-200 pb-1'>
                    Professional Experience
                  </h2>
                  <div class='space-y-4'>
                    {resumeData().work_experience.map((job: any) => (
                      <div class='space-y-2'>
                        <div class='flex justify-between items-start'>
                          <div>
                            <h3 class='font-semibold text-gray-900'>{job.position}</h3>
                            <p class='text-gray-600'>{job.company}</p>
                          </div>
                          <span class='text-gray-500 text-sm'>
                            {job.start_date} - {job.end_date || 'Present'}
                          </span>
                        </div>
                        {job.description && <p class='text-gray-700'>{job.description}</p>}
                        {job.achievements?.length > 0 && (
                          <ul class='list-disc list-inside text-gray-700 space-y-1'>
                            {job.achievements.map((achievement: string) => (
                              <li>{achievement}</li>
                            ))}
                          </ul>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </Show>

              {/* Education */}
              <Show when={resumeData()?.education?.length > 0}>
                <div>
                  <h2 class='text-xl font-semibold text-gray-900 mb-3 border-b border-gray-200 pb-1'>
                    Education
                  </h2>
                  <div class='space-y-3'>
                    {resumeData().education.map((edu: any) => (
                      <div class='flex justify-between items-start'>
                        <div>
                          <h3 class='font-semibold text-gray-900'>{edu.degree}</h3>
                          <p class='text-gray-600'>{edu.institution}</p>
                          {edu.field_of_study && (
                            <p class='text-gray-500 text-sm'>{edu.field_of_study}</p>
                          )}
                        </div>
                        <span class='text-gray-500 text-sm'>{edu.graduation_date}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </Show>

              {/* Skills */}
              <Show when={resumeData()?.skills?.length > 0}>
                <div>
                  <h2 class='text-xl font-semibold text-gray-900 mb-3 border-b border-gray-200 pb-1'>
                    Skills
                  </h2>
                  <div class='flex flex-wrap gap-2'>
                    {resumeData().skills.map((skill: any) => (
                      <span class='px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm'>
                        {skill.name}
                      </span>
                    ))}
                  </div>
                </div>
              </Show>

              {/* Empty State */}
              <Show
                when={
                  !resumeData()?.summary &&
                  (!resumeData()?.work_experience || resumeData().work_experience.length === 0) &&
                  (!resumeData()?.education || resumeData().education.length === 0) &&
                  (!resumeData()?.skills || resumeData().skills.length === 0)
                }
              >
                <div class='text-center py-12 text-gray-500'>
                  <div class='text-4xl mb-4'>📝</div>
                  <p class='text-lg font-medium mb-2'>Resume Content Empty</p>
                  <p>Start by adding your professional information in the resume builder.</p>
                  <button class='btn btn-primary mt-4' onClick={props.onEdit}>
                    Edit Resume
                  </button>
                </div>
              </Show>
            </div>
          </div>
        </div>
      </Show>
    </div>
  );
};

export default ResumePreview;
