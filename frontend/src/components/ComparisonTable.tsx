import type {ComparisonResult} from '../types/domain';
import {percent,pvalue} from '../utils/format';

export function ComparisonTable({result}:{result:ComparisonResult}){
 const t=result.totals;
 return <div className="table-scroll"><table>
  <thead><tr>
   <th>复核组 / 配对样本</th><th>都判对</th><th>仅基准判对</th><th>仅待审判对</th><th>都判错</th>
   <th>不一致判定</th><th>精确 p 值（双侧）</th><th>Holm 校正 p</th><th>校正后显著（α={result.alpha}）</th>
  </tr></thead>
  <tbody>
   {result.groups.map(g=><tr key={g.group}>
    <td><b>{g.group}</b><small>n = {g.n}</small></td>
    <td>{g.both_right}</td>
    <td>{g.baseline_only_right}</td>
    <td>{g.candidate_only_right}</td>
    <td>{g.both_wrong}</td>
    <td>{g.discordant}{g.discordant===0&&<small>无不一致，保留有效结果</small>}</td>
    <td>{pvalue(g.p_value)}</td>
    <td>{pvalue(g.p_holm)}</td>
    <td><span className={'status '+(g.significant_holm?'failed':'')}>{g.significant_holm?'显著':'不显著'}</span></td>
   </tr>)}
   <tr className="total-row">
    <td><b>全样本合计</b><small>n = {t.n}</small></td>
    <td><b>{t.both_right}</b></td>
    <td><b>{t.baseline_only_right}</b></td>
    <td><b>{t.candidate_only_right}</b></td>
    <td><b>{t.both_wrong}</b></td>
    <td><b>{t.baseline_only_right+t.candidate_only_right}</b></td>
    <td colSpan={3}><small>基准准确率 {percent(t.baseline_accuracy)} ｜ 待审准确率 {percent(t.candidate_accuracy)}</small></td>
   </tr>
  </tbody>
 </table></div>;
}
