import math

# 成对判定统计：双侧精确 McNemar 检验（二项精确法）与 Holm 多重比较校正。
# 全部使用整数计数与对数空间运算，满额 5000 样本也不会触发浮点溢出。

def _log_binom_pmf(k,n,p=0.5):
 # 二项分布质量函数的对数值：log C(n,k) + k log p + (n-k) log(1-p)
 return math.lgamma(n+1)-math.lgamma(k+1)-math.lgamma(n-k+1)+k*math.log(p)+(n-k)*math.log(1-p)

def mcnemar_exact(b,c):
 # b: 仅基准判对（基准正确、待审错误）；c: 仅待审判对（待审正确、基准错误）
 # 不一致判定数 n=b+c；在“两方案无差异”的零假设下服从 Binomial(n, 0.5)。
 # 双侧 p 值为所有概率不超过观测点概率的取值之和。无不一致判定时保留有效结果 p=1.0。
 n=b+c
 if n==0:return 1.0
 if b==c:return 1.0  # 观测点即零假设下的众数，所有取值概率均不超过它，双侧 p 值恰为 1
 observed=_log_binom_pmf(min(b,c),n)
 log_terms=[_log_binom_pmf(k,n) for k in range(n+1) if _log_binom_pmf(k,n)<=observed+1e-12]
 return min(1.0,math.fsum(math.exp(t) for t in log_terms))

def holm(raw_p,alpha=0.05):
 # Holm-Bonferroni 逐步校正，返回与输入同序的校正 p 值及 alpha 下显著性。
 m=len(raw_p)
 if m==0:return [],[]
 order=sorted(range(m),key=lambda i:raw_p[i])
 adjusted=[0.0]*m
 running=0.0
 for rank,i in enumerate(order):
  running=min(1.0,max(running,(m-rank)*raw_p[i]))
  adjusted[i]=running
 return adjusted,[p<=alpha for p in adjusted]
