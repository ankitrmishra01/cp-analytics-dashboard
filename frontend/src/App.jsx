import { useState } from 'react';
import { fetchUser, fetchAnalytics, fetchSentiment, refreshUser } from './api/cfApi';
import LandingPage from './pages/LandingPage';
import Dashboard from './pages/Dashboard';

export default function App() {
  const [view, setView] = useState('landing');
  const [handle, setHandle] = useState('');
  const [userData, setUserData] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [sentiment, setSentiment] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (inputHandle) => {
    const trimmed = inputHandle.trim();
    if (!trimmed) return;

    setLoading(true);
    setError(null);

    try {
      // Step 1: Fetch + cache user (may hit Codeforces API)
      const user = await fetchUser(trimmed);
      setUserData(user);
      setHandle(trimmed);

      // Step 2: Fetch analytics + sentiment in parallel (best-effort)
      const [analyticsResult, sentimentResult] = await Promise.allSettled([
        fetchAnalytics(trimmed),
        fetchSentiment(trimmed),
      ]);

      setAnalytics(
        analyticsResult.status === 'fulfilled' ? analyticsResult.value : null
      );
      setSentiment(
        sentimentResult.status === 'fulfilled' ? sentimentResult.value : null
      );

      setView('dashboard');
    } catch (err) {
      const msg =
        err?.response?.data?.detail ||
        err?.message ||
        'Something went wrong. Please try again.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    if (!handle) return;
    setLoading(true);
    setError(null);
    try {
      const user = await refreshUser(handle);
      setUserData(user);

      const [analyticsResult, sentimentResult] = await Promise.allSettled([
        fetchAnalytics(handle),
        fetchSentiment(handle),
      ]);

      setAnalytics(
        analyticsResult.status === 'fulfilled' ? analyticsResult.value : null
      );
      setSentiment(
        sentimentResult.status === 'fulfilled' ? sentimentResult.value : null
      );
    } catch (err) {
      setError(err?.response?.data?.detail || err?.message || 'Refresh failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    setView('landing');
    setError(null);
  };

  if (view === 'dashboard') {
    return (
      <Dashboard
        handle={handle}
        userData={userData}
        analytics={analytics}
        sentiment={sentiment}
        loading={loading}
        onBack={handleBack}
        onRefresh={handleRefresh}
      />
    );
  }

  return (
    <LandingPage
      onSearch={handleSearch}
      loading={loading}
      error={error}
    />
  );
}
