"""Application configuration derived from F-14 System Configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """CLB application settings."""

    # Google Calendar OAuth
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/v1/auth/google/callback"

    # Database
    database_url: str = "postgresql://clb_user:clb_password@localhost:5432/clb_db"

    # Application
    app_secret_key: str = "change-me-in-production"
    app_env: str = "development"
    frontend_url: str = "http://localhost:3000"

    # Miro
    miro_board_url: str = "https://miro.com/app/board/uXjVHOUD00o=/"

    # CLB System Configuration (F-14: CFG-01 through CFG-12)
    work_hours_start: str = "08:00"  # CFG-01
    work_hours_end: str = "18:00"  # CFG-02
    after_hours_threshold_mins: int = 30  # CFG-03
    work_days: list[str] = ["Mon", "Tue", "Wed", "Thu", "Fri"]  # CFG-04
    demo_mode_enabled: bool = False  # CFG-05
    demo_actor_name: str = "Alex Chen"  # CFG-06
    timezone: str = "America/Los_Angeles"  # CFG-07
    data_retention_days: int = 90  # CFG-08
    score_refresh_interval_mins: int = 15  # CFG-09
    focus_block_duration_mins: int = 120  # CFG-10
    back_to_back_gap_threshold_mins: int = 15  # CFG-11
    weekend_alert_enabled: bool = True  # CFG-12

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
