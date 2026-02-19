import { useState, useEffect, useRef } from 'react';
import Sidebar from './components/Sidebar';
import ChatInterface from './components/ChatInterface';
import SystemPromptSelector from './components/SystemPromptSelector';
import { api } from './api';
import './App.css';

function App() {
  const [conversations, setConversations] = useState([]);
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [currentConversation, setCurrentConversation] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [promptConfig, setPromptConfig] = useState({ template_id: 'blank', system_prompt: '' });
  const [starterQuestions, setStarterQuestions] = useState([]);
  // Prevents the loadConversation useEffect from firing when we manually
  // set currentConversation during a starter-question stream (avoids race condition crash)
  const skipConvLoadRef = useRef(false);

  // Load conversations on mount
  useEffect(() => {
    loadConversations();
    loadStarterQuestions();
  }, []);

  // Load conversation details when selected
  useEffect(() => {
    if (currentConversationId) {
      if (skipConvLoadRef.current) {
        skipConvLoadRef.current = false; // consume the flag, skip this load
        return;
      }
      loadConversation(currentConversationId);
    }
  }, [currentConversationId]);

  const loadConversations = async () => {
    try {
      const convs = await api.listConversations();
      setConversations(convs);
    } catch (error) {
      console.error('Failed to load conversations:', error);
    }
  };

  const loadStarterQuestions = async () => {
    try {
      const qs = await api.listStarterQuestions();
      setStarterQuestions(qs);
    } catch (error) {
      console.error('Failed to load starter questions:', error);
    }
  };

  const loadConversation = async (id) => {
    try {
      const conv = await api.getConversation(id);
      setCurrentConversation(conv);
    } catch (error) {
      console.error('Failed to load conversation:', error);
    }
  };

  const handleNewConversation = async () => {
    try {
      const newConv = await api.createConversation({
        system_prompt: promptConfig.system_prompt,
        template_id: promptConfig.template_id,
      });
      setConversations([
        { id: newConv.id, created_at: newConv.created_at, message_count: 0 },
        ...conversations,
      ]);
      setCurrentConversationId(newConv.id);
    } catch (error) {
      console.error('Failed to create conversation:', error);
    }
  };

  const handleSelectConversation = (id) => {
    setCurrentConversationId(id);
  };

  // Core streaming helper — works with an explicit convId to avoid stale closure
  const _streamMessage = async (convId, content) => {
    // Optimistic user message
    const userMessage = { role: 'user', content };
    const assistantMessage = {
      role: 'assistant', stage1: null, stage2: null, stage3: null, metadata: null,
      loading: { stage1: false, stage2: false, stage3: false },
    };
    setCurrentConversation((prev) => ({
      ...prev,
      messages: prev ? [...prev.messages, userMessage, assistantMessage] : [userMessage, assistantMessage],
    }));

    await api.sendMessageStream(convId, content, (eventType, event) => {
      switch (eventType) {
        case 'stage1_start':
          setCurrentConversation((prev) => {
            if (!prev?.messages?.length) return prev;
            const msgs = [...prev.messages];
            const last = msgs[msgs.length - 1];
            if (!last?.loading) return prev;
            msgs[msgs.length - 1] = { ...last, loading: { ...last.loading, stage1: true } };
            return { ...prev, messages: msgs };
          });
          break;
        case 'stage1_complete':
          setCurrentConversation((prev) => {
            if (!prev?.messages?.length) return prev;
            const msgs = [...prev.messages];
            const last = msgs[msgs.length - 1];
            if (!last) return prev;
            msgs[msgs.length - 1] = { ...last, stage1: event.data, loading: { ...(last.loading || {}), stage1: false } };
            return { ...prev, messages: msgs };
          });
          break;
        case 'stage2_start':
          setCurrentConversation((prev) => {
            if (!prev?.messages?.length) return prev;
            const msgs = [...prev.messages];
            const last = msgs[msgs.length - 1];
            if (!last?.loading) return prev;
            msgs[msgs.length - 1] = { ...last, loading: { ...last.loading, stage2: true } };
            return { ...prev, messages: msgs };
          });
          break;
        case 'stage2_complete':
          setCurrentConversation((prev) => {
            if (!prev?.messages?.length) return prev;
            const msgs = [...prev.messages];
            const last = msgs[msgs.length - 1];
            if (!last) return prev;
            msgs[msgs.length - 1] = { ...last, stage2: event.data, metadata: event.metadata, loading: { ...(last.loading || {}), stage2: false } };
            return { ...prev, messages: msgs };
          });
          break;
        case 'stage3_start':
          setCurrentConversation((prev) => {
            if (!prev?.messages?.length) return prev;
            const msgs = [...prev.messages];
            const last = msgs[msgs.length - 1];
            if (!last?.loading) return prev;
            msgs[msgs.length - 1] = { ...last, loading: { ...last.loading, stage3: true } };
            return { ...prev, messages: msgs };
          });
          break;
        case 'stage3_complete':
          setCurrentConversation((prev) => {
            if (!prev?.messages?.length) return prev;
            const msgs = [...prev.messages];
            const last = msgs[msgs.length - 1];
            if (!last) return prev;
            msgs[msgs.length - 1] = { ...last, stage3: event.data, loading: { ...(last.loading || {}), stage3: false } };
            return { ...prev, messages: msgs };
          });
          break;
        case 'title_complete':
          loadConversations();
          break;
        case 'complete':
          loadConversations();
          setIsLoading(false);
          break;
        case 'error':
          console.error('Stream error:', event.message);
          setIsLoading(false);
          break;
        default:
          break;
      }
    });
  };

  const handleSendMessage = async (content) => {
    if (!currentConversationId || isLoading) return;
    setIsLoading(true);
    try {
      await _streamMessage(currentConversationId, content);
    } catch (error) {
      console.error('Failed to send message:', error);
      setCurrentConversation((prev) => ({
        ...prev,
        messages: prev.messages.slice(0, -2),
      }));
      setIsLoading(false);
    }
  };

  const handleStarterQuestion = async (question) => {
    if (isLoading) return;
    setIsLoading(true);
    try {
      // Fetch full question prompt
      const questionData = await api.getStarterQuestion(question.id);

      // Create conversation with the Fanvue Copilot template
      const newConv = await api.createConversation({
        template_id: question.template_id,
        system_prompt: '',
      });

      // Update UI state with new conversation
      setConversations((prev) => [
        { id: newConv.id, created_at: newConv.created_at, title: 'New Conversation', message_count: 0 },
        ...prev,
      ]);
      // Skip the loadConversation useEffect — we're about to stream into this conversation
      // and don't want the server fetch to race/overwrite our optimistic state
      skipConvLoadRef.current = true;
      setCurrentConversationId(newConv.id);
      setCurrentConversation({ ...newConv, messages: [] });
      setPromptConfig({ template_id: question.template_id, system_prompt: newConv.system_prompt || '' });

      // Stream the question to the new conversation
      await _streamMessage(newConv.id, questionData.prompt);
    } catch (error) {
      console.error('Failed to start starter question:', error);
      setIsLoading(false);
    }
  };

  return (
    <div className="app">
      <Sidebar
        conversations={conversations}
        currentConversationId={currentConversationId}
        onSelectConversation={handleSelectConversation}
        onNewConversation={handleNewConversation}
      />
      <div className="main-panel">
        <SystemPromptSelector
          onSelect={setPromptConfig}
          disabled={isLoading}
        />
        <ChatInterface
          conversation={currentConversation}
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
          starterQuestions={starterQuestions}
          onStarterQuestion={handleStarterQuestion}
        />
      </div>
    </div>
  );
}

export default App;
