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

if __name__ == "__main__":
    df = load_data("data.parquet", columns=["count"])
    logger.info("Data Loaded")

    logger.info("Loading Model")
    nlp = spacy.load("en_core_web_lg", disable=["ner"])
    logger.info(f"loaded model. Pipeline: {nlp.pipe_names}")
    logger.error(f"Failed to configure logger: {e}")
