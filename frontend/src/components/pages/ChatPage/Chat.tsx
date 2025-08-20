import { Component, createSignal, createEffect, For } from 'solid-js';
import type { ChatMessage, ProgressState } from '../../../types';
import { webSocketService } from '../../../services/websocket';

interface ChatProps {
  messages: () => ChatMessage[];
  onMessageSend: (message: string) => void;
  isProcessing: () => boolean;
  progress: () => ProgressState;
}

const Chat: Component<ChatProps> = props => {
  const [inputMessage, setInputMessage] = createSignal('');
  let messagesContainer: HTMLDivElement | undefined;
  let messageInput: HTMLTextAreaElement | undefined;

  createEffect(() => {
    // Auto-scroll to bottom when new messages arrive
    if (messagesContainer) {
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
  });

  const sendMessage = () => {
    const message = inputMessage().trim();
    if (message && !props.isProcessing()) {
      props.onMessageSend(message);
      setInputMessage('');
    }
  };

  const handleKeyPress = (e: KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey && !props.isProcessing()) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatMessage = (content: string) => {
    // Format markdown-like content
    let formatted = content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>');

    // Format job listings
    formatted = formatted.replace(
      /(\d+\.)\s+(.*?)\s+-\s+(.*?)\s+-\s+(.*?)\n/g,
      '<div class="bg-base-200 p-2 my-2 rounded-lg border-l-4 border-l-success">' +
        '<strong>$2</strong><br>' +
        '<span class="text-base-content/70">$3</span><br>' +
        '<a href="$4" target="_blank" class="link link-primary">View Job</a>' +
        '</div>'
    );

    // Format URLs as links
    formatted = formatted.replace(
      /https?:\/\/([-\w\.])+(:\d+)?(\/([[\w\/_\.])*(\?[^\s]*)?)?/g,
      '<a href="$&" target="_blank" class="link link-primary">$&</a>'
    );

    return formatted;
  };

  return (
    <div class='card bg-base-100 shadow-xl h-full flex flex-col'>
      <div class='card-header bg-ai-color-gradient text-white p-2 rounded-t-xl'>
        <div class='flex justify-between items-center'>
          <div class='flex items-center space-x-2'>
            <span class='text-xl'>💬</span>
            <h2 class='card-title'>Chat with JobPilot Agent</h2>
          </div>
          <div class='flex items-center space-x-2'>
            <div
              class={`badge ${
                webSocketService.getIsConnected()() ? 'badge-success' : 'badge-error'
              }`}
            >
              {webSocketService.getIsConnected()() ? 'Connected' : 'Disconnected'}
            </div>
          </div>
        </div>
        {props.progress().isActive && (
          <div class='mt-2'>
            <div class='flex justify-between text-sm opacity-90'>
              <span>Processing...</span>
              <span>
                {props.progress().current}/{props.progress().total}
              </span>
            </div>
            <progress
              class='progress progress-secondary w-full mt-1'
              value={props.progress().current}
              max={props.progress().total}
            ></progress>
          </div>
        )}
      </div>

      <div
        ref={messagesContainer}
        class='flex-1 p-2 overflow-y-auto scrollbar-thin space-y-2 min-h-0'
      >
        {props.messages().length === 0 && (
          <div class='assistant-message chat-message'>
            <div class='flex items-start space-x-2'>
              <span class='text-xl'>👋</span>
              <div>
                <p>
                  Hello! I'm your transparent JobPilot AI assistant. I can help you find job
                  opportunities, analyze market trends, and optimize your applications.
                </p>
                <br />
                <div class='text-sm'>
                  <strong>🔍 What makes me transparent:</strong>
                  <br />
                  • You'll see every website I visit in real-time
                  <br />
                  • All my actions and tool usage are logged
                  <br />
                  • My reasoning process is fully visible
                  <br />
                  <br />
                  Try asking: "Show me Python developer jobs with 5 years experience in data
                  science"
                </div>
              </div>
            </div>
          </div>
        )}

        <For each={props.messages()}>
          {message => (
            <div
              class={`chat-message ${
                message.type === 'user'
                  ? 'user-message'
                  : message.type === 'progress'
                  ? 'progress-message'
                  : 'assistant-message'
              }`}
            >
              {message.type === 'progress' && (
                <div class='flex items-center space-x-2'>
                  <span class='loading loading-spinner loading-xs'></span>
                  <span innerHTML={`🔄 ${message.content}`}></span>
                </div>
              )}
              {message.type !== 'progress' && (
                <div innerHTML={formatMessage(message.content)}></div>
              )}
            </div>
          )}
        </For>
      </div>

      <div class='card-footer p-2 border-t border-base-200 space-y-2'>
        <textarea
          ref={messageInput}
          class='textarea textarea-bordered w-full resize-none'
          rows='3'
          placeholder='Ask about job opportunities... You can type multiple lines here.'
          value={inputMessage()}
          onInput={e => setInputMessage(e.currentTarget.value)}
          onKeyPress={handleKeyPress}
          disabled={props.isProcessing()}
        ></textarea>
        <div class='flex justify-end'>
          <button
            class='btn btn-primary'
            onClick={sendMessage}
            disabled={props.isProcessing() || !inputMessage().trim()}
          >
            {props.isProcessing() ? (
              <>
                <span class='loading loading-spinner loading-sm mr-2'></span>
                Processing...
              </>
            ) : (
              <>
                <svg class='w-4 h-4 mr-2' fill='none' stroke='currentColor' viewBox='0 0 24 24'>
                  <path
                    stroke-linecap='round'
                    stroke-linejoin='round'
                    stroke-width='2'
                    d='M12 19l9 2-9-18-9 18 9-2zm0 0v-8'
                  />
                </svg>
                Send Message
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Chat;
