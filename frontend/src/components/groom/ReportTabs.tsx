import { useState } from "react";
import MarkdownView from "./MarkdownView";
import JsonView from "./JsonView";

export default function ReportTabs({ markdown, data }: {
  markdown: string;
  data: unknown;
}) {
  const [tab, setTab] = useState<"report" | "json">("report");
  
  return (
    <div className="rounded-2xl border bg-white shadow-sm">
      <div className="flex gap-2 border-b p-2">
        <button 
          className={`px-3 py-1 rounded ${tab === "report" ? "bg-blue-600 text-white" : "hover:bg-gray-100"}`} 
          onClick={() => setTab("report")}
        >
          Report
        </button>
        <button 
          className={`px-3 py-1 rounded ${tab === "json" ? "bg-blue-600 text-white" : "hover:bg-gray-100"}`} 
          onClick={() => setTab("json")}
        >
          JSON
        </button>
      </div>
      <div className="p-4">
        {tab === "report" ? (
          <MarkdownView content={markdown} />
        ) : (
          <JsonView data={data} />
        )}
      </div>
    </div>
  );
}
