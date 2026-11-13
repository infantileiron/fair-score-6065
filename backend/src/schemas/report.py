from pydantic import BaseModel,Field,model_validator
class ReportInput(BaseModel):
 run_id:str|None=None
 comparison_id:str|None=None
 title:str=Field(min_length=2,max_length=120)
 @model_validator(mode="after")
 def one_target(self):
  if bool(self.run_id)==bool(self.comparison_id):
   raise ValueError("归档须指定单方案计算记录或方案对照中的恰好一项")
  return self
