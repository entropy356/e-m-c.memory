# 有价值资料收集

这里收集可能对 e-m-c 的研究、实验、实现及项目组织有价值的资料，包括论文、代码仓库、技术文档和其他线索；不局限于当前研究方向。

- 尽可能保留原始链接，并简述资料内容及可能的参考价值。
- 允许暂存未经充分核实的线索，存在不确定性时明确标注。收录不代表认可其论断或决定采用其方案。
- 本文件是资料收集草稿，不作为项目正式结论、架构决策或实现依赖。经过核实和整理的成果应独立写入正式文档。

## 近期关注的 Agent 基础设施与工作流

### DeepSeek Harness：可组合的 Agent Harness

- [代码仓库](https://github.com/deepseek-ai/deepseek-harness)
- [架构文档](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/architecture.md)
- [Cordis：其使用的组合式插件框架](https://github.com/cordiverse/cordis)

可参考其模块组合、生命周期及宿主与模块的边界设计。

### dsh-superagent-prototype：仓库开发 Agent 研究原型

- [代码仓库](https://github.com/deepseek-ai/dsh-superagent-prototype)

基于 DeepSeek Harness 的单仓库主动式编码 Agent 原型，可参考其任务授权、隔离执行、GitHub 交互与减少人工注意力负担的工作流。仓库明确标注为研究原型，并非生产就绪的软件。

## 情绪、单胺与状态空间

### Lövheim（2012）：情绪立方

**A new three-dimensional model for emotions and monoamine neurotransmitters**

Hugo Lövheim. *Medical Hypotheses*, 78(2), 341–348.

- [DOI / 出版社入口](https://doi.org/10.1016/j.mehy.2011.11.016)
- [PubMed 摘要与书目信息](https://pubmed.ncbi.nlm.nih.gov/22153577/)

以血清素、多巴胺、去甲肾上腺素为三个正交轴，将按 Tomkins 命名的八种基本情绪放在立方体顶点。可参考其状态空间的构造。正式卷期为 2012 年，在线发表时间为 2011 年。

### Gu 等（2018）：情绪维度与认知过程

**The Neural Mechanism Underlying Cognitive and Emotional Processes in Creativity**

Simeng Gu, Mengdan Gao, Yaoyao Yan, Fushun Wang, Yi-yuan Tang, Jason H. Huang. *Frontiers in Psychology*, 9:1924.

- [DOI / 开放全文](https://doi.org/10.3389/fpsyg.2018.01924)

讨论基本情绪、核心感受、神经调质与创造性认知。下列 2020 年社论中的“三原色”示意图改编自此文。

### Gu 等（2019）：基本情绪与行为

**A Model for Basic Emotions Using Observations of Behavior in Drosophila**

Simeng Gu, Fushun Wang, Nitesh P. Patel, James A. Bourgeois, Jason H. Huang. *Frontiers in Psychology*, 10:781.

- [DOI / 开放全文](https://doi.org/10.3389/fpsyg.2019.00781)
- [PMC 全文](https://pmc.ncbi.nlm.nih.gov/articles/PMC6491740/)

从果蝇行为讨论核心感受、单胺与情绪流动（emotion flow），包括压力、奖赏、惩罚与行为的联系。

### Gu 等（2019）：连续维度与离散情绪

**An Integrative Way for Studying Neural Basis of Basic Emotions With fMRI**

Simeng Gu, Fushun Wang, Chenbo Cao, Enquan Wu, Yi-yuan Tang, Jason H. Huang. *Frontiers in Neuroscience*, 13:628.

- [DOI / 开放全文](https://doi.org/10.3389/fnins.2019.00628)

讨论如何整合基本情绪与维度模型，以及刺激的安全价值、享乐价值和情绪位置之间的关系。

### Wang 等（2020）：情绪三原色资料入口

**Editorial: Neurotransmitters and Emotions**

Fushun Wang, Jiongjiong Yang, Fang Pan, Roger C. Ho, Jason H. Huang. *Frontiers in Psychology*, 11:21.

- [DOI / 开放全文](https://doi.org/10.3389/fpsyg.2020.00021)
- [PMC 全文](https://pmc.ncbi.nlm.nih.gov/articles/PMC7025515/)

介绍单胺基础情绪模型（“three primary color model”），并提供前序研究的引用入口。文章类型为专题社论；其引用包括 Lövheim（2012）、Gu 等（2018）以及上列 2019 年 fMRI 综述。

## 情绪与计算架构

### 三单胺系统的机器模拟（2018）

**Bio-plausible simulation of three monoamine systems to replicate emotional phenomena in a machine**

*Procedia Computer Science*, 145, 300–305.

- [DOI / 出版社入口](https://doi.org/10.1016/j.procs.2018.11.075)
- [机构存档：摘要与参考文献，非完整论文](https://dspace.kpfu.ru/xmlui/bitstream/net/149253/-1/SCOPUS-2018-145-SID85059468794-a1.pdf)

使用 NEST 模拟多巴胺、血清素、去甲肾上腺素子系统，并把情绪模型连接到计算过程和资源调节。可用于查找“持续内部状态如何调节计算资源、决策与调度”的实现思路。其参考文献还包含 NEUCOGAR 神经调质认知架构相关研究。

## 记忆的提取、保留与时间尺度

### Bjork 与 Bjork（1992）：New Theory of Disuse

**A New Theory of Disuse and an Old Theory of Stimulus Fluctuation**

- [UCLA Bjork Lab：原文 PDF](https://bjorklab.psych.ucla.edu/wp-content/uploads/sites/13/2016/07/RBjork_EBjork_1992.pdf)
- [Bjork Lab：理论与研究简介](https://bjorklab.psych.ucla.edu/research/)

区分 `retrieval strength`（当前可提取性）与 `storage strength`（学习/储存强度），讨论提取、干扰与后续学习的关系。为区分记忆的存储强度和提取强度提供理论参照。

### Bjork 与 Bjork（2011）：Desirable Difficulties

**Making Things Hard on Yourself, But in a Good Way: Creating Desirable Difficulties to Enhance Learning**

- [UCLA Bjork Lab：章节原文 PDF](https://bjorklab.psych.ucla.edu/wp-content/uploads/sites/13/2016/11/Making-Things-Hard-on-Yourself-but-in-a-Good-Way-20111.pdf)

讨论提取间隔、学习难度与长期保持之间的关系。

### de Snoo 与 Frankland（2025）：跨时间尺度的遗忘

**Neurobiological mechanisms of forgetting across timescales**

Mitchell L. de Snoo, Paul W. Frankland. *Current Opinion in Neurobiology*, 90:102972.

- [DOI / 期刊入口](https://doi.org/10.1016/j.conb.2025.102972)
- [PubMed 摘要与书目信息](https://pubmed.ncbi.nlm.nih.gov/39892316/)

综述不同时间尺度上使记忆痕迹更难访问的机制，提示“不可提取”不必等同于“痕迹已删除”。可用于理解记忆可访问性与跨时间尺度变化之间的关系。

## 实验支撑与基础设施参考

### e-m-c.runtime：Runtime 基础设施原型

- [代码仓库与运行说明](https://github.com/entropy356/e-m-c.runtime)

当前实现长期记忆聊天、状态持久化、Chat/Embedding 接入及状态查看能力。目标是通过模块化重构形成供不同实验复用的基础设施。

### THU-CoAI ECM：情绪条件化对话生成

**Emotional Chatting Machine: Emotional Conversation Generation with Internal and External Memory**

- [论文（arXiv）](https://arxiv.org/abs/1704.01074)
- [实现（thu-coai/ecm）](https://github.com/thu-coai/ecm)

使用情绪标签和内部/外部记忆机制生成带有情绪色彩的回应，可作为情绪影响对话生成的相关实现。

## 来源线索

- [B 站视频](https://www.bilibili.com/video/BV1KDdUYbEB2/)（[短链接](https://b23.tv/MgVJcSC)）：上述资料检索的线索来源。
- 视频所述“2012 年情绪立方”与 Lövheim（2012）对应。
- 视频所述“2020 年中国团队的情绪三原色”与 Wang 等（2020）社论高度吻合，尚未通过视频参考文献列表确认。
- 其他条目来自论文引用追踪或相关研究检索，不表示视频直接引用了它们。
