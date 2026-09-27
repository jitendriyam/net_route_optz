from fastapi import APIRouter, Depends, Response

from app.db.session import get_session
from app.schemas.test_data import TestDataResponse
from app.services.test_data import TestDataService

router = APIRouter(prefix="/test-data", tags=["test-data"])


@router.post("", response_model=TestDataResponse, status_code=201)
def create_test_data(session=Depends(get_session)) -> TestDataResponse:
    """Create the deterministic sample network for manual API testing."""
    return TestDataService(session).create()


@router.delete("", status_code=204)
def delete_test_data(session=Depends(get_session)) -> Response:
    """Delete the deterministic sample network and its cascaded edges."""
    TestDataService(session).delete()
    return Response(status_code=204)
