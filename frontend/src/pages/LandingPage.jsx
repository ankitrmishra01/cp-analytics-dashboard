import SearchBar from '../components/SearchBar';

const FEATURES = [
  { icon: '📈', label: 'Rating Trends', desc: 'Contest-by-contest rating progression' },
  { icon: '🧩', label: 'Topic Analysis', desc: 'Solve counts by tag and difficulty' },
  { icon: '🤖', label: 'NLP Sentiment', desc: 'Community mood via VADER + TextBlob' },
  { icon: '⚠️', label: 'Weak Topics', desc: 'Tags with low acceptance rate' },
];

export default function LandingPage({ onSearch, loading, error }) {
  return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center px-4 relative overflow-hidden">
      {/* Background glow blobs */}
      <div
        className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full pointer-events-none"
        style={{
          background:
            'radial-gradient(circle, rgba(59,130,246,0.08) 0%, transparent 70%)',
        }}
      />
      <div
        className="absolute bottom-1/4 right-1/4 w-[400px] h-[400px] rounded-full pointer-events-none"
        style={{
          background:
            'radial-gradient(circle, rgba(139,92,246,0.06) 0%, transparent 70%)',
        }}
      />

      <div className="relative z-10 w-full max-w-2xl mx-auto text-center animate-fade-in">
        {/* Portfolio badge */}
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold mb-8 tracking-wide">
          🏆 Portfolio Project · FastAPI + React + NLP
        </div>

        {/* Headline */}
        <h1 className="text-5xl sm:text-6xl font-extrabold tracking-tight leading-none mb-4">
          <span className="text-white">Competitive</span>
          <br />
          <span
            className="bg-clip-text text-transparent"
            style={{
              backgroundImage:
                'linear-gradient(135deg, #3b82f6 0%, #8b5cf6 50%, #06b6d4 100%)',
            }}
          >
            Programming
          </span>
          <br />
          <span className="text-white text-4xl sm:text-5xl">Analytics Dashboard</span>
        </h1>

        {/* Subtitle */}
        <p className="text-slate-400 text-base sm:text-lg mb-10 max-w-lg mx-auto leading-relaxed">
          Visualize your Codeforces journey — rating progression, topic mastery,
          weak areas, and community sentiment. All in one place.
        </p>

        {/* Search */}
        <div className="mb-10">
          <SearchBar onSearch={onSearch} loading={loading} error={error} />
        </div>

        {/* Feature pills */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {FEATURES.map((f) => (
            <div
              key={f.label}
              className="glass-card p-3 rounded-xl text-center hover:border-blue-500/30 transition-colors duration-200"
            >
              <div className="text-xl mb-1">{f.icon}</div>
              <div className="text-slate-300 text-xs font-semibold">{f.label}</div>
              <div className="text-slate-600 text-xs mt-0.5 leading-tight">{f.desc}</div>
            </div>
          ))}
        </div>

        {/* Footer note */}
        <p className="mt-10 text-slate-700 text-xs">
          Powered by the public Codeforces API · No login required
        </p>
      </div>
    </div>
  );
}
