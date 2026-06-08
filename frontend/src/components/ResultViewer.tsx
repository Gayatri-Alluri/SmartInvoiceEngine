import { Light as SyntaxHighlighter } from "react-syntax-highlighter";
import json from "react-syntax-highlighter/dist/esm/languages/hljs/json";
import { atomOneDark } from "react-syntax-highlighter/dist/esm/styles/hljs";
import type { InvoiceJSON } from "../types/invoice";

SyntaxHighlighter.registerLanguage("json", json);

interface ResultViewerProps {
  result: InvoiceJSON;
}

function ResultViewer({ result }: ResultViewerProps) {
  const jsonString = JSON.stringify(result, null, 2);

  return (
    <div className="rounded-lg overflow-hidden border border-gray-700">
      <div className="bg-gray-800 px-4 py-2 flex items-center justify-between">
        <span className="text-sm text-gray-300 font-mono">result.json</span>
        <span
          className={`text-xs px-2 py-0.5 rounded font-semibold ${
            result.metadata.validation_status === "passed"
              ? "bg-green-700 text-green-100"
              : result.metadata.validation_status === "corrected"
              ? "bg-yellow-700 text-yellow-100"
              : "bg-red-700 text-red-100"
          }`}
        >
          {result.metadata.validation_status}
        </span>
      </div>
      <SyntaxHighlighter
        language="json"
        style={atomOneDark}
        customStyle={{ margin: 0, padding: "1rem", maxHeight: "500px" }}
      >
        {jsonString}
      </SyntaxHighlighter>
    </div>
  );
}

export default ResultViewer;
