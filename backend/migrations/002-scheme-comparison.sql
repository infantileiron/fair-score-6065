-- 方案对照（双份分数线方案的精确配对检验）结构升级。
-- 生产发布前按 001-initial.sql 的约定评审；以下语句面向 PostgreSQL 16，均可重复执行。
CREATE TABLE IF NOT EXISTS scheme_comparisons (
 id VARCHAR PRIMARY KEY,
 baseline_run_id VARCHAR REFERENCES audit_runs(id),
 candidate_run_id VARCHAR REFERENCES audit_runs(id),
 result JSON DEFAULT '{}',
 created_by VARCHAR,
 created_at VARCHAR
);
ALTER TABLE audit_reports ADD COLUMN IF NOT EXISTS comparison_id VARCHAR;
CREATE UNIQUE INDEX IF NOT EXISTS uq_audit_reports_comparison ON audit_reports(comparison_id);
-- 旧归档的 run_id 保持非空语义由应用侧单方案分支保证；新归档两类目标恰好填一项。
