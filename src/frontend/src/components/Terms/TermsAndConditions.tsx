import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ChevronLeft, Shield, Globe } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { changeLanguage } from '../../i18n/config';

const TermsAndConditions: React.FC = () => {
  const [termsContent, setTermsContent] = useState<string>('');
  const { i18n } = useTranslation();
  
  useEffect(() => {
    // Load terms of use file based on language
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
    <div className="min-h-screen bg-black text-white overflow-y-auto">
      {/* Header */}
      <header className="bg-black/50 backdrop-blur-md border-b border-green-500/20 px-6 py-4 sticky top-0 z-10">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <div className="flex items-center">
            <Shield className="w-5 h-5 text-green-400 mr-2" />
            <h1 className="text-xl font-bold text-green-400">
              {i18n.language === 'he' ? 'תנאי שימוש ומדיניות פרטיות' : 'Terms of Use and Privacy Policy'}
            </h1>
          </div>
          <Link to="/" className="flex items-center text-green-400 hover:text-green-300 transition-colors">
            <ChevronLeft className="w-4 h-4 mr-1" />
            <span>{i18n.language === 'he' ? 'חזרה' : 'Back'}</span>
          </Link>
        </div>
      </header>
      
      {/* Content */}
      <main className="max-w-5xl mx-auto py-8 px-6">
        <div className="bg-black/20 border border-green-500/20 rounded-lg p-6 shadow-lg prose prose-invert prose-green max-w-none">
          {termsContent ? (
            <div className="markdown-content" dangerouslySetInnerHTML={{ __html: formatMarkdown(termsContent) }} />
          ) : (
            <div className="flex justify-center items-center py-10">
              <div className="flex space-x-2">
                {[...Array(3)].map((_, i) => (
                  <div
                    key={i}
                    className="w-2 h-2 bg-green-400 rounded-full animate-bounce"
                    style={{ animationDelay: `${i * 0.2}s` }}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      </main>
      
      {/* Footer */}
      <footer className="bg-black/30 border-t border-green-500/10 py-4 px-6 mt-10">
        <div className="max-w-5xl mx-auto flex justify-between items-center text-green-400/50 text-sm">
          <p>© 2024 APEX Systems. {i18n.language === 'he' ? 'כל הזכויות שמורות.' : 'All rights reserved.'}</p>
          <button 
            onClick={toggleLanguage} 
            className="flex items-center text-green-400/70 hover:text-green-400 transition-colors"
          >
            <Globe className="w-4 h-4 mr-1" />
            <span>{i18n.language === 'he' ? 'English' : 'עברית'}</span>
          </button>
        </div>
      </footer>
    </div>
  );
};

// Helper function for formatting markdown
const formatMarkdown = (markdown: string): string => {
  // Basic conversion of markdown syntax to HTML
  let html = markdown
    // Headers
    .replace(/^# (.*$)/gm, '<h1 class="text-2xl font-bold text-green-400 my-4">$1</h1>')
    .replace(/^## (.*$)/gm, '<h2 class="text-xl font-bold text-green-400 my-3">$1</h2>')
    .replace(/^### (.*$)/gm, '<h3 class="text-lg font-bold text-green-400 my-2">$1</h3>')
    // Bold
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    // Italic
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    // Lists
    .replace(/^- (.*$)/gm, '<ul class="list-disc list-inside mb-4"><li>$1</li></ul>')
    // Paragraphs
    .replace(/^\s*(\n)?(.+)/gm, (m) => {
      return /\<(\/)?(h|ul|ol|li|blockquote|code|strong|em)/.test(m) ? m : `<p class="mb-4 text-green-100/80">${m}</p>`;
    })
    // Fix for multiple <ul> tags
    .replace(/<\/ul>\s*<ul class="list-disc list-inside mb-4">/g, '');
  
  return html;
};

export default TermsAndConditions; 