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