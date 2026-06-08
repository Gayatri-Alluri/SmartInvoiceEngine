import UploadForm from "./components/UploadForm";
import PipelineStatus from "./components/PipelineStatus";
import ResultViewer from "./components/ResultViewer";
import DownloadButton from "./components/DownloadButton";
import useProcessInvoice from "./hooks/useProcessInvoice";

function App() {
  const { upload, status, result, error, isProcessing } = useProcessInvoice();

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="mx-auto max-w-4xl px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900">
            Smart Invoice Engine
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            AI-powered invoice-to-JSON processor
          </p>
        </div>
      </header>
      <main className="mx-auto max-w-4xl px-4 py-8 space-y-6">
        <UploadForm onSubmit={upload} isProcessing={isProcessing} />

        {status && (
          <PipelineStatus
            stages_completed={status.stages_completed}
            current_stage={status.current_stage}
            status={status.status}
          />
        )}

        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-700 font-medium">Error: {error}</p>
          </div>
        )}

        {result && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-800">Result</h2>
              <DownloadButton result={result} filename={status?.current_stage || "invoice"} />
            </div>
            <ResultViewer result={result} />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
