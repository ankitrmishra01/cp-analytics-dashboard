import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { Doughnut } from 'react-chartjs-2';

ChartJS.register(ArcElement, Tooltip, Legend);

const VERDICT_COLORS = {
  OK: '#22c55e',
  WRONG_ANSWER: '#ef4444',
  TIME_LIMIT_EXCEEDED: '#f59e0b',
  COMPILATION_ERROR: '#8b5cf6',
  RUNTIME_ERROR: '#ec4899',
  MEMORY_LIMIT_EXCEEDED: '#06b6d4',
  SKIPPED: '#64748b',
  CHALLENGED: '#f97316',
};

const VERDICT_LABELS = {
  OK: 'Accepted',
  WRONG_ANSWER: 'Wrong Answer',
  TIME_LIMIT_EXCEEDED: 'TLE',
  COMPILATION_ERROR: 'Compile Error',
  RUNTIME_ERROR: 'Runtime Error',
  MEMORY_LIMIT_EXCEEDED: 'MLE',
  SKIPPED: 'Skipped',
  CHALLENGED: 'Challenged',
};

function getColor(verdict) {
  return VERDICT_COLORS[verdict] || '#94a3b8';
}

function getLabel(verdict) {
  return VERDICT_LABELS[verdict] || verdict.replace(/_/g, ' ');
}

export default function VerdictChart({ verdictDistribution }) {
  if (!verdictDistribution || verdictDistribution.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-500 text-sm">
        No submission data available.
      </div>
    );
  }

  const total = verdictDistribution.reduce((s, v) => s + v.count, 0);
  const colors = verdictDistribution.map((v) => getColor(v.verdict));

  const data = {
    labels: verdictDistribution.map((v) => getLabel(v.verdict)),
    datasets: [
      {
        data: verdictDistribution.map((v) => v.count),
        backgroundColor: colors.map((c) => `${c}cc`),
        borderColor: colors,
        borderWidth: 2,
        hoverOffset: 8,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '68%',
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: 'rgba(15, 23, 42, 0.95)',
        borderColor: 'rgba(59,130,246,0.3)',
        borderWidth: 1,
        titleColor: '#94a3b8',
        bodyColor: '#e2e8f0',
        padding: 10,
        callbacks: {
          label: (item) => {
            const pct = ((item.raw / total) * 100).toFixed(1);
            return ` ${item.raw} (${pct}%)`;
          },
        },
      },
    },
  };

  return (
    <div>
      {/* Chart with centre label */}
      <div className="relative" style={{ height: 200 }}>
        <Doughnut data={data} options={options} />
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
          <span className="text-2xl font-bold text-white">{total}</span>
          <span className="text-xs text-slate-500">submissions</span>
        </div>
      </div>

      {/* Custom legend */}
      <div className="mt-4 space-y-1.5 max-h-40 overflow-y-auto pr-1">
        {verdictDistribution.map((v) => {
          const pct = ((v.count / total) * 100).toFixed(1);
          const color = getColor(v.verdict);
          return (
            <div key={v.verdict} className="flex items-center justify-between text-xs">
              <div className="flex items-center gap-2">
                <span
                  className="w-2.5 h-2.5 rounded-sm flex-shrink-0"
                  style={{ background: color }}
                />
                <span className="text-slate-300 truncate max-w-[130px]">
                  {getLabel(v.verdict)}
                </span>
              </div>
              <div className="flex items-center gap-2 text-slate-400 flex-shrink-0">
                <span>{v.count}</span>
                <span className="text-slate-600">({pct}%)</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
