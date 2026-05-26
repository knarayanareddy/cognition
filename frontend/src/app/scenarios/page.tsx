"use client";

import { useState, useEffect } from "react";
import { Navigation } from "@/components/Navigation";
import { Badge } from "@/components/Badge";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Scenario {
  scenario_id: string;
  name: string;
  description: string;
  sources_affected: string[];
}

export default function DemoScenarios() {
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [activeScenario, setActiveScenario] = useState<string | null>(null);
  const [score, setScore] = useState<any>(null);

  useEffect(() => {
    fetchScenarios();
    fetchScore();
  }, []);

  async function fetchScenarios() {
    try {
      const res = await fetch(`${API_BASE}/api/v1/scenarios`, {
        credentials: "include",
      });
      const data = await res.json();
      setScenarios(data.scenarios || []);
    } catch (err) {
      console.error("Failed to fetch scenarios:", err);
    }
  }

  async function fetchScore() {
    try {
      const res = await fetch(`${API_BASE}/api/v1/scores/current`, {
        credentials: "include",
      });
      setScore(await res.json());
    } catch (err) {
      console.error("Failed to fetch score:", err);
    }
  }

  async function activateScenario(scenarioId: string) {
    try {
      await fetch(`${API_BASE}/api/v1/scenarios/activate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ scenario_id: scenarioId, data_mode: "mock" }),
      });
      setActiveScenario(scenarioId);
      // Refresh score to show real-time update
      await fetchScore();
    } catch (err) {
      console.error("Failed to activate scenario:", err);
    }
  }

  async function deactivateScenario() {
    try {
      await fetch(`${API_BASE}/api/v1/scenarios/deactivate`, {
        method: "POST",
        credentials: "include",
      });
      setActiveScenario(null);
      await fetchScore();
    } catch (err) {
      console.error("Failed to deactivate:", err);
    }
  }

  return (
    <>
      <Navigation />
      <main className="p-6 max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold">Demo Scenarios</h1>
            <p className="text-gray-400 text-sm mt-0.5">
              Toggle mock scenarios (F-03). Score updates in real time.
            </p>
          </div>
          {activeScenario && (
            <button
              onClick={deactivateScenario}
              className="px-3 py-1.5 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm transition-colors"
            >
              Deactivate Mock → Return to LIVE
            </button>
          )}
        </div>

        {/* Current Score Display */}
        {score && (
          <div className="bg-gray-900 rounded-xl p-5 border border-gray-800 mb-6">
            <div className="flex items-center gap-4">
              <div>
                <span className="text-sm text-gray-400">Current CL Score</span>
                <div className="text-3xl font-bold">{score.cl_score}</div>
              </div>
              <div>
                <span className="text-sm text-gray-400">Band</span>
                <div className="text-lg font-semibold">{score.band}</div>
              </div>
              <div>
                <span className="text-sm text-gray-400">Mode</span>
                <div>
                  <Badge type={score.data_mode === "live" ? "live" : "mock"} />
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Scenario Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {scenarios.map((scenario) => (
            <div
              key={scenario.scenario_id}
              className={`rounded-xl p-5 border transition-colors ${
                activeScenario === scenario.scenario_id
                  ? "border-blue-500 bg-blue-500/10"
                  : "border-gray-800 bg-gray-900 hover:border-gray-700"
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-mono text-gray-500">
                  {scenario.scenario_id}
                </span>
                <Badge type="mock" />
              </div>
              <h3 className="font-semibold mb-1">{scenario.name}</h3>
              <p className="text-sm text-gray-400 mb-3">{scenario.description}</p>
              <div className="text-xs text-gray-500 mb-3">
                Sources: {scenario.sources_affected.join(", ")}
              </div>
              <button
                onClick={() => activateScenario(scenario.scenario_id)}
                disabled={activeScenario === scenario.scenario_id}
                className={`w-full py-2 rounded-lg text-sm font-medium transition-colors ${
                  activeScenario === scenario.scenario_id
                    ? "bg-blue-600 text-white cursor-default"
                    : "bg-gray-800 hover:bg-gray-700 text-gray-300"
                }`}
              >
                {activeScenario === scenario.scenario_id ? "Active" : "Activate"}
              </button>
            </div>
          ))}
        </div>
      </main>
    </>
  );
}
