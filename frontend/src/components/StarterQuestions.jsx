import './StarterQuestions.css';

const SEVERITY_COLORS = {
  'P0-FIRE':   '#dc2626',
  'P1-URGENT': '#ea580c',
  'P2-NORMAL': '#ca8a04',
  'P3-LOW':    '#16a34a',
};

export default function StarterQuestions({ questions, onSelect, disabled }) {
  if (!questions || questions.length === 0) return null;

  return (
    <div className="starter-questions">
      <div className="starter-questions-header">
        <span className="starter-icon">⚡</span>
        <span>Fanvue Engineering Sessions</span>
        <span className="starter-subtext">— click to load a pre-built council question</span>
      </div>
      <div className="starter-grid">
        {questions.map((q) => (
          <button
            key={q.id}
            className="starter-card"
            onClick={() => !disabled && onSelect(q)}
            disabled={disabled}
          >
            <div className="starter-card-header">
              <span
                className="severity-badge"
                style={{ color: SEVERITY_COLORS[q.severity] || '#888' }}
              >
                {q.severity}
              </span>
              <span className="domain-badge">{q.domain}</span>
            </div>
            <div className="starter-card-title">{q.title}</div>
            <div className="starter-card-preview">{q.preview}</div>
          </button>
        ))}
      </div>
    </div>
  );
}
