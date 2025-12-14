from typing import Dict, Optional
from pydantic import BaseModel


class ConstraintDefinitionVo(BaseModel):
    code: str
    soft_flag: bool
    penalty_weight: Optional[float]
    parameters: Optional[Dict[str, str]]
