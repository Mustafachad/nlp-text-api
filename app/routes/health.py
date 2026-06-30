from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

# Response model — defines exactly what shape the JSON response will have.
# Pydantic validates that the data we return matches this before sending it.
class HealthResponse(BaseModel):
    status: str
    version: str
    service: str


@router.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """
    Returns the current status and version of the API.
    Used by load balancers and monitoring tools to confirm the service is up.
    """
    return HealthResponse(
        status="ok",
        version="1.0.0",
        service="NLP Text Analysis API",
    )
