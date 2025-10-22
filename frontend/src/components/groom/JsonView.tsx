import React from "react";
import { Copy } from "lucide-react";

export default function JsonView({ data }: { data: unknown }) {
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(JSON.stringify(data, null, 2));
    } catch (err) {
      console.error('Failed to copy JSON:', err);
    }
  };

  return (
    <div>
      <div className="flex justify-end mb-2">
        <button
          className="text-sm px-2 py-1 border rounded hover:bg-gray-50 flex items-center space-x-1"
          onClick={handleCopy}
        >
          <Copy className="h-4 w-4" />
          <span>Copy JSON</span>
        </button>
      </div>
      <pre className="text-sm bg-gray-50 p-3 rounded overflow-auto whitespace-pre-wrap break-words">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
}
