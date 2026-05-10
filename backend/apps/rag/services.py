import logging
import re

logger = logging.getLogger(__name__)


class RAGService:

    def _get_embedding_function(self):
        from django.conf import settings
        api_key = getattr(settings, 'OPENAI_API_KEY', '')
        if not api_key:
            return None
        try:
            from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
            return OpenAIEmbeddingFunction(
                api_key=api_key,
                model_name=getattr(settings, 'RAG_EMBEDDING_MODEL', 'text-embedding-3-small'),
            )
        except Exception as e:
            logger.warning(f'OpenAI embedding function unavailable, using default: {e}')
            return None

    def _get_client(self):
        import chromadb
        import requests as req
        from django.conf import settings

        base = f"http://{settings.CHROMA_HOST}:{settings.CHROMA_PORT}"

        # Ensure tenant and database exist (ChromaDB 1.0 uses /api/v2)
        try:
            req.post(f"{base}/api/v2/tenants", json={"name": "default_tenant"}, timeout=5)
        except Exception:
            pass
        try:
            req.post(f"{base}/api/v2/tenants/default_tenant/databases", json={"name": "default_database"}, timeout=5)
        except Exception:
            pass

        return chromadb.HttpClient(
            host=settings.CHROMA_HOST,
            port=settings.CHROMA_PORT,
            tenant='default_tenant',
            database='default_database',
        )

    def _get_collection(self):
        from django.conf import settings
        client = self._get_client()
        kwargs = {
            'name': settings.CHROMA_COLLECTION,
            'metadata': {'hnsw:space': 'cosine'},
        }
        embedding_fn = self._get_embedding_function()
        if embedding_fn:
            kwargs['embedding_function'] = embedding_fn
        return client.get_or_create_collection(**kwargs)

    def search(self, query: str, client_id: int = None, top_k: int = None) -> str:
        from django.conf import settings
        threshold = getattr(settings, 'RAG_DISTANCE_THRESHOLD', 0.7)
        if top_k is None:
            top_k = getattr(settings, 'RAG_TOP_K', 5)

        try:
            collection = self._get_collection()
            count = collection.count()
            if count == 0:
                return ''

            results = collection.query(
                query_texts=[query],
                n_results=min(top_k, count),
                include=['documents', 'distances', 'metadatas'],
            )

            docs = results.get('documents', [[]])[0]
            distances = results.get('distances', [[]])[0]
            metadatas = results.get('metadatas', [[]])[0]

            relevant = []
            for doc, dist, meta in zip(docs, distances, metadatas):
                if dist < threshold:
                    title = meta.get('title', '')
                    relevant.append(f'[{title}]\n{doc}' if title else doc)

            return '\n\n'.join(relevant) if relevant else ''

        except Exception as e:
            logger.warning(f'RAG search failed: {e}')
            return ''

    def index_document(self, knowledge_id: int):
        try:
            from apps.knowledge.models import KnowledgeBase, Embedding

            doc = KnowledgeBase.objects.get(id=knowledge_id)
            text = self._extract_text(doc)
            chunks = self._split_text(text)

            if not chunks:
                logger.warning(f'No text extracted from document {knowledge_id}')
                return

            # Remove old chunks before re-indexing
            old_ids = list(
                Embedding.objects.filter(knowledge=doc).values_list('chroma_id', flat=True)
            )
            if old_ids:
                try:
                    collection = self._get_collection()
                    collection.delete(ids=old_ids)
                except Exception:
                    pass
                Embedding.objects.filter(knowledge=doc).delete()

            collection = self._get_collection()
            ids, texts, metadatas = [], [], []
            embeddings_to_create = []

            for i, chunk in enumerate(chunks):
                chroma_id = f'doc_{knowledge_id}_chunk_{i}'
                ids.append(chroma_id)
                texts.append(chunk)
                metadatas.append({
                    'knowledge_id': knowledge_id,
                    'chunk_index': i,
                    'title': doc.title,
                    'doc_type': doc.doc_type,
                })
                embeddings_to_create.append(Embedding(
                    knowledge=doc,
                    chunk_index=i,
                    chunk_text=chunk,
                    chroma_id=chroma_id,
                    token_count=len(chunk.split()),
                ))

            collection.upsert(ids=ids, documents=texts, metadatas=metadatas)
            Embedding.objects.bulk_create(embeddings_to_create)

            doc.is_indexed = True
            doc.chunk_count = len(chunks)
            doc.save(update_fields=['is_indexed', 'chunk_count'])
            logger.info(f'Indexed document {knowledge_id}: {len(chunks)} chunks')

        except Exception as e:
            logger.exception(f'Failed to index document {knowledge_id}: {e}')
            raise

    def delete_document(self, knowledge_id: int):
        try:
            from apps.knowledge.models import Embedding
            ids = list(
                Embedding.objects.filter(knowledge_id=knowledge_id).values_list('chroma_id', flat=True)
            )
            if ids:
                collection = self._get_collection()
                collection.delete(ids=ids)
                Embedding.objects.filter(knowledge_id=knowledge_id).delete()
        except Exception as e:
            logger.warning(f'Failed to delete document {knowledge_id} from Chroma: {e}')

    def _split_text(self, text: str, chunk_size: int = 400, overlap: int = 40) -> list[str]:
        if not text or not text.strip():
            return []

        # Split by sentence boundaries for semantic coherence
        sentences = re.split(r'(?<=[.!?\n])\s+', text.strip())
        chunks = []
        current_words: list[str] = []

        for sentence in sentences:
            words = sentence.split()
            if not words:
                continue
            if len(current_words) + len(words) > chunk_size and current_words:
                chunks.append(' '.join(current_words))
                current_words = current_words[-overlap:] + words
            else:
                current_words.extend(words)

        if current_words:
            chunks.append(' '.join(current_words))

        return [c.strip() for c in chunks if c.strip()]

    def _extract_text(self, doc) -> str:
        if doc.doc_type == 'url' and doc.source_url:
            fetched = self._fetch_url(doc.source_url)
            return fetched or doc.content
        if doc.content:
            return doc.content
        if doc.file and doc.doc_type == 'pdf':
            try:
                from pypdf import PdfReader
                reader = PdfReader(doc.file.path)
                return '\n'.join(page.extract_text() or '' for page in reader.pages)
            except Exception as e:
                logger.warning(f'PDF extraction failed: {e}')
        return ''

    def _fetch_url(self, url: str) -> str:
        try:
            import requests
            resp = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
            resp.raise_for_status()
            # Strip scripts, styles, and HTML tags
            text = re.sub(r'<script[^>]*>.*?</script>', '', resp.text, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r'<[^>]+>', ' ', text)
            text = re.sub(r'&\w+;', ' ', text)
            text = re.sub(r'\s+', ' ', text).strip()
            return text[:50000]
        except Exception as e:
            logger.warning(f'URL fetch failed for {url}: {e}')
            return ''


rag_service = RAGService()
