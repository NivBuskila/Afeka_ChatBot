import React from 'react';
import { useTranslation } from 'react-i18next';
import { Brain, TrendingUp, Cpu } from 'lucide-react';
import { RAGProfile } from '../RAGService';

interface RAGOverviewProps {
  currentProfile: RAGProfile | undefined;
}

const RAGOverview: React.FC<RAGOverviewProps> = ({ currentProfile }) => {
  const { t } = useTranslation();

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {/* Current Profile Card */}
      <div className="bg-white/80 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-green-500/20 p-6 shadow-lg">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-green-600 dark:text-green-400">
            {t("rag.current.profile") || "פרופיל נוכחי"}
          </h3>
          <Brain className="w-6 h-6 text-green-600 dark:text-green-500" />
        </div>
        <div className="space-y-3">
          <div>
            <p className="text-gray-800 dark:text-green-300 font-semibold text-xl">
              {currentProfile?.name || "לא נמצא"}
            </p>
            <p className="text-gray-600 dark:text-green-400/70 text-sm">
              {currentProfile?.description || ""}
            </p>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-green-400/60 text-sm">
                {t("rag.similarity.threshold") || "סף דמיון"}:
              </span>
              <span className="text-gray-800 dark:text-green-300 text-sm">
                {currentProfile?.config.similarityThreshold || "N/A"}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-green-400/60 text-sm">
                {t("rag.max.chunks") || "צ'אנקים מקס"}:
              </span>
              <span className="text-gray-800 dark:text-green-300 text-sm">
                {currentProfile?.config.maxChunks || "N/A"}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-green-400/60 text-sm">
                {t("rag.temperature") || "טמפרטורה"}:
              </span>
              <span className="text-gray-800 dark:text-green-300 text-sm">
                {currentProfile?.config.temperature || "N/A"}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Profile Characteristics Card */}
      <div className="bg-white/80 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-blue-500/20 p-6 shadow-lg">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-blue-600 dark:text-blue-400">
            {t("rag.profileCharacteristics") || "מאפיינים"}
          </h3>
          <TrendingUp className="w-6 h-6 text-blue-600 dark:text-blue-500" />
        </div>
        <div className="space-y-3">
          <div>
            <p className="text-gray-600 dark:text-blue-400/70 text-sm">
              {t("rag.focus")}:
            </p>
            <p className="text-gray-800 dark:text-blue-300 text-sm">
              {currentProfile?.characteristics.focus || t("rag.notAvailable")}
            </p>
          </div>
          <div>
            <p className="text-gray-600 dark:text-blue-400/70 text-sm">
              {t("rag.expectedSpeed")}:
            </p>
            <p className="text-gray-800 dark:text-blue-300 text-sm">
              {currentProfile?.characteristics.expectedSpeed || t("rag.notAvailable")}
            </p>
          </div>
          <div>
            <p className="text-gray-600 dark:text-blue-400/70 text-sm">
              {t("rag.expectedQuality")}:
            </p>
            <p className="text-gray-800 dark:text-blue-300 text-sm">
              {currentProfile?.characteristics.expectedQuality || t("rag.notAvailable")}
            </p>
          </div>
        </div>
      </div>

      {/* Advanced Configuration Card */}
      <div className="bg-white/80 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-purple-500/20 p-6 shadow-lg">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-purple-600 dark:text-purple-400">
            {t("rag.configuration") || "קונפיגורציה מתקדמת"}
          </h3>
          <Cpu className="w-6 h-6 text-purple-600 dark:text-purple-500" />
        </div>
        <div className="space-y-2">
          {currentProfile?.config.chunkSize && (
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-purple-400/60 text-sm">
                {t("rag.chunkSize") || "גודל צ'אנק"}:
              </span>
              <span className="text-gray-800 dark:text-purple-300 text-sm">
                {currentProfile.config.chunkSize}
              </span>
            </div>
          )}
          {currentProfile?.config.chunkOverlap && (
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-purple-400/60 text-sm">
                {t("rag.chunkOverlap") || "חפיפת צ'אנקים"}:
              </span>
              <span className="text-gray-800 dark:text-purple-300 text-sm">
                {currentProfile.config.chunkOverlap}
              </span>
            </div>
          )}
          {currentProfile?.config.maxContextTokens && (
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-purple-400/60 text-sm">
                {t("rag.maxContext") || "קונטקסט מקס"}:
              </span>
              <span className="text-gray-800 dark:text-purple-300 text-sm">
                {currentProfile.config.maxContextTokens}
              </span>
            </div>
          )}
          {currentProfile?.config.hybridSemanticWeight && (
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-purple-400/60 text-sm">
                {t("rag.semanticWeight") || "משקל סמנטי"}:
              </span>
              <span className="text-gray-800 dark:text-purple-300 text-sm">
                {currentProfile.config.hybridSemanticWeight}
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RAGOverview; 