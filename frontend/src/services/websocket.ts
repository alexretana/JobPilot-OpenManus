import { createSignal } from 'solid-js';
import type { WebSocketMessage } from '../types';

export type MessageHandler = (message: WebSocketMessage) => void;

class WebSocketService {
  private ws: WebSocket | null = null;
  private handlers = new Set<MessageHandler>();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;

  private isConnectedSignal = createSignal(false);

  connect() {
    if (this.ws?.readyState === WebSocket.OPEN) return;

    const wsUrl = `ws://${window.location.hostname}:8080/ws`;
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.isConnectedSignal[1](true);
      this.reconnectAttempts = 0;
    };

    this.ws.onmessage = event => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        this.handlers.forEach(handler => handler(message));
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
      this.isConnectedSignal[1](false);
      this.attemptReconnect();
    };

    this.ws.onerror = error => {
      console.error('WebSocket error:', error);
      this.isConnectedSignal[1](false);
    };
  }

  private attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('Max reconnection attempts reached');
      return;
    }

    this.reconnectAttempts++;
    console.log(
      `Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`
    );

    setTimeout(() => {
      this.connect();
    }, this.reconnectDelay * this.reconnectAttempts);
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.isConnectedSignal[1](false);
  }

  sendMessage(message: string) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(
        JSON.stringify({
          type: 'message',
          content: message,
        })
      );
    } else {
      console.error('WebSocket is not connected');
    }
  }

  addMessageHandler(handler: MessageHandler) {
    this.handlers.add(handler);
    return () => this.handlers.delete(handler);
  }

  getIsConnected() {
    return this.isConnectedSignal[0];
  }
}

export const webSocketService = new WebSocketService();
