import { Component } from 'solid-js';
import Chat from './Chat';
import type { ChatMessage, ProgressState } from '../../../types';

interface ChatPageProps {
  messages: () => ChatMessage[];
  onMessageSend: (message: string) => void;
  isProcessing: () => boolean;
  progress: () => ProgressState;
}

const ChatPage: Component<ChatPageProps> = props => {
  return (
    <Chat
      messages={props.messages}
      onMessageSend={props.onMessageSend}
      isProcessing={props.isProcessing}
      progress={props.progress}
    />
  );
};

export default ChatPage;
