import uuid,csv,io
from fastapi import HTTPException
from sqlalchemy import select
from src.models import AuditReport,GroupReview,SchemeComparison
from src.services.runs import require_completed
from src.services.comparisons import require as require_comparison
from src.utils.time import now
from src.utils.serialization import serialize

def create(db,payload,user):
 if payload.comparison_id:
  comparison=require_comparison(db,payload.comparison_id)
  if db.scalar(select(AuditReport).where(AuditReport.comparison_id==comparison.id)):
   raise HTTPException(409,"本次方案对照已归档")
  item=AuditReport(id=str(uuid.uuid4()),comparison_id=comparison.id,run_id=None,
   published_by=user["email"],created_at=now(),title=payload.title)
 else:
  require_completed(db,payload.run_id)
  reviews=list(db.scalars(select(GroupReview).where(GroupReview.run_id==payload.run_id).order_by(GroupReview.created_at.desc())))
  if not reviews or reviews[0].decision!="accepted": raise HTTPException(409,"最新复核须为接受后才能归档")
  if db.scalar(select(AuditReport).where(AuditReport.run_id==payload.run_id)): raise HTTPException(409,"本次计算已归档")
  item=AuditReport(id=str(uuid.uuid4()),run_id=payload.run_id,comparison_id=None,
   published_by=user["email"],created_at=now(),title=payload.title)
 db.add(item);db.commit();return serialize(item)

def _run_csv(run):
 buf=io.StringIO()
 buf.write("# 单方案复核归档\n")
 cols=["group","n","selected","qualified","tp","fp","fn","tn","selection_rate","tpr","fpr"]
 writer=csv.DictWriter(buf,cols,extrasaction="ignore");writer.writeheader();writer.writerows(run.result["groups"])
 return buf.getvalue()

def _comparison_csv(comparison):
 r=comparison.result
 buf=io.StringIO();meta=csv.writer(buf)
 b,c=r["baseline"],r["candidate"]
 meta.writerow(["# 方案对照归档（双侧精确 McNemar + Holm 校正）"])
 meta.writerow(["# 基准方案",b["policy_name"],"阈值",b["threshold"],"run_id",b["run_id"],"checksum",b["checksum"]])
 meta.writerow(["# 待审方案",c["policy_name"],"阈值",c["threshold"],"run_id",c["run_id"],"checksum",c["checksum"]])
 meta.writerow(["# 样本卷宗",b["dataset_name"],"配对样本数",r["totals"]["n"],"alpha",r["alpha"]])
 cols=["group","n","both_right","baseline_only_right","candidate_only_right","both_wrong",
  "discordant","p_value","p_holm","significant_holm"]
 writer=csv.DictWriter(buf,cols,extrasaction="ignore");writer.writeheader();writer.writerows(r["groups"])
 t=r["totals"]
 meta.writerow(["# 合计","n="+str(t["n"]),"都判对="+str(t["both_right"]),"仅基准判对="+str(t["baseline_only_right"]),
  "仅待审判对="+str(t["candidate_only_right"]),"都判错="+str(t["both_wrong"]),
  "基准准确率="+f"{t['baseline_accuracy']:.6f}","待审准确率="+f"{t['candidate_accuracy']:.6f}"])
 return buf.getvalue()

def export(db,id):
 report=db.get(AuditReport,id)
 if not report: raise HTTPException(404,"归档报告不存在")
 if report.comparison_id:
  body=_comparison_csv(require_comparison(db,report.comparison_id))
 else:
  body=_run_csv(require_completed(db,report.run_id))
 return "﻿"+body
