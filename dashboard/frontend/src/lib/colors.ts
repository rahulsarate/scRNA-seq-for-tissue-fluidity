/** Colorblind-safe palettes matching publication figures and analysis_config.yaml */

export const CONDITION_COLORS: Record<string, string> = {
  control: "#2166AC",
  wound_3d: "#F4A582",
  wound_7d: "#D6604D",
  wound_14d: "#B2182B",
};

export const CELL_TYPE_COLORS: Record<string, string> = {
  Basal_Keratinocyte: "#E69F00",
  Diff_Keratinocyte: "#F0E442",
  Fibroblast: "#56B4E9",
  Myofibroblast: "#009E73",
  Macrophage: "#D55E00",
  Neutrophil: "#CC79A7",
  T_Cell: "#0072B2",
  Endothelial: "#999999",
  Hair_Follicle_SC: "#882255",
  Melanocyte: "#44AA99",
};

export function getColor(
  value: string,
  colorMap?: Record<string, string>
): string {
  if (colorMap && value in colorMap) return colorMap[value];
  if (value in CONDITION_COLORS) return CONDITION_COLORS[value];
  if (value in CELL_TYPE_COLORS) return CELL_TYPE_COLORS[value];
  return "#999999";
}
