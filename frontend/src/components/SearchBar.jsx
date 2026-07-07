import { useState } from 'react';
import { Search } from 'lucide-react';

export default function SearchBar({ onSearch, loading, error }) {
  const [inputValue, setInputValue] = useState('');
  const [localError, setLocalError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = inputValue.trim();
    if (!trimmed) {
      setLocalError('Please enter a Codeforces handle.');
      return;
    }
    setLocalError('');
    onSearch(trimmed);
  };

  const displayError = localError || error;

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-xl mx-auto">
      <div className="relative flex items-center gap-3">
        {/* Input */}
        <div className="relative flex-1">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
          <input
            id="cf-handle-input"
            type="text"
            value={inputValue}
            onChange={(e) => {
              setInputValue(e.target.value);
              if (localError) setLocalError('');
            }}
            onKeyDown={(e) => e.key === 'Enter' && handleSubmit(e)}
            placeholder="Enter Codeforces handle (e.g. tourist)"
            disabled={loading}
            autoComplete="off"
            spellCheck={false}
            className="w-full pl-12 pr-4 py-3.5 rounded-xl bg-slate-800/60 border border-slate-600/50
                       text-slate-100 placeholder-slate-500 text-sm font-medium
                       focus:outline-none focus:ring-2 focus:ring-blue-500/60 focus:border-blue-500/60
                       hover:border-slate-500 transition-all duration-200
                       disabled:opacity-50 disabled:cursor-not-allowed"
          />
        </div>

        {/* Submit button */}
        <button
          id="cf-search-btn"
          type="submit"
          disabled={loading}
          className="px-6 py-3.5 rounded-xl bg-blue-600 hover:bg-blue-500 active:scale-95
                     text-white text-sm font-semibold tracking-wide
                     transition-all duration-200 shadow-lg shadow-blue-500/25
                     disabled:opacity-50 disabled:cursor-not-allowed
                     flex items-center gap-2 whitespace-nowrap"
        >
          {loading ? (
            <>
              <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Analyzing…
            </>
          ) : (
            <>
              <Search className="w-4 h-4" />
              Analyze
            </>
          )}
        </button>
      </div>

      {/* Error */}
      {displayError && (
        <p className="mt-3 text-red-400 text-sm text-center animate-fade-in">
          ⚠ {displayError}
        </p>
      )}

      {/* Hint */}
      {!displayError && (
        <p className="mt-2 text-slate-600 text-xs text-center">
          Fetches your last 1,000 Codeforces submissions • Data cached for 1 hour
        </p>
      )}
    </form>
  );
}
