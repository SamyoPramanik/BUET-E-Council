from fastapi import APIRouter, status

router = APIRouter(tags=["Health"])

@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Service is healthy"}
    }
)
async def health_check():
    """
    Basic health check endpoint to verify the API is running.
    """
    return {"status": "ok"}
