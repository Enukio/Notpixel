import sys
from loguru import logger

# Remove default logger configuration
logger.remove()

# Add a new sink with improved format
logger.add(
    sink=sys.stdout,
    format="<white>{time:YYYY-MM-DD HH:mm:ss}</white> | "
           "<level>{level: <8}</level> | "
           "<cyan>Line {line}</cyan> - <white>{message}</white>",
    colorize=True
)

# Optional: Add a safeguard for adding more sinks or use cases
try:
    # Example of adding a file sink (commented out for flexibility)
    # logger.add("app.log", rotation="1 MB", retention="10 days", compression="zip")
    pass
except Exception as e:
    logger.error(f"Failed to configure logger: {e}")
