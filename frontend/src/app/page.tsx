"use client";

import { useState, useEffect } from "react";
import { ConsentScreen } from "@/components/ConsentScreen";
import { Navigation } from "@/components/Navigation";
import { Badge } from "@/components/Badge";
import { ScoreBand } from "@/components/ScoreBand";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface ScoreData {
  cl_score: number;
  band: string;
  burnout_risk: number;
  flow_state: boolean;
  component_scores: Record<string, number>;
  risk_factors: string[];
  data_mode: string;
}

export default function Dashboard() {
  const [consentGranted, setConsentGranted] = useState<boolean | null>(null);
  const [score, setScore] = useState<ScoreData | null>(null);
  const [signals, setSignals] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkConsent();
  }, []);

  async function checkConsent() {
    try {
      const res = await fetch(`${API_BASE}/api/v1/consent/settings`, {
        credentials: "include",
      });
      const data = await res.json();
      setConsentGranted(data.consent_level !== null);
      if (data.consent_level) {
        await fetchData();
      }
    } catch {
      setConsentGranted(false);
    } finally {
      setLoading(false);
    }
  }

  async function fetchData() {
    try {
      const [scoreRes, signalsRes] = await Promise.all([
        fetch(`${API_BASE}/api/v1/scores/current`, { credentials: "include" }),
        fetch(`${API_BASE}/api/v1/signals/current`, { credentials: "include" }),
      ]);
      const scoreData = await scoreRes.json();
      const signalsData = await signalsRes.json();
      setScore(scoreData);
      setSignals(signalsData.signals || []);
    } catch (err) {
      console.error("Failed to fetch data:", err);
    }
  }

  if (loading) {
    return (
      <main className="flex items-center justify-center min-h-screen">
        <div className="text-gray-400">Loading...</div>
      </main>
    );
  }

  // AC08: Consent screen must be shown before any data collection
  if (!consentGranted) {
    return <ConsentScreen onConsentGranted={() => { setConsentGranted(true); fetchData(); }} />;
  }

  return (
    <>
      <Navigation />
      <main className="p-6 max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold">Cognitive Load Balancer</h1>
            <p className="text-gray-400 text-sm mt-0.5">
              Your Miro board thinks. Your agent acts.
            </p>
          </div>
          {score && <Badge type={score.data_mode === "live" ? "live" : "mock"} />}
        </div>

        {/* Score Cards Row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          {/* CL Score */}
          <div className="bg-gray-900 rounded-xl p-5 border border-gray-800">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-medium text-gray-400">CL Score</h2>
              <Badge type={score?.data_mode === "live" ? "live" : "mock"} />
            </div>
            {score ? (
              <ScoreBand score={score.cl_score} band={score.band} size="lg" />
            ) : (
              <div className="text-4xl font-bold text-gray-600">--</div>
            )}
          </div>

          {/* Burnout Risk */}
          <div className="bg-gray-900 rounded-xl p-5 border border-gray-800">
            <h2 className="text-sm font-medium text-gray-400 mb-3">Burnout Risk</h2>
            <div className={`text-4xl font-bold ${
              score && score.burnout_risk > 0.75 ? "text-red-500" :
              score && score.burnout_risk > 0.5 ? "text-orange-400" :
              "text-green-400"
            }`}>
              {score ? `${Math.round(score.burnout_risk * 100)}%` : "--%"}
            </div>
            <p className="text-xs text-gray-500 mt-2">
              {score && score.burnout_risk > 0.75 ? "Urgent — intervention required" :
               score && score.burnout_risk > 0.5 ? "Elevated — monitor closely" :
               "Within safe range"}
            </p>
          </div>

          {/* Flow State */}
          <div className="bg-gray-900 rounded-xl p-5 border border-gray-800">
            <h2 className="text-sm font-medium text-gray-400 mb-3">Flow State</h2>
            <div className={`text-4xl font-bold ${
              score?.flow_state ? "text-green-400" : "text-gray-500"
            }`}>
              {score ? (score.flow_state ? "Active" : "Inactive") : "--"}
            </div>
            <p className="text-xs text-gray-500 mt-2">
              All 5 conditions must be met for flow state
            </p>
          </div>
        </div>

        {/* Component Scores */}
        {score?.component_scores && (
          <div className="bg-gray-900 rounded-xl p-5 border border-gray-800 mb-6">
            <h2 className="text-sm font-medium text-gray-400 mb-4">
              Signal Categories (F-05 Weights)
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { key: "temporal", label: "Temporal", weight: "30%", source: "LIVE" },
                { key: "communication", label: "Communication", weight: "25%", source: "MOCK" },
                { key: "task", label: "Task", weight: "25%", source: "MOCK" },
                { key: "boundary", label: "Boundary", weight: "20%", source: "derived" },
              ].map((comp) => (
                <div key={comp.key} className="text-center">
                  <div className="text-2xl font-bold">
                    {score.component_scores[comp.key] ?? 0}
                  </div>
                  <div className="text-xs text-gray-400 mt-1">{comp.label}</div>
                  <div className="flex items-center justify-center gap-1 mt-1">
                    <span className="text-xs text-gray-500">{comp.weight}</span>
                    <Badge type={comp.source === "LIVE" ? "live" : "mock"} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* All 24 Signals */}
        {signals.length > 0 && (
          <div className="bg-gray-900 rounded-xl p-5 border border-gray-800">
            <h2 className="text-sm font-medium text-gray-400 mb-4">
              All 24 Signals (F-04)
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
              {signals.map((signal) => (
                <div
                  key={signal.signal_id}
                  className="bg-gray-800/50 rounded-lg p-3 border border-gray-700/50"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-mono text-gray-400">
                      {signal.signal_id}
                    </span>
                    <Badge type={signal.source_mode === "live" ? "live" : "mock"} />
                  </div>
                  <div className="text-lg font-semibold">
                    {typeof signal.value === "number"
                      ? signal.value.toFixed(1)
                      : signal.value}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Connect Calendar CTA (if no live data) */}
        {score && score.component_scores?.temporal === 0 && (
          <div className="mt-6 bg-gray-900 rounded-xl p-5 border border-gray-800">
            <h2 className="text-sm font-medium text-gray-400 mb-2">
              Connect Google Calendar
            </h2>
            <p className="text-gray-500 text-sm mb-3">
              Connect your calendar to get LIVE temporal signals (T-01 to T-07).
            </p>
            <button
              onClick={handleConnectCalendar}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm font-medium transition-colors"
            >
              Connect Calendar
            </button>
          </div>
        )}
      </main>
    </>
  );
}

async function handleConnectCalendar() {
  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  try {
    const res = await fetch(`${API_BASE}/api/v1/auth/google/init`, { method: "POST" });
    const data = await res.json();
    if (data.auth_url) window.location.href = data.auth_url;
  } catch (err) {
    console.error("Failed to initiate OAuth:", err);
  }
}
