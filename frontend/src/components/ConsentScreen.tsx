"use client";

import { useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface ConsentScreenProps {
  onConsentGranted: () => void;
}

/**
 * Privacy Consent Screen (AC08).
 *
 * Must be shown before any data collection begins.
 * Supports three consent levels: BASIC, STANDARD, FULL.
 * Derived from F-07 Privacy & Consent rules.
 */
export function ConsentScreen({ onConsentGranted }: ConsentScreenProps) {
  const [selectedLevel, setSelectedLevel] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const levels = [
    {
      id: "BASIC",
      name: "Basic",
      collected: "Calendar event counts and durations only",
      notCollected: "Event titles, attendees",
    },
    {
      id: "STANDARD",
      name: "Standard",
      collected: "Basic + Slack metadata (counts, timing)",
      notCollected: "Message content",
    },
    {
      id: "FULL",
      name: "Full",
      collected: "Standard + GitHub/Jira activity metadata",
      notCollected: "Code content, ticket text",
    },
  ];

  async function handleSubmit() {
    if (!selectedLevel) return;
    setSubmitting(true);

    try {
      const res = await fetch(`${API_BASE}/api/v1/consent/level`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ consent_level: selectedLevel }),
      });

      if (res.ok) {
        onConsentGranted();
      }
    } catch (err) {
      console.error("Failed to set consent:", err);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="flex items-center justify-center min-h-screen p-4">
      <div className="max-w-lg w-full bg-gray-900 rounded-2xl p-8 border border-gray-800">
        <h1 className="text-2xl font-bold mb-2">Privacy & Consent</h1>
        <p className="text-gray-400 mb-6">
          The Cognitive Load Balancer needs your permission before collecting any
          data. Choose what level of data you are comfortable sharing.
        </p>

        <div className="space-y-3 mb-6">
          {levels.map((level) => (
            <button
              key={level.id}
              onClick={() => setSelectedLevel(level.id)}
              className={`w-full text-left p-4 rounded-lg border transition-colors ${
                selectedLevel === level.id
                  ? "border-blue-500 bg-blue-500/10"
                  : "border-gray-700 hover:border-gray-600"
              }`}
            >
              <div className="font-semibold mb-1">{level.name}</div>
              <div className="text-sm text-gray-400">
                <span className="text-green-400">Collected:</span>{" "}
                {level.collected}
              </div>
              <div className="text-sm text-gray-400">
                <span className="text-red-400">Never collected:</span>{" "}
                {level.notCollected}
              </div>
            </button>
          ))}
        </div>

        <div className="text-xs text-gray-500 mb-4">
          <p>• Only derived signals are stored — never raw message content</p>
          <p>• You can delete all your data at any time (one-click)</p>
          <p>• Data is auto-deleted after 90 days</p>
          <p>• Mock mode never touches your real data</p>
        </div>

        <button
          onClick={handleSubmit}
          disabled={!selectedLevel || submitting}
          className="w-full py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:text-gray-500 rounded-lg font-medium transition-colors"
        >
          {submitting ? "Saving..." : "Grant Consent & Continue"}
        </button>
      </div>
    </main>
  );
}
