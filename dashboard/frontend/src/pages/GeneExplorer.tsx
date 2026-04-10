import { useCallback, useState } from "react";
import GeneSearch from "../components/GeneSearch";
import UMAPPlot from "../components/UMAPPlot";
import { api, GeneExpressionResponse } from "../lib/api";
import { useApi } from "../hooks/useApi";

export default function GeneExplorer() {
  const [gene, setGene] = useState<string | null>(null);

  const fetcher = useCallback(
    () => (gene ? api.getGeneExpression(gene) : Promise.resolve(null)),
    [gene]
  );
  const { data: exprData, loading } =
    useApi<GeneExpressionResponse | null>(fetcher);

  return (
    <div>
      <div className="flex items-center gap-4 mb-4">
        <h2 className="text-xl font-semibold">Gene Explorer</h2>
        <GeneSearch onSelect={setGene} />
      </div>

      <div className="flex flex-wrap gap-6">
        <UMAPPlot
          colorBy="cell_type"
          expressionOverlay={
            exprData && gene
              ? { expression: exprData.expression, gene }
              : null
          }
        />

        {/* Stats card */}
        {gene && exprData && !loading && (
          <div className="bg-white border rounded-lg p-4 w-72 h-fit shadow-sm">
            <h3 className="font-semibold mb-2">{gene}</h3>
            <dl className="text-sm space-y-1">
              <div className="flex justify-between">
                <dt className="text-gray-500">Mean expression</dt>
                <dd>{exprData.mean_expression.toFixed(3)}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-500">% cells expressing</dt>
                <dd>{exprData.percent_expressing.toFixed(1)}%</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-500">Max expression</dt>
                <dd>{Math.max(...exprData.expression).toFixed(2)}</dd>
              </div>
            </dl>
            {exprData.by_cell_type && (
              <div className="mt-4">
                <h4 className="text-sm font-medium text-gray-600 mb-1">
                  By cell type
                </h4>
                <ul className="text-xs space-y-0.5 max-h-48 overflow-auto">
                  {Object.entries(exprData.by_cell_type)
                    .sort(([, a], [, b]) => (b as number) - (a as number))
                    .map(([ct, val]) => (
                      <li key={ct} className="flex justify-between">
                        <span className="text-gray-600">{ct}</span>
                        <span>{(val as number).toFixed(3)}</span>
                      </li>
                    ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
