import { Component, createSignal, onMount, onCleanup } from 'solid-js';
import Header from './components/Header';
import Chat from './components/Chat';
import BrowserViewport from './components/BrowserViewport';
import ActivityLog from './components/ActivityLog';
import StatusPanel from './components/StatusPanel';
import { webSocketService } from './services/websocket';
import type { ChatMessage, ActivityLogEntry, ProgressState, BrowserState, WebSocketMessage } from './types';

const App: Component = () => {
  // State management
  const [messages, setMessages] = createSignal<ChatMessage[]>([]);
  const [activities, setActivities] = createSignal<ActivityLogEntry[]>([]);
  const [isProcessing, setIsProcessing] = createSignal(false);
  const [progress, setProgress] = createSignal<ProgressState>({ current: 0, total: 20, isActive: false });
  const [browserState, setBrowserState] = createSignal<BrowserState>({
    status: 'Idle',
    url: 'No active browsing session',
    content: 'Waiting for browser activity...'
  });

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
      timestamp: new Date()
    };
    setMessages(prev => [...prev, message]);
  };

  const addActivity = (type: ActivityLogEntry['type'], message: string) => {
    const activity: ActivityLogEntry = {
      id: generateActivityId(),
      type,
      message,
      timestamp: new Date()
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
          isActive: true
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
            content: message.content || 'Loading page content...'
          });
          addActivity('browser', `🌐 Browser: ${message.action} - ${message.url}`);
        }
        break;

      case 'error':
        if (message.content) {
          addMessage('assistant', `❌ Error: ${message.content}`);
          addActivity('error', `❌ Error: ${message.content}`);
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
    <div class="min-h-screen bg-base-200" data-theme="corporate">
      <Header />
      
      <main class="container mx-auto p-4 h-[calc(100vh-80px)]">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 h-full">
          {/* Left Column - Chat */}
          <div class="lg:col-span-1 flex flex-col min-h-0">
            <div class="flex-1 min-h-0 mb-4">
              <Chat 
                messages={messages}
                onMessageSend={handleMessageSend}
                isProcessing={isProcessing}
                progress={progress}
              />
            </div>
            <div class="h-80">
              <ActivityLog activities={activities} />
            </div>
          </div>
          
          {/* Middle Column - Browser Viewport */}
          <div class="lg:col-span-1 min-h-0">
            <BrowserViewport browserState={browserState} />
          </div>
          
          {/* Right Column - Status Panel */}
          <div class="lg:col-span-1 min-h-0">
            <StatusPanel 
              onQuickAction={handleQuickAction}
              isProcessing={isProcessing}
            />
          </div>
        </div>
      </main>
      
      {/* Mobile responsive adjustments */}
      <div class="lg:hidden">
        {/* On mobile, stack vertically with better spacing */}
      </div>
    </div>
  );
};

export default App;
