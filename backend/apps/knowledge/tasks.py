import logging
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, queue='default', max_retries=3)
def index_document_task(self, knowledge_id: int):
    """Index a knowledge base document into ChromaDB."""
    try:
        from apps.rag.services import rag_service
        rag_service.index_document(knowledge_id)
    except Exception as exc:
        logger.exception(f'Failed to index document {knowledge_id}: {exc}')
        raise self.retry(exc=exc, countdown=30)
