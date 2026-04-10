import { useCallback } from "react";
import FluidityPanel from "../components/FluidityPanel";
import { api, FluiditySignaturesResponse } from "../lib/api";
import { useApi } from "../hooks/useApi";

export default function FluidityDash() {
  const fetcher = useCallback(() => api.getFluiditySignatures(), []);
  const { data: sigs } = useApi<FluiditySignaturesResponse>(fetcher);

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">
        Tissue Fluidity Analysis
      </h2>

      {/* Signature gene lists */}
      {sigs && (
        <div className="grid grid-cols-2 lg:grid-cols-5 gap-3 mb-6">
          {Object.entries(sigs.signatures).map(([cat, genes]) => (
            <div
              key={cat}
              className="bg-white border rounded p-3 shadow-sm"
            >
              <h4 className="text-sm font-semibold text-gray-700 mb-1">
                {cat.replaceAll("_", " ")}
              </h4>
              <p className="text-xs text-gray-500">
                {(genes as string[]).join(", ")}
              </p>
            </div>
          ))}
        </div>
      )}

      <FluidityPanel />
    </div>
  );
}
