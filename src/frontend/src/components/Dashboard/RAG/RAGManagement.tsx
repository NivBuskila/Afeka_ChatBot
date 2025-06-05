import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Brain, Cpu, TrendingUp, Search, Check, AlertCircle, Clock, Settings } from 'lucide-react';
import { ragService, RAGProfile, RAGTestResult } from './RAGService';

type Language = 'he' | 'en';

interface RAGManagementProps {
  activeSubItem: string | null;
  language: Language;
  onRefresh: () => void;
}

export const RAGManagement: React.FC<RAGManagementProps> = ({ 
  activeSubItem, 
  language, 
  onRefresh 
}) => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(false);
  const [currentProfile, setCurrentProfile] = useState<string>('');
  const [profiles, setProfiles] = useState<RAGProfile[]>([]);
  const [testQuery, setTestQuery] = useState('');
  const [testResult, setTestResult] = useState<RAGTestResult | null>(null);
  const [isRunningTest, setIsRunningTest] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchProfiles = async () => {
    try {
      setLoading(true);
      const profilesData = await ragService.getAllProfiles(language);
      setProfiles(profilesData);
    } catch (error) {
      console.error('Error fetching profiles:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProfiles();
  }, [language]);

  const handleProfileChange = async (profileId: string) => {
    setLoading(true);
    setError(null);
    try {
      const result = await ragService.activateProfile(profileId);
      console.log('Successfully switched to profile:', result);
      
      // Reload profiles to get updated status
      await fetchProfiles();
      
    } catch (error) {
      console.error('Error switching profile:', error);
      setError(`Failed to switch to profile: ${profileId}`);
    } finally {
      setLoading(false);
    }
  };

  const handleRunTest = async () => {
    if (!testQuery.trim()) return;
    
    setIsRunningTest(true);
    setError(null);
    try {
      console.log('Running test with query:', testQuery);
      
      const result = await ragService.testQuery(testQuery);
      setTestResult(result);
      
    } catch (error) {
      console.error('Error running test:', error);
      setError('Failed to run test query');
    } finally {
      setIsRunningTest(false);
    }
  };

  const renderOverview = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div className="bg-black/30 backdrop-blur-lg rounded-lg border border-green-500/20 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-green-400">{t('rag.current.profile') || 'פרופיל נוכחי'}</h3>
          <Brain className="w-6 h-6 text-green-500" />
        </div>
        <div className="space-y-3">
          <div>
            <p className="text-green-300 font-semibold text-xl">
              {profiles.find(p => p.isActive)?.name || 'לא נמצא'}
            </p>
            <p className="text-green-400/70 text-sm">
              {profiles.find(p => p.isActive)?.description || ''}
            </p>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-green-400/60 text-sm">{t('rag.similarity.threshold') || 'סף דמיון'}:</span>
              <span className="text-green-300 text-sm">
                {profiles.find(p => p.isActive)?.config.similarityThreshold || 'N/A'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-green-400/60 text-sm">{t('rag.max.chunks') || 'צ\'אנקים מקס'}:</span>
              <span className="text-green-300 text-sm">
                {profiles.find(p => p.isActive)?.config.maxChunks || 'N/A'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-green-400/60 text-sm">{t('rag.temperature') || 'טמפרטורה'}:</span>
              <span className="text-green-300 text-sm">
                {profiles.find(p => p.isActive)?.config.temperature || 'N/A'}
              </span>
            </div>
          </div>
        </div>
      </div>
      
      <div className="bg-black/30 backdrop-blur-lg rounded-lg border border-blue-500/20 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-blue-400">{t('rag.profileCharacteristics') || 'מאפיינים'}</h3>
          <TrendingUp className="w-6 h-6 text-blue-500" />
        </div>
        <div className="space-y-3">
          <div>
            <p className="text-blue-400/70 text-sm">{t('rag.focus')}:</p>
            <p className="text-blue-300 text-sm">
              {profiles.find(p => p.isActive)?.characteristics.focus || t('rag.notAvailable')}
            </p>
          </div>
          <div>
            <p className="text-blue-400/70 text-sm">{t('rag.expectedSpeed')}:</p>
            <p className="text-blue-300 text-sm">
              {profiles.find(p => p.isActive)?.characteristics.expectedSpeed || t('rag.notAvailable')}
            </p>
          </div>
          <div>
            <p className="text-blue-400/70 text-sm">{t('rag.expectedQuality')}:</p>
            <p className="text-blue-300 text-sm">
              {profiles.find(p => p.isActive)?.characteristics.expectedQuality || t('rag.notAvailable')}
            </p>
          </div>
        </div>
      </div>
      
      <div className="bg-black/30 backdrop-blur-lg rounded-lg border border-purple-500/20 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-purple-400">{t('rag.configuration') || 'קונפיגורציה מתקדמת'}</h3>
          <Cpu className="w-6 h-6 text-purple-500" />
        </div>
        <div className="space-y-2">
          {profiles.find(p => p.isActive)?.config.chunkSize && (
            <div className="flex justify-between">
              <span className="text-purple-400/60 text-sm">{t('rag.chunkSize') || 'גודל צ\'אנק'}:</span>
              <span className="text-purple-300 text-sm">
                {profiles.find(p => p.isActive)?.config.chunkSize}
              </span>
            </div>
          )}
          {profiles.find(p => p.isActive)?.config.chunkOverlap && (
            <div className="flex justify-between">
              <span className="text-purple-400/60 text-sm">{t('rag.chunkOverlap') || 'חפיפת צ\'אנקים'}:</span>
              <span className="text-purple-300 text-sm">
                {profiles.find(p => p.isActive)?.config.chunkOverlap}
              </span>
            </div>
          )}
          {profiles.find(p => p.isActive)?.config.maxContextTokens && (
            <div className="flex justify-between">
              <span className="text-purple-400/60 text-sm">{t('rag.maxContext') || 'קונטקסט מקס'}:</span>
              <span className="text-purple-300 text-sm">
                {profiles.find(p => p.isActive)?.config.maxContextTokens}
              </span>
            </div>
          )}
          {profiles.find(p => p.isActive)?.config.hybridSemanticWeight && (
            <div className="flex justify-between">
              <span className="text-purple-400/60 text-sm">{t('rag.semanticWeight') || 'משקל סמנטי'}:</span>
              <span className="text-purple-300 text-sm">
                {profiles.find(p => p.isActive)?.config.hybridSemanticWeight}
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  const renderProfiles = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {profiles.map((profile) => (
          <div
            key={profile.id}
            className={`bg-black/30 backdrop-blur-lg rounded-lg border p-6 transition-all ${
              profile.isActive 
                ? 'border-green-500/50 bg-green-500/5' 
                : 'border-green-500/20 hover:border-green-500/30'
            }`}
          >
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-green-400">{profile.name}</h3>
                <p className="text-sm text-green-400/70 mt-1">{profile.description}</p>
              </div>
              {profile.isActive && (
                <div className="flex items-center space-x-2 bg-green-500/20 px-3 py-1 rounded-full">
                  <Check className="w-4 h-4 text-green-500" />
                  <span className="text-sm text-green-400">{t('rag.profile.active')}</span>
                </div>
              )}
            </div>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <p className="text-xs text-green-400/50 uppercase tracking-wide">{t('rag.settings') || 'הגדרות'}</p>
                <div className="space-y-1 mt-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-green-400/70">{t('rag.similarity.threshold') || 'סף דמיון'}:</span>
                    <span className="text-green-300">{profile.config.similarityThreshold}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-green-400/70">{t('rag.chunks') || 'צ\'אנקים'}:</span>
                    <span className="text-green-300">{profile.config.maxChunks}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-green-400/70">{t('rag.temperature') || 'טמפרטורה'}:</span>
                    <span className="text-green-300">{profile.config.temperature}</span>
                  </div>
                </div>
              </div>
              <div>
                <p className="text-xs text-green-400/50 uppercase tracking-wide">{t('rag.characteristics') || 'מאפיינים'}</p>
                <div className="space-y-1 mt-2">
                  <div className="text-sm">
                    <span className="text-green-400/70">{t('rag.focus')}:</span>
                    <p className="text-green-300 text-xs mt-1">{profile.characteristics.focus}</p>
                  </div>
                  <div className="text-sm">
                    <span className="text-green-400/70">{t('rag.bestFor')}:</span>
                    <p className="text-green-300 text-xs mt-1">{profile.characteristics.bestFor}</p>
                  </div>
                </div>
              </div>
            </div>

            {!profile.isActive && (
              <button
                onClick={() => handleProfileChange(profile.id)}
                disabled={loading}
                className="w-full bg-green-500/20 hover:bg-green-500/30 text-green-400 font-medium py-2 px-4 rounded-lg border border-green-500/30 transition-colors disabled:opacity-50"
              >
{loading ? (t('rag.switching') || 'מחליף...') : t('rag.apply.profile')}
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );

  const renderPerformance = () => (
    <div className="space-y-6">
      <div className="bg-black/30 backdrop-blur-lg rounded-lg border border-green-500/20 p-6">
        <h3 className="text-lg font-semibold text-green-400 mb-4">{t('rag.currentProfileConfig') || 'קונפיגורציה פרופיל נוכחי'}</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-green-400 mb-2">
              {profiles.find(p => p.isActive)?.config.similarityThreshold || 'N/A'}
            </div>
            <p className="text-sm text-green-400/70">{t('rag.similarity.threshold') || 'סף דמיון'}</p>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-400 mb-2">
              {profiles.find(p => p.isActive)?.config.maxChunks || 'N/A'}
            </div>
            <p className="text-sm text-green-400/70">{t('rag.max.chunks') || 'צ\'אנקים מקסימליים'}</p>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-400 mb-2">
              {profiles.find(p => p.isActive)?.config.temperature || 'N/A'}
            </div>
            <p className="text-sm text-green-400/70">{t('rag.temperature') || 'טמפרטורה'}</p>
          </div>
        </div>
        
        <div className="mt-6 bg-black/40 rounded-lg p-4">
          <h4 className="text-md font-semibold text-green-400 mb-3">{t('rag.expectedBehavior') || 'התנהגות צפויה'}</h4>
          <div className="space-y-2">
            <p className="text-green-300 text-sm">
              <span className="text-green-400/70">{t('rag.focus')}:</span> {profiles.find(p => p.isActive)?.characteristics.focus}
            </p>
            <p className="text-green-300 text-sm">
              <span className="text-green-400/70">{t('rag.expectedSpeed')}:</span> {profiles.find(p => p.isActive)?.characteristics.expectedSpeed}
            </p>
            <p className="text-green-300 text-sm">
              <span className="text-green-400/70">{t('rag.expectedQuality')}:</span> {profiles.find(p => p.isActive)?.characteristics.expectedQuality}
            </p>
            <p className="text-green-300 text-sm">
              <span className="text-green-400/70">{t('rag.bestFor')}:</span> {profiles.find(p => p.isActive)?.characteristics.bestFor}
            </p>
            <p className="text-yellow-300 text-sm">
              <span className="text-yellow-400/70">{t('rag.tradeoffs')}:</span> {profiles.find(p => p.isActive)?.characteristics.tradeoffs}
            </p>
          </div>
        </div>
      </div>
      
      <div className="bg-black/30 backdrop-blur-lg rounded-lg border border-green-500/20 p-6">
        <h3 className="text-lg font-semibold text-green-400 mb-4">{t('rag.profilesComparison') || 'השוואת פרופילים'}</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-green-500/20">
                <th className={`py-3 text-green-400 ${language === 'he' ? 'text-right' : 'text-left'}`}>{t('rag.profileName') || 'שם פרופיל'}</th>
                <th className={`py-3 text-green-400 ${language === 'he' ? 'text-right' : 'text-left'}`}>{t('rag.similarity.threshold') || 'סף דמיון'}</th>
                <th className={`py-3 text-green-400 ${language === 'he' ? 'text-right' : 'text-left'}`}>{t('rag.max.chunks') || 'צ\'אנקים מקס'}</th>
                <th className={`py-3 text-green-400 ${language === 'he' ? 'text-right' : 'text-left'}`}>{t('rag.focus') || 'מיקוד'}</th>
                <th className={`py-3 text-green-400 ${language === 'he' ? 'text-right' : 'text-left'}`}>{t('rag.status') || 'סטטוס'}</th>
              </tr>
            </thead>
            <tbody>
              {profiles.map((profile) => (
                <tr key={profile.id} className="border-b border-green-500/10">
                  <td className={`py-3 text-green-300 ${language === 'he' ? 'text-right' : 'text-left'}`}>{profile.name}</td>
                  <td className={`py-3 text-green-400/70 ${language === 'he' ? 'text-right' : 'text-left'}`}>{profile.config.similarityThreshold}</td>
                  <td className={`py-3 text-green-400/70 ${language === 'he' ? 'text-right' : 'text-left'}`}>{profile.config.maxChunks}</td>
                  <td className={`py-3 text-green-400/70 ${language === 'he' ? 'text-right' : 'text-left'} max-w-xs truncate`}>
                    {profile.characteristics.focus}
                  </td>
                  <td className={`py-3 ${language === 'he' ? 'text-right' : 'text-left'}`}>
                    {profile.isActive ? (
                      <span className="text-green-500">{t('rag.profile.active') || 'פעיל'}</span>
                    ) : (
                      <span className="text-green-400/50">{t('rag.profile.inactive') || 'לא פעיל'}</span>
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

  const renderTestCenter = () => (
    <div className="space-y-6">
      <div className="bg-black/30 backdrop-blur-lg rounded-lg border border-green-500/20 p-6">
        <h3 className="text-lg font-semibold text-green-400 mb-4">{t('rag.test.center')}</h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-green-400 mb-2">
              {t('rag.test.query')}
            </label>
            <input
              type="text"
              value={testQuery}
              onChange={(e) => setTestQuery(e.target.value)}
              placeholder={t('rag.test.placeholder') || 'הכנס שאילתה לבדיקה...'}
              className="w-full px-4 py-2 bg-black/50 border border-green-500/30 rounded-lg text-green-300 placeholder-green-400/50 focus:border-green-500/50 focus:outline-none"
            />
          </div>
          
          <button
            onClick={handleRunTest}
            disabled={!testQuery.trim() || isRunningTest}
            className="bg-green-500/20 hover:bg-green-500/30 text-green-400 font-medium py-2 px-6 rounded-lg border border-green-500/30 transition-colors disabled:opacity-50 flex items-center space-x-2"
          >
            {isRunningTest ? (
              <>
                <Clock className="w-4 h-4 animate-spin" />
                <span>{t('rag.runningTest') || 'מריץ בדיקה...'}</span>
              </>
            ) : (
              <>
                <Search className="w-4 h-4" />
                <span>{t('rag.run.test')}</span>
              </>
            )}
          </button>
        </div>

        {testResult && (
          <div className="mt-6 bg-black/50 rounded-lg p-4 border border-green-500/20">
            <h4 className="text-md font-semibold text-green-400 mb-3">{t('rag.test.results') || 'תוצאות הבדיקה'}</h4>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-green-400/70">{t('rag.query') || 'שאילתה'}:</p>
                <p className="text-green-300">{testResult.query}</p>
              </div>
              <div>
                <p className="text-sm text-green-400/70">{t('rag.answer') || 'תשובה'}:</p>
                <p className="text-green-300">{testResult.answer}</p>
              </div>
              <div className="grid grid-cols-3 gap-4 mt-4">
                <div>
                  <p className="text-xs text-green-400/50">{t('rag.response.timeShort') || 'זמן תגובה'}</p>
                  <p className="text-green-300 font-semibold">{testResult.responseTime}ms</p>
                </div>
                <div>
                  <p className="text-xs text-green-400/50">{t('rag.sourcesFound') || 'מקורות נמצאו'}</p>
                  <p className="text-green-300 font-semibold">{testResult.sourcesFound}</p>
                </div>
                <div>
                  <p className="text-xs text-green-400/50">{t('rag.chunks') || 'צ\'אנקים'}</p>
                  <p className="text-green-300 font-semibold">{testResult.chunks}</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );

  const renderContent = () => {
    switch (activeSubItem) {
      case 'profiles':
        return renderProfiles();
      case 'performance':
        return renderPerformance();
      case 'test':
        return renderTestCenter();
      default:
        return renderOverview();
    }
  };

  if (loading && profiles.length === 0) {
    return (
      <div className="p-6 flex items-center justify-center">
        <div className="text-green-400">
          <Clock className="w-8 h-8 animate-spin mx-auto mb-2" />
          <p>{t('rag.loading') || 'טוען נתוני RAG...'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-green-400">
          {t('rag.management')}
          {activeSubItem && activeSubItem !== 'overview' && (
            <span className="text-green-400/70 mr-2">
              / {activeSubItem === 'profiles' ? t('rag.profile.selector') :
                 activeSubItem === 'performance' ? t('rag.performanceMonitor') :
                 activeSubItem === 'test' ? t('rag.test.center') : ''}
            </span>
          )}
        </h2>
        <button
          onClick={() => {
            onRefresh();
            fetchProfiles();
          }}
          disabled={loading}
          className="bg-green-500/20 hover:bg-green-500/30 text-green-400 font-medium py-2 px-4 rounded-lg border border-green-500/30 transition-colors disabled:opacity-50"
        >
{loading ? (t('rag.loadingShort') || 'טוען...') : (t('rag.refresh') || 'רענן')}
        </button>
      </div>
      
      {error && (
        <div className="mb-6 bg-red-500/20 border border-red-500/30 rounded-lg p-4 flex items-center">
          <AlertCircle className="w-5 h-5 text-red-400 mr-3" />
          <span className="text-red-400">{error}</span>
          <button
            onClick={() => setError(null)}
            className="mr-auto text-red-400 hover:text-red-300"
          >
            ✕
          </button>
        </div>
      )}
      
      {renderContent()}
    </div>
  );
}; 