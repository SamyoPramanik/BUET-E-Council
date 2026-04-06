from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    # Method A: Use a default of None but tell Pydantic it MUST be a string
    # 'None' satisfies Pylance, but Pydantic will still validate it's in .env
    SECRET_KEY: Optional[str] = Field(default=None) 
    
    FRONTEND_URL: str = "http://localhost:5173"
    
    model_config = SettingsConfigDict(env_file=".env")

# Now Pylance sees that Settings() doesn't *require* arguments in the constructor
settings = Settings()