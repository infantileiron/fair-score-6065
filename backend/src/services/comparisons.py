import uuid
from fastapi import HTTPException
from sqlalchemy import select
from src.models import AuditRun,ScorePolicy,CandidateDataset,SchemeComparison
from src.services.stats import mcnemar_exact,holm
from src.utils.time import now
from src.utils.serialization import serialize

def _completed_run(db,run_id,role):
 run=db.get(AuditRun,run_id)
 if not run: raise HTTPException(404,f"{role}计算记录不存在")
 if run.status!="completed": raise HTTPException(409,f"{role}计算尚未完成，无法对照")
 return run

def _dataset_map(db,policy):
 dataset=db.get(CandidateDataset,policy.dataset_id)
 if not dataset: raise HTTPException(404,"计算记录对应的样本卷宗不存在")
 return {r["candidate_id"]:r for r in dataset.rows}

def _run_brief(run,policy,dataset):
 return {"run_id":run.id,"policy_id":policy.id,"policy_name":policy.name,
  "threshold":run.result["threshold"],"dataset_id":dataset.id,"dataset_name":dataset.name,
  "checksum":run.result["checksum"]}

def compare(db,payload,user):
 if payload.baseline_run_id==payload.candidate_run_id:
  raise HTTPException(400,"基准与待审须为两份不同方案的计算记录")
 baseline=_completed_run(db,payload.baseline_run_id,"基准方案")
 candidate=_completed_run(db,payload.candidate_run_id,"待审方案")
 base_policy=db.get(ScorePolicy,baseline.policy_id)
 cand_policy=db.get(ScorePolicy,candidate.policy_id)
 if not base_policy or not cand_policy: raise HTTPException(404,"方案不存在")
 base_rows=_dataset_map(db,base_policy)
 cand_rows=_dataset_map(db,cand_policy)
 # 样本内容不同拒绝对照；仅排列不同仍可比较：按候选ID对齐并逐字段核对。
 if set(base_rows)!=set(cand_rows):
  raise HTTPException(409,"两份方案的样本内容不同（候选ID集合不一致），拒绝对照")
 common_ids=sorted(base_rows)
 for cid in common_ids:
  a,b=base_rows[cid],cand_rows[cid]
  if a["group"]!=b["group"] or a["score"]!=b["score"] or a["qualified"]!=b["qualified"]:
   raise HTTPException(409,"两份方案的样本内容不同（候选字段不一致），拒绝对照")
 base_brief=_run_brief(baseline,base_policy,db.get(CandidateDataset,base_policy.dataset_id))
 cand_brief=_run_brief(candidate,cand_policy,db.get(CandidateDataset,cand_policy.dataset_id))
 groups=sorted({base_rows[cid]["group"] for cid in common_ids})
 group_results=[]
 for name in groups:
  ids=[cid for cid in common_ids if base_rows[cid]["group"]==name]
  both_right=base_only=cand_only=both_wrong=0
  for cid in ids:
   row=base_rows[cid]
   qualified=row["qualified"]==1
   base_correct=(row["score"]>=baseline.result["threshold"])==qualified
   cand_correct=(row["score"]>=candidate.result["threshold"])==qualified
   if base_correct and cand_correct: both_right+=1
   elif base_correct: base_only+=1
   elif cand_correct: cand_only+=1
   else: both_wrong+=1
  p_value=mcnemar_exact(base_only,cand_only)
  group_results.append({"group":name,"n":len(ids),"both_right":both_right,
   "baseline_only_right":base_only,"candidate_only_right":cand_only,"both_wrong":both_wrong,
   "discordant":base_only+cand_only,"p_value":p_value})
 adjusted,significant=holm([g["p_value"] for g in group_results])
 for g,adj,sig in zip(group_results,adjusted,significant):
  g["p_holm"]=adj;g["significant_holm"]=sig
 totals={"n":len(common_ids),
  "both_right":sum(g["both_right"] for g in group_results),
  "baseline_only_right":sum(g["baseline_only_right"] for g in group_results),
  "candidate_only_right":sum(g["candidate_only_right"] for g in group_results),
  "both_wrong":sum(g["both_wrong"] for g in group_results)}
 totals["baseline_accuracy"]=(totals["both_right"]+totals["baseline_only_right"])/totals["n"]
 totals["candidate_accuracy"]=(totals["both_right"]+totals["candidate_only_right"])/totals["n"]
 result={"baseline":base_brief,"candidate":cand_brief,
  "eligible":True,"alpha":0.05,
  "test":"two_sided_exact_mcnemar","correction":"holm",
  "groups":group_results,"totals":totals,
  "warnings":["双侧精确 McNemar 检验仅使用不一致判定（基准/待审判对翻转的候选）。",
   "Holm 法按复核组数对 p 值做族系校正；校正后仍不显著不等于两方案等价。",
   "样本按候选ID对齐，排列顺序不影响结果；对照仅反映回顾性判定差异，不自动产生招聘决策。"]}
 item=SchemeComparison(id=str(uuid.uuid4()),baseline_run_id=baseline.id,
  candidate_run_id=candidate.id,result=result,created_by=user["email"],created_at=now())
 db.add(item);db.commit()
 return serialize(item)

def require(db,comparison_id):
 item=db.get(SchemeComparison,comparison_id)
 if not item: raise HTTPException(404,"方案对照不存在")
 return item

def listing(db):
 return [serialize(x) for x in db.scalars(select(SchemeComparison).order_by(SchemeComparison.created_at.desc()))]
