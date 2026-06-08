import { useCallback, useState } from "react";
import type { DragEvent, ChangeEvent } from "react";

interface UploadFormProps {
  onSubmit: (file: File) => void;
  isProcessing: boolean;
}

function UploadForm({ onSubmit, isProcessing }: UploadFormProps) {
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleDrop = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped) setFile(dropped);
  }, []);

  const handleDragOver = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setIsDragging(false);
  }, []);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) setFile(selected);
  };

  const handleSubmit = () => {
    if (file) onSubmit(file);
  };

  return (
    <div className="space-y-4">
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          isDragging
            ? "border-blue-500 bg-blue-50"
            : "border-gray-300 hover:border-gray-400"
        }`}
      >
        <p className="text-gray-600 mb-2">
          Drag & drop an invoice here, or click to select
        </p>
        <input
          type="file"
          accept=".pdf,.png,.jpeg,.jpg"
          onChange={handleFileChange}
          className="block mx-auto text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
        />
        {file && (
          <p className="mt-2 text-sm text-green-700 font-medium">
            Selected: {file.name}
          </p>
        )}
      </div>
      <button
        onClick={handleSubmit}
        disabled={!file || isProcessing}
        className="w-full py-3 px-4 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
      >
        {isProcessing ? "Processing..." : "Process Invoice"}
      </button>
    </div>
  );
}

export default UploadForm;
