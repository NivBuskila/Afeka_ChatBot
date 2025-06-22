import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Clock } from 'lucide-react';
import { RAGProfile } from '../RAGService';

type Language = "he" | "en";

interface CreateProfileModalProps {
  language: Language;
  onSubmit: (profileData: Partial<RAGProfile>) => void;
  onCancel: () => void;
  isCreating: boolean;
}

const CreateProfileModal: React.FC<CreateProfileModalProps> = ({
  onSubmit,
  onCancel,
  isCreating,
}) => {
  const { t } = useTranslation();
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    config: {
      similarityThreshold: 0.4,
      maxChunks: 15,
      temperature: 0.1,
      modelName: "gemini-2.0-flash",
      chunkSize: 1500,
      chunkOverlap: 200,
      maxContextTokens: 8000,
      targetTokensPerChunk: 300,
      hybridSemanticWeight: 0.7,
      hybridKeywordWeight: 0.3,
    },
    characteristics: {
      focus: "",
      expectedSpeed: "",
      expectedQuality: "",
      bestFor: "",
      tradeoffs: "",
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name.trim()) return;

    onSubmit({
      id: formData.name.toLowerCase().replace(/\s+/g, "_"),
      name: formData.name,
      description: formData.description,
      config: formData.config,
      characteristics: formData.characteristics,
      isActive: false,
    });
  };

  const handleConfigChange = (key: string, value: number | string) => {
    setFormData((prev) => ({
      ...prev,
      config: {
        ...prev.config,
        [key]: value,
      },
    }));
  };

  const handleCharacteristicChange = (key: string, value: string) => {
    setFormData((prev) => ({
      ...prev,
      characteristics: {
        ...prev.characteristics,
        [key]: value,
      },
    }));
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-black/80 backdrop-blur-lg rounded-lg border border-gray-300 dark:border-green-500/30 max-w-4xl w-full max-h-[90vh] overflow-y-auto shadow-2xl">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-semibold text-gray-800 dark:text-green-400">
              {t("rag.create.new.profile") || "יצירת פרופיל חדש"}
            </h3>
            <button
              onClick={onCancel}
              className="text-gray-600 dark:text-green-400/70 hover:text-gray-800 dark:hover:text-green-400 text-xl"
            >
              ✕
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Basic Profile Details */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-green-400 mb-2">
                  {t("rag.profileFormName") || "שם הפרופיל"}
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) =>
                    setFormData((prev) => ({ ...prev, name: e.target.value }))
                  }
                  className="w-full px-4 py-2 bg-white dark:bg-black/50 border border-gray-300 dark:border-green-500/30 rounded-lg text-gray-800 dark:text-green-300 placeholder-gray-500 dark:placeholder-green-400/50 focus:border-green-500 dark:focus:border-green-500/50 focus:outline-none"
                  placeholder={
                    t("rag.profileFormNamePlaceholder") || "הכנס שם לפרופיל..."
                  }
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-green-400 mb-2">
                  {t("rag.profileFormDescription") || "תיאור"}
                </label>
                <input
                  type="text"
                  value={formData.description}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      description: e.target.value,
                    }))
                  }
                  className="w-full px-4 py-2 bg-white dark:bg-black/50 border border-gray-300 dark:border-green-500/30 rounded-lg text-gray-800 dark:text-green-300 placeholder-gray-500 dark:placeholder-green-400/50 focus:border-green-500 dark:focus:border-green-500/50 focus:outline-none"
                  placeholder={
                    t("rag.profileFormDescriptionPlaceholder") ||
                    "תיאור הפרופיל..."
                  }
                />
              </div>
            </div>

            {/* Advanced Configuration */}
            <div className="border-t border-gray-200 dark:border-green-500/20 pt-6">
              <h4 className="text-lg font-medium text-gray-800 dark:text-green-400 mb-4">
                {t("rag.configurationSettings") || "הגדרות קונפיגורציה"}
              </h4>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {/* Similarity Threshold */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-green-400 mb-2">
                    {t("rag.similarity.threshold") || "סף דמיון"} ({formData.config.similarityThreshold})
                  </label>
                  <input
                    type="range"
                    min="0.1"
                    max="1.0"
                    step="0.1"
                    value={formData.config.similarityThreshold}
                    onChange={(e) => handleConfigChange('similarityThreshold', parseFloat(e.target.value))}
                    className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer"
                  />
                  <div className="flex justify-between text-xs text-gray-500 dark:text-green-400/50 mt-1">
                    <span>0.1</span>
                    <span>1.0</span>
                  </div>
                </div>

                {/* Max Chunks */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-green-400 mb-2">
                    {t("rag.max.chunks") || "צ'אנקים מקסימליים"}
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="50"
                    value={formData.config.maxChunks}
                    onChange={(e) => handleConfigChange('maxChunks', parseInt(e.target.value))}
                    className="w-full px-3 py-2 bg-white dark:bg-black/50 border border-gray-300 dark:border-green-500/30 rounded-lg text-gray-800 dark:text-green-300 focus:border-green-500 dark:focus:border-green-500/50 focus:outline-none"
                  />
                </div>

                {/* Temperature */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-green-400 mb-2">
                    {t("rag.temperature") || "טמפרטורה"} ({formData.config.temperature})
                  </label>
                  <input
                    type="range"
                    min="0.0"
                    max="1.0"
                    step="0.1"
                    value={formData.config.temperature}
                    onChange={(e) => handleConfigChange('temperature', parseFloat(e.target.value))}
                    className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer"
                  />
                  <div className="flex justify-between text-xs text-gray-500 dark:text-green-400/50 mt-1">
                    <span>0.0</span>
                    <span>1.0</span>
                  </div>
                </div>

                {/* Model Name */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-green-400 mb-2">
                    {t("rag.model.name") || "שם המודל"}
                  </label>
                  <select
                    value={formData.config.modelName}
                    onChange={(e) => handleConfigChange('modelName', e.target.value)}
                    className="w-full px-3 py-2 bg-white dark:bg-black/50 border border-gray-300 dark:border-green-500/30 rounded-lg text-gray-800 dark:text-green-300 focus:border-green-500 dark:focus:border-green-500/50 focus:outline-none"
                  >
                    <option value="gemini-2.0-flash">Gemini 2.0 Flash</option>
                    <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
                    <option value="gemini-1.5-flash">Gemini 1.5 Flash</option>
                  </select>
                </div>

                {/* Chunk Size */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-green-400 mb-2">
                    {t("rag.chunkSize") || "גודל צ'אנק"}
                  </label>
                  <input
                    type="number"
                    min="500"
                    max="3000"
                    step="100"
                    value={formData.config.chunkSize}
                    onChange={(e) => handleConfigChange('chunkSize', parseInt(e.target.value))}
                    className="w-full px-3 py-2 bg-white dark:bg-black/50 border border-gray-300 dark:border-green-500/30 rounded-lg text-gray-800 dark:text-green-300 focus:border-green-500 dark:focus:border-green-500/50 focus:outline-none"
                  />
                </div>

                {/* Max Context Tokens */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-green-400 mb-2">
                    {t("rag.maxContext") || "טוקנים מקסימליים"}
                  </label>
                  <input
                    type="number"
                    min="2000"
                    max="16000"
                    step="1000"
                    value={formData.config.maxContextTokens}
                    onChange={(e) => handleConfigChange('maxContextTokens', parseInt(e.target.value))}
                    className="w-full px-3 py-2 bg-white dark:bg-black/50 border border-gray-300 dark:border-green-500/30 rounded-lg text-gray-800 dark:text-green-300 focus:border-green-500 dark:focus:border-green-500/50 focus:outline-none"
                  />
                </div>
              </div>
            </div>

            {/* Characteristics */}
            <div className="border-t border-gray-200 dark:border-green-500/20 pt-6">
              <h4 className="text-lg font-medium text-gray-800 dark:text-green-400 mb-4">
                {t("rag.characteristics") || "מאפיינים"}
              </h4>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-green-400 mb-2">
                    {t("rag.focus") || "מיקוד"}
                  </label>
                  <textarea
                    rows={3}
                    value={formData.characteristics.focus}
                    onChange={(e) => handleCharacteristicChange('focus', e.target.value)}
                    className="w-full px-3 py-2 bg-white dark:bg-black/50 border border-gray-300 dark:border-green-500/30 rounded-lg text-gray-800 dark:text-green-300 placeholder-gray-500 dark:placeholder-green-400/50 focus:border-green-500 dark:focus:border-green-500/50 focus:outline-none"
                    placeholder={t("rag.focusPlaceholder") || "על מה הפרופיל מתמקד..."}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-green-400 mb-2">
                    {t("rag.bestFor") || "מתאים עבור"}
                  </label>
                  <textarea
                    rows={3}
                    value={formData.characteristics.bestFor}
                    onChange={(e) => handleCharacteristicChange('bestFor', e.target.value)}
                    className="w-full px-3 py-2 bg-white dark:bg-black/50 border border-gray-300 dark:border-green-500/30 rounded-lg text-gray-800 dark:text-green-300 placeholder-gray-500 dark:placeholder-green-400/50 focus:border-green-500 dark:focus:border-green-500/50 focus:outline-none"
                    placeholder={t("rag.bestForPlaceholder") || "מתאים ביותר עבור..."}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-green-400 mb-2">
                    {t("rag.expectedSpeed") || "מהירות צפויה"}
                  </label>
                  <select
                    value={formData.characteristics.expectedSpeed}
                    onChange={(e) => handleCharacteristicChange('expectedSpeed', e.target.value)}
                    className="w-full px-3 py-2 bg-white dark:bg-black/50 border border-gray-300 dark:border-green-500/30 rounded-lg text-gray-800 dark:text-green-300 focus:border-green-500 dark:focus:border-green-500/50 focus:outline-none"
                  >
                    <option value="">{t("selectSpeed") || "בחר מהירות..."}</option>
                    <option value="Fast">{t("fast") || "מהיר"}</option>
                    <option value="Medium">{t("medium") || "בינוני"}</option>
                    <option value="Slow">{t("slow") || "איטי"}</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-green-400 mb-2">
                    {t("rag.expectedQuality") || "איכות צפויה"}
                  </label>
                  <select
                    value={formData.characteristics.expectedQuality}
                    onChange={(e) => handleCharacteristicChange('expectedQuality', e.target.value)}
                    className="w-full px-3 py-2 bg-white dark:bg-black/50 border border-gray-300 dark:border-green-500/30 rounded-lg text-gray-800 dark:text-green-300 focus:border-green-500 dark:focus:border-green-500/50 focus:outline-none"
                  >
                    <option value="">{t("selectQuality") || "בחר איכות..."}</option>
                    <option value="High">{t("high") || "גבוה"}</option>
                    <option value="Medium">{t("medium") || "בינוני"}</option>
                    <option value="Basic">{t("basic") || "בסיסי"}</option>
                  </select>
                </div>
              </div>

              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700 dark:text-green-400 mb-2">
                  {t("rag.tradeoffs") || "איזונים"}
                </label>
                <textarea
                  rows={2}
                  value={formData.characteristics.tradeoffs}
                  onChange={(e) => handleCharacteristicChange('tradeoffs', e.target.value)}
                  className="w-full px-3 py-2 bg-white dark:bg-black/50 border border-gray-300 dark:border-green-500/30 rounded-lg text-gray-800 dark:text-green-300 placeholder-gray-500 dark:placeholder-green-400/50 focus:border-green-500 dark:focus:border-green-500/50 focus:outline-none"
                  placeholder={t("rag.tradeoffsPlaceholder") || "מה הפשרות בפרופיל הזה..."}
                />
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex justify-end space-x-4">
              <button
                type="button"
                onClick={onCancel}
                className="px-6 py-2 border border-gray-300 dark:border-green-500/30 text-gray-700 dark:text-green-400 rounded-lg hover:bg-gray-100 dark:hover:bg-green-500/10 transition-colors"
              >
                {t("rag.cancel") || "ביטול"}
              </button>
              <button
                type="submit"
                disabled={isCreating || !formData.name.trim()}
                className="px-6 py-2 bg-green-100 dark:bg-green-500/20 border border-green-300 dark:border-green-500/30 text-green-800 dark:text-green-400 rounded-lg hover:bg-green-200 dark:hover:bg-green-500/30 transition-colors disabled:opacity-50 flex items-center space-x-2"
              >
                {isCreating ? (
                  <>
                    <Clock className="w-4 h-4 animate-spin" />
                    <span>{t("rag.creating") || "יוצר..."}</span>
                  </>
                ) : (
                  <span>{t("rag.create.profile") || "צור פרופיל"}</span>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default CreateProfileModal; 