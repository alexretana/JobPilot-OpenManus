import { Component, createSignal, onMount, onCleanup, Show } from 'solid-js';
import Header from './components/UI/Header';
import ChatPage from './components/pages/ChatPage';
import { JobDetailsModal } from './components/pages/JobSearchPage/JobsTab/JobDetailsModal';
import BrowserViewport from './components/UI/BrowserViewport';
import TimelineModal from './components/Timeline/TimelineModal';
import StatusPanel from './components/UI/StatusPanel';
import JobSearchManager from './components/pages/JobSearchPage';
import ResumeBuilderPage from './components/pages/ResumeBuilderPage';
import { webSocketService } from './services/websocket';
import type {
  ChatMessage,
  ActivityLogEntry,
  ProgressState,
  BrowserState,
  WebSocketMessage,
} from './types';

const App: Component = () => {
  // State management
  const [messages, setMessages] = createSignal<ChatMessage[]>([]);
  const [activities, setActivities] = createSignal<ActivityLogEntry[]>([]);
  const [isProcessing, setIsProcessing] = createSignal(false);
  const [progress, setProgress] = createSignal<ProgressState>({
    current: 0,
    total: 20,
    isActive: false,
  });
  const [browserState, setBrowserState] = createSignal<BrowserState>({
    status: 'Idle',
    url: 'No active browsing session',
    content: 'Waiting for browser activity...',
  });
  const [showTimelineModal, setShowTimelineModal] = createSignal(false);
  const [showStatusPanel, setShowStatusPanel] = createSignal(false);
  const [systemHealthy, setSystemHealthy] = createSignal(true);
  const [activeTab, setActiveTab] = createSignal<'chat' | 'job-search' | 'resume-builder'>('chat');
  const [selectedJobId, setSelectedJobId] = createSignal<string | null>(null);
  const [showJobModal, setShowJobModal] = createSignal(false);
  const [shouldCreateNewResume, setShouldCreateNewResume] = createSignal(false);

  let messageIdCounter = 0;
  let activityIdCounter = 0;

  // Helper functions
  const generateId = () => `msg_${++messageIdCounter}`;
  const generateActivityId = () => `activity_${++activityIdCounter}`;

  const addMessage = (type: ChatMessage['type'], content: string) => {
    const message: ChatMessage = {
      id: generateId(),
      type,
      content,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, message]);
  };

  const addActivity = (type: ActivityLogEntry['type'], message: string) => {
    const activity: ActivityLogEntry = {
      id: generateActivityId(),
      type,
      message,
      timestamp: new Date(),
    };
    setActivities(prev => {
      const newActivities = [...prev, activity];
      // Keep only last 20 activities to prevent memory issues
      return newActivities.slice(-20);
    });
  };

  const handleWebSocketMessage = (message: WebSocketMessage) => {
    switch (message.type) {
      case 'response':
        if (message.content) {
          addMessage('assistant', message.content);
        }
        setIsProcessing(false);
        setProgress(prev => ({ ...prev, isActive: false }));
        setBrowserState(prev => ({ ...prev, status: 'Idle' }));
        break;

      case 'progress':
        if (message.content) {
          addMessage('progress', message.content);
          addActivity('info', message.content);
        }
        setProgress({
          current: message.step || 0,
          total: message.total || 20,
          isActive: true,
        });
        break;

      case 'tool_start':
        if (message.tool) {
          addActivity('tool', `🔧 Using tool: ${message.tool}`);
          setBrowserState(prev => ({ ...prev, status: 'Active' }));
        }
        break;

      case 'tool_result':
        if (message.tool) {
          addActivity('tool', `✅ Tool ${message.tool} completed`);
          if (message.url) {
            setBrowserState(prev => ({ ...prev, url: message.url || prev.url }));
          }
          if (message.content) {
            setBrowserState(prev => ({ ...prev, content: message.content || prev.content }));
          }
        }
        break;

      case 'browser_action':
        if (message.action && message.url) {
          setBrowserState({
            status: 'Browsing',
            url: message.url,
            content: message.content || 'Loading page content...',
          });
          addActivity('browser', `🌐 Browser: ${message.action} - ${message.url}`);
        }
        break;

      case 'error':
        if (message.content) {
          addMessage('assistant', `❌ Error: ${message.content}`);
          addActivity('error', `❌ Error: ${message.content}`);
          setSystemHealthy(false);
        }
        setIsProcessing(false);
        setProgress(prev => ({ ...prev, isActive: false }));
        setBrowserState(prev => ({ ...prev, status: 'Idle' }));
        break;
    }
  };

  const handleMessageSend = (message: string) => {
    addMessage('user', message);
    setIsProcessing(true);
    setProgress({ current: 0, total: 20, isActive: true });
    setBrowserState(prev => ({ ...prev, status: 'Initializing' }));
    webSocketService.sendMessage(message);
    addActivity('info', '🤖 JobPilot agent started processing request');
  };

  const handleQuickAction = (query: string) => {
    if (!isProcessing()) {
      handleMessageSend(query);
    }
  };

  const handleJobSelect = (jobId: string) => {
    setSelectedJobId(jobId);
    setShowJobModal(true);
    addActivity('info', `📋 Opening job details: ${jobId}`);
  };

  const handleJobModalClose = () => {
    setShowJobModal(false);
    setSelectedJobId(null);
  };

  const handleJobSave = (jobId: string) => {
    // TODO: Implement job saving functionality
    console.log('Saved job:', jobId);
    addActivity('info', `💾 Saved job: ${jobId}`);
  };

  // Initialize WebSocket connection and handle cleanup
  onMount(() => {
    webSocketService.connect();
    const removeHandler = webSocketService.addMessageHandler(handleWebSocketMessage);

    // Add initial activity log entry
    addActivity('info', 'System initialized and ready');
    addActivity('info', '💬 Web interface loaded and connected');

    onCleanup(() => {
      removeHandler();
      webSocketService.disconnect();
    });
  });

  return (
    <div class='h-screen bg-base-200 flex flex-col'>
      <Header
        activities={activities}
        onShowTimeline={() => setShowTimelineModal(true)}
        onShowStatusPanel={() => setShowStatusPanel(true)}
        systemHealthy={() => systemHealthy() && webSocketService.getIsConnected()()}
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />

      <main class='flex-1 mx-2 p-2 min-h-0'>
        <Show when={activeTab() === 'chat'}>
          <div class='flex flex-col lg:flex-row gap-2 h-full'>
            {/* Chat Column */}
            <div class='flex-1 flex flex-col min-h-0'>
              <ChatPage
                messages={messages}
                onMessageSend={handleMessageSend}
                isProcessing={isProcessing}
                progress={progress}
              />
            </div>

            {/* Browser Viewport Column */}
            <div class='flex-1 min-h-0'>
              <BrowserViewport browserState={browserState} />
            </div>
          </div>
        </Show>

        <Show when={activeTab() === 'job-search'}>
          <div class='bg-base-200 rounded-lg p-2 h-full'>
            <JobSearchManager onJobSelect={handleJobSelect} onJobSave={handleJobSave} />
          </div>
        </Show>

        <Show when={activeTab() === 'resume-builder'}>
          <div class='bg-base-200 rounded-lg p-2 h-full'>
            <ResumeBuilderPage
              userId='demo-user-123'
              shouldCreateNewResume={shouldCreateNewResume()}
              onCreateNewHandled={() => setShouldCreateNewResume(false)}
              onProfileChange={profile => {
                console.log('Profile updated in main app:', profile);
                addActivity(
                  'info',
                  `👤 Profile updated: ${profile.first_name} ${profile.last_name}`
                );
              }}
            />
          </div>
        </Show>
      </main>

      {/* Job Details Modal */}
      <JobDetailsModal
        jobId={selectedJobId()}
        isOpen={showJobModal()}
        onClose={handleJobModalClose}
      />

      {/* Timeline Modal */}
      <TimelineModal
        activities={activities}
        isOpen={showTimelineModal}
        onClose={() => setShowTimelineModal(false)}
        userProfileId='demo-user-123' // TODO: Replace with actual user ID from auth
      />

      {/* Status Panel Drawer */}
      <StatusPanel
        onQuickAction={handleQuickAction}
        isProcessing={isProcessing}
        isOpen={showStatusPanel}
        onClose={() => setShowStatusPanel(false)}
      />

      {/* Mobile responsive adjustments */}
      <div class='lg:hidden'>{/* On mobile, stack vertically with better spacing */}</div>
    </div>
  );
};

export default App;
