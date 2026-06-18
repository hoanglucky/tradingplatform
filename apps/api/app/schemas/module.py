from pydantic import BaseModel


class ModuleStatus(BaseModel):
    name: str
    role: str
    status: str

