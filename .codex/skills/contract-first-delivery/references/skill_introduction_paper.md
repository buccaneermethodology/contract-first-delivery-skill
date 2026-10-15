# 先写清“什么算完成”，再让 AI 写代码：`contract-first-delivery` 如何帮助降低 AI 编程中的返工与失控风险

## 摘要

AI 编程最危险的时刻，往往不是它不会写代码，而是它写得太快 —— 快过了需求、边界和验收标准被真正说清楚的速度。

当目标、非目标、输入输出、失败语义和验收标准还没有说清楚时，AI 很容易自行补全缺失信息：选择一个看似合理的架构、扩大接口范围、生成一批结构完整的代码，最后却发现实现方向与真实需求并不一致。

`contract-first-delivery` 解决的正是这个问题：

> 在实现开始前，
> 先把最昂贵、最难返工的边界冻结下来，
> 再把模糊需求转换成可执行、可失败、可验证的合同，
> 让 AI 在合同允许的范围内高速推进，并让越界行为更容易被识别和阻断。

它不是“多写一些设计文档”，而是把开发顺序从 **Code-First**：

> 模糊需求 → 大量代码 → 测试补救 → 反复返工

改造成 **Contract-First**：

> 完整目标与 Must-have Ledger → Constitution → Module Contract → Schema/Example/Golden → Acceptance Policy → 全量切片计划 → 最小 Ready Slice → Ledger 复核与继续执行 → Session Closeout

本文基于 `contract-first-delivery-skill` v2.0.0，解析它如何在编码前冻结完整完成边界，再通过有界切片推进实现。

## 这个 Skill 具体做什么

`contract-first-delivery` skill 在 v2.0.0 中定义了十步工作流：

1. **冻结完整任务与 Session 完成边界**  
    在 `constitution.json` 中保存原始目标和全部 must-haves，并定义非目标、用户、系统边界、兼容目标、发布阶段、质量门禁、测试策略、完整 completion rule、continuation rule、allowed termination conditions、Scope Delta policy 和变更控制。
    
2. **定义模块合同**  
    在 `module-contract.json` 中明确输入、输出、依赖、状态变化、错误、约束、验证行为、非目标和下游消费者。
    
3. **先定义结构化契约**  
    如果输出是结构化 artifact，先建立 `artifact.schema.json`，再实现 producer。
    
4. **建立正常示例**  
    添加至少一个代表性的 `example.valid.json`，并实际验证它符合 schema。
    
5. **建立人工 Oracle**  
    对语义或高风险输出建立人工编写、带来源和审阅记录的 `golden.json`；不得让 candidate 生成自己的 oracle。
    
6. **定义验收策略和证据上限**  
    在 `acceptance-policy.json` 中分离 blocking 与 advisory checks，并明确当前证据最多支持什么声明。
    
7. **合同包确定性验证**  
    运行 packaged deterministic validator；所有 blocking findings 关闭后才允许进入实现。通过只证明 validator 实际检查的结构和关系成立，不证明业务语义、生产成熟或外部批准。
    
8. **建立覆盖完整 Ledger 的有序切片计划**  
    将每个原始 must-have 映射到一个或多个 implementation slices，明确依赖、readiness 和可观察 outcome，再识别最小安全的 first slice。所有切片合起来必须覆盖完整 ledger。

9. **逐切片实现、复核并继续**  
    每个切片完成后回到原始 must-have ledger 复核。只要 completion rule 尚未满足，且没有必须由人类决定的事项或已验证 blocker，就继续执行下一个 ready slice。

10. **分别关闭 Slice 与 Session**  
    closeout 必须分别报告 slice verdict 与 Session terminal verdict，同时列出 remaining must-haves、Scope Delta、next slice 和 human-decision state。

这其实定义了一条 Contract Evidence Chain，各个合同面分别回答：

- 为什么做、什么绝对不做、完整完成条件是什么？—— Constitution + Session Completion Contract
- 模块对外承诺什么行为？—— Module Contract
- 输出结构必须长什么样？—— Schema
- 至少一个合法实例是什么？—— Valid Example
- 语义上什么才算对？—— Manual Golden
- 哪些失败必须阻断、哪些只是建议？—— Acceptance Policy
- 这些结构与关系是否满足预设规则？—— Deterministic Validator
- 所有原始 must-haves 如何被有序实现？—— Implementation Slice Plan
- 当前切片通过后，Session 是否真的终止？—— Ledger Re-evaluation + Closeout
- 现有证据最多支持什么结论？—— Claim Ceiling

它最重要的决策规则很简单：

> 如果实现细节仍然模糊，不要让模型宽泛地开始编码；先强化那个能够让下一次编码变得有界、可测试的最小合同。但强化更小的合同面，不能重新定义原始完成边界。

完整文件合同、finding codes、迁移规则和维护边界见随 Skill 发布的 `REFERENCE.md`。

注意：上面描述的“**进入最小安全实现切片**”只是实现入口。`slice_pass` 不等于这次任务全部完成，也不自动推出 `session_terminal=true`。

每个切片完成后，Agent 必须报告：

- `slice_verdict`
- `session_terminal`
- `remaining_must_haves`
- `scope_delta`
- `next_slice`
- `human_decision_required`

项目还可以增加 `original_must_haves_covered`、`next_slice_ready` 等扩展字段，但不能省略以上六项 v2 closeout 字段。

只有以下情况可以停止：

1. 原始 Session completion rule 已满足；
2. 存在需要明确人类决定的事项；
3. 存在经过验证的 blocker。

删除、弱化、延后或转移原始 must-have 都属于 Scope Delta。Scope Delta 获得人类批准后，应先更新完成边界，再重新判断 completion rule，而不能把“已批准变更”直接当作独立的停止理由。普通的未完成工作也不是 termination condition；否则必须继续进入下一个 ready slice。

### v2.0.0 的破坏性变化

v2.0.0 的关键变化不是简单增加几个字段，而是将完成纪律变成 fail-closed 合同：首个安全切片只能决定从哪里开始，不能重新定义整个任务在哪里结束。

已有 v1 合同包迁移到 v2 时必须增加：

- `constitution.json.session_completion`：保存原始 must-have ledger、completion/continuation rules、allowed termination conditions 和 Scope Delta policy；
- `module-contract.json.implementation_slices`：以有序切片覆盖每一个原始 must-have；
- `acceptance-policy.json.required_closeout_fields`：强制区分 slice verdict 与 Session terminal verdict。

缺失或不一致时，v2 validator 会 fail closed，并分别报告 `CFD-MISSING-SESSION-COMPLETION` 或 `CFD-INCOMPLETE-SLICE-PLAN`。六个文件名和 v1 finding code 的既有含义保持兼容，但 v1 合同包不能在未迁移时直接宣称通过 v2 校验。

## 它带来的核心价值

### 1. 降低 AI 静默替产品和架构做决定的风险

模糊需求中一定存在空白。如果没有合同，AI 会用自己的默认判断填空。

Constitution 和 non-goals 会明确告诉 AI：

- 当前要解决什么；
- 哪些能力明确不做；
- 什么必须保持兼容；
- 哪些细节可以在实现阶段演化；
- 哪些边界变化必须重新审批。

比如，我在开发 Semx 时，首先就在 `Implementation Constitution V1` 中冻结了几个关键决策：

- 正式实现线面向 V2 contract，不把旧 demo runtime 顺势扩张成正式主线；
- CLI 必须分阶段落地；
- runtime depth 不能落后于命令面宽度。

这不是抽象的架构口号，而是直接阻止了一条成本很高的错误路线。

### 2. 把“看起来不错”变成“能通过或拒绝”

Schema 只能证明结构合法，不能自动证明：

- 引用是否完整；
- lineage 是否可信；
- 错误是否被掩盖；
- 输出是否越过语义边界；
- candidate 是否有资格进入下游。

`contract-first-delivery` 要求**定义 blocking 与 advisory 的区别**。参考实现还通过 fail-closed 负向回归证明已命名的危险形状会被稳定拒绝；具体项目则应按风险补充自己的 negative fixtures。这样验收系统不仅会说“这个例子通过了”，还会检查已声明的危险输入是否被稳定拒绝。

### 3. 把返工提前到最便宜的阶段

修改一张合同表、一个 schema 或一个 negative fixture，通常比推翻一批已经互相依赖的实现便宜得多。

Skill 的价值不是消除所有变化，而是把变化前移：**先在合同层发现矛盾，再允许 Builder 写代码**。

### 4. 让多 Agent 协作不再依赖“大家理解得差不多”

合同可以成为共同交接面：

- Design Agent 冻结边界；
- Builder 按合同实现；
- Validation Agent 从相同输入独立复算；
- 后续 Agent 可以从 schema、fixtures 和验收命令恢复上下文。

这有助于降低长任务中不同角色悄悄携带不同定义的风险。

### 5. 建立诚实的完成声明

合同优先开发会强迫团队区分：

- schema valid；
- tests passed；
- candidate accepted；
- independently validated；
- publicly released；
- production ready。

## 案例：用 Contract First 建立 P01 Evidence 验收门

下面使用 Semx 项目历史上的 `SP-002 / S-051` 作为案例。它展示的不是“先写一份漂亮设计”，而是如何把“可信的 P01 evidence”变成真正能执行和拒绝的合同。

### 第一步：向 Codex 下达完整提示

可直接使用下面这段提示：

```text
请使用 $contract-first-delivery，为 Semx 的 P01 evidence 建立第一版可执行验收门。

背景：
- 当前已经有 semx_evidence_v1 schema 和正常示例；
- 但 schema 通过还不能证明 evidence 可以安全进入 P02；
- 需要建立一个 maintained、可回归、能拒绝危险 candidate 的验收入口。

请按以下顺序执行：

1. 先检查现有 Implementation Constitution、P01 phase contract、
   schema、examples 和 contract-test 入口。
2. 保存原始目标和完整 must-have ledger，冻结本轮非目标、输入、输出、
   错误行为、completion/continuation rules、termination conditions 和
   Scope Delta policy。
3. 定义 blocking/advisory 规则和 claim ceiling，明确第一版能从
   evidence 自身确定性判断什么，不能判断什么。
4. 不修改 evidence schema，除非发现无法绕开的合同歧义。
5. 增加至少一个正常示例和一个 schema-valid 但
   acceptance-invalid 的负例。
6. 建立覆盖全部 must-haves 的有序 implementation slice plan，
   再实现第一个 ready 的最小 CLI/validator 代码切片。
7. 运行正向、负向、兼容性和既有回归门禁；每个切片结束后回到
   原始 ledger 复核，并在允许时继续下一个 ready slice。
8. 最后分别报告 slice_verdict、session_terminal、
   remaining_must_haves、scope_delta、next_slice 和
   human_decision_required，并说明哪些内容仍未证明。

不要把 schema valid 表述为 semantic correct，
也不要把第一版 evidence-only gate 表述为完整 manifest-aware acceptance。
```

### 第二步：确认已有 Constitution

项目已经存在 `Implementation Constitution V1`，因此本任务不需要重新发明项目边界。

它对本例给出了三项直接约束：

- acceptance harness 必须先于大规模 runtime 扩张；
- 先交付 machine-checkable contract，再扩大实现宽度；
- 当前 legacy `build` 路径仍是 transitional，不能借本任务升级为正式主线。

这一步防止 Coding Agent 从“增加 P01 验收门”膨胀成“重构整个早期 runtime”。

S-051 自身的完整完成边界：本 Session 的目标是建立“第一版 evidence-self-contained P01 acceptance gate”，而不是解决完整 manifest-aware acceptance。

### 第三步：冻结模块合同

把当时的落地内容整理成可复用合同如下：

|合同项|冻结内容|
|---|---|
|Purpose|判断一个 `01_evidence.json` 是否足以进入 maintained P02 路径|
|Input|一个符合 `semx_evidence_v1` 结构的 evidence artifact|
|Output|成功或失败退出码，以及可定位的诊断|
|Blocking|schema 失败、重复稳定 ID、悬空引用、error diagnostic、明显命名边界泄漏、test-only scope 泄漏|
|Advisory|warning/info diagnostics，本身不阻断|
|State change|验收本身不修改 candidate，不生成 canonical truth|
|Non-goal|第一版不根据 `manifest_ref` 猜测完整 manifest 内容，不做精确 source-scope replay|
|Downstream consumer|maintained P02 runtime 与相应回归流程|
|Claim ceiling|只证明 evidence 通过第一版确定性验收，不证明语义完整、生产正确或 manifest 精确一致|

本 Session 的 must-have ledger 为：

|Must-have|要求|验收证据|
|---|---|---|
|MH-001|对 evidence 自身可观察事实执行确定性验收，并拒绝已命名的边界违规|正常、degraded、branching 与 boundary violation fixtures|
|MH-002|分离 blocking 与 advisory，并冻结 claim ceiling|acceptance policy 及诊断断言|
|MH-003|提供 maintained CLI 入口和确定性退出行为|`semx contract-test --p01-acceptance`|
|MH-004|建立可重复的正向、负向和兼容性回归|maintained regression 与既有门禁结果|

这里最关键的决策是：第一版只检查 evidence 内部可确定性观察到的事实。

### 第四步：确定 Schema、Example 和 Oracle 策略

本轮不新增 schema，因为已有 `semx_evidence_v1` 足以承载第一版验收。

准备的证据包括：

- 正常示例：`01_evidence.example.json`；
- degraded warning 示例：允许通过，但保留 advisory diagnostics；
- branching 示例：验证另一种正常结构；
- schema-valid、acceptance-invalid 负例。

本例没有创建新的“语义 golden”。原因是本轮判断目标是可确定性计算的结构、引用、诊断和边界规则，不要求模型判断开放语义。已有 maintained positive fixtures 加人工设计的 negative fixture，就是这一切片所需的 oracle surface。

如果任务改成“判断 evidence 是否完整表达了代码的真实业务意义”，则必须另行引入人工 golden/oracle，不能继续只靠 schema 和规则。

### 第五步：先写 Acceptance Policy

历史任务将验收规则落到 `p01_evidence_acceptance_policy.md`，明确规定：

- 哪些问题立即阻断；
- warning/info 为什么只作 advisory；
- 第一版能证明什么；
- 第一版不能证明什么；
- candidate-only 与 manifest-aware 模式分别如何调用。

这一步把“可信 evidence”从一句口号变成了 Builder、Validation 和下游消费者可以共同引用的判断标准。

### 第六步：建立完整切片计划，再实现最小安全切片

在实现前，先把全部 must-haves 映射到有序切片，而不是只描述第一个切片：

|Slice|覆盖|依赖|Readiness|可观察结果|
|---|---|---|---|---|
|SLICE-1|MH-001、MH-002|无|ready|冻结 evidence-self-contained 规则、fixtures 和 claim ceiling|
|SLICE-2|MH-001、MH-003|SLICE-1|ready_after_dependencies|落地 validator helpers、CLI 参数和确定性退出行为|
|SLICE-3|MH-004|SLICE-2|ready_after_dependencies|正负回归与既有兼容性门禁通过，并生成 closeout 证据|

合同冻结后，Builder 没有新造一套独立工具，而是在现有 `semx contract-test` 上增加：

```text
--p01-acceptance
```

最小实现包括：

- validator 中的 P01 acceptance helpers；
- CLI 参数和退出行为；
- schema-valid 负例；
- acceptance policy；
- maintained regression。

这体现了 contract-first 的另一个价值：合同不仅限制功能范围，也帮助团队发现最小的集成位置。

### 第七步：建立可重复的正负回归

历史任务建立了 `p01_evidence_acceptance_regression.py`，至少覆盖：

|Case|预期|
|---|---|
|正常 TBC evidence|退出 0|
|带 warning 的 degraded evidence|退出 0，并保留指定 diagnostic|
|branching evidence|退出 0|
|boundary violation evidence|退出 1|

核心命令为：

```bash
python3 -m semx.cli contract-test --p01-acceptance
```

验证单个 candidate：

```bash
python3 -m semx.cli contract-test \
  --p01-acceptance \
  --candidate-only \
  --evidence examples/artifacts/01_evidence.example.json
```

运行 maintained regression：

```bash
python3 tests/contract/p01_evidence_acceptance_regression.py
```

这样，可重复的正负回归门禁就建立起来了：P01 门禁、既有 P02/M0.5 回归、KB render 和 `git diff --check`。

### 第八步：分别关闭当前切片与 Session

S-051 可以声明：

> 第一版 evidence-self-contained P01 acceptance gate 已落地，正负例和回归能够稳定区分允许进入下游的 candidate 与明确的边界违规。

但不能声明：

- 完整 P01 trust 问题已全部解决；
- manifest scope 已精确重放；
- schema valid 等于语义正确；
- 整条 P00→P02 runtime 已完成生产化。

按上面明确冻结的 S-051 边界，closeout 至少应表达：

```text
slice_verdict: pass
session_terminal: true
remaining_must_haves: []
scope_delta: none
next_slice: none within S-051
human_decision_required: false
```

这里的 `session_terminal: true` 只成立于 S-051 的原始目标明确限定为第一版 evidence-self-contained gate，且 MH-001 至 MH-004 全部取得验收证据。它不代表完整 P01 trust、manifest-aware replay 或整条 runtime 已经完成。

稳定验收规则进入了 canonical KB；执行状态和完成记录进入 Dashboard。

## 什么时候最值得使用

以下任务尤其适合在第一行就点名 Contract-First Delivery：

- 新模块、新 CLI、新 API 或新 phase；
- JSON、YAML、协议、事件或数据库结构输出；
- LLM extraction、classification、evaluation 等语义型产物；
- 需要 golden/oracle 的生成任务；
- acceptance、promotion、approval 或 write boundary 变化；
- 多 Agent 并行实现；
- “需求看起来清楚，但一问错误行为和非目标就说不明白”的任务；
- 已经开始频繁返工，且每次返工都来自不同的人对“完成”理解不一致。

它并不是所有改动都必须套用的重型流程。对于没有持久接口、风险较低、容易回滚的小改动，可以使用轻量 inline contract；它也不能替代产品发现、安全审查、领域批准、性能测量或生产运维。

一个通用的最短提示是：

```text
请先使用 $contract-first-delivery，不要立即实现。

先检查现有 constitution 和 contract，然后冻结：
原始目标、完整 must-have ledger、非目标、输入、输出、状态变化、
错误行为、兼容边界、完整 completion rule、continuation rule、
allowed termination conditions、Scope Delta policy、schema、正负示例、
golden/oracle 责任、blocking/advisory 验收规则以及最大允许声明。

把全部 must-haves 映射到有序 implementation slices，明确每个 slice 的
依赖、readiness 和可观察 outcome，并指出最小安全的 first slice。
只有合同足以支持确定性验收后再进入实现。

每个切片完成后回到原始 ledger 复核；只要 completion rule 尚未满足，
且没有必须由人类决定的事项或已验证 blocker，就继续下一个 ready slice。
最终分别报告 slice_verdict、session_terminal、remaining_must_haves、
scope_delta、next_slice 和 human_decision_required。
```

## 结语

`contract-first-delivery` 的目标不是增加流程负担，而是拒绝在最昂贵的方向上盲目加速，把高成本返工尽量前移到合同阶段。

它把“**先想清楚再写代码**”从一句经验性建议，进一步工程化为**一组结构化合同、一个确定性 validator、一套 fail-closed findings 和一个明确的 evidence ceiling**。

它真正推广的不是“文档优先”，而是三件事：

- **让人类先决定不可返工的边界；**
- **让 AI 在清晰、有限、可测试的空间内高速实现；**
- **让“完成”由可重放证据决定，而不是由代码数量或模型自信决定。**

在 AI 能够一天生成成千上万行代码的时代，真正稀缺的已经不是代码生成能力，而是对目标、边界、语义和验收责任的控制能力。`contract-first-delivery` 就是把这种控制能力变成可复用工程流程的 Skill。

它是在 AI 具备高速实现能力之后，对**研发入口**重新做的一次工程化设计：
**先把不可由实现决定的事情冻结下来，再把可以由实现决定的事情交给 AI**。
