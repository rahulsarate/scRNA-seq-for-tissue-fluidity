import Plot from "react-plotly.js";
import { DEResultResponse } from "../lib/api";

interface Props {
  data: DEResultResponse;
}

export default function VolcanoPlot({ data }: Props) {
  const ns = data.genes.filter((g) => g.significant === "ns");
  const up = data.genes.filter((g) => g.significant === "up");
  const down = data.genes.filter((g) => g.significant === "down");

  const toTrace = (
    genes: typeof ns,
    color: string,
    name: string
  ) => ({
    x: genes.map((g) => g.log2FC),
    y: genes.map((g) => -Math.log10(g.padj + 1e-300)),
    mode: "markers" as const,
    type: "scattergl" as const,
    name,
    marker: { color, size: 3, opacity: 0.6 },
    text: genes.map(
      (g) =>
        `${g.gene}<br>log2FC: ${g.log2FC.toFixed(2)}<br>padj: ${g.padj.toExponential(2)}`
    ),
    hoverinfo: "text" as const,
  });

  return (
    <Plot
      data={[
        toTrace(ns, "#BBBBBB", `NS (${ns.length})`),
        toTrace(up, "#D6604D", `Up (${up.length})`),
        toTrace(down, "#2166AC", `Down (${down.length})`),
      ]}
      layout={{
        width: 680,
        height: 520,
        title: { text: data.comparison.replaceAll("_", " ") },
        xaxis: { title: { text: "log\u2082 Fold Change" }, zeroline: true },
        yaxis: { title: { text: "-log\u2081\u2080(padj)" }, zeroline: false },
        shapes: [
          {
            type: "line",
            x0: -data.thresholds.log2fc,
            x1: -data.thresholds.log2fc,
            y0: 0,
            y1: 1,
            yref: "paper",
            line: { dash: "dash", color: "#888", width: 1 },
          },
          {
            type: "line",
            x0: data.thresholds.log2fc,
            x1: data.thresholds.log2fc,
            y0: 0,
            y1: 1,
            yref: "paper",
            line: { dash: "dash", color: "#888", width: 1 },
          },
          {
            type: "line",
            x0: 0,
            x1: 1,
            xref: "paper",
            y0: -Math.log10(data.thresholds.padj),
            y1: -Math.log10(data.thresholds.padj),
            line: { dash: "dash", color: "#888", width: 1 },
          },
        ],
        margin: { t: 40, l: 60, r: 20, b: 50 },
        paper_bgcolor: "white",
        plot_bgcolor: "white",
      }}
      config={{ responsive: true }}
    />
  );
}
