import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ChevronLeft, Shield, Globe } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { changeLanguage } from '../../i18n/config';
import { useTheme } from '../../contexts/ThemeContext';

const TermsAndConditions: React.FC = () => {
  const [termsContent, setTermsContent] = useState<string>('');
  const { i18n } = useTranslation();
  const { theme } = useTheme();
  
  useEffect(() => {
    // Load terms file based on language
    const termsFile = i18n.language === 'he' 
      ? '/terms-and-conditions.md' 
      : '/terms-and-conditions-en.md';

    fetch(termsFile)
      .then(response => response.text())
      .then(text => {
        setTermsContent(text);
      })
      .catch(error => {
        console.error('Error loading terms and conditions:', error);
        setTermsContent(i18n.language === 'he' 
          ? 'שגיאה בטעינת תנאי השימוש. אנא נסה שוב מאוחר יותר.' 
          : 'Error loading terms and conditions. Please try again later.');
      });
  }, [i18n.language]);

  const toggleLanguage = () => {
    const newLang = i18n.language === 'he' ? 'en' : 'he';
    changeLanguage(newLang);
  };

  return (
    <div className={`min-h-screen overflow-y-auto ${
      theme === 'dark' 
        ? 'bg-black text-white' 
        : 'bg-gray-50 text-gray-900'
    }`}>
      {/* Header */}
      <header className={`backdrop-blur-md border-b px-6 py-4 sticky top-0 z-10 ${
        theme === 'dark' 
          ? 'bg-black/50 border-green-500/20' 
          : 'bg-white/80 border-gray-200'
      }`}>
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <div className="flex items-center">
            <Shield className={`w-5 h-5 mr-2 ${
              theme === 'dark' ? 'text-green-400' : 'text-green-600'
            }`} />
            <h1 className={`text-xl font-bold ${
              theme === 'dark' ? 'text-green-400' : 'text-green-600'
            }`}>
              {i18n.language === 'he' ? 'תנאי שימוש ומדיניות פרטיות' : 'Terms of Use and Privacy Policy'}
            </h1>
          </div>
          <Link to="/" className={`flex items-center transition-colors ${
            theme === 'dark' 
              ? 'text-green-400 hover:text-green-300' 
              : 'text-green-600 hover:text-green-700'
          }`}>
            <ChevronLeft className="w-4 h-4 mr-1" />
            <span>{i18n.language === 'he' ? 'חזרה' : 'Back'}</span>
          </Link>
        </div>
      </header>
      
      {/* Content */}
      <main className="max-w-5xl mx-auto py-8 px-6">
        <div className={`border rounded-lg p-6 shadow-lg prose max-w-none ${
          theme === 'dark' 
            ? 'bg-black/20 border-green-500/20 prose-invert prose-green' 
            : 'bg-white border-gray-200 prose-gray'
        }`}>
          {termsContent ? (
            <div 
              className="markdown-content" 
              dangerouslySetInnerHTML={{ __html: formatMarkdown(termsContent, theme) }} 
            />
          ) : (
            <div className="flex justify-center items-center py-10">
              <div className="flex space-x-2">
                {[...Array(3)].map((_, i) => (
                  <div
                    key={i}
                    className={`w-2 h-2 rounded-full animate-bounce ${
                      theme === 'dark' ? 'bg-green-400' : 'bg-green-600'
                    }`}
                    style={{ animationDelay: `${i * 0.2}s` }}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      </main>
      
      {/* Footer */}
      <footer className={`border-t py-4 px-6 mt-10 ${
        theme === 'dark' 
          ? 'bg-black/30 border-green-500/10' 
          : 'bg-gray-100 border-gray-200'
      }`}>
        <div className={`max-w-5xl mx-auto flex justify-between items-center text-sm ${
          theme === 'dark' ? 'text-green-400/50' : 'text-gray-600'
        }`}>
          <p>© 2024 APEX Systems. {i18n.language === 'he' ? 'כל הזכויות שמורות.' : 'All rights reserved.'}</p>
          <button 
            onClick={toggleLanguage} 
            className={`flex items-center transition-colors ${
              theme === 'dark' 
                ? 'text-green-400/70 hover:text-green-400' 
                : 'text-gray-600 hover:text-gray-700'
            }`}
          >
            <Globe className="w-4 h-4 mr-1" />
            <span>{i18n.language === 'he' ? 'English' : 'עברית'}</span>
          </button>
        </div>
      </footer>
    </div>
  );
};

// Helper function for formatting markdown with theme support
const formatMarkdown = (markdown: string, theme: 'dark' | 'light'): string => {
  const headerClass = theme === 'dark' ? 'text-green-400' : 'text-green-600';
  const textClass = theme === 'dark' ? 'text-green-100/80' : 'text-gray-700';
  const listClass = theme === 'dark' ? 'text-green-100/80' : 'text-gray-700';
  
  // Basic markdown to HTML conversion
  let html = markdown
    // Headers
    .replace(/^# (.*$)/gm, `<h1 class="text-2xl font-bold ${headerClass} my-4">$1</h1>`)
    .replace(/^## (.*$)/gm, `<h2 class="text-xl font-bold ${headerClass} my-3">$1</h2>`)
    .replace(/^### (.*$)/gm, `<h3 class="text-lg font-bold ${headerClass} my-2">$1</h3>`)
    // Bold
    .replace(/\*\*(.*?)\*\*/g, `<strong class="${theme === 'dark' ? 'text-green-300' : 'text-gray-800'}">$1</strong>`)
    // Italic
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    // Lists
    .replace(/^- (.*$)/gm, `<ul class="list-disc list-inside mb-4 ${listClass}"><li>$1</li></ul>`)
    // Paragraphs
    .replace(/^\s*(\n)?(.+)/gm, (m) => {
      return /\<(\/)?(h|ul|ol|li|blockquote|code|strong|em)/.test(m) ? m : `<p class="mb-4 ${textClass}">${m}</p>`;
    })
    // Fix for multiple <ul> tags
    .replace(/<\/ul>\s*<ul class="list-disc list-inside mb-4[^"]*">/g, '');
  
  return html;
};

export default TermsAndConditions; 