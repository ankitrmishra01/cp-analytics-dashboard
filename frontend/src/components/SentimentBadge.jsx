import { Info } from 'lucide-react';

const SENTIMENT_CONFIG = {
  positive: {
    emoji: '😊',
    label: 'Positive',
    color: '#22c55e',
    bg: 'rgba(34,197,94,0.1)',
    border: 'rgba(34,197,94,0.3)',
    description: 'The community felt good about this contest!',
  },
  neutral: {
    emoji: '😐',
    label: 'Neutral',
    color: '#f59e0b',
    bg: 'rgba(245,158,11,0.1)',
    border: 'rgba(245,158,11,0.3)',
    description: 'Mixed feelings in the community.',
  },
  negative: {
    emoji: '😞',
    label: 'Negative',
    color: '#ef4444',
    bg: 'rgba(239,68,68,0.1)',
    border: 'rgba(239,68,68,0.3)',
    description: 'The community wasn\'t too happy about this one.',
  },
};

function ScoreGauge({ score }) {
  // Map score from [-1, 1] to [0, 100]
  const pct = Math.round(((score + 1) / 2) * 100);

  let color = '#f59e0b';
  if (score >= 0.05) color = '#22c55e';
  else if (score <= -0.05) color = '#ef4444';

  return (
    <div className="mt-3">
      <div className="flex justify-between text-xs text-slate-500 mb-1">
        <span>Negative</span>
        <span>Positive</span>
      </div>
      <div className="relative h-2 bg-slate-700/50 rounded-full overflow-hidden">
        {/* Track gradient */}
        <div
          className="absolute inset-0 rounded-full opacity-20"
          style={{
            background:
              'linear-gradient(to right, #ef4444, #f59e0b 50%, #22c55e)',
          }}
        />
        {/* Indicator */}
        <div
          className="absolute top-0 h-full w-1 rounded-full -translate-x-1/2 transition-all duration-500"
          style={{ left: `${pct}%`, background: color }}
        />
      </div>
      <div className="text-center mt-1">
        <span className="text-xs font-mono" style={{ color }}>
          {score >= 0 ? '+' : ''}{score.toFixed(3)}
        </span>
      </div>
    </div>
  );
}

export default function SentimentBadge({ sentiment }) {
  if (!sentiment || !sentiment.available) {
    return (
      <div className="flex flex-col items-center justify-center py-6 text-center gap-3">
        <Info className="w-8 h-8 text-slate-600" />
        <div>
          <p className="text-slate-400 font-medium text-sm">No Sentiment Data</p>
          <p className="text-slate-600 text-xs mt-1">
            {sentiment?.contest_name
              ? `No blog comments found for "${sentiment.contest_name}"`
              : 'No recent contest data available'}
          </p>
        </div>
      </div>
    );
  }

  const config = SENTIMENT_CONFIG[sentiment.label] || SENTIMENT_CONFIG.neutral;
  const contestDisplay =
    sentiment.contest_name && sentiment.contest_name.length > 40
      ? sentiment.contest_name.slice(0, 40) + '…'
      : sentiment.contest_name;

  return (
    <div className="flex flex-col gap-3">
      {/* Contest name */}
      <p
        className="text-xs text-slate-500 truncate"
        title={sentiment.contest_name}
      >
        📋 {contestDisplay}
      </p>

      {/* Badge */}
      <div
        className="flex items-center gap-3 p-3 rounded-xl border"
        style={{
          background: config.bg,
          borderColor: config.border,
        }}
      >
        <span className="text-3xl">{config.emoji}</span>
        <div>
          <p
            className="text-lg font-bold leading-none"
            style={{ color: config.color }}
          >
            {config.label}
          </p>
          <p className="text-xs text-slate-400 mt-0.5">{config.description}</p>
        </div>
      </div>

      {/* Score gauge */}
      <ScoreGauge score={sentiment.compound_score} />

      {/* Footer */}
      <p className="text-xs text-slate-600 text-center">
        Based on {sentiment.comment_count} comments · VADER + TextBlob NLP
      </p>
    </div>
  );
}
