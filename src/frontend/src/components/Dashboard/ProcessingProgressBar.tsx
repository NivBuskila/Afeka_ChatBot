import React, { useEffect, useState } from 'react';
import { Clock, Check, AlertTriangle, RefreshCw } from 'lucide-react';
import { documentService } from '../../services/documentService';

interface ProcessingProgressBarProps {
  documentId: number;
  refreshInterval?: number; // in milliseconds, default 5000 (5 seconds)
}

const ProcessingProgressBar: React.FC<ProcessingProgressBarProps> = ({ 
  documentId,
  refreshInterval = 5000
}) => {
  const [processingData, setProcessingData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchProcessingStatus = async () => {
    try {
      setLoading(true);
      const data = await documentService.getProcessingStatus(documentId);
      setProcessingData(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching processing status:', err);
      setError('שגיאה בטעינת נתוני העיבוד');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProcessingStatus();
    
    // Set up polling if document is not completed and not failed
    const intervalId = setInterval(() => {
      if (processingData?.document?.status !== 'completed' && 
          processingData?.document?.status !== 'failed') {
        fetchProcessingStatus();
      }
    }, refreshInterval);
    
    return () => clearInterval(intervalId);
  }, [documentId, refreshInterval, processingData?.document?.status]);

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

  const { document, progress, chunks_count } = processingData;
  const status = document?.status || 'unknown';

  const getStatusIcon = () => {
    switch (status) {
      case 'pending':
        return <Clock className="w-4 h-4 text-yellow-400" />;
      case 'processing':
        return <RefreshCw className="w-4 h-4 text-blue-400 animate-spin" />;
      case 'completed':
        return <Check className="w-4 h-4 text-green-400" />;
      case 'failed':
        return <AlertTriangle className="w-4 h-4 text-red-400" />;
      default:
        return <Clock className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-400/20 text-yellow-400';
      case 'processing':
        return 'bg-blue-400/20 text-blue-400';
      case 'completed':
        return 'bg-green-400/20 text-green-400';
      case 'failed':
        return 'bg-red-400/20 text-red-400';
      default:
        return 'bg-gray-400/20 text-gray-400';
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'pending':
        return 'ממתין לעיבוד';
      case 'processing':
        return `מעבד... ${progress}%`;
      case 'completed':
        return `הושלם (${chunks_count} חלקים)`;
      case 'failed':
        return 'נכשל';
      default:
        return 'לא ידוע';
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
          {chunks_count > 0 && `${chunks_count} וקטורים`}
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