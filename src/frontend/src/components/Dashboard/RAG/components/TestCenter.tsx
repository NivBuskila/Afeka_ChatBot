import React from 'react';
import { useTranslation } from 'react-i18next';
import { Search } from 'lucide-react';
import { RAGTestResult } from '../RAGService';
import AIResponseRenderer from '../../../common/AIResponseRenderer';

type Language = "he" | "en";

interface TestCenterProps {
  testQuery: string;
  setTestQuery: (value: string) => void;
  testResult: RAGTestResult | null;
  isRunningTest: boolean;
  showFullChunk: boolean;
  onRunTest: () => void;
  onToggleChunk: () => void;
  language: Language;
}

const TestCenter: React.FC<TestCenterProps> = ({
  testQuery,
  setTestQuery,
  testResult,
  isRunningTest,
  showFullChunk,
  onRunTest,
  onToggleChunk,
  language,
}) => {
  const { t } = useTranslation();

  return (
    <div className="space-y-6">
      {/* Test Interface */}
      <div className="bg-white/80 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-green-500/20 p-6 shadow-lg">
        <h3 className="text-xl font-semibold text-gray-800 dark:text-green-400 mb-4">
          {t("rag.test.center") || "מרכז בדיקות RAG"}
        </h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm text-gray-600 dark:text-green-400/70 mb-2">
              {t("rag.test.query") || "שאילתת בדיקה"}
            </label>
            <div className="relative">
              <textarea
                value={testQuery}
                onChange={(e) => setTestQuery(e.target.value)}
                className="w-full h-24 px-4 py-3 bg-white dark:bg-black/50 border border-gray-300 dark:border-green-500/30 rounded-lg text-gray-800 dark:text-green-300 focus:border-green-500 dark:focus:border-green-500/50 focus:outline-none resize-none"
                placeholder={
                  language === "he"
                    ? "הכנס שאילתה לבדיקת המערכת..."
                    : "Enter a query to test the system..."
                }
                dir={language === "he" ? "rtl" : "ltr"}
              />
            </div>
          </div>

          <button
            onClick={onRunTest}
            disabled={!testQuery.trim() || isRunningTest}
            className="w-full bg-green-600 dark:bg-green-500/20 hover:bg-green-700 dark:hover:bg-green-500/30 text-white dark:text-green-400 font-medium py-3 px-4 rounded-lg border border-green-600 dark:border-green-500/30 transition-colors flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isRunningTest ? (
              <div className="flex items-center space-x-2">
                <div className="w-4 h-4 border-2 border-white dark:border-green-400 border-t-transparent rounded-full animate-spin" />
                <span>{t("running.test") || "מריץ בדיקה..."}</span>
              </div>
            ) : (
              <>
                <Search className="w-5 h-5" />
                <span>{t("rag.run.test") || "הרץ בדיקה"}</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Test Results */}
      {testResult && (
        <div className="bg-gray-50 dark:bg-black/50 rounded-lg p-6 border border-gray-200 dark:border-green-500/20">
          <h4 className="text-lg font-semibold text-gray-800 dark:text-green-400 mb-4">
            {t("rag.test.results") || "תוצאות הבדיקה"}
          </h4>
          
          <div className="space-y-4">
            {/* Query */}
            <div>
              <p className="text-sm text-gray-600 dark:text-green-400/70 mb-2">
                {t("rag.query") || "שאילתה"}:
              </p>
              <div 
                className="text-gray-800 dark:text-green-300 bg-white dark:bg-black/30 p-3 rounded border border-gray-200 dark:border-green-500/10" 
                dir={language === "he" ? "rtl" : "ltr"}
              >
                {testResult.query}
              </div>
            </div>

            {/* Answer */}
            <div>
              <p className="text-sm text-gray-600 dark:text-green-400/70 mb-2">
                {t("rag.answer") || "תשובה"}:
              </p>
              <div className="bg-white dark:bg-black/30 p-4 rounded border border-gray-200 dark:border-green-500/10">
                <AIResponseRenderer 
                  content={testResult.answer}
                  className="text-gray-800 dark:text-green-300"
                />
              </div>
            </div>

            {/* Source Information */}
            {testResult.chunkText && (
              <div>
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm text-gray-600 dark:text-green-400/70">
                    {t("rag.source.chunk") || "מקור המידע"}:
                  </p>
                  <div className="flex items-center space-x-3 text-xs text-gray-500 dark:text-green-400/50">
                    {testResult.similarity && (
                      <span>
                        {t("rag.similarity") || "דמיון"}: {(testResult.similarity * 100).toFixed(1)}%
                      </span>
                    )}
                    {testResult.documentTitle && (
                      <span>
                        {t("rag.document") || "מסמך"}: {testResult.documentTitle}
                      </span>
                    )}
                  </div>
                </div>
                
                <div className="bg-blue-50 dark:bg-blue-500/10 p-4 rounded border border-blue-200 dark:border-blue-500/20">
                  <div 
                    className="text-gray-800 dark:text-blue-300" 
                    dir={language === "he" ? "rtl" : "ltr"}
                  >
                    {showFullChunk 
                      ? testResult.chunkText 
                      : testResult.chunkText.length > 200 
                        ? testResult.chunkText.substring(0, 200) + "..."
                        : testResult.chunkText
                    }
                  </div>
                  
                  {testResult.chunkText.length > 200 && (
                    <button
                      onClick={onToggleChunk}
                      className="mt-3 text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 text-sm font-medium flex items-center gap-1 transition-colors"
                    >
                      {showFullChunk ? (
                        <>
                          <span>{t("rag.showLess") || "הצג פחות"}</span>
                          <svg
                            className="w-4 h-4 transform rotate-180"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M19 9l-7 7-7-7"
                            />
                          </svg>
                        </>
                      ) : (
                        <>
                          <span>{t("rag.viewMore") || "הצג עוד"}</span>
                          <svg
                            className="w-4 h-4"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M19 9l-7 7-7-7"
                            />
                          </svg>
                        </>
                      )}
                    </button>
                  )}
                </div>
              </div>
            )}

            {/* Performance Metrics */}
            {(testResult.responseTime || testResult.chunks) && (
              <div className="bg-green-50 dark:bg-green-500/10 p-4 rounded border border-green-200 dark:border-green-500/20">
                <p className="text-sm text-gray-600 dark:text-green-400/70 mb-2">
                  {t("performance.metrics") || "מדדי ביצועים"}:
                </p>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  {testResult.responseTime && (
                    <div>
                      <span className="text-gray-600 dark:text-green-400/70">
                        {t("rag.response.time") || "זמן תגובה"}:
                      </span>
                      <span className="text-gray-800 dark:text-green-300 ml-2">
                        {testResult.responseTime}ms
                      </span>
                    </div>
                  )}
                  {testResult.chunks && (
                    <div>
                      <span className="text-gray-600 dark:text-green-400/70">
                        {t("chunks.found") || "צ'אנקים שנמצאו"}:
                      </span>
                      <span className="text-gray-800 dark:text-green-300 ml-2">
                        {testResult.chunks}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default TestCenter; 