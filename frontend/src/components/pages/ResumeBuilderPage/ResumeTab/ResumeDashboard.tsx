import { Component, createSignal, Show } from 'solid-js';
import { ResumeList, ResumeBuilder, ResumePreview } from './index';

interface ResumeDashboardProps {
  userId: string;
  shouldCreateNew?: boolean;
  onCreateNewHandled?: () => void;
}

type ResumeView = 'list' | 'builder' | 'preview';

const ResumeDashboard: Component<ResumeDashboardProps> = props => {
  const [currentView, setCurrentView] = createSignal<ResumeView>('list');
  const [selectedResumeId, setSelectedResumeId] = createSignal<string | null>(null);

  // Handle external signal to create new resume
  if (props.shouldCreateNew) {
    setCurrentView('builder');
    setSelectedResumeId(null);
    props.onCreateNewHandled?.();
  }

  const handleCreateNew = () => {
    setSelectedResumeId(null);
    setCurrentView('builder');
  };

  const handleEditResume = (resumeId: string) => {
    setSelectedResumeId(resumeId);
    setCurrentView('builder');
  };

  const handleViewResume = (resumeId: string) => {
    setSelectedResumeId(resumeId);
    setCurrentView('preview');
  };

  const handleBackToList = () => {
    setCurrentView('list');
    setSelectedResumeId(null);
  };

  const handleResumeSaved = (resumeId: string) => {
    setSelectedResumeId(resumeId);
    setCurrentView('preview');
  };

  return (
    <div class='h-full flex flex-col'>
      <Show when={currentView() === 'list'}>
        <ResumeList
          userId={props.userId}
          onCreateNew={handleCreateNew}
          onEditResume={handleEditResume}
          onViewResume={handleViewResume}
        />
      </Show>

      <Show when={currentView() === 'builder'}>
        <ResumeBuilder
          resumeId={selectedResumeId() || undefined}
          userId={props.userId}
          onSave={handleResumeSaved}
          onCancel={handleBackToList}
        />
      </Show>

      <Show when={currentView() === 'preview'}>
        <ResumePreview
          resumeId={selectedResumeId()!}
          userId={props.userId}
          onEdit={() => setCurrentView('builder')}
          onClose={handleBackToList}
        />
      </Show>
    </div>
  );
};

export default ResumeDashboard;
