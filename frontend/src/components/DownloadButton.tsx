import type { InvoiceJSON } from "../types/invoice";

interface DownloadButtonProps {
  result: InvoiceJSON;
  filename: string;
}

function DownloadButton({ result, filename }: DownloadButtonProps) {
  const handleDownload = () => {
    const json = JSON.stringify(result, null, 2);
    const blob = new Blob([json], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename.replace(/\.[^.]+$/, "") + ".json";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <button
      onClick={handleDownload}
      className="py-2 px-4 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 transition-colors"
    >
      Download JSON
    </button>
  );
}

export default DownloadButton;
