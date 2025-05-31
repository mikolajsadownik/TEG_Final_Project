
import logging

logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
import logging

logger = logging.getLogger(__name__)

class AiAgentError(Exception):
    def __init__(self, message):
        super().__init__(message)
        logger.error(f"An error occurred: {message}")

    def log_error(self):
        logger.error(f"Logged error: {self.args[0]}")

    def __str__(self):
        return f"Error: {self.args[0]}"


class BadUserPrompt(AiAgentError):
    def __init__(self,user_prompt):
        super().__init__(f"User gave bad prompt: {user_prompt}")


class BadAiApiRes(AiAgentError):
    def __init__(self, user_prompt):
        super().__init__(f"Unexpected answer for user prompt: {user_prompt}")

