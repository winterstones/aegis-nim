"""Central application settings using Pydantic Settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # NVIDIA NIM
    nvidia_api_key: str = Field(default="mock-key", alias="NVIDIA_API_KEY")
    nim_base_url: str = Field(default="https://integrate.api.nvidia.com/v1", alias="NIM_BASE_URL")
    nim_model: str = Field(default="deepseek-ai/deepseek-v4-flash-0731", alias="NIM_MODEL")

    # NeMo Guardrails
    nemo_config_path: str = Field(default="config/guardrails", alias="NEMO_CONFIG_PATH")

    # Simulation & Ops
    mock_mode: bool = Field(default=True, alias="MOCK_MODE")
    hitl_timeout_seconds: int = Field(default=30, alias="HITL_TIMEOUT_SECONDS")
    step_delay_seconds: float = Field(default=2.0, alias="STEP_DELAY_SECONDS")


settings = Settings()
