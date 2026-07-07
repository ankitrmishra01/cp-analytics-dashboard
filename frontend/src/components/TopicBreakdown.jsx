import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const GRID_COLOR = 'rgba(255,255,255,0.04)';
const AXIS_COLOR = '#64748b';

// Generate a vibrant colour palette for the bars
function generateColors(n) {
  const palette = [
    '#3b82f6', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b',
    '#ef4444', '#ec4899', '#14b8a6', '#f97316', '#84cc16',
    '#6366f1', '#0ea5e9', '#a855f7', '#22c55e', '#fb923c',
  ];
  return Array.from({ length: n }, (_, i) => palette[i % palette.length]);
}

export default function TopicBreakdown({ tagDistribution }) {
  if (!tagDistribution || tagDistribution.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-500 text-sm">
        No tag data available.
      </div>
    );
  }

  const top15 = tagDistribution.slice(0, 15);
  const colors = generateColors(top15.length);

  const data = {
    labels: top15.map((t) => t.tag),
    datasets: [
      {
        label: 'Problems Solved',
        data: top15.map((t) => t.count),
        backgroundColor: colors.map((c) => `${c}cc`),
        borderColor: colors,
        borderWidth: 1.5,
        borderRadius: 6,
        borderSkipped: false,
      },
    ],
  };

  const options = {
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
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
          label: (item) => ` ${item.raw} problems solved`,
        },
      },
    },
    scales: {
      x: {
        grid: { color: GRID_COLOR },
        ticks: { color: AXIS_COLOR, font: { size: 11 } },
      },
      y: {
        grid: { display: false },
        ticks: {
          color: '#cbd5e1',
          font: { size: 11 },
          crossAlign: 'far',
        },
      },
    },
  };

  // Dynamic height based on number of bars
  const chartHeight = Math.max(220, top15.length * 30);

  return (
    <div style={{ height: chartHeight }}>
      <Bar data={data} options={options} />
    </div>
  );
}
