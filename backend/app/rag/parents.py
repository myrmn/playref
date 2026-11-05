"""Parent section expansion helper."""

from qdrant_client import models

from backend.app.config import settings
from backend.app.ingestion.indexer import get_qdrant_client


class ParentExpander:
    """Retrieves parent section text to expand context when helpful."""

    def __init__(self, collection_name: str = settings.qdrant_collection):
        self.collection_name = collection_name
        self.client = get_qdrant_client()
        self._cache: dict[str, str | None] = {}

    def get_parent_text(self, parent_id: str | None) -> str | None:
        if not parent_id:
            return None

        if parent_id in self._cache:
            return self._cache[parent_id]

        try:
            results, _ = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="parent_id",
                            match=models.MatchValue(value=parent_id),
                        )
                    ]
                ),
                limit=1,
                with_payload=True,
            )
            if results:
                text = results[0].payload.get("clean_text")
                self._cache[parent_id] = text
                return text
        except Exception:
            pass

        self._cache[parent_id] = None
        return None


parent_expander = ParentExpander()
