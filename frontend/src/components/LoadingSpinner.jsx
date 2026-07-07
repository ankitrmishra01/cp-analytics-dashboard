export default function LoadingSpinner({ message = 'Fetching Codeforces data...' }) {
  return (
    <div className="fixed inset-0 bg-slate-950/90 backdrop-blur-sm flex flex-col items-center justify-center z-50">
      {/* Animated ring */}
      <div className="relative mb-6">
        <div className="w-16 h-16 rounded-full border-4 border-slate-700 border-t-blue-500 animate-spin" />
        <div className="absolute inset-0 w-16 h-16 rounded-full border-4 border-transparent border-r-violet-500 animate-spin"
          style={{ animationDirection: 'reverse', animationDuration: '1.5s' }}
        />
      </div>

      <p className="text-slate-300 text-sm font-medium tracking-wide animate-pulse">
        {message}
      </p>
      <p className="text-slate-500 text-xs mt-2">This may take a few seconds…</p>
    </div>
  );
}
