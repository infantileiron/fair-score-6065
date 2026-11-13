export interface Candidate {candidate_id:string; group:string; score:number; qualified:number}
export interface Dataset {id:string;name:string;source:string;rows:Candidate[];created_at:string}
export interface Policy {id:string;name:string;dataset_id:string;threshold:number;max_gap:number;created_at:string}
export interface GroupMetric {group:string;n:number;selected:number;qualified:number;tp:number;fp:number;fn:number;tn:number;selection_rate:number;selection_ci:[number,number];tpr:number|null;fpr:number|null;small_sample:boolean}
export interface Frontier {threshold:number;accuracy:number;selection_gap:number;pareto:boolean}
export interface Result {n:number;threshold:number;groups:GroupMetric[];selection_gap:number;tpr_gap:number|null;fpr_gap:number|null;accuracy:number;max_gap:number;exceeds_gap:boolean;frontier:Frontier[];warnings:string[];checksum:string}
export interface Run {id:string;policy_id:string;status:string;result:Result;error:string;created_at:string}
export interface Review {id:string;run_id:string;note:string;decision:string;author:string;created_at:string}
export interface SchemeBrief {run_id:string;policy_id:string;policy_name:string;threshold:number;dataset_id:string;dataset_name:string;checksum:string}
export interface PairwiseGroup {group:string;n:number;both_right:number;baseline_only_right:number;candidate_only_right:number;both_wrong:number;discordant:number;p_value:number;p_holm:number;significant_holm:boolean}
export interface PairwiseTotals {n:number;both_right:number;baseline_only_right:number;candidate_only_right:number;both_wrong:number;baseline_accuracy:number;candidate_accuracy:number}
export interface ComparisonResult {baseline:SchemeBrief;candidate:SchemeBrief;eligible:boolean;alpha:number;test:string;correction:string;groups:PairwiseGroup[];totals:PairwiseTotals;warnings:string[]}
export interface Comparison {id:string;baseline_run_id:string;candidate_run_id:string;result:ComparisonResult;created_by:string;created_at:string}
export interface Report {id:string;run_id:string|null;comparison_id:string|null;title:string;published_by:string;created_at:string}
export interface Audit {id:string;actor:string;action:string;status:number;created_at:string}
export interface User {email:string;role:string}
