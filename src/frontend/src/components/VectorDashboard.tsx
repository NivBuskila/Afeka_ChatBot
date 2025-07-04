import React, { useState, useEffect } from "react";
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
  XCircle,
  RefreshCw,
  AlertTriangle,
} from "lucide-react";
import { Pagination, usePagination } from "./common/Pagination";
import { ItemsPerPageSelector } from "./common/ItemsPerPageSelector";
import { useTheme } from '../contexts/ThemeContext';

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
  const { theme } = useTheme();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [stats, setStats] = useState<VectorStats | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [searchType, setSearchType] = useState<"semantic" | "hybrid">(
    "semantic"
  );

  // Pagination state
  const [itemsPerPage, setItemsPerPage] = useState(10);
  const [currentPage, setCurrentPage] = useState(1);

  // Message system
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Pagination logic
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const paginatedDocuments = documents.slice(startIndex, endIndex);

  // Reset to first page if current page is out of bounds
  const totalPages = Math.ceil(documents.length / itemsPerPage);
  React.useEffect(() => {
    if (currentPage > totalPages && totalPages > 0) {
      setCurrentPage(1);
    }
  }, [documents.length, itemsPerPage, currentPage, totalPages]);

  useEffect(() => {
    loadDocuments();
    loadStats();
  }, []);

  const loadDocuments = async () => {
    try {
      const response = await fetch("/api/vector/documents", {
        headers: {
          Authorization: "Bearer dev-token", // For development
        },
      });

      if (response.ok) {
        const data = await response.json();
        setDocuments(data.documents);
      }
    } catch (error) {
      // Silent fail
    }
  };

  const loadStats = async () => {
    try {
      const response = await fetch("/api/vector/stats", {
        headers: {
          Authorization: "Bearer dev-token",
        },
      });

      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      // Silent fail
    }
  };

  const handleFileUpload = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await fetch("/api/vector/upload-document", {
        method: "POST",
        headers: {
          Authorization: "Bearer dev-token",
        },
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        showSuccessMessage(`מסמך הועלה בהצלחה! ID: ${result.document_id}`);
        setSelectedFile(null);
        loadDocuments();
        loadStats();
      } else {
        const error = await response.json();
        showErrorMessage(`שגיאה בהעלאת המסמך: ${error.detail}`);
      }
    } catch (error) {
      showErrorMessage("שגיאה בהעלאת הקובץ");
    } finally {
      setIsUploading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    try {
      const endpoint =
        searchType === "semantic"
          ? "/api/vector/search"
          : "/api/vector/search/hybrid";
      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer dev-token",
        },
        body: JSON.stringify({
          query: searchQuery,
          limit: 10,
          threshold: 0.78,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setSearchResults(data.results);
      }
    } catch (error) {
      // Silent fail
    } finally {
      setIsSearching(false);
    }
  };

  const handleDeleteDocument = async (documentId: number) => {
    if (!confirm("האם אתה בטוח שברצונך למחוק את המסמך וכל ה-embeddings שלו?")) {
      return;
    }

    try {
      const response = await fetch(`/api/vector/document/${documentId}`, {
        method: "DELETE",
        headers: {
          Authorization: "Bearer dev-token",
        },
      });

      if (response.ok) {
        showSuccessMessage("המסמך נמחק בהצלחה");
        loadDocuments();
        loadStats();
      } else {
        const error = await response.json();
        showErrorMessage(`שגיאה במחיקת המסמך: ${error.detail}`);
      }
    } catch (error) {
      showErrorMessage("שגיאה במחיקת המסמך");
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case "processing":
        return <Clock className="w-5 h-5 text-yellow-500" />;
      case "failed":
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <AlertCircle className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case "completed":
        return "הושלם";
      case "processing":
        return "מעובד";
      case "failed":
        return "נכשל";
      case "pending":
        return "ממתין";
      default:
        return status;
    }
  };

  // Show message functions
  const showSuccessMessage = (message: string) => {
    setSuccessMessage(message);
    setErrorMessage("");
    setTimeout(() => setSuccessMessage(""), 3000);
  };

  const showErrorMessage = (message: string) => {
    setErrorMessage(message);
    setSuccessMessage("");
    setTimeout(() => setErrorMessage(""), 5000);
  };

  return (
    <div className={`min-h-screen p-6 ${
      theme === 'dark' ? 'bg-black' : 'bg-gray-50'
    }`} dir="rtl">
      {/* Success message */}
      {successMessage && (
        <div className={`fixed top-4 right-4 z-50 border-l-4 border-green-500 p-4 rounded shadow-md max-w-md animate-fadeIn ${
          theme === 'dark' 
            ? 'bg-green-900/20' 
            : 'bg-green-50'
        }`}>
          <div className="flex items-center">
            <CheckCircle className={`w-5 h-5 mr-2 ${
              theme === 'dark' ? 'text-green-400' : 'text-green-600'
            }`} />
            <p className={theme === 'dark' ? 'text-green-400' : 'text-green-700'}>{successMessage}</p>
          </div>
        </div>
      )}

      {/* Error message */}
      {errorMessage && (
        <div className={`fixed top-4 right-4 z-50 border-l-4 border-red-500 p-4 rounded shadow-md max-w-md animate-fadeIn ${
          theme === 'dark' 
            ? 'bg-red-900/20' 
            : 'bg-red-50'
        }`}>
          <div className="flex items-center">
            <AlertCircle className={`w-5 h-5 mr-2 ${
              theme === 'dark' ? 'text-red-400' : 'text-red-600'
            }`} />
            <p className={theme === 'dark' ? 'text-red-400' : 'text-red-700'}>{errorMessage}</p>
          </div>
        </div>
      )}

      <div className="max-w-7xl mx-auto">
        <h1 className={`text-3xl font-bold mb-8 ${
          theme === 'dark' ? 'text-white' : 'text-gray-900'
        }`}>
          <Database className="inline-block w-8 h-8 ml-2" />
          ניהול מסד נתונים וקטורי
        </h1>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className={`rounded-lg shadow p-6 ${
              theme === 'dark' ? 'bg-gray-800' : 'bg-white'
            }`}>
              <div className="flex items-center">
                <FileText className="w-8 h-8 text-blue-500" />
                <div className="mr-4">
                  <p className={`text-sm font-medium ${
                    theme === 'dark' ? 'text-gray-300' : 'text-gray-600'
                  }`}>
                    סה"כ מסמכים
                  </p>
                  <p className={`text-2xl font-bold ${
                    theme === 'dark' ? 'text-white' : 'text-gray-900'
                  }`}>
                    {stats.total_documents}
                  </p>
                </div>
              </div>
            </div>

            <div className={`rounded-lg shadow p-6 ${
              theme === 'dark' ? 'bg-gray-800' : 'bg-white'
            }`}>
              <div className="flex items-center">
                <Database className="w-8 h-8 text-green-500" />
                <div className="mr-4">
                  <p className={`text-sm font-medium ${
                    theme === 'dark' ? 'text-gray-300' : 'text-gray-600'
                  }`}>
                    סה"כ chunks
                  </p>
                  <p className={`text-2xl font-bold ${
                    theme === 'dark' ? 'text-white' : 'text-gray-900'
                  }`}>
                    {stats.total_chunks}
                  </p>
                </div>
              </div>
            </div>

            <div className={`rounded-lg shadow p-6 ${
              theme === 'dark' ? 'bg-gray-800' : 'bg-white'
            }`}>
              <div className="flex items-center">
                <Activity className="w-8 h-8 text-purple-500" />
                <div className="mr-4">
                  <p className={`text-sm font-medium ${
                    theme === 'dark' ? 'text-gray-300' : 'text-gray-600'
                  }`}>
                    מודל Embedding
                  </p>
                  <p className={`text-xs font-bold ${
                    theme === 'dark' ? 'text-white' : 'text-gray-900'
                  }`}>
                    Gemini Embedding
                  </p>
                </div>
              </div>
            </div>

            <div className={`rounded-lg shadow p-6 ${
              theme === 'dark' ? 'bg-gray-800' : 'bg-white'
            }`}>
              <div className="flex items-center">
                <CheckCircle className="w-8 h-8 text-green-500" />
                <div className="mr-4">
                  <p className={`text-sm font-medium ${
                    theme === 'dark' ? 'text-gray-300' : 'text-gray-600'
                  }`}>הושלמו</p>
                  <p className={`text-2xl font-bold ${
                    theme === 'dark' ? 'text-white' : 'text-gray-900'
                  }`}>
                    {stats.status_breakdown.completed || 0}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Upload Section */}
          <div className={`rounded-lg shadow p-6 ${
            theme === 'dark' ? 'bg-gray-800' : 'bg-white'
          }`}>
            <h2 className={`text-xl font-semibold mb-4 ${
              theme === 'dark' ? 'text-white' : 'text-gray-900'
            }`}>
              <Upload className="inline-block w-5 h-5 ml-2" />
              העלאת מסמך חדש
            </h2>

            <div className="space-y-4">
              <div>
                <input
                  type="file"
                  accept=".pdf,.txt,.docx,.doc"
                  onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                  className={`block w-full text-sm file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 ${
                    theme === 'dark' ? 'text-gray-300' : 'text-gray-500'
                  }`}
                />
              </div>

              <button
                onClick={handleFileUpload}
                disabled={!selectedFile || isUploading}
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isUploading ? "מעלה..." : "העלה מסמך"}
              </button>

              <p className={`text-sm ${
                theme === 'dark' ? 'text-gray-300' : 'text-gray-600'
              }`}>
                פורמטים נתמכים: PDF, TXT, DOCX, DOC
              </p>
            </div>
          </div>

          {/* Search Section */}
          <div className={`rounded-lg shadow p-6 ${
            theme === 'dark' ? 'bg-gray-800' : 'bg-white'
          }`}>
            <h2 className="text-xl font-semibold mb-4">
              <Search className="inline-block w-5 h-5 ml-2" />
              חיפוש במסמכים
            </h2>

            <div className="space-y-4">
              <div className="flex gap-2">
                <button
                  onClick={() => setSearchType("semantic")}
                  className={`px-3 py-1 rounded text-sm ${
                    searchType === "semantic"
                      ? "bg-blue-600 text-white"
                      : "bg-gray-200 text-gray-700"
                  }`}
                >
                  חיפוש סמנטי
                </button>
                <button
                  onClick={() => setSearchType("hybrid")}
                  className={`px-3 py-1 rounded text-sm ${
                    searchType === "hybrid"
                      ? "bg-blue-600 text-white"
                      : "bg-gray-200 text-gray-700"
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
                onKeyPress={(e) => e.key === "Enter" && handleSearch()}
              />

              <button
                onClick={handleSearch}
                disabled={!searchQuery.trim() || isSearching}
                className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 disabled:opacity-50"
              >
                {isSearching ? "מחפש..." : "חפש"}
              </button>
            </div>

            {/* Search Results */}
            {searchResults.length > 0 && (
              <div className="mt-6">
                <h3 className="font-semibold mb-3">
                  תוצאות חיפוש ({searchResults.length})
                </h3>
                <div className="space-y-3 max-h-64 overflow-y-auto">
                  {searchResults.map((result, index) => (
                    <div key={index} className={`p-3 rounded border ${
                      theme === 'dark' ? 'bg-gray-800 border-green-500/30' : 'bg-gray-50 border-gray-200'
                    }`}>
                      <div className="flex justify-between items-start mb-2">
                        <span className={`font-medium text-sm ${
                          theme === 'dark' ? 'text-green-400' : 'text-gray-900'
                        }`}>
                          {result.name}
                        </span>
                        <span className={`text-xs ${
                          theme === 'dark' ? 'text-gray-400' : 'text-gray-500'
                        }`}>
                          דמיון: {(result.similarity * 100).toFixed(1)}%
                        </span>
                      </div>
                      <p className={`text-sm line-clamp-3 ${
                        theme === 'dark' ? 'text-gray-300' : 'text-gray-700'
                      }`}>
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
        <div className={`mt-8 rounded-lg shadow ${
          theme === 'dark' ? 'bg-gray-800' : 'bg-white'
        }`}>
          <div className={`p-6 border-b ${
            theme === 'dark' ? 'border-green-500/30' : 'border-gray-200'
          }`}>
            <div className="flex justify-between items-center">
              <h2 className={`text-xl font-semibold ${
                theme === 'dark' ? 'text-green-400' : 'text-gray-900'
              }`}>
                רשימת מסמכים ({documents.length})
              </h2>

              {documents.length > 10 && (
                <ItemsPerPageSelector
                  itemsPerPage={itemsPerPage}
                  onItemsPerPageChange={(newItemsPerPage) => {
                    setItemsPerPage(newItemsPerPage);
                    setCurrentPage(1);
                  }}
                  options={[10, 25, 50, 100]}
                />
              )}
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className={`min-w-full divide-y ${
              theme === 'dark' ? 'divide-green-500/30' : 'divide-gray-200'
            }`}>
              <thead className={theme === 'dark' ? 'bg-gray-900' : 'bg-gray-50'}>
                <tr>
                  <th className={`px-6 py-3 text-right text-xs font-medium uppercase tracking-wider ${
                    theme === 'dark' ? 'text-green-400' : 'text-gray-500'
                  }`}>
                    שם המסמך
                  </th>
                  <th className={`px-6 py-3 text-right text-xs font-medium uppercase tracking-wider ${
                    theme === 'dark' ? 'text-green-400' : 'text-gray-500'
                  }`}>
                    סטטוס
                  </th>
                  <th className={`px-6 py-3 text-right text-xs font-medium uppercase tracking-wider ${
                    theme === 'dark' ? 'text-green-400' : 'text-gray-500'
                  }`}>
                    Chunks
                  </th>
                  <th className={`px-6 py-3 text-right text-xs font-medium uppercase tracking-wider ${
                    theme === 'dark' ? 'text-green-400' : 'text-gray-500'
                  }`}>
                    גודל
                  </th>
                  <th className={`px-6 py-3 text-right text-xs font-medium uppercase tracking-wider ${
                    theme === 'dark' ? 'text-green-400' : 'text-gray-500'
                  }`}>
                    תאריך יצירה
                  </th>
                  <th className={`px-6 py-3 text-right text-xs font-medium uppercase tracking-wider ${
                    theme === 'dark' ? 'text-green-400' : 'text-gray-500'
                  }`}>
                    פעולות
                  </th>
                </tr>
              </thead>
              <tbody className={`divide-y ${
                theme === 'dark' ? 'bg-gray-800 divide-green-500/30' : 'bg-white divide-gray-200'
              }`}>
                {paginatedDocuments.map((doc) => (
                  <tr key={doc.id}>
                    <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${
                      theme === 'dark' ? 'text-green-400' : 'text-gray-900'
                    }`}>
                      {doc.name}
                    </td>
                    <td className={`px-6 py-4 whitespace-nowrap text-sm ${
                      theme === 'dark' ? 'text-gray-300' : 'text-gray-500'
                    }`}>
                      <div className="flex items-center">
                        {getStatusIcon(doc.processing_status)}
                        <span className="mr-2">
                          {getStatusText(doc.processing_status)}
                        </span>
                      </div>
                    </td>
                    <td className={`px-6 py-4 whitespace-nowrap text-sm ${
                      theme === 'dark' ? 'text-gray-300' : 'text-gray-500'
                    }`}>
                      {doc.chunk_count}
                    </td>
                    <td className={`px-6 py-4 whitespace-nowrap text-sm ${
                      theme === 'dark' ? 'text-gray-300' : 'text-gray-500'
                    }`}>
                      {(doc.size / 1024).toFixed(1)} KB
                    </td>
                    <td className={`px-6 py-4 whitespace-nowrap text-sm ${
                      theme === 'dark' ? 'text-gray-300' : 'text-gray-500'
                    }`}>
                      {new Date(doc.created_at).toLocaleDateString("he-IL")}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button
                        onClick={() => handleDeleteDocument(doc.id)}
                        className={`hover:text-red-900 ${
                          theme === 'dark' ? 'text-red-400 hover:text-red-300' : 'text-red-600'
                        }`}
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {documents.length > itemsPerPage && (
            <div className={`px-6 py-3 border-t ${
              theme === 'dark' ? 'border-green-500/30' : 'border-gray-200'
            }`}>
              <Pagination
                currentPage={currentPage}
                totalItems={documents.length}
                itemsPerPage={itemsPerPage}
                onPageChange={setCurrentPage}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default VectorDashboard;
