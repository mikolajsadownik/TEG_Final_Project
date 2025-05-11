from config.config_manager import ConfigManager

def get_frontend_message():
    config = ConfigManager()
    welcome_message = config.get("WELCOME_MESSAGE", "Hello from the frontend!")
    return welcome_message
