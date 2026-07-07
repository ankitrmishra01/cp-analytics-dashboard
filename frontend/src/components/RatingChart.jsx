import { useRef, useEffect } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale, LinearScale, PointElement, LineElement,
  Title, Tooltip, Legend, Filler
);

const GRID_COLOR = 'rgba(255, 255, 255, 0.04)';
const AXIS_COLOR = '#64748b';

function getRatingColor(rating) {
  if (!rating) return '#60a5fa';
  if (rating >= 2400) return '#ff0000';
  if (rating >= 2100) return '#ff8c00';
  if (rating >= 1900) return '#aa00aa';
  if (rating >= 1600) return '#0000ff';
  if (rating >= 1400) return '#03a89e';
  if (rating >= 1200) return '#008000';
  return '#808080';
}

function formatDate(ts) {
  return new Date(ts * 1000).toLocaleDateString('en-US', {
    month: 'short',
    year: '2-digit',
  });
}

export default function RatingChart({ ratingHistory }) {
  const chartRef = useRef(null);

  if (!ratingHistory || ratingHistory.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-500 text-sm">
        No rating history available.
      </div>
    );
  }

  const sorted = [...ratingHistory].sort((a, b) => a.time_seconds - b.time_seconds);
  const latest = sorted[sorted.length - 1];
  const ratingColor = getRatingColor(latest?.new_rating);

  const labels = sorted.map((p) => formatDate(p.time_seconds));
  const ratings = sorted.map((p) => p.new_rating);

  const data = {
    labels,
    datasets: [
      {
        label: 'Rating',
        data: ratings,
        borderColor: '#3b82f6',
        backgroundColor: (ctx) => {
          const chart = ctx.chart;
          const { ctx: canvas, chartArea } = chart;
          if (!chartArea) return 'rgba(59,130,246,0.1)';
          const gradient = canvas.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
          gradient.addColorStop(0, 'rgba(59, 130, 246, 0.25)');
          gradient.addColorStop(1, 'rgba(59, 130, 246, 0.0)');
          return gradient;
        },
        borderWidth: 2.5,
        pointRadius: sorted.length > 50 ? 2 : 4,
        pointHoverRadius: 6,
        pointBackgroundColor: '#3b82f6',
        pointBorderColor: '#fff',
        pointBorderWidth: 1.5,
        tension: 0.4,
        fill: true,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: 'index', intersect: false },
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: 'rgba(15, 23, 42, 0.95)',
        borderColor: 'rgba(59, 130, 246, 0.3)',
        borderWidth: 1,
        titleColor: '#94a3b8',
        bodyColor: '#e2e8f0',
        padding: 12,
        callbacks: {
          title: (items) => sorted[items[0].dataIndex]?.contest_name || '',
          label: (item) => ` Rating: ${item.raw}`,
          afterLabel: (item) => ` Rank: #${sorted[item.dataIndex]?.rank ?? '—'}`,
        },
      },
    },
    scales: {
      x: {
        grid: { color: GRID_COLOR },
        ticks: {
          color: AXIS_COLOR,
          maxTicksLimit: 10,
          font: { size: 11 },
        },
      },
      y: {
        grid: { color: GRID_COLOR },
        ticks: {
          color: AXIS_COLOR,
          font: { size: 11 },
        },
      },
    },
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <span className="text-xs text-slate-500 uppercase tracking-widest font-semibold">
          {sorted.length} contests
        </span>
        <span
          className="text-sm font-bold px-3 py-1 rounded-full"
          style={{
            color: ratingColor,
            background: `${ratingColor}18`,
            border: `1px solid ${ratingColor}40`,
          }}
        >
          Current: {latest?.new_rating ?? '—'}
        </span>
      </div>
      <div className="chart-container">
        <Line ref={chartRef} data={data} options={options} />
      </div>
    </div>
  );
}
