from pydantic import BaseModel
class ComparisonInput(BaseModel):
 baseline_run_id:str
 candidate_run_id:str
