import React from 'react';
import { useTranslation } from 'react-i18next';
import ChatInput from '../ChatInput';

interface WelcomeScreenProps {
  input: string;
  setInput: (value: string) => void;
  onSend: () => void;
  isLoading: boolean;
}

const WelcomeScreen: React.FC<WelcomeScreenProps> = ({
  input,
  setInput,
  onSend,
  isLoading,
}) => {
  const { t } = useTranslation();

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <div className="flex-1 flex flex-col items-center justify-center">
        <h1 className="text-5xl font-light mb-8 text-gray-800 dark:text-white">
          {t("chat.noActiveSession", "ברוך הבא לצ'אטבוט אפקה!")}
        </h1>
        <p className="text-gray-500 dark:text-gray-400 mb-12 text-lg text-center mx-auto max-w-2xl leading-relaxed">
          {t(
            "chat.startNewChatPrompt",
            "כאן תוכלו לשאול שאלות לגבי תקנון הלימודים, נהלי הפקולטה, ומידע אחר שקשור ללימודים באפקה. התחילו שיחה חדשה כדי להתחיל!"
          )}
        </p>

        {/* Input in the center for initial screen */}
        <div className="w-full max-w-md">
          <ChatInput
            input={input}
            setInput={setInput}
            onSend={onSend}
            isLoading={isLoading}
          />
        </div>
      </div>
    </div>
  );
};

export default WelcomeScreen; 