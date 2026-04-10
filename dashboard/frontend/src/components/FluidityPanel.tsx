import { useCallback } from "react";
import Plot from "react-plotly.js";
import { api, FluidityScoresResponse } from "../lib/api";
import { CONDITION_COLORS } from "../lib/colors";
import { useApi } from "../hooks/useApi";

export default function FluidityPanel() {
  const fetcher = useCallback(() => api.getFluidityScores(), []);
  const { data, loading, error } = useApi<FluidityScoresResponse>(fetcher);

  if (loading)
    return <div className="animate-pulse h-96 bg-gray-100 rounded" />;
  if (error)
    return <div className="text-red-600 text-sm">Error: {error}</div>;
  if (!data) return null;

  const categories = Object.keys(data.scores);
  const conditions = data.condition ? [...new Set(data.condition)] : [];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      {categories.map((cat) => {
        const traces = conditions.map((cond) => {
          const indices = data
            .condition!.map((c, i) => (c === cond ? i : -1))
            .filter((i) => i >= 0);
          return {
            y: indices.map((i) => data.scores[cat][i]),
            name: cond,
            type: "box" as const,
            marker: { color: CONDITION_COLORS[cond] ?? "#999" },
            boxpoints: false as const,
          };
        });

        return (
          <Plot
            key={cat}
            data={traces}
            layout={{
              width: 420,
              height: 320,
              title: { text: cat.replaceAll("_", " ") },
              yaxis: { title: { text: "Score" } },
              showlegend: true,
              legend: { orientation: "h", y: -0.2 },
              margin: { t: 40, l: 50, r: 20, b: 60 },
              paper_bgcolor: "white",
              plot_bgcolor: "white",
            }}
            config={{ responsive: true, displayModeBar: false }}
          />
        );
      })}
    </div>
  );
}
