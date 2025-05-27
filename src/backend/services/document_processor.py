import os
import asyncio
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import hashlib
import json
import tempfile

import google.generativeai as genai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
import tiktoken
from supabase import create_client, Client
import PyPDF2
from docx import Document as DocxDocument

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        self.supabase: Client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
        )
        # Configure Gemini - מגדיר מחדש את המפתח API בצורה ישירה מתוך משתני הסביבה
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY not found in environment variables")
        else:
            logger.info("GEMINI_API_KEY found in environment")
            
        genai.configure(api_key=api_key)
        self.gemini_model = genai.GenerativeModel('gemini-pro')
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        self.encoding = tiktoken.get_encoding("cl100k_base")

    async def process_document(self, document_id: int, file_path: str) -> Dict[str, Any]:
        """
        עיבוד מסמך מלא: חלוקה לחלקים, יצירת embeddings, ושמירה במסד הנתונים
        """
        try:
            logger.info(f"Starting processing document {document_id}")
            
            # Get document name
            doc_result = self.supabase.table("documents").select("name").eq("id", document_id).execute()
            document_name = doc_result.data[0]["name"] if doc_result.data else f"Document {document_id}"
            
            # Update status to processing
            await self._update_document_status(document_id, "processing")
            
            # Load and split document
            chunks = await self._load_and_split_document(file_path)
            logger.info(f"Document {document_id} split into {len(chunks)} chunks")
            
            # טעינה מחדש של משתני הסביבה לפני עיבוד המסמך
            import dotenv
            dotenv.load_dotenv(override=True)
            
            # וידוא שיש לנו מפתח API תקף
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                logger.error("GEMINI_API_KEY not found in environment variables during document processing")
                # נשתמש בסטטוס failed במקום failed_api_key
                await self._update_document_status(document_id, "failed")
                return {
                    "success": False,
                    "error": "Missing GEMINI_API_KEY in environment",
                    "document_id": document_id
                }
                
            logger.info(f"GEMINI_API_KEY found for document {document_id}, length: {len(api_key)}")
                
            # הגדר מחדש את ה-API key לספריית genai
            genai.configure(api_key=api_key)
            logger.info(f"Gemini API key configured successfully for document {document_id}")
            
            # Generate embeddings for each chunk
            embeddings_data = []
            chunk_info = []  # שמירת מידע נוסף לכל חלק עבור שימוש בטבלאות אחרות
            for i, chunk in enumerate(chunks):
                try:
                    # וידוא שהטקסט לא ריק
                    if not chunk.page_content.strip():
                        logger.warning(f"Empty content in chunk {i}, skipping")
                        continue
                        
                    embedding = await self._generate_embedding(chunk.page_content)
                    if not embedding or len(embedding) == 0:
                        logger.error(f"Empty embedding returned for chunk {i}")
                        continue
                        
                    token_count = len(self.encoding.encode(chunk.page_content))
                    
                    # נשמור רק את השדות שקיימים בטבלת document_chunks
                    embeddings_data.append({
                        "document_id": document_id,
                        "chunk_text": chunk.page_content,
                        "embedding": embedding,
                        "content_token_count": token_count
                    })
                    
                    # שמירת אינדקס החלק עבור השימוש בטבלת embeddings
                    chunk_info.append({"chunk_index": i})
                    logger.info(f"Generated embedding for chunk {i+1}/{len(chunks)}")
                except Exception as e:
                    logger.error(f"Error generating embedding for chunk {i}: {str(e)}")
                    continue
            
            # Save embeddings to database
            if embeddings_data:
                try:
                    # Save to document_chunks table
                    chunks_result = self.supabase.table("document_chunks").insert(embeddings_data).execute()
                    logger.info(f"Saved {len(embeddings_data)} chunks to document_chunks table")
                    
                    # הדפסה של הנתונים שנשמרו כדי לוודא
                    for i, data in enumerate(embeddings_data):
                        logger.info(f"Chunk {i} saved: document_id={data['document_id']}, embedding length={len(data['embedding'])}")
                    
                    # גם שמירה לטבלת embeddings לתאימות לאחור
                    try:
                        for i, item in enumerate(embeddings_data):
                            embedding_data = {
                                "content": item["chunk_text"],
                                "metadata": {"document_id": document_id, "chunk_index": chunk_info[i]["chunk_index"]},
                                "embedding": item["embedding"],
                            }
                            self.supabase.table("embeddings").insert(embedding_data).execute()
                        logger.info(f"Saved {len(embeddings_data)} items to embeddings table")
                    except Exception as e_back:
                        logger.error(f"Error saving to embeddings table (backwards compatibility): {str(e_back)}")
                    
                except Exception as db_error:
                    logger.error(f"Database error when saving embeddings: {str(db_error)}")
                    await self._update_document_status(document_id, "failed")
                    return {
                        "success": False,
                        "error": f"Database error: {str(db_error)}",
                        "document_id": document_id
                    }
            else:
                logger.warning(f"No valid embeddings generated for document {document_id}")
                await self._update_document_status(document_id, "failed")
                return {
                    "success": False,
                    "error": "No valid embeddings could be generated",
                    "document_id": document_id
                }
            
            # Update document status and content
            await self._update_document_status(document_id, "completed")
            await self._update_document_content(document_id, chunks)
            
            logger.info(f"Successfully processed document {document_id} with {len(chunks)} chunks")
            
            return {
                "success": True,
                "document_id": document_id,
                "chunks_created": len(chunks),
                "total_tokens": sum(len(self.encoding.encode(item["chunk_text"])) for item in embeddings_data)
            }
            
        except Exception as e:
            logger.error(f"Error processing document {document_id}: {str(e)}")
            await self._update_document_status(document_id, "failed")
            return {
                "success": False,
                "error": str(e),
                "document_id": document_id
            }

    async def _load_and_split_document(self, file_path: str) -> List[Any]:
        """טעינה וחלוקת מסמך לחלקים"""
        file_extension = Path(file_path).suffix.lower()
        
        try:
            if file_extension == '.pdf':
                # Use PyPDF2 for better compatibility
                text = self._extract_pdf_text(file_path)
                documents = [type('Document', (), {'page_content': text, 'metadata': {}})()]
            elif file_extension == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                documents = [type('Document', (), {'page_content': text, 'metadata': {}})()]
            elif file_extension in ['.docx', '.doc']:
                text = self._extract_docx_text(file_path)
                documents = [type('Document', (), {'page_content': text, 'metadata': {}})()]
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
            
            chunks = self.text_splitter.split_documents(documents)
            return chunks
            
        except Exception as e:
            logger.error(f"Error loading document {file_path}: {str(e)}")
            raise

    def _extract_pdf_text(self, file_path: str) -> str:
        """חילוץ טקסט מקובץ PDF"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            logger.error(f"Error extracting PDF text: {str(e)}")
            raise
        return text

    def _extract_docx_text(self, file_path: str) -> str:
        """חילוץ טקסט מקובץ DOCX"""
        try:
            doc = DocxDocument(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting DOCX text: {str(e)}")
            raise

    async def _generate_embedding(self, text: str) -> List[float]:
        """יצירת embedding לטקסט"""
        if not text or not text.strip():
            logger.error("Cannot generate embedding for empty text")
            raise ValueError("Text cannot be empty")
            
        # טעינה מחדש של משתני הסביבה - הוספנו את זה כברירת מחדל
        import dotenv
        dotenv.load_dotenv(override=True)
        
        # הגדר מחדש את ה-API key ישירות מסביבה
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            logger.error("GEMINI_API_KEY not found in environment variables")
            raise ValueError("Missing GEMINI_API_KEY in environment")
            
        logger.info(f"GEMINI_API_KEY found, length: {len(api_key)}")
            
        # הגדר מחדש את המפתח לספריית genai בכל פעם
        genai.configure(api_key=api_key)
        
        try:
            # התקשרות למודל ה-embedding של Gemini
            cleaned_text = text.replace("\n", " ").strip()
            logger.info(f"Generating embedding for text of length {len(cleaned_text)}")
            
            result = genai.embed_content(
                model="models/embedding-001",
                content=cleaned_text,
                task_type="retrieval_document"
            )
            
            # בדיקה שיש לנו תוצאה תקינה
            if not result or 'embedding' not in result:
                logger.error(f"Invalid embedding result: {result}")
                raise ValueError("Invalid embedding result from Gemini API")
                
            embedding = result['embedding']
            logger.info(f"Successfully generated embedding with {len(embedding)} dimensions")
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise

    async def _update_document_status(self, document_id: int, status: str):
        """עדכון סטטוס עיבוד המסמך"""
        try:
            # וידוא שהסטטוס הוא אחד מהערכים המותרים
            allowed_statuses = ['pending', 'processing', 'completed', 'failed']
            if status not in allowed_statuses:
                logger.warning(f"Invalid status '{status}', defaulting to 'failed'")
                status = 'failed'
                
            logger.info(f"Updating document {document_id} status to {status}")
            
            self.supabase.table("documents").update({
                "processing_status": status,
                "updated_at": "now()",
                "embedding_model": "gemini-embedding-001"
            }).eq("id", document_id).execute()
            logger.info(f"Updated document {document_id} status to {status}")
        except Exception as e:
            logger.error(f"Error updating document status: {str(e)}")
            logger.error(f"Failed to update document {document_id} status to {status}")

    async def _update_document_content(self, document_id: int, chunks: List[Any]):
        """עדכון תוכן המסמך"""
        try:
            full_content = "\n\n".join([chunk.page_content for chunk in chunks])
            self.supabase.table("documents").update({
                "content": full_content[:10000]  # Limit content size
            }).eq("id", document_id).execute()
        except Exception as e:
            logger.error(f"Error updating document content: {str(e)}")

    async def delete_document_embeddings(self, document_id: int) -> Dict[str, Any]:
        """מחיקת כל ה-embeddings של מסמך"""
        try:
            # Delete chunks
            result = self.supabase.table("document_chunks").delete().eq("document_id", document_id).execute()
            
            # Reset document status
            self.supabase.table("documents").update({
                "processing_status": "pending",
                "content": None,
                "embedding": None
            }).eq("id", document_id).execute()
            
            logger.info(f"Successfully deleted embeddings for document {document_id}")
            
            return {
                "success": True,
                "document_id": document_id,
                "chunks_deleted": len(result.data) if result.data else 0
            }
            
        except Exception as e:
            logger.error(f"Error deleting embeddings for document {document_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "document_id": document_id
            }

    async def search_documents(self, query: str, limit: int = 10, threshold: float = 0.78) -> List[Dict[str, Any]]:
        """חיפוש סמנטי במסמכים"""
        try:
            # Generate embedding for query
            query_embedding = await self._generate_embedding(query)
            
            # Search using the database function
            result = self.supabase.rpc("match_documents_semantic", {
                "query_embedding": query_embedding,
                "match_threshold": threshold,
                "match_count": limit
            }).execute()
            
            # Map results to standard format
            standardized_results = []
            if result.data:
                for item in result.data:
                    # Make sure we handle both content and chunk_text fields
                    content = item.get("content", item.get("chunk_text", ""))
                    standardized_results.append({
                        "id": item.get("id"),
                        "content": content,
                        "document_id": item.get("document_id"),
                        "chunk_index": item.get("chunk_index"),
                        "similarity": item.get("similarity", 0)
                    })
            
            return standardized_results
            
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            return []

    async def hybrid_search(self, query: str, limit: int = 10, threshold: float = 0.78) -> List[Dict[str, Any]]:
        """חיפוש היברידי (סמנטי + מילות מפתח)"""
        try:
            # Generate embedding for query
            query_embedding = await self._generate_embedding(query)
            
            # Search using the hybrid function
            result = self.supabase.rpc("match_documents_hybrid", {
                "query_embedding": query_embedding,
                "query_text": query,
                "match_threshold": threshold,
                "match_count": limit
            }).execute()
            
            # Map results to standard format
            standardized_results = []
            if result.data:
                for item in result.data:
                    # Make sure we handle both content and chunk_text fields
                    content = item.get("content", item.get("chunk_text", ""))
                    standardized_results.append({
                        "id": item.get("id"),
                        "content": content,
                        "document_id": item.get("document_id"),
                        "chunk_index": item.get("chunk_index"),
                        "similarity": item.get("similarity", 0),
                        "text_match_rank": item.get("text_match_rank", 0)
                    })
            
            return standardized_results
            
        except Exception as e:
            logger.error(f"Error in hybrid search: {str(e)}")
            return [] 