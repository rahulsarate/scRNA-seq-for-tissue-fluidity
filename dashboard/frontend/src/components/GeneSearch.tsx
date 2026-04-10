import { useCallback, useRef, useState } from "react";
import { api } from "../lib/api";

interface Props {
  onSelect: (gene: string) => void;
}

export default function GeneSearch({ onSelect }: Props) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<string[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const debounceRef = useRef<ReturnType<typeof setTimeout>>();

  const handleInput = useCallback(
    (value: string) => {
      setQuery(value);
      if (debounceRef.current) clearTimeout(debounceRef.current);
      if (value.length < 1) {
        setResults([]);
        setShowDropdown(false);
        return;
      }
      debounceRef.current = setTimeout(async () => {
        try {
          const res = await api.searchGenes(value);
          setResults(res.matches);
          setShowDropdown(res.matches.length > 0);
        } catch {
          setResults([]);
        }
      }, 200);
    },
    []
  );

  return (
    <div className="relative w-72">
      <input
        type="text"
        value={query}
        onChange={(e) => handleInput(e.target.value)}
        onFocus={() => results.length > 0 && setShowDropdown(true)}
        placeholder="Search gene (e.g. Krt14, Vim)..."
        className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      {showDropdown && (
        <ul className="absolute z-10 w-full bg-white border border-gray-200 rounded-md shadow-lg max-h-60 overflow-auto mt-1">
          {results.map((gene) => (
            <li
              key={gene}
              onClick={() => {
                onSelect(gene);
                setQuery(gene);
                setShowDropdown(false);
              }}
              className="px-3 py-1.5 text-sm cursor-pointer hover:bg-blue-50"
            >
              {gene}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
