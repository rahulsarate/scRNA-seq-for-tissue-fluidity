import { NavLink, Route, Routes } from "react-router-dom";
import DEResults from "./pages/DEResults";
import FluidityDash from "./pages/FluidityDash";
import GeneExplorer from "./pages/GeneExplorer";
import Overview from "./pages/Overview";

const navItems = [
  { to: "/", label: "Overview" },
  { to: "/genes", label: "Gene Explorer" },
  { to: "/de", label: "DE Results" },
  { to: "/fluidity", label: "Fluidity" },
];

export default function App() {
  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <nav className="w-56 bg-gray-900 text-white flex flex-col p-4 shrink-0">
        <h1 className="text-lg font-bold mb-1">Wound Healing</h1>
        <p className="text-xs text-gray-400 mb-6">scRNA-seq Dashboard</p>
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/"}
            className={({ isActive }) =>
              `block px-3 py-2 rounded text-sm mb-1 transition-colors ${
                isActive
                  ? "bg-blue-600 text-white"
                  : "text-gray-300 hover:bg-gray-800"
              }`
            }
          >
            {item.label}
          </NavLink>
        ))}
        <div className="mt-auto text-xs text-gray-500">
          <p>PI: Rahul M Sarate</p>
          <p>Mus musculus &middot; GRCm39</p>
        </div>
      </nav>

      {/* Main content area */}
      <main className="flex-1 overflow-auto p-6">
        <Routes>
          <Route path="/" element={<Overview />} />
          <Route path="/genes" element={<GeneExplorer />} />
          <Route path="/de" element={<DEResults />} />
          <Route path="/fluidity" element={<FluidityDash />} />
        </Routes>
      </main>
    </div>
  );
}
