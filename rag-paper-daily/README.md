# 📚 RAG Paper Daily

### 📅 2025-09-21
<table style='width:100%;'><colgroup><col style="width:61.8%;"><col style="width:38.2%;"></colgroup><thead><tr><th>title</th><th>abstract</th></tr></thead><tbody></tbody></table>

### 📅 2025-09-20
<table style='width:100%;'><colgroup><col style="width:61.8%;"><col style="width:38.2%;"></colgroup><thead><tr><th>title</th><th>abstract</th></tr></thead><tbody></tbody></table>

### 📅 2025-09-19
<table style='width:100%;'><colgroup><col style="width:61.8%;"><col style="width:38.2%;"></colgroup><thead><tr><th>title</th><th>abstract</th></tr></thead><tbody><tr><td><a href="http://arxiv.org/abs/2509.16198v1">RPG: A Repository Planning Graph for Unified and Scalable Codebase Generation</a></td><td><details><summary>展开</summary>Large language models excel at function- and file-level code generation, yet
generating complete repositories from scratch remains a fundamental challenge.
This process demands coherent and reliable planning across proposal- and
implementation-level stages, while natural language, due to its ambiguity and
verbosity, is ill-suited for faithfully representing complex software
structures. To address this, we introduce the Repository Planning Graph (RPG),
a persistent representation that unifies proposal- and implementation-level
planning by encoding capabilities, file structures, data flows, and functions
in one graph. RPG replaces ambiguous natural language with an explicit
blueprint, enabling long-horizon planning and scalable repository generation.
Building on RPG, we develop ZeroRepo, a graph-driven framework for repository
generation from scratch. It operates in three stages: proposal-level planning
and implementation-level refinement to construct the graph, followed by
graph-guided code generation with test validation. To evaluate this setting, we
construct RepoCraft, a benchmark of six real-world projects with 1,052 tasks.
On RepoCraft, ZeroRepo produces repositories averaging nearly 36K LOC, roughly
3.9$\times$ the strongest baseline (Claude Code) and about 64$\times$ other
baselines. It attains 81.5% functional coverage and a 69.7% pass rate,
exceeding Claude Code by 27.3 and 35.8 percentage points, respectively. Further
analysis shows that RPG models complex dependencies, enables progressively more
sophisticated planning through near-linear scaling, and enhances LLM
understanding of repositories, thereby accelerating agent localization.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.16179v1">Fast OTSU Thresholding Using Bisection Method</a></td><td><details><summary>展开</summary>The Otsu thresholding algorithm represents a fundamental technique in image
segmentation, yet its computational efficiency is severely limited by
exhaustive search requirements across all possible threshold values. This work
presents an optimized implementation that leverages the bisection method to
exploit the unimodal characteristics of the between-class variance function.
Our approach reduces the computational complexity from O(L) to O(log L)
evaluations while preserving segmentation accuracy. Experimental validation on
48 standard test images demonstrates a 91.63% reduction in variance
computations and 97.21% reduction in algorithmic iterations compared to
conventional exhaustive search. The bisection method achieves exact threshold
matches in 66.67% of test cases, with 95.83% exhibiting deviations within 5
gray levels. The algorithm maintains universal convergence within theoretical
logarithmic bounds while providing deterministic performance guarantees
suitable for real-time applications. This optimization addresses critical
computational bottlenecks in large-scale image processing systems without
compromising the theoretical foundations or segmentation quality of the
original Otsu method.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.16126v1">Network-Based Detection of Autism Spectrum Disorder Using Sustainable and Non-invasive Salivary Biomarkers</a></td><td><details><summary>展开</summary>Autism Spectrum Disorder (ASD) lacks reliable biological markers, delaying
early diagnosis. Using 159 salivary samples analyzed by ATR-FTIR spectroscopy,
we developed GANet, a genetic algorithm-based network optimization framework
leveraging PageRank and Degree for importance-based feature characterization.
GANet systematically optimizes network structure to extract meaningful patterns
from high-dimensional spectral data. It achieved superior performance compared
to linear discriminant analysis, support vector machines, and deep learning
models, reaching 0.78 accuracy, 0.61 sensitivity, 0.90 specificity, and a 0.74
harmonic mean. These results demonstrate GANet's potential as a robust,
bio-inspired, non-invasive tool for precise ASD detection and broader
spectral-based health applications.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.16117v1">DiffusionNFT: Online Diffusion Reinforcement with Forward Process</a></td><td><details><summary>展开</summary>Online reinforcement learning (RL) has been central to post-training language
models, but its extension to diffusion models remains challenging due to
intractable likelihoods. Recent works discretize the reverse sampling process
to enable GRPO-style training, yet they inherit fundamental drawbacks,
including solver restrictions, forward-reverse inconsistency, and complicated
integration with classifier-free guidance (CFG). We introduce Diffusion
Negative-aware FineTuning (DiffusionNFT), a new online RL paradigm that
optimizes diffusion models directly on the forward process via flow matching.
DiffusionNFT contrasts positive and negative generations to define an implicit
policy improvement direction, naturally incorporating reinforcement signals
into the supervised learning objective. This formulation enables training with
arbitrary black-box solvers, eliminates the need for likelihood estimation, and
requires only clean images rather than sampling trajectories for policy
optimization. DiffusionNFT is up to $25\times$ more efficient than FlowGRPO in
head-to-head comparisons, while being CFG-free. For instance, DiffusionNFT
improves the GenEval score from 0.24 to 0.98 within 1k steps, while FlowGRPO
achieves 0.95 with over 5k steps and additional CFG employment. By leveraging
multiple reward models, DiffusionNFT significantly boosts the performance of
SD3.5-Medium in every benchmark tested.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.16093v1">Beyond Pointwise Scores: Decomposed Criteria-Based Evaluation of LLM Responses</a></td><td><details><summary>展开</summary>Evaluating long-form answers in high-stakes domains such as law or medicine
remains a fundamental challenge. Standard metrics like BLEU and ROUGE fail to
capture semantic correctness, and current LLM-based evaluators often reduce
nuanced aspects of answer quality into a single undifferentiated score. We
introduce DeCE, a decomposed LLM evaluation framework that separates precision
(factual accuracy and relevance) and recall (coverage of required concepts),
using instance-specific criteria automatically extracted from gold answer
requirements. DeCE is model-agnostic and domain-general, requiring no
predefined taxonomies or handcrafted rubrics. We instantiate DeCE to evaluate
different LLMs on a real-world legal QA task involving multi-jurisdictional
reasoning and citation grounding. DeCE achieves substantially stronger
correlation with expert judgments ($r=0.78$), compared to traditional metrics
($r=0.12$), pointwise LLM scoring ($r=0.35$), and modern multidimensional
evaluators ($r=0.48$). It also reveals interpretable trade-offs: generalist
models favor recall, while specialized models favor precision. Importantly,
only 11.95% of LLM-generated criteria required expert revision, underscoring
DeCE's scalability. DeCE offers an interpretable and actionable LLM evaluation
framework in expert domains.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.16068v1">Communications to Circulations: 3D Wind Field Retrieval and Real-Time Prediction Using 5G GNSS Signals and Deep Learning</a></td><td><details><summary>展开</summary>Accurate atmospheric wind field information is crucial for various
applications, including weather forecasting, aviation safety, and disaster risk
reduction. However, obtaining high spatiotemporal resolution wind data remains
challenging due to limitations in traditional in-situ observations and remote
sensing techniques, as well as the computational expense and biases of
numerical weather prediction (NWP) models. This paper introduces G-WindCast, a
novel deep learning framework that leverages signal strength variations from 5G
Global Navigation Satellite System (GNSS) signals to retrieve and forecast
three-dimensional (3D) atmospheric wind fields. The framework utilizes Forward
Neural Networks (FNN) and Transformer networks to capture complex, nonlinear,
and spatiotemporal relationships between GNSS-derived features and wind
dynamics. Our preliminary results demonstrate promising accuracy in both wind
retrieval and short-term wind forecasting (up to 30 minutes lead time), with
skill scores comparable to high-resolution NWP outputs in certain scenarios.
The model exhibits robustness across different forecast horizons and pressure
levels, and its predictions for wind speed and direction show superior
agreement with observations compared to concurrent ERA5 reanalysis data.
Furthermore, we show that the system can maintain excellent performance for
localized forecasting even with a significantly reduced number of GNSS stations
(e.g., around 100), highlighting its cost-effectiveness and scalability. This
interdisciplinary approach underscores the transformative potential of
exploiting non-traditional data sources and deep learning for advanced
environmental monitoring and real-time atmospheric applications.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.16028v1">Think, Verbalize, then Speak: Bridging Complex Thoughts and Comprehensible Speech</a></td><td><details><summary>展开</summary>Spoken dialogue systems increasingly employ large language models (LLMs) to
leverage their advanced reasoning capabilities. However, direct application of
LLMs in spoken communication often yield suboptimal results due to mismatches
between optimal textual and verbal delivery. While existing approaches adapt
LLMs to produce speech-friendly outputs, their impact on reasoning performance
remains underexplored. In this work, we propose Think-Verbalize-Speak, a
framework that decouples reasoning from spoken delivery to preserve the full
reasoning capacity of LLMs. Central to our method is verbalizing, an
intermediate step that translates thoughts into natural, speech-ready text. We
also introduce ReVerT, a latency-efficient verbalizer based on incremental and
asynchronous summarization. Experiments across multiple benchmarks show that
our method enhances speech naturalness and conciseness with minimal impact on
reasoning. The project page with the dataset and the source code is available
at https://yhytoto12.github.io/TVS-ReVerT</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.15964v1">MoE-CE: Enhancing Generalization for Deep Learning based Channel Estimation via a Mixture-of-Experts Framework</a></td><td><details><summary>展开</summary>Reliable channel estimation (CE) is fundamental for robust communication in
dynamic wireless environments, where models must generalize across varying
conditions such as signal-to-noise ratios (SNRs), the number of resource blocks
(RBs), and channel profiles. Traditional deep learning (DL)-based methods
struggle to generalize effectively across such diverse settings, particularly
under multitask and zero-shot scenarios. In this work, we propose MoE-CE, a
flexible mixture-of-experts (MoE) framework designed to enhance the
generalization capability of DL-based CE methods. MoE-CE provides an
appropriate inductive bias by leveraging multiple expert subnetworks, each
specialized in distinct channel characteristics, and a learned router that
dynamically selects the most relevant experts per input. This architecture
enhances model capacity and adaptability without a proportional rise in
computational cost while being agnostic to the choice of the backbone model and
the learning algorithm. Through extensive experiments on synthetic datasets
generated under diverse SNRs, RB numbers, and channel profiles, including
multitask and zero-shot evaluations, we demonstrate that MoE-CE consistently
outperforms conventional DL approaches, achieving significant performance gains
while maintaining efficiency.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.15952v1">Compose Yourself: Average-Velocity Flow Matching for One-Step Speech Enhancement</a></td><td><details><summary>展开</summary>Diffusion and flow matching (FM) models have achieved remarkable progress in
speech enhancement (SE), yet their dependence on multi-step generation is
computationally expensive and vulnerable to discretization errors. Recent
advances in one-step generative modeling, particularly MeanFlow, provide a
promising alternative by reformulating dynamics through average velocity
fields. In this work, we present COSE, a one-step FM framework tailored for SE.
To address the high training overhead of Jacobian-vector product (JVP)
computations in MeanFlow, we introduce a velocity composition identity to
compute average velocity efficiently, eliminating expensive computation while
preserving theoretical consistency and achieving competitive enhancement
quality. Extensive experiments on standard benchmarks show that COSE delivers
up to 5x faster sampling and reduces training cost by 40%, all without
compromising speech quality. Code is available at
https://github.com/ICDM-UESTC/COSE.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.15932v1">The Alignment Bottleneck</a></td><td><details><summary>展开</summary>Large language models improve with scale, yet feedback-based alignment still
exhibits systematic deviations from intended behavior. Motivated by bounded
rationality in economics and cognitive science, we view judgment as
resource-limited and feedback as a constrained channel. On this basis, we model
the loop as a two-stage cascade $U \to H \to Y$ given $S$, with cognitive
capacity $C_{\text{cog}|S}$ and average total capacity
$\bar{C}_{\text{tot}|S}$. Our main result is a capacity-coupled Alignment
Performance Interval. It pairs a data size-independent Fano lower bound proved
on a separable codebook mixture with a PAC-Bayes upper bound whose KL term is
controlled by the same channel via $m \, \bar{C}_{\text{tot}|S}$. The PAC-Bayes
bound becomes an upper bound on the same true risk when the canonical
observable loss is used and the dataset is drawn from the same mixture. Under
these matched conditions, both limits are governed by a single capacity.
Consequences include that, with value complexity and capacity fixed, adding
labels alone cannot cross the bound; attaining lower risk on more complex
targets requires capacity that grows with $\log M$; and once useful signal
saturates capacity, further optimization tends to fit channel regularities,
consistent with reports of sycophancy and reward hacking. The analysis views
alignment as interface engineering: measure and allocate limited capacity,
manage task complexity, and decide where information is spent.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.15908v1">An Equivariant Graph Network for Interpretable Nanoporous Materials Design</a></td><td><details><summary>展开</summary>Nanoporous materials hold promise for diverse sustainable applications, yet
their vast chemical space poses challenges for efficient design. Machine
learning offers a compelling pathway to accelerate the exploration, but
existing models lack either interpretability or fidelity for elucidating the
correlation between crystal geometry and property. Here, we report a
three-dimensional periodic space sampling method that decomposes large
nanoporous structures into local geometrical sites for combined property
prediction and site-wise contribution quantification. Trained with a
constructed database and retrieved datasets, our model achieves
state-of-the-art accuracy and data efficiency for property prediction on gas
storage, separation, and electrical conduction. Meanwhile, this approach
enables the interpretation of the prediction and allows for accurate
identification of significant local sites for targeted properties. Through
identifying transferable high-performance sites across diverse nanoporous
frameworks, our model paves the way for interpretable, symmetry-aware
nanoporous materials design, which is extensible to other materials, like
molecular crystals and beyond.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.15895v1">From Data to Diagnosis: A Large, Comprehensive Bone Marrow Dataset and AI Methods for Childhood Leukemia Prediction</a></td><td><details><summary>展开</summary>Leukemia diagnosis primarily relies on manual microscopic analysis of bone
marrow morphology supported by additional laboratory parameters, making it
complex and time consuming. While artificial intelligence (AI) solutions have
been proposed, most utilize private datasets and only cover parts of the
diagnostic pipeline. Therefore, we present a large, high-quality, publicly
available leukemia bone marrow dataset spanning the entire diagnostic process,
from cell detection to diagnosis. Using this dataset, we further propose
methods for cell detection, cell classification, and diagnosis prediction. The
dataset comprises 246 pediatric patients with diagnostic, clinical and
laboratory information, over 40 000 cells with bounding box annotations and
more than 28 000 of these with high-quality class labels, making it the most
comprehensive dataset publicly available. Evaluation of the AI models yielded
an average precision of 0.96 for the cell detection, an area under the curve of
0.98, and an F1-score of 0.61 for the 33-class cell classification, and a mean
F1-score of 0.90 for the diagnosis prediction using predicted cell counts.
While the proposed approaches demonstrate their usefulness for AI-assisted
diagnostics, the dataset will foster further research and development in the
field, ultimately contributing to more precise diagnoses and improved patient
outcomes.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.15848v1">A Comparative Study of Rule-Based and Data-Driven Approaches in Industrial Monitoring</a></td><td><details><summary>展开</summary>Industrial monitoring systems, especially when deployed in Industry 4.0
environments, are experiencing a shift in paradigm from traditional rule-based
architectures to data-driven approaches leveraging machine learning and
artificial intelligence. This study presents a comparison between these two
methodologies, analyzing their respective strengths, limitations, and
application scenarios, and proposes a basic framework to evaluate their key
properties. Rule-based systems offer high interpretability, deterministic
behavior, and ease of implementation in stable environments, making them ideal
for regulated industries and safety-critical applications. However, they face
challenges with scalability, adaptability, and performance in complex or
evolving contexts. Conversely, data-driven systems excel in detecting hidden
anomalies, enabling predictive maintenance and dynamic adaptation to new
conditions. Despite their high accuracy, these models face challenges related
to data availability, explainability, and integration complexity. The paper
suggests hybrid solutions as a possible promising direction, combining the
transparency of rule-based logic with the analytical power of machine learning.
Our hypothesis is that the future of industrial monitoring lies in intelligent,
synergic systems that leverage both expert knowledge and data-driven insights.
This dual approach enhances resilience, operational efficiency, and trust,
paving the way for smarter and more flexible industrial environments.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.15811v1">Best-of-L: Cross-Lingual Reward Modeling for Mathematical Reasoning</a></td><td><details><summary>展开</summary>While the reasoning abilities of large language models (LLMs) continue to
advance, it remains unclear how such ability varies across languages in
multilingual LLMs and whether different languages produce reasoning paths that
complement each other. To investigate this question, we train a reward model to
rank generated responses for a given question across languages. Our results
show that our cross-lingual reward model substantially improves mathematical
reasoning performance compared to using reward modeling within a single
language, benefiting even high-resource languages. While English often exhibits
the highest performance in multilingual models, we find that cross-lingual
sampling particularly benefits English under low sampling budgets. Our findings
reveal new opportunities to improve multilingual reasoning by leveraging the
complementary strengths of diverse languages.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.15810v1">Instance Generation for Meta-Black-Box Optimization through Latent Space Reverse Engineering</a></td><td><details><summary>展开</summary>To relieve intensive human-expertise required to design optimization
algorithms, recent Meta-Black-Box Optimization (MetaBBO) researches leverage
generalization strength of meta-learning to train neural network-based
algorithm design policies over a predefined training problem set, which
automates the adaptability of the low-level optimizers on unseen problem
instances. Currently, a common training problem set choice in existing MetaBBOs
is well-known benchmark suites CoCo-BBOB. Although such choice facilitates the
MetaBBO's development, problem instances in CoCo-BBOB are more or less limited
in diversity, raising the risk of overfitting of MetaBBOs, which might further
results in poor generalization. In this paper, we propose an instance
generation approach, termed as \textbf{LSRE}, which could generate diverse
training problem instances for MetaBBOs to learn more generalizable policies.
LSRE first trains an autoencoder which maps high-dimensional problem features
into a 2-dimensional latent space. Uniform-grid sampling in this latent space
leads to hidden representations of problem instances with sufficient diversity.
By leveraging a genetic-programming approach to search function formulas with
minimal L2-distance to these hidden representations, LSRE reverse engineers a
diversified problem set, termed as \textbf{Diverse-BBO}. We validate the
effectiveness of LSRE by training various MetaBBOs on Diverse-BBO and observe
their generalization performances on either synthetic or realistic scenarios.
Extensive experimental results underscore the superiority of Diverse-BBO to
existing training set choices in MetaBBOs. Further ablation studies not only
demonstrate the effectiveness of design choices in LSRE, but also reveal
interesting insights on instance diversity and MetaBBO's generalization.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.15800v1">ChronoForge-RL: Chronological Forging through Reinforcement Learning for Enhanced Video Understanding</a></td><td><details><summary>展开</summary>Current state-of-the-art video understanding methods typically struggle with
two critical challenges: (1) the computational infeasibility of processing
every frame in dense video content and (2) the difficulty in identifying
semantically significant frames through naive uniform sampling strategies. In
this paper, we propose a novel video understanding framework, called
ChronoForge-RL, which combines Temporal Apex Distillation (TAD) and
KeyFrame-aware Group Relative Policy Optimization (KF-GRPO) to tackle these
issues. Concretely, we introduce a differentiable keyframe selection mechanism
that systematically identifies semantic inflection points through a three-stage
process to enhance computational efficiency while preserving temporal
information. Then, two particular modules are proposed to enable effective
temporal reasoning: Firstly, TAD leverages variation scoring, inflection
detection, and prioritized distillation to select the most informative frames.
Secondly, we introduce KF-GRPO which implements a contrastive learning paradigm
with a saliency-enhanced reward mechanism that explicitly incentivizes models
to leverage both frame content and temporal relationships. Finally, our
proposed ChronoForge-RL achieves 69.1% on VideoMME and 52.7% on LVBench
compared to baseline methods, clearly surpassing previous approaches while
enabling our 7B parameter model to achieve performance comparable to 72B
parameter alternatives.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.15796v1">Monte Carlo Tree Diffusion with Multiple Experts for Protein Design</a></td><td><details><summary>展开</summary>The goal of protein design is to generate amino acid sequences that fold into
functional structures with desired properties. Prior methods combining
autoregressive language models with Monte Carlo Tree Search (MCTS) struggle
with long-range dependencies and suffer from an impractically large search
space. We propose MCTD-ME, Monte Carlo Tree Diffusion with Multiple Experts,
which integrates masked diffusion models with tree search to enable multi-token
planning and efficient exploration. Unlike autoregressive planners, MCTD-ME
uses biophysical-fidelity-enhanced diffusion denoising as the rollout engine,
jointly revising multiple positions and scaling to large sequence spaces. It
further leverages experts of varying capacities to enrich exploration, guided
by a pLDDT-based masking schedule that targets low-confidence regions while
preserving reliable residues. We propose a novel multi-expert selection rule
(PH-UCT-ME) extends predictive-entropy UCT to expert ensembles. On the inverse
folding task (CAMEO and PDB benchmarks), MCTD-ME outperforms single-expert and
unguided baselines in both sequence recovery (AAR) and structural similarity
(scTM), with gains increasing for longer proteins and benefiting from
multi-expert guidance. More generally, the framework is model-agnostic and
applicable beyond inverse folding, including de novo protein engineering and
multi-objective molecular generation.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.15785v1">CBPNet: A Continual Backpropagation Prompt Network for Alleviating Plasticity Loss on Edge Devices</a></td><td><details><summary>展开</summary>To meet the demands of applications like robotics and autonomous driving that
require real-time responses to dynamic environments, efficient continual
learning methods suitable for edge devices have attracted increasing attention.
In this transition, using frozen pretrained models with prompts has become a
mainstream strategy to combat catastrophic forgetting. However, this approach
introduces a new critical bottleneck: plasticity loss, where the model's
ability to learn new knowledge diminishes due to the frozen backbone and the
limited capacity of prompt parameters. We argue that the reduction in
plasticity stems from a lack of update vitality in underutilized parameters
during the training process. To this end, we propose the Continual
Backpropagation Prompt Network (CBPNet), an effective and parameter efficient
framework designed to restore the model's learning vitality. We innovatively
integrate an Efficient CBP Block that counteracts plasticity decay by
adaptively reinitializing these underutilized parameters. Experimental results
on edge devices demonstrate CBPNet's effectiveness across multiple benchmarks.
On Split CIFAR-100, it improves average accuracy by over 1% against a strong
baseline, and on the more challenging Split ImageNet-R, it achieves a state of
the art accuracy of 69.41%. This is accomplished by training additional
parameters that constitute less than 0.2% of the backbone's size, validating
our approach.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.15733v1">GP3: A 3D Geometry-Aware Policy with Multi-View Images for Robotic Manipulation</a></td><td><details><summary>展开</summary>Effective robotic manipulation relies on a precise understanding of 3D scene
geometry, and one of the most straightforward ways to acquire such geometry is
through multi-view observations. Motivated by this, we present GP3 -- a 3D
geometry-aware robotic manipulation policy that leverages multi-view input. GP3
employs a spatial encoder to infer dense spatial features from RGB
observations, which enable the estimation of depth and camera parameters,
leading to a compact yet expressive 3D scene representation tailored for
manipulation. This representation is fused with language instructions and
translated into continuous actions via a lightweight policy head. Comprehensive
experiments demonstrate that GP3 consistently outperforms state-of-the-art
methods on simulated benchmarks. Furthermore, GP3 transfers effectively to
real-world robots without depth sensors or pre-mapped environments, requiring
only minimal fine-tuning. These results highlight GP3 as a practical,
sensor-agnostic solution for geometry-aware robotic manipulation.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.15676v1">KITE: Kernelized and Information Theoretic Exemplars for In-Context Learning</a></td><td><details><summary>展开</summary>In-context learning (ICL) has emerged as a powerful paradigm for adapting
large language models (LLMs) to new and data-scarce tasks using only a few
carefully selected task-specific examples presented in the prompt. However,
given the limited context size of LLMs, a fundamental question arises: Which
examples should be selected to maximize performance on a given user query?
While nearest-neighbor-based methods like KATE have been widely adopted for
this purpose, they suffer from well-known drawbacks in high-dimensional
embedding spaces, including poor generalization and a lack of diversity. In
this work, we study this problem of example selection in ICL from a principled,
information theory-driven perspective. We first model an LLM as a linear
function over input embeddings and frame the example selection task as a
query-specific optimization problem: selecting a subset of exemplars from a
larger example bank that minimizes the prediction error on a specific query.
This formulation departs from traditional generalization-focused learning
theoretic approaches by targeting accurate prediction for a specific query
instance. We derive a principled surrogate objective that is approximately
submodular, enabling the use of a greedy algorithm with an approximation
guarantee. We further enhance our method by (i) incorporating the kernel trick
to operate in high-dimensional feature spaces without explicit mappings, and
(ii) introducing an optimal design-based regularizer to encourage diversity in
the selected examples. Empirically, we demonstrate significant improvements
over standard retrieval methods across a suite of classification tasks,
highlighting the benefits of structure-aware, diverse example selection for ICL
in real-world, label-scarce scenarios.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.15651v1">Toward Efficient Influence Function: Dropout as a Compression Tool</a></td><td><details><summary>展开</summary>Assessing the impact the training data on machine learning models is crucial
for understanding the behavior of the model, enhancing the transparency, and
selecting training data. Influence function provides a theoretical framework
for quantifying the effect of training data points on model's performance given
a specific test data. However, the computational and memory costs of influence
function presents significant challenges, especially for large-scale models,
even when using approximation methods, since the gradients involved in
computation are as large as the model itself. In this work, we introduce a
novel approach that leverages dropout as a gradient compression mechanism to
compute the influence function more efficiently. Our method significantly
reduces computational and memory overhead, not only during the influence
function computation but also in gradient compression process. Through
theoretical analysis and empirical validation, we demonstrate that our method
could preserves critical components of the data influence and enables its
application to modern large-scale models.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.15635v1">MicroRCA-Agent: Microservice Root Cause Analysis Method Based on Large Language Model Agents</a></td><td><details><summary>展开</summary>This paper presents MicroRCA-Agent, an innovative solution for microservice
root cause analysis based on large language model agents, which constructs an
intelligent fault root cause localization system with multimodal data fusion.
The technical innovations are embodied in three key aspects: First, we combine
the pre-trained Drain log parsing algorithm with multi-level data filtering
mechanism to efficiently compress massive logs into high-quality fault
features. Second, we employ a dual anomaly detection approach that integrates
Isolation Forest unsupervised learning algorithms with status code validation
to achieve comprehensive trace anomaly identification. Third, we design a
statistical symmetry ratio filtering mechanism coupled with a two-stage LLM
analysis strategy to enable full-stack phenomenon summarization across
node-service-pod hierarchies. The multimodal root cause analysis module
leverages carefully designed cross-modal prompts to deeply integrate multimodal
anomaly information, fully exploiting the cross-modal understanding and logical
reasoning capabilities of large language models to generate structured analysis
results encompassing fault components, root cause descriptions, and reasoning
trace. Comprehensive ablation studies validate the complementary value of each
modal data and the effectiveness of the system architecture. The proposed
solution demonstrates superior performance in complex microservice fault
scenarios, achieving a final score of 50.71. The code has been released at:
https://github.com/tangpan360/MicroRCA-Agent.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.15582v1">Momentum-constrained Hybrid Heuristic Trajectory Optimization Framework with Residual-enhanced DRL for Visually Impaired Scenarios</a></td><td><details><summary>展开</summary>This paper proposes a momentum-constrained hybrid heuristic trajectory
optimization framework (MHHTOF) tailored for assistive navigation in visually
impaired scenarios, integrating trajectory sampling generation, optimization
and evaluation with residual-enhanced deep reinforcement learning (DRL). In the
first stage, heuristic trajectory sampling cluster (HTSC) is generated in the
Frenet coordinate system using third-order interpolation with fifth-order
polynomials and momentum-constrained trajectory optimization (MTO) constraints
to ensure smoothness and feasibility. After first stage cost evaluation, the
second stage leverages a residual-enhanced actor-critic network with LSTM-based
temporal feature modeling to adaptively refine trajectory selection in the
Cartesian coordinate system. A dual-stage cost modeling mechanism (DCMM) with
weight transfer aligns semantic priorities across stages, supporting
human-centered optimization. Experimental results demonstrate that the proposed
LSTM-ResB-PPO achieves significantly faster convergence, attaining stable
policy performance in approximately half the training iterations required by
the PPO baseline, while simultaneously enhancing both reward outcomes and
training stability. Compared to baseline method, the selected model reduces
average cost and cost variance by 30.3% and 53.3%, and lowers ego and obstacle
risks by over 77%. These findings validate the framework's effectiveness in
enhancing robustness, safety, and real-time feasibility in complex assistive
planning tasks.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.15577v1">Relevance to Utility: Process-Supervised Rewrite for RAG</a></td><td><details><summary>展开</summary>Retrieval-Augmented Generation systems often suffer from a gap between
optimizing retrieval relevance and generative utility: retrieved documents may
be topically relevant but still lack the content needed for effective reasoning
during generation. While existing "bridge" modules attempt to rewrite the
retrieved text for better generation, we show how they fail to capture true
document utility. In this work, we propose R2U, with a key distinction of
directly optimizing to maximize the probability of generating a correct answer
through process supervision. As such direct observation is expensive, we also
propose approximating an efficient distillation pipeline by scaling the
supervision from LLMs, which helps the smaller rewriter model generalize
better. We evaluate our method across multiple open-domain question-answering
benchmarks. The empirical results demonstrate consistent improvements over
strong bridging baselines.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.15568v1">LiteLong: Resource-Efficient Long-Context Data Synthesis for LLMs</a></td><td><details><summary>展开</summary>High-quality long-context data is essential for training large language
models (LLMs) capable of processing extensive documents, yet existing synthesis
approaches using relevance-based aggregation face challenges of computational
efficiency. We present LiteLong, a resource-efficient method for synthesizing
long-context data through structured topic organization and multi-agent debate.
Our approach leverages the BISAC book classification system to provide a
comprehensive hierarchical topic organization, and then employs a debate
mechanism with multiple LLMs to generate diverse, high-quality topics within
this structure. For each topic, we use lightweight BM25 retrieval to obtain
relevant documents and concatenate them into 128K-token training samples.
Experiments on HELMET and Ruler benchmarks demonstrate that LiteLong achieves
competitive long-context performance and can seamlessly integrate with other
long-dependency enhancement methods. LiteLong makes high-quality long-context
data synthesis more accessible by reducing both computational and data
engineering costs, facilitating further research in long-context language
training.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.15556v1">Exploring Polyglot Harmony: On Multilingual Data Allocation for Large Language Models Pretraining</a></td><td><details><summary>展开</summary>Large language models (LLMs) have become integral to a wide range of
applications worldwide, driving an unprecedented global demand for effective
multilingual capabilities. Central to achieving robust multilingual performance
is the strategic allocation of language proportions within training corpora.
However, determining optimal language ratios is highly challenging due to
intricate cross-lingual interactions and sensitivity to dataset scale. This
paper introduces Climb (Cross-Lingual Interaction-aware Multilingual
Balancing), a novel framework designed to systematically optimize multilingual
data allocation. At its core, Climb introduces a cross-lingual
interaction-aware language ratio, explicitly quantifying each language's
effective allocation by capturing inter-language dependencies. Leveraging this
ratio, Climb proposes a principled two-step optimization procedure--first
equalizing marginal benefits across languages, then maximizing the magnitude of
the resulting language allocation vectors--significantly simplifying the
inherently complex multilingual optimization problem. Extensive experiments
confirm that Climb can accurately measure cross-lingual interactions across
various multilingual settings. LLMs trained with Climb-derived proportions
consistently achieve state-of-the-art multilingual performance, even achieving
competitive performance with open-sourced LLMs trained with more tokens.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.15541v1">Stress Testing Deliberative Alignment for Anti-Scheming Training</a></td><td><details><summary>展开</summary>Highly capable AI systems could secretly pursue misaligned goals -- what we
call "scheming". Because a scheming AI would deliberately try to hide its
misaligned goals and actions, measuring and mitigating scheming requires
different strategies than are typically used in ML. We propose that assessing
anti-scheming interventions requires at least (1) testing propensity to scheme
on far out-of-distribution (OOD) tasks, (2) evaluating whether lack of scheming
is driven by situational awareness, and (3) checking for robustness to
pre-existing misaligned goals. We use a broad category of "covert actions" --
such as secretly breaking rules or intentionally underperforming in tests -- as
a proxy for scheming, and design evaluations for covert actions. We then
stress-test deliberative alignment as a case study for anti-scheming. Across 26
OOD evaluations (180+ environments), deliberative alignment reduces covert
action rates (OpenAI o3: 13%->0.4%) but does not fully eliminate them. Our
mitigation is also able to largely stop agents from pursuing a hidden goal
previously trained into the model, but we still find misbehavior after
additional red-teaming. We find that models' chain-of-thought (CoT) often
demonstrates awareness of being evaluated for alignment, and show causal
evidence that this awareness decreases covert behavior, while unawareness
increases it. Therefore, we cannot exclude that the observed reductions in
covert action rates are at least partially driven by situational awareness.
While we rely on human-legible CoT for training, studying situational
awareness, and demonstrating clear evidence of misalignment, our ability to
rely on this degrades as models continue to depart from reasoning in standard
English. We encourage research into alignment mitigations for scheming and
their assessment, especially for the adversarial case of deceptive alignment,
which this paper does not address.</details></td></tr></tbody></table>

### 📅 2025-09-18
<table style='width:100%;'><colgroup><col style="width:61.8%;"><col style="width:38.2%;"></colgroup><thead><tr><th>title</th><th>abstract</th></tr></thead><tbody><tr><td><a href="http://arxiv.org/abs/2509.15210v1">Explicit Context-Driven Neural Acoustic Modeling for High-Fidelity RIR Generation</a></td><td><details><summary>展开</summary>Realistic sound simulation plays a critical role in many applications. A key
element in sound simulation is the room impulse response (RIR), which
characterizes how sound propagates from a source to a listener within a given
space. Recent studies have applied neural implicit methods to learn RIR using
context information collected from the environment, such as scene images.
However, these approaches do not effectively leverage explicit geometric
information from the environment. To further exploit the potential of neural
implicit models with direct geometric features, we present Mesh-infused Neural
Acoustic Field (MiNAF), which queries a rough room mesh at given locations and
extracts distance distributions as an explicit representation of local context.
Our approach demonstrates that incorporating explicit local geometric features
can better guide the neural network in generating more accurate RIR
predictions. Through comparisons with conventional and state-of-the-art
baseline methods, we show that MiNAF performs competitively across various
evaluation metrics. Furthermore, we verify the robustness of MiNAF in datasets
with limited training samples, demonstrating an advance in high-fidelity sound
simulation.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.15207v1">FlowRL: Matching Reward Distributions for LLM Reasoning</a></td><td><details><summary>展开</summary>We propose FlowRL: matching the full reward distribution via flow balancing
instead of maximizing rewards in large language model (LLM) reinforcement
learning (RL). Recent advanced reasoning models adopt reward-maximizing methods
(\eg, PPO and GRPO), which tend to over-optimize dominant reward signals while
neglecting less frequent but valid reasoning paths, thus reducing diversity. In
contrast, we transform scalar rewards into a normalized target distribution
using a learnable partition function, and then minimize the reverse KL
divergence between the policy and the target distribution. We implement this
idea as a flow-balanced optimization method that promotes diverse exploration
and generalizable reasoning trajectories. We conduct experiments on math and
code reasoning tasks: FlowRL achieves a significant average improvement of
$10.0\%$ over GRPO and $5.1\%$ over PPO on math benchmarks, and performs
consistently better on code reasoning tasks. These results highlight reward
distribution-matching as a key step toward efficient exploration and diverse
reasoning in LLM reinforcement learning.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.15174v1">SMARTER: A Data-efficient Framework to Improve Toxicity Detection with Explanation via Self-augmenting Large Language Models</a></td><td><details><summary>展开</summary>WARNING: This paper contains examples of offensive materials. Toxic content
has become pervasive on social media platforms. We introduce SMARTER, a
data-efficient two-stage framework for explainable content moderation using
Large Language Models (LLMs). In Stage 1, we leverage LLMs' own outputs to
generate synthetic explanations for both correct and incorrect labels, enabling
alignment via preference optimization with minimal human supervision. In Stage
2, we refine explanation quality through cross-model training, allowing weaker
models to align stylistically and semantically with stronger ones. Experiments
on three benchmark tasks -- HateXplain, Latent Hate, and Implicit Hate --
demonstrate that SMARTER enables LLMs to achieve up to a 13.5% macro-F1
improvement over standard few-shot baselines while using only a fraction of the
full training data. Our framework offers a scalable strategy for low-resource
settings by harnessing LLMs' self-improving capabilities for both
classification and explanation.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.15172v1">Internalizing Self-Consistency in Language Models: Multi-Agent Consensus Alignment</a></td><td><details><summary>展开</summary>Language Models (LMs) are inconsistent reasoners, often generating
contradictory responses to identical prompts. While inference-time methods can
mitigate these inconsistencies, they fail to address the core problem: LMs
struggle to reliably select reasoning pathways leading to consistent outcomes
under exploratory sampling. To address this, we formalize self-consistency as
an intrinsic property of well-aligned reasoning models and introduce
Multi-Agent Consensus Alignment (MACA), a reinforcement learning framework that
post-trains models to favor reasoning trajectories aligned with their internal
consensus using majority/minority outcomes from multi-agent debate. These
trajectories emerge from deliberative exchanges where agents ground reasoning
in peer arguments, not just aggregation of independent attempts, creating
richer consensus signals than single-round majority voting. MACA enables agents
to teach themselves to be more decisive and concise, and better leverage peer
insights in multi-agent settings without external supervision, driving
substantial improvements across self-consistency (+27.6% on GSM8K),
single-agent reasoning (+23.7% on MATH), sampling-based inference (+22.4%
Pass@20 on MATH), and multi-agent ensemble decision-making (+42.7% on MathQA).
These findings, coupled with strong generalization to unseen benchmarks (+16.3%
on GPQA, +11.6% on CommonsenseQA), demonstrate robust self-alignment that more
reliably unlocks latent reasoning potential of language models.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.15156v1">Leveraging Geometric Visual Illusions as Perceptual Inductive Biases for Vision Models</a></td><td><details><summary>展开</summary>Contemporary deep learning models have achieved impressive performance in
image classification by primarily leveraging statistical regularities within
large datasets, but they rarely incorporate structured insights drawn directly
from perceptual psychology. To explore the potential of perceptually motivated
inductive biases, we propose integrating classic geometric visual illusions
well-studied phenomena from human perception into standard image-classification
training pipelines. Specifically, we introduce a synthetic, parametric
geometric-illusion dataset and evaluate three multi-source learning strategies
that combine illusion recognition tasks with ImageNet classification
objectives. Our experiments reveal two key conceptual insights: (i)
incorporating geometric illusions as auxiliary supervision systematically
improves generalization, especially in visually challenging cases involving
intricate contours and fine textures; and (ii) perceptually driven inductive
biases, even when derived from synthetic stimuli traditionally considered
unrelated to natural image recognition, can enhance the structural sensitivity
of both CNN and transformer-based architectures. These results demonstrate a
novel integration of perceptual science and machine learning and suggest new
directions for embedding perceptual priors into vision model design.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.15151v1">Exploring How Audio Effects Alter Emotion with Foundation Models</a></td><td><details><summary>展开</summary>Audio effects (FX) such as reverberation, distortion, modulation, and dynamic
range processing play a pivotal role in shaping emotional responses during
music listening. While prior studies have examined links between low-level
audio features and affective perception, the systematic impact of audio FX on
emotion remains underexplored. This work investigates how foundation models -
large-scale neural architectures pretrained on multimodal data - can be
leveraged to analyze these effects. Such models encode rich associations
between musical structure, timbre, and affective meaning, offering a powerful
framework for probing the emotional consequences of sound design techniques. By
applying various probing methods to embeddings from deep learning models, we
examine the complex, nonlinear relationships between audio FX and estimated
emotion, uncovering patterns tied to specific effects and evaluating the
robustness of foundation audio models. Our findings aim to advance
understanding of the perceptual impact of audio production practices, with
implications for music cognition, performance, and affective computing.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.15130v1">WorldForge: Unlocking Emergent 3D/4D Generation in Video Diffusion Model via Training-Free Guidance</a></td><td><details><summary>展开</summary>Recent video diffusion models demonstrate strong potential in spatial
intelligence tasks due to their rich latent world priors. However, this
potential is hindered by their limited controllability and geometric
inconsistency, creating a gap between their strong priors and their practical
use in 3D/4D tasks. As a result, current approaches often rely on retraining or
fine-tuning, which risks degrading pretrained knowledge and incurs high
computational costs. To address this, we propose WorldForge, a training-free,
inference-time framework composed of three tightly coupled modules. Intra-Step
Recursive Refinement introduces a recursive refinement mechanism during
inference, which repeatedly optimizes network predictions within each denoising
step to enable precise trajectory injection. Flow-Gated Latent Fusion leverages
optical flow similarity to decouple motion from appearance in the latent space
and selectively inject trajectory guidance into motion-related channels.
Dual-Path Self-Corrective Guidance compares guided and unguided denoising paths
to adaptively correct trajectory drift caused by noisy or misaligned structural
signals. Together, these components inject fine-grained, trajectory-aligned
guidance without training, achieving both accurate motion control and
photorealistic content generation. Extensive experiments across diverse
benchmarks validate our method's superiority in realism, trajectory
consistency, and visual fidelity. This work introduces a novel plug-and-play
paradigm for controllable video synthesis, offering a new perspective on
leveraging generative priors for spatial intelligence.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.15095v1">Listening, Imagining \& Refining: A Heuristic Optimized ASR Correction Framework with LLMs</a></td><td><details><summary>展开</summary>Automatic Speech Recognition (ASR) systems remain prone to errors that affect
downstream applications. In this paper, we propose LIR-ASR, a heuristic
optimized iterative correction framework using LLMs, inspired by human auditory
perception. LIR-ASR applies a "Listening-Imagining-Refining" strategy,
generating phonetic variants and refining them in context. A heuristic
optimization with finite state machine (FSM) is introduced to prevent the
correction process from being trapped in local optima and rule-based
constraints help maintain semantic fidelity. Experiments on both English and
Chinese ASR outputs show that LIR-ASR achieves average reductions in CER/WER of
up to 1.5 percentage points compared to baselines, demonstrating substantial
accuracy gains in transcription.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.15058v1">Communication Efficient Split Learning of ViTs with Attention-based Double Compression</a></td><td><details><summary>展开</summary>This paper proposes a novel communication-efficient Split Learning (SL)
framework, named Attention-based Double Compression (ADC), which reduces the
communication overhead required for transmitting intermediate Vision
Transformers activations during the SL training process. ADC incorporates two
parallel compression strategies. The first one merges samples' activations that
are similar, based on the average attention score calculated in the last client
layer; this strategy is class-agnostic, meaning that it can also merge samples
having different classes, without losing generalization ability nor decreasing
final results. The second strategy follows the first and discards the least
meaningful tokens, further reducing the communication cost. Combining these
strategies not only allows for sending less during the forward pass, but also
the gradients are naturally compressed, allowing the whole model to be trained
without additional tuning or approximations of the gradients. Simulation
results demonstrate that Attention-based Double Compression outperforms
state-of-the-art SL frameworks by significantly reducing communication
overheads while maintaining high accuracy.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.15027v1">CLEAR: A Comprehensive Linguistic Evaluation of Argument Rewriting by Large Language Models</a></td><td><details><summary>展开</summary>While LLMs have been extensively studied on general text generation tasks,
there is less research on text rewriting, a task related to general text
generation, and particularly on the behavior of models on this task. In this
paper we analyze what changes LLMs make in a text rewriting setting. We focus
specifically on argumentative texts and their improvement, a task named
Argument Improvement (ArgImp). We present CLEAR: an evaluation pipeline
consisting of 57 metrics mapped to four linguistic levels: lexical, syntactic,
semantic and pragmatic. This pipeline is used to examine the qualities of
LLM-rewritten arguments on a broad set of argumentation corpora and compare the
behavior of different LLMs on this task and analyze the behavior of different
LLMs on this task in terms of linguistic levels. By taking all four linguistic
levels into consideration, we find that the models perform ArgImp by shortening
the texts while simultaneously increasing average word length and merging
sentences. Overall we note an increase in the persuasion and coherence
dimensions.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.14998v1">A Knowledge-driven Adaptive Collaboration of LLMs for Enhancing Medical Decision-making</a></td><td><details><summary>展开</summary>Medical decision-making often involves integrating knowledge from multiple
clinical specialties, typically achieved through multidisciplinary teams.
Inspired by this collaborative process, recent work has leveraged large
language models (LLMs) in multi-agent collaboration frameworks to emulate
expert teamwork. While these approaches improve reasoning through agent
interaction, they are limited by static, pre-assigned roles, which hinder
adaptability and dynamic knowledge integration. To address these limitations,
we propose KAMAC, a Knowledge-driven Adaptive Multi-Agent Collaboration
framework that enables LLM agents to dynamically form and expand expert teams
based on the evolving diagnostic context. KAMAC begins with one or more expert
agents and then conducts a knowledge-driven discussion to identify and fill
knowledge gaps by recruiting additional specialists as needed. This supports
flexible, scalable collaboration in complex clinical scenarios, with decisions
finalized through reviewing updated agent comments. Experiments on two
real-world medical benchmarks demonstrate that KAMAC significantly outperforms
both single-agent and advanced multi-agent methods, particularly in complex
clinical scenarios (i.e., cancer prognosis) requiring dynamic, cross-specialty
expertise. Our code is publicly available at:
https://github.com/XiaoXiao-Woo/KAMAC.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.14980v1">M4Diffuser: Multi-View Diffusion Policy with Manipulability-Aware Control for Robust Mobile Manipulation</a></td><td><details><summary>展开</summary>Mobile manipulation requires the coordinated control of a mobile base and a
robotic arm while simultaneously perceiving both global scene context and
fine-grained object details. Existing single-view approaches often fail in
unstructured environments due to limited fields of view, exploration, and
generalization abilities. Moreover, classical controllers, although stable,
struggle with efficiency and manipulability near singularities. To address
these challenges, we propose M4Diffuser, a hybrid framework that integrates a
Multi-View Diffusion Policy with a novel Reduced and Manipulability-aware QP
(ReM-QP) controller for mobile manipulation. The diffusion policy leverages
proprioceptive states and complementary camera perspectives with both
close-range object details and global scene context to generate task-relevant
end-effector goals in the world frame. These high-level goals are then executed
by the ReM-QP controller, which eliminates slack variables for computational
efficiency and incorporates manipulability-aware preferences for robustness
near singularities. Comprehensive experiments in simulation and real-world
environments show that M4Diffuser achieves 7 to 56 percent higher success rates
and reduces collisions by 3 to 31 percent over baselines. Our approach
demonstrates robust performance for smooth whole-body coordination, and strong
generalization to unseen tasks, paving the way for reliable mobile manipulation
in unstructured environments. Details of the demo and supplemental material are
available on our project website https://sites.google.com/view/m4diffuser.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.14930v1">Cross-Modal Knowledge Distillation for Speech Large Language Models</a></td><td><details><summary>展开</summary>In this work, we present the first systematic evaluation of catastrophic
forgetting and modality inequivalence in speech large language models, showing
that introducing speech capabilities can degrade knowledge and reasoning even
when inputs remain textual, and performance further decreases with spoken
queries. To address these challenges, we propose a cross-modal knowledge
distillation framework that leverages both text-to-text and speech-to-text
channels to transfer knowledge from a text-based teacher model to a speech LLM.
Extensive experiments on dialogue and audio understanding tasks validate the
effectiveness of our approach in preserving textual knowledge, improving
cross-modal alignment, and enhancing reasoning in speech-based interactions.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.14886v1">A Multi-To-One Interview Paradigm for Efficient MLLM Evaluation</a></td><td><details><summary>展开</summary>The rapid progress of Multi-Modal Large Language Models (MLLMs) has spurred
the creation of numerous benchmarks. However, conventional full-coverage
Question-Answering evaluations suffer from high redundancy and low efficiency.
Inspired by human interview processes, we propose a multi-to-one interview
paradigm for efficient MLLM evaluation. Our framework consists of (i) a
two-stage interview strategy with pre-interview and formal interview phases,
(ii) dynamic adjustment of interviewer weights to ensure fairness, and (iii) an
adaptive mechanism for question difficulty-level chosen. Experiments on
different benchmarks show that the proposed paradigm achieves significantly
higher correlation with full-coverage results than random sampling, with
improvements of up to 17.6% in PLCC and 16.7% in SRCC, while reducing the
number of required questions. These findings demonstrate that the proposed
paradigm provides a reliable and efficient alternative for large-scale MLLM
benchmarking.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.14860v1">MARIC: Multi-Agent Reasoning for Image Classification</a></td><td><details><summary>展开</summary>Image classification has traditionally relied on parameter-intensive model
training, requiring large-scale annotated datasets and extensive fine tuning to
achieve competitive performance. While recent vision language models (VLMs)
alleviate some of these constraints, they remain limited by their reliance on
single pass representations, often failing to capture complementary aspects of
visual content. In this paper, we introduce Multi Agent based Reasoning for
Image Classification (MARIC), a multi agent framework that reformulates image
classification as a collaborative reasoning process. MARIC first utilizes an
Outliner Agent to analyze the global theme of the image and generate targeted
prompts. Based on these prompts, three Aspect Agents extract fine grained
descriptions along distinct visual dimensions. Finally, a Reasoning Agent
synthesizes these complementary outputs through integrated reflection step,
producing a unified representation for classification. By explicitly
decomposing the task into multiple perspectives and encouraging reflective
synthesis, MARIC mitigates the shortcomings of both parameter-heavy training
and monolithic VLM reasoning. Experiments on 4 diverse image classification
benchmark datasets demonstrate that MARIC significantly outperforms baselines,
highlighting the effectiveness of multi-agent visual reasoning for robust and
interpretable image classification.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.14858v1">MeanFlowSE: one-step generative speech enhancement via conditional mean flow</a></td><td><details><summary>展开</summary>Multistep inference is a bottleneck for real-time generative speech
enhancement because flow- and diffusion-based systems learn an instantaneous
velocity field and therefore rely on iterative ordinary differential equation
(ODE) solvers. We introduce MeanFlowSE, a conditional generative model that
learns the average velocity over finite intervals along a trajectory. Using a
Jacobian-vector product (JVP) to instantiate the MeanFlow identity, we derive a
local training objective that directly supervises finite-interval displacement
while remaining consistent with the instantaneous-field constraint on the
diagonal. At inference, MeanFlowSE performs single-step generation via a
backward-in-time displacement, removing the need for multistep solvers; an
optional few-step variant offers additional refinement. On VoiceBank-DEMAND,
the single-step model achieves strong intelligibility, fidelity, and perceptual
quality with substantially lower computational cost than multistep baselines.
The method requires no knowledge distillation or external teachers, providing
an efficient, high-fidelity framework for real-time generative speech
enhancement.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.14832v1">Diffusion-Based Scenario Tree Generation for Multivariate Time Series Prediction and Multistage Stochastic Optimization</a></td><td><details><summary>展开</summary>Stochastic forecasting is critical for efficient decision-making in uncertain
systems, such as energy markets and finance, where estimating the full
distribution of future scenarios is essential. We propose Diffusion Scenario
Tree (DST), a general framework for constructing scenario trees for
multivariate prediction tasks using diffusion-based probabilistic forecasting
models. DST recursively samples future trajectories and organizes them into a
tree via clustering, ensuring non-anticipativity (decisions depending only on
observed history) at each stage. We evaluate the framework on the optimization
task of energy arbitrage in New York State's day-ahead electricity market.
Experimental results show that our approach consistently outperforms the same
optimization algorithms that use scenario trees from more conventional models
and Model-Free Reinforcement Learning baselines. Furthermore, using DST for
stochastic optimization yields more efficient decision policies, achieving
higher performance by better handling uncertainty than deterministic and
stochastic MPC variants using the same diffusion-based forecaster.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.14750v1">Enhancing Retrieval Augmentation via Adversarial Collaboration</a></td><td><details><summary>展开</summary>Retrieval-augmented Generation (RAG) is a prevalent approach for
domain-specific LLMs, yet it is often plagued by "Retrieval Hallucinations"--a
phenomenon where fine-tuned models fail to recognize and act upon poor-quality
retrieved documents, thus undermining performance. To address this, we propose
the Adversarial Collaboration RAG (AC-RAG) framework. AC-RAG employs two
heterogeneous agents: a generalist Detector that identifies knowledge gaps, and
a domain-specialized Resolver that provides precise solutions. Guided by a
moderator, these agents engage in an adversarial collaboration, where the
Detector's persistent questioning challenges the Resolver's expertise. This
dynamic process allows for iterative problem dissection and refined knowledge
retrieval. Extensive experiments show that AC-RAG significantly improves
retrieval accuracy and outperforms state-of-the-art RAG methods across various
vertical domains.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.14693v1">RationAnomaly: Log Anomaly Detection with Rationality via Chain-of-Thought and Reinforcement Learning</a></td><td><details><summary>展开</summary>Logs constitute a form of evidence signaling the operational status of
software systems. Automated log anomaly detection is crucial for ensuring the
reliability of modern software systems. However, existing approaches face
significant limitations: traditional deep learning models lack interpretability
and generalization, while methods leveraging Large Language Models are often
hindered by unreliability and factual inaccuracies. To address these issues, we
propose RationAnomaly, a novel framework that enhances log anomaly detection by
synergizing Chain-of-Thought (CoT) fine-tuning with reinforcement learning. Our
approach first instills expert-like reasoning patterns using CoT-guided
supervised fine-tuning, grounded in a high-quality dataset corrected through a
rigorous expert-driven process. Subsequently, a reinforcement learning phase
with a multi-faceted reward function optimizes for accuracy and logical
consistency, effectively mitigating hallucinations. Experimentally,
RationAnomaly outperforms state-of-the-art baselines, achieving superior
F1-scores on key benchmarks while providing transparent, step-by-step
analytical outputs. We have released the corresponding resources, including
code and datasets.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.14671v1">TableDART: Dynamic Adaptive Multi-Modal Routing for Table Understanding</a></td><td><details><summary>展开</summary>Modeling semantic and structural information from tabular data remains a core
challenge for effective table understanding. Existing Table-as-Text approaches
flatten tables for large language models (LLMs), but lose crucial structural
cues, while Table-as-Image methods preserve structure yet struggle with
fine-grained semantics. Recent Table-as-Multimodality strategies attempt to
combine textual and visual views, but they (1) statically process both
modalities for every query-table pair within a large multimodal LLMs (MLLMs),
inevitably introducing redundancy and even conflicts, and (2) depend on costly
fine-tuning of MLLMs. In light of this, we propose TableDART, a
training-efficient framework that integrates multimodal views by reusing
pretrained single-modality models. TableDART introduces a lightweight
2.59M-parameter MLP gating network that dynamically selects the optimal path
(either Text-only, Image-only, or Fusion) for each table-query pair,
effectively reducing redundancy and conflicts from both modalities. In
addition, we propose a novel agent to mediate cross-modal knowledge integration
by analyzing outputs from text- and image-based models, either selecting the
best result or synthesizing a new answer through reasoning. This design avoids
the prohibitive costs of full MLLM fine-tuning. Extensive experiments on seven
benchmarks show that TableDART establishes new state-of-the-art performance
among open-source models, surpassing the strongest baseline by an average of
4.02%. The code is available at:
https://anonymous.4open.science/r/TableDART-C52B</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.14662v1">Understanding the Thinking Process of Reasoning Models: A Perspective from Schoenfeld's Episode Theory</a></td><td><details><summary>展开</summary>While Large Reasoning Models (LRMs) generate extensive chain-of-thought
reasoning, we lack a principled framework for understanding how these thoughts
are structured. In this paper, we introduce a novel approach by applying
Schoenfeld's Episode Theory, a classic cognitive framework for human
mathematical problem-solving, to analyze the reasoning traces of LRMs. We
annotated thousands of sentences and paragraphs from model-generated solutions
to math problems using seven cognitive labels (e.g., Plan, Implement, Verify).
The result is the first publicly available benchmark for the fine-grained
analysis of machine reasoning, including a large annotated corpus and detailed
annotation guidebooks. Our preliminary analysis reveals distinct patterns in
LRM reasoning, such as the transition dynamics between cognitive states. This
framework provides a theoretically grounded methodology for interpreting LRM
cognition and enables future work on more controllable and transparent
reasoning systems.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.14623v1">Automating Modelica Module Generation Using Large Language Models: A Case Study on Building Control Description Language</a></td><td><details><summary>展开</summary>Dynamic energy systems and controls require advanced modeling frameworks to
design and test supervisory and fault tolerant strategies. Modelica is a widely
used equation based language, but developing control modules is labor intensive
and requires specialized expertise. This paper examines the use of large
language models (LLMs) to automate the generation of Control Description
Language modules in the Building Modelica Library as a case study. We developed
a structured workflow that combines standardized prompt scaffolds, library
aware grounding, automated compilation with OpenModelica, and human in the loop
evaluation. Experiments were carried out on four basic logic tasks (And, Or,
Not, and Switch) and five control modules (chiller enable/disable, bypass valve
control, cooling tower fan speed, plant requests, and relief damper control).
The results showed that GPT 4o failed to produce executable Modelica code in
zero shot mode, while Claude Sonnet 4 achieved up to full success for basic
logic blocks with carefully engineered prompts. For control modules, success
rates reached 83 percent, and failed outputs required medium level human repair
(estimated one to eight hours). Retrieval augmented generation often produced
mismatches in module selection (for example, And retrieved as Or), while a
deterministic hard rule search strategy avoided these errors. Human evaluation
also outperformed AI evaluation, since current LLMs cannot assess simulation
results or validate behavioral correctness. Despite these limitations, the LLM
assisted workflow reduced the average development time from 10 to 20 hours down
to 4 to 6 hours per module, corresponding to 40 to 60 percent time savings.
These results highlight both the potential and current limitations of LLM
assisted Modelica generation, and point to future research in pre simulation
validation, stronger grounding, and closed loop evaluation.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.14622v1">Adversarial Distilled Retrieval-Augmented Guarding Model for Online Malicious Intent Detection</a></td><td><details><summary>展开</summary>With the deployment of Large Language Models (LLMs) in interactive
applications, online malicious intent detection has become increasingly
critical. However, existing approaches fall short of handling diverse and
complex user queries in real time. To address these challenges, we introduce
ADRAG (Adversarial Distilled Retrieval-Augmented Guard), a two-stage framework
for robust and efficient online malicious intent detection. In the training
stage, a high-capacity teacher model is trained on adversarially perturbed,
retrieval-augmented inputs to learn robust decision boundaries over diverse and
complex user queries. In the inference stage, a distillation scheduler
transfers the teacher's knowledge into a compact student model, with a
continually updated knowledge base collected online. At deployment, the compact
student model leverages top-K similar safety exemplars retrieved from the
online-updated knowledge base to enable both online and real-time malicious
query detection. Evaluations across ten safety benchmarks demonstrate that
ADRAG, with a 149M-parameter model, achieves 98.5% of WildGuard-7B's
performance, surpasses GPT-4 by 3.3% and Llama-Guard-3-8B by 9.5% on
out-of-distribution detection, while simultaneously delivering up to 5.6x lower
latency at 300 queries per second (QPS) in real-time applications.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.14608v1">Enterprise AI Must Enforce Participant-Aware Access Control</a></td><td><details><summary>展开</summary>Large language models (LLMs) are increasingly deployed in enterprise settings
where they interact with multiple users and are trained or fine-tuned on
sensitive internal data. While fine-tuning enhances performance by
internalizing domain knowledge, it also introduces a critical security risk:
leakage of confidential training data to unauthorized users. These risks are
exacerbated when LLMs are combined with Retrieval-Augmented Generation (RAG)
pipelines that dynamically fetch contextual documents at inference time.
  We demonstrate data exfiltration attacks on AI assistants where adversaries
can exploit current fine-tuning and RAG architectures to leak sensitive
information by leveraging the lack of access control enforcement. We show that
existing defenses, including prompt sanitization, output filtering, system
isolation, and training-level privacy mechanisms, are fundamentally
probabilistic and fail to offer robust protection against such attacks.
  We take the position that only a deterministic and rigorous enforcement of
fine-grained access control during both fine-tuning and RAG-based inference can
reliably prevent the leakage of sensitive data to unauthorized recipients.
  We introduce a framework centered on the principle that any content used in
training, retrieval, or generation by an LLM is explicitly authorized for
\emph{all users involved in the interaction}. Our approach offers a simple yet
powerful paradigm shift for building secure multi-user LLM systems that are
grounded in classical access control but adapted to the unique challenges of
modern AI workflows. Our solution has been deployed in Microsoft Copilot
Tuning, a product offering that enables organizations to fine-tune models using
their own enterprise-specific data.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.14589v1">ATLANTIS: AI-driven Threat Localization, Analysis, and Triage Intelligence System</a></td><td><details><summary>展开</summary>We present ATLANTIS, the cyber reasoning system developed by Team Atlanta
that won 1st place in the Final Competition of DARPA's AI Cyber Challenge
(AIxCC) at DEF CON 33 (August 2025). AIxCC (2023-2025) challenged teams to
build autonomous cyber reasoning systems capable of discovering and patching
vulnerabilities at the speed and scale of modern software. ATLANTIS integrates
large language models (LLMs) with program analysis -- combining symbolic
execution, directed fuzzing, and static analysis -- to address limitations in
automated vulnerability discovery and program repair. Developed by researchers
at Georgia Institute of Technology, Samsung Research, KAIST, and POSTECH, the
system addresses core challenges: scaling across diverse codebases from C to
Java, achieving high precision while maintaining broad coverage, and producing
semantically correct patches that preserve intended behavior. We detail the
design philosophy, architectural decisions, and implementation strategies
behind ATLANTIS, share lessons learned from pushing the boundaries of automated
security when program analysis meets modern AI, and release artifacts to
support reproducibility and future research.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.14547v1">(P)rior(D)yna(F)low: A Priori Dynamic Workflow Construction via Multi-Agent Collaboration</a></td><td><details><summary>展开</summary>Recent studies have shown that carefully designed workflows coordinating
large language models(LLMs) significantly enhance task-solving capabilities
compared to using a single model. While an increasing number of works focus on
autonomous workflow construction, most existing approaches rely solely on
historical experience, leading to limitations in efficiency and adaptability.
We argue that while historical experience is valuable, workflow construction
should also flexibly respond to the unique characteristics of each task. To
this end, we propose an a priori dynamic framework for automated workflow
construction. Our framework first leverages Q-table learning to optimize the
decision space, guiding agent decisions and enabling effective use of
historical experience. At the same time, agents evaluate the current task
progress and make a priori decisions regarding the next executing agent,
allowing the system to proactively select the more suitable workflow structure
for each given task. Additionally, we incorporate mechanisms such as cold-start
initialization, early stopping, and pruning to further improve system
efficiency. Experimental evaluations on four benchmark datasets demonstrate the
feasibility and effectiveness of our approach. Compared to state-of-the-art
baselines, our method achieves an average improvement of 4.05%, while reducing
workflow construction and inference costs to only 30.68%-48.31% of those
required by existing methods.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.14532v1">Leveraging Artificial Intelligence as a Strategic Growth Catalyst for Small and Medium-sized Enterprises</a></td><td><details><summary>展开</summary>Artificial Intelligence (AI) has transitioned from a futuristic concept
reserved for large corporations to a present-day, accessible, and essential
growth lever for Small and Medium-sized Enterprises (SMEs). For entrepreneurs
and business leaders, strategic AI adoption is no longer an option but an
imperative for competitiveness, operational efficiency, and long-term survival.
This report provides a comprehensive framework for SME leaders to navigate this
technological shift, offering the foundational knowledge, business case,
practical applications, and strategic guidance necessary to harness the power
of AI. The quantitative evidence supporting AI adoption is compelling; 91% of
SMEs using AI report that it directly boosts their revenue. Beyond top-line
growth, AI drives profound operational efficiencies, with studies showing it
can reduce operational costs by up to 30% and save businesses more than 20
hours of valuable time each month. This transformation is occurring within the
context of a seismic economic shift; the global AI market is projected to surge
from $233.46 Billion in 2024 to an astonishing $1.77 Trillion by 2032. This
paper demystifies the core concepts of AI, presents a business case based on
market data, details practical applications, and lays out a phased, actionable
adoption strategy.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.14526v1">Delta Knowledge Distillation for Large Language Models</a></td><td><details><summary>展开</summary>Knowledge distillation (KD) is a widely adopted approach for compressing
large neural networks by transferring knowledge from a large teacher model to a
smaller student model. In the context of large language models, token level KD,
typically minimizing the KL divergence between student output distribution and
teacher output distribution, has shown strong empirical performance. However,
prior work assumes student output distribution and teacher output distribution
share the same optimal representation space, a premise that may not hold in
many cases. To solve this problem, we propose Delta Knowledge Distillation
(Delta-KD), a novel extension of token level KD that encourages the student to
approximate an optimal representation space by explicitly preserving the
distributional shift Delta introduced during the teacher's supervised
finetuning (SFT). Empirical results on ROUGE metrics demonstrate that Delta KD
substantially improves student performance while preserving more of the
teacher's knowledge.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.14519v1">BEACON: Behavioral Malware Classification with Large Language Model Embeddings and Deep Learning</a></td><td><details><summary>展开</summary>Malware is becoming increasingly complex and widespread, making it essential
to develop more effective and timely detection methods. Traditional static
analysis often fails to defend against modern threats that employ code
obfuscation, polymorphism, and other evasion techniques. In contrast,
behavioral malware detection, which monitors runtime activities, provides a
more reliable and context-aware solution. In this work, we propose BEACON, a
novel deep learning framework that leverages large language models (LLMs) to
generate dense, contextual embeddings from raw sandbox-generated behavior
reports. These embeddings capture semantic and structural patterns of each
sample and are processed by a one-dimensional convolutional neural network (1D
CNN) for multi-class malware classification. Evaluated on the Avast-CTU Public
CAPE Dataset, our framework consistently outperforms existing methods,
highlighting the effectiveness of LLM-based behavioral embeddings and the
overall design of BEACON for robust malware classification.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.14507v1">DeKeyNLU: Enhancing Natural Language to SQL Generation through Task Decomposition and Keyword Extraction</a></td><td><details><summary>展开</summary>Natural Language to SQL (NL2SQL) provides a new model-centric paradigm that
simplifies database access for non-technical users by converting natural
language queries into SQL commands. Recent advancements, particularly those
integrating Retrieval-Augmented Generation (RAG) and Chain-of-Thought (CoT)
reasoning, have made significant strides in enhancing NL2SQL performance.
However, challenges such as inaccurate task decomposition and keyword
extraction by LLMs remain major bottlenecks, often leading to errors in SQL
generation. While existing datasets aim to mitigate these issues by fine-tuning
models, they struggle with over-fragmentation of tasks and lack of
domain-specific keyword annotations, limiting their effectiveness. To address
these limitations, we present DeKeyNLU, a novel dataset which contains 1,500
meticulously annotated QA pairs aimed at refining task decomposition and
enhancing keyword extraction precision for the RAG pipeline. Fine-tuned with
DeKeyNLU, we propose DeKeySQL, a RAG-based NL2SQL pipeline that employs three
distinct modules for user question understanding, entity retrieval, and
generation to improve SQL generation accuracy. We benchmarked multiple model
configurations within DeKeySQL RAG pipeline. Experimental results demonstrate
that fine-tuning with DeKeyNLU significantly improves SQL generation accuracy
on both BIRD (62.31% to 69.10%) and Spider (84.2% to 88.7%) dev datasets.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.14504v1">Introducing OmniGEC: A Silver Multilingual Dataset for Grammatical Error Correction</a></td><td><details><summary>展开</summary>In this paper, we introduce OmniGEC, a collection of multilingual
silver-standard datasets for the task of Grammatical Error Correction (GEC),
covering eleven languages: Czech, English, Estonian, German, Greek, Icelandic,
Italian, Latvian, Slovene, Swedish, and Ukrainian. These datasets facilitate
the development of multilingual GEC solutions and help bridge the data gap in
adapting English GEC solutions to multilingual GEC. The texts in the datasets
originate from three sources: Wikipedia edits for the eleven target languages,
subreddits from Reddit in the eleven target languages, and the Ukrainian-only
UberText 2.0 social media corpus. While Wikipedia edits were derived from
human-made corrections, the Reddit and UberText 2.0 data were automatically
corrected with the GPT-4o-mini model. The quality of the corrections in the
datasets was evaluated both automatically and manually. Finally, we fine-tune
two open-source large language models - Aya-Expanse (8B) and Gemma-3 (12B) - on
the multilingual OmniGEC corpora and achieve state-of-the-art (SOTA) results
for paragraph-level multilingual GEC. The dataset collection and the
best-performing models are available on Hugging Face.</details></td></tr></tbody></table>

### 📅 2025-09-17
<table style='width:100%;'><colgroup><col style="width:61.8%;"><col style="width:38.2%;"></colgroup><thead><tr><th>title</th><th>abstract</th></tr></thead><tbody><tr><td><a href="http://arxiv.org/abs/2509.14233v1">Apertus: Democratizing Open and Compliant LLMs for Global Language Environments</a></td><td><details><summary>展开</summary>We present Apertus, a fully open suite of large language models (LLMs)
designed to address two systemic shortcomings in today's open model ecosystem:
data compliance and multilingual representation. Unlike many prior models that
release weights without reproducible data pipelines or regard for content-owner
rights, Apertus models are pretrained exclusively on openly available data,
retroactively respecting robots.txt exclusions and filtering for
non-permissive, toxic, and personally identifiable content. To mitigate risks
of memorization, we adopt the Goldfish objective during pretraining, strongly
suppressing verbatim recall of data while retaining downstream task
performance. The Apertus models also expand multilingual coverage, training on
15T tokens from over 1800 languages, with ~40% of pretraining data allocated to
non-English content. Released at 8B and 70B scales, Apertus approaches
state-of-the-art results among fully open models on multilingual benchmarks,
rivalling or surpassing open-weight counterparts. Beyond model weights, we
release all scientific artifacts from our development cycle with a permissive
license, including data preparation scripts, checkpoints, evaluation suites,
and training code, enabling transparent audit and extension.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.14223v1">Language models' activations linearly encode training-order recency</a></td><td><details><summary>展开</summary>We show that language models' activations linearly encode when information
was learned during training. Our setup involves creating a model with a known
training order by sequentially fine-tuning Llama-3.2-1B on six disjoint but
otherwise similar datasets about named entities. We find that the average
activations of test samples for the six training datasets encode the training
order: when projected into a 2D subspace, these centroids are arranged exactly
in the order of training and lie on a straight line. Further, we show that
linear probes can accurately (~90%) distinguish "early" vs. "late" entities,
generalizing to entities unseen during the probes' own training. The model can
also be fine-tuned to explicitly report an unseen entity's training stage (~80%
accuracy). Interestingly, this temporal signal does not seem attributable to
simple differences in activation magnitudes, losses, or model confidence. Our
paper demonstrates that models are capable of differentiating information by
its acquisition time, and carries significant implications for how they might
manage conflicting data and respond to knowledge modifications.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.14093v1">Reasoning Efficiently Through Adaptive Chain-of-Thought Compression: A Self-Optimizing Framework</a></td><td><details><summary>展开</summary>Chain-of-Thought (CoT) reasoning enhances Large Language Models (LLMs) by
prompting intermediate steps, improving accuracy and robustness in arithmetic,
logic, and commonsense tasks. However, this benefit comes with high
computational costs: longer outputs increase latency, memory usage, and
KV-cache demands. These issues are especially critical in software engineering
tasks where concise and deterministic outputs are required. To investigate
these trade-offs, we conduct an empirical study based on code generation
benchmarks. The results reveal that longer CoT does not always help. Excessive
reasoning often causes truncation, accuracy drops, and latency up to five times
higher, with failed outputs consistently longer than successful ones. These
findings challenge the assumption that longer reasoning is inherently better
and highlight the need for adaptive CoT control. Motivated by this, we propose
SEER (Self-Enhancing Efficient Reasoning), an adaptive framework that
compresses CoT while preserving accuracy. SEER combines Best-of-N sampling with
task-aware adaptive filtering, dynamically adjusting thresholds based on
pre-inference outputs to reduce verbosity and computational overhead. We then
evaluate SEER on three software engineering tasks and one math task. On
average, SEER shortens CoT by 42.1%, improves accuracy by reducing truncation,
and eliminates most infinite loops. These results demonstrate SEER as a
practical method to make CoT-enhanced LLMs more efficient and robust, even
under resource constraints.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.14036v1">SSL-SSAW: Self-Supervised Learning with Sigmoid Self-Attention Weighting for Question-Based Sign Language Translation</a></td><td><details><summary>展开</summary>Sign Language Translation (SLT) bridges the communication gap between deaf
people and hearing people, where dialogue provides crucial contextual cues to
aid in translation. Building on this foundational concept, this paper proposes
Question-based Sign Language Translation (QB-SLT), a novel task that explores
the efficient integration of dialogue. Unlike gloss (sign language
transcription) annotations, dialogue naturally occurs in communication and is
easier to annotate. The key challenge lies in aligning multimodality features
while leveraging the context of the question to improve translation. To address
this issue, we propose a cross-modality Self-supervised Learning with Sigmoid
Self-attention Weighting (SSL-SSAW) fusion method for sign language
translation. Specifically, we employ contrastive learning to align
multimodality features in QB-SLT, then introduce a Sigmoid Self-attention
Weighting (SSAW) module for adaptive feature extraction from question and sign
language sequences. Additionally, we leverage available question text through
self-supervised learning to enhance representation and translation
capabilities. We evaluated our approach on newly constructed CSL-Daily-QA and
PHOENIX-2014T-QA datasets, where SSL-SSAW achieved SOTA performance. Notably,
easily accessible question assistance can achieve or even surpass the
performance of gloss assistance. Furthermore, visualization results demonstrate
the effectiveness of incorporating dialogue in improving translation quality.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.14031v1">You Are What You Train: Effects of Data Composition on Training Context-aware Machine Translation Models</a></td><td><details><summary>展开</summary>Achieving human-level translations requires leveraging context to ensure
coherence and handle complex phenomena like pronoun disambiguation. Sparsity of
contextually rich examples in the standard training data has been hypothesized
as the reason for the difficulty of context utilization. In this work, we
systematically validate this claim in both single- and multilingual settings by
constructing training datasets with a controlled proportions of contextually
relevant examples. We demonstrate a strong association between training data
sparsity and model performance confirming sparsity as a key bottleneck.
Importantly, we reveal that improvements in one contextual phenomenon do no
generalize to others. While we observe some cross-lingual transfer, it is not
significantly higher between languages within the same sub-family. Finally, we
propose and empirically evaluate two training strategies designed to leverage
the available data. These strategies improve context utilization, resulting in
accuracy gains of up to 6 and 8 percentage points on the ctxPro evaluation in
single- and multilingual settings respectively.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.14030v1">CrowdAgent: Multi-Agent Managed Multi-Source Annotation System</a></td><td><details><summary>展开</summary>High-quality annotated data is a cornerstone of modern Natural Language
Processing (NLP). While recent methods begin to leverage diverse annotation
sources-including Large Language Models (LLMs), Small Language Models (SLMs),
and human experts-they often focus narrowly on the labeling step itself. A
critical gap remains in the holistic process control required to manage these
sources dynamically, addressing complex scheduling and quality-cost trade-offs
in a unified manner. Inspired by real-world crowdsourcing companies, we
introduce CrowdAgent, a multi-agent system that provides end-to-end process
control by integrating task assignment, data annotation, and quality/cost
management. It implements a novel methodology that rationally assigns tasks,
enabling LLMs, SLMs, and human experts to advance synergistically in a
collaborative annotation workflow. We demonstrate the effectiveness of
CrowdAgent through extensive experiments on six diverse multimodal
classification tasks. The source code and video demo are available at
https://github.com/QMMMS/CrowdAgent.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.14001v1">MOCHA: Multi-modal Objects-aware Cross-arcHitecture Alignment</a></td><td><details><summary>展开</summary>We introduce MOCHA (Multi-modal Objects-aware Cross-arcHitecture Alignment),
a knowledge distillation approach that transfers region-level multimodal
semantics from a large vision-language teacher (e.g., LLaVa) into a lightweight
vision-only object detector student (e.g., YOLO). A translation module maps
student features into a joint space, where the training of the student and
translator is guided by a dual-objective loss that enforces both local
alignment and global relational consistency. Unlike prior approaches focused on
dense or global alignment, MOCHA operates at the object level, enabling
efficient transfer of semantics without modifying the teacher or requiring
textual input at inference. We validate our method across four personalized
detection benchmarks under few-shot regimes. Results show consistent gains over
baselines, with a +10.1 average score improvement. Despite its compact
architecture, MOCHA reaches performance on par with larger multimodal models,
proving its suitability for real-world deployment.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.13978v1">LLM Agents for Interactive Workflow Provenance: Reference Architecture and Evaluation Methodology</a></td><td><details><summary>展开</summary>Modern scientific discovery increasingly relies on workflows that process
data across the Edge, Cloud, and High Performance Computing (HPC) continuum.
Comprehensive and in-depth analyses of these data are critical for hypothesis
validation, anomaly detection, reproducibility, and impactful findings.
Although workflow provenance techniques support such analyses, at large scale,
the provenance data become complex and difficult to analyze. Existing systems
depend on custom scripts, structured queries, or static dashboards, limiting
data interaction. In this work, we introduce an evaluation methodology,
reference architecture, and open-source implementation that leverages
interactive Large Language Model (LLM) agents for runtime data analysis. Our
approach uses a lightweight, metadata-driven design that translates natural
language into structured provenance queries. Evaluations across LLaMA, GPT,
Gemini, and Claude, covering diverse query classes and a real-world chemistry
workflow, show that modular design, prompt tuning, and Retrieval-Augmented
Generation (RAG) enable accurate and insightful LLM agent responses beyond
recorded provenance.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.13926v1">MAP: End-to-End Autonomous Driving with Map-Assisted Planning</a></td><td><details><summary>展开</summary>In recent years, end-to-end autonomous driving has attracted increasing
attention for its ability to jointly model perception, prediction, and planning
within a unified framework. However, most existing approaches underutilize the
online mapping module, leaving its potential to enhance trajectory planning
largely untapped. This paper proposes MAP (Map-Assisted Planning), a novel
map-assisted end-to-end trajectory planning framework. MAP explicitly
integrates segmentation-based map features and the current ego status through a
Plan-enhancing Online Mapping module, an Ego-status-guided Planning module, and
a Weight Adapter based on current ego status. Experiments conducted on the
DAIR-V2X-seq-SPD dataset demonstrate that the proposed method achieves a 16.6%
reduction in L2 displacement error, a 56.2% reduction in off-road rate, and a
44.5% improvement in overall score compared to the UniV2X baseline, even
without post-processing. Furthermore, it achieves top ranking in Track 2 of the
End-to-End Autonomous Driving through V2X Cooperation Challenge of MEIS
Workshop @CVPR2025, outperforming the second-best model by 39.5% in terms of
overall score. These results highlight the effectiveness of explicitly
leveraging semantic map features in planning and suggest new directions for
improving structure design in end-to-end autonomous driving systems. Our code
is available at https://gitee.com/kymkym/map.git</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.13914v1">Ensemble of Pre-Trained Models for Long-Tailed Trajectory Prediction</a></td><td><details><summary>展开</summary>This work explores the application of ensemble modeling to the
multidimensional regression problem of trajectory prediction for vehicles in
urban environments. As newer and bigger state-of-the-art prediction models for
autonomous driving continue to emerge, an important open challenge is the
problem of how to combine the strengths of these big models without the need
for costly re-training. We show how, perhaps surprisingly, combining
state-of-the-art deep learning models out-of-the-box (without retraining or
fine-tuning) with a simple confidence-weighted average method can enhance the
overall prediction. Indeed, while combining trajectory prediction models is not
straightforward, this simple approach enhances performance by 10% over the best
prediction model, especially in the long-tailed metrics. We show that this
performance improvement holds on both the NuScenes and Argoverse datasets, and
that these improvements are made across the dataset distribution. The code for
our work is open source.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.13895v1">FedSSG: Expectation-Gated and History-Aware Drift Alignment for Federated Learning</a></td><td><details><summary>展开</summary>Non-IID data and partial participation induce client drift and inconsistent
local optima in federated learning, causing unstable convergence and accuracy
loss. We present FedSSG, a stochastic sampling-guided, history-aware drift
alignment method. FedSSG maintains a per-client drift memory that accumulates
local model differences as a lightweight sketch of historical gradients;
crucially, it gates both the memory update and the local alignment term by a
smooth function of the observed/expected participation ratio (a
phase-by-expectation signal derived from the server sampler). This
statistically grounded gate stays weak and smooth when sampling noise dominates
early, then strengthens once participation statistics stabilize, contracting
the local-global gap without extra communication. Across CIFAR-10/100 with
100/500 clients and 2-15 percent participation, FedSSG consistently outperforms
strong drift-aware baselines and accelerates convergence; on our benchmarks it
improves test accuracy by up to a few points (e.g., about +0.9 on CIFAR-10 and
about +2.7 on CIFAR-100 on average over the top-2 baseline) and yields about
4.5x faster target-accuracy convergence on average. The method adds only O(d)
client memory and a constant-time gate, and degrades gracefully to a mild
regularizer under near-IID or uniform sampling. FedSSG shows that sampling
statistics can be turned into a principled, history-aware phase control to
stabilize and speed up federated training.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.13773v1">MIRA: Empowering One-Touch AI Services on Smartphones with MLLM-based Instruction Recommendation</a></td><td><details><summary>展开</summary>The rapid advancement of generative AI technologies is driving the
integration of diverse AI-powered services into smartphones, transforming how
users interact with their devices. To simplify access to predefined AI
services, this paper introduces MIRA, a pioneering framework for task
instruction recommendation that enables intuitive one-touch AI tasking on
smartphones. With MIRA, users can long-press on images or text objects to
receive contextually relevant instruction recommendations for executing AI
tasks. Our work introduces three key innovations: 1) A multimodal large
language model (MLLM)-based recommendation pipeline with structured reasoning
to extract key entities, infer user intent, and generate precise instructions;
2) A template-augmented reasoning mechanism that integrates high-level
reasoning templates, enhancing task inference accuracy; 3) A prefix-tree-based
constrained decoding strategy that restricts outputs to predefined instruction
candidates, ensuring coherent and intent-aligned suggestions. Through
evaluation using a real-world annotated datasets and a user study, MIRA has
demonstrated substantial improvements in the accuracy of instruction
recommendation. The encouraging results highlight MIRA's potential to
revolutionize the way users engage with AI services on their smartphones,
offering a more seamless and efficient experience.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.13761v1">THOR: Tool-Integrated Hierarchical Optimization via RL for Mathematical Reasoning</a></td><td><details><summary>展开</summary>Large Language Models (LLMs) have made remarkable progress in mathematical
reasoning, but still continue to struggle with high-precision tasks like
numerical computation and formal symbolic manipulation. Integrating external
tools has emerged as a promising approach to bridge this gap. Despite recent
advances, existing methods struggle with three key challenges: constructing
tool-integrated reasoning data, performing fine-grained optimization, and
enhancing inference. To overcome these limitations, we propose THOR
(Tool-Integrated Hierarchical Optimization via RL). First, we introduce TIRGen,
a multi-agent actor-critic-based pipeline for constructing high-quality
datasets of tool-integrated reasoning paths, aligning with the policy and
generalizing well across diverse models. Second, to perform fine-grained
hierarchical optimization, we introduce an RL strategy that jointly optimizes
for both trajectory-level problem solving and step-level code generation. This
is motivated by our key insight that the success of an intermediate tool call
is a strong predictor of the final answer's correctness. Finally, THOR
incorporates a self-correction mechanism that leverages immediate tool feedback
to dynamically revise erroneous reasoning paths during inference. Our approach
demonstrates strong generalization across diverse models, performing
effectively in both reasoning and non-reasoning models. It further achieves
state-of-the-art performance for models of a similar scale on multiple
mathematical benchmarks, while also delivering consistent improvements on code
benchmarks. Our code will be publicly available at
https://github.com/JingMog/THOR.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.13722v1">Mitigating Query Selection Bias in Referring Video Object Segmentation</a></td><td><details><summary>展开</summary>Recently, query-based methods have achieved remarkable performance in
Referring Video Object Segmentation (RVOS) by using textual static object
queries to drive cross-modal alignment. However, these static queries are
easily misled by distractors with similar appearance or motion, resulting in
\emph{query selection bias}. To address this issue, we propose Triple Query
Former (TQF), which factorizes the referring query into three specialized
components: an appearance query for static attributes, an intra-frame
interaction query for spatial relations, and an inter-frame motion query for
temporal association. Instead of relying solely on textual embeddings, our
queries are dynamically constructed by integrating both linguistic cues and
visual guidance. Furthermore, we introduce two motion-aware aggregation modules
that enhance object token representations: Intra-frame Interaction Aggregation
incorporates position-aware interactions among objects within a single frame,
while Inter-frame Motion Aggregation leverages trajectory-guided alignment
across frames to ensure temporal coherence. Extensive experiments on multiple
RVOS benchmarks demonstrate the advantages of TQF and the effectiveness of our
structured query design and motion-aware aggregation modules.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.13702v1">DSCC-HS: A Dynamic Self-Reinforcing Framework for Hallucination Suppression in Large Language Models</a></td><td><details><summary>展开</summary>Large Language Model (LLM) hallucination is a significant barrier to their
reliable deployment. Current methods like Retrieval-Augmented Generation (RAG)
are often reactive. We introduce **Dynamic Self-reinforcing Calibration for
Hallucination Suppression (DSCC-HS)**, a novel, proactive framework that
intervenes during autoregressive decoding. Inspired by dual-process cognitive
theory, DSCC-HS uses a compact proxy model, trained in adversarial roles as a
Factual Alignment Proxy (FAP) and a Hallucination Detection Proxy (HDP). During
inference, these proxies dynamically steer a large target model by injecting a
real-time steering vector, which is the difference between FAP and HDP logits,
at each decoding step. This plug-and-play approach requires no modification to
the target model. Our experiments on TruthfulQA and BioGEN show DSCC-HS
achieves state-of-the-art performance. On TruthfulQA, it reached a 99.2%
Factual Consistency Rate (FCR). On the long-form BioGEN benchmark, it attained
the highest FActScore of 46.50. These results validate DSCC-HS as a principled
and efficient solution for enhancing LLM factuality.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.13688v1">CraftMesh: High-Fidelity Generative Mesh Manipulation via Poisson Seamless Fusion</a></td><td><details><summary>展开</summary>Controllable, high-fidelity mesh editing remains a significant challenge in
3D content creation. Existing generative methods often struggle with complex
geometries and fail to produce detailed results. We propose CraftMesh, a novel
framework for high-fidelity generative mesh manipulation via Poisson Seamless
Fusion. Our key insight is to decompose mesh editing into a pipeline that
leverages the strengths of 2D and 3D generative models: we edit a 2D reference
image, then generate a region-specific 3D mesh, and seamlessly fuse it into the
original model. We introduce two core techniques: Poisson Geometric Fusion,
which utilizes a hybrid SDF/Mesh representation with normal blending to achieve
harmonious geometric integration, and Poisson Texture Harmonization for
visually consistent texture blending. Experimental results demonstrate that
CraftMesh outperforms state-of-the-art methods, delivering superior global
consistency and local detail in complex editing tasks.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.13676v1">Re-purposing SAM into Efficient Visual Projectors for MLLM-Based Referring Image Segmentation</a></td><td><details><summary>展开</summary>Recently, Referring Image Segmentation (RIS) frameworks that pair the
Multimodal Large Language Model (MLLM) with the Segment Anything Model (SAM)
have achieved impressive results. However, adapting MLLM to segmentation is
computationally intensive, primarily due to visual token redundancy. We observe
that traditional patch-wise visual projectors struggle to strike a balance
between reducing the number of visual tokens and preserving semantic clarity,
often retaining overly long token sequences to avoid performance drops.
Inspired by text tokenizers, we propose a novel semantic visual projector that
leverages semantic superpixels generated by SAM to identify "visual words" in
an image. By compressing and projecting semantic superpixels as visual tokens,
our approach adaptively shortens the token sequence according to scene
complexity while minimizing semantic loss in compression. To mitigate loss of
information, we propose a semantic superpixel positional embedding to
strengthen MLLM's awareness of superpixel geometry and position, alongside a
semantic superpixel aggregator to preserve both fine-grained details inside
superpixels and global context outside. Experiments show that our method cuts
visual tokens by 93% without compromising performance, notably speeding up MLLM
training and inference, and outperforming existing compressive visual
projectors on RIS.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.13666v1">DREAM: Domain-aware Reasoning for Efficient Autonomous Underwater Monitoring</a></td><td><details><summary>展开</summary>The ocean is warming and acidifying, increasing the risk of mass mortality
events for temperature-sensitive shellfish such as oysters. This motivates the
development of long-term monitoring systems. However, human labor is costly and
long-duration underwater work is highly hazardous, thus favoring robotic
solutions as a safer and more efficient option. To enable underwater robots to
make real-time, environment-aware decisions without human intervention, we must
equip them with an intelligent "brain." This highlights the need for
persistent,wide-area, and low-cost benthic monitoring. To this end, we present
DREAM, a Vision Language Model (VLM)-guided autonomy framework for long-term
underwater exploration and habitat monitoring. The results show that our
framework is highly efficient in finding and exploring target objects (e.g.,
oysters, shipwrecks) without prior location information. In the
oyster-monitoring task, our framework takes 31.5% less time than the previous
baseline with the same amount of oysters. Compared to the vanilla VLM, it uses
23% fewer steps while covering 8.88% more oysters. In shipwreck scenes, our
framework successfully explores and maps the wreck without collisions,
requiring 27.5% fewer steps than the vanilla model and achieving 100% coverage,
while the vanilla model achieves 60.23% average coverage in our shipwreck
environments.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.13633v1">DeepLogit: A sequentially constrained explainable deep learning modeling approach for transport policy analysis</a></td><td><details><summary>展开</summary>Despite the significant progress of deep learning models in multitude of
applications, their adaption in planning and policy related areas remains
challenging due to the black-box nature of these models. In this work, we
develop a set of DeepLogit models that follow a novel sequentially constrained
approach in estimating deep learning models for transport policy analysis. In
the first step of the proposed approach, we estimate a convolutional neural
network (CNN) model with only linear terms, which is equivalent of a
linear-in-parameter multinomial logit model. We then estimate other deep
learning models by constraining the parameters that need interpretability at
the values obtained in the linear-in-parameter CNN model and including higher
order terms or by introducing advanced deep learning architectures like
Transformers. Our approach can retain the interpretability of the selected
parameters, yet provides significantly improved model accuracy than the
discrete choice model. We demonstrate our approach on a transit route choice
example using real-world transit smart card data from Singapore. This study
shows the potential for a unifying approach, where theory-based discrete choice
model (DCM) and data-driven AI models can leverage each other's strengths in
interpretability and predictive power. With the availability of larger datasets
and more complex constructions, such approach can lead to more accurate models
using discrete choice models while maintaining its applicability in planning
and policy-related areas. Our code is available on
https://github.com/jeremyoon/route-choice/ .</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.13626v1">Mind the Gap: Aligning Knowledge Bases with User Needs to Enhance Mental Health Retrieval</a></td><td><details><summary>展开</summary>Access to reliable mental health information is vital for early help-seeking,
yet expanding knowledge bases is resource-intensive and often misaligned with
user needs. This results in poor performance of retrieval systems when
presented concerns are not covered or expressed in informal or contextualized
language. We present an AI-based gap-informed framework for corpus augmentation
that authentically identifies underrepresented topics (gaps) by overlaying
naturalistic user data such as forum posts in order to prioritize expansions
based on coverage and usefulness. In a case study, we compare Directed
(gap-informed augmentations) with Non-Directed augmentation (random additions),
evaluating the relevance and usefulness of retrieved information across four
retrieval-augmented generation (RAG) pipelines. Directed augmentation achieved
near-optimal performance with modest expansions--requiring only a 42% increase
for Query Transformation, 74% for Reranking and Hierarchical, and 318% for
Baseline--to reach ~95% of the performance of an exhaustive reference corpus.
In contrast, Non-Directed augmentation required substantially larger and thus
practically infeasible expansions to achieve comparable performance (232%,
318%, 403%, and 763%, respectively). These results show that strategically
targeted corpus growth can reduce content creation demands while sustaining
high retrieval and provision quality, offering a scalable approach for building
trusted health information repositories and supporting generative AI
applications in high-stakes domains.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.13620v1">A reduced-order derivative-informed neural operator for subsurface fluid-flow</a></td><td><details><summary>展开</summary>Neural operators have emerged as cost-effective surrogates for expensive
fluid-flow simulators, particularly in computationally intensive tasks such as
permeability inversion from time-lapse seismic data, and uncertainty
quantification. In these applications, the fidelity of the surrogate's
gradients with respect to system parameters is crucial, as the accuracy of
downstream tasks, such as optimization and Bayesian inference, relies directly
on the quality of the derivative information. Recent advances in
physics-informed methods have leveraged derivative information to improve
surrogate accuracy. However, incorporating explicit Jacobians can become
computationally prohibitive, as the complexity typically scales quadratically
with the number of input parameters. To address this limitation, we propose
DeFINO (Derivative-based Fisher-score Informed Neural Operator), a
reduced-order, derivative-informed training framework. DeFINO integrates
Fourier neural operators (FNOs) with a novel derivative-based training strategy
guided by the Fisher Information Matrix (FIM). By projecting Jacobians onto
dominant eigen-directions identified by the FIM, DeFINO captures critical
sensitivity information directly informed by observational data, significantly
reducing computational expense. We validate DeFINO through synthetic
experiments in the context of subsurface multi-phase fluid-flow, demonstrating
improvements in gradient accuracy while maintaining robust forward predictions
of underlying fluid dynamics. These results highlight DeFINO's potential to
offer practical, scalable solutions for inversion problems in complex
real-world scenarios, all at substantially reduced computational cost.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.13603v1">Modernizing Facebook Scoped Search: Keyword and Embedding Hybrid Retrieval with LLM Evaluation</a></td><td><details><summary>展开</summary>Beyond general web-scale search, social network search uniquely enables users
to retrieve information and discover potential connections within their social
context. We introduce a framework of modernized Facebook Group Scoped Search by
blending traditional keyword-based retrieval with embedding-based retrieval
(EBR) to improve the search relevance and diversity of search results. Our
system integrates semantic retrieval into the existing keyword search pipeline,
enabling users to discover more contextually relevant group posts. To
rigorously assess the impact of this blended approach, we introduce a novel
evaluation framework that leverages large language models (LLMs) to perform
offline relevance assessments, providing scalable and consistent quality
benchmarks. Our results demonstrate that the blended retrieval system
significantly enhances user engagement and search quality, as validated by both
online metrics and LLM-based evaluation. This work offers practical insights
for deploying and evaluating advanced retrieval systems in large-scale,
real-world social platforms.</details></td></tr></tbody></table>

### 📅 2025-09-16
<table style='width:100%;'><colgroup><col style="width:61.8%;"><col style="width:38.2%;"></colgroup><thead><tr><th>title</th><th>abstract</th></tr></thead><tbody><tr><td><a href="http://arxiv.org/abs/2509.13255v1">ResidualViT for Efficient Temporally Dense Video Encoding</a></td><td><details><summary>展开</summary>Several video understanding tasks, such as natural language temporal video
grounding, temporal activity localization, and audio description generation,
require "temporally dense" reasoning over frames sampled at high temporal
resolution. However, computing frame-level features for these tasks is
computationally expensive given the temporal resolution requirements. In this
paper, we make three contributions to reduce the cost of computing features for
temporally dense tasks. First, we introduce a vision transformer (ViT)
architecture, dubbed ResidualViT, that leverages the large temporal redundancy
in videos to efficiently compute temporally dense frame-level features. Our
architecture incorporates (i) learnable residual connections that ensure
temporal consistency across consecutive frames and (ii) a token reduction
module that enhances processing speed by selectively discarding temporally
redundant information while reusing weights of a pretrained foundation model.
Second, we propose a lightweight distillation strategy to approximate the
frame-level features of the original foundation model. Finally, we evaluate our
approach across four tasks and five datasets, in both zero-shot and fully
supervised settings, demonstrating significant reductions in computational cost
(up to 60%) and improvements in inference speed (up to 2.5x faster), all while
closely approximating the accuracy of the original foundation model.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.13237v1">Metacognitive Reuse: Turning Recurring LLM Reasoning Into Concise Behaviors</a></td><td><details><summary>展开</summary>Large language models (LLMs) now solve multi-step problems by emitting
extended chains of thought. During the process, they often re-derive the same
intermediate steps across problems, inflating token usage and latency. This
saturation of the context window leaves less capacity for exploration. We study
a simple mechanism that converts recurring reasoning fragments into concise,
reusable "behaviors" (name + instruction) via the model's own metacognitive
analysis of prior traces. These behaviors are stored in a "behavior handbook"
which supplies them to the model in-context at inference or distills them into
parameters via supervised fine-tuning. This approach achieves improved
test-time reasoning across three different settings - 1) Behavior-conditioned
inference: Providing the LLM relevant behaviors in-context during reasoning
reduces number of reasoning tokens by up to 46% while matching or improving
baseline accuracy; 2) Behavior-guided self-improvement: Without any parameter
updates, the model improves its own future reasoning by leveraging behaviors
from its own past problem solving attempts. This yields up to 10% higher
accuracy than a naive critique-and-revise baseline; and 3) Behavior-conditioned
SFT: SFT on behavior-conditioned reasoning traces is more effective at
converting non-reasoning models into reasoning models as compared to vanilla
SFT. Together, these results indicate that turning slow derivations into fast
procedural hints enables LLMs to remember how to reason, not just what to
conclude.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.13235v1">A Scenario-Driven Cognitive Approach to Next-Generation AI Memory</a></td><td><details><summary>展开</summary>As artificial intelligence advances toward artificial general intelligence
(AGI), the need for robust and human-like memory systems has become
increasingly evident. Current memory architectures often suffer from limited
adaptability, insufficient multimodal integration, and an inability to support
continuous learning. To address these limitations, we propose a scenario-driven
methodology that extracts essential functional requirements from representative
cognitive scenarios, leading to a unified set of design principles for
next-generation AI memory systems. Based on this approach, we introduce the
\textbf{COgnitive Layered Memory Architecture (COLMA)}, a novel framework that
integrates cognitive scenarios, memory processes, and storage mechanisms into a
cohesive design. COLMA provides a structured foundation for developing AI
systems capable of lifelong learning and human-like reasoning, thereby
contributing to the pragmatic development of AGI.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.13232v1">Single-stream Policy Optimization</a></td><td><details><summary>展开</summary>We revisit policy-gradient optimization for Large Language Models (LLMs) from
a single-stream perspective. Prevailing group-based methods like GRPO reduce
variance with on-the-fly baselines but suffer from critical flaws: frequent
degenerate groups erase learning signals, and synchronization barriers hinder
scalability. We introduce Single-stream Policy Optimization (SPO), which
eliminates these issues by design. SPO replaces per-group baselines with a
persistent, KL-adaptive value tracker and normalizes advantages globally across
the batch, providing a stable, low-variance learning signal for every sample.
Being group-free, SPO enables higher throughput and scales effectively in
long-horizon or tool-integrated settings where generation times vary.
Furthermore, the persistent value tracker naturally enables an adaptive
curriculum via prioritized sampling. Experiments using Qwen3-8B show that SPO
converges more smoothly and attains higher accuracy than GRPO, while
eliminating computation wasted on degenerate groups. Ablation studies confirm
that SPO's gains stem from its principled approach to baseline estimation and
advantage normalization, offering a more robust and efficient path for LLM
reasoning. Across five hard math benchmarks with Qwen3 8B, SPO improves the
average maj@32 by +3.4 percentage points (pp) over GRPO, driven by substantial
absolute point gains on challenging datasets, including +7.3 pp on BRUMO 25,
+4.4 pp on AIME 25, +3.3 pp on HMMT 25, and achieves consistent relative gain
in pass@$k$ across the evaluated $k$ values. SPO's success challenges the
prevailing trend of adding incidental complexity to RL algorithms, highlighting
a path where fundamental principles, not architectural workarounds, drive the
next wave of progress in LLM reasoning.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.13107v1">Hierarchical Deep Fusion Framework for Multi-dimensional Facial Forgery Detection - The 2024 Global Deepfake Image Detection Challenge</a></td><td><details><summary>展开</summary>The proliferation of sophisticated deepfake technology poses significant
challenges to digital security and authenticity. Detecting these forgeries,
especially across a wide spectrum of manipulation techniques, requires robust
and generalized models. This paper introduces the Hierarchical Deep Fusion
Framework (HDFF), an ensemble-based deep learning architecture designed for
high-performance facial forgery detection. Our framework integrates four
diverse pre-trained sub-models, Swin-MLP, CoAtNet, EfficientNetV2, and DaViT,
which are meticulously fine-tuned through a multi-stage process on the
MultiFFDI dataset. By concatenating the feature representations from these
specialized models and training a final classifier layer, HDFF effectively
leverages their collective strengths. This approach achieved a final score of
0.96852 on the competition's private leaderboard, securing the 20th position
out of 184 teams, demonstrating the efficacy of hierarchical fusion for complex
image classification tasks.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.13021v1">xOffense: An AI-driven autonomous penetration testing framework with offensive knowledge-enhanced LLMs and multi agent systems</a></td><td><details><summary>展开</summary>This work introduces xOffense, an AI-driven, multi-agent penetration testing
framework that shifts the process from labor-intensive, expert-driven manual
efforts to fully automated, machine-executable workflows capable of scaling
seamlessly with computational infrastructure. At its core, xOffense leverages a
fine-tuned, mid-scale open-source LLM (Qwen3-32B) to drive reasoning and
decision-making in penetration testing. The framework assigns specialized
agents to reconnaissance, vulnerability scanning, and exploitation, with an
orchestration layer ensuring seamless coordination across phases. Fine-tuning
on Chain-of-Thought penetration testing data further enables the model to
generate precise tool commands and perform consistent multi-step reasoning. We
evaluate xOffense on two rigorous benchmarks: AutoPenBench and
AI-Pentest-Benchmark. The results demonstrate that xOffense consistently
outperforms contemporary methods, achieving a sub-task completion rate of
79.17%, decisively surpassing leading systems such as VulnBot and PentestGPT.
These findings highlight the potential of domain-adapted mid-scale LLMs, when
embedded within structured multi-agent orchestration, to deliver superior,
cost-efficient, and reproducible solutions for autonomous penetration testing.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.12987v1">Toward PDDL Planning Copilot</a></td><td><details><summary>展开</summary>Large Language Models (LLMs) are increasingly being used as autonomous agents
capable of performing complicated tasks. However, they lack the ability to
perform reliable long-horizon planning on their own. This paper bridges this
gap by introducing the Planning Copilot, a chatbot that integrates multiple
planning tools and allows users to invoke them through instructions in natural
language. The Planning Copilot leverages the Model Context Protocol (MCP), a
recently developed standard for connecting LLMs with external tools and
systems. This approach allows using any LLM that supports MCP without
domain-specific fine-tuning. Our Planning Copilot supports common planning
tasks such as checking the syntax of planning problems, selecting an
appropriate planner, calling it, validating the plan it generates, and
simulating their execution. We empirically evaluate the ability of our Planning
Copilot to perform these tasks using three open-source LLMs. The results show
that the Planning Copilot highly outperforms using the same LLMs without the
planning tools. We also conducted a limited qualitative comparison of our tool
against Chat GPT-5, a very recent commercial LLM. Our results shows that our
Planning Copilot significantly outperforms GPT-5 despite relying on a much
smaller LLM. This suggests dedicated planning tools may be an effective way to
enable LLMs to perform planning tasks.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.12958v1">Forget What's Sensitive, Remember What Matters: Token-Level Differential Privacy in Memory Sculpting for Continual Learning</a></td><td><details><summary>展开</summary>Continual Learning (CL) models, while adept at sequential knowledge
acquisition, face significant and often overlooked privacy challenges due to
accumulating diverse information. Traditional privacy methods, like a uniform
Differential Privacy (DP) budget, indiscriminately protect all data, leading to
substantial model utility degradation and hindering CL deployment in
privacy-sensitive areas. To overcome this, we propose a privacy-enhanced
continual learning (PeCL) framework that forgets what's sensitive and remembers
what matters. Our approach first introduces a token-level dynamic Differential
Privacy strategy that adaptively allocates privacy budgets based on the
semantic sensitivity of individual tokens. This ensures robust protection for
private entities while minimizing noise injection for non-sensitive, general
knowledge. Second, we integrate a privacy-guided memory sculpting module. This
module leverages the sensitivity analysis from our dynamic DP mechanism to
intelligently forget sensitive information from the model's memory and
parameters, while explicitly preserving the task-invariant historical knowledge
crucial for mitigating catastrophic forgetting. Extensive experiments show that
PeCL achieves a superior balance between privacy preserving and model utility,
outperforming baseline models by maintaining high accuracy on previous tasks
while ensuring robust privacy.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.12939v1">Sy-FAR: Symmetry-based Fair Adversarial Robustness</a></td><td><details><summary>展开</summary>Security-critical machine-learning (ML) systems, such as face-recognition
systems, are susceptible to adversarial examples, including real-world
physically realizable attacks. Various means to boost ML's adversarial
robustness have been proposed; however, they typically induce unfair
robustness: It is often easier to attack from certain classes or groups than
from others. Several techniques have been developed to improve adversarial
robustness while seeking perfect fairness between classes. Yet, prior work has
focused on settings where security and fairness are less critical. Our insight
is that achieving perfect parity in realistic fairness-critical tasks, such as
face recognition, is often infeasible -- some classes may be highly similar,
leading to more misclassifications between them. Instead, we suggest that
seeking symmetry -- i.e., attacks from class $i$ to $j$ would be as successful
as from $j$ to $i$ -- is more tractable. Intuitively, symmetry is a desirable
because class resemblance is a symmetric relation in most domains.
Additionally, as we prove theoretically, symmetry between individuals induces
symmetry between any set of sub-groups, in contrast to other fairness notions
where group-fairness is often elusive. We develop Sy-FAR, a technique to
encourage symmetry while also optimizing adversarial robustness and extensively
evaluate it using five datasets, with three model architectures, including
against targeted and untargeted realistic attacks. The results show Sy-FAR
significantly improves fair adversarial robustness compared to state-of-the-art
methods. Moreover, we find that Sy-FAR is faster and more consistent across
runs. Notably, Sy-FAR also ameliorates another type of unfairness we discover
in this work -- target classes that adversarial examples are likely to be
classified into become significantly less vulnerable after inducing symmetry.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.12886v1">The LLM Already Knows: Estimating LLM-Perceived Question Difficulty via Hidden Representations</a></td><td><details><summary>展开</summary>Estimating the difficulty of input questions as perceived by large language
models (LLMs) is essential for accurate performance evaluation and adaptive
inference. Existing methods typically rely on repeated response sampling,
auxiliary models, or fine-tuning the target model itself, which may incur
substantial computational costs or compromise generality. In this paper, we
propose a novel approach for difficulty estimation that leverages only the
hidden representations produced by the target LLM. We model the token-level
generation process as a Markov chain and define a value function to estimate
the expected output quality given any hidden state. This allows for efficient
and accurate difficulty estimation based solely on the initial hidden state,
without generating any output tokens. Extensive experiments across both textual
and multimodal tasks demonstrate that our method consistently outperforms
existing baselines in difficulty estimation. Moreover, we apply our difficulty
estimates to guide adaptive reasoning strategies, including Self-Consistency,
Best-of-N, and Self-Refine, achieving higher inference efficiency with fewer
generated tokens.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.12849v1">AI Factories: It's time to rethink the Cloud-HPC divide</a></td><td><details><summary>展开</summary>The strategic importance of artificial intelligence is driving a global push
toward Sovereign AI initiatives. Nationwide governments are increasingly
developing dedicated infrastructures, called AI Factories (AIF), to achieve
technological autonomy and secure the resources necessary to sustain robust
local digital ecosystems.
  In Europe, the EuroHPC Joint Undertaking is investing hundreds of millions of
euros into several AI Factories, built atop existing high-performance computing
(HPC) supercomputers. However, while HPC systems excel in raw performance, they
are not inherently designed for usability, accessibility, or serving as
public-facing platforms for AI services such as inference or agentic
applications. In contrast, AI practitioners are accustomed to cloud-native
technologies like Kubernetes and object storage, tools that are often difficult
to integrate within traditional HPC environments.
  This article advocates for a dual-stack approach within supercomputers:
integrating both HPC and cloud-native technologies. Our goal is to bridge the
divide between HPC and cloud computing by combining high performance and
hardware acceleration with ease of use and service-oriented front-ends. This
convergence allows each paradigm to amplify the other. To this end, we will
study the cloud challenges of HPC (Serverless HPC) and the HPC challenges of
cloud technologies (High-performance Cloud).</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.12838v1">Multi-Robot Task Planning for Multi-Object Retrieval Tasks with Distributed On-Site Knowledge via Large Language Models</a></td><td><details><summary>展开</summary>It is crucial to efficiently execute instructions such as "Find an apple and
a banana" or "Get ready for a field trip," which require searching for multiple
objects or understanding context-dependent commands. This study addresses the
challenging problem of determining which robot should be assigned to which part
of a task when each robot possesses different situational on-site
knowledge-specifically, spatial concepts learned from the area designated to it
by the user. We propose a task planning framework that leverages large language
models (LLMs) and spatial concepts to decompose natural language instructions
into subtasks and allocate them to multiple robots. We designed a novel
few-shot prompting strategy that enables LLMs to infer required objects from
ambiguous commands and decompose them into appropriate subtasks. In our
experiments, the proposed method achieved 47/50 successful assignments,
outperforming random (28/50) and commonsense-based assignment (26/50).
Furthermore, we conducted qualitative evaluations using two actual mobile
manipulators. The results demonstrated that our framework could handle
instructions, including those involving ad hoc categories such as "Get ready
for a field trip," by successfully performing task decomposition, assignment,
sequential planning, and execution.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.12822v1">A Pressure-Based Diffusion Model for Influence Maximization on Social Networks</a></td><td><details><summary>展开</summary>In many real-world scenarios, an individual's local social network carries
significant influence over the opinions they form and subsequently propagate to
others. In this paper, we propose a novel diffusion model -- the Pressure
Threshold model (PT) -- for dynamically simulating the spread of influence
through a social network. This new model extends the popular Linear Threshold
Model (LT) by adjusting a node's outgoing influence proportional to the
influence it receives from its activated neighbors. We address the Influence
Maximization (IM) problem, which involves selecting the most effective seed
nodes to achieve maximal graph coverage after a diffusion process, and how the
problem manifests with the PT Model. Experiments conducted on real-world
networks, facilitated by enhancements to the open-source network-diffusion
Python library, CyNetDiff, demonstrate unique seed node selection for the PT
Model when compared to the LT Model. Moreover, analyses demonstrate that
densely connected networks amplify pressure effects more significantly than
sparse networks.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.12816v1">Gesture Evaluation in Virtual Reality</a></td><td><details><summary>展开</summary>Gestures are central to human communication, enriching interactions through
non-verbal expression. Virtual avatars increasingly use AI-generated gestures
to enhance life-likeness, yet evaluations have largely been confined to 2D.
Virtual Reality (VR) provides an immersive alternative that may affect how
gestures are perceived. This paper presents a comparative evaluation of
computer-generated gestures in VR and 2D, examining three models from the 2023
GENEA Challenge. Results show that gestures viewed in VR were rated slightly
higher on average, with the strongest effect observed for motion-capture "true
movement." While model rankings remained consistent across settings, VR
influenced participants' overall perception and offered unique benefits over
traditional 2D evaluation.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.12777v1">CECT-Mamba: a Hierarchical Contrast-enhanced-aware Model for Pancreatic Tumor Subtyping from Multi-phase CECT</a></td><td><details><summary>展开</summary>Contrast-enhanced computed tomography (CECT) is the primary imaging technique
that provides valuable spatial-temporal information about lesions, enabling the
accurate diagnosis and subclassification of pancreatic tumors. However, the
high heterogeneity and variability of pancreatic tumors still pose substantial
challenges for precise subtyping diagnosis. Previous methods fail to
effectively explore the contextual information across multiple CECT phases
commonly used in radiologists' diagnostic workflows, thereby limiting their
performance. In this paper, we introduce, for the first time, an automatic way
to combine the multi-phase CECT data to discriminate between pancreatic tumor
subtypes, among which the key is using Mamba with promising learnability and
simplicity to encourage both temporal and spatial modeling from multi-phase
CECT. Specifically, we propose a dual hierarchical contrast-enhanced-aware
Mamba module incorporating two novel spatial and temporal sampling sequences to
explore intra and inter-phase contrast variations of lesions. A
similarity-guided refinement module is also imposed into the temporal scanning
modeling to emphasize the learning on local tumor regions with more obvious
temporal variations. Moreover, we design the space complementary integrator and
multi-granularity fusion module to encode and aggregate the semantics across
different scales, achieving more efficient learning for subtyping pancreatic
tumors. The experimental results on an in-house dataset of 270 clinical cases
achieve an accuracy of 97.4% and an AUC of 98.6% in distinguishing between
pancreatic ductal adenocarcinoma (PDAC) and pancreatic neuroendocrine tumors
(PNETs), demonstrating its potential as a more accurate and efficient tool.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.12765v1">InfoGain-RAG: Boosting Retrieval-Augmented Generation via Document Information Gain-based Reranking and Filtering</a></td><td><details><summary>展开</summary>Retrieval-Augmented Generation (RAG) has emerged as a promising approach to
address key limitations of Large Language Models (LLMs), such as hallucination,
outdated knowledge, and lacking reference. However, current RAG frameworks
often struggle with identifying whether retrieved documents meaningfully
contribute to answer generation. This shortcoming makes it difficult to filter
out irrelevant or even misleading content, which notably impacts the final
performance. In this paper, we propose Document Information Gain (DIG), a novel
metric designed to quantify the contribution of retrieved documents to correct
answer generation. DIG measures a document's value by computing the difference
of LLM's generation confidence with and without the document augmented.
Further, we introduce InfoGain-RAG, a framework that leverages DIG scores to
train a specialized reranker, which prioritizes each retrieved document from
exact distinguishing and accurate sorting perspectives. This approach can
effectively filter out irrelevant documents and select the most valuable ones
for better answer generation. Extensive experiments across various models and
benchmarks demonstrate that InfoGain-RAG can significantly outperform existing
approaches, on both single and multiple retrievers paradigm. Specifically on
NaturalQA, it achieves the improvements of 17.9%, 4.5%, 12.5% in exact match
accuracy against naive RAG, self-reflective RAG and modern ranking-based RAG
respectively, and even an average of 15.3% increment on advanced proprietary
model GPT-4o across all datasets. These results demonstrate the feasibility of
InfoGain-RAG as it can offer a reliable solution for RAG in multiple
applications.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.12754v1">Toward Ownership Understanding of Objects: Active Question Generation with Large Language Model and Probabilistic Generative Model</a></td><td><details><summary>展开</summary>Robots operating in domestic and office environments must understand object
ownership to correctly execute instructions such as ``Bring me my cup.''
However, ownership cannot be reliably inferred from visual features alone. To
address this gap, we propose Active Ownership Learning (ActOwL), a framework
that enables robots to actively generate and ask ownership-related questions to
users. ActOwL employs a probabilistic generative model to select questions that
maximize information gain, thereby acquiring ownership knowledge efficiently to
improve learning efficiency. Additionally, by leveraging commonsense knowledge
from Large Language Models (LLM), objects are pre-classified as either shared
or owned, and only owned objects are targeted for questioning. Through
experiments in a simulated home environment and a real-world laboratory
setting, ActOwL achieved significantly higher ownership clustering accuracy
with fewer questions than baseline methods. These findings demonstrate the
effectiveness of combining active inference with LLM-guided commonsense
reasoning, advancing the capability of robots to acquire ownership knowledge
for practical and socially appropriate task execution.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.12743v1">Zero-shot Graph Reasoning via Retrieval Augmented Framework with LLMs</a></td><td><details><summary>展开</summary>We propose a new, training-free method, Graph Reasoning via Retrieval
Augmented Framework (GRRAF), that harnesses retrieval-augmented generation
(RAG) alongside the code-generation capabilities of large language models
(LLMs) to address a wide range of graph reasoning tasks. In GRRAF, the target
graph is stored in a graph database, and the LLM is prompted to generate
executable code queries that retrieve the necessary information. This approach
circumvents the limitations of existing methods that require extensive
finetuning or depend on predefined algorithms, and it incorporates an error
feedback loop with a time-out mechanism to ensure both correctness and
efficiency. Experimental evaluations on the GraphInstruct dataset reveal that
GRRAF achieves 100% accuracy on most graph reasoning tasks, including cycle
detection, bipartite graph checks, shortest path computation, and maximum flow,
while maintaining consistent token costs regardless of graph sizes. Imperfect
but still very high performance is observed on subgraph matching. Notably,
GRRAF scales effectively to large graphs with up to 10,000 nodes.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.12740v1">Deep Generative and Discriminative Digital Twin endowed with Variational Autoencoder for Unsupervised Predictive Thermal Condition Monitoring of Physical Robots in Industry 6.0 and Society 6.0</a></td><td><details><summary>展开</summary>Robots are unrelentingly used to achieve operational efficiency in Industry
4.0 along with symbiotic and sustainable assistance for the work-force in
Industry 5.0. As resilience, robustness, and well-being are required in
anti-fragile manufacturing and human-centric societal tasks, an autonomous
anticipation and adaption to thermal saturation and burns due to motors
overheating become instrumental for human safety and robot availability. Robots
are thereby expected to self-sustain their performance and deliver user
experience, in addition to communicating their capability to other agents in
advance to ensure fully automated thermally feasible tasks, and prolong their
lifetime without human intervention. However, the traditional robot shutdown,
when facing an imminent thermal saturation, inhibits productivity in factories
and comfort in the society, while cooling strategies are hard to implement
after the robot acquisition. In this work, smart digital twins endowed with
generative AI, i.e., variational autoencoders, are leveraged to manage
thermally anomalous and generate uncritical robot states. The notion of thermal
difficulty is derived from the reconstruction error of variational
autoencoders. A robot can use this score to predict, anticipate, and share the
thermal feasibility of desired motion profiles to meet requirements from
emerging applications in Industry 6.0 and Society 6.0.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.12724v1">Defense-to-Attack: Bypassing Weak Defenses Enables Stronger Jailbreaks in Vision-Language Models</a></td><td><details><summary>展开</summary>Despite their superb capabilities, Vision-Language Models (VLMs) have been
shown to be vulnerable to jailbreak attacks. While recent jailbreaks have
achieved notable progress, their effectiveness and efficiency can still be
improved. In this work, we reveal an interesting phenomenon: incorporating weak
defense into the attack pipeline can significantly enhance both the
effectiveness and the efficiency of jailbreaks on VLMs. Building on this
insight, we propose Defense2Attack, a novel jailbreak method that bypasses the
safety guardrails of VLMs by leveraging defensive patterns to guide jailbreak
prompt design. Specifically, Defense2Attack consists of three key components:
(1) a visual optimizer that embeds universal adversarial perturbations with
affirmative and encouraging semantics; (2) a textual optimizer that refines the
input using a defense-styled prompt; and (3) a red-team suffix generator that
enhances the jailbreak through reinforcement fine-tuning. We empirically
evaluate our method on four VLMs and four safety benchmarks. The results
demonstrate that Defense2Attack achieves superior jailbreak performance in a
single attempt, outperforming state-of-the-art attack methods that often
require multiple tries. Our work offers a new perspective on jailbreaking VLMs.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.12716v1">Joint AoI and Handover Optimization in Space-Air-Ground Integrated Network</a></td><td><details><summary>展开</summary>Despite the widespread deployment of terrestrial networks, providing reliable
communication services to remote areas and maintaining connectivity during
emergencies remains challenging. Low Earth orbit (LEO) satellite constellations
offer promising solutions with their global coverage capabilities and reduced
latency, yet struggle with intermittent coverage and limited communication
windows due to orbital dynamics. This paper introduces an age of information
(AoI)-aware space-air-ground integrated network (SAGIN) architecture that
leverages a high-altitude platform (HAP) as intelligent relay between the LEO
satellites and ground terminals. Our three-layer design employs hybrid
free-space optical (FSO) links for high-capacity satellite-to-HAP communication
and reliable radio frequency (RF) links for HAP-to-ground transmission, and
thus addressing the temporal discontinuity in LEO satellite coverage while
serving diverse user priorities. Specifically, we formulate a joint
optimization problem to simultaneously minimize the AoI and satellite handover
frequency through optimal transmit power distribution and satellite selection
decisions. This highly dynamic, non-convex problem with time-coupled
constraints presents significant computational challenges for traditional
approaches. To address these difficulties, we propose a novel diffusion model
(DM)-enhanced dueling double deep Q-network with action decomposition and state
transformer encoder (DD3QN-AS) algorithm that incorporates transformer-based
temporal feature extraction and employs a DM-based latent prompt generative
module to refine state-action representations through conditional denoising.
Simulation results highlight the superior performance of the proposed approach
compared with policy-based methods and some other deep reinforcement learning
(DRL) benchmarks.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.12678v1">Instance-level Randomization: Toward More Stable LLM Evaluations</a></td><td><details><summary>展开</summary>Evaluations of large language models (LLMs) suffer from instability, where
small changes of random factors such as few-shot examples can lead to drastic
fluctuations of scores and even model rankings. Moreover, different LLMs can
have different preferences for a certain setting of random factors. As a
result, using a fixed setting of random factors, which is often adopted as the
paradigm of current evaluations, can lead to potential unfair comparisons
between LLMs. To mitigate the volatility of evaluations, we first theoretically
analyze the sources of variance induced by changes in random factors. Targeting
these specific sources, we then propose the instance-level randomization (ILR)
method to reduce variance and enhance fairness in model comparisons. Instead of
using a fixed setting across the whole benchmark in a single experiment, we
randomize all factors that affect evaluation scores for every single instance,
run multiple experiments and report the averaged score. Theoretical analyses
and empirical results demonstrate that ILR can reduce the variance and unfair
comparisons caused by random factors, as well as achieve similar robustness
level with less than half computational cost compared with previous methods.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.12650v1">Leveraging Intermediate Representations of Time Series Foundation Models for Anomaly Detection</a></td><td><details><summary>展开</summary>Detecting anomalies in time series data is essential for the reliable
operation of many real-world systems. Recently, time series foundation models
(TSFMs) have emerged as a powerful tool for anomaly detection. However,
existing methods typically rely on the final layer's representations of TSFMs,
computing the anomaly score as a reconstruction or forecasting error via a
task-specific head. Instead, we propose TimeRep, a novel anomaly detection
approach that leverages the intermediate layer's representations of TSFMs,
computing the anomaly score as the distance between these representations.
Given a pre-trained TSFM, TimeRep selects the intermediate layer and
patch-token position that yield the most informative representation. TimeRep
forms a reference collection of intermediate representations from the training
data and applies a core-set strategy to reduce its size while maintaining
distributional coverage. During inference, TimeRep computes the anomaly score
for incoming data by measuring the distance between its intermediate
representations and those of the collection. To address concept drift, TimeRep
integrates an adaptation mechanism that, at inference time, augments the
collection exclusively with non-redundant intermediate representations from
incoming data. We conducted extensive experiments on the UCR Anomaly Archive,
which contains 250 univariate time series. TimeRep consistently outperforms a
broad spectrum of state-of-the-art baselines, including non-DL, DL, and
foundation model-based methods.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.12643v1">Learn to Relax with Large Language Models: Solving Nonlinear Combinatorial Optimization Problems via Bidirectional Coevolution</a></td><td><details><summary>展开</summary>Nonlinear Combinatorial Optimization Problems (NCOPs) present a formidable
computational hurdle in practice, as their nonconvex nature gives rise to
multi-modal solution spaces that defy efficient optimization. Traditional
constraint relaxation approaches rely heavily on expert-driven, iterative
design processes that lack systematic automation and scalable adaptability.
While recent Large Language Model (LLM)-based optimization methods show promise
for autonomous problem-solving, they predominantly function as passive
constraint validators rather than proactive strategy architects, failing to
handle the sophisticated constraint interactions inherent to NCOPs.To address
these limitations, we introduce the first end-to-end \textbf{Auto}mated
\textbf{C}onstraint \textbf{O}ptimization (AutoCO) method, which revolutionizes
NCOPs resolution through learning to relax with LLMs.Specifically, we leverage
structured LLM reasoning to generate constraint relaxation strategies, which
are dynamically evolving with algorithmic principles and executable code
through a unified triple-representation scheme. We further establish a novel
bidirectional (global-local) coevolution mechanism that synergistically
integrates Evolutionary Algorithms for intensive local refinement with Monte
Carlo Tree Search for systematic global strategy space exploration, ensuring
optimal balance between intensification and diversification in fragmented
solution spaces. Finally, comprehensive experiments on three challenging NCOP
benchmarks validate AutoCO's consistent effectiveness and superior performance
over the baselines.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.12633v1">CIARD: Cyclic Iterative Adversarial Robustness Distillation</a></td><td><details><summary>展开</summary>Adversarial robustness distillation (ARD) aims to transfer both performance
and robustness from teacher model to lightweight student model, enabling
resilient performance on resource-constrained scenarios. Though existing ARD
approaches enhance student model's robustness, the inevitable by-product leads
to the degraded performance on clean examples. We summarize the causes of this
problem inherent in existing methods with dual-teacher framework as: 1. The
divergent optimization objectives of dual-teacher models, i.e., the clean and
robust teachers, impede effective knowledge transfer to the student model, and
2. The iteratively generated adversarial examples during training lead to
performance deterioration of the robust teacher model. To address these
challenges, we propose a novel Cyclic Iterative ARD (CIARD) method with two key
innovations: a. A multi-teacher framework with contrastive push-loss alignment
to resolve conflicts in dual-teacher optimization objectives, and b. Continuous
adversarial retraining to maintain dynamic teacher robustness against
performance degradation from the varying adversarial examples. Extensive
experiments on CIFAR-10, CIFAR-100, and Tiny-ImageNet demonstrate that CIARD
achieves remarkable performance with an average 3.53 improvement in adversarial
defense rates across various attack scenarios and a 5.87 increase in clean
sample accuracy, establishing a new benchmark for balancing model robustness
and generalization. Our code is available at https://github.com/eminentgu/CIARD</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.12611v1">Analogy-Driven Financial Chain-of-Thought (AD-FCoT): A Prompting Approach for Financial Sentiment Analysis</a></td><td><details><summary>展开</summary>Financial news sentiment analysis is crucial for anticipating market
movements. With the rise of AI techniques such as Large Language Models (LLMs),
which demonstrate strong text understanding capabilities, there has been
renewed interest in enhancing these systems. Existing methods, however, often
struggle to capture the complex economic context of news and lack transparent
reasoning, which undermines their reliability. We propose Analogy-Driven
Financial Chain-of-Thought (AD-FCoT), a prompting framework that integrates
analogical reasoning with chain-of-thought (CoT) prompting for sentiment
prediction on historical financial news. AD-FCoT guides LLMs to draw parallels
between new events and relevant historical scenarios with known outcomes,
embedding these analogies into a structured, step-by-step reasoning chain. To
our knowledge, this is among the first approaches to explicitly combine
analogical examples with CoT reasoning in finance. Operating purely through
prompting, AD-FCoT requires no additional training data or fine-tuning and
leverages the model's internal financial knowledge to generate rationales that
mirror human analytical reasoning. Experiments on thousands of news articles
show that AD-FCoT outperforms strong baselines in sentiment classification
accuracy and achieves substantially higher correlation with market returns. Its
generated explanations also align with domain expertise, providing
interpretable insights suitable for real-world financial analysis.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.12610v1">ScaleDoc: Scaling LLM-based Predicates over Large Document Collections</a></td><td><details><summary>展开</summary>Predicates are foundational components in data analysis systems. However,
modern workloads increasingly involve unstructured documents, which demands
semantic understanding, beyond traditional value-based predicates. Given
enormous documents and ad-hoc queries, while Large Language Models (LLMs)
demonstrate powerful zero-shot capabilities, their high inference cost leads to
unacceptable overhead. Therefore, we introduce \textsc{ScaleDoc}, a novel
system that addresses this by decoupling predicate execution into an offline
representation phase and an optimized online filtering phase. In the offline
phase, \textsc{ScaleDoc} leverages a LLM to generate semantic representations
for each document. Online, for each query, it trains a lightweight proxy model
on these representations to filter the majority of documents, forwarding only
the ambiguous cases to the LLM for final decision. Furthermore,
\textsc{ScaleDoc} proposes two core innovations to achieve significant
efficiency: (1) a contrastive-learning-based framework that trains the proxy
model to generate reliable predicating decision scores; (2) an adaptive cascade
mechanism that determines the effective filtering policy while meeting specific
accuracy targets. Our evaluations across three datasets demonstrate that
\textsc{ScaleDoc} achieves over a 2$\times$ end-to-end speedup and reduces
expensive LLM invocations by up to 85\%, making large-scale semantic analysis
practical and efficient.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.12600v1">A Multimodal Foundation Model to Enhance Generalizability and Data Efficiency for Pan-cancer Prognosis Prediction</a></td><td><details><summary>展开</summary>Multimodal data provides heterogeneous information for a holistic
understanding of the tumor microenvironment. However, existing AI models often
struggle to harness the rich information within multimodal data and extract
poorly generalizable representations. Here we present MICE (Multimodal data
Integration via Collaborative Experts), a multimodal foundation model that
effectively integrates pathology images, clinical reports, and genomics data
for precise pan-cancer prognosis prediction. Instead of conventional
multi-expert modules, MICE employs multiple functionally diverse experts to
comprehensively capture both cross-cancer and cancer-specific insights.
Leveraging data from 11,799 patients across 30 cancer types, we enhanced MICE's
generalizability by coupling contrastive and supervised learning. MICE
outperformed both unimodal and state-of-the-art multi-expert-based multimodal
models, demonstrating substantial improvements in C-index ranging from 3.8% to
11.2% on internal cohorts and 5.8% to 8.8% on independent cohorts,
respectively. Moreover, it exhibited remarkable data efficiency across diverse
clinical scenarios. With its enhanced generalizability and data efficiency,
MICE establishes an effective and scalable foundation for pan-cancer prognosis
prediction, holding strong potential to personalize tailored therapies and
improve treatment outcomes.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.12592v1">Match Chat: Real Time Generative AI and Generative Computing for Tennis</a></td><td><details><summary>展开</summary>We present Match Chat, a real-time, agent-driven assistant designed to
enhance the tennis fan experience by delivering instant, accurate responses to
match-related queries. Match Chat integrates Generative Artificial Intelligence
(GenAI) with Generative Computing (GenComp) techniques to synthesize key
insights during live tennis singles matches. The system debuted at the 2025
Wimbledon Championships and the 2025 US Open, where it provided about 1 million
users with seamless access to streaming and static data through natural
language queries. The architecture is grounded in an Agent-Oriented
Architecture (AOA) combining rule engines, predictive models, and agents to
pre-process and optimize user queries before passing them to GenAI components.
The Match Chat system had an answer accuracy of 92.83% with an average response
time of 6.25 seconds under loads of up to 120 requests per second (RPS). Over
96.08% of all queries were guided using interactive prompt design, contributing
to a user experience that prioritized clarity, responsiveness, and minimal
effort. The system was designed to mask architectural complexity, offering a
frictionless and intuitive interface that required no onboarding or technical
familiarity. Across both Grand Slam deployments, Match Chat maintained 100%
uptime and supported nearly 1 million unique users, underscoring the
scalability and reliability of the platform. This work introduces key design
patterns for real-time, consumer-facing AI systems that emphasize speed,
precision, and usability that highlights a practical path for deploying
performant agentic systems in dynamic environments.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.12589v1">Redefining CX with Agentic AI: Minerva CQ Case Study</a></td><td><details><summary>展开</summary>Despite advances in AI for contact centers, customer experience (CX)
continues to suffer from high average handling time (AHT), low first-call
resolution, and poor customer satisfaction (CSAT). A key driver is the
cognitive load on agents, who must navigate fragmented systems, troubleshoot
manually, and frequently place customers on hold. Existing AI-powered
agent-assist tools are often reactive driven by static rules, simple prompting,
or retrieval-augmented generation (RAG) without deeper contextual reasoning. We
introduce Agentic AI goal-driven, autonomous, tool-using systems that
proactively support agents in real time. Unlike conventional approaches,
Agentic AI identifies customer intent, triggers modular workflows, maintains
evolving context, and adapts dynamically to conversation state. This paper
presents a case study of Minerva CQ, a real-time Agent Assist product deployed
in voice-based customer support. Minerva CQ integrates real-time transcription,
intent and sentiment detection, entity recognition, contextual retrieval,
dynamic customer profiling, and partial conversational summaries enabling
proactive workflows and continuous context-building. Deployed in live
production, Minerva CQ acts as an AI co-pilot, delivering measurable
improvements in agent efficiency and customer experience across multiple
deployments.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.12531v1">Pre-trained Visual Representations Generalize Where it Matters in Model-Based Reinforcement Learning</a></td><td><details><summary>展开</summary>In visuomotor policy learning, the control policy for the robotic agent is
derived directly from visual inputs. The typical approach, where a policy and
vision encoder are trained jointly from scratch, generalizes poorly to novel
visual scene changes. Using pre-trained vision models (PVMs) to inform a policy
network improves robustness in model-free reinforcement learning (MFRL). Recent
developments in Model-based reinforcement learning (MBRL) suggest that MBRL is
more sample-efficient than MFRL. However, counterintuitively, existing work has
found PVMs to be ineffective in MBRL. Here, we investigate PVM's effectiveness
in MBRL, specifically on generalization under visual domain shifts. We show
that, in scenarios with severe shifts, PVMs perform much better than a baseline
model trained from scratch. We further investigate the effects of varying
levels of fine-tuning of PVMs. Our results show that partial fine-tuning can
maintain the highest average task performance under the most extreme
distribution shifts. Our results demonstrate that PVMs are highly successful in
promoting robustness in visual policy learning, providing compelling evidence
for their wider adoption in model-based robotic learning applications.</details></td></tr></tbody></table>

### 📅 2025-09-15
<table style='width:100%;'><colgroup><col style="width:61.8%;"><col style="width:38.2%;"></colgroup><thead><tr><th>title</th><th>abstract</th></tr></thead><tbody><tr><td><a href="http://arxiv.org/abs/2509.12187v1">HoloGarment: 360° Novel View Synthesis of In-the-Wild Garments</a></td><td><details><summary>展开</summary>Novel view synthesis (NVS) of in-the-wild garments is a challenging task due
significant occlusions, complex human poses, and cloth deformations. Prior
methods rely on synthetic 3D training data consisting of mostly unoccluded and
static objects, leading to poor generalization on real-world clothing. In this
paper, we propose HoloGarment (Hologram-Garment), a method that takes 1-3
images or a continuous video of a person wearing a garment and generates
360{\deg} novel views of the garment in a canonical pose. Our key insight is to
bridge the domain gap between real and synthetic data with a novel implicit
training paradigm leveraging a combination of large-scale real video data and
small-scale synthetic 3D data to optimize a shared garment embedding space.
During inference, the shared embedding space further enables dynamic
video-to-360{\deg} NVS through the construction of a garment "atlas"
representation by finetuning a garment embedding on a specific real-world
video. The atlas captures garment-specific geometry and texture across all
viewpoints, independent of body pose or motion. Extensive experiments show that
HoloGarment achieves state-of-the-art performance on NVS of in-the-wild
garments from images and videos. Notably, our method robustly handles
challenging real-world artifacts -- such as wrinkling, pose variation, and
occlusion -- while maintaining photorealism, view consistency, fine texture
details, and accurate geometry. Visit our project page for additional results:
https://johannakarras.github.io/HoloGarment</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.12168v1">RAGs to Riches: RAG-like Few-shot Learning for Large Language Model Role-playing</a></td><td><details><summary>展开</summary>Role-playing Large language models (LLMs) are increasingly deployed in
high-stakes domains such as healthcare, education, and governance, where
failures can directly impact user trust and well-being. A cost effective
paradigm for LLM role-playing is few-shot learning, but existing approaches
often cause models to break character in unexpected and potentially harmful
ways, especially when interacting with hostile users. Inspired by
Retrieval-Augmented Generation (RAG), we reformulate LLM role-playing into a
text retrieval problem and propose a new prompting framework called
RAGs-to-Riches, which leverages curated reference demonstrations to condition
LLM responses. We evaluate our framework with LLM-as-a-judge preference voting
and introduce two novel token-level ROUGE metrics: Intersection over Output
(IOO) to quantity how much an LLM improvises and Intersection over References
(IOR) to measure few-shot demonstrations utilization rate during the evaluation
tasks. When simulating interactions with a hostile user, our prompting strategy
incorporates in its responses during inference an average of 35% more tokens
from the reference demonstrations. As a result, across 453 role-playing
interactions, our models are consistently judged as being more authentic, and
remain in-character more often than zero-shot and in-context Learning (ICL)
methods. Our method presents a scalable strategy for building robust,
human-aligned LLM role-playing frameworks.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.12159v1">EfficientUICoder: Efficient MLLM-based UI Code Generation via Input and Output Token Compression</a></td><td><details><summary>展开</summary>Multimodal Large Language Models have demonstrated exceptional performance in
UI2Code tasks, significantly enhancing website development efficiency. However,
these tasks incur substantially higher computational overhead than traditional
code generation due to the large number of input image tokens and extensive
output code tokens required. Our comprehensive study identifies significant
redundancies in both image and code tokens that exacerbate computational
complexity and hinder focus on key UI elements, resulting in excessively
lengthy and often invalid HTML files. We propose EfficientUICoder, a
compression framework for efficient UI code generation with three key
components. First, Element and Layout-aware Token Compression preserves
essential UI information by detecting element regions and constructing UI
element trees. Second, Region-aware Token Refinement leverages attention scores
to discard low-attention tokens from selected regions while integrating
high-attention tokens from unselected regions. Third, Adaptive Duplicate Token
Suppression dynamically reduces repetitive generation by tracking HTML/CSS
structure frequencies and applying exponential penalties. Extensive experiments
show EfficientUICoderachieves a 55%-60% compression ratio without compromising
webpage quality and delivers superior efficiency improvements: reducing
computational cost by 44.9%, generated tokens by 41.4%, prefill time by 46.6%,
and inference time by 48.8% on 34B-level MLLMs. Code is available at
https://github.com/WebPAI/EfficientUICoder.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.12098v1">Is 'Hope' a person or an idea? A pilot benchmark for NER: comparing traditional NLP tools and large language models on ambiguous entities</a></td><td><details><summary>展开</summary>This pilot study presents a small-scale but carefully annotated benchmark of
Named Entity Recognition (NER) performance across six systems: three non-LLM
NLP tools (NLTK, spaCy, Stanza) and three general-purpose large language models
(LLMs: Gemini-1.5-flash, DeepSeek-V3, Qwen-3-4B). The dataset contains 119
tokens covering five entity types (PERSON, LOCATION, ORGANIZATION, DATE, TIME).
We evaluated each system's output against the manually annotated gold standard
dataset using F1-score. The results show that LLMs generally outperform
conventional tools in recognizing context-sensitive entities like person names,
with Gemini achieving the highest average F1-score. However, traditional
systems like Stanza demonstrate greater consistency in structured tags such as
LOCATION and DATE. We also observed variability among LLMs, particularly in
handling temporal expressions and multi-word organizations. Our findings
highlight that while LLMs offer improved contextual understanding, traditional
tools remain competitive in specific tasks, informing model selection.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.12080v1">A Time-Series Foundation Model by Universal Delay Embedding</a></td><td><details><summary>展开</summary>This study introduces Universal Delay Embedding (UDE), a pretrained
foundation model designed to revolutionize time-series forecasting through
principled integration of delay embedding representation and Koopman operator
prediction. Leveraging Takens' embedding theorem, UDE as a dynamical
representation of observed data constructs two-dimensional subspace patches
from Hankel matrices, theoretically preserving dynamical and topological
properties of underlying dynamical systems. Such patches are viewed as images,
which can be efficiently processed by exploiting advanced deep learning
technologies. Computationally, these patches further serve as tokens for
learning a self-attention encoder, thus enabling accurate prediction of
nonlinear time-series by a finite-dimensional Koopman operator in a linear
manner in a latent space. Extensive evaluations across various benchmarks and
real-world climate datasets demonstrate over 20% average reduction in mean
squared error versus state-of-the-art foundation models, alongside superior
generalization in fine-tuning scenarios. In particular, the learned dynamical
representations and Koopman operator prediction forms from the patches exhibit
exceptional interpretability, with consistent identification of topologically
informative subspaces and robust encoding of domain-invariant dynamics,
establishing UDE as a scalable, interpretable framework for universal
time-series modeling and forecasting with broad scientific and industrial
applicability.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.12069v1">U-Mamba2: Scaling State Space Models for Dental Anatomy Segmentation in CBCT</a></td><td><details><summary>展开</summary>Cone-Beam Computed Tomography (CBCT) is a widely used 3D imaging technique in
dentistry, providing volumetric information about the anatomical structures of
jaws and teeth. Accurate segmentation of these anatomies is critical for
clinical applications such as diagnosis and surgical planning, but remains
time-consuming and challenging. In this paper, we present U-Mamba2, a new
neural network architecture designed for multi-anatomy CBCT segmentation in the
context of the ToothFairy3 challenge. U-Mamba2 integrates the Mamba2 state
space models into the U-Net architecture, enforcing stronger structural
constraints for higher efficiency without compromising performance. In
addition, we integrate interactive click prompts with cross-attention blocks,
pre-train U-Mamba2 using self-supervised learning, and incorporate dental
domain knowledge into the model design to address key challenges of dental
anatomy segmentation in CBCT. Extensive experiments, including independent
tests, demonstrate that U-Mamba2 is both effective and efficient, securing top
3 places in both tasks of the Toothfairy3 challenge. In Task 1, U-Mamba2
achieved a mean Dice of 0.792, HD95 of 93.19 with the held-out test data, with
an average inference time of XX (TBC during the ODIN workshop). In Task 2,
U-Mamba2 achieved the mean Dice of 0.852 and HD95 of 7.39 with the held-out
test data. The code is publicly available at
https://github.com/zhiqin1998/UMamba2.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.12053v1">LEGO: Spatial Accelerator Generation and Optimization for Tensor Applications</a></td><td><details><summary>展开</summary>Modern tensor applications, especially foundation models and generative AI
applications require multiple input modalities (both vision and language),
which increases the demand for flexible accelerator architecture. Existing
frameworks suffer from the trade-off between design flexibility and
productivity of RTL generation: either limited to very few hand-written
templates or cannot automatically generate the RTL. To address this challenge,
we propose the LEGO framework, which targets tensor applications and
automatically generates spatial architecture design and outputs synthesizable
RTL code without handwritten RTL design templates. Leveraging the
affine-transformation-based architecture representation, LEGO front end finds
interconnections between function units, synthesizes the memory system, and
fuses different spatial dataflow designs based on data reuse analysis. LEGO
back end then translates the hardware in a primitive-level graph to perform
lower-level optimizations, and applies a set of linear-programming algorithms
to optimally insert pipeline registers and reduce the overhead of unused logic
when switching spatial dataflows. Our evaluation demonstrates that LEGO can
achieve 3.2x speedup and 2.4x energy efficiency compared to previous work
Gemmini, and can generate one architecture for diverse modern foundation models
in generative AI applications.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.12047v1">A Computer Vision Pipeline for Individual-Level Behavior Analysis: Benchmarking on the Edinburgh Pig Dataset</a></td><td><details><summary>展开</summary>Animal behavior analysis plays a crucial role in understanding animal
welfare, health status, and productivity in agricultural settings. However,
traditional manual observation methods are time-consuming, subjective, and
limited in scalability. We present a modular pipeline that leverages
open-sourced state-of-the-art computer vision techniques to automate animal
behavior analysis in a group housing environment. Our approach combines
state-of-the-art models for zero-shot object detection, motion-aware tracking
and segmentation, and advanced feature extraction using vision transformers for
robust behavior recognition. The pipeline addresses challenges including animal
occlusions and group housing scenarios as demonstrated in indoor pig
monitoring. We validated our system on the Edinburgh Pig Behavior Video Dataset
for multiple behavioral tasks. Our temporal model achieved 94.2% overall
accuracy, representing a 21.2 percentage point improvement over existing
methods. The pipeline demonstrated robust tracking capabilities with 93.3%
identity preservation score and 89.3% object detection precision. The modular
design suggests potential for adaptation to other contexts, though further
validation across species would be required. The open-source implementation
provides a scalable solution for behavior monitoring, contributing to precision
pig farming and welfare assessment through automated, objective, and continuous
analysis.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.12026v1">Imitation Learning as Return Distribution Matching</a></td><td><details><summary>展开</summary>We study the problem of training a risk-sensitive reinforcement learning (RL)
agent through imitation learning (IL). Unlike standard IL, our goal is not only
to train an agent that matches the expert's expected return (i.e., its average
performance) but also its risk attitude (i.e., other features of the return
distribution, such as variance). We propose a general formulation of the
risk-sensitive IL problem in which the objective is to match the expert's
return distribution in Wasserstein distance. We focus on the tabular setting
and assume the expert's reward is known. After demonstrating the limited
expressivity of Markovian policies for this task, we introduce an efficient and
sufficiently expressive subclass of non-Markovian policies tailored to it.
Building on this subclass, we develop two provably efficient algorithms, RS-BC
and RS-KT, for solving the problem when the transition model is unknown and
known, respectively. We show that RS-KT achieves substantially lower sample
complexity than RS-BC by exploiting dynamics information. We further
demonstrate the sample efficiency of return distribution matching in the
setting where the expert's reward is unknown by designing an oracle-based
variant of RS-KT. Finally, we complement our theoretical analysis of RS-KT and
RS-BC with numerical simulations, highlighting both their sample efficiency and
the advantages of non-Markovian policies over standard sample-efficient IL
algorithms.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.12010v1">Generalizing Behavior via Inverse Reinforcement Learning with Closed-Form Reward Centroids</a></td><td><details><summary>展开</summary>We study the problem of generalizing an expert agent's behavior, provided
through demonstrations, to new environments and/or additional constraints.
Inverse Reinforcement Learning (IRL) offers a promising solution by seeking to
recover the expert's underlying reward function, which, if used for planning in
the new settings, would reproduce the desired behavior. However, IRL is
inherently ill-posed: multiple reward functions, forming the so-called feasible
set, can explain the same observed behavior. Since these rewards may induce
different policies in the new setting, in the absence of additional
information, a decision criterion is needed to select which policy to deploy.
In this paper, we propose a novel, principled criterion that selects the
"average" policy among those induced by the rewards in a certain bounded subset
of the feasible set. Remarkably, we show that this policy can be obtained by
planning with the reward centroid of that subset, for which we derive a
closed-form expression. We then present a provably efficient algorithm for
estimating this centroid using an offline dataset of expert demonstrations
only. Finally, we conduct numerical simulations that illustrate the
relationship between the expert's behavior and the behavior produced by our
method.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.11991v1">Text Adaptation to Plain Language and Easy Read via Automatic Post-Editing Cycles</a></td><td><details><summary>展开</summary>We describe Vicomtech's participation in the CLEARS challenge on text
adaptation to Plain Language and Easy Read in Spanish. Our approach features
automatic post-editing of different types of initial Large Language Model
adaptations, where successive adaptations are generated iteratively until
readability and similarity metrics indicate that no further adaptation
refinement can be successfully performed. Taking the average of all official
metrics, our submissions achieved first and second place in Plain language and
Easy Read adaptation, respectively.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.11947v1">A GPU-Accelerated RAG-Based Telegram Assistant for Supporting Parallel Processing Students</a></td><td><details><summary>展开</summary>This project addresses a critical pedagogical need: offering students
continuous, on-demand academic assistance beyond conventional reception hours.
I present a domain-specific Retrieval-Augmented Generation (RAG) system powered
by a quantized Mistral-7B Instruct model and deployed as a Telegram bot. The
assistant enhances learning by delivering real-time, personalized responses
aligned with the "Introduction to Parallel Processing" course materials. GPU
acceleration significantly improves inference latency, enabling practical
deployment on consumer hardware. This approach demonstrates how consumer GPUs
can enable affordable, private, and effective AI tutoring for HPC education.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.11937v1">MMORE: Massive Multimodal Open RAG & Extraction</a></td><td><details><summary>展开</summary>We introduce MMORE, an open-source pipeline for Massive Multimodal Open
RetrievalAugmented Generation and Extraction, designed to ingest, transform,
and retrieve knowledge from heterogeneous document formats at scale. MMORE
supports more than fifteen file types, including text, tables, images, emails,
audio, and video, and processes them into a unified format to enable downstream
applications for LLMs. The architecture offers modular, distributed processing,
enabling scalable parallelization across CPUs and GPUs. On processing
benchmarks, MMORE demonstrates a 3.8-fold speedup over single-node baselines
and 40% higher accuracy than Docling on scanned PDFs. The pipeline integrates
hybrid dense-sparse retrieval and supports both interactive APIs and batch RAG
endpoints. Evaluated on PubMedQA, MMORE-augmented medical LLMs improve
biomedical QA accuracy with increasing retrieval depth. MMORE provides a
robust, extensible foundation for deploying task-agnostic RAG systems on
diverse, real-world multimodal data. The codebase is available at
https://github.com/swiss-ai/mmore.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.11865v1">Tenma: Robust Cross-Embodiment Robot Manipulation with Diffusion Transformer</a></td><td><details><summary>展开</summary>Scaling Transformer policies and diffusion models has advanced robotic
manipulation, yet combining these techniques in lightweight, cross-embodiment
learning settings remains challenging. We study design choices that most affect
stability and performance for diffusion-transformer policies trained on
heterogeneous, multimodal robot data, and introduce Tenma, a lightweight
diffusion-transformer for bi-manual arm control. Tenma integrates multiview
RGB, proprioception, and language via a cross-embodiment normalizer that maps
disparate state/action spaces into a shared latent space; a Joint State-Time
encoder for temporally aligned observation learning with inference speed
boosts; and a diffusion action decoder optimized for training stability and
learning capacity. Across benchmarks and under matched compute, Tenma achieves
an average success rate of 88.95% in-distribution and maintains strong
performance under object and scene shifts, substantially exceeding baseline
policies whose best in-distribution average is 18.12%. Despite using moderate
data scale, Tenma delivers robust manipulation and generalization, indicating
the great potential for multimodal and cross-embodiment learning strategies for
further augmenting the capacity of transformer-based imitation learning
policies.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.11815v1">SpecVLM: Fast Speculative Decoding in Vision-Language Models</a></td><td><details><summary>展开</summary>Speculative decoding is a powerful way to accelerate autoregressive large
language models (LLMs), but directly porting it to vision-language models
(VLMs) faces unique systems constraints: the prefill stage is dominated by
visual tokens whose count scales with image resolution and video length,
inflating both compute and memory, especially the key-value (KV) cache. We
study speculative decoding for VLMs and introduce SpecVLM, a practical system
that (1) establishes a strong EAGLE-2-style baseline, EagleVLM, delivering
1.5--2.3x end-to-end speedups over full autoregressive inference, and (2)
further accelerates VLM inference with an elastic visual compressor that
adaptively selects among pruning, pooling, convolution, and resampler
primitives to balance FLOPs/parameters and accuracy per input. To avoid costly
offline distillation corpora, we propose an online-logit distillation protocol
that trains the draft model with on-the-fly teacher logits and penultimate
features using a combined cross-entropy and Smooth L1 objective, eliminating
storage and preprocessing while remaining compute-efficient. This protocol
reveals a training-time scaling effect: longer online training monotonically
increases the draft model's average accepted length, improving speculative
efficiency. Empirically, SpecVLM achieves additional acceleration, culminating
in 2.5--2.9x end-to-end speedups within 5 epochs across LLaVA and MMMU,
consistently over resolutions and task difficulties, while preserving the
target model's output distribution (lossless decoding). Our code is available
at https://github.com/haiduo/SpecVLM.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.11731v1">Bridging the Gap Between Sparsity and Redundancy: A Dual-Decoding Framework with Global Context for Map Inference</a></td><td><details><summary>展开</summary>Trajectory data has become a key resource for automated map in-ference due to
its low cost, broad coverage, and continuous availability. However, uneven
trajectory density often leads to frag-mented roads in sparse areas and
redundant segments in dense regions, posing significant challenges for existing
methods. To address these issues, we propose DGMap, a dual-decoding framework
with global context awareness, featuring Multi-scale Grid Encoding,
Mask-enhanced Keypoint Extraction, and Global Context-aware Relation
Prediction. By integrating global semantic context with local geometric
features, DGMap improves keypoint detection accuracy to reduce road
fragmentation in sparse-trajectory areas. Additionally, the Global
Context-aware Relation Prediction module suppresses false connections in
dense-trajectory regions by modeling long-range trajectory patterns.
Experimental results on three real-world datasets show that DGMap outperforms
state-of-the-art methods by 5% in APLS, with notable performance gains on
trajectory data from the Didi Chuxing platform</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.11698v1">CoachMe: Decoding Sport Elements with a Reference-Based Coaching Instruction Generation Model</a></td><td><details><summary>展开</summary>Motion instruction is a crucial task that helps athletes refine their
technique by analyzing movements and providing corrective guidance. Although
recent advances in multimodal models have improved motion understanding,
generating precise and sport-specific instruction remains challenging due to
the highly domain-specific nature of sports and the need for informative
guidance. We propose CoachMe, a reference-based model that analyzes the
differences between a learner's motion and a reference under temporal and
physical aspects. This approach enables both domain-knowledge learning and the
acquisition of a coach-like thinking process that identifies movement errors
effectively and provides feedback to explain how to improve. In this paper, we
illustrate how CoachMe adapts well to specific sports such as skating and
boxing by learning from general movements and then leveraging limited data.
Experiments show that CoachMe provides high-quality instructions instead of
directions merely in the tone of a coach but without critical information.
CoachMe outperforms GPT-4o by 31.6% in G-Eval on figure skating and by 58.3% on
boxing. Analysis further confirms that it elaborates on errors and their
corresponding improvement methods in the generated instructions. You can find
CoachMe here: https://motionxperts.github.io/</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.11686v1">Do Code Semantics Help? A Comprehensive Study on Execution Trace-Based Information for Code Large Language Models</a></td><td><details><summary>展开</summary>Code Large Language Models (Code LLMs) have opened a new era in programming
with their impressive capabilities. However, recent research has revealed
critical limitations in their ability to reason about runtime behavior and
understand the actual functionality of programs, which poses significant
challenges for their post-training and practical deployment. Specifically, Code
LLMs encounter two principal issues: (1) a lack of proficiency in reasoning
about program execution behavior, as they struggle to interpret what programs
actually do during runtime, and (2) the inconsistent and fragmented
representation of semantic information, such as execution traces, across
existing methods, which hinders their ability to generalize and reason
effectively. These challenges underscore the necessity for more systematic
approaches to enhance the reasoning capabilities of Code LLMs. To address these
issues, we introduce a generic framework to support integrating semantic
information~(e.g., execution trace) to code task-relevant prompts, and conduct
a comprehensive study to explore the role of semantic information in enhancing
the reasoning ability of Code LLMs accordingly. Specifically, we focus on
investigating the usefulness of trace-based semantic information in boosting
supervised fine-tuning~(SFT) and post-phase inference of Code LLMs. The
experimental results surprisingly disagree with previous works and demonstrate
that semantic information has limited usefulness for SFT and test time scaling
of Code LLM.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.11663v1">ParaEQsA: Parallel and Asynchronous Embodied Questions Scheduling and Answering</a></td><td><details><summary>展开</summary>This paper formulates the Embodied Questions Answering (EQsA) problem,
introduces a corresponding benchmark, and proposes a system to tackle the
problem. Classical Embodied Question Answering (EQA) is typically formulated as
answering one single question by actively exploring a 3D environment. Real
deployments, however, often demand handling multiple questions that may arrive
asynchronously and carry different urgencies. We formalize this setting as
Embodied Questions Answering (EQsA) and present ParaEQsA, a framework for
parallel, urgency-aware scheduling and answering. ParaEQsA leverages a group
memory module shared among questions to reduce redundant exploration, and a
priority-planning module to dynamically schedule questions. To evaluate this
setting, we contribute the Parallel Asynchronous Embodied Questions (PAEQs)
benchmark containing 40 indoor scenes and five questions per scene (200 in
total), featuring asynchronous follow-up questions and urgency labels. We
further propose metrics for EQsA performance: Direct Answer Rate (DAR), and
Normalized Urgency-Weighted Latency (NUWL), which jointly measure efficiency
and responsiveness of this system. ParaEQsA consistently outperforms strong
sequential baselines adapted from recent EQA systems, while reducing
exploration and delay. Empirical evaluations investigate the relative
contributions of priority, urgency modeling, spatial scope, reward estimation,
and dependency reasoning within our framework. Together, these results
demonstrate that urgency-aware, parallel scheduling is key to making embodied
agents responsive and efficient under realistic, multi-question workloads.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.11662v1">MindVL: Towards Efficient and Effective Training of Multimodal Large Language Models on Ascend NPUs</a></td><td><details><summary>展开</summary>We propose MindVL, a multimodal large langauge model trained on Ascend NPUs.
Similar to Qwen2.5-VL, MindVL adopts native-resolution Vision Transformers,
which enables it to process images at their original variable resolutions. This
design avoids the degradation caused by fixed-resolution tiling while
preserving fine-grained details and global layouts, which is crucial for
visually dense content such as complex charts and diagrams. To ensure the
smooth training of MindVL on Ascend NPUs, we develop Mindspeed-MLLM, a
distributed multimodal training framework tailored for Ascend NPUs. To maintain
training accuracy, we implement equivalent replacements for certain operators.
MindVL undergoes a three-phase training process, namely the warm-up phase,
multitask training phase, and supervised instruction tuning phase, to gradually
enhance its capabilities. This process starts with basic visual and multimodal
pre-training, followed by large-scale multiask trainging and instruction
tuning. We also adopt multimodal data packaging and hybrid parallelism
techniques, which significantly improve end-to-end training speed. To further
boost model performance, we specifically introduce test-time resolution search
and model weight averaging. Notably, despite using about 1/10 of the training
data required by Qwen2.5-VL, MindVL achieves performance on par with Qwen2.5-VL
in evaluations of general multimodal understanding and document/table
comprehension. Beyond overall scores, MindVL also delivers leading performance
in OCR assessments.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.11656v1">MALLM: Multi-Agent Large Language Models Framework</a></td><td><details><summary>展开</summary>Multi-agent debate (MAD) has demonstrated the ability to augment collective
intelligence by scaling test-time compute and leveraging expertise. Current
frameworks for multi-agent debate are often designed towards tool use, lack
integrated evaluation, or provide limited configurability of agent personas,
response generators, discussion paradigms, and decision protocols. We introduce
MALLM (Multi-Agent Large Language Models), an open-source framework that
enables systematic analysis of MAD components. MALLM offers more than 144
unique configurations of MAD, including (1) agent personas (e.g., Expert,
Personality), (2) response generators (e.g., Critical, Reasoning), (3)
discussion paradigms (e.g., Memory, Relay), and (4) decision protocols (e.g.,
Voting, Consensus). MALLM uses simple configuration files to define a debate.
Furthermore, MALLM can load any textual Huggingface dataset (e.g., MMLU-Pro,
WinoGrande) and provides an evaluation pipeline for easy comparison of MAD
configurations. MALLM is tailored towards researchers and provides a window
into the heart of multi-agent debate, facilitating the understanding of its
components and their interplay.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.11645v1">Adapting and Evaluating Multimodal Large Language Models for Adolescent Idiopathic Scoliosis Self-Management: A Divide and Conquer Framework</a></td><td><details><summary>展开</summary>This study presents the first comprehensive evaluation of Multimodal Large
Language Models (MLLMs) for Adolescent Idiopathic Scoliosis (AIS)
self-management. We constructed a database of approximately 3,000
anteroposterior X-rays with diagnostic texts and evaluated five MLLMs through a
`Divide and Conquer' framework consisting of a visual question-answering task,
a domain knowledge assessment task, and a patient education counseling
assessment task. Our investigation revealed limitations of MLLMs' ability in
interpreting complex spinal radiographs and comprehending AIS care knowledge.
To address these, we pioneered enhancing MLLMs with spinal keypoint prompting
and compiled an AIS knowledge base for retrieval augmented generation (RAG),
respectively. Results showed varying effectiveness of visual prompting across
different architectures, while RAG substantially improved models' performances
on the knowledge assessment task. Our findings indicate current MLLMs are far
from capable in realizing personalized assistant in AIS care. The greatest
challenge lies in their abilities to obtain accurate detections of spinal
deformity locations (best accuracy: 0.55) and directions (best accuracy: 0.13).</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.11636v1">Task-Agnostic Learnable Weighted-Knowledge Base Scheme for Robust Semantic Communications</a></td><td><details><summary>展开</summary>With the emergence of diverse and massive data in the upcoming
sixth-generation (6G) networks, the task-agnostic semantic communication system
is regarded to provide robust intelligent services. In this paper, we propose a
task-agnostic learnable weighted-knowledge base semantic communication (TALSC)
framework for robust image transmission to address the real-world heterogeneous
data bias in KB, including label flipping noise and class imbalance. The TALSC
framework incorporates a sample confidence module (SCM) as meta-learner and the
semantic coding networks as learners. The learners are updated based on the
empirical knowledge provided by the learnable weighted-KB (LW-KB). Meanwhile,
the meta-learner evaluates the significance of samples according to the task
loss feedback, and adjusts the update strategy of learners to enhance the
robustness in semantic recovery for unknown tasks. To strike a balance between
SCM parameters and precision of significance evaluation, we design an SCM-grid
extension (SCM-GE) approach by embedding the Kolmogorov-Arnold networks (KAN)
within SCM, which leverages the concept of spline refinement in KAN and enables
scalable SCM with customizable granularity without retraining. Simulations
demonstrate that the TALSC framework effectively mitigates the effects of
flipping noise and class imbalance in task-agnostic image semantic
communication, achieving at least 12% higher semantic recovery accuracy (SRA)
and multi-scale structural similarity (MS-SSIM) compared to state-of-the-art
methods.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.11595v1">AMLNet: A Knowledge-Based Multi-Agent Framework to Generate and Detect Realistic Money Laundering Transactions</a></td><td><details><summary>展开</summary>Anti-money laundering (AML) research is constrained by the lack of publicly
shareable, regulation-aligned transaction datasets. We present AMLNet, a
knowledge-based multi-agent framework with two coordinated units: a
regulation-aware transaction generator and an ensemble detection pipeline. The
generator produces 1,090,173 synthetic transactions (approximately 0.16\%
laundering-positive) spanning core laundering phases (placement, layering,
integration) and advanced typologies (e.g., structuring, adaptive threshold
behavior). Regulatory alignment reaches 75\% based on AUSTRAC rule coverage
(Section 4.2), while a composite technical fidelity score of 0.75 summarizes
temporal, structural, and behavioral realism components (Section 4.4). The
detection ensemble achieves F1 0.90 (precision 0.84, recall 0.97) on the
internal test partitions of AMLNet and adapts to the external SynthAML dataset,
indicating architectural generalizability across different synthetic generation
paradigms. We provide multi-dimensional evaluation (regulatory, temporal,
network, behavioral) and release the dataset (Version 1.0,
https://doi.org/10.5281/zenodo.16736515), to advance reproducible and
regulation-conscious AML experimentation.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.11594v1">GBPP: Grasp-Aware Base Placement Prediction for Robots via Two-Stage Learning</a></td><td><details><summary>展开</summary>GBPP is a fast learning based scorer that selects a robot base pose for
grasping from a single RGB-D snapshot. The method uses a two stage curriculum:
(1) a simple distance-visibility rule auto-labels a large dataset at low cost;
and (2) a smaller set of high fidelity simulation trials refines the model to
match true grasp outcomes. A PointNet++ style point cloud encoder with an MLP
scores dense grids of candidate poses, enabling rapid online selection without
full task-and-motion optimization. In simulation and on a real mobile
manipulator, GBPP outperforms proximity and geometry only baselines, choosing
safer and more reachable stances and degrading gracefully when wrong. The
results offer a practical recipe for data efficient, geometry aware base
placement: use inexpensive heuristics for coverage, then calibrate with
targeted simulation.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.11555v1">Dstack: A Zero Trust Framework for Confidential Containers</a></td><td><details><summary>展开</summary>Web3 applications require execution platforms that maintain confidentiality
and integrity without relying on centralized trust authorities. While Trusted
Execution Environments (TEEs) offer promising capabilities for confidential
computing, current implementations face significant limitations when applied to
Web3 contexts, particularly in security reliability, censorship resistance, and
vendor independence.
  This paper presents dstack, a comprehensive framework that transforms raw TEE
technology into a true Zero Trust platform. We introduce three key innovations:
(1) Portable Confidential Containers that enable seamless workload migration
across heterogeneous TEE environments while maintaining security guarantees,
(2) Decentralized Code Management that leverages smart contracts for
transparent governance of TEE applications, and (3) Verifiable Domain
Management that ensures secure and verifiable application identity without
centralized authorities.
  These innovations are implemented through three core components: dstack-OS,
dstack-KMS, and dstack-Gateway. Together, they demonstrate how to achieve both
the performance advantages of VM-level TEE solutions and the trustless
guarantees required by Web3 applications. Our evaluation shows that dstack
provides comprehensive security guarantees while maintaining practical
usability for real-world applications.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.11552v1">HiChunk: Evaluating and Enhancing Retrieval-Augmented Generation with Hierarchical Chunking</a></td><td><details><summary>展开</summary>Retrieval-Augmented Generation (RAG) enhances the response capabilities of
language models by integrating external knowledge sources. However, document
chunking as an important part of RAG system often lacks effective evaluation
tools. This paper first analyzes why existing RAG evaluation benchmarks are
inadequate for assessing document chunking quality, specifically due to
evidence sparsity. Based on this conclusion, we propose HiCBench, which
includes manually annotated multi-level document chunking points, synthesized
evidence-dense quetion answer(QA) pairs, and their corresponding evidence
sources. Additionally, we introduce the HiChunk framework, a multi-level
document structuring framework based on fine-tuned LLMs, combined with the
Auto-Merge retrieval algorithm to improve retrieval quality. Experiments
demonstrate that HiCBench effectively evaluates the impact of different
chunking methods across the entire RAG pipeline. Moreover, HiChunk achieves
better chunking quality within reasonable time consumption, thereby enhancing
the overall performance of RAG systems.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.11513v1">Unsupervised Candidate Ranking for Lexical Substitution via Holistic Sentence Semantics</a></td><td><details><summary>展开</summary>A key subtask in lexical substitution is ranking the given candidate words. A
common approach is to replace the target word with a candidate in the original
sentence and feed the modified sentence into a model to capture semantic
differences before and after substitution. However, effectively modeling the
bidirectional influence of candidate substitution on both the target word and
its context remains challenging. Existing methods often focus solely on
semantic changes at the target position or rely on parameter tuning over
multiple evaluation metrics, making it difficult to accurately characterize
semantic variation. To address this, we investigate two approaches: one based
on attention weights and another leveraging the more interpretable integrated
gradients method, both designed to measure the influence of context tokens on
the target token and to rank candidates by incorporating semantic similarity
between the original and substituted sentences. Experiments on the LS07 and
SWORDS datasets demonstrate that both approaches improve ranking performance.</details></td></tr></tbody></table>

### 📅 2025-09-14
<table style='width:100%;'><colgroup><col style="width:61.8%;"><col style="width:38.2%;"></colgroup><thead><tr><th>title</th><th>abstract</th></tr></thead><tbody><tr><td><a href="http://arxiv.org/abs/2509.11478v1">Designing and Evaluating a Conversational Agent for Early Detection of Alzheimer's Disease and Related Dementias</a></td><td><details><summary>展开</summary>Early detection of Alzheimer's disease and related dementias (ADRD) is
critical for timely intervention, yet most diagnoses are delayed until advanced
stages. While comprehensive patient narratives are essential for accurate
diagnosis, prior work has largely focused on screening studies that classify
cognitive status from interactions rather than supporting the diagnostic
process. We designed voice-interactive conversational agents, leveraging large
language models (LLMs), to elicit narratives relevant to ADRD from patients and
informants. We evaluated the agent with 30 adults with suspected ADRD through
conversation analysis (n=30), user surveys (n=19), and clinical validation
against blinded specialist interviews (n=24). Symptoms detected by the agent
aligned well with those identified by specialists across symptoms. Users
appreciated the agent's patience and systematic questioning, which supported
engagement and expression of complex, hard-to-describe experiences. This
preliminary work suggests conversational agents may serve as structured
front-end tools for dementia assessment, highlighting interaction design
considerations in sensitive healthcare contexts.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.11431v1">Securing AI Agents: Implementing Role-Based Access Control for Industrial Applications</a></td><td><details><summary>展开</summary>The emergence of Large Language Models (LLMs) has significantly advanced
solutions across various domains, from political science to software
development. However, these models are constrained by their training data,
which is static and limited to information available up to a specific date.
Additionally, their generalized nature often necessitates fine-tuning --
whether for classification or instructional purposes -- to effectively perform
specific downstream tasks. AI agents, leveraging LLMs as their core, mitigate
some of these limitations by accessing external tools and real-time data,
enabling applications such as live weather reporting and data analysis. In
industrial settings, AI agents are transforming operations by enhancing
decision-making, predictive maintenance, and process optimization. For example,
in manufacturing, AI agents enable near-autonomous systems that boost
productivity and support real-time decision-making. Despite these advancements,
AI agents remain vulnerable to security threats, including prompt injection
attacks, which pose significant risks to their integrity and reliability. To
address these challenges, this paper proposes a framework for integrating
Role-Based Access Control (RBAC) into AI agents, providing a robust security
guardrail. This framework aims to support the effective and scalable deployment
of AI agents, with a focus on on-premises implementations.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.11417v2">Enhancing Generalization in Vision-Language-Action Models by Preserving Pretrained Representations</a></td><td><details><summary>展开</summary>Vision-language-action (VLA) models finetuned from vision-language models
(VLMs) hold the promise of leveraging rich pretrained representations to build
generalist robots across diverse tasks and environments. However, direct
fine-tuning on robot data often disrupts these representations and limits
generalization. We present a framework that better preserves pretrained
features while adapting them for robot manipulation. Our approach introduces
three components: (i) a dual-encoder design with one frozen vision encoder to
retain pretrained features and another trainable for task adaptation, (ii) a
string-based action tokenizer that casts continuous actions into character
sequences aligned with the model's pretraining domain, and (iii) a co-training
strategy that combines robot demonstrations with vision-language datasets
emphasizing spatial reasoning and affordances. Evaluations in simulation and on
real robots show that our method improves robustness to visual perturbations,
generalization to novel instructions and environments, and overall task success
compared to baselines.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.11413v1">Framing AI System Benchmarking as a Learning Task: FlexBench and the Open MLPerf Dataset</a></td><td><details><summary>展开</summary>Existing AI system benchmarks such as MLPerf often struggle to keep pace with
the rapidly evolving AI landscape, making it difficult to support informed
deployment, optimization, and co-design decisions for AI systems. We suggest
that benchmarking itself can be framed as an AI task - one in which models are
continuously evaluated and optimized across diverse datasets, software, and
hardware, using key metrics such as accuracy, latency, throughput, energy
consumption, and cost. To support this perspective, we present FlexBench: a
modular extension of the MLPerf LLM inference benchmark, integrated with
HuggingFace and designed to provide relevant and actionable insights.
Benchmarking results and metadata are collected into an Open MLPerf Dataset,
which can be collaboratively curated, extended, and leveraged for predictive
modeling and feature engineering. We successfully validated the FlexBench
concept through MLPerf Inference submissions, including evaluations of DeepSeek
R1 and LLaMA 3.3 on commodity servers. The broader objective is to enable
practitioners to make cost-effective AI deployment decisions that reflect their
available resources, requirements, and constraints.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.11398v1">From Firewalls to Frontiers: AI Red-Teaming is a Domain-Specific Evolution of Cyber Red-Teaming</a></td><td><details><summary>展开</summary>A red team simulates adversary attacks to help defenders find effective
strategies to defend their systems in a real-world operational setting. As more
enterprise systems adopt AI, red-teaming will need to evolve to address the
unique vulnerabilities and risks posed by AI systems. We take the position that
AI systems can be more effectively red-teamed if AI red-teaming is recognized
as a domain-specific evolution of cyber red-teaming. Specifically, we argue
that existing Cyber Red Teams who adopt this framing will be able to better
evaluate systems with AI components by recognizing that AI poses new risks, has
new failure modes to exploit, and often contains unpatchable bugs that
re-prioritize disclosure and mitigation strategies. Similarly, adopting a
cybersecurity framing will allow existing AI Red Teams to leverage a
well-tested structure to emulate realistic adversaries, promote mutual
accountability with formal rules of engagement, and provide a pattern to mature
the tooling necessary for repeatable, scalable engagements. In these ways, the
merging of AI and Cyber Red Teams will create a robust security ecosystem and
best position the community to adapt to the rapidly changing threat landscape.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.11376v1">Intelligent Reservoir Decision Support: An Integrated Framework Combining Large Language Models, Advanced Prompt Engineering, and Multimodal Data Fusion for Real-Time Petroleum Operations</a></td><td><details><summary>展开</summary>The petroleum industry faces unprecedented challenges in reservoir
management, requiring rapid integration of complex multimodal datasets for
real-time decision support. This study presents a novel integrated framework
combining state-of-the-art large language models (GPT-4o, Claude 4 Sonnet,
Gemini 2.5 Pro) with advanced prompt engineering techniques and multimodal data
fusion for comprehensive reservoir analysis. The framework implements
domain-specific retrieval-augmented generation (RAG) with over 50,000 petroleum
engineering documents, chain-of-thought reasoning, and few-shot learning for
rapid field adaptation. Multimodal integration processes seismic
interpretations, well logs, and production data through specialized AI models
with vision transformers. Field validation across 15 diverse reservoir
environments demonstrates exceptional performance: 94.2% reservoir
characterization accuracy, 87.6% production forecasting precision, and 91.4%
well placement optimization success rate. The system achieves sub-second
response times while maintaining 96.2% safety reliability with no high-risk
incidents during evaluation. Economic analysis reveals 62-78% cost reductions
(mean 72%) relative to traditional methods with 8-month payback period.
Few-shot learning reduces field adaptation time by 72%, while automated prompt
optimization achieves 89% improvement in reasoning quality. The framework
processed real-time data streams with 96.2% anomaly detection accuracy and
reduced environmental incidents by 45%. We provide detailed experimental
protocols, baseline comparisons, ablation studies, and statistical significance
testing to ensure reproducibility. This research demonstrates practical
integration of cutting-edge AI technologies with petroleum domain expertise for
enhanced operational efficiency, safety, and economic performance.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.11361v1">MAPGD: Multi-Agent Prompt Gradient Descent for Collaborative Prompt Optimization</a></td><td><details><summary>展开</summary>Prompt engineering is crucial for leveraging large language models (LLMs),
but existing methods often rely on a single optimization trajectory, limiting
adaptability and efficiency while suffering from narrow perspectives, gradient
conflicts, and high computational cost. We propose MAPGD (Multi-Agent Prompt
Gradient Descent), a framework integrating multi-agent collaboration with
gradient-based optimization. MAPGD features specialized agents for task
clarity, example selection, format design, and stylistic refinement; semantic
gradient coordination to resolve conflicts; bandit-based candidate selection
for efficient exploration-exploitation; and theoretical convergence guarantees.
Experiments on classification, generation, and reasoning tasks show MAPGD
outperforms single-agent and random baselines in accuracy and efficiency.
Ablations confirm the benefits of gradient fusion, agent specialization, and
conflict resolution, providing a unified, gradient-inspired multi-agent
approach to robust and interpretable prompt optimization.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.11355v1">Promoting Shape Bias in CNNs: Frequency-Based and Contrastive Regularization for Corruption Robustness</a></td><td><details><summary>展开</summary>Convolutional Neural Networks (CNNs) excel at image classification but remain
vulnerable to common corruptions that humans handle with ease. A key reason for
this fragility is their reliance on local texture cues rather than global
object shapes -- a stark contrast to human perception. To address this, we
propose two complementary regularization strategies designed to encourage
shape-biased representations and enhance robustness. The first introduces an
auxiliary loss that enforces feature consistency between original and
low-frequency filtered inputs, discouraging dependence on high-frequency
textures. The second incorporates supervised contrastive learning to structure
the feature space around class-consistent, shape-relevant representations.
Evaluated on the CIFAR-10-C benchmark, both methods improve corruption
robustness without degrading clean accuracy. Our results suggest that
loss-level regularization can effectively steer CNNs toward more shape-aware,
resilient representations.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.11336v1">The power of dynamic causality in observer-based design for soft sensor applications</a></td><td><details><summary>展开</summary>This paper introduces a novel framework for optimizing observer-based soft
sensors through dynamic causality analysis. Traditional approaches to sensor
selection often rely on linearized observability indices or statistical
correlations that fail to capture the temporal evolution of complex systems. We
address this gap by leveraging liquid-time constant (LTC) networks,
continuous-time neural architectures with input-dependent time constants, to
systematically identify and prune sensor inputs with minimal causal influence
on state estimation. Our methodology implements an iterative workflow: training
an LTC observer on candidate inputs, quantifying each input's causal impact
through controlled perturbation analysis, removing inputs with negligible
effect, and retraining until performance degradation occurs. We demonstrate
this approach on three mechanistic testbeds representing distinct physical
domains: a harmonically forced spring-mass-damper system, a nonlinear
continuous stirred-tank reactor, and a predator-prey model following the
structure of the Lotka-Volterra model, but with seasonal forcing and added
complexity. Results show that our causality-guided pruning consistently
identifies minimal sensor sets that align with underlying physics while
improving prediction accuracy. The framework automatically distinguishes
essential physical measurements from noise and determines when derived
interaction terms provide complementary versus redundant information. Beyond
computational efficiency, this approach enhances interpretability by grounding
sensor selection decisions in dynamic causal relationships rather than static
correlations, offering significant benefits for soft sensing applications
across process engineering, ecological monitoring, and agricultural domains.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.11330v1">Decoding Plastic Toxicity: An Intelligent Framework for Conflict-Aware Relational Metapath Extraction from Scientific Abstracts</a></td><td><details><summary>展开</summary>The widespread use of plastics and their persistence in the environment have
led to the accumulation of micro- and nano-plastics across air, water, and
soil, posing serious health risks including respiratory, gastrointestinal, and
neurological disorders. We propose a novel framework that leverages large
language models to extract relational metapaths, multi-hop semantic chains
linking pollutant sources to health impacts, from scientific abstracts. Our
system identifies and connects entities across diverse contexts to construct
structured relational metapaths, which are aggregated into a Toxicity
Trajectory Graph that traces pollutant propagation through exposure routes and
biological systems. Moreover, to ensure consistency and reliability, we
incorporate a dynamic evidence reconciliation module that resolves semantic
conflicts arising from evolving or contradictory research findings. Our
approach demonstrates strong performance in extracting reliable, high-utility
relational knowledge from noisy scientific text and offers a scalable solution
for mining complex cause-effect structures in domain-specific corpora.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.12282v1">AIssistant: An Agentic Approach for Human--AI Collaborative Scientific Work on Reviews and Perspectives in Machine Learning</a></td><td><details><summary>展开</summary>Advances in AI-assisted research have introduced powerful tools for
literature retrieval, hypothesis generation, experimentation, and manuscript
preparation. However, systems remain fragmented and lack human-centred
workflows. To address these gaps, we introduce AIssistant, an agentic,
open-source Human-AI collaborative framework designed to simplify the
end-to-end creation of scientific workflows. Since our development is still in
an early stage, we present here the first experiments with AIssistant for
perspective and review research papers in machine learning. Our system
integrates modular tools and agents for literature synthesis, section-wise
experimentation, citation management, and automatic LaTeX paper text
generation, while maintaining human oversight at every stage to ensure
accuracy, coherence, and scholarly rigour. We conducted a comprehensive
evaluation across three layers: (1) Independent Human Review, following NeurIPS
double-blind standards; (2) Automated LLM Review, using GPT-5 as a scalable
human review proxy; and (3) Program Chair Oversight, where the chair monitors
the entire review process and makes final validation and acceptance decisions.
The results demonstrate that AIssistant improves drafting efficiency and
thematic consistency. Nonetheless, Human-AI collaboration remains essential for
maintaining factual correctness, methodological soundness, and ethical
compliance. Despite its effectiveness, we identify key limitations, including
hallucinated citations, difficulty adapting to dynamic paper structures, and
incomplete integration of multimodal content.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.11285v1">Efficient Single-Step Framework for Incremental Class Learning in Neural Networks</a></td><td><details><summary>展开</summary>Incremental learning remains a critical challenge in machine learning, as
models often struggle with catastrophic forgetting -the tendency to lose
previously acquired knowledge when learning new information. These challenges
are even more pronounced in resource-limited settings. Many existing Class
Incremental Learning (CIL) methods achieve high accuracy by continually
adapting their feature representations; however, they often require substantial
computational resources and complex, iterative training procedures. This work
introduces CIFNet (Class Incremental and Frugal Network), a novel CIL approach
that addresses these limitations by offering a highly efficient and sustainable
solution. CIFNet's key innovation lies in its novel integration of several
existing, yet separately explored, components: a pre-trained and frozen feature
extractor, a compressed data buffer, and an efficient non-iterative one-layer
neural network for classification. A pre-trained and frozen feature extractor
eliminates computationally expensive fine-tuning of the backbone. This,
combined with a compressed buffer for efficient memory use, enables CIFNet to
perform efficient class-incremental learning through a single-step optimization
process on fixed features, minimizing computational overhead and training time
without requiring multiple weight updates. Experiments on benchmark datasets
confirm that CIFNet effectively mitigates catastrophic forgetting at the
classifier level, achieving high accuracy comparable to that of existing
state-of-the-art methods, while substantially improving training efficiency and
sustainability. CIFNet represents a significant advancement in making
class-incremental learning more accessible and pragmatic in environments with
limited resources, especially when strong pre-trained feature extractors are
available.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.11270v1">Embodied Intelligence in Disassembly: Multimodal Perception Cross-validation and Continual Learning in Neuro-Symbolic TAMP</a></td><td><details><summary>展开</summary>With the rapid development of the new energy vehicle industry, the efficient
disassembly and recycling of power batteries have become a critical challenge
for the circular economy. In current unstructured disassembly scenarios, the
dynamic nature of the environment severely limits the robustness of robotic
perception, posing a significant barrier to autonomous disassembly in
industrial applications. This paper proposes a continual learning framework
based on Neuro-Symbolic task and motion planning (TAMP) to enhance the
adaptability of embodied intelligence systems in dynamic environments. Our
approach integrates a multimodal perception cross-validation mechanism into a
bidirectional reasoning flow: the forward working flow dynamically refines and
optimizes action strategies, while the backward learning flow autonomously
collects effective data from historical task executions to facilitate continual
system learning, enabling self-optimization. Experimental results show that the
proposed framework improves the task success rate in dynamic disassembly
scenarios from 81.68% to 100%, while reducing the average number of perception
misjudgments from 3.389 to 1.128. This research provides a new paradigm for
enhancing the robustness and adaptability of embodied intelligence in complex
industrial environments.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.11218v1">Geometrically Constrained and Token-Based Probabilistic Spatial Transformers</a></td><td><details><summary>展开</summary>Fine-grained visual classification (FGVC) remains highly sensitive to
geometric variability, where objects appear under arbitrary orientations,
scales, and perspective distortions. While equivariant architectures address
this issue, they typically require substantial computational resources and
restrict the hypothesis space. We revisit Spatial Transformer Networks (STNs)
as a canonicalization tool for transformer-based vision pipelines, emphasizing
their flexibility, backbone-agnostic nature, and lack of architectural
constraints. We propose a probabilistic, component-wise extension that improves
robustness. Specifically, we decompose affine transformations into rotation,
scaling, and shearing, and regress each component under geometric constraints
using a shared localization encoder. To capture uncertainty, we model each
component with a Gaussian variational posterior and perform sampling-based
canonicalization during inference.A novel component-wise alignment loss
leverages augmentation parameters to guide spatial alignment. Experiments on
challenging moth classification benchmarks demonstrate that our method
consistently improves robustness compared to other STNs.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.11206v2">Evalet: Evaluating Large Language Models by Fragmenting Outputs into Functions</a></td><td><details><summary>展开</summary>Practitioners increasingly rely on Large Language Models (LLMs) to evaluate
generative AI outputs through "LLM-as-a-Judge" approaches. However, these
methods produce holistic scores that obscure which specific elements influenced
the assessments. We propose functional fragmentation, a method that dissects
each output into key fragments and interprets the rhetoric functions that each
fragment serves relative to evaluation criteria -- surfacing the elements of
interest and revealing how they fulfill or hinder user goals. We instantiate
this approach in Evalet, an interactive system that visualizes fragment-level
functions across many outputs to support inspection, rating, and comparison of
evaluations. A user study (N=10) found that, while practitioners struggled to
validate holistic scores, our approach helped them identify 48% more evaluation
misalignments. This helped them calibrate trust in LLM evaluations and rely on
them to find more actionable issues in model outputs. Our work shifts LLM
evaluation from quantitative scores toward qualitative, fine-grained analysis
of model behavior.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.11198v1">Quantum Architecture Search for Solving Quantum Machine Learning Tasks</a></td><td><details><summary>展开</summary>Quantum computing leverages quantum mechanics to address computational
problems in ways that differ fundamentally from classical approaches. While
current quantum hardware remains error-prone and limited in scale, Variational
Quantum Circuits offer a noise-resilient framework suitable for today's
devices. The performance of these circuits strongly depends on the underlying
architecture of their parameterized quantum components. Identifying efficient,
hardware-compatible quantum circuit architectures -- known as Quantum
Architecture Search (QAS) -- is therefore essential. Manual QAS is complex and
error-prone, motivating efforts to automate it. Among various automated
strategies, Reinforcement Learning (RL) remains underexplored, particularly in
Quantum Machine Learning contexts. This work introduces RL-QAS, a framework
that applies RL to discover effective circuit architectures for classification
tasks. We evaluate RL-QAS using the Iris and binary MNIST datasets. The agent
autonomously discovers low-complexity circuit designs that achieve high test
accuracy. Our results show that RL is a viable approach for automated
architecture search in quantum machine learning. However, applying RL-QAS to
more complex tasks will require further refinement of the search strategy and
performance evaluation mechanisms.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.13353v1">Hybrid Quantum-Classical Model for Image Classification</a></td><td><details><summary>展开</summary>This study presents a systematic comparison between hybrid quantum-classical
neural networks and purely classical models across three benchmark datasets
(MNIST, CIFAR100, and STL10) to evaluate their performance, efficiency, and
robustness. The hybrid models integrate parameterized quantum circuits with
classical deep learning architectures, while the classical counterparts use
conventional convolutional neural networks (CNNs). Experiments were conducted
over 50 training epochs for each dataset, with evaluations on validation
accuracy, test accuracy, training time, computational resource usage, and
adversarial robustness (tested with $\epsilon=0.1$ perturbations).Key findings
demonstrate that hybrid models consistently outperform classical models in
final accuracy, achieving {99.38\% (MNIST), 41.69\% (CIFAR100), and 74.05\%
(STL10) validation accuracy, compared to classical benchmarks of 98.21\%,
32.25\%, and 63.76\%, respectively. Notably, the hybrid advantage scales with
dataset complexity, showing the most significant gains on CIFAR100 (+9.44\%)
and STL10 (+10.29\%). Hybrid models also train 5--12$\times$ faster (e.g.,
21.23s vs. 108.44s per epoch on MNIST) and use 6--32\% fewer parameters} while
maintaining superior generalization to unseen test data.Adversarial robustness
tests reveal that hybrid models are significantly more resilient on simpler
datasets (e.g., 45.27\% robust accuracy on MNIST vs. 10.80\% for classical) but
show comparable fragility on complex datasets like CIFAR100 ($\sim$1\%
robustness for both). Resource efficiency analyses indicate that hybrid models
consume less memory (4--5GB vs. 5--6GB for classical) and lower CPU utilization
(9.5\% vs. 23.2\% on average).These results suggest that hybrid
quantum-classical architectures offer compelling advantages in accuracy,
training efficiency, and parameter scalability, particularly for complex vision
tasks.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.11197v1">DreamNav: A Trajectory-Based Imaginative Framework for Zero-Shot Vision-and-Language Navigation</a></td><td><details><summary>展开</summary>Vision-and-Language Navigation in Continuous Environments (VLN-CE), which
links language instructions to perception and control in the real world, is a
core capability of embodied robots. Recently, large-scale pretrained foundation
models have been leveraged as shared priors for perception, reasoning, and
action, enabling zero-shot VLN without task-specific training. However,
existing zero-shot VLN methods depend on costly perception and passive scene
understanding, collapsing control to point-level choices. As a result, they are
expensive to deploy, misaligned in action semantics, and short-sighted in
planning. To address these issues, we present DreamNav that focuses on the
following three aspects: (1) for reducing sensory cost, our EgoView Corrector
aligns viewpoints and stabilizes egocentric perception; (2) instead of
point-level actions, our Trajectory Predictor favors global trajectory-level
planning to better align with instruction semantics; and (3) to enable
anticipatory and long-horizon planning, we propose an Imagination Predictor to
endow the agent with proactive thinking capability. On VLN-CE and real-world
tests, DreamNav sets a new zero-shot state-of-the-art (SOTA), outperforming the
strongest egocentric baseline with extra information by up to 7.49\% and
18.15\% in terms of SR and SPL metrics. To our knowledge, this is the first
zero-shot VLN method to unify trajectory-level planning and active imagination
while using only egocentric inputs.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.11196v1">Federated Recommender System with Data Valuation for E-commerce Platform</a></td><td><details><summary>展开</summary>Federated Learning (FL) is gaining prominence in machine learning as privacy
concerns grow. This paradigm allows each client (e.g., an individual online
store) to train a recommendation model locally while sharing only model
updates, without exposing the raw interaction logs to a central server, thereby
preserving privacy in a decentralized environment. Nonetheless, most existing
FL-based recommender systems still rely solely on each client's private data,
despite the abundance of publicly available datasets that could be leveraged to
enrich local training; this potential remains largely underexplored. To this
end, we consider a realistic scenario wherein a large shopping platform
collaborates with multiple small online stores to build a global recommender
system. The platform possesses global data, such as shareable user and item
lists, while each store holds a portion of interaction data privately (or
locally). Although integrating global data can help mitigate the limitations of
sparse and biased clients' local data, it also introduces additional
challenges: simply combining all global interactions can amplify noise and
irrelevant patterns, worsening personalization and increasing computational
costs. To address these challenges, we propose FedGDVE, which selectively
augments each client's local graph with semantically aligned samples from the
global dataset. FedGDVE employs: (i) a pre-trained graph encoder to extract
global structural features, (ii) a local valid predictor to assess
client-specific relevance, (iii) a reinforcement-learning-based probability
estimator to filter and sample only the most pertinent global interactions.
FedGDVE improves performance by up to 34.86% on recognized benchmarks in FL
environments.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.11167v1">Harnessing Optimization Dynamics for Curvature-Informed Model Merging</a></td><td><details><summary>展开</summary>Model merging is an effective post-training strategy for composing
capabilities in large language models without joint retraining. We study this
in the supervised fine-tuning (SFT) stage, where multiple capability-based SFT
checkpoints -- spanning math, code, precise instruction following, general
instruction following, and knowledge recall -- must be consolidated into a
single model. We introduce Optimization Trajectory Aware (OTA) Merging, a
curvature-aware aggregation that leverages optimizer second-moment statistics
as a diagonal curvature proxy to reweight parameter edits and mitigate
interference. Complementing OTA, we propose Fast Fisher Grafting (FFG), a
curvature-driven task-localization step that sparsifies conflicting or
low-importance edits. FFG induces extremely low-rank masks concentrated in
early attention query/key projections and token embeddings, exploiting shared
curvature across capabilities. We further develop a memory-light compression of
the second moments that preserves OTA's effect. Across diverse capability-based
SFT checkpoints, OTA+FFG improves merged-model quality over strong weight-space
baselines, reduces negative transfer, and remains robust across sparsity
levels. Analyses reveal substantial curvature overlap between checkpoints,
offering a novel lens on why simple linear merging can be effective in
practice. Ablations confirm that FFG is critical for reducing task interference
and that the compressed second moments retain the gains of the full
formulation. To facilitate reproducibility, we open-source all code, training
and evaluation scripts, visualization artifacts, and capability-specific SFT
checkpoints at https://github.com/pmahdavi/ota-merge.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.13352v1">Agentic UAVs: LLM-Driven Autonomy with Integrated Tool-Calling and Cognitive Reasoning</a></td><td><details><summary>展开</summary>Unmanned Aerial Vehicles (UAVs) are increasingly deployed in defense,
surveillance, and disaster response, yet most systems remain confined to SAE
Level 2--3 autonomy. Their reliance on rule-based control and narrow AI
restricts adaptability in dynamic, uncertain missions. Existing UAV frameworks
lack context-aware reasoning, autonomous decision-making, and ecosystem-level
integration; critically, none leverage Large Language Model (LLM) agents with
tool-calling for real-time knowledge access. This paper introduces the Agentic
UAVs framework, a five-layer architecture (Perception, Reasoning, Action,
Integration, Learning) that augments UAVs with LLM-driven reasoning, database
querying, and third-party system interaction. A ROS2 and Gazebo-based prototype
integrates YOLOv11 object detection with GPT-4 reasoning and local Gemma-3
deployment. In simulated search-and-rescue scenarios, agentic UAVs achieved
higher detection confidence (0.79 vs. 0.72), improved person detection rates
(91% vs. 75%), and markedly increased action recommendation (92% vs. 4.5%).
These results confirm that modest computational overhead enables qualitatively
new levels of autonomy and ecosystem integration.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.12279v1">Domain Adaptive SAR Wake Detection: Leveraging Similarity Filtering and Memory Guidance</a></td><td><details><summary>展开</summary>Synthetic Aperture Radar (SAR), with its all-weather and wide-area
observation capabilities, serves as a crucial tool for wake detection. However,
due to its complex imaging mechanism, wake features in SAR images often appear
abstract and noisy, posing challenges for accurate annotation. In contrast,
optical images provide more distinct visual cues, but models trained on optical
data suffer from performance degradation when applied to SAR images due to
domain shift. To address this cross-modal domain adaptation challenge, we
propose a Similarity-Guided and Memory-Guided Domain Adaptation (termed
SimMemDA) framework for unsupervised domain adaptive ship wake detection via
instance-level feature similarity filtering and feature memory guidance.
Specifically, to alleviate the visual discrepancy between optical and SAR
images, we first utilize WakeGAN to perform style transfer on optical images,
generating pseudo-images close to the SAR style. Then, instance-level feature
similarity filtering mechanism is designed to identify and prioritize source
samples with target-like distributions, minimizing negative transfer.
Meanwhile, a Feature-Confidence Memory Bank combined with a K-nearest neighbor
confidence-weighted fusion strategy is introduced to dynamically calibrate
pseudo-labels in the target domain, improving the reliability and stability of
pseudo-labels. Finally, the framework further enhances generalization through
region-mixed training, strategically combining source annotations with
calibrated target pseudo-labels. Experimental results demonstrate that the
proposed SimMemDA method can improve the accuracy and robustness of cross-modal
ship wake detection tasks, validating the effectiveness and feasibility of the
proposed method.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.11154v1">Feature Space Topology Control via Hopkins Loss</a></td><td><details><summary>展开</summary>Feature space topology refers to the organization of samples within the
feature space. Modifying this topology can be beneficial in machine learning
applications, including dimensionality reduction, generative modeling, transfer
learning, and robustness to adversarial attacks. This paper introduces a novel
loss function, Hopkins loss, which leverages the Hopkins statistic to enforce a
desired feature space topology, which is in contrast to existing
topology-related methods that aim to preserve input feature topology. We
evaluate the effectiveness of Hopkins loss on speech, text, and image data in
two scenarios: classification and dimensionality reduction using nonlinear
bottleneck autoencoders. Our experiments show that integrating Hopkins loss
into classification or dimensionality reduction has only a small impact on
classification performance while providing the benefit of modifying feature
topology.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.14265v1">Evolution of Kernels: Automated RISC-V Kernel Optimization with Large Language Models</a></td><td><details><summary>展开</summary>Automated kernel design is critical for overcoming software ecosystem
barriers in emerging hardware platforms like RISC-V. While large language
models (LLMs) have shown promise for automated kernel optimization,
demonstrating success in CUDA domains with comprehensive technical documents
and mature codebases, their effectiveness remains unproven for reference-scarce
domains like RISC-V. We present Evolution of Kernels (EoK), a novel LLM-based
evolutionary program search framework that automates kernel design for domains
with limited reference material. EoK mitigates reference scarcity by mining and
formalizing reusable optimization ideas (general design principles + actionable
thoughts) from established kernel libraries' development histories; it then
guides parallel LLM explorations using these ideas, enriched via
Retrieval-Augmented Generation (RAG) with RISC-V-specific context, prioritizing
historically effective techniques. Empirically, EoK achieves a median 1.27x
speedup, surpassing human experts on all 80 evaluated kernel design tasks and
improving upon prior LLM-based automated kernel design methods by 20%. These
results underscore the viability of incorporating human experience into
emerging domains and highlight the immense potential of LLM-based automated
kernel optimization.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.12275v3">Omni-CLST: Error-aware Curriculum Learning with guided Selective chain-of-Thought for audio question answering</a></td><td><details><summary>展开</summary>With the rapid progress of large audio-language models (LALMs), audio
question answering (AQA) has emerged as a challenging task requiring both
fine-grained audio understanding and complex reasoning. While current methods
mainly rely on constructing new datasets via captioning or reasoning traces,
existing high-quality AQA data remains underutilized. To address this, we
propose Omni-CLST, an error-aware Curriculum Learning framework with guided
Selective Chain-of-Thought. The framework efficiently leverages existing
high-quality dataset through two key strategies: an error-aware curriculum that
organizes samples by difficulty, and a guided thought dropout mechanism that
focuses reasoning on challenging cases. Experiments show that Omni-CLST
achieves 73.80% on MMAU-mini and a new state of the art of 64.30% on MMAR,
demonstrating robust generalization in multimodal audio-language understanding.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.11112v1">Multi-Modal Sensing Aided mmWave Beamforming for V2V Communications with Transformers</a></td><td><details><summary>展开</summary>Beamforming techniques are utilized in millimeter wave (mmWave) communication
to address the inherent path loss limitation, thereby establishing and
maintaining reliable connections. However, adopting standard defined
beamforming approach in highly dynamic vehicular environments often incurs high
beam training overheads and reduces the available airtime for communications,
which is mainly due to exchanging pilot signals and exhaustive beam
measurements. To this end, we present a multi-modal sensing and fusion learning
framework as a potential alternative solution to reduce such overheads. In this
framework, we first extract the features individually from the visual and GPS
coordinates sensing modalities by modality specific encoders, and subsequently
fuse the multimodal features to obtain predicted top-k beams so that the best
line-of-sight links can be proactively established. To show the
generalizability of the proposed framework, we perform a comprehensive
experiment in four different vehicle-to-vehicle (V2V) scenarios from real-world
multi-modal sensing and communication dataset. From the experiment, we observe
that the proposed framework achieves up to 77.58% accuracy on predicting top-15
beams correctly, outperforms single modalities, incurs roughly as low as 2.32
dB average power loss, and considerably reduces the beam searching space
overheads by 76.56% for top-15 beams with respect to standard defined approach.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.11079v1">Difficulty-Aware Agent Orchestration in LLM-Powered Workflows</a></td><td><details><summary>展开</summary>Large Language Model (LLM)-based agentic systems have shown strong
capabilities across various tasks. However, existing multi-agent frameworks
often rely on static or task-level workflows, which either over-process simple
queries or underperform on complex ones, while also neglecting the
efficiency-performance trade-offs across heterogeneous LLMs. To address these
limitations, we propose Difficulty-Aware Agentic Orchestration (DAAO), a
dynamic framework that adapts workflow depth, operator selection, and LLM
assignment based on the difficulty of each input query. DAAO comprises three
interdependent modules: a variational autoencoder (VAE) for difficulty
estimation, a modular operator allocator, and a cost- and performance-aware LLM
router. By leveraging heterogeneous LLMs and dynamically tailoring workflows,
DAAO enables fine-grained, query-specific reasoning strategies. DAAO
outperforms prior multi-agent systems in both accuracy and inference efficiency
across six benchmarks. We will release our code and implementation details upon
publication.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.11044v1">FragmentGPT: A Unified GPT Model for Fragment Growing, Linking, and Merging in Molecular Design</a></td><td><details><summary>展开</summary>Fragment-Based Drug Discovery (FBDD) is a popular approach in early drug
development, but designing effective linkers to combine disconnected molecular
fragments into chemically and pharmacologically viable candidates remains
challenging. Further complexity arises when fragments contain structural
redundancies, like duplicate rings, which cannot be addressed by simply adding
or removing atoms or bonds. To address these challenges in a unified framework,
we introduce FragmentGPT, which integrates two core components: (1) a novel
chemically-aware, energy-based bond cleavage pre-training strategy that equips
the GPT-based model with fragment growing, linking, and merging capabilities,
and (2) a novel Reward Ranked Alignment with Expert Exploration (RAE) algorithm
that combines expert imitation learning for diversity enhancement, data
selection and augmentation for Pareto and composite score optimality, and
Supervised Fine-Tuning (SFT) to align the learner policy with multi-objective
goals. Conditioned on fragment pairs, FragmentGPT generates linkers that
connect diverse molecular subunits while simultaneously optimizing for multiple
pharmaceutical goals. It also learns to resolve structural redundancies-such as
duplicated fragments-through intelligent merging, enabling the synthesis of
optimized molecules. FragmentGPT facilitates controlled, goal-driven molecular
assembly. Experiments and ablation studies on real-world cancer datasets
demonstrate its ability to generate chemically valid, high-quality molecules
tailored for downstream drug discovery tasks.</details></td></tr></tbody></table>

### 📅 2025-09-13
<table style='width:100%;'><colgroup><col style="width:61.8%;"><col style="width:38.2%;"></colgroup><thead><tr><th>title</th><th>abstract</th></tr></thead><tbody><tr><td><a href="http://arxiv.org/abs/2509.11000v1">Hardness, Structural Knowledge, and Opportunity: An Analytical Framework for Modular Performance Modeling</a></td><td><details><summary>展开</summary>Performance-influence models are beneficial for understanding how
configurations affect system performance, but their creation is challenging due
to the exponential growth of configuration spaces. While gray-box approaches
leverage selective "structural knowledge" (like the module execution graph of
the system) to improve modeling, the relationship between this knowledge, a
system's characteristics (we call them "structural aspects"), and potential
model improvements is not well understood. This paper addresses this gap by
formally investigating how variations in structural aspects (e.g., the number
of modules and options per module) and the level of structural knowledge impact
the creation of "opportunities" for improved "modular performance modeling". We
introduce and quantify the concept of modeling "hardness", defined as the
inherent difficulty of performance modeling. Through controlled experiments
with synthetic system models, we establish an "analytical matrix" to measure
these concepts. Our findings show that modeling hardness is primarily driven by
the number of modules and configuration options per module. More importantly,
we demonstrate that both higher levels of structural knowledge and increased
modeling hardness significantly enhance the opportunity for improvement. The
impact of these factors varies by performance metric; for ranking accuracy
(e.g., in debugging task), structural knowledge is more dominant, while for
prediction accuracy (e.g., in resource management task), hardness plays a
stronger role. These results provide actionable insights for system designers,
guiding them to strategically allocate time and select appropriate modeling
approaches based on a system's characteristics and a given task's objectives.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.10972v1">Enhancing Computational Cognitive Architectures with LLMs: A Case Study</a></td><td><details><summary>展开</summary>Computational cognitive architectures are broadly scoped models of the human
mind that combine different psychological functionalities (as well as often
different computational methods for these different functionalities) into one
unified framework. They structure them in a psychologically plausible and
validated way. However, such models thus far have only limited computational
capabilities, mostly limited by the computational tools and techniques that
were adopted. More recently, LLMs have proved to be more capable
computationally than any other tools. Thus, in order to deal with both
real-world complexity and psychological realism at the same time, incorporating
LLMs into cognitive architectures naturally becomes an important task. In the
present article, a synergistic combination of the Clarion cognitive
architecture and LLMs is discussed as a case study. The implicit-explicit
dichotomy that is fundamental to Clarion is leveraged for a seamless
integration of Clarion and LLMs. As a result, computational power of LLMs is
combined with psychological nicety of Clarion.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.10946v1">When the Code Autopilot Breaks: Why LLMs Falter in Embedded Machine Learning</a></td><td><details><summary>展开</summary>Large Language Models (LLMs) are increasingly used to automate software
generation in embedded machine learning workflows, yet their outputs often fail
silently or behave unpredictably. This article presents an empirical
investigation of failure modes in LLM-powered ML pipelines, based on an
autopilot framework that orchestrates data preprocessing, model conversion, and
on-device inference code generation. We show how prompt format, model behavior,
and structural assumptions influence both success rates and failure
characteristics, often in ways that standard validation pipelines fail to
detect. Our analysis reveals a diverse set of error-prone behaviors, including
format-induced misinterpretations and runtime-disruptive code that compiles but
breaks downstream. We derive a taxonomy of failure categories and analyze
errors across multiple LLMs, highlighting common root causes and systemic
fragilities. Though grounded in specific devices, our study reveals broader
challenges in LLM-based code generation. We conclude by discussing directions
for improving reliability and traceability in LLM-powered embedded ML systems.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.10886v1">CultureSynth: A Hierarchical Taxonomy-Guided and Retrieval-Augmented Framework for Cultural Question-Answer Synthesis</a></td><td><details><summary>展开</summary>Cultural competence, defined as the ability to understand and adapt to
multicultural contexts, is increasingly vital for large language models (LLMs)
in global environments. While several cultural benchmarks exist to assess LLMs'
cultural competence, current evaluations suffer from fragmented taxonomies,
domain specificity, and heavy reliance on manual data annotation. To address
these limitations, we introduce CultureSynth, a novel framework comprising (1)
a comprehensive hierarchical multilingual cultural taxonomy covering 12 primary
and 130 secondary topics, and (2) a Retrieval-Augmented Generation (RAG)-based
methodology leveraging factual knowledge to synthesize culturally relevant
question-answer pairs. The CultureSynth-7 synthetic benchmark contains 19,360
entries and 4,149 manually verified entries across 7 languages. Evaluation of
14 prevalent LLMs of different sizes reveals clear performance stratification
led by ChatGPT-4o-Latest and Qwen2.5-72B-Instruct. The results demonstrate that
a 3B-parameter threshold is necessary for achieving basic cultural competence,
models display varying architectural biases in knowledge processing, and
significant geographic disparities exist across models. We believe that
CultureSynth offers a scalable framework for developing culturally aware AI
systems while reducing reliance on manual annotation\footnote{Benchmark is
available at https://github.com/Eyr3/CultureSynth.}.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.10858v1">Large Language Models for Security Operations Centers: A Comprehensive Survey</a></td><td><details><summary>展开</summary>Large Language Models (LLMs) have emerged as powerful tools capable of
understanding and generating human-like text, offering transformative potential
across diverse domains. The Security Operations Center (SOC), responsible for
safeguarding digital infrastructure, represents one of these domains. SOCs
serve as the frontline of defense in cybersecurity, tasked with continuous
monitoring, detection, and response to incidents. However, SOCs face persistent
challenges such as high alert volumes, limited resources, high demand for
experts with advanced knowledge, delayed response times, and difficulties in
leveraging threat intelligence effectively. In this context, LLMs can offer
promising solutions by automating log analysis, streamlining triage, improving
detection accuracy, and providing the required knowledge in less time. This
survey systematically explores the integration of generative AI and more
specifically LLMs into SOC workflow, providing a structured perspective on its
capabilities, challenges, and future directions. We believe that this survey
offers researchers and SOC managers a broad overview of the current state of
LLM integration within academic study. To the best of our knowledge, this is
the first comprehensive study to examine LLM applications in SOCs in details.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.10852v1">Pre-Storage Reasoning for Episodic Memory: Shifting Inference Burden to Memory for Personalized Dialogue</a></td><td><details><summary>展开</summary>Effective long-term memory in conversational AI requires synthesizing
information across multiple sessions. However, current systems place excessive
reasoning burden on response generation, making performance significantly
dependent on model sizes. We introduce PREMem (Pre-storage Reasoning for
Episodic Memory), a novel approach that shifts complex reasoning processes from
inference to memory construction. PREMem extracts fine-grained memory fragments
categorized into factual, experiential, and subjective information; it then
establishes explicit relationships between memory items across sessions,
capturing evolution patterns like extensions, transformations, and
implications. By performing this reasoning during pre-storage rather than when
generating a response, PREMem creates enriched representations while reducing
computational demands during interactions. Experiments show significant
performance improvements across all model sizes, with smaller models achieving
results comparable to much larger baselines while maintaining effectiveness
even with constrained token budgets. Code and dataset are available at
https://github.com/sangyeop-kim/PREMem.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.10833v1">Towards Automated Error Discovery: A Study in Conversational AI</a></td><td><details><summary>展开</summary>Although LLM-based conversational agents demonstrate strong fluency and
coherence, they still produce undesirable behaviors (errors) that are
challenging to prevent from reaching users during deployment. Recent research
leverages large language models (LLMs) to detect errors and guide
response-generation models toward improvement. However, current LLMs struggle
to identify errors not explicitly specified in their instructions, such as
those arising from updates to the response-generation model or shifts in user
behavior. In this work, we introduce Automated Error Discovery, a framework for
detecting and defining errors in conversational AI, and propose SEEED (Soft
Clustering Extended Encoder-Based Error Detection), as an encoder-based
approach to its implementation. We enhance the Soft Nearest Neighbor Loss by
amplifying distance weighting for negative samples and introduce Label-Based
Sample Ranking to select highly contrastive examples for better representation
learning. SEEED outperforms adapted baselines -- including GPT-4o and Phi-4 --
across multiple error-annotated dialogue datasets, improving the accuracy for
detecting unknown errors by up to 8 points and demonstrating strong
generalization to unknown intent detection.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.10818v1">LLM Enhancement with Domain Expert Mental Model to Reduce LLM Hallucination with Causal Prompt Engineering</a></td><td><details><summary>展开</summary>Difficult decision-making problems abound in various disciplines and domains.
The proliferation of generative techniques, especially large language models
(LLMs), has excited interest in using them for decision support. However, LLMs
cannot yet resolve missingness in their training data, leading to
hallucinations. Retrieval-Augmented Generation (RAG) enhances LLMs by
incorporating external information retrieval, reducing hallucinations and
improving accuracy. Yet, RAG and related methods are only partial solutions, as
they may lack access to all necessary sources or key missing information. Even
everyday issues often challenge LLMs' abilities. Submitting longer prompts with
context and examples is one approach to address knowledge gaps, but designing
effective prompts is non-trivial and may not capture complex mental models of
domain experts. For tasks with missing critical information, LLMs are
insufficient, as are many existing systems poorly represented in available
documents. This paper explores how LLMs can make decision-making more
efficient, using a running example of evaluating whether to respond to a call
for proposals. We propose a technology based on optimized human-machine
dialogue and monotone Boolean and k-valued functions to discover a
computationally tractable personal expert mental model (EMM) of
decision-making. Our EMM algorithm for LLM prompt engineering has four steps:
(1) factor identification, (2) hierarchical structuring of factors, (3)
generating a generalized expert mental model specification, and (4) generating
a detailed generalized expert mental model from that specification.</details></td></tr></tbody></table>

### 📅 2025-09-12
<table style='width:100%;'><colgroup><col style="width:61.8%;"><col style="width:38.2%;"></colgroup><thead><tr><th>title</th><th>abstract</th></tr></thead><tbody><tr><td><a href="http://arxiv.org/abs/2509.10744v1">Automated MCQA Benchmarking at Scale: Evaluating Reasoning Traces as Retrieval Sources for Domain Adaptation of Small Language Models</a></td><td><details><summary>展开</summary>As scientific knowledge grows at an unprecedented pace, evaluation benchmarks
must evolve to reflect new discoveries and ensure language models are tested on
current, diverse literature. We propose a scalable, modular framework for
generating multiple-choice question-answering (MCQA) benchmarks directly from
large corpora of scientific papers. Our pipeline automates every stage of MCQA
creation, including PDF parsing, semantic chunking, question generation, and
model evaluation. As a case study, we generate more than 16,000 MCQs from
22,000 open-access articles in radiation and cancer biology. We then evaluate a
suite of small language models (1.1B-14B parameters) on these questions,
comparing baseline accuracy with retrieval-augmented generation (RAG) from
paper-derived semantic chunks and from reasoning traces distilled from GPT-4.1.
We find that reasoning-trace retrieval consistently improves performance on
both synthetic and expert-annotated benchmarks, enabling several small models
to surpass GPT-4 on the 2023 Astro Radiation and Cancer Biology exam.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.10693v1">Learning Concave Bid Shading Strategies in Online Auctions via Measure-valued Proximal Optimization</a></td><td><details><summary>展开</summary>This work proposes a bid shading strategy for first-price auctions as a
measure-valued optimization problem. We consider a standard parametric form for
bid shading and formulate the problem as convex optimization over the joint
distribution of shading parameters. After each auction, the shading parameter
distribution is adapted via a regularized Wasserstein-proximal update with a
data-driven energy functional. This energy functional is conditional on the
context, i.e., on publisher/user attributes such as domain, ad slot type,
device, or location. The proposed algorithm encourages the bid distribution to
place more weight on values with higher expected surplus, i.e., where the win
probability and the value gap are both large. We show that the resulting
measure-valued convex optimization problem admits a closed form solution. A
numerical example illustrates the proposed method.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.13345v1">Accuracy Paradox in Large Language Models: Regulating Hallucination Risks in Generative AI</a></td><td><details><summary>展开</summary>As Large Language Models (LLMs) permeate everyday decision-making, their
epistemic and societal risks demand urgent scrutiny. Hallucinations, the
generation of fabricated, misleading, oversimplified or untrustworthy outputs,
has emerged as imperative challenges. While regulatory, academic, and technical
discourse position accuracy as the principal benchmark for mitigating such
harms, this article contends that overreliance on accuracy misdiagnoses the
problem and has counterproductive effect: the accuracy paradox. Drawing on
interdisciplinary literatures, this article develops a taxonomy of
hallucination types and shows the paradox along three intertwining dimensions:
outputs, individuals and society. First, accuracy functions as a superficial
proxy for reliability, incentivising the optimisation of rhetorical fluency and
surface-level correctness over epistemic trustworthiness. This encourages
passive user trust in outputs that appear accurate but epistemically untenable.
Second, accuracy as a singular metric fails to detect harms that are not
factually false but are nonetheless misleading, value-laden, or socially
distorting, including consensus illusions, sycophantic alignment, and subtle
manipulation. Third, regulatory overemphasis on accuracy obscures the wider
societal consequences of hallucination, including social sorting, privacy
violations, equity harms, epistemic convergence that marginalises dissent,
reduces pluralism, and causes social deskilling. By examining the EU AI Act,
GDPR, and DSA, the article argues that current regulations are not yet
structurally equipped to address these epistemic, relational, and systemic
harms and exacerbated by the overreliance on accuracy. By exposing such
conceptual and practical challenges, this article calls for a fundamental shift
towards pluralistic, context-aware, and manipulation-resilient approaches to AI
trustworthy governance.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.10656v1">Self-Supervised Goal-Reaching Results in Multi-Agent Cooperation and Exploration</a></td><td><details><summary>展开</summary>For groups of autonomous agents to achieve a particular goal, they must
engage in coordination and long-horizon reasoning. However, designing reward
functions to elicit such behavior is challenging. In this paper, we study how
self-supervised goal-reaching techniques can be leveraged to enable agents to
cooperate. The key idea is that, rather than have agents maximize some scalar
reward, agents aim to maximize the likelihood of visiting a certain goal. This
problem setting enables human users to specify tasks via a single goal state
rather than implementing a complex reward function. While the feedback signal
is quite sparse, we will demonstrate that self-supervised goal-reaching
techniques enable agents to learn from such feedback. On MARL benchmarks, our
proposed method outperforms alternative approaches that have access to the same
sparse reward signal as our method. While our method has no explicit mechanism
for exploration, we observe that self-supervised multi-agent goal-reaching
leads to emergent cooperation and exploration in settings where alternative
approaches never witness a single successful trial.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.10653v1">SCOR: A Framework for Responsible AI Innovation in Digital Ecosystems</a></td><td><details><summary>展开</summary>AI-driven digital ecosystems span diverse stakeholders including technology
firms, regulators, accelerators and civil society, yet often lack cohesive
ethical governance. This paper proposes a four-pillar framework (SCOR) to embed
accountability, fairness, and inclusivity across such multi-actor networks.
Leveraging a design science approach, we develop a Shared Ethical Charter(S),
structured Co-Design and Stakeholder Engagement protocols(C), a system of
Continuous Oversight and Learning(O), and Adaptive Regulatory Alignment
strategies(R). Each component includes practical guidance, from lite modules
for resource-constrained start-ups to in-depth auditing systems for larger
consortia. Through illustrative vignettes in healthcare, finance, and smart
city contexts, we demonstrate how the framework can harmonize organizational
culture, leadership incentives, and cross-jurisdictional compliance. Our
mixed-method KPI design further ensures that quantitative targets are
complemented by qualitative assessments of user trust and cultural change. By
uniting ethical principles with scalable operational structures, this paper
offers a replicable pathway toward responsible AI innovation in complex digital
ecosystems.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.10641v1">Test-Time Warmup for Multimodal Large Language Models</a></td><td><details><summary>展开</summary>Multimodal Large Language Models (MLLMs) hold great promise for advanced
reasoning at the intersection of text and images, yet they have not fully
realized this potential. MLLMs typically integrate an LLM, a vision encoder,
and a connector that maps the vision encoder's embeddings into the LLM's text
embedding space. Although each component is pretrained on massive datasets with
billions of samples, the entire multimodal model is typically trained on only
thousands (or a few million) samples, which can result in weak performance on
complex reasoning tasks. To address these shortcomings, instead of relying on
extensive labeled datasets for fine-tuning, we propose a Test-Time Warmup
method that adapts the MLLM per test instance by leveraging data from weakly
supervised auxiliary tasks. With our approach, we observe a relative
performance improvement of 4.03% on MMMU, 5.28% on VQA-Rad, and 1.63% on GQA on
the Llama-Vision-Instruct model. Our method demonstrates that 'warming up'
before inference can enhance MLLMs' robustness across diverse reasoning tasks.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.10401v1">Abduct, Act, Predict: Scaffolding Causal Inference for Automated Failure Attribution in Multi-Agent Systems</a></td><td><details><summary>展开</summary>Failure attribution in multi-agent systems -- pinpointing the exact step
where a decisive error occurs -- is a critical yet unsolved challenge. Current
methods treat this as a pattern recognition task over long conversation logs,
leading to critically low step-level accuracy (below 17\%), which renders them
impractical for debugging complex systems. Their core weakness is a fundamental
inability to perform robust counterfactual reasoning: to determine if
correcting a single action would have actually averted the task failure. To
bridge this counterfactual inference gap, we introduce Abduct-Act-Predict (A2P)
Scaffolding, a novel agent framework that transforms failure attribution from
pattern recognition into a structured causal inference task. A2P explicitly
guides a large language model through a formal three-step reasoning process
within a single inference pass: (1) Abduction, to infer the hidden root causes
behind an agent's actions; (2) Action, to define a minimal corrective
intervention; and (3) Prediction, to simulate the subsequent trajectory and
verify if the intervention resolves the failure. This structured approach
leverages the holistic context of the entire conversation while imposing a
rigorous causal logic on the model's analysis. Our extensive experiments on the
Who\&When benchmark demonstrate its efficacy. On the Algorithm-Generated
dataset, A2P achieves 47.46\% step-level accuracy, a 2.85$\times$ improvement
over the 16.67\% of the baseline. On the more complex Hand-Crafted dataset, it
achieves 29.31\% step accuracy, a 2.43$\times$ improvement over the baseline's
12.07\%. By reframing the problem through a causal lens, A2P Scaffolding
provides a robust, verifiable, and significantly more accurate solution for
automated failure attribution.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.10344v1">GLAM: Geometry-Guided Local Alignment for Multi-View VLP in Mammography</a></td><td><details><summary>展开</summary>Mammography screening is an essential tool for early detection of breast
cancer. The speed and accuracy of mammography interpretation have the potential
to be improved with deep learning methods. However, the development of a
foundation visual language model (VLM) is hindered by limited data and domain
differences between natural and medical images. Existing mammography VLMs,
adapted from natural images, often ignore domain-specific characteristics, such
as multi-view relationships in mammography. Unlike radiologists who analyze
both views together to process ipsilateral correspondence, current methods
treat them as independent images or do not properly model the multi-view
correspondence learning, losing critical geometric context and resulting in
suboptimal prediction. We propose GLAM: Global and Local Alignment for
Multi-view mammography for VLM pretraining using geometry guidance. By
leveraging the prior knowledge about the multi-view imaging process of
mammograms, our model learns local cross-view alignments and fine-grained local
features through joint global and local, visual-visual, and visual-language
contrastive learning. Pretrained on EMBED [14], one of the largest open
mammography datasets, our model outperforms baselines across multiple datasets
under different settings.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.10334v1">I-Segmenter: Integer-Only Vision Transformer for Efficient Semantic Segmentation</a></td><td><details><summary>展开</summary>Vision Transformers (ViTs) have recently achieved strong results in semantic
segmentation, yet their deployment on resource-constrained devices remains
limited due to their high memory footprint and computational cost. Quantization
offers an effective strategy to improve efficiency, but ViT-based segmentation
models are notoriously fragile under low precision, as quantization errors
accumulate across deep encoder-decoder pipelines. We introduce I-Segmenter, the
first fully integer-only ViT segmentation framework. Building on the Segmenter
architecture, I-Segmenter systematically replaces floating-point operations
with integer-only counterparts. To further stabilize both training and
inference, we propose $\lambda$-ShiftGELU, a novel activation function that
mitigates the limitations of uniform quantization in handling long-tailed
activation distributions. In addition, we remove the L2 normalization layer and
replace bilinear interpolation in the decoder with nearest neighbor upsampling,
ensuring integer-only execution throughout the computational graph. Extensive
experiments show that I-Segmenter achieves accuracy within a reasonable margin
of its FP32 baseline (5.1 % on average), while reducing model size by up to
3.8x and enabling up to 1.2x faster inference with optimized runtimes. Notably,
even in one-shot PTQ with a single calibration image, I-Segmenter delivers
competitive accuracy, underscoring its practicality for real-world deployment.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.10594v1">SME-TEAM: Leveraging Trust and Ethics for Secure and Responsible Use of AI and LLMs in SMEs</a></td><td><details><summary>展开</summary>Artificial Intelligence (AI) and Large Language Models (LLMs) are reshaping
today's business practices, however, their adoption within small and
medium-sized enterprises (SMEs) raises significant technical, ethical and trust
issues. This paper proposes a structured, multi-phased framework designed to
embed trust and ethical principles throughout the AI lifecycle for their secure
and responsible use in SMEs. Structured around four pillars, i.e., Data,
Algorithms, Human oversight, and Model Architecture, the framework bridges
theoretical ethical principles with operational practice, enhancing AI
capabilities in diverse SME applications. Ultimately, this paper offers a
structured roadmap for responsible AI adoption, framing trust and ethics as a
catalyst for resilience, competitiveness, and sustainable innovation in SMEs.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.10266v1">SignClip: Leveraging Mouthing Cues for Sign Language Translation by Multimodal Contrastive Fusion</a></td><td><details><summary>展开</summary>Sign language translation (SLT) aims to translate natural language from sign
language videos, serving as a vital bridge for inclusive communication. While
recent advances leverage powerful visual backbones and large language models,
most approaches mainly focus on manual signals (hand gestures) and tend to
overlook non-manual cues like mouthing. In fact, mouthing conveys essential
linguistic information in sign languages and plays a crucial role in
disambiguating visually similar signs. In this paper, we propose SignClip, a
novel framework to improve the accuracy of sign language translation. It fuses
manual and non-manual cues, specifically spatial gesture and lip movement
features. Besides, SignClip introduces a hierarchical contrastive learning
framework with multi-level alignment objectives, ensuring semantic consistency
across sign-lip and visual-text modalities. Extensive experiments on two
benchmark datasets, PHOENIX14T and How2Sign, demonstrate the superiority of our
approach. For example, on PHOENIX14T, in the Gloss-free setting, SignClip
surpasses the previous state-of-the-art model SpaMo, improving BLEU-4 from
24.32 to 24.71, and ROUGE from 46.57 to 48.38.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.10590v1">Machine Unlearning for Responsible and Adaptive AI in Education</a></td><td><details><summary>展开</summary>The concept of Machine Unlearning (MU) has gained popularity in various
domains due to its ability to address several issues in Machine Learning (ML)
models, particularly those related to privacy, security, bias mitigation, and
adaptability. With these abilities, MU is evolving into a promising technology
in upholding Responsible AI principles and optimizing ML models' performance.
However, despite its promising potential, the concept has not received much
attention in the education sector. In an attempt to encourage further uptake of
this promising technology in the educational landscape, this paper demonstrates
that MU indeed has great potential to serve as a practical mechanism for
operationalizing Responsible AI principles as well as an essential tool for
Adaptive AI within the educational application domain hence fostering trust in
AI-driven educational systems. Through a structured review of 42 peer-reviewed
sources, we identify four domains where MU holds particular promise namely
privacy protection, resilience against adversarial inputs, mitigation of
systemic bias, and adaptability in evolving learning contexts. We
systematically explore these potentials and their interventions to core
challenges in ML-based education systems. As a conceptual contribution, we
present a reference Machine Unlearning application architecture for Responsible
and Adaptive AI (MU-RAAI) in education context.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.10162v1">Online Robust Planning under Model Uncertainty: A Sample-Based Approach</a></td><td><details><summary>展开</summary>Online planning in Markov Decision Processes (MDPs) enables agents to make
sequential decisions by simulating future trajectories from the current state,
making it well-suited for large-scale or dynamic environments. Sample-based
methods such as Sparse Sampling and Monte Carlo Tree Search (MCTS) are widely
adopted for their ability to approximate optimal actions using a generative
model. However, in practical settings, the generative model is often learned
from limited data, introducing approximation errors that can degrade
performance or lead to unsafe behaviors. To address these challenges, Robust
MDPs (RMDPs) offer a principled framework for planning under model uncertainty,
yet existing approaches are typically computationally intensive and not suited
for real-time use. In this work, we introduce Robust Sparse Sampling (RSS), the
first online planning algorithm for RMDPs with finite-sample theoretical
performance guarantees. Unlike Sparse Sampling, which estimates the nominal
value function, RSS computes a robust value function by leveraging the
efficiency and theoretical properties of Sample Average Approximation (SAA),
enabling tractable robust policy computation in online settings. RSS is
applicable to infinite or continuous state spaces, and its sample and
computational complexities are independent of the state space size. We provide
theoretical performance guarantees and empirically show that RSS outperforms
standard Sparse Sampling in environments with uncertain dynamics.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.10127v1">Population-Aligned Persona Generation for LLM-based Social Simulation</a></td><td><details><summary>展开</summary>Recent advances in large language models (LLMs) have enabled human-like
social simulations at unprecedented scale and fidelity, offering new
opportunities for computational social science. A key challenge, however, is
the construction of persona sets that authentically represent the diversity and
distribution of real-world populations. Most existing LLM-based social
simulation studies focus primarily on designing agentic frameworks and
simulation environments, often overlooking the complexities of persona
generation and the potential biases introduced by unrepresentative persona
sets. In this paper, we propose a systematic framework for synthesizing
high-quality, population-aligned persona sets for LLM-driven social simulation.
Our approach begins by leveraging LLMs to generate narrative personas from
long-term social media data, followed by rigorous quality assessment to filter
out low-fidelity profiles. We then apply importance sampling to achieve global
alignment with reference psychometric distributions, such as the Big Five
personality traits. To address the needs of specific simulation contexts, we
further introduce a task-specific module that adapts the globally aligned
persona set to targeted subpopulations. Extensive experiments demonstrate that
our method significantly reduces population-level bias and enables accurate,
flexible social simulation for a wide range of research and policy
applications.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.10104v1">AI Harmonics: a human-centric and harms severity-adaptive AI risk assessment framework</a></td><td><details><summary>展开</summary>The absolute dominance of Artificial Intelligence (AI) introduces
unprecedented societal harms and risks. Existing AI risk assessment models
focus on internal compliance, often neglecting diverse stakeholder perspectives
and real-world consequences. We propose a paradigm shift to a human-centric,
harm-severity adaptive approach grounded in empirical incident data. We present
AI Harmonics, which includes a novel AI harm assessment metric (AIH) that
leverages ordinal severity data to capture relative impact without requiring
precise numerical estimates. AI Harmonics combines a robust, generalized
methodology with a data-driven, stakeholder-aware framework for exploring and
prioritizing AI harms. Experiments on annotated incident data confirm that
political and physical harms exhibit the highest concentration and thus warrant
urgent mitigation: political harms erode public trust, while physical harms
pose serious, even life-threatening risks, underscoring the real-world
relevance of our approach. Finally, we demonstrate that AI Harmonics
consistently identifies uneven harm distributions, enabling policymakers and
organizations to target their mitigation efforts effectively.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.12250v1">OnlineHOI: Towards Online Human-Object Interaction Generation and Perception</a></td><td><details><summary>展开</summary>The perception and generation of Human-Object Interaction (HOI) are crucial
for fields such as robotics, AR/VR, and human behavior understanding. However,
current approaches model this task in an offline setting, where information at
each time step can be drawn from the entire interaction sequence. In contrast,
in real-world scenarios, the information available at each time step comes only
from the current moment and historical data, i.e., an online setting. We find
that offline methods perform poorly in an online context. Based on this
observation, we propose two new tasks: Online HOI Generation and Perception. To
address this task, we introduce the OnlineHOI framework, a network architecture
based on the Mamba framework that employs a memory mechanism. By leveraging
Mamba's powerful modeling capabilities for streaming data and the Memory
mechanism's efficient integration of historical information, we achieve
state-of-the-art results on the Core4D and OAKINK2 online generation tasks, as
well as the online HOI4D perception task.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.10004v1">Unsupervised Hallucination Detection by Inspecting Reasoning Processes</a></td><td><details><summary>展开</summary>Unsupervised hallucination detection aims to identify hallucinated content
generated by large language models (LLMs) without relying on labeled data.
While unsupervised methods have gained popularity by eliminating
labor-intensive human annotations, they frequently rely on proxy signals
unrelated to factual correctness. This misalignment biases detection probes
toward superficial or non-truth-related aspects, limiting generalizability
across datasets and scenarios. To overcome these limitations, we propose IRIS,
an unsupervised hallucination detection framework, leveraging internal
representations intrinsic to factual correctness. IRIS prompts the LLM to
carefully verify the truthfulness of a given statement, and obtain its
contextualized embedding as informative features for training. Meanwhile, the
uncertainty of each response is considered a soft pseudolabel for truthfulness.
Experimental results demonstrate that IRIS consistently outperforms existing
unsupervised methods. Our approach is fully unsupervised, computationally low
cost, and works well even with few training data, making it suitable for
real-time detection.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.09970v1">Securing LLM-Generated Embedded Firmware through AI Agent-Driven Validation and Patching</a></td><td><details><summary>展开</summary>Large Language Models (LLMs) show promise in generating firmware for embedded
systems, but often introduce security flaws and fail to meet real-time
performance constraints. This paper proposes a three-phase methodology that
combines LLM-based firmware generation with automated security validation and
iterative refinement in a virtualized environment. Using structured prompts,
models like GPT-4 generate firmware for networking and control tasks, deployed
on FreeRTOS via QEMU. These implementations are tested using fuzzing, static
analysis, and runtime monitoring to detect vulnerabilities such as buffer
overflows (CWE-120), race conditions (CWE-362), and denial-of-service threats
(CWE-400). Specialized AI agents for Threat Detection, Performance
Optimization, and Compliance Verification collaborate to improve detection and
remediation. Identified issues are categorized using CWE, then used to prompt
targeted LLM-generated patches in an iterative loop. Experiments show a 92.4\%
Vulnerability Remediation Rate (37.3\% improvement), 95.8\% Threat Model
Compliance, and 0.87 Security Coverage Index. Real-time metrics include 8.6ms
worst-case execution time and 195{\mu}s jitter. This process enhances firmware
security and performance while contributing an open-source dataset for future
research.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.09969v1">Large Language Models Meet Legal Artificial Intelligence: A Survey</a></td><td><details><summary>展开</summary>Large Language Models (LLMs) have significantly advanced the development of
Legal Artificial Intelligence (Legal AI) in recent years, enhancing the
efficiency and accuracy of legal tasks. To advance research and applications of
LLM-based approaches in legal domain, this paper provides a comprehensive
review of 16 legal LLMs series and 47 LLM-based frameworks for legal tasks, and
also gather 15 benchmarks and 29 datasets to evaluate different legal
capabilities. Additionally, we analyse the challenges and discuss future
directions for LLM-based approaches in the legal domain. We hope this paper
provides a systematic introduction for beginners and encourages future research
in this field. Resources are available at
https://github.com/ZhitianHou/LLMs4LegalAI.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.09955v1">Adaptive Token Merging for Efficient Transformer Semantic Communication at the Edge</a></td><td><details><summary>展开</summary>Large-scale transformers are central to modern semantic communication, yet
their high computational and communication costs hinder deployment on
resource-constrained edge devices. This paper introduces a training-free
framework for adaptive token merging, a novel mechanism that compresses
transformer representations at runtime by selectively merging semantically
redundant tokens under per-layer similarity thresholds. Unlike prior
fixed-ratio reduction, our approach couples merging directly to input
redundancy, enabling data-dependent adaptation that balances efficiency and
task relevance without retraining. We cast the discovery of merging strategies
as a multi-objective optimization problem and leverage Bayesian optimization to
obtain Pareto-optimal trade-offs between accuracy, inference cost, and
communication cost. On ImageNet classification, we match the accuracy of the
unmodified transformer with 30\% fewer floating-point operations per second and
under 20\% of the original communication cost, while for visual question
answering our method achieves performance competitive with the full LLaVA model
at less than one-third of the compute and one-tenth of the bandwidth. Finally,
we show that our adaptive merging is robust across varying channel conditions
and provides inherent privacy benefits, substantially degrading the efficacy of
model inversion attacks. Our framework provides a practical and versatile
solution for deploying powerful transformer models in resource-limited edge
intelligence scenarios.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.09919v1">A Markovian Framing of WaveFunctionCollapse for Procedurally Generating Aesthetically Complex Environments</a></td><td><details><summary>展开</summary>Procedural content generation often requires satisfying both
designer-specified objectives and adjacency constraints implicitly imposed by
the underlying tile set. To address the challenges of jointly optimizing both
constraints and objectives, we reformulate WaveFunctionCollapse (WFC) as a
Markov Decision Process (MDP), enabling external optimization algorithms to
focus exclusively on objective maximization while leveraging WFC's propagation
mechanism to enforce constraint satisfaction. We empirically compare optimizing
this MDP to traditional evolutionary approaches that jointly optimize global
metrics and local tile placement. Across multiple domains with various
difficulties, we find that joint optimization not only struggles as task
complexity increases, but consistently underperforms relative to optimization
over the WFC-MDP, underscoring the advantages of decoupling local constraint
satisfaction from global objective optimization.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.10584v1">Smart Trial: Evaluating the Use of Large Language Models for Recruiting Clinical Trial Participants via Social Media</a></td><td><details><summary>展开</summary>Clinical trials (CT) are essential for advancing medical research and
treatment, yet efficiently recruiting eligible participants -- each of whom
must meet complex eligibility criteria -- remains a significant challenge.
Traditional recruitment approaches, such as advertisements or electronic health
record screening within hospitals, are often time-consuming and geographically
constrained. This work addresses the recruitment challenge by leveraging the
vast amount of health-related information individuals share on social media
platforms. With the emergence of powerful large language models (LLMs) capable
of sophisticated text understanding, we pose the central research question: Can
LLM-driven tools facilitate CT recruitment by identifying potential
participants through their engagement on social media? To investigate this
question, we introduce TRIALQA, a novel dataset comprising two social media
collections from the subreddits on colon cancer and prostate cancer. Using
eligibility criteria from public real-world CTs, experienced annotators are
hired to annotate TRIALQA to indicate (1) whether a social media user meets a
given eligibility criterion and (2) the user's stated reasons for interest in
participating in CT. We benchmark seven widely used LLMs on these two
prediction tasks, employing six distinct training and inference strategies. Our
extensive experiments reveal that, while LLMs show considerable promise, they
still face challenges in performing the complex, multi-hop reasoning needed to
accurately assess eligibility criteria.</details></td></tr><tr><td><a href="http://arxiv.org/abs/2509.09906v1">Tackling One Health Risks: How Large Language Models are leveraged for Risk Negotiation and Consensus-building</a></td><td><details><summary>展开</summary>Key global challenges of our times are characterized by complex
interdependencies and can only be effectively addressed through an integrated,
participatory effort. Conventional risk analysis frameworks often reduce
complexity to ensure manageability, creating silos that hinder comprehensive
solutions. A fundamental shift towards holistic strategies is essential to
enable effective negotiations between different sectors and to balance the
competing interests of stakeholders. However, achieving this balance is often
hindered by limited time, vast amounts of information, and the complexity of
integrating diverse perspectives. This study presents an AI-assisted
negotiation framework that incorporates large language models (LLMs) and
AI-based autonomous agents into a negotiation-centered risk analysis workflow.
The framework enables stakeholders to simulate negotiations, systematically
model dynamics, anticipate compromises, and evaluate solution impacts. By
leveraging LLMs' semantic analysis capabilities we could mitigate information
overload and augment decision-making process under time constraints.
Proof-of-concept implementations were conducted in two real-world scenarios:
(i) prudent use of a biopesticide, and (ii) targeted wild animal population
control. Our work demonstrates the potential of AI-assisted negotiation to
address the current lack of tools for cross-sectoral engagement. Importantly,
the solution's open source, web based design, suits for application by a
broader audience with limited resources and enables users to tailor and develop
it for their own needs.</details></td></tr></tbody></table>
