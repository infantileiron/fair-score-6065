import {useState} from 'react';
import type {Workspace} from '../stores/workspace';
import {PageHeading} from '../components/common/PageHeading';
import {Notice} from '../components/common/Notice';
import {Empty} from '../components/common/Empty';
import {ComparisonTable} from '../components/ComparisonTable';
import {createComparison} from '../api/comparisons';
import {createReports} from '../api/reports';
import {downloadReport} from '../api/client';
import {useAsync} from '../hooks/useAsync';
import {date,percent} from '../utils/format';

export function Compare({data,canWrite,isAdmin,refresh}:{data:Workspace;canWrite:boolean;isAdmin:boolean;refresh:()=>Promise<void>}){
 const [baseline,setBaseline]=useState('');
 const [candidate,setCandidate]=useState('');
 const task=useAsync();
 const completed=data.runs.filter(r=>r.status==='completed');
 const policyOf=(runId:string)=>data.policies.find(p=>p.id===data.runs.find(r=>r.id===runId)?.policy_id);
 const datasetOf=(runId:string)=>data.datasets.find(d=>d.id===policyOf(runId)?.dataset_id);
 const label=(runId:string)=>{
  const run=data.runs.find(r=>r.id===runId);const p=policyOf(runId);const d=datasetOf(runId);
  return run&&p?`${p.name} · 阈值${run.result.threshold} · ${d?.name??'未知卷宗'}`:'';
 };
 const sameDataset=baseline&&candidate&&datasetOf(baseline)?.id===datasetOf(candidate)?.id;
 const archived=(comparisonId:string)=>data.reports.find(r=>r.comparison_id===comparisonId);
 return <>
  <PageHeading label="05 / SCHEME COMPARISON" title="两份分数线，逐组配对比较。">
   双侧精确 McNemar 检验只看判定翻转的候选，Holm 法校正多组比较。<br/>样本内容不同将拒绝对照；仅排列不同仍可比较。
  </PageHeading>
  {canWrite&&<section className="paper">
   <h2>新建方案对照</h2>
   <form className="policy-form" onSubmit={e=>{e.preventDefault();task.execute(async()=>{
    await createComparison({baseline_run_id:baseline,candidate_run_id:candidate});
    setBaseline('');setCandidate('');await refresh();
   })}}>
    <label>基准方案（已完成计算）
     <select aria-label="基准方案" required value={baseline} onChange={e=>setBaseline(e.target.value)}>
      <option value="" disabled>请选择基准计算记录</option>
      {completed.map(r=><option key={r.id} value={r.id} disabled={r.id===candidate}>{label(r.id)}</option>)}
     </select>
    </label>
    <label>待审方案（已完成计算）
     <select aria-label="待审方案" required value={candidate} onChange={e=>setCandidate(e.target.value)}>
      <option value="" disabled>请选择待审计算记录</option>
      {completed.map(r=><option key={r.id} value={r.id} disabled={r.id===baseline}>{label(r.id)}</option>)}
     </select>
    </label>
    <p className="wide compare-hint">
     {baseline&&candidate?(baseline===candidate?'基准与待审不能是同一条计算记录。'
      :sameDataset?'同一卷宗：将按候选ID逐一对齐，排列顺序不影响结果。'
      :<b>两份方案来自不同卷宗，提交后后端会校验样本内容，不一致将拒绝对照。</b>)
      :'请分别选择基准与待审的已完成计算记录。'}
    </p>
    <button disabled={task.busy||!baseline||!candidate||baseline===candidate}>计算配对检验</button>
   </form>
  </section>}
  {task.error&&<Notice error>{task.error}</Notice>}
  <section className="paper">
   <h2>对照记录</h2>
   {data.comparisons.length===0?<Empty>先运行两份分数线方案，再在此处建立方案对照。</Empty>:
    data.comparisons.map(c=>{
     const r=c.result;const rep=archived(c.id);
     return <article className="comparison-record" key={c.id}>
      <div className="comparison-head">
       <div>
        <span className="eyebrow">{r.test} · {r.correction} 校正 · α={r.alpha}</span>
        <h3>{r.baseline.policy_name}（基准） ↔ {r.candidate.policy_name}（待审）</h3>
        <small>{c.created_by} · {date(c.created_at)} · 配对 n={r.totals.n}</small>
       </div>
       <div className="comparison-actions">
        {isAdmin&&!rep&&<button className="secondary" disabled={task.busy} onClick={()=>task.execute(async()=>{
         await createReports({comparison_id:c.id,title:'方案对照归档 · '+c.created_at.slice(0,10)});await refresh();
        })}>批准并归档</button>}
        {rep&&<button className="secondary" onClick={()=>task.execute(()=>downloadReport(rep.id))}>下载归档CSV　↓</button>}
       </div>
      </div>
      <div className="scheme-pair">
       <div><small>基准方案</small><b>{r.baseline.policy_name}</b><small>阈值 {r.baseline.threshold} · 准确率 {percent(r.totals.baseline_accuracy)}</small><small>卷宗 {r.baseline.dataset_name}</small><small className="checksum">校验码 {r.baseline.checksum.slice(0,16)}</small></div>
       <div><small>待审方案</small><b>{r.candidate.policy_name}</b><small>阈值 {r.candidate.threshold} · 准确率 {percent(r.totals.candidate_accuracy)}</small><small>卷宗 {r.candidate.dataset_name}</small><small className="checksum">校验码 {r.candidate.checksum.slice(0,16)}</small></div>
      </div>
      <ComparisonTable result={r}/>
      <div className="evidence-note comparison-warnings">
       {r.warnings.map((s,i)=><p key={s}><b>0{i+1}</b>{s}</p>)}
      </div>
     </article>;
    })}
  </section>
 </>;
}
