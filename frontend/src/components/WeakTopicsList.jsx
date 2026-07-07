import { AlertTriangle, CheckCircle, TrendingUp } from 'lucide-react';

function AcceptRateBar({ rate }) {
  const pct = Math.round(rate * 100);
  let barColor = '#22c55e';
  if (pct < 30) barColor = '#ef4444';
  else if (pct < 60) barColor = '#f59e0b';

  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 bg-slate-700/50 rounded-full h-1.5 overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{ width: `${pct}%`, background: barColor }}
        />
      </div>
      <span
        className="text-xs font-semibold w-10 text-right"
        style={{ color: barColor }}
      >
        {pct}%
      </span>
    </div>
  );
}

export default function WeakTopicsList({ weakTopics }) {
  if (!weakTopics || weakTopics.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-10 text-center">
        <CheckCircle className="w-10 h-10 text-green-500 mb-3" />
        <p className="text-slate-300 font-medium">No significant weak topics found!</p>
        <p className="text-slate-500 text-sm mt-1">
          You need ≥3 unique problems attempted per topic to appear here.
        </p>
      </div>
    );
  }

  const top10 = weakTopics.slice(0, 10);

  return (
    <div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-slate-500 text-xs uppercase tracking-widest border-b border-slate-700/50">
              <th className="text-left py-2 pr-4 font-semibold">Topic</th>
              <th className="text-center py-2 px-2 font-semibold">Problems</th>
              <th className="text-center py-2 px-2 font-semibold">Solved</th>
              <th className="text-left py-2 pl-4 font-semibold w-40">Accept Rate</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-700/30">
            {top10.map((topic) => {
              const pct = Math.round(topic.accept_rate * 100);
              const isWeak = pct < 30;
              return (
                <tr
                  key={topic.tag}
                  className="hover:bg-slate-700/20 transition-colors duration-150"
                >
                  <td className="py-3 pr-4">
                    <div className="flex items-center gap-2">
                      {isWeak && (
                        <AlertTriangle className="w-3.5 h-3.5 text-red-400 flex-shrink-0" />
                      )}
                      <span className="text-slate-200 font-medium capitalize">
                        {topic.tag}
                      </span>
                    </div>
                  </td>
                  <td className="py-3 px-2 text-center text-slate-400">
                    {topic.attempts}
                  </td>
                  <td className="py-3 px-2 text-center">
                    <span className={topic.accepted > 0 ? 'text-green-400' : 'text-slate-500'}>
                      {topic.accepted}
                    </span>
                  </td>
                  <td className="py-3 pl-4 w-40">
                    <AcceptRateBar rate={topic.accept_rate} />
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <p className="mt-4 text-xs text-slate-600 flex items-center gap-1">
        <TrendingUp className="w-3 h-3" />
        Sorted by lowest acceptance rate. Focus on these topics to improve your rating.
      </p>
    </div>
  );
}
