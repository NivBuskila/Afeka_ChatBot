import { useState } from 'react';
import { ragService, RAGTestResult } from '../RAGService';

export function useRAGTesting() {
  const [testQuery, setTestQuery] = useState("");
  const [testResult, setTestResult] = useState<RAGTestResult | null>(null);
  const [isRunningTest, setIsRunningTest] = useState(false);
  const [showFullChunk, setShowFullChunk] = useState(false);

  const handleRunTest = async () => {
    if (!testQuery.trim()) return;

    setIsRunningTest(true);
    setShowFullChunk(false); // Reset chunk display
    try {
      const testResponse = await ragService.testQuery(testQuery);
      setTestResult(testResponse);
    } catch (error) {
      console.error("Error running test:", error);
      throw new Error("Failed to run test query");
    } finally {
      setIsRunningTest(false);
    }
  };

  const clearTest = () => {
    setTestResult(null);
    setTestQuery("");
    setShowFullChunk(false);
  };

  return {
    testQuery,
    setTestQuery,
    testResult,
    setTestResult,
    isRunningTest,
    showFullChunk,
    setShowFullChunk,
    handleRunTest,
    clearTest,
  };
} 