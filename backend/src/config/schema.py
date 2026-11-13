from sqlalchemy import inspect,text
from src.models.comparison import SchemeComparison

# 演示环境的幂等结构升级：生产环境以 migrations 下评审过的 ALTER 脚本为准。
# 旧库升级后保留既有单方案数据与复核流程，仅补齐方案对照所需的表与列。
def ensure_schema(engine):
 insp=inspect(engine)
 if "scheme_comparisons" not in insp.get_table_names():
  SchemeComparison.__table__.create(engine)
 if "audit_reports" in insp.get_table_names():
  cols={c["name"] for c in insp.get_columns("audit_reports")}
  covered=any("comparison_id" in uc["column_names"] for uc in insp.get_unique_constraints("audit_reports")) or \
   any(i["unique"] and "comparison_id" in i["column_names"] for i in insp.get_indexes("audit_reports"))
  with engine.begin() as conn:
   if "comparison_id" not in cols:
    conn.execute(text("ALTER TABLE audit_reports ADD COLUMN comparison_id VARCHAR(32)"))
   if not covered:
    conn.execute(text("CREATE UNIQUE INDEX uq_audit_reports_comparison ON audit_reports(comparison_id)"))
