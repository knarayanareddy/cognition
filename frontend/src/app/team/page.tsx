"use client";

import { useState, useEffect } from "react";
import { Navigation } from "@/components/Navigation";
import { Badge } from "@/components/Badge";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const BAND_COLORS: Record<string, string> = {
  OPTIMAL: "border-green-500 bg-green-500/10",
  MODERATE: "border-yellow-500 bg-yellow-500/10",
  HIGH: "border-orange-500 bg-orange-500/10",
  CRITICAL: "border-red-500 bg-red-500/10",
  BURNOUT: "border-red-800 bg-red-900/10",
};

const BAND_TEXT: Record<string, string> = {
  OPTIMAL: "text-green-400",
  MODERATE: "text-yellow-400",
  HIGH: "text-orange-400",
  CRITICAL: "text-red-500",
  BURNOUT: "text-red-800",
};

interface TeamMember {
  user_id: string;
  cl_score: number;
  band: string;
  burnout_risk: number;
  flow_state: boolean;
  data_mode: string;
  last_updated: string;
}

export default function TeamHeatmap() {
  const [team, setTeam] = useState<TeamMember[]>([]);

  useEffect(() => {
    fetchTeam();
  }, []);

  async function fetchTeam() {
    try {
      const res = await fetch(`${API_BASE}/api/v1/team/heatmap`, {
        credentials: "include",
      });
      const data = await res.json();
      setTeam(data.users || []);
    } catch (err) {
      console.error("Failed to fetch team:", err);
    }
  }

  return (
    <>
      <Navigation />
      <main className="p-6 max-w-7xl mx-auto">
        <div className="mb-6">
          <h1 className="text-2xl font-bold">Team Heatmap</h1>
          <p className="text-gray-400 text-sm mt-0.5">
            Real-time cognitive load visualization (F-08). Updated every 15 minutes.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {team.map((member) => (
            <div
              key={member.user_id}
              className={`rounded-xl p-5 border-2 ${BAND_COLORS[member.band] || "border-gray-700 bg-gray-900"}`}
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs text-gray-400 font-mono">
                  {member.user_id.slice(0, 8)}...
                </span>
                <Badge type={member.data_mode === "live" ? "live" : "mock"} />
              </div>

              <div className={`text-4xl font-bold ${BAND_TEXT[member.band]}`}>
                {member.cl_score}
              </div>
              <div className={`text-sm font-medium mt-1 ${BAND_TEXT[member.band]}`}>
                {member.band}
              </div>

              <div className="mt-3 space-y-1 text-xs text-gray-400">
                <div className="flex justify-between">
                  <span>Burnout Risk</span>
                  <span className={member.burnout_risk > 0.75 ? "text-red-400" : ""}>
                    {Math.round(member.burnout_risk * 100)}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Flow State</span>
                  <span className={member.flow_state ? "text-green-400" : "text-gray-500"}>
                    {member.flow_state ? "Active" : "Inactive"}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </main>
    </>
  );
}
