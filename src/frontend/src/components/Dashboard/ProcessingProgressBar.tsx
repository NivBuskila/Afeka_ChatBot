import React, { useEffect, useState, useRef } from "react";
import { Clock, Check, AlertTriangle, RefreshCw } from "lucide-react";
import { documentService } from "../../services/documentService";

interface ProcessingProgressBarProps {
  documentId: number;
  refreshInterval?: number; // in milliseconds, default 10000 (10 seconds)
  maxPollingTime?: number; // in milliseconds, default 120000 (2 minutes)
}

const ProcessingProgressBar: React.FC<ProcessingProgressBarProps> = ({
  documentId,
  refreshInterval = 10000,
  maxPollingTime = 120000,
}) => {
  const [processingData, setProcessingData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [pollingTimeout, setPollingTimeout] = useState<boolean>(false);
  const [forceCompleted, setForceCompleted] = useState<boolean>(false);
  const startTimeRef = useRef<number>(Date.now());
  const pollCountRef = useRef<number>(0);

  const fetchProcessingStatus = async () => {
    try {
      setLoading(true);
      pollCountRef.current += 1;
      const data = await documentService.getProcessingStatus(documentId);

      // If we have chunks but no status, force completed state
      if (
        data &&
        data.chunk_count > 0 &&
        (!data.status || data.status === "processing")
      ) {
        if (pollCountRef.current > 5) {
          // After 5 polls with chunks but no completion
          setForceCompleted(true);
          data.status = "completed";
        }
      }

      setProcessingData(data);
      setError(null);
    } catch (err) {
      console.error("Error fetching processing status:", err);
      setError("שגיאה בטעינת נתוני העיבוד");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProcessingStatus();

    // Set up polling if document is not completed and not failed
    const intervalId = setInterval(() => {
      // Check if we've exceeded the maximum polling time
      const elapsedTime = Date.now() - startTimeRef.current;
      if (elapsedTime > maxPollingTime) {
        setPollingTimeout(true);

        // If we have chunk data but timed out, force completion status
        if (processingData?.chunk_count > 0) {
          setForceCompleted(true);
        }

        clearInterval(intervalId);
        return;
      }

      // Check if status is completed or failed
      if (
        processingData?.status === "completed" ||
        processingData?.status === "failed" ||
        forceCompleted
      ) {
        clearInterval(intervalId);
      } else {
        fetchProcessingStatus();
      }
    }, refreshInterval);

    return () => clearInterval(intervalId);
  }, [
    documentId,
    refreshInterval,
    processingData?.status,
    processingData?.chunk_count,
    maxPollingTime,
    forceCompleted,
  ]);

  if (loading && !processingData) {
    return (
      <div className="flex items-center space-x-2 text-green-400/70">
        <RefreshCw className="w-4 h-4 animate-spin" />
        <span className="text-sm">טוען נתונים...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center space-x-2 text-red-400">
        <AlertTriangle className="w-4 h-4" />
        <span className="text-sm">{error}</span>
      </div>
    );
  }

  if (!processingData) {
    return null;
  }

  // Extract data from processing response
  const { status: rawStatus, chunk_count } = processingData;
  // Use forced completed status if applicable
  const status = forceCompleted ? "completed" : rawStatus;
  // Set progress to 100% if chunks exist or status is completed
  const progress =
    processingData.chunk_count > 0 || status === "completed" ? 100 : 0;

  const getStatusIcon = () => {
    switch (status) {
      case "pending":
        return <Clock className="w-4 h-4 text-yellow-400" />;
      case "processing":
        return <RefreshCw className="w-4 h-4 text-blue-400 animate-spin" />;
      case "completed":
        return <Check className="w-4 h-4 text-green-400" />;
      case "failed":
        return <AlertTriangle className="w-4 h-4 text-red-400" />;
      default:
        return <Clock className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case "pending":
        return "bg-yellow-400/20 text-yellow-400";
      case "processing":
        return "bg-blue-400/20 text-blue-400";
      case "completed":
        return "bg-green-400/20 text-green-400";
      case "failed":
        return "bg-red-400/20 text-red-400";
      default:
        return "bg-gray-400/20 text-gray-400";
    }
  };

  const getStatusText = () => {
    // Safely get chunk count with fallback
    const chunks =
      chunk_count ||
      processingData?.chunks_processed ||
      processingData?.total_chunks ||
      0;

    switch (status) {
      case "pending":
        return "ממתין לעיבוד";
      case "processing":
        return `מעבד...`;
      case "completed":
        return `הושלם${forceCompleted ? " (אוטומטי)" : ""} (${chunks} חלקים)`;
      case "failed":
        return "נכשל";
      default:
        return pollingTimeout ? `הושלם (${chunks} חלקים)` : "לא ידוע";
    }
  };

  return (
    <div className="w-full">
      <div className="flex items-center mb-1 justify-between">
        <div className="flex items-center space-x-2">
          {getStatusIcon()}
          <span className="text-sm font-medium">{getStatusText()}</span>
        </div>
        <span className="text-xs text-green-400/70">
          {(() => {
            const chunks =
              chunk_count ||
              processingData?.chunks_processed ||
              processingData?.total_chunks ||
              0;
            return chunks > 0 ? `${chunks} וקטורים` : "";
          })()}
        </span>
      </div>
      <div className="w-full bg-black/50 rounded-full h-2 overflow-hidden">
        <div
          className={`h-full rounded-full ${getStatusColor()}`}
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  );
};

export default ProcessingProgressBar;
