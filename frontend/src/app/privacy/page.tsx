"use client";

import { useState, useEffect } from "react";
import { Navigation } from "@/components/Navigation";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const CONSENT_LEVELS = [
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

export default function PrivacyPage() {
  const [consentLevel, setConsentLevel] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [deleted, setDeleted] = useState(false);

  useEffect(() => {
    fetchConsent();
  }, []);

  async function fetchConsent() {
    try {
      const res = await fetch(`${API_BASE}/api/v1/consent/settings`, {
        credentials: "include",
      });
      const data = await res.json();
      setConsentLevel(data.consent_level);
    } catch (err) {
      console.error("Failed to fetch consent:", err);
    }
  }

  async function updateConsent(level: string) {
    try {
      await fetch(`${API_BASE}/api/v1/consent/level`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ consent_level: level }),
      });
      setConsentLevel(level);
    } catch (err) {
      console.error("Failed to update consent:", err);
    }
  }

  async function deleteAllData() {
    if (!confirm("Delete ALL your data? This cannot be undone.")) return;
    setDeleting(true);
    try {
      await fetch(`${API_BASE}/api/v1/user/data`, {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ confirm: true }),
      });
      setDeleted(true);
      setConsentLevel(null);
    } catch (err) {
      console.error("Failed to delete data:", err);
    } finally {
      setDeleting(false);
    }
  }

  return (
    <>
      <Navigation />
      <main className="p-6 max-w-3xl mx-auto">
        <div className="mb-6">
          <h1 className="text-2xl font-bold">Privacy & Data Management</h1>
          <p className="text-gray-400 text-sm mt-0.5">
            Control your data. GDPR Art. 17 compliant. (F-07)
          </p>
        </div>

        {/* Current Consent Level */}
        <div className="bg-gray-900 rounded-xl p-5 border border-gray-800 mb-6">
          <h2 className="text-sm font-medium text-gray-400 mb-4">
            Your Consent Level
          </h2>
          <div className="space-y-3">
            {CONSENT_LEVELS.map((level) => (
              <button
                key={level.id}
                onClick={() => updateConsent(level.id)}
                className={`w-full text-left p-4 rounded-lg border transition-colors ${
                  consentLevel === level.id
                    ? "border-blue-500 bg-blue-500/10"
                    : "border-gray-700 hover:border-gray-600"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-semibold">{level.name}</span>
                  {consentLevel === level.id && (
                    <span className="text-xs text-blue-400">Active</span>
                  )}
                </div>
                <div className="text-sm text-gray-400 mt-1">
                  <span className="text-green-400">Collected:</span>{" "}
                  {level.collected}
                </div>
                <div className="text-sm text-gray-400">
                  <span className="text-red-400">Never:</span>{" "}
                  {level.notCollected}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Core Principles */}
        <div className="bg-gray-900 rounded-xl p-5 border border-gray-800 mb-6">
          <h2 className="text-sm font-medium text-gray-400 mb-3">
            Core Principles
          </h2>
          <ul className="space-y-2 text-sm text-gray-300">
            <li>• Only derived signals stored — never raw message content</li>
            <li>• Every data point visible in this dashboard</li>
            <li>• Mock mode never touches your real data</li>
            <li>• Data auto-deleted after 90 days (CFG-08)</li>
          </ul>
        </div>

        {/* Delete All Data */}
        <div className="bg-gray-900 rounded-xl p-5 border border-red-900/30">
          <h2 className="text-sm font-medium text-red-400 mb-2">
            Delete All Data (EP-17)
          </h2>
          <p className="text-sm text-gray-400 mb-4">
            One-click deletion of all scores, interventions, and signals.
            GDPR Art. 17 compliant. This cannot be undone.
          </p>
          {deleted ? (
            <p className="text-green-400 text-sm">All data deleted.</p>
          ) : (
            <button
              onClick={deleteAllData}
              disabled={deleting}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-700 rounded-lg text-sm font-medium transition-colors"
            >
              {deleting ? "Deleting..." : "Delete All My Data"}
            </button>
          )}
        </div>
      </main>
    </>
  );
}
