import sys
from loguru import logger


logger.remove()
logger.add(
    sink=sys.stdout, 
    format="<r>[Not pixel]</r> | <white>{time:YYYY-MM-DD HH:mm:ss}</white>"
           " | <level>{level: <8}</level>"
           " | <cyan><b>{line}</b></cyan>"
           " - <white><b>{message}</b></white>")
logger = logger.opt(colors=True)

except Exception as e:
    logger.error(f"Failed to configure logger: {e}")
