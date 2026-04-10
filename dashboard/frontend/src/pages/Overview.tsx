import { useState } from "react";
import UMAPPlot from "../components/UMAPPlot";
import ProportionChart from "../components/ProportionChart";

const colorOptions = ["cell_type", "condition", "leiden", "sample_id"];

export default function Overview() {
  const [colorBy, setColorBy] = useState("cell_type");

  return (
    <div>
      <div className="flex items-center gap-4 mb-4">
        <h2 className="text-xl font-semibold">Overview</h2>
        <select
          value={colorBy}
          onChange={(e) => setColorBy(e.target.value)}
          className="border rounded px-2 py-1 text-sm"
        >
          {colorOptions.map((opt) => (
            <option key={opt} value={opt}>
              {opt.replaceAll("_", " ")}
            </option>
          ))}
        </select>
      </div>

      <div className="flex flex-wrap gap-6">
        <UMAPPlot colorBy={colorBy} />
        <ProportionChart />
      </div>
    </div>
  );
}
