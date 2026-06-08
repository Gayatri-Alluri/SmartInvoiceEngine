interface PipelineStatusProps {
  stages_completed: string[];
  current_stage: string;
  status: string;
}

const STAGES = ["ocr", "extraction", "validation", "correction", "formatting", "complete"];
const STAGE_LABELS: Record<string, string> = {
  ocr: "OCR",
  extraction: "Extraction",
  validation: "Validation",
  correction: "Correction",
  formatting: "Formatting",
  complete: "Complete",
};

function PipelineStatus({ stages_completed, current_stage, status }: PipelineStatusProps) {
  return (
    <div className="flex items-center justify-between py-4">
      {STAGES.map((stage, i) => {
        const isCompleted = stages_completed.includes(stage) || (status === "completed" && stage === "complete");
        const isCurrent = current_stage === stage && status === "processing";

        return (
          <div key={stage} className="flex items-center">
            <div className="flex flex-col items-center">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                  isCompleted
                    ? "bg-green-500 text-white"
                    : isCurrent
                    ? "bg-blue-500 text-white animate-pulse"
                    : "bg-gray-200 text-gray-500"
                }`}
              >
                {isCompleted ? "✓" : i + 1}
              </div>
              <span className="mt-1 text-xs text-gray-600">
                {STAGE_LABELS[stage]}
              </span>
            </div>
            {i < STAGES.length - 1 && (
              <div
                className={`w-12 h-0.5 mx-1 ${
                  stages_completed.includes(stage) ? "bg-green-500" : "bg-gray-200"
                }`}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}

export default PipelineStatus;
