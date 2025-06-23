import React from 'react';
import { useTranslation } from 'react-i18next';
import { CheckCircle } from 'lucide-react';
import { RAGProfile } from '../RAGService';

type Language = "he" | "en";

interface PerformanceDashboardProps {
  profiles: RAGProfile[];
  language: Language;
}

const PerformanceDashboard: React.FC<PerformanceDashboardProps> = ({
  profiles,
  language,
}) => {
  const { t } = useTranslation();
  const activeProfile = profiles.find(p => p.isActive);

  return (
    <div className="space-y-6">
      {/* Current Profile Configuration */}
      <div className="bg-white/80 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-green-500/20 p-6 shadow-lg">
        <h3 className="text-lg font-semibold text-green-600 dark:text-green-400 mb-4">
          {t("rag.currentProfileConfig") || "קונפיגורציה פרופיל נוכחי"}
        </h3>
        
        {activeProfile ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600 dark:text-green-400 mb-2">
                {activeProfile.config.similarityThreshold}
              </div>
              <p className="text-sm text-gray-600 dark:text-green-400/70">
                {t("rag.similarity.threshold") || "סף דמיון"}
              </p>
            </div>
            
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 dark:text-blue-400 mb-2">
                {activeProfile.config.maxChunks}
              </div>
              <p className="text-sm text-gray-600 dark:text-green-400/70">
                {t("rag.max.chunks") || "צ'אנקים מקסימליים"}
              </p>
            </div>
            
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600 dark:text-purple-400 mb-2">
                {activeProfile.config.temperature}
              </div>
              <p className="text-sm text-gray-600 dark:text-green-400/70">
                {t("rag.temperature") || "טמפרטורה"}
              </p>
            </div>
          </div>
        ) : (
          <div className="text-center text-gray-500 dark:text-gray-400">
            {t("rag.noActiveProfile") || "אין פרופיל פעיל"}
          </div>
        )}

        {/* Advanced Configuration */}
        {activeProfile && (
          <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
            {activeProfile.config.chunkSize && (
              <div className="text-center">
                <div className="text-lg font-bold text-gray-800 dark:text-gray-300">
                  {activeProfile.config.chunkSize}
                </div>
                <p className="text-xs text-gray-600 dark:text-green-400/70">
                  {t("rag.chunkSize") || "גודל צ'אנק"}
                </p>
              </div>
            )}
            
            {activeProfile.config.chunkOverlap && (
              <div className="text-center">
                <div className="text-lg font-bold text-gray-800 dark:text-gray-300">
                  {activeProfile.config.chunkOverlap}
                </div>
                <p className="text-xs text-gray-600 dark:text-green-400/70">
                  {t("rag.chunkOverlap") || "חפיפת צ'אנקים"}
                </p>
              </div>
            )}
            
            {activeProfile.config.maxContextTokens && (
              <div className="text-center">
                <div className="text-lg font-bold text-gray-800 dark:text-gray-300">
                  {activeProfile.config.maxContextTokens}
                </div>
                <p className="text-xs text-gray-600 dark:text-green-400/70">
                  {t("rag.maxContext") || "קונטקסט מקס"}
                </p>
              </div>
            )}
            
            {activeProfile.config.hybridSemanticWeight && (
              <div className="text-center">
                <div className="text-lg font-bold text-gray-800 dark:text-gray-300">
                  {activeProfile.config.hybridSemanticWeight}
                </div>
                <p className="text-xs text-gray-600 dark:text-green-400/70">
                  {t("rag.semanticWeight") || "משקל סמנטי"}
                </p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Profile Characteristics */}
      {activeProfile && (
        <div className="bg-white/80 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-blue-500/20 p-6 shadow-lg">
          <h3 className="text-lg font-semibold text-blue-600 dark:text-blue-400 mb-4">
            {t("rag.profileCharacteristics") || "מאפייני הפרופיל"}
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="text-sm font-medium text-gray-600 dark:text-blue-400/70 mb-2">
                {t("rag.focus") || "מיקוד"}
              </h4>
              <p className="text-gray-800 dark:text-blue-300">
                {activeProfile.characteristics.focus || t("rag.notAvailable")}
              </p>
            </div>
            
            <div>
              <h4 className="text-sm font-medium text-gray-600 dark:text-blue-400/70 mb-2">
                {t("rag.expectedSpeed") || "מהירות צפויה"}
              </h4>
              <p className="text-gray-800 dark:text-blue-300">
                {activeProfile.characteristics.expectedSpeed || t("rag.notAvailable")}
              </p>
            </div>
            
            <div>
              <h4 className="text-sm font-medium text-gray-600 dark:text-blue-400/70 mb-2">
                {t("rag.expectedQuality") || "איכות צפויה"}
              </h4>
              <p className="text-gray-800 dark:text-blue-300">
                {activeProfile.characteristics.expectedQuality || t("rag.notAvailable")}
              </p>
            </div>
            
            <div>
              <h4 className="text-sm font-medium text-gray-600 dark:text-blue-400/70 mb-2">
                {t("rag.bestFor") || "מתאים ל"}
              </h4>
              <p className="text-gray-800 dark:text-blue-300">
                {activeProfile.characteristics.bestFor || t("rag.notAvailable")}
              </p>
            </div>
          </div>
          
          {activeProfile.characteristics.tradeoffs && (
            <div className="mt-4">
              <h4 className="text-sm font-medium text-gray-600 dark:text-blue-400/70 mb-2">
                {t("rag.tradeoffs") || "פשרות"}
              </h4>
              <p className="text-gray-800 dark:text-blue-300">
                {activeProfile.characteristics.tradeoffs}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Profiles Comparison Table */}
      <div className="bg-white/80 dark:bg-black/30 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-green-500/20 p-6 shadow-lg">
        <h3 className="text-lg font-semibold text-green-600 dark:text-green-400 mb-4">
          {t("rag.profilesComparison") || "השוואת פרופילים"}
        </h3>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-300 dark:border-green-500/20">
                <th className={`py-3 text-gray-800 dark:text-green-400 ${
                  language === "he" ? "text-right" : "text-left"
                }`}>
                  {t("rag.profileName") || "שם פרופיל"}
                </th>
                <th className={`py-3 text-gray-800 dark:text-green-400 ${
                  language === "he" ? "text-right" : "text-left"
                }`}>
                  {t("rag.similarity.threshold") || "סף דמיון"}
                </th>
                <th className={`py-3 text-gray-800 dark:text-green-400 ${
                  language === "he" ? "text-right" : "text-left"
                }`}>
                  {t("rag.max.chunks") || "צ'אנקים מקס"}
                </th>
                <th className={`py-3 text-gray-800 dark:text-green-400 ${
                  language === "he" ? "text-right" : "text-left"
                }`}>
                  {t("rag.focus") || "מיקוד"}
                </th>
                <th className={`py-3 text-gray-800 dark:text-green-400 ${
                  language === "he" ? "text-right" : "text-left"
                }`}>
                  {t("rag.status") || "סטטוס"}
                </th>
              </tr>
            </thead>
            <tbody>
              {profiles.map((profile) => (
                <tr
                  key={profile.id}
                  className="border-b border-gray-200 dark:border-green-500/10"
                >
                  <td className={`py-3 text-gray-800 dark:text-green-300 ${
                    language === "he" ? "text-right" : "text-left"
                  }`}>
                    {profile.name}
                  </td>
                  <td className={`py-3 text-gray-600 dark:text-green-400/70 ${
                    language === "he" ? "text-right" : "text-left"
                  }`}>
                    {profile.config.similarityThreshold}
                  </td>
                  <td className={`py-3 text-gray-600 dark:text-green-400/70 ${
                    language === "he" ? "text-right" : "text-left"
                  }`}>
                    {profile.config.maxChunks}
                  </td>
                  <td className={`py-3 text-gray-600 dark:text-green-400/70 ${
                    language === "he" ? "text-right" : "text-left"
                  } max-w-xs truncate`}>
                    {profile.characteristics.focus}
                  </td>
                  <td className={`py-3 ${
                    language === "he" ? "text-right" : "text-left"
                  }`}>
                    {profile.isActive ? (
                      <div className="flex items-center text-green-600 dark:text-green-400">
                        <CheckCircle className="w-4 h-4 mr-1" />
                        <span className="text-sm font-medium">
                          {language === "he" ? "פעיל" : "Active"}
                        </span>
                      </div>
                    ) : (
                      <span className="text-gray-400 dark:text-gray-500 text-sm">
                        {language === "he" ? "לא פעיל" : "Inactive"}
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default PerformanceDashboard; 