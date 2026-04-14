from pydantic import BaseModel
from typing import Any, Optional


class AgentResponse(BaseModel):
    """
    Standard API response model using Pydantic.
    Ensures validation + serialization + schema generation.
    """

    status: int
    data: Any = None
    message: Optional[str] = None
    success: bool = True