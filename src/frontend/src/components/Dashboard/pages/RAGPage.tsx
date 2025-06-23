import React from "react";
import { RAGManagement } from "../RAG/RAGManagement";

type Language = "he" | "en";

interface RAGPageProps {
  activeSubItem: string;
  language: Language;
}

export const RAGPage: React.FC<RAGPageProps> = ({
  activeSubItem,
  language,
}) => {
  return <RAGManagement activeSubItem={activeSubItem} language={language} />;
}; 