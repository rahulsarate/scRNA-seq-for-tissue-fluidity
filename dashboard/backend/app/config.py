"""Load project configuration from configs/analysis_config.yaml."""

from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[3]
CONFIG_PATH = PROJECT_ROOT / "configs" / "analysis_config.yaml"


def load_config() -> dict[str, Any]:
    """Load and return the analysis config, or empty dict if missing."""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r") as f:
            return yaml.safe_load(f) or {}
    return {}


CONFIG: dict[str, Any] = load_config()

CONDITION_COLORS: dict[str, str] = {
    "control": "#2166AC",
    "wound_3d": "#F4A582",
    "wound_7d": "#D6604D",
    "wound_14d": "#B2182B",
}

CELL_TYPE_COLORS: dict[str, str] = {
    "Basal_Keratinocyte": "#E69F00",
    "Diff_Keratinocyte": "#F0E442",
    "Fibroblast": "#56B4E9",
    "Myofibroblast": "#009E73",
    "Macrophage": "#D55E00",
    "Neutrophil": "#CC79A7",
    "T_Cell": "#0072B2",
    "Endothelial": "#999999",
    "Hair_Follicle_SC": "#882255",
    "Melanocyte": "#44AA99",
}
