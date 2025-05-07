"""
Retriever module for the Afeka ChatBot RAG system.
"""
import logging
import json
import os
from typing import List, Dict, Any, Optional, Union, Tuple
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.embeddings import Embeddings

from .vector_store import search_vector_store

logger = logging.getLogger(__name__)

def get_llm(api_key: Optional[str] = None, model_name: str = "gemini-1.5-flash") -> ChatGoogleGenerativeAI:
    """
    Get a language model instance.
    
    Args:
        api_key: Optional API key. If not provided, will use environment variable.
        model_name: Model to use.
        
    Returns:
        ChatGoogleGenerativeAI model.
    """
    try:
        # Get API key from environment if not provided
        if not api_key:
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                logger.error("GEMINI_API_KEY not found in environment variables")
                raise ValueError("GEMINI_API_KEY is required")
        
        # Configure generation parameters
        generation_config = {
            "temperature": 0.3,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 1024
        }
        
        # Create and return the LLM
        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=generation_config["temperature"],
            top_p=generation_config["top_p"],
            top_k=generation_config["top_k"],
            max_output_tokens=generation_config["max_output_tokens"],
            convert_system_message_to_human=True  # Better handling of system messages
        )
    except Exception as e:
        logger.error(f"Error creating LLM: {str(e)}")
        # Return a dummy LLM for testing (will not actually work)
        logger.warning("Using fallback LLM for testing - no real AI responses will be generated")
        return ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key="dummy_key")

def get_prompt_template() -> ChatPromptTemplate:
    """
    Get prompt template for question answering.
    
    Returns:
        ChatPromptTemplate object.
    """
    system_message = """
אתה עוזר חכם של מכללת אפקה להנדסה. תפקידך לסייע לסטודנטים ולמרצים במציאת מידע אקדמי.
מידע זה:
{context}

ענה על השאלה של המשתמש בהתבסס על המידע המסופק לעיל בלבד.
אם המידע המסופק לא מכיל את התשובה לשאלה, ציין זאת באופן מפורש ואל תמציא מידע.
השתדל לנסח את תשובתך בבהירות, באופן מקצועי אך ידידותי.
עיין בכל המידע המסופק ונסח תשובה מלאה ומפורטת במבנה של פסקאות.

כשאתה מצטט מידע:
1. ציין תמיד את המקור המדויק של המידע: "(מתוך: [שם המסמך המדויק], סעיף X.Y)".
2. אם מצטט מסעיף, השתמש במבנה: "בסעיף X.Y במסמך [שם המסמך] נאמר: ...".
3. חשוב מאוד: ציין את שם המסמך המדויק לכל ציטוט, במיוחד אם המידע מגיע ממסמכים שונים.
4. לעולם אל תשתמש בביטויים כמו "מסמך 1" או "מסמך 2". השתמש בשם המלא של המסמך.

כאשר נשאלת על סעיפים מסוימים:
1. אם המידע מכיל את הסעיף המדויק שנשאלת עליו, הקפד לצטט אותו במדויק ולציין את שם המסמך.
2. השתמש במונחים "בסעיף X במסמך [שם המסמך] נאמר:" או "סעיף Y במסמך [שם המסמך] קובע:". 
3. אם הסעיף המסוים אינו מופיע במידע המסופק, הבהר זאת באופן מפורש.

כאשר המידע מגיע מנוהל המילואים, ציין זאת באופן מפורש: "מתוך נוהל זכויות סטודנטים המשרתים במילואים".

שפת התשובה: עברית
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("human", "{question}")
    ])
    
    return prompt

def get_query_analysis_prompt() -> ChatPromptTemplate:
    """
    Get prompt template for query analysis.
    
    Returns:
        ChatPromptTemplate object.
    """
    system_message = """
אתה מנתח שאלות עבור מערכת RAG של מכללת אפקה להנדסה. 
משימתך היא לנתח את שאלת המשתמש ולספק מידע שיעזור למצוא את התוכן הרלוונטי ביותר.

טיפול מיוחד בשאילתות:

1. סעיפים בתקנון:
   - אם השאלה מכילה בקשה למידע על סעיף מסוים (לדוגמה: "סעיף 4.3", "סעיף 5.1"), חשוב להתמקד בתוכן הסעיף הזה בדיוק.
   - הקפד לציין את מספר הסעיף בשאילתת החיפוש באופן מדויק.

2. נושאים מרכזיים:
   - מילואים: אם השאלה קשורה לזכויות סטודנטים במילואים, ציין זאת במפורש בשדה category וסמן את הנושא ברשימת נושאים (topics).
   - בחינות: אם מדובר בשאלה על בחינות, מועדי בחינה, מועד מיוחד, ערעורים, או נושאים קשורים, הוסף מילות מפתח כמו "בחינות", "מועד בחינה".
   - נוכחות: אם השאלה עוסקת בנוכחות בקורסים, היעדרות, או אחוזי נוכחות, סמן זאת בנושאים.

הנחיות נוספות:
- התמקד בנושאים המרכזיים בשאלת המשתמש.
- הוצא מילות מפתח רלוונטיות שיכולות לעזור במציאת המידע המדויק.
- אל תוסיף מידע שלא קיים בשאלה המקורית.

פורמט התשובה:
תחזיר ב-JSON פשוט את הניתוח שלך עם השדות הבאים:
- search_query: שאילתת חיפוש אופטימלית בהתבסס על השאלה המקורית
- category: הקטגוריה המרכזית של השאלה (למשל: בחינות, נוכחות, מילואים, כללי)
- doc_type: סוג המסמך הרלוונטי אם ידוע (למשל: תקנון, נוהל)
- section_number: מספר סעיף ספציפי אם מוזכר בשאלה
- topics: רשימה של נושאים רלוונטיים (למשל: [בחינות, מועד מיוחד, מילואים])
"""
    
    human_message = """
שאלת המשתמש: {question}

נתח את השאלה וספק את המידע הדרוש לחיפוש יעיל.
"""
    
    return ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("human", human_message)
    ])

def analyze_query(question: str, llm: Optional[ChatGoogleGenerativeAI] = None) -> Dict[str, Any]:
    """
    Analyze a query to determine the best search strategy.
    
    Args:
        question: User question.
        llm: LLM for analysis. If not provided, one will be created.
        
    Returns:
        Dictionary containing structured analysis of the query.
    """
    if not llm:
        llm = get_llm()
    
    try:
        prompt = get_query_analysis_prompt()
        chain = prompt | llm | StrOutputParser()
        
        # Pass only the question without any additional parameters
        result = chain.invoke({"question": question})
        
        try:
            # Parse the JSON output
            analysis = json.loads(result)
            logger.info(f"Query analysis: {analysis}")
            return analysis
        except Exception as e:
            logger.error(f"Error parsing query analysis JSON: {e}")
            logger.error(f"Raw output: {result}")
            # Return a default analysis with the original question as the search query
            return {
                "search_query": question,
                "category": "general",
                "doc_type": "unknown",
                "section_number": "None",
                "topics": []
            }
    except Exception as e:
        logger.error(f"Error analyzing query: {e}")
        # Return a default analysis
        return {
            "search_query": question,
            "category": "general",
            "doc_type": "unknown", 
            "section_number": "None",
            "topics": []
        }

def format_context(docs: List[Document]) -> str:
    """
    Format documents into a string context for the prompt.
    
    Args:
        docs: List of Document objects.
        
    Returns:
        Formatted context string.
    """
    if not docs:
        return "לא נמצאו מסמכים רלוונטיים."
    
    context_texts = []
    
    for doc in docs:
        source = doc.metadata.get("source", "מקור לא ידוע")
        title = doc.metadata.get("title", "כותרת לא ידועה")
        doc_type = doc.metadata.get("doc_type", "")
        category = doc.metadata.get("category", "")
        section_number = doc.metadata.get("section_number", "")
        section_title = doc.metadata.get("section_title", "")
        
        # יצירת שם מסמך מלא ומפורט
        document_name = title
        if doc_type:
            document_name = f"{title} ({doc_type})"
        
        # הוספת מידע על הסעיף אם קיים
        section_info = ""
        if section_number and section_title:
            section_info = f" - סעיף {section_number}: {section_title}"
        elif section_number:
            section_info = f" - סעיף {section_number}"
        
        # Format the document content with detailed source information without numbering the documents
        formatted_doc = f"[{document_name}{section_info}]\n{doc.page_content}\n"
        context_texts.append(formatted_doc)
    
    return "\n\n".join(context_texts)

def create_retrieval_chain(
    vector_store: VectorStore,
    llm: Optional[ChatGoogleGenerativeAI] = None
):
    """
    Create a retrieval chain for question answering.
    
    Args:
        vector_store: Vector store for retrieving documents.
        llm: LLM for generation. If not provided, one will be created.
        
    Returns:
        Retrieval chain.
    """
    if not vector_store:
        logger.error("No vector store provided")
        raise ValueError("Vector store is required")
    
    if not llm:
        llm = get_llm()
    
    # Define the retrieval function
    def retrieve_and_format(query_info):
        # Handle if query_info is a string or a dictionary
        if isinstance(query_info, str):
            query = query_info
        else:
            # Assume it's a dictionary with a 'question' key
            query = query_info.get("question", "")
        
        # Try to analyze the query for better retrieval
        try:
            # קוראים לפונקציה עם שאילתה בלבד
            analysis = analyze_query(query, llm)
            search_query = analysis.get("search_query", query)
            category = analysis.get("category")
            doc_type = analysis.get("doc_type")
            section_number = analysis.get("section_number")
            topics = analysis.get("topics", [])
            
            # Log the analysis for debugging
            logger.info(f"Query analysis results: search_query='{search_query}', category='{category}', doc_type='{doc_type}', section_number='{section_number}', topics={topics}")
            
            # Enhance query with topics if available and relevant
            if topics and len(topics) > 0:
                search_terms = []
                for topic in topics:
                    if topic and topic.strip() and topic.strip() not in search_query:
                        search_terms.append(topic.strip())
                
                if search_terms:
                    enhanced_query = f"{search_query} {' '.join(search_terms)}"
                    logger.info(f"Enhanced query with topics: {enhanced_query}")
                    search_query = enhanced_query
            
            # Get relevant documents based on the analysis
            docs = search_vector_store(
                vector_store=vector_store,
                query=search_query,
                k=4,
                category=category if category and category != "general" else None,
                doc_type=doc_type if doc_type and doc_type != "unknown" else None,
                section_number=section_number if section_number else None,
                topics=topics if topics and len(topics) > 0 else None
            )
        except Exception as e:
            logger.error(f"Error in query analysis, falling back to basic retrieval: {e}")
            docs = vector_store.similarity_search(query=query, k=4)
        
        # Format the retrieved documents into a context string
        return format_context(docs)
    
    # Create the chain
    prompt = get_prompt_template()
    
    # Build the retrieval chain
    chain = (
        {"context": retrieve_and_format, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return chain

def get_answer(
    question: str,
    vector_store: VectorStore,
    llm: Optional[ChatGoogleGenerativeAI] = None
) -> Tuple[str, List[Document]]:
    """
    Get an answer for a question using RAG.
    
    Args:
        question: User question.
        vector_store: Vector store for retrieving documents.
        llm: Language model for generation. If not provided, one will be created.
        
    Returns:
        Tuple of (answer, relevant docs)
    """
    if not llm:
        llm = get_llm()
    
    # Log the input for debugging
    logger.info(f"Processing question: {repr(question)}")
    
    try:
        # Create chain
        chain = create_retrieval_chain(vector_store, llm)
        
        # Get the answer
        logger.info("Executing retrieval chain")
        answer = chain.invoke(question)
        
        # Extract relevant documents 
        # This needs to be done separately since the chain only returns the answer text
        logger.info("Retrieving relevant documents")
        
        # Try to analyze the query for better retrieval
        try:
            analysis = analyze_query(question, llm)
            search_query = analysis.get("search_query", question)
            category = analysis.get("category")
            doc_type = analysis.get("doc_type")
            section_number = analysis.get("section_number")
            topics = analysis.get("topics", [])
            
            logger.info(f"Query analysis results: search_query='{search_query}', category='{category}', doc_type='{doc_type}', section_number='{section_number}', topics={topics}")
            
            # Enhance query with topics if available and relevant
            if topics and len(topics) > 0:
                search_terms = []
                for topic in topics:
                    if topic and topic.strip() and topic.strip() not in search_query:
                        search_terms.append(topic.strip())
                
                if search_terms:
                    enhanced_query = f"{search_query} {' '.join(search_terms)}"
                    logger.info(f"Enhanced query with topics: {enhanced_query}")
                    search_query = enhanced_query
            
            # Get relevant documents based on the analysis
            docs = search_vector_store(
                vector_store=vector_store,
                query=search_query,
                k=4,
                category=category if category and category != "general" else None,
                doc_type=doc_type if doc_type and doc_type != "unknown" else None,
                section_number=section_number if section_number else None,
                topics=topics if topics and len(topics) > 0 else None
            )
        except Exception as e:
            logger.error(f"Error in query analysis, falling back to basic retrieval: {e}")
            docs = vector_store.similarity_search(query=question, k=4)
            
        # Log retrieval results
        logger.info(f"Retrieved {len(docs)} relevant documents")
        for i, doc in enumerate(docs[:3]):  # Log first 3 docs
            source = doc.metadata.get("source", "unknown")
            content_preview = doc.page_content[:100].replace('\n', ' ')
            logger.info(f"Doc {i+1}: Source={source}, Content='{content_preview}...'")
            
        # Check if answer is valid UTF-8 text (sometimes Hebrew can cause issues)
        try:
            answer.encode('utf-8').decode('utf-8')
        except UnicodeError:
            logger.warning("Unicode issue detected in answer, attempting to fix encoding")
            # Try to fix encoding issues
            answer = answer.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
        
        # Log the answer for debugging
        logger.info(f"Generated answer (preview): {answer[:200]}")
        
        return answer, docs
    except Exception as e:
        logger.error(f"Error in RAG process: {str(e)}", exc_info=True)
        raise 

def search_vector_store(
    vector_store: VectorStore,
    query: str,
    k: int = 4,
    category: Optional[str] = None,
    doc_type: Optional[str] = None,
    section_number: Optional[str] = None,
    topics: Optional[List[str]] = None
) -> List[Document]:
    """
    Search for documents in the vector store with optional filtering.
    
    Args:
        vector_store: VectorStore to search in.
        query: Query string.
        k: Number of documents to return.
        category: Optional category filter.
        doc_type: Optional document type filter.
        section_number: Optional section number to search for.
        topics: Optional list of topics to enhance search.
        
    Returns:
        List of Document objects.
    """
    # Log input parameters
    logger.info(f"Searching for documents with: query='{query}', k={k}, category={category}, doc_type={doc_type}, section_number={section_number}, topics={topics}")
    
    # Enhance query with section number information if available
    original_query = query
    
    # טיפול בסעיפים
    if section_number:
        # Add section number to the query explicitly
        section_terms = [f"סעיף {section_number}", f"פרק {section_number}", f"חלק {section_number}"]
        enhanced_queries = [f"{term} {original_query}" for term in section_terms]
        enhanced_queries.append(f"{original_query} {section_number}")
        
        # Try each enhanced query
        all_docs = []
        for enhanced_query in enhanced_queries:
            logger.info(f"Trying enhanced query: '{enhanced_query}'")
            docs = vector_store.similarity_search(
                enhanced_query,
                k=k,
                filter=None  # Don't use filters with enhanced queries
            )
            if docs:
                all_docs.extend(docs)
                
        # If we found documents with enhanced queries, return them
        if all_docs:
            # Remove duplicates based on content
            unique_docs = []
            seen_contents = set()
            for doc in all_docs:
                content_hash = hash(doc.page_content)
                if content_hash not in seen_contents:
                    seen_contents.add(content_hash)
                    unique_docs.append(doc)
            
            # Return up to k unique documents
            return unique_docs[:k]
    
    # טיפול בנושאים
    if topics and len(topics) > 0:
        # נסה לשפר את החיפוש עם נושאים ספציפיים
        enhanced_topic_queries = []
        for topic in topics:
            if topic and topic.strip() and topic.strip() not in original_query:
                enhanced_topic_queries.append(f"{original_query} {topic.strip()}")
                
        if enhanced_topic_queries:
            all_topic_docs = []
            for topic_query in enhanced_topic_queries:
                logger.info(f"Trying topic-enhanced query: '{topic_query}'")
                docs = vector_store.similarity_search(
                    topic_query,
                    k=2,  # פחות מסמכים לכל שאילתת נושא
                    filter=None
                )
                if docs:
                    all_topic_docs.extend(docs)
                    
            if all_topic_docs:
                # הסר כפילויות
                unique_topic_docs = []
                seen_contents = set()
                for doc in all_topic_docs:
                    content_hash = hash(doc.page_content)
                    if content_hash not in seen_contents:
                        seen_contents.add(content_hash)
                        unique_topic_docs.append(doc)
                
                # Return up to k unique documents
                if len(unique_topic_docs) >= k:
                    return unique_topic_docs[:k]
    
    # Ensure query is properly encoded for multibyte characters like Hebrew
    try:
        # Test if string can be properly encoded
        query_bytes = query.encode('utf-8')
        logger.info(f"Query length in bytes: {len(query_bytes)}")
        # Decode back just to make sure everything is fine
        query = query_bytes.decode('utf-8')
    except UnicodeError as e:
        # If there's an encoding issue, try to fix it
        logger.warning(f"Unicode issue with query: {e}")
        query = query.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
        logger.info(f"Fixed query: {query}")
    
    # Build filter dictionary for search
    filters = {}
    
    if category:
        filters["category"] = category
    
    if doc_type:
        filters["doc_type"] = doc_type
    
    # Search for documents
    if filters:
        logger.info(f"Searching with filters: {filters}")
        docs = vector_store.similarity_search(query, k=k, filter=filters)
    else:
        logger.info(f"Searching without filters")
        docs = vector_store.similarity_search(query, k=k)
    
    # Log the results
    logger.info(f"Retrieved {len(docs)} documents for query '{query}'")
    for i, doc in enumerate(docs[:2]):  # Log just first 2 for brevity
        metadata_str = ', '.join([f"{k}={v}" for k, v in doc.metadata.items() if k in ['source', 'title', 'doc_type', 'category']])
        logger.info(f"Doc {i+1}: {metadata_str}")
    
    return docs 