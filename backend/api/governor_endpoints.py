from fastapi import APIRouter, HTTPException
import logging

router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.get("/hello")
async def hello_world():
    """Returns a hello world message."""
    try:
        logger.info("Hello World endpoint called")
        return {"message": "Hello, World!"}
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")