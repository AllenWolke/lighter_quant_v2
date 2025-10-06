import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { WebSocketMessage, MarketDataMessage, TradeMessage, OrderMessage, PositionMessage, NotificationMessage } from '../types';

interface WebSocketState {
  // 连接状态
  isConnected: boolean;
  isConnecting: boolean;
  connectionError: string | null;
  
  // WebSocket实例
  socket: WebSocket | null;
  
  // 订阅管理
  subscriptions: Set<string>;
  
  // 连接方法
  connect: () => Promise<void>;
  disconnect: () => void;
  reconnect: () => Promise<void>;
  
  // 订阅方法
  subscribe: (channel: string) => void;
  unsubscribe: (channel: string) => void;
  
  // 消息处理
  sendMessage: (message: WebSocketMessage) => void;
  onMessage: (callback: (message: WebSocketMessage) => void) => void;
  
  // 状态更新
  setConnected: (connected: boolean) => void;
  setConnecting: (connecting: boolean) => void;
  setError: (error: string | null) => void;
}

export const useWebSocketStore = create<WebSocketState>()(
  devtools(
    (set, get) => {
      let messageCallbacks: ((message: WebSocketMessage) => void)[] = [];
      
      const connect = async () => {
        const { isConnected, isConnecting } = get();
        
        if (isConnected || isConnecting) {
          return;
        }
        
        try {
          set({ isConnecting: true, connectionError: null });
          
          const wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws';
          const socket = new WebSocket(wsUrl);
          
          socket.onopen = () => {
            console.log('WebSocket连接已建立');
            set({
              isConnected: true,
              isConnecting: false,
              connectionError: null,
              socket,
            });
            
            // 重新订阅之前的频道
            const { subscriptions } = get();
            subscriptions.forEach(channel => {
              socket.send(JSON.stringify({
                type: 'subscribe',
                channel,
              }));
            });
          };
          
          socket.onclose = () => {
            console.log('WebSocket连接已关闭');
            set({
              isConnected: false,
              isConnecting: false,
              socket: null,
            });
          };
          
          socket.onerror = (error) => {
            console.error('WebSocket连接错误:', error);
            set({
              isConnected: false,
              isConnecting: false,
              connectionError: 'WebSocket连接失败',
              socket: null,
            });
          };
          
          socket.onmessage = (event) => {
            try {
              const message: WebSocketMessage = JSON.parse(event.data);
              
              // 调用所有注册的回调函数
              messageCallbacks.forEach(callback => {
                try {
                  callback(message);
                } catch (error) {
                  console.error('消息回调错误:', error);
                }
              });
            } catch (error) {
              console.error('WebSocket消息解析错误:', error);
            }
          };
          
        } catch (error) {
          console.error('WebSocket连接异常:', error);
          set({
            isConnected: false,
            isConnecting: false,
            connectionError: 'WebSocket连接异常',
            socket: null,
          });
        }
      };
      
      const disconnect = () => {
        const { socket } = get();
        
        if (socket) {
          socket.close();
        }
        
        set({
          isConnected: false,
          isConnecting: false,
          socket: null,
          connectionError: null,
        });
      };
      
      const reconnect = async () => {
        disconnect();
        await new Promise(resolve => setTimeout(resolve, 1000));
        await connect();
      };
      
      const subscribe = (channel: string) => {
        const { socket, subscriptions } = get();
        
        if (socket && socket.readyState === WebSocket.OPEN) {
          socket.send(JSON.stringify({
            type: 'subscribe',
            channel,
          }));
        }
        
        set({
          subscriptions: new Set([...subscriptions, channel])
        });
      };
      
      const unsubscribe = (channel: string) => {
        const { socket, subscriptions } = get();
        
        if (socket && socket.readyState === WebSocket.OPEN) {
          socket.send(JSON.stringify({
            type: 'unsubscribe',
            channel,
          }));
        }
        
        const newSubscriptions = new Set(subscriptions);
        newSubscriptions.delete(channel);
        set({ subscriptions: newSubscriptions });
      };
      
      const sendMessage = (message: WebSocketMessage) => {
        const { socket } = get();
        
        if (socket && socket.readyState === WebSocket.OPEN) {
          socket.send(JSON.stringify(message));
        } else {
          console.warn('WebSocket未连接，无法发送消息');
        }
      };
      
      const onMessage = (callback: (message: WebSocketMessage) => void) => {
        messageCallbacks.push(callback);
        
        // 返回取消订阅函数
        return () => {
          messageCallbacks = messageCallbacks.filter(cb => cb !== callback);
        };
      };
      
      return {
        isConnected: false,
        isConnecting: false,
        connectionError: null,
        socket: null,
        subscriptions: new Set(),
        
        connect,
        disconnect,
        reconnect,
        subscribe,
        unsubscribe,
        sendMessage,
        onMessage,
        
        setConnected: (connected) => set({ isConnected: connected }),
        setConnecting: (connecting) => set({ isConnecting: connecting }),
        setError: (error) => set({ connectionError: error }),
      };
    },
    {
      name: 'websocket-store',
    }
  )
);
