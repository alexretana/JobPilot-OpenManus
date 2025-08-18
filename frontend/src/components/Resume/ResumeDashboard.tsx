import { Component, createSignal, Show } from 'solid-js';
import ResumeList from './ResumeList';
import ResumeBuilder from './ResumeBuilder';
import ResumePreview from './ResumePreview';

interface ResumeDashboardProps {
  userId: string;
}

type ViewMode = 'list' | 'builder' | 'preview';

const ResumeDashboard: Component<ResumeDashboardProps> = props => {
  const [currentView, setCurrentView] = createSignal<ViewMode>('list');
  const [selectedResumeId, setSelectedResumeId] = createSignal<string | null>(null);

  const showResumeList = () => {
    setCurrentView('list');
    setSelectedResumeId(null);
  };

  const showResumeBuilder = (resumeId?: string) => {
    setCurrentView('builder');
    setSelectedResumeId(resumeId || null);
  };

  const showResumePreview = (resumeId: string) => {
    setCurrentView('preview');
    setSelectedResumeId(resumeId);
  };

  const handleSaveResume = (resumeId: string) => {
    // After saving, show the preview
    showResumePreview(resumeId);
  };

  return (
    <div class='h-full'>
      {/* Resume List View */}
      <Show when={currentView() === 'list'}>
        <ResumeList
          userId={props.userId}
          onCreateNew={() => showResumeBuilder()}
          onEditResume={resumeId => showResumeBuilder(resumeId)}
          onViewResume={resumeId => showResumePreview(resumeId)}
        />
      </Show>

      {/* Resume Builder View */}
      <Show when={currentView() === 'builder'}>
        <ResumeBuilder
          resumeId={selectedResumeId() || undefined}
          userId={props.userId}
          onSave={handleSaveResume}
          onCancel={showResumeList}
        />
      </Show>

      {/* Resume Preview View */}
      <Show when={currentView() === 'preview' && selectedResumeId()}>
        <ResumePreview
          resumeId={selectedResumeId()!}
          userId={props.userId}
          onEdit={() => showResumeBuilder(selectedResumeId()!)}
          onClose={showResumeList}
        />
      </Show>
    </div>
  );
};

export default ResumeDashboard;
