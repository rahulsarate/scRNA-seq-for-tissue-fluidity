const BASE = "/api/v1";

async function fetchJson<T>(url: string): Promise<T> {
  const res = await fetch(`${BASE}${url}`);
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`API ${res.status}: ${detail}`);
  }
  return res.json();
}

// -------------------------------------------------------------------
// Response types
// -------------------------------------------------------------------

export interface UmapResponse {
  x: number[];
  y: number[];
  n_cells: number;
  labels?: string[];
  color_by?: string;
  color_map?: Record<string, string>;
  hover?: Record<string, string[]>;
}

export interface GeneSearchResponse {
  query: string;
  matches: string[];
  count: number;
}

export interface GeneExpressionResponse {
  gene: string;
  expression: number[];
  mean_expression: number;
  percent_expressing: number;
  by_cell_type?: Record<string, number>;
  x?: number[];
  y?: number[];
}

export interface DEListResponse {
  comparisons: { name: string; n_genes: number; columns: string[] }[];
}

export interface DEResultResponse {
  comparison: string;
  genes: { gene: string; log2FC: number; padj: number; significant: string }[];
  n_total: number;
  n_up: number;
  n_down: number;
  thresholds: { padj: number; log2fc: number };
}

export interface ProportionsResponse {
  conditions: string[];
  cell_types: string[];
  proportions: Record<string, Record<string, number>>;
  counts: Record<string, Record<string, number>>;
  condition_colors: Record<string, string>;
  cell_type_colors: Record<string, string>;
}

export interface FluidityScoresResponse {
  scores: Record<string, number[]>;
  n_cells: number;
  condition?: string[];
  cell_type?: string[];
  x?: number[];
  y?: number[];
}

export interface FluiditySignaturesResponse {
  signatures: Record<string, string[]>;
}

export interface ConfigResponse {
  condition_colors: Record<string, string>;
  cell_type_colors: Record<string, string>;
  conditions: string[];
  qc_thresholds: Record<string, number>;
  tissue_fluidity_signatures: Record<string, { genes: string[] }>;
}

// -------------------------------------------------------------------
// API client
// -------------------------------------------------------------------

export const api = {
  getConfig: () => fetchJson<ConfigResponse>("/config"),
  getUmap: (colorBy = "cell_type") =>
    fetchJson<UmapResponse>(`/umap?color_by=${encodeURIComponent(colorBy)}`),
  searchGenes: (q: string) =>
    fetchJson<GeneSearchResponse>(`/genes/search?q=${encodeURIComponent(q)}`),
  getGeneExpression: (gene: string) =>
    fetchJson<GeneExpressionResponse>(`/genes/${encodeURIComponent(gene)}`),
  listDE: () => fetchJson<DEListResponse>("/de"),
  getDE: (comparison: string) =>
    fetchJson<DEResultResponse>(`/de/${encodeURIComponent(comparison)}`),
  getProportions: () => fetchJson<ProportionsResponse>("/proportions"),
  getFluidityScores: () =>
    fetchJson<FluidityScoresResponse>("/fluidity/scores"),
  getFluiditySignatures: () =>
    fetchJson<FluiditySignaturesResponse>("/fluidity/signatures"),
  getDEResults: (comparison: string) =>
    fetchJson<DEResultResponse>(`/de/${encodeURIComponent(comparison)}`),
};
