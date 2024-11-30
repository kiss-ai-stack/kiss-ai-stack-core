from typing import Optional

from pydantic import BaseModel

from kiss_ai_stack.core.models.config.ai_client import AIClientProperties
from kiss_ai_stack.core.models.enums.tool_kind import ToolKind


class ToolProperties(BaseModel):
    name: str
    role: str
    kind: ToolKind
    ai_client: AIClientProperties
    embeddings: Optional[str] = None

    class Config:
        str_min_length = 1
        str_strip_whitespace = True