### New Environment Variables for RAG Service
 
| Variable                | Description                                                                                                                               | Default Value |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- | ------------- |
| `ENABLE_RERANK`         | Global switch to enable (`true`) or disable (`false`) the reranking step in the RAG pipeline.                                           | `true`        |
| `RERANK_THREADS`        | Number of worker threads to use in the `ThreadPoolExecutor` for the reranking process (CrossEncoder predictions).                     | `4`           |
| `RERANK_LATENCY_CAP_S`  | Latency cap in seconds for the reranking step. If a single rerank operation exceeds this, reranking will be dynamically disabled for that `RAGService` instance to maintain performance. | `1.5`         | 