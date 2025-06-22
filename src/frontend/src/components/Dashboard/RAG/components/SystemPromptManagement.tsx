import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import {
  Save,
  RotateCcw,
  AlertCircle,
  CheckCircle,
  Clock,
  User,
  History,
  Eye,
  EyeOff,
} from "lucide-react";

// Services
import { systemPromptService } from "../../../../services/systemPromptService";

// Types
interface SystemPrompt {
  id: string;
  prompt_text: string;
  version: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  updated_by: string | null;
  notes: string | null;
  updated_by_email: string | null;
}

interface SystemPromptManagementProps {
  language: "he" | "en";
}

export const SystemPromptManagement: React.FC<SystemPromptManagementProps> = ({
  language,
}) => {
  const { t } = useTranslation();

  // State
  const [currentPrompt, setCurrentPrompt] = useState<SystemPrompt | null>(null);
  const [promptHistory, setPromptHistory] = useState<SystemPrompt[]>([]);
  const [editedPrompt, setEditedPrompt] = useState<string>("");
  const [notes, setNotes] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [resetting, setResetting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [showHistory, setShowHistory] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [showResetConfirm, setShowResetConfirm] = useState(false);

  // Load current prompt and history
  useEffect(() => {
    loadCurrentPrompt();
    loadPromptHistory();
  }, []);

  // Check for unsaved changes
  useEffect(() => {
    if (currentPrompt) {
      const hasChanges =
        editedPrompt !== currentPrompt.prompt_text ||
        notes !== (currentPrompt.notes || "");
      setHasUnsavedChanges(hasChanges);
    }
  }, [editedPrompt, notes, currentPrompt]);

  const loadCurrentPrompt = async () => {
    try {
      setLoading(true);
      const prompt = await systemPromptService.getCurrentPrompt();
      setCurrentPrompt(prompt);
      setEditedPrompt(prompt.prompt_text);
      setNotes(prompt.notes || "");
      setError(null);
    } catch (err: any) {
      setError(err.message || "Failed to load current system prompt");
    } finally {
      setLoading(false);
    }
  };

  const loadPromptHistory = async () => {
    try {
      const history = await systemPromptService.getPromptHistory(10);
      setPromptHistory(history);
    } catch (err: any) {
      console.error("Failed to load prompt history:", err);
    }
  };

  const handleSave = async () => {
    if (!currentPrompt || !editedPrompt.trim()) {
      setError(
        language === "he"
          ? "הנחיות המערכת לא יכולות להיות ריקות"
          : "System prompt cannot be empty"
      );
      return;
    }

    try {
      setSaving(true);
      setError(null);

      const updatedPrompt = await systemPromptService.updatePrompt(
        currentPrompt.id,
        {
          prompt_text: editedPrompt.trim(),
          notes: notes.trim() || null,
        }
      );

      setCurrentPrompt(updatedPrompt);
      setSuccess(
        language === "he"
          ? "הנחיות המערכת עודכנו בהצלחה"
          : "System prompt updated successfully"
      );
      setHasUnsavedChanges(false);

      // Refresh history
      await loadPromptHistory();

      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(
        err.message ||
          (language === "he"
            ? "נכשל בשמירת הנחיות המערכת"
            : "Failed to save system prompt")
      );
    } finally {
      setSaving(false);
    }
  };

  const handleResetToDefault = () => {
    setShowResetConfirm(true);
  };

  const handleConfirmReset = async () => {
    setShowResetConfirm(false);

    try {
      setResetting(true);
      setError(null);

      const defaultPrompt = await systemPromptService.resetToDefault();
      setCurrentPrompt(defaultPrompt);
      setEditedPrompt(defaultPrompt.prompt_text);
      setNotes(defaultPrompt.notes || "");
      setSuccess(
        language === "he"
          ? "הנחיות המערכת אופסו לברירת המחדל בהצלחה"
          : "System prompt reset to default successfully"
      );
      setHasUnsavedChanges(false);

      // Refresh history
      await loadPromptHistory();

      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(
        err.message ||
          (language === "he"
            ? "נכשל באיפוס הנחיות המערכת"
            : "Failed to reset system prompt")
      );
    } finally {
      setResetting(false);
    }
  };

  const handleActivateVersion = async (promptId: string) => {
    try {
      setError(null);

      const activatedPrompt = await systemPromptService.activatePrompt(
        promptId
      );
      setCurrentPrompt(activatedPrompt);
      setEditedPrompt(activatedPrompt.prompt_text);
      setNotes(activatedPrompt.notes || "");
      setSuccess("System prompt version activated successfully");
      setHasUnsavedChanges(false);

      // Refresh history
      await loadPromptHistory();

      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(err.message || "Failed to activate system prompt version");
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString(
      language === "he" ? "he-IL" : "en-US"
    );
  };

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center">
        <div className="text-gray-700 dark:text-green-400">
          <Clock className="w-8 h-8 animate-spin mx-auto mb-2" />
          <p>
            {language === "he"
              ? "טוען הנחיות מערכת..."
              : "Loading system prompt..."}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-xl font-bold text-gray-800 dark:text-green-400">
            {t("rag.system.prompt")}
          </h3>
          {currentPrompt && (
            <p className="text-sm text-gray-600 dark:text-green-400/70">
              {language === "he" ? "גרסה נוכחית" : "Current Version"}:{" "}
              {currentPrompt.version} |{" "}
              {language === "he" ? "עודכן לאחרונה" : "Last Updated"}:{" "}
              {formatDate(currentPrompt.updated_at)}
              {currentPrompt.updated_by_email && (
                <span>
                  {" "}
                  {language === "he" ? "על ידי" : "by"}{" "}
                  {currentPrompt.updated_by_email}
                </span>
              )}
            </p>
          )}
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors flex items-center gap-2"
          >
            <History className="w-4 h-4" />
            {showHistory
              ? language === "he"
                ? "הסתר היסטוריה"
                : "Hide History"
              : language === "he"
              ? "הצג היסטוריה"
              : "Show History"}
          </button>
        </div>
      </div>

      {/* Error and Success Messages */}
      {error && (
        <div className="bg-red-100 dark:bg-red-500/20 border border-red-300 dark:border-red-500/30 rounded-lg p-4 flex items-center">
          <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 mr-3" />
          <span className="text-red-800 dark:text-red-400">{error}</span>
          <button
            onClick={() => setError(null)}
            className="ml-auto text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300"
          >
            ✕
          </button>
        </div>
      )}

      {success && (
        <div className="bg-green-100 dark:bg-green-500/20 border border-green-300 dark:border-green-500/30 rounded-lg p-4 flex items-center">
          <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400 mr-3" />
          <span className="text-green-800 dark:text-green-400">{success}</span>
          <button
            onClick={() => setSuccess(null)}
            className="ml-auto text-green-600 dark:text-green-400 hover:text-green-800 dark:hover:text-green-300"
          >
            ✕
          </button>
        </div>
      )}

      {/* Main Content */}
      <div className="w-full max-w-4xl">
        {/* Editor */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-green-400 mb-2">
              {language === "he" ? "טקסט הנחיות המערכת" : "System Prompt Text"}
              {hasUnsavedChanges && (
                <span className="text-orange-500 ml-2">
                  • {language === "he" ? "שינויים לא נשמרו" : "Unsaved changes"}
                </span>
              )}
            </label>
            <textarea
              value={editedPrompt}
              onChange={(e) => setEditedPrompt(e.target.value)}
              className="w-full h-96 p-4 border border-gray-300 dark:border-green-600 rounded-lg bg-white dark:bg-black text-gray-900 dark:text-green-400 font-mono text-sm resize-none focus:outline-none focus:ring-2 focus:ring-green-500"
              placeholder={
                language === "he"
                  ? "הכנס הנחיות מערכת..."
                  : "Enter system prompt..."
              }
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-green-400 mb-2">
              {language === "he" ? "הערות (אופציונלי)" : "Notes (Optional)"}
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className="w-full h-20 p-3 border border-gray-300 dark:border-green-600 rounded-lg bg-white dark:bg-black text-gray-900 dark:text-green-400 resize-none focus:outline-none focus:ring-2 focus:ring-green-500"
              placeholder={
                language === "he"
                  ? "הוסף הערות על גרסה זו..."
                  : "Add notes about this version..."
              }
            />
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3">
            <button
              onClick={handleSave}
              disabled={saving || !editedPrompt.trim() || !hasUnsavedChanges}
              className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white rounded-lg transition-colors flex items-center justify-center gap-2"
            >
              {saving ? (
                <Clock className="w-4 h-4 animate-spin" />
              ) : (
                <Save className="w-4 h-4" />
              )}
              {saving
                ? language === "he"
                  ? "שומר..."
                  : "Saving..."
                : language === "he"
                ? "שמור שינויים"
                : "Save Changes"}
            </button>
            <button
              onClick={handleResetToDefault}
              disabled={resetting}
              className="flex-1 px-4 py-2 bg-green-500 hover:bg-green-600 disabled:bg-gray-400 text-white rounded-lg transition-colors flex items-center justify-center gap-2"
            >
              {resetting ? (
                <Clock className="w-4 h-4 animate-spin" />
              ) : (
                <RotateCcw className="w-4 h-4" />
              )}
              {resetting
                ? language === "he"
                  ? "מאפס..."
                  : "Resetting..."
                : language === "he"
                ? "אפס לברירת מחדל"
                : "Reset to Default"}
            </button>
          </div>
        </div>
      </div>

      {/* History */}
      {showHistory && (
        <div className="space-y-4">
          <h4 className="text-lg font-semibold text-gray-800 dark:text-green-400">
            {language === "he" ? "היסטוריית גרסאות" : "Version History"}
          </h4>
          <div className="space-y-3">
            {promptHistory.map((prompt) => (
              <div
                key={prompt.id}
                className={`p-4 rounded-lg border ${
                  prompt.is_active
                    ? "border-green-500 bg-green-50 dark:bg-green-500/10"
                    : "border-gray-300 dark:border-green-600 bg-white dark:bg-gray-900"
                }`}
              >
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-gray-800 dark:text-green-400">
                        {language === "he" ? "גרסה" : "Version"}{" "}
                        {prompt.version}
                      </span>
                      {prompt.is_active && (
                        <span className="px-2 py-1 bg-green-500 text-white text-xs rounded">
                          {language === "he" ? "פעיל" : "Active"}
                        </span>
                      )}
                    </div>
                    <div className="text-sm text-gray-600 dark:text-green-400/70 flex items-center gap-2">
                      <Clock className="w-3 h-3" />
                      {formatDate(prompt.updated_at)}
                      {prompt.updated_by_email && (
                        <>
                          <User className="w-3 h-3 ml-2" />
                          {prompt.updated_by_email}
                        </>
                      )}
                    </div>
                  </div>
                  {!prompt.is_active && (
                    <button
                      onClick={() => handleActivateVersion(prompt.id)}
                      className="px-3 py-1 bg-green-600 hover:bg-green-700 text-white text-sm rounded transition-colors"
                    >
                      {language === "he" ? "הפעל" : "Activate"}
                    </button>
                  )}
                </div>
                {prompt.notes && (
                  <div className="text-sm text-gray-600 dark:text-green-400/70 mb-2">
                    <strong>{language === "he" ? "הערות:" : "Notes:"}</strong>{" "}
                    {prompt.notes}
                  </div>
                )}
                <div className="text-xs text-gray-500 dark:text-green-400/50 font-mono max-h-20 overflow-y-auto">
                  {prompt.prompt_text.substring(0, 200)}
                  {prompt.prompt_text.length > 200 && "..."}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Reset Confirmation Modal */}
      {showResetConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
            <div className="flex items-center gap-3 mb-4">
              <div className="flex-shrink-0">
                <AlertCircle className="w-6 h-6 text-orange-500" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-green-400">
                {language === "he" ? "אישור איפוס" : "Confirm Reset"}
              </h3>
            </div>

            <p className="text-gray-700 dark:text-green-400/70 mb-6">
              {language === "he"
                ? "האם אתה בטוח שברצונך לאפס להנחיות המערכת הדיפולטיביות? זה יצור גרסה חדשה."
                : "Are you sure you want to reset to the default system prompt? This will create a new version."}
            </p>

            <div className="flex justify-end gap-3">
              <button
                onClick={() => setShowResetConfirm(false)}
                className="px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white rounded-lg transition-colors"
              >
                {language === "he" ? "ביטול" : "Cancel"}
              </button>
              <button
                onClick={handleConfirmReset}
                disabled={resetting}
                className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white rounded-lg transition-colors flex items-center gap-2"
              >
                {resetting && <Clock className="w-4 h-4 animate-spin" />}
                {language === "he" ? "אפס" : "Reset"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
