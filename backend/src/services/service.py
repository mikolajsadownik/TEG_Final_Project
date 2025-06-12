from src.config.config_manager import ConfigManager

def run_backend_service():
    config = ConfigManager()
    db_url = config.get("DB_URL", "localhost:5432")
    print(f"Running backend service connected to: {db_url}")
