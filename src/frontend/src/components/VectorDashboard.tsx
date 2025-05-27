import React, { useState, useEffect } from 'react';
import { 
  Upload, 
  Search, 
  Trash2, 
  FileText, 
  Database, 
  Activity,
  CheckCircle,
  Clock,
  AlertCircle,
  XCircle
} from 'lucide-react';

interface Document {
  id: number;
  name: string;
  type: string;
  size: number;
  processing_status: string;
  chunk_count: number;
  created_at: string;
  updated_at: string;
}

interface VectorStats {
  total_documents: number;
  total_chunks: number;
  status_breakdown: Record<string, number>;
  embedding_model: string;
}

interface SearchResult {
  id: number;
  name: string;
  content: string;
  similarity: number;
  chunk_index: number;
  document_id: number;
}

const VectorDashboard: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [stats, setStats] = useState<VectorStats | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [searchType, setSearchType] = useState<'semantic' | 'hybrid'>('semantic');

  useEffect(() => {
    loadDocuments();
    loadStats();
  }, []);

  const loadDocuments = async () => {
    try {
      const response = await fetch('/api/vector/documents', {
        headers: {
          'Authorization': 'Bearer dev-token' // For development
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setDocuments(data.documents);
      }
    } catch (error) {
      console.error('Error loading documents:', error);
    }
  };

  const loadStats = async () => {
    try {
      const response = await fetch('/api/vector/stats', {
        headers: {
          'Authorization': 'Bearer dev-token'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Error loading stats:', error);
    }
  };

  const handleFileUpload = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch('/api/vector/upload-document', {
        method: 'POST',
        headers: {
          'Authorization': 'Bearer dev-token'
        },
        body: formData
      });

      if (response.ok) {
        const result = await response.json();
        alert(`מסמך הועלה בהצלחה! ID: ${result.document_id}`);
        setSelectedFile(null);
        loadDocuments();
        loadStats();
      } else {
        const error = await response.json();
        alert(`שגיאה בהעלאת המסמך: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      alert('שגיאה בהעלאת הקובץ');
    } finally {
      setIsUploading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    try {
      const endpoint = searchType === 'semantic' ? '/api/vector/search' : '/api/vector/search/hybrid';
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer dev-token'
        },
        body: JSON.stringify({
          query: searchQuery,
          limit: 10,
          threshold: 0.78
        })
      });

      if (response.ok) {
        const data = await response.json();
        setSearchResults(data.results);
      }
    } catch (error) {
      console.error('Error searching:', error);
    } finally {
      setIsSearching(false);
    }
  };

  const handleDeleteDocument = async (documentId: number) => {
    if (!confirm('האם אתה בטוח שברצונך למחוק את המסמך וכל ה-embeddings שלו?')) {
      return;
    }

    try {
      const response = await fetch(`/api/vector/document/${documentId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': 'Bearer dev-token'
        }
      });

      if (response.ok) {
        alert('המסמך נמחק בהצלחה');
        loadDocuments();
        loadStats();
      } else {
        const error = await response.json();
        alert(`שגיאה במחיקת המסמך: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error deleting document:', error);
      alert('שגיאה במחיקת המסמך');
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'processing':
        return <Clock className="w-5 h-5 text-yellow-500" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <AlertCircle className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return 'הושלם';
      case 'processing':
        return 'מעובד';
      case 'failed':
        return 'נכשל';
      case 'pending':
        return 'ממתין';
      default:
        return status;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6" dir="rtl">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          <Database className="inline-block w-8 h-8 ml-2" />
          ניהול מסד נתונים וקטורי
        </h1>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <FileText className="w-8 h-8 text-blue-500" />
                <div className="mr-4">
                  <p className="text-sm font-medium text-gray-600">סה"כ מסמכים</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.total_documents}</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <Database className="w-8 h-8 text-green-500" />
                <div className="mr-4">
                  <p className="text-sm font-medium text-gray-600">סה"כ chunks</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.total_chunks}</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <Activity className="w-8 h-8 text-purple-500" />
                <div className="mr-4">
                  <p className="text-sm font-medium text-gray-600">מודל Embedding</p>
                  <p className="text-xs font-bold text-gray-900">Gemini Embedding</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <CheckCircle className="w-8 h-8 text-green-500" />
                <div className="mr-4">
                  <p className="text-sm font-medium text-gray-600">הושלמו</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {stats.status_breakdown.completed || 0}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Upload Section */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">
              <Upload className="inline-block w-5 h-5 ml-2" />
              העלאת מסמך חדש
            </h2>
            
            <div className="space-y-4">
              <div>
                <input
                  type="file"
                  accept=".pdf,.txt,.docx,.doc"
                  onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                  className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                />
              </div>
              
              <button
                onClick={handleFileUpload}
                disabled={!selectedFile || isUploading}
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isUploading ? 'מעלה...' : 'העלה מסמך'}
              </button>
              
              <p className="text-sm text-gray-600">
                פורמטים נתמכים: PDF, TXT, DOCX, DOC
              </p>
            </div>
          </div>

          {/* Search Section */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">
              <Search className="inline-block w-5 h-5 ml-2" />
              חיפוש במסמכים
            </h2>
            
            <div className="space-y-4">
              <div className="flex gap-2">
                <button
                  onClick={() => setSearchType('semantic')}
                  className={`px-3 py-1 rounded text-sm ${
                    searchType === 'semantic' 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-gray-200 text-gray-700'
                  }`}
                >
                  חיפוש סמנטי
                </button>
                <button
                  onClick={() => setSearchType('hybrid')}
                  className={`px-3 py-1 rounded text-sm ${
                    searchType === 'hybrid' 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-gray-200 text-gray-700'
                  }`}
                >
                  חיפוש היברידי
                </button>
              </div>
              
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="הכנס שאלה או מילות מפתח..."
                className="w-full p-2 border border-gray-300 rounded-md"
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
              
              <button
                onClick={handleSearch}
                disabled={!searchQuery.trim() || isSearching}
                className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 disabled:opacity-50"
              >
                {isSearching ? 'מחפש...' : 'חפש'}
              </button>
            </div>

            {/* Search Results */}
            {searchResults.length > 0 && (
              <div className="mt-6">
                <h3 className="font-semibold mb-3">תוצאות חיפוש ({searchResults.length})</h3>
                <div className="space-y-3 max-h-64 overflow-y-auto">
                  {searchResults.map((result, index) => (
                    <div key={index} className="p-3 bg-gray-50 rounded border">
                      <div className="flex justify-between items-start mb-2">
                        <span className="font-medium text-sm">{result.name}</span>
                        <span className="text-xs text-gray-500">
                          דמיון: {(result.similarity * 100).toFixed(1)}%
                        </span>
                      </div>
                      <p className="text-sm text-gray-700 line-clamp-3">
                        {result.content.substring(0, 200)}...
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Documents Table */}
        <div className="mt-8 bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold">רשימת מסמכים</h2>
          </div>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    שם המסמך
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    סטטוס
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Chunks
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    גודל
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    תאריך יצירה
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    פעולות
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {documents.map((doc) => (
                  <tr key={doc.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {doc.name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <div className="flex items-center">
                        {getStatusIcon(doc.processing_status)}
                        <span className="mr-2">{getStatusText(doc.processing_status)}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {doc.chunk_count}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {(doc.size / 1024).toFixed(1)} KB
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(doc.created_at).toLocaleDateString('he-IL')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button
                        onClick={() => handleDeleteDocument(doc.id)}
                        className="text-red-600 hover:text-red-900"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VectorDashboard;