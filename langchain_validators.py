from langchain_core.pydantic_v1 import BaseModel, Field

class ExpectedOutputBotTA(BaseModel):
    go_database: bool = Field(..., description = "True if it is question is about food catalog or table availability. Otherwise, False.")
