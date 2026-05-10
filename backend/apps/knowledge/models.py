from django.db import models


class KnowledgeBase(models.Model):

    class DocType(models.TextChoices):
        FAQ = 'faq', 'FAQ'
        PDF = 'pdf', 'PDF Document'
        TEXT = 'text', 'Text Document'
        URL = 'url', 'Web URL'

    title = models.CharField(max_length=500)
    doc_type = models.CharField(max_length=20, choices=DocType.choices)
    content = models.TextField(blank=True)
    file = models.FileField(upload_to='knowledge/', null=True, blank=True)
    source_url = models.URLField(blank=True)
    is_indexed = models.BooleanField(default=False)
    chunk_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'knowledge_base'
        verbose_name = 'Knowledge Base Entry'
        verbose_name_plural = 'Knowledge Base'

    def __str__(self):
        return f'{self.title} ({self.doc_type})'


class Embedding(models.Model):
    knowledge = models.ForeignKey(
        KnowledgeBase, on_delete=models.CASCADE, related_name='embeddings'
    )
    chunk_index = models.PositiveIntegerField()
    chunk_text = models.TextField()
    chroma_id = models.CharField(max_length=100, unique=True, db_index=True)
    token_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'embeddings'
        verbose_name = 'Embedding'
        verbose_name_plural = 'Embeddings'
        unique_together = [('knowledge', 'chunk_index')]

    def __str__(self):
        return f'Embedding {self.chroma_id} (chunk {self.chunk_index})'
