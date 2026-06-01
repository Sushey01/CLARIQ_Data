% ============================================================
%  Clariq — CMP6200 Project Interim Report
%  Shekhar Lamichhane Magar  |  BCU ID: 23189647
% ============================================================
\documentclass[12pt, a4paper]{article}

% ── Packages ─────────────────────────────────────────────────
\usepackage[a4paper, top=2.5cm, bottom=2.5cm,
            left=2.5cm, right=2.5cm]{geometry}
\usepackage{fontenc}
\usepackage{inputenc}
\usepackage{microtype}
\usepackage{setspace}
\usepackage{parskip}
\usepackage{titlesec}
\usepackage{titletoc}
\usepackage{fancyhdr}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{array}
\usepackage{longtable}
\usepackage{tabularx}
\usepackage{multirow}
\usepackage[table]{xcolor}
\usepackage{hyperref}
\usepackage{natbib}
\usepackage{enumitem}
\usepackage{amsmath}
\usepackage{pdflscape}
\usepackage{caption}
\usepackage{float}
\usepackage{colortbl}
\usepackage{tikz}
\usetikzlibrary{shapes.geometric, arrows.meta, positioning, fit, backgrounds}

% ── Colours ──────────────────────────────────────────────────
\definecolor{bcuBlue}{RGB}{0,51,102}
\definecolor{layerBlue}{RGB}{61,126,191}
\definecolor{layerGreen}{RGB}{46,139,87}
\definecolor{layerOrange}{RGB}{224,123,57}
\definecolor{layerPurple}{RGB}{123,94,167}
\definecolor{layerTeal}{RGB}{42,157,143}
\definecolor{layerDark}{RGB}{26,58,92}
\definecolor{tableHead}{RGB}{46,64,87}
\definecolor{riskHigh}{RGB}{231,76,60}
\definecolor{riskMed}{RGB}{243,156,18}
\definecolor{riskLow}{RGB}{46,204,113}

% ── Typography ───────────────────────────────────────────────
\onehalfspacing
\setlength{\parindent}{0pt}
\setlength{\parskip}{8pt}

% ── Section headings ─────────────────────────────────────────
\titleformat{\section}
  {\large\bfseries\color{bcuBlue}}
  {\thesection}{1em}{}[\titlerule]

\titleformat{\subsection}
  {\normalsize\bfseries\color{bcuBlue}}
  {\thesubsection}{1em}{}

\titlespacing*{\section}{0pt}{18pt}{8pt}
\titlespacing*{\subsection}{0pt}{12pt}{4pt}

% ── Header / Footer ──────────────────────────────────────────
\pagestyle{fancy}
\fancyhf{}
\lhead{\small 25-26 Project Interim Report}
\rhead{\includegraphics[height=0.9cm]{logo.png}}
\cfoot{\small\thepage}
\renewcommand{\headrulewidth}{0.4pt}
\setlength{\headheight}{14pt}

% ── Hyperref ─────────────────────────────────────────────────
\hypersetup{
  colorlinks=true,
  linkcolor=bcuBlue,
  citecolor=bcuBlue,
  urlcolor=bcuBlue
}

% ── Bibliography style ───────────────────────────────────────
\bibliographystyle{agsm}

% ============================================================
\begin{document}
\pagenumbering{gobble}

% ============================================================
%  COVER PAGE
% ============================================================
\begin{titlepage}
\centering
\vspace*{0.5cm}
\includegraphics[width=0.45\linewidth]{logo.png}\\[0.6cm]
\rule{\linewidth}{1pt}\\[2.5cm]
{\Large \textbf{CMP6200/DIG6200}}\\[0.5cm]
{\Large \textbf{Individual Undergraduate Project (FYP)}}\\[0.5cm]
{\Large \textbf{Project Interim Report}}\\[1.5cm]
{\LARGE \textbf{Clariq: An AI-Powered Socratic Science Tutor}}\\[0.3cm]
{\LARGE \textbf{with Adaptive Knowledge Tracking}}\\[0.3cm]
{\LARGE \textbf{for SEE Students (Class 10, Nepal)}}\\[2.5cm]
\rule{\linewidth}{1pt}\\[1.5cm]
\begin{flushleft}
\large
\textbf{Student Name:} Shekhar Lamichhane Magar\\[0.3cm]
\textbf{Student ID:} 23189647\\[0.3cm]
\textbf{Course:} BSc (Hons) Computer and Data Science\\[0.3cm]
\textbf{Supervisor:} Rupak Koirala\\[0.3cm]
\textbf{Date:} \today
\end{flushleft}
\end{titlepage}

% ============================================================
%  FRONT MATTER — ToC + List of Figures + List of Tables
% ============================================================
\pagenumbering{roman}
\tableofcontents
\newpage
\listoffigures
\newpage
\listoftables
\newpage
\pagenumbering{arabic}

% ============================================================
%  1.0  INTRODUCTION AND CONTEXT
% ============================================================
\section{Introduction and Context}

Access to high-quality science education remains unevenly distributed at the upper secondary
level. In Nepal, Class~10 students prepare for the Secondary Education Examination (SEE) a
high-stakes national board examination administered by the National Examination Board (NEB).
NEB data show that Science and Technology consistently ranks among the subjects with the
highest failure counts: in 2080--81 alone, 79,271 out of 514,071 students were ungraded in
Science, while the overall pass rate stood at only 62\%and just 48\% the previous
year \citep{neb2081}. This makes personalised science support particularly critical yet
economically inaccessible for most students. Private tutoring is costly, while static resources and generic
AI chatbots either require high self-motivation or deliver direct answers that bypass learning,
leading to memorisation rather than reasoning on the analytical questions that characterise
the SEE.

Recent studies show LLM-based tutoring can deliver engaging, personalised learning at
scale \citep{goyal2026,lieb2024}, yet the literature is concentrated in higher education and
non-science domains. No curriculum-grounded, Socratic science tutor exists for upper secondary
students preparing for high-stakes examinations such as the SEE \citep{chang2025,watson2026}.

This project proposes Clariq, an AI-powered Socratic science tutor grounded in the SEE
Physics, Chemistry, and Biology curriculum via Retrieval-Augmented Generation (RAG).
Clariq guides students through questioning rather than direct answers, monitors understanding
through an adaptive Knowledge Graph, and generates weekly teacher reports. Two research
questions are investigated: (1)~Can a RAG-grounded Socratic tutor improve comprehension
outcomes in SEE science topics versus traditional self-study? (2)~Can a Knowledge Graph
provide accurate concept-level monitoring for actionable teacher feedback?

\subsection{Problem Statement}

SEE students face three interconnected gaps that existing tools do not address.

First, no AI tutoring system is calibrated to the SEE science syllabus prescribed by Nepal's
Curriculum Development Centre (CDC). General-purpose LLMs produce content above the target
readability level without curriculum grounding \citep{karaca2024}, generating answers
misaligned with NEB marking schemes. NEB result data confirm that Science and Technology
recorded 79,271 non-graded students in 2080--81 the third-highest failure count across all
SEE subjects underscoring the urgent need for targeted, curriculum-accurate
support \citep{neb2081}.

Second, most AI tools deliver answers rather than understanding. Vygotsky's Zone of Proximal
Development and Reiser's scaffolding work show guided questioning produces better conceptual
outcomes than direct provision of answers \citep{vygotsky1978,reiser2004}. A secondary physics
study confirmed that Socratic tutoring improves engagement over a general-purpose
baseline \citep{lieb2024}. For SEE candidates, where analytical questions carry the highest
marks, this distinction is especially consequential.

Third, concept-level tracking is absent. Without it, teachers lack scalable insight into
student misconceptions ahead of the SEE. Chen et al.\ showed AI feedback can identify weak
points with 92\% accuracy and improve exam scores by 11.5 points across six secondary
schools \citep{chen2025}.

% ============================================================
%  2.0  REVIEW OF EXISTING KNOWLEDGE
% ============================================================
\section{Review of Existing Knowledge}

\subsection{Theme 1: Socratic AI Tutoring and Conversational Learning Systems}

Goyal et al.\ \citeyearpar{goyal2026} demonstrate through Sakshm~AI that Socratic guidance
via conversational AI with session memory significantly improves problem-solving behaviour
and sustained engagement ($n=1{,}170$). Critically, cross-session memory proved the strongest
differentiator of effectiveness: tutors that retained prior context could target known gaps
from the outset rather than starting from scratch each session a design principle Clariq
adopts directly through its Knowledge Graph. Lieb and Goel \citeyearpar{lieb2024} provide
complementary secondary-level evidence through NewtBot, a physics chatbot for German upper
secondary students ($n=50$). Despite 72\% of participants expressing initial apprehension,
70\% stated they would use the system for schoolwork, confirming that secondary students
engage productively with Socratic AI when it is domain-specific and supportive in tone.

The theoretical foundation for this approach is established by \citet{vygotsky1978}, whose
Zone of Proximal Development holds that learning advances most significantly when guidance
pushes the learner just beyond their current understanding rather than providing the answer
outright. Reiser \citeyearpar{reiser2004} extended this to digital environments, demonstrating
that scaffolded instruction produces superior conceptual outcomes compared to direct instruction.
These two findings jointly motivate Clariq's core constraint: the system never supplies direct
answers, only targeted questions that surface the gap in a student's reasoning. For SEE
students, where higher-order analytical questions carry the greatest weight in NEB marking
schemes, this guided-questioning approach is particularly consequential.

\subsection{Theme 2: Curriculum Grounding and Adaptive Knowledge Tracking}

A persistent risk of deploying general-purpose LLMs in education is hallucination generating
plausible but factually incorrect content. In science, where misconceptions compound across
topics, this risk is particularly acute. Chang \citeyearpar{chang2025} reviewed LLM applications across secondary subjects and identified curriculum alignment as a critical gap; Watson \citeyearpar{watson2026} demonstrated clear advantages of RAG-based LLMs over off-the-shelf AI in achieving secondary curriculum alignment and material quality. Karaca \citeyearpar{karaca2024} reinforces this, showing that ungrounded LLMs
consistently produce content above the secondary readability level, a calibration failure that
Clariq's CDC-seeded RAG pipeline is specifically designed to prevent.

At the knowledge-tracking layer, Chen et al.\ \citeyearpar{chen2025} deployed an intelligent
feedback system across six secondary schools achieving 92\% accuracy in identifying weak
knowledge points, reducing teacher feedback time by 68\%, and improving examination scores by
11.5 points in pilot classes. Vandewaetere et al.\ \citeyearpar{vandewaetere2011} showed that
adaptive systems maintaining individualised knowledge models improve learning outcomes by
20--40\% compared to non-adaptive alternatives. Together these findings validate Clariq's
directed Knowledge Graph, which enforces prerequisite-aware scaffolding and surfaces
concept-level misconceptions to teachers in a weekly report. Crucially, by grounding the
RAG pipeline in the CDC-prescribed SEE syllabus, every retrieved passage is guaranteed to
align with the content and depth that NEB examiners expect a precision that generic
knowledge bases cannot provide.

\subsection{Theme 3: Student Adoption and Teacher Integration}

Setälä \citeyearpar{setala2025} applied the Technology Acceptance Model (TAM) to Finnish upper
secondary students using generative AI in mathematics, finding that perceived usefulness
particularly for examination preparation was the strongest predictor of adoption intention,
with perceived enjoyment as a significant mediating variable. Lu \citeyearpar{lu2026} reinforced
this, identifying grade-improvement framing as the dominant driver of student AI adoption.
Both findings are especially pertinent in the SEE context, where the examination is a
once-only national milestone that directly determines whether a student progresses to
higher secondary education. For Clariq, these findings translate into a concrete design
priority: the Knowledge Graph progress dashboard must provide immediate, tangible evidence
of learning progress, directly connecting engagement to SEE readiness.

Teacher readiness depends on prior AI experience, professional development access, and the
quality of available resources \citep{addo2024}. Lian and Zhang \citeyearpar{liandzhang2024}
found performance expectancy and enabling conditions as significant predictors of teacher
adoption intent under the UTAUT framework. Clariq responds to both barriers through its
automated weekly teacher reports, which deliver actionable diagnostic insight strongest
and weakest concept nodes per student, confusion frequency by topic without requiring
any direct technical interaction with the AI system.

\subsection{Theme 4: Ethical Considerations and Data Governance}

Any AI system collecting conversational data from minors, tracking behaviour across sessions,
and sharing reports with third-party teachers operates in an ethically sensitive space. Zhu
et al.\ \citeyearpar{zhu2026} proposed a three-tier governance framework covering data
classification by sensitivity level, algorithmic ethics review, and clearly defined digital
rights for student and teacher participants directly applicable to Clariq. Denzler
\citeyearpar{denzler2024} documented a rise in AI-assisted academic passivity following
ChatGPT adoption, with suspicious submission rates increasing from 18\% to 26\% within one
academic year. Clariq's Socratic model structurally prevents this: the system cannot produce
a direct exam answer, only redirect students through conceptual questions. Whyte
\citeyearpar{whyte2024} found that secondary students commonly anthropomorphise AI systems;
Clariq therefore includes age-appropriate onboarding explaining its curriculum-based nature,
defined knowledge limits, and the importance of cross-checking explanations with textbooks.

\subsection{Critical Analysis and Gap Identification}

Three research gaps define Clariq's contribution. First, neither \citet{goyal2026} nor
\citet{lieb2024} validates Socratic tutoring across multi-domain secondary science spanning
Physics, Chemistry, and Biology simultaneously. Second, no RAG pipeline has been seeded
with a complete secondary science syllabus aligned to a national examination board
specifically Nepal's CDC/NEB SEE syllabus and validated against curriculum-aligned test
queries that reflect actual NEB marking expectations. Third, \citet{chen2025} derives mastery
estimates from homework submissions rather than real-time conversational signals a harder
inference problem that no study has addressed at secondary science level. These three gaps
define the methodological space this research occupies.

\subsection{Project Justification}

Academically, Clariq integrates Socratic tutoring, curriculum-grounded RAG, and real-time
Knowledge Graph monitoring into a single, evaluable system, addressing all three gaps with
a reproducible, curriculum-specific design. Practically, in Nepal and comparable contexts,
qualified science teachers are unevenly distributed and private tutoring is economically
inaccessible for most SEE students. Clariq demonstrates that personalised, SEE-aligned
science tutoring can be delivered at negligible marginal cost to any student with a device
and internet access, while grounding design in responsible data governance \citep{zhu2026}.

% ============================================================
%  3.0  PROJECT AIMS, OBJECTIVES, AND SCOPE
% ============================================================
\section{Project Aims, Objectives, and Scope}

\subsection{Project Aim}

To design, develop, and evaluate Clariq an AI-powered Socratic science tutor that delivers
curriculum-grounded, personalised learning conversations for students preparing for Nepal's
Secondary Education Examination (SEE, Class~10) in Physics, Chemistry, and Biology; tracks
individual knowledge gaps and confusion patterns through an adaptive Knowledge Graph;
generates structured weekly progress reports for teachers; and demonstrates measurably better
comprehension outcomes than traditional self-study in a controlled evaluation.

\subsection{Project Objectives}

\begin{enumerate}[label=\textbf{Objective \arabic*:}, leftmargin=*, align=left]

\item \textbf{Curriculum Dataset and RAG Pipeline.}
  Curate and structure the full SEE Science syllabus (CDC, Nepal) into a hierarchical
  knowledge base and integrate it into a RAG pipeline using sentence-transformer embeddings
  and pgvector, achieving Precision@3 $\geq 0.85$ on 100 held-out curriculum-aligned test queries
  sourced from published NEB past papers (2016--2024). Test query validation: manually annotate
  top-3 relevant curriculum passages per query for ground truth (300 judgments total).

\item \textbf{Socratic Tutor Model.}
  Fine-tune LLaMA-3-8B via LoRA on a curated Socratic science tutoring dataset (700 examples:
  500 synthetic via GPT-4o-mini + 200 teacher-authored from 3 educators) constrained
  never to provide direct answers, achieving ROUGE-L $\geq 0.50$ and human pedagogical
  rating $\geq 4.0/5.0$ (on Socratic adherence, curriculum accuracy, age-appropriate language,
  clarity, scaffolding) from five secondary science teachers (ICC $\geq 0.75$).

\item \textbf{System Integration and Backend.}
  Build a FastAPI backend orchestrating the RAG pipeline and Socratic LLM, maintaining session
  state and real-time Knowledge Graph updates, with end-to-end latency $\leq 5$ seconds under
  typical load.

\item \textbf{Adaptive Knowledge Graph and Reporting.}
  Implement a directed Knowledge Graph covering $\sim$135 SEE concept nodes (Physics 45, Chemistry 50, Biology 40)
  and prerequisite edges validated by teacher consensus (Cohen's $\kappa \geq 0.70$),
  dynamically updated from session data via student response evaluation loop ($s_t = \text{sim} \times \text{coherence}$),
  with automated weekly teacher reports validated for diagnostic usefulness by five science teachers.

\item \textbf{Controlled User Evaluation.}
  Conduct a within-subjects crossover study with $n = 20$ SEE students measuring
  time-to-comprehension and post-session retention versus textbook self-study, with recruitment
  beginning Week~8 and evaluation Weeks~15--20 (concurrent with system development). Target
  30\% reduction in time-to-comprehension and statistically significant retention improvement
  ($\alpha = 0.05$), with ICC $\geq 0.75$ for inter-rater reliability on the teacher rubric.
  Reduced from $n=40$ to $n=20$ to maintain timeline feasibility while achieving publishable results (60\% power vs 80\%).

\end{enumerate}

\subsection{Project Scope}

The conversational component handles science queries within the SEE Physics, Chemistry, and
Biology syllabi as prescribed by the CDC, Nepal, supporting multi-turn Socratic dialogue
within a session. Not in scope: Open discussion outside the science discipline, examination
answers, and incorporation into the school management system. RAG knowledge database is created
from syllabus documents and NEB-approved textbooks, with the students allowed to add their own
PDF notes in addition to that. The Knowledge Graph comprises all of SEE syllabus at concept node
level. Evaluation is through a prototype web application only.

% ============================================================
%  4.0  PROJECT DESIGN
% ============================================================
\section{Project Design}

Clariq is structured across six functional layers connected through a FastAPI backend: data
ingestion (offline), student input, RAG retrieval, LLM inference, Knowledge Graph monitoring,
and teacher reporting. Figure~\ref{fig:architecture} illustrates the end-to-end architecture.

\begin{figure}[H]
    \centering
    \includegraphics[width=\textwidth]{clariq_architecture.png}
    \caption{End-to-end system architecture of Clariq, integrating the FastAPI backend,
    RAG pipeline, four-layer Socratic Constraint Enforcement, and LLaMA-3-8B (LoRA) tutor
    with adaptive Knowledge Graph tracking (\textasciitilde135 concept nodes) for
    concept-level monitoring and automated weekly teacher reporting.}
    \label{fig:architecture}
\end{figure}

\subsection{Design and Methods}

The project follows a design-and-build strategy, constructing and evaluating a working system
to demonstrate the feasibility of Socratic, curriculum-grounded science tutoring with
real-time Knowledge Graph monitoring.

\textbf{Data Ingestion} uses PyMuPDF to extract text from CDC curriculum PDFs. LangChain
splits content into 300-token chunks (50-token overlap), each tagged with subject, chapter,
and hierarchy level; sentence-transformers generate embeddings stored in pgvector.

\textbf{Student Input} is accepted via a React.js interface supporting typed queries and
optional PDF uploads (personal notes, past papers). Uploaded content is injected into session
context only, keeping the verified curriculum knowledge base uncontaminated.

\textbf{RAG and LLM Inference}: FastAPI orchestrates each message by retrieving the top-$k$
curriculum chunks from pgvector and passing them with session history to LLaMA-3-8B (LoRA),
whose system prompt constrains it never to provide direct answers. 

A Socratic example: when
a student asks ``Why does ice float?'', Clariq responds: ``What do you remember about what
happens to the density of most substances when they freeze?' activating prior knowledge
rather than supplying the answer \citep{goyal2026,reiser2004}.

\textbf{Student Response Evaluation Loop}: To operationalise adaptive mastery tracking, when a
student provides a response to a Socratic prompt (via the \texttt{answer} command), the system
executes the following pipeline:
\begin{enumerate}[itemsep=2pt]
  \item \textbf{Retrieval Context}: Fetches the top-$k$ curriculum passages previously matched to the Socratic question
  \item \textbf{Embedding Generation}: Encodes both student response and curriculum passages using sentence-transformers (\texttt{all-MiniLM-L6-v2}), producing fixed 384-dimensional vectors
  \item \textbf{Semantic Similarity Computation}: $\text{sim} = \cos(\mathbf{e}_{\text{student}}, \mathbf{e}_{\text{curriculum}})$, capturing alignment between student language and expected curriculum content (range: [0, 1])
  \item \textbf{Coherence Penalty}: Detects rote copying (verbatim overlap $>80\%$ $\rightarrow$ penalty $\times 0.5$), fragmentation (length $< 5$ words $\rightarrow$ penalty $\times 0.3$), and applies formula: $s_t = \text{sim} \times \text{coherence}_{\text{penalty}}$
  \item \textbf{Mastery Update}: $m_{t+1} = m_t + \alpha(s_t - m_t)$, where $\alpha = 0.25$ (cold-start: $m_0 = 0.5$ for new students)
\end{enumerate}

\emph{Example:} When a student answers a Socratic prompt, the system computes semantic similarity $s_t = \text{sim} \times \text{coherence}$ and updates mastery via $m_{t+1} = m_t + \alpha(s_t - m_t)$.

Responses with $s_t < 0.40$ trigger follow-up Socratic prompts rather than advancement; consecutive $s_t < 0.40$ across 3+ attempts on a single concept node flags confusion for teacher alert.

\textbf{Knowledge Graph}: Each student's state is a directed graph encoding $\sim$135 concept nodes across Physics (45 concepts), Chemistry (50 concepts), and Biology (40 concepts) with prerequisite edges defined through teacher validation (Cohen's $\kappa \geq 0.70$). Example: ``Density'' $\rightarrow$ ``Buoyancy'', ``Charge'' $\rightarrow$ ``Electric Current''. Nodes with $m_t \geq 0.75$ unlock dependent concepts for subsequent Socratic prompts; sustained confusion ($s_t < 0.4$ across 3+ attempts) flags concept for weekly teacher report. Graph construction: extract learning outcomes from CDC syllabus $\rightarrow$ interview 3--5 science teachers to map dependencies $\rightarrow$ validate with 2 independent teachers \citep{reiser2004}.



% \begin{figure}[H]
%     \centering
%     \includegraphics[width=\textwidth]{clariq_knowledge_graph.png}
%     \caption{Adaptive Knowledge Graph for a sample student session across Physics,
%     Chemistry, and Biology. Filled nodes denote mastered concepts ($m_t \geq 0.75$);
%     dashed arrows flag concepts for the weekly teacher report after 3+ consecutive
%     low-mastery responses ($s_t < 0.4$). Prerequisite edges are validated by teacher
%     consensus (Cohen's $\kappa \geq 0.70$).}
%     \label{fig:kg}
% \end{figure}

\subsection{Evaluation}

The system is evaluated on three dimensions: technical performance, learning effectiveness,
and usability.

\textbf{Technical performance.} RAG retrieval precision is validated via Precision@3 metric on 100 held-out test queries sourced from published NEB past-paper questions (5 per subject, 2016--2024). Ground truth: manually annotate top-3 most relevant curriculum passages per query, yielding 300 relevance judgments. Success threshold: $\text{Precision@3} \geq 0.85$ (i.e., average $\geq 2.55$ relevant docs in top-3 retrieved). Fallback tuning: if precision $< 0.85$, trial chunk sizes (200/300/400 tokens), embedding models (bge-base-en-v1.5 vs current all-MiniLM-L6-v2), and cross-encoder re-ranking. ROUGE-L ($\geq 0.50$) evaluates Socratic explanation quality against reference responses written by science teachers. End-to-end latency ($\leq 5$~s) is tested under a simulated load of 10 concurrent sessions.

\textbf{Learning effectiveness.} A within-subjects crossover design involving $n = 20$ SEE Class 10
students ($15 - 16$ years old); order of the sessions is counterbalanced. Reasons for choosing this study design: feasibility of the timeline with earlier completion while still producing publishable findings; sample size of $n=20$ reduced statistical power to 60\% (from 80\% when n = 40), but enough to detect a directional effect. Recruitment begins Week 8; testing takes place in Weeks 15 to 20. A 10-item MCQ pre-test establishes
baseline knowledge; parallel post-tests measure immediate and one-week delayed retention.
Primary analysis: paired $t$-test (or Wilcoxon signed-rank if normality is rejected), with
Cohen's $d$ for effect size and Benjamini--Hochberg FDR correction at $\alpha = 0.05$.

\textbf{Pedagogical rating.} Five secondary science teachers independently rate 30 sampled
responses on a five-point Likert rubric: (1) Socratic adherence (response asks questions, not answers), (2) curriculum accuracy (alignment with CDC/NEB standards), (3) age-appropriate language (Class~10 reading level), (4) clarity of guiding question (students understand what is being asked), (5) scaffolding quality (question targets zone of proximal development). Inter-rater reliability is assessed via ICC$_{(3,k)}$ Consistency (threshold $\geq 0.75$). Mean rating $\geq 4.0/5.0$
constitutes a pass threshold.

\textbf{Usability.} System Usability Scale (SUS) administered to students (n=20) and teachers (n=5) after evaluation sessions; score $\geq 68$ indicates acceptable usability. Additional semi-structured interviews (10 minutes per participant) gather qualitative feedback on Knowledge Graph understandability and teacher report actionability.

\subsection{Justification of Methods}

Design-and-build is required because both research questions are systems-level and demand a
functioning prototype to generate empirical data. 

\textbf{LLaMA-3-8B with LoRA} eliminates per-query API costs, making continuous student use economically viable. Fine-tuning dataset: 700 examples comprising 500 synthetic Socratic dialogues (generated via GPT-4o-mini with prompt: ``Generate a Socratic tutor response using only curriculum context. Never give direct answers.'', each validated by $\geq 1$ teacher for adherence) and 200 teacher-authored dialogues from 3 secondary science educators. Quality gates: every synthetic example rated $\geq 3/5$ on Socratic adherence by teachers; remove responses providing direct answers. Target: ROUGE-L $\geq 0.50$ and human pedagogical rating $\geq 4.0/5.0$.

\textbf{Socratic Constraint Enforcement} uses a multi-layer approach: (Layer~1) System prompt explicitly constrains LLM never to provide direct answers; (Layer~2) Binary answer-detection classifier (DistilBERT) screening responses pre-delivery—if $P(\text{direct answer}) > 0.6$, reject and regenerate; (Layer~3) Retrieval-only mode—pass concept headers and guiding questions to LLM, not full answer passages; (Layer~4) Template fallback—if classifier rejects response 3$\times$ consecutively, use human-approved Socratic templates (e.g., ``Think about [CONCEPT]. What do you already know?''). Validation: 50 known-answer questions; target $\leq 5\%$ constraint violations.

\textbf{RAG} prevents hallucination and keeps the knowledge base auditable without model retraining
\citep{karaca2024,watson2026}. \textbf{FastAPI} provides native async and WebSocket support
for concurrent classroom sessions. \textbf{A directed Knowledge Graph} encodes prerequisite
dependencies that a flat progress table cannot represent; construction validated through teacher consensus (Cohen's $\kappa \geq 0.70$) \citep{reiser2004}.

\textbf{Sample size adjustment}: $n = 20$ (instead of 40) balances statistical power (60\% vs 80\%) with timeline feasibility; recruitment and evaluation run concurrent with system development (Weeks~8--20, 3--4 hours per student). Sufficient for detecting directional learning effects and publishable in education venues (e.g., \textit{Computers \& Education}).

\subsection{Project Timeline}

The project spans 30 weeks across seven phases (11~April -- 11~October~2026). Key milestones: RAG pipeline ready (Week~9), interim report (Week~14), Knowledge Graph validation (Week~7), LoRA fine-tuning (Week~11), integrated system (Week~23), student recruitment begins Week~8, evaluation runs Weeks~15--20 concurrent with teacher report development, analysis and writing (Weeks~21--27), final submission (Week~30). This timeline is feasible through parallel development and recruitment. The Gantt chart (Figure~\ref{fig:gantt}) shows the full schedule.

\begin{figure}[H]
    \centering
    \includegraphics[width=\textwidth]{clariq_gantt_chart.png}
    \caption{Project Gantt chart (Apr~2026 -- Oct~2026, 7 phases). The red dashed line marks
    today (27~April 2026). Red diamonds indicate key milestones.}
    \label{fig:gantt}
\end{figure}

% ============================================================
%  5.0  FEASIBILITY, RISKS, AND ETHICAL ASPECTS
% ============================================================
\section{Feasibility, Risks, and Ethical Aspects}

\subsection{Feasibility}

The project is feasible across all dimensions. All core technologies are open-source and
well-documented (LLaMA-3-8B, LoRA/PEFT, LangChain, pgvector, FastAPI, React.js, PyMuPDF),
and the full SEE Science syllabus is publicly available from the CDC. School partnership
recruitment is underway; $n = 20$ students is achievable over a 4--6 week evaluation window
(Weeks~15--20) with concurrent system development, eliminating timeline contention. LoRA fine-tuning dataset (700 examples) acquisition: 500 synthetic via GPT-4o-mini (Weeks~4--5) and 200 teacher-authored via 3 educators (Week~5). Knowledge Graph prerequisite validation: 5 teachers (Weeks~6--7, Cohen's $\kappa$ test). Identified skill gaps in LoRA and RAG configuration will be addressed through Hugging~Face PEFT and LangChain documentation in Phase~1.

\subsection{Risk Analysis and Mitigation}

\begin{table}[H]
\centering
\caption{Key project risks and mitigation strategies}
\label{tab:risks}
\renewcommand{\arraystretch}{1.4}
\begin{tabular}{|>{\raggedright\arraybackslash}p{4.0cm}
                |>{\centering\arraybackslash}p{1.3cm}
                |>{\centering\arraybackslash}p{1.3cm}
                |>{\raggedright\arraybackslash}p{6.5cm}|}
\hline
\rowcolor{tableHead}
\textcolor{white}{\textbf{Risk}} &
\textcolor{white}{\textbf{L}} &
\textcolor{white}{\textbf{I}} &
\textcolor{white}{\textbf{Mitigation}} \\
\hline
LoRA fine-tuning undershoots ROUGE-L $\geq 0.50$ &
M & H &
Augment with additional GPT-4o-mini synthetic examples; implement multi-layer Socratic constraint enforcement (Layers 1--4) as fallback to compensate for weaker ROUGE scores. \\
\hline
RAG precision $<0.85$ on test queries &
M & H &
Tune chunk size (200/300/400 tokens); trial \texttt{bge-base-en-v1.5} embedding model; add cross-encoder re-ranking; iteratively expand test query set. \\
\hline
Study participants $<20$ &
M & M &
Begin school recruitment Week~8; identify backup schools (n$\geq 3$); prepare remote/hybrid evaluation option; use stratified sampling if $n>20$ to ensure Physics/Chemistry/Biology balance. \\
\hline
Teacher validation for KG edges ($\kappa < 0.70$) &
M & H &
If initial consensus weak, reduce prerequisite graph scope to core Physics concepts only; iterate validation with additional teachers. \\
\hline
GPU unavailable for fine-tuning &
L & H &
Use Colab Pro (£10/month) or Kaggle; schedule LoRA training for off-peak hours (nights/weekends); prepare checkpoint restart strategy. \\
\hline
School partner withdraws &
L & H &
Identify two backup schools by Week~7; prepare university-network recruitment fallback (alumni, existing contacts). \\
\hline
\end{tabular}
\end{table}

\subsection{Ethical Considerations}

\textbf{Student data and privacy.} All the participants are minors (Class~10, age about
15--16), and they all need to provide informed consent in writing from the
student and the parent/legal guardian before any data collection takes place. All the
session data and Knowledge Graph data are anonymized during the data collection process;
no personal information will be recorded along with the analytics.

\textbf{Algorithmic fairness and academic integrity.} Clariq's Socratic model structurally
prevents academic passivity by never providing direct answers \citep{denzler2024}. Mastery
assessments are diagnostic only communicated to teachers as support data, not formal
grades and teachers retain full professional authority over assessment decisions.

\textbf{AI literacy.} Following \citet{whyte2024}, onboarding explains that Clariq is a
curriculum-based AI with defined limits that can make mistakes; students are encouraged to
verify explanations against textbooks, preventing anthropomorphic misconceptions.

\textbf{Data governance.} In accordance with \citet{zhu2026}, session transcripts, mastery scores,
and confusion markers are kept in separate databases away from personally identifying
information. Ethical approval is required for any outputs to be used on actual students, and
teacher rights in the digital space, such as the freedom to ignore AI advice, are clearly stated.

% ============================================================
%  BIBLIOGRAPHY
% ============================================================
\newpage
\addcontentsline{toc}{section}{References}
\bibliography{references}

\end{document}