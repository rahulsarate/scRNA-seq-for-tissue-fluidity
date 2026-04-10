import { useCallback } from "react";
import Plot from "react-plotly.js";
import { api, ProportionsResponse } from "../lib/api";
import { useApi } from "../hooks/useApi";

export default function ProportionChart() {
  const fetcher = useCallback(() => api.getProportions(), []);
  const { data, loading, error } = useApi<ProportionsResponse>(fetcher);

  if (loading)
    return <div className="animate-pulse h-64 bg-gray-100 rounded" />;
  if (error)
    return <div className="text-red-600 text-sm">Error: {error}</div>;
  if (!data) return null;

  const traces = data.cell_types.map((ct) => ({
    x: data.conditions,
    y: data.conditions.map(
      (cond) => (data.proportions[cond]?.[ct] ?? 0) * 100
    ),
    name: ct,
    type: "bar" as const,
    marker: { color: data.cell_type_colors[ct] ?? "#999" },
  }));

  return (
    <Plot
      data={traces}
      layout={{
        barmode: "stack",
        width: 500,
        height: 450,
        title: { text: "Cell Type Proportions by Condition" },
        xaxis: { title: { text: "Condition" } },
        yaxis: { title: { text: "% of cells" }, range: [0, 100] },
        legend: { orientation: "v", x: 1.02, y: 1, font: { size: 10 } },
        margin: { t: 40, l: 60, r: 140, b: 60 },
        paper_bgcolor: "white",
        plot_bgcolor: "white",
      }}
      config={{ responsive: true }}
    />
  );
}
