from fastapi import APIRouter,Depends
from src.config.database import db_session
from src.controllers.auth import current_user,writer
from src.schemas.comparison import ComparisonInput
from src.services import comparisons as service
router=APIRouter(prefix="/comparisons")
@router.get("")
def listing(db=Depends(db_session),user=Depends(current_user)): return service.listing(db)
@router.post("")
def create(payload:ComparisonInput,db=Depends(db_session),user=Depends(writer)):
 return service.compare(db,payload,user)
