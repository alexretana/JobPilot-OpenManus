import { Component, createSignal, Show, createEffect } from 'solid-js';
import ResumeList from './views/ResumeList';
import ResumeBuilder from './views/ResumeBuilder';
import ResumePreview from './views/ResumePreview';

interface ResumeDashboardProps {
  userId: string;
  shouldCreateNew?: boolean;
  onCreateNewHandled?: () => void;
}

type ViewMode = 'list' | 'builder' | 'preview';

const ResumeDashboard: Component<ResumeDashboardProps> = props => {
  const [currentView, setCurrentView] = createSignal<ViewMode>('list');
  const [selectedResumeId, setSelectedResumeId] = createSignal<string | null>(null);

  // Handle auto-create new resume from profile
  createEffect(() => {
    if (props.shouldCreateNew) {
      showResumeBuilder(); // Start building a new resume
      props.onCreateNewHandled?.(); // Notify that we handled the signal
    }
  });

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
    <div class='container mx-auto h-full'>
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
