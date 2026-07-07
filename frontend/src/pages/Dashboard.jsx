import { ArrowLeft, RefreshCw, Clock, ExternalLink } from 'lucide-react';
import RatingChart from '../components/RatingChart';
import TopicBreakdown from '../components/TopicBreakdown';
import VerdictChart from '../components/VerdictChart';
import WeakTopicsList from '../components/WeakTopicsList';
import SentimentBadge from '../components/SentimentBadge';
import LoadingSpinner from '../components/LoadingSpinner';

const RANK_COLORS = {
  newbie: '#808080',
  pupil: '#008000',
  specialist: '#03a89e',
  expert: '#0000ff',
  'candidate master': '#aa00aa',
  master: '#ff8c00',
  'international master': '#ff8c00',
  grandmaster: '#ff0000',
  'international grandmaster': '#ff0000',
  'legendary grandmaster': '#ff0000',
};

function getRankColor(rank) {
  if (!rank) return '#94a3b8';
  return RANK_COLORS[rank.toLowerCase()] || '#94a3b8';
}

function StatCard({ label, value, sub, color }) {
  return (
    <div className="glass-card glow-blue p-4 rounded-xl">
      <p className="text-slate-500 text-xs uppercase tracking-widest font-semibold mb-1">
        {label}
      </p>
      <p
        className="text-2xl font-extrabold"
        style={{ color: color || '#f1f5f9' }}
      >
        {value ?? '—'}
      </p>
      {sub && <p className="text-slate-500 text-xs mt-0.5 capitalize">{sub}</p>}
    </div>
  );
}

function SectionCard({ title, children, className = '' }) {
  return (
    <div className={`glass-card glow-blue p-5 rounded-2xl animate-fade-in ${className}`}>
      {title && (
        <h2 className="text-slate-300 text-xs uppercase tracking-widest font-semibold mb-4 flex items-center gap-2">
          <span className="w-1 h-4 bg-blue-500 rounded-full" />
          {title}
        </h2>
      )}
      {children}
    </div>
  );
}

export default function Dashboard({
  handle,
  userData,
  analytics,
  sentiment,
  loading,
  onBack,
  onRefresh,
}) {
  const user = userData?.user;
  const fetchedAt = userData?.fetched_at
    ? new Date(userData.fetched_at).toLocaleTimeString()
    : null;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      {loading && <LoadingSpinner message="Refreshing data…" />}

      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* ── Top bar ─────────────────────────────────────────────── */}
        <div className="flex items-center justify-between mb-6 flex-wrap gap-3">
          <div className="flex items-center gap-4">
            <button
              id="back-to-landing-btn"
              onClick={onBack}
              className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors text-sm"
            >
              <ArrowLeft className="w-4 h-4" />
              Back
            </button>

            <div className="flex items-center gap-3">
              {user?.avatar && (
                <img
                  src={user.avatar}
                  alt={handle}
                  className="w-10 h-10 rounded-full border-2 border-slate-700"
                  onError={(e) => { e.target.style.display = 'none'; }}
                />
              )}
              <div>
                <div className="flex items-center gap-2">
                  <h1 className="text-lg font-bold text-white">{handle}</h1>
                  <a
                    href={`https://codeforces.com/profile/${handle}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-slate-500 hover:text-blue-400 transition-colors"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                </div>
                {user?.rank && (
                  <span
                    className="text-xs font-semibold capitalize"
                    style={{ color: getRankColor(user.rank) }}
                  >
                    {user.rank}
                  </span>
                )}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {fetchedAt && (
              <span className="text-slate-600 text-xs flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {userData?.cached ? 'Cached at' : 'Fetched at'} {fetchedAt}
              </span>
            )}
            <button
              id="refresh-data-btn"
              onClick={onRefresh}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700
                         border border-slate-700 text-slate-300 hover:text-white text-sm
                         transition-all duration-200 disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>
        </div>

        {/* ── Stats row ────────────────────────────────────────────── */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
          <StatCard
            label="Total Solved"
            value={analytics?.total_solved}
            color="#22c55e"
          />
          <StatCard
            label="Submissions"
            value={analytics?.total_submissions}
            color="#60a5fa"
          />
          <StatCard
            label="Current Rating"
            value={user?.rating}
            sub={user?.rank}
            color={getRankColor(user?.rank)}
          />
          <StatCard
            label="Max Rating"
            value={user?.max_rating}
            sub={user?.max_rank}
            color={getRankColor(user?.max_rank)}
          />
        </div>

        {/* ── Rating chart (full width) ─────────────────────────────── */}
        <div className="mb-4">
          <SectionCard title="Rating Progression">
            {analytics?.rating_history ? (
              <RatingChart ratingHistory={analytics.rating_history} />
            ) : (
              <p className="text-slate-500 text-sm text-center py-10">
                Rating history unavailable.
              </p>
            )}
          </SectionCard>
        </div>

        {/* ── Topic + Verdict row ───────────────────────────────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-4">
          <div className="lg:col-span-2">
            <SectionCard title="Topic Breakdown (Top 15 Tags by Solves)">
              <TopicBreakdown tagDistribution={analytics?.tag_distribution} />
            </SectionCard>
          </div>
          <div>
            <SectionCard title="Verdict Distribution">
              <VerdictChart verdictDistribution={analytics?.verdict_distribution} />
            </SectionCard>
          </div>
        </div>

        {/* ── Difficulty row ────────────────────────────────────────── */}
        {analytics?.difficulty_distribution && (
          <div className="mb-4">
            <SectionCard title="Solves by Difficulty Bucket">
              <div className="grid grid-cols-4 sm:grid-cols-8 gap-2">
                {analytics.difficulty_distribution.map((b) => (
                  <div
                    key={b.bucket}
                    className="bg-slate-800/60 rounded-xl p-3 text-center border border-slate-700/50 hover:border-blue-500/30 transition-colors"
                  >
                    <p className="text-xl font-bold text-white">{b.count}</p>
                    <p className="text-slate-500 text-xs mt-0.5 leading-tight">
                      {b.bucket}
                    </p>
                  </div>
                ))}
              </div>
            </SectionCard>
          </div>
        )}

        {/* ── Weak topics + Sentiment row ───────────────────────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-4">
          <div className="lg:col-span-2">
            <SectionCard title="Weak Topics (Low Acceptance Rate)">
              <WeakTopicsList weakTopics={analytics?.weak_topics} />
            </SectionCard>
          </div>
          <div>
            <SectionCard title="Community Sentiment">
              <SentimentBadge sentiment={sentiment} />
            </SectionCard>
          </div>
        </div>

        {/* ── Footer ───────────────────────────────────────────────── */}
        <footer className="text-center text-slate-700 text-xs mt-8">
          CP Analytics Dashboard · Data from{' '}
          <a
            href="https://codeforces.com"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-slate-500 transition-colors"
          >
            Codeforces API
          </a>{' '}
          · NLP: VADER + TextBlob
        </footer>
      </div>
    </div>
  );
}
