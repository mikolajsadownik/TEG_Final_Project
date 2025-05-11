from config.config_manager import ConfigManager

def run_ai_service():
    config = ConfigManager()
    ai_model = config.get("AI_MODEL", "default-model")
    print(f"Running AI service with model: {ai_model}")