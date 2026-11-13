from sqlalchemy import String,JSON,ForeignKey
from sqlalchemy.orm import Mapped,mapped_column
from src.config.database import Base
class SchemeComparison(Base):
 __tablename__="scheme_comparisons"
 id:Mapped[str]=mapped_column(String,primary_key=True)
 baseline_run_id:Mapped[str]=mapped_column(ForeignKey("audit_runs.id"))
 candidate_run_id:Mapped[str]=mapped_column(ForeignKey("audit_runs.id"))
 result:Mapped[dict]=mapped_column(JSON,default=dict)
 created_by:Mapped[str]=mapped_column(String)
 created_at:Mapped[str]=mapped_column(String)
