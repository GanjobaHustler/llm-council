import { useState, useEffect } from 'react';
import { api } from '../api';
import './SystemPromptSelector.css';

export default function SystemPromptSelector({ onSelect, disabled }) {
  const [templates, setTemplates] = useState([]);
  const [selectedId, setSelectedId] = useState('blank');
  const [customPrompt, setCustomPrompt] = useState('');
  const [showEditor, setShowEditor] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      const list = await api.listTemplates();
      setTemplates(list);
    } catch (e) {
      console.error('Failed to load templates:', e);
    }
  };

  const handleTemplateChange = async (e) => {
    const id = e.target.value;
    setSelectedId(id);

    if (id === 'blank') {
      setCustomPrompt('');
      setShowEditor(false);
      onSelect?.({ template_id: 'blank', system_prompt: '' });
      return;
    }

    // Load the full prompt text
    setLoading(true);
    try {
      const data = await api.getTemplate(id);
      setCustomPrompt(data.prompt);
      setShowEditor(true);
      onSelect?.({ template_id: id, system_prompt: data.prompt });
    } catch (e) {
      console.error('Failed to load template:', e);
    } finally {
      setLoading(false);
    }
  };

  const handlePromptEdit = (e) => {
    const text = e.target.value;
    setCustomPrompt(text);
    onSelect?.({ template_id: selectedId, system_prompt: text });
  };

  const toggleEditor = () => setShowEditor(!showEditor);

  return (
    <div className="system-prompt-selector">
      <div className="template-row">
        <label htmlFor="template-select">System Prompt:</label>
        <select
          id="template-select"
          value={selectedId}
          onChange={handleTemplateChange}
          disabled={disabled}
        >
          {templates.map((t) => (
            <option key={t.id} value={t.id}>
              {t.name}
            </option>
          ))}
          {templates.length === 0 && <option value="blank">Blank</option>}
        </select>
        {customPrompt && (
          <button
            className="toggle-editor-btn"
            onClick={toggleEditor}
            disabled={disabled}
            title={showEditor ? 'Hide prompt editor' : 'Show prompt editor'}
          >
            {showEditor ? '▲' : '▼'}
          </button>
        )}
      </div>

      {selectedId !== 'blank' && !showEditor && !loading && (
        <div className="template-description">
          {templates.find((t) => t.id === selectedId)?.description}
        </div>
      )}

      {loading && <div className="template-loading">Loading template...</div>}

      {showEditor && !loading && (
        <textarea
          className="prompt-editor"
          value={customPrompt}
          onChange={handlePromptEdit}
          disabled={disabled}
          rows={6}
          placeholder="Enter a custom system prompt..."
        />
      )}
    </div>
  );
}
