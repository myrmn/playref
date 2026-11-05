"""Vision client stub for PlayRef (To be implemented in Phase 4)."""

from typing import Any


class VisionClient:
    """Stub client for vision and multimodal analysis."""

    async def analyze_image(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError(
            "Vision analysis is out of scope for Phase 1 (scheduled for Phase 4)."
        )


vision_client = VisionClient()
