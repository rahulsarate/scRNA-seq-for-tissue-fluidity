import { useCallback, useState } from "react";
import VolcanoPlot from "../components/VolcanoPlot";
import { api, DEResultResponse } from "../lib/api";
import { useApi } from "../hooks/useApi";

const COMPARISONS = [
  "wound_3d_vs_control",
  "wound_7d_vs_control",
  "wound_14d_vs_control",
];

export default function DEResults() {
  const [comparison, setComparison] = useState(COMPARISONS[0]);

  const fetcher = useCallback(
    () => api.getDEResults(comparison),
    [comparison]
  );
  const { data, loading, error } = useApi<DEResultResponse>(fetcher);

  return (
    <div>
      <div className="flex items-center gap-4 mb-4">
        <h2 className="text-xl font-semibold">Differential Expression</h2>
        <select
          value={comparison}
          onChange={(e) => setComparison(e.target.value)}
          className="border rounded px-2 py-1 text-sm"
        >
          {COMPARISONS.map((c) => (
            <option key={c} value={c}>
              {c.replaceAll("_", " ")}
            </option>
          ))}
        </select>
      </div>

      {loading && (
        <div className="animate-pulse h-96 bg-gray-100 rounded" />
      )}
      {error && <div className="text-red-600 text-sm">Error: {error}</div>}

      {data && (
        <div className="flex flex-wrap gap-6">
          <VolcanoPlot data={data} />

          {/* Summary table */}
          <div className="bg-white border rounded-lg p-4 w-80 h-fit shadow-sm">
            <h3 className="font-semibold mb-2">Summary</h3>
            <dl className="text-sm space-y-1">
              <div className="flex justify-between">
                <dt className="text-gray-500">Total genes</dt>
                <dd>{data.genes.length}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-500">Upregulated</dt>
                <dd className="text-red-600">
                  {data.genes.filter((g) => g.significant === "up").length}
                </dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-500">Downregulated</dt>
                <dd className="text-blue-600">
                  {data.genes.filter((g) => g.significant === "down").length}
                </dd>
              </div>
            </dl>

            {/* Top genes table */}
            <h4 className="text-sm font-medium text-gray-600 mt-4 mb-1">
              Top DE genes
            </h4>
            <table className="w-full text-xs">
              <thead>
                <tr className="text-gray-500">
                  <th className="text-left">Gene</th>
                  <th className="text-right">log2FC</th>
                  <th className="text-right">padj</th>
                </tr>
              </thead>
              <tbody>
                {data.genes
                  .filter((g) => g.significant !== "ns")
                  .sort((a, b) => a.padj - b.padj)
                  .slice(0, 15)
                  .map((g) => (
                    <tr key={g.gene}>
                      <td className="font-mono">{g.gene}</td>
                      <td
                        className={`text-right ${
                          g.log2FC > 0 ? "text-red-600" : "text-blue-600"
                        }`}
                      >
                        {g.log2FC.toFixed(2)}
                      </td>
                      <td className="text-right">
                        {g.padj.toExponential(1)}
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
