import { useCallback } from "react";
import Plot from "react-plotly.js";
import { api, UmapResponse } from "../lib/api";
import { getColor } from "../lib/colors";
import { useApi } from "../hooks/useApi";

interface Props {
  colorBy?: string;
  expressionOverlay?: { expression: number[]; gene: string } | null;
}

export default function UMAPPlot({
  colorBy = "cell_type",
  expressionOverlay,
}: Props) {
  const fetcher = useCallback(() => api.getUmap(colorBy), [colorBy]);
  const { data, loading, error } = useApi<UmapResponse>(fetcher);

  if (loading)
    return <div className="animate-pulse h-96 bg-gray-100 rounded" />;
  if (error)
    return <div className="text-red-600 text-sm p-4">Error: {error}</div>;
  if (!data) return null;

  // Feature-plot mode: color by continuous expression values
  if (expressionOverlay) {
    return (
      <Plot
        data={[
          {
            x: data.x,
            y: data.y,
            mode: "markers",
            type: "scattergl",
            marker: {
              color: expressionOverlay.expression,
              colorscale: "Reds",
              size: 2,
              colorbar: { title: { text: expressionOverlay.gene }, thickness: 15 },
            },
            hoverinfo: "text",
            text: expressionOverlay.expression.map(
              (v, i) =>
                `${expressionOverlay.gene}: ${v.toFixed(2)}${
                  data.hover?.cell_type
                    ? `<br>${data.hover.cell_type[i]}`
                    : ""
                }`
            ),
          },
        ]}
        layout={{
          width: 680,
          height: 580,
          title: { text: `${expressionOverlay.gene} Expression` },
          xaxis: { title: { text: "UMAP1" }, zeroline: false },
          yaxis: { title: { text: "UMAP2" }, zeroline: false },
          margin: { t: 40, l: 50, r: 20, b: 50 },
          paper_bgcolor: "white",
          plot_bgcolor: "white",
        }}
        config={{ responsive: true, displayModeBar: true }}
      />
    );
  }

  // Categorical mode: one trace per unique label
  const uniqueLabels = [...new Set(data.labels ?? [])];
  const traces = uniqueLabels.map((label) => {
    const indices = data
      .labels!.map((l, i) => (l === label ? i : -1))
      .filter((i) => i >= 0);
    return {
      x: indices.map((i) => data.x[i]),
      y: indices.map((i) => data.y[i]),
      mode: "markers" as const,
      type: "scattergl" as const,
      name: label,
      marker: { color: getColor(label, data.color_map), size: 2 },
      hoverinfo: "text" as const,
      text: indices.map((i) => {
        const parts = [label];
        if (data.hover) {
          for (const [key, vals] of Object.entries(data.hover)) {
            if (key !== colorBy) parts.push(`${key}: ${vals[i]}`);
          }
        }
        return parts.join("<br>");
      }),
    };
  });

  return (
    <Plot
      data={traces}
      layout={{
        width: 680,
        height: 580,
        title: { text: `UMAP — ${colorBy}` },
        xaxis: { title: { text: "UMAP1" }, zeroline: false },
        yaxis: { title: { text: "UMAP2" }, zeroline: false },
        legend: { orientation: "v", x: 1.02, y: 1 },
        margin: { t: 40, l: 50, r: 140, b: 50 },
        paper_bgcolor: "white",
        plot_bgcolor: "white",
      }}
      config={{ responsive: true, displayModeBar: true }}
    />
  );
}
