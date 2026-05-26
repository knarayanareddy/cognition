"use client";

import { useState, useEffect } from "react";
import { Navigation } from "@/components/Navigation";
import { Badge } from "@/components/Badge";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Intervention definitions from F-06
const INTERVENTIONS = [
  { id: "INT-01", name: "Add Focus Block", mode: "live", trigger: "focus_blocks_available == 0 AND CL > 50" },
  { id: "INT-02", name: "Insert Meeting Buffers", mode: "dry-run", trigger: "back_to_back_chains >= 3" },
  { id: "INT-03", name: "Enable Slack DND", mode: "dry-run", trigger: "after_hours_messages > 5" },
  { id: "INT-04", name: "Decline Non-Critical Meetings", mode: "dry-run", trigger: "total_meeting_hours > 6 AND CL > 65" },
  { id: "INT-05", name: "Reduce Sprint Scope", mode: "dry-run", trigger: "avg_tasks_in_progress > 7" },
  { id: "INT-06", name: "Manager Alert", mode: "dry-run", trigger: "CL > 80 OR burnout_risk > 0.75" },
  { id: "INT-07", name: "Vacation Guard", mode: "dry-run", trigger: "vacation_interrupted == true" },
];

interface InterventionRecord {
  intervention_id: string;
  int_type: string;
  execution_mode: string;
  triggered_by: string[];
  cl_score_at_trigger: number;
  action_taken: string;
  outcome: string;
  timestamp: string;
}

export default function InterventionLog() {
  const [history, setHistory] = useState<InterventionRecord[]>([]);
  const [triggering, setTriggering] = useState<string | null>(null);

  useEffect(() => {
    fetchHistory();
  }, []);

  async function fetchHistory() {
    try {
      const res = await fetch(`${API_BASE}/api/v1/interventions/history`, {
        credentials: "include",
      });
      const data = await res.json();
      setHistory(data.interventions || []);
    } catch (err) {
      console.error("Failed to fetch history:", err);
    }
  }

  async function triggerIntervention(intType: string) {
    setTriggering(intType);
    const mode = intType === "INT-01" ? "live" : "dry-run";
    try {
      const res = await fetch(`${API_BASE}/api/v1/interventions/trigger`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ int_type: intType, execution_mode: mode, force: true }),
      });
      if (res.ok) {
        await fetchHistory();
      }
    } catch (err) {
      console.error("Failed to trigger:", err);
    } finally {
      setTriggering(null);
    }
  }

  return (
    <>
      <Navigation />
      <main className="p-6 max-w-7xl mx-auto">
        <div className="mb-6">
          <h1 className="text-2xl font-bold">Intervention Log</h1>
          <p className="text-gray-400 text-sm mt-0.5">
            Audit trail of all interventions (F-09). Cards written to Miro board.
          </p>
        </div>

        {/* Intervention Rules Table */}
        <div className="bg-gray-900 rounded-xl p-5 border border-gray-800 mb-6">
          <h2 className="text-sm font-medium text-gray-400 mb-4">
            Intervention Rules (F-06)
          </h2>
          <div className="space-y-2">
            {INTERVENTIONS.map((int) => (
              <div
                key={int.id}
                className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg"
              >
                <div className="flex items-center gap-3">
                  <span className="font-mono text-xs text-gray-500 w-14">
                    {int.id}
                  </span>
                  <span className="text-sm font-medium">{int.name}</span>
                  <Badge type={int.mode === "live" ? "live" : "dry-run"} />
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-xs text-gray-500 hidden md:block">
                    {int.trigger}
                  </span>
                  <button
                    onClick={() => triggerIntervention(int.id)}
                    disabled={triggering === int.id}
                    className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-xs transition-colors disabled:opacity-50"
                  >
                    {triggering === int.id ? "..." : "Trigger"}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* History */}
        <div className="bg-gray-900 rounded-xl p-5 border border-gray-800">
          <h2 className="text-sm font-medium text-gray-400 mb-4">
            Intervention History (EP-09)
          </h2>
          {history.length === 0 ? (
            <p className="text-gray-500 text-sm">
              No interventions fired yet. Trigger one above or wait for automatic evaluation.
            </p>
          ) : (
            <div className="space-y-2">
              {history.map((record) => (
                <div
                  key={record.intervention_id}
                  className={`p-3 rounded-lg border ${
                    record.execution_mode === "live"
                      ? "border-green-500/30 bg-green-500/5"
                      : "border-yellow-500/30 bg-yellow-500/5"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs">{record.int_type}</span>
                      <Badge type={record.execution_mode === "live" ? "live" : "dry-run"} />
                      <span className="text-sm">{record.action_taken}</span>
                    </div>
                    <span className="text-xs text-gray-500">{record.outcome}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </>
  );
}
