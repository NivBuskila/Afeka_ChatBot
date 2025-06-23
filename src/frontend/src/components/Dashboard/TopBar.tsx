import React from "react";
import { useTranslation } from "react-i18next";

type Language = "he" | "en";

interface TopBarProps {
  language: Language;
}

export const TopBar: React.FC<TopBarProps> = ({}) => {
  useTranslation();

  return (
    <div className="bg-gray-100/50 dark:bg-black/50 backdrop-blur-sm border-b border-gray-300/20 dark:border-green-500/20 py-3 px-6 transition-colors duration-300">
      <div className="flex justify-between items-center">
        <div></div>
        <div></div>
      </div>
    </div>
  );
};
