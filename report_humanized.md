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
\addcontentsline{toc}{section}{List of Figures}
\newpage
\listoftables
\addcontentsline{toc}{section}{List of Tables}
\newpage
\pagenumbering{arabic}

% ============================================================
%  1.0  INTRODUCTION AND CONTEXT
% ============================================================
\section{Introduction and Context}

Quality science education---the kind that teaches students to reason critically and solve problems---remains unevenly distributed across Nepal's upper secondary schools. In the country, Class~10 students face the Secondary Education Examination (SEE), a high-stakes national board exam administered by the National Examination Board (NEB). It's a moment that defines much of their educational future. The statistics paint a stark picture: in 2080--81 alone, 79,271 students were unable to pass Science and Technology out of 514,071 total test-takers. The overall pass rate hovered at just 62\% that year, having been only 48\% the previous year \citep{neb2081}. For a developing nation trying to build a STEM-capable workforce, these numbers are troubling.

The underlying problem is straightforward. Personalised, high-quality science support is economically inaccessible for most students. Private tutoring costs money many families don't have. Meanwhile, static textbooks and generic AI chatbots fail to address the real learning challenge: they either demand too much self-motivation from students or they shortcut the learning process entirely, handing out direct answers rather than building conceptual understanding. For the SEE, where analytical reasoning questions carry the highest marks, this shortcutting is particularly damaging \citep{goyal2026,lieb2024}.

Yet emerging research shows genuine promise. LLM-based tutoring systems can deliver engaging, personalised learning at scale. But the bulk of that research sits in higher education contexts and non-science domains. For upper secondary science---especially for a high-stakes exam like the SEE---no curriculum-grounded, Socratic tutor exists yet \citep{chang2025,watson2026}.

This project proposes Clariq: an AI-powered Socratic science tutor grounded specifically in the SEE Physics, Chemistry, and Biology curriculum, using Retrieval-Augmented Generation (RAG) to ensure every response stays aligned with what students actually need to know. Rather than providing answers, Clariq asks strategic questions that guide students toward their own understanding. It monitors their progress through an adaptive Knowledge Graph, generating weekly diagnostic reports for teachers. Two research questions drive the work: (1)~Can a RAG-grounded Socratic tutor actually improve comprehension outcomes compared to traditional textbook study? (2)~Can real-time Knowledge Graph tracking provide teachers with accurate, actionable insights into student misconceptions?

\subsection{Problem Statement}

SEE students face three interconnected gaps that current tools simply don't address.

First: there is no AI tutoring system calibrated to Nepal's SEE science curriculum. General-purpose LLMs produce content that reads well but sits above the target readability level---and worse, they often generate answers misaligned with NEB marking schemes \citep{karaca2024}. The NEB data we cited earlier underscore this: 79,271 non-graded students in 2080--81 across Science and Technology, making it the third-highest failure count across all SEE subjects \citep{neb2081}. Students need help that's not just good, but good in relation to what examiners actually expect.

Second: most AI tutoring tools deliver answers rather than understanding. This matters enormously for learning science. Vygotsky's Zone of Proximal Development and Reiser's work on scaffolding both show the same thing: guided questioning produces better conceptual outcomes than direct answer provision \citep{vygotsky1978,reiser2004}. When secondary physics students worked with a Socratic chatbot like NewtBot, they engaged better and showed stronger learning gains compared to general-purpose baselines \citep{lieb2024}. For SEE candidates, where analytical questions dominate the rubric, this distinction between asking and answering is not academic---it's the difference between memorisation and genuine reasoning.

Third: real-time concept-level tracking is missing. Teachers don't have scalable insight into what their students actually misunderstand before exam day. Chen et al. showed that AI-driven feedback systems can identify weak knowledge points with 92\% accuracy and improve exam scores by 11.5 points across secondary schools \citep{chen2025}. Imagine what targeted teacher reports could do if they arrived weekly, not after the fact.

% ============================================================
%  2.0  REVIEW OF EXISTING KNOWLEDGE
% ============================================================
\section{Review of Existing Knowledge}

\subsection{Theme 1: Socratic AI Tutoring and Conversational Learning Systems}

Recent work in AI tutoring gives us reason for optimism. Goyal et al.\ showed through their Sakshm~AI system that Socratic guidance via conversational AI with session memory significantly improves both problem-solving behaviour and engagement across 1{,}170 participants \citep{goyal2026}. What stood out: cross-session memory was the strongest predictor of effectiveness. Tutors that retained prior context could target known gaps from the start, rather than forcing students to re-explain themselves each session. This is exactly what Clariq does with its Knowledge Graph. 

On the ground level, Lieb and Goel studied secondary students using NewtBot, a physics chatbot for German upper secondary students \citep{lieb2024}. Initial apprehension was high (72\% nervous), yet 70\% said they'd use the system for real schoolwork. That shift happened because the system was domain-specific and maintained a supportive tone. Students engage productively with Socratic AI when it's genuinely tailored to what they need to learn.

The theory underpinning this approach goes back decades. Vygotsky established the Zone of Proximal Development: learning happens most effectively when guidance pushes you just beyond what you already know \citep{vygotsky1978}. Reiser extended this principle to digital environments, showing that scaffolded instruction beats direct instruction for conceptual mastery \citep{reiser2004}. Together, these findings motivate Clariq's core design principle: never provide direct answers. Instead, ask strategic questions that expose gaps in reasoning. For SEE students tackling higher-order analytical questions, this approach isn't a nice-to-have---it's essential.

\subsection{Theme 2: Curriculum Grounding and Adaptive Knowledge Tracking}

Deploying general-purpose LLMs in education carries a well-known risk: hallucination. They can sound plausible while being factually wrong. In science, where misconceptions compound across topics, this risk is acute. Chang recently reviewed LLM applications across secondary subjects and identified curriculum alignment as a critical bottleneck \citep{chang2025}. Watson went further, demonstrating clear advantages of RAG-based LLMs for secondary curriculum alignment compared to off-the-shelf AI \citep{watson2026}. Karaca reinforced this finding: ungrounded LLMs consistently produce content above secondary readability level, a calibration failure Clariq's CDC-seeded RAG pipeline is designed specifically to prevent \citep{karaca2024}.

When it comes to tracking what students actually understand, the picture is similarly promising but incomplete. Chen et al. deployed intelligent feedback systems across six secondary schools and achieved 92\% accuracy in identifying weak knowledge points, reduced teacher feedback time by 68\%, and improved exam scores by 11.5 points in pilot classes \citep{chen2025}. Vandewaetere et al. showed that adaptive systems maintaining individual knowledge models improve learning outcomes by 20--40\% versus non-adaptive alternatives \citep{vandewaetere2011}. These findings validate Clariq's directed Knowledge Graph approach: it enforces prerequisite-aware scaffolding and surfaces misconceptions to teachers weekly. The crucial difference: because we ground retrieval in the CDC-prescribed SEE syllabus, every passage we retrieve aligns with both content coverage and depth that NEB examiners expect. That precision generic knowledge bases simply cannot match.

\subsection{Theme 3: Student Adoption and Teacher Integration}

Why would students actually choose to use such a system? Setälä studied Finnish secondary students adopting generative AI for maths and found that perceived usefulness---specifically for exam preparation---was the strongest adoption predictor \citep{setala2025}. Lu reinforced this: grade-improvement framing drives adoption \citep{lu2026}. For the SEE context, where the exam is a once-only milestone determining higher secondary progression, this insight matters deeply. Clariq's Knowledge Graph dashboard needs to provide immediate, tangible evidence of learning progress, connecting daily engagement directly to exam readiness.

Teachers present a different adoption barrier. Readiness depends on prior AI experience, professional development access, and quality of available resources \citep{addo2024}. Lian and Zhang found that performance expectancy and enabling conditions predict teacher adoption under the UTAUT framework \citep{liandzhang2024}. Clariq addresses both barriers through automated weekly teacher reports delivering diagnostic insight---strongest and weakest concepts per student, confusion frequency by topic---without requiring technical interaction.

\subsection{Theme 4: Ethical Considerations and Data Governance}

Any AI system collecting conversational data from minors, tracking behaviour across sessions, and sharing reports with teachers operates in ethically sensitive territory. Zhu et al. proposed a three-tier governance framework: data classification by sensitivity level, algorithmic ethics review, and clearly defined digital rights for students and teachers \citep{zhu2026}. That framework directly applies to Clariq.

Denzler documented a concerning trend: AI-assisted academic passivity increased following ChatGPT adoption, with suspicious submission rates jumping from 18\% to 26\% in one academic year \citep{denzler2024}. Clariq's model structurally prevents this---the system cannot produce exam answers, only redirect students through conceptual questions. Whyte found secondary students commonly anthropomorphise AI systems \citep{whyte2024}, so Clariq includes age-appropriate onboarding explaining its curriculum-based nature, defined limits, and the importance of cross-checking explanations against textbooks.

\subsection{Critical Analysis and Gap Identification}

Three research gaps define Clariq's space. First, no study validates Socratic tutoring across multi-domain secondary science (Physics, Chemistry, and Biology simultaneously). Second, no RAG pipeline has been seeded with a complete national secondary science syllabus and validated against actual examination marking expectations. Third, while Chen et al. infer mastery from homework submissions, real-time conversational signals pose a harder inference problem no secondary science study has tackled.

\subsection{Project Justification}

Academically, Clariq integrates Socratic tutoring, curriculum-grounded RAG, and real-time Knowledge Graph monitoring into a single evaluable system, addressing all three gaps. Practically, in Nepal and comparable contexts, qualified science teachers are unevenly distributed and private tutoring remains inaccessible for most. Clariq demonstrates that personalised SEE-aligned science tutoring can be delivered at marginal cost to any student with internet access, while grounding the design in responsible data governance.

% ============================================================
%  3.0  PROJECT AIMS, OBJECTIVES, AND SCOPE
% ============================================================
\section{Project Aims, Objectives, and Scope}

\subsection{Project Aim}

To design, develop, and evaluate Clariq---an AI-powered Socratic science tutor delivering curriculum-grounded personalised conversations for Nepal's Secondary Education Examination (Class~10) in Physics, Chemistry, and Biology; tracking individual gaps and misconceptions through an adaptive Knowledge Graph; generating structured weekly teacher reports; and demonstrating measurably better comprehension than traditional self-study in a controlled evaluation.

\subsection{Project Objectives}

\begin{enumerate}[label=\textbf{Objective \arabic*:}, leftmargin=*, align=left]

\item \textbf{Curriculum Dataset and RAG Pipeline.}
  Curate the full SEE Science syllabus (CDC, Nepal) into a hierarchical knowledge base, integrate it into a RAG pipeline using sentence-transformer embeddings and pgvector, achieving Precision@3 $\geq 0.85$ on 100 held-out test queries from NEB past papers (2016--2024), with manual ground-truth annotation of 300 relevance judgments.

\item \textbf{Socratic Tutor Model.}
  Fine-tune LLaMA-3-8B via LoRA on 700 examples (500 synthetic via GPT-4o-mini + 200 teacher-authored) constrained never to provide direct answers, achieving ROUGE-L $\geq 0.50$ and human pedagogical rating $\geq 4.0/5.0$ (Socratic adherence, curriculum accuracy, age-appropriate language, clarity, scaffolding) from five teachers (ICC $\geq 0.75$).

\item \textbf{System Integration and Backend.}
  Build a FastAPI backend orchestrating RAG and Socratic LLM with session state and Knowledge Graph updates, maintaining end-to-end latency $\leq 5$ seconds under typical load.

\item \textbf{Adaptive Knowledge Graph and Reporting.}
  Implement a directed graph encoding ~135 SEE concept nodes (Physics 45, Chemistry 50, Biology 40) with prerequisite edges validated by teacher consensus (Cohen's $\kappa \geq 0.70$), dynamically updated from session data, with automated weekly teacher reports validated for diagnostic usefulness.

\item \textbf{Controlled User Evaluation.}
  Conduct within-subjects crossover study with $n = 20$ SEE students (aged 15--16), measuring time-to-comprehension and retention versus textbook self-study, targeting 30\% reduction in comprehension time and statistically significant retention improvement ($\alpha = 0.05$), with inter-rater reliability (ICC $\geq 0.75$). Reduced from $n=40$ (80\% power) to $n=20$ (60\% power) to maintain timeline feasibility.

\end{enumerate}

\subsection{Project Scope}

Clariq handles science queries within SEE Physics, Chemistry, and Biology syllabi, supporting multi-turn Socratic dialogue. Out of scope: open-ended conversation, direct exam answers, school management integration. The RAG base uses syllabus documents and NEB-aligned textbooks; students may upload personal notes. The Knowledge Graph covers full SEE syllabus at concept level. Evaluation uses a prototype web application.

% ============================================================
%  4.0  PROJECT DESIGN
% ============================================================
\section{Project Design}

Clariq is structured across six layers connected through FastAPI: data ingestion (offline), student input, RAG retrieval, LLM inference, Knowledge Graph monitoring, and reporting. The architecture diagram (Figure~\ref{fig:architecture}) shows the full pipeline.

\begin{figure}[H]
    \centering
    \includegraphics[width=\textwidth]{clariq_architecture.png}
    \caption{System architecture: FastAPI backend orchestrates RAG retrieval, four-layer Socratic Constraint Enforcement, LLaMA-3-8B (LoRA), and adaptive Knowledge Graph (~135 concept nodes) for real-time monitoring and weekly teacher reports.}
    \label{fig:architecture}
\end{figure}

\subsection{Design and Methods}

The approach is design-and-build: construct a working system, then evaluate its feasibility.

\textbf{Data Ingestion.} PyMuPDF extracts text from CDC curriculum PDFs. LangChain chunks content into 300-token segments (50-token overlap), tagged with subject and hierarchy; sentence-transformers encode embeddings stored in pgvector.

\textbf{Student Input.} A React.js interface accepts typed queries and PDF uploads (notes, past papers), injecting uploads into session context only, keeping the verified knowledge base uncontaminated.

\textbf{RAG and LLM Inference.} FastAPI retrieves top-$k$ curriculum chunks and passes them to LLaMA-3-8B (LoRA), whose system prompt constrains it never to provide direct answers. Example: when a student asks ``Why does ice float?'', Clariq responds: ``What do you remember about what happens to density when substances freeze?''---activating prior knowledge rather than supplying the answer \citep{goyal2026,reiser2004}.

\textbf{Student Response Evaluation Loop.} When students answer Socratic prompts:
\begin{enumerate}[itemsep=2pt]
  \item \textbf{Retrieval Context}: Fetch top-$k$ passages matched to the question
  \item \textbf{Embedding}: Encode response and passages using sentence-transformers (384-dimensional)
  \item \textbf{Similarity}: Compute $\text{sim} = \cos(\mathbf{e}_{\text{student}}, \mathbf{e}_{\text{curriculum}})$ (range [0, 1])
  \item \textbf{Coherence Penalty}: Detect rote copying (>80\% overlap $\times 0.5$), fragmentation (<5 words $\times 0.3$); apply $s_t = \text{sim} \times \text{coherence}_{\text{penalty}}$
  \item \textbf{Mastery Update}: $m_{t+1} = m_t + \alpha(s_t - m_t)$, where $\alpha = 0.25$ (cold-start: $m_0 = 0.5$)
\end{enumerate}

\emph{Example:} When a student answers a Socratic prompt, the system computes semantic similarity $s_t = \text{sim} \times \text{coherence}$ and updates mastery via $m_{t+1} = m_t + \alpha(s_t - m_t)$.

Responses with $s_t < 0.40$ trigger follow-up Socratic prompts; three consecutive $s_t < 0.40$ flags confusion for teacher alert.

\textbf{Knowledge Graph.} Each student's state is a directed graph encoding ~135 concept nodes across Physics (45), Chemistry (50), Biology (40) with prerequisite edges from teacher validation (Cohen's $\kappa \geq 0.70$). Example: ``Density'' $\rightarrow$ ``Buoyancy''. Nodes with $m_t \geq 0.75$ unlock dependents; sustained confusion ($s_t < 0.4$ for 3+ attempts) flags for weekly teacher report. Graph construction: extract learning outcomes $\rightarrow$ interview 3--5 teachers for dependencies $\rightarrow$ validate with 2 independent teachers.

\subsection{Evaluation}

The system is evaluated on three dimensions: technical performance, learning effectiveness, and usability.

\textbf{Technical performance.} RAG precision: Precision@3 metric on 100 test queries (5 per subject, 2016--2024 NEB papers), manually annotating top-3 relevant passages per query for ground truth (300 judgments). Success: $\text{Precision@3} \geq 0.85$. If $< 0.85$, tune chunk sizes (200/300/400 tokens), trial bge-base-en-v1.5 embedding, add cross-encoder re-ranking. ROUGE-L ($\geq 0.50$) evaluates Socratic quality against teacher-written references. Latency tested under simulated 10 concurrent sessions ($\leq 5$~s).

\textbf{Learning effectiveness.} Within-subjects crossover: $n = 20$ Class~10 students (aged 15--16), session order counterbalanced. Each completes one Clariq session and one textbook excerpt on the same concept. 10-item MCQ pre-test establishes baseline; parallel post-tests measure immediate and one-week delayed retention. Analysis: paired $t$-test (or Wilcoxon if non-normal), Cohen's $d$ effect size, Benjamini--Hochberg FDR correction ($\alpha = 0.05$).

\textbf{Pedagogical rating.} Five teachers independently rate 30 sampled responses on a five-point Likert rubric: (1) Socratic adherence, (2) curriculum accuracy, (3) age-appropriate language, (4) guiding question clarity, (5) scaffolding quality. ICC$_{(3,k)}$ Consistency ($\geq 0.75$). Pass threshold: mean rating $\geq 4.0/5.0$.

\textbf{Usability.} System Usability Scale (SUS) for students (n=20) and teachers (n=5) after evaluation; score $\geq 68$ acceptable. Semi-structured interviews (10 min per participant) gather qualitative feedback on Knowledge Graph understandability and teacher report actionability.

\subsection{Justification of Methods}

Design-and-build is required because both research questions are systems-level and demand a functioning prototype. 

\textbf{LLaMA-3-8B with LoRA} eliminates API costs, making continuous student use economically viable. Fine-tuning dataset: 700 examples (500 synthetic via GPT-4o-mini prompt: ``Generate a Socratic response using only curriculum context. Never give direct answers.'', validated by $\geq 1$ teacher; 200 teacher-authored). Quality gates: every synthetic example rated $\geq 3/5$ on Socratic adherence; remove direct answers. Target: ROUGE-L $\geq 0.50$ and rating $\geq 4.0/5.0$.

\textbf{Socratic Constraint Enforcement:} (Layer~1) System prompt explicitly constrains the LLM. (Layer~2) DistilBERT classifier screens responses ($P(\text{direct answer}) > 0.6$ $\Rightarrow$ reject and regenerate). (Layer~3) Retrieval-only mode passes concept headers, not full answers. (Layer~4) Template fallback (3$\times$ consecutive rejections $\Rightarrow$ human-approved templates like ``Think about [CONCEPT]. What do you know?''). Validation: 50 known-answer questions; target $\leq 5\%$ violations.

\textbf{Sample size:} $n = 20$ (instead of 40) balances power (60\% vs 80\%) with timeline feasibility; recruitment and evaluation run concurrent with system development (Weeks~8--20, 3--4 hours per student).

\subsection{Project Timeline}

30 weeks across seven phases (11~April -- 11~October~2026). Key milestones: RAG pipeline ready (Week~9), interim report (Week~14), Knowledge Graph validation (Week~7), LoRA fine-tuning (Week~11), integrated system (Week~23), student recruitment begins Week~8, evaluation Weeks~15--20 concurrent with teacher report development, analysis and writing (Weeks~21--27), final submission (Week~30). Feasible through parallel development and recruitment. Gantt chart (Figure~\ref{fig:gantt}) shows full schedule.

\begin{figure}[H]
    \centering
    \includegraphics[width=\textwidth]{clariq_gantt_chart.png}
    \caption{Project Gantt chart (Apr~2026 -- Oct~2026, 7 phases). Red dashed line marks today (27~April 2026). Red diamonds indicate key milestones.}
    \label{fig:gantt}
\end{figure}

% ============================================================
%  5.0  FEASIBILITY, RISKS, AND ETHICAL ASPECTS
% ============================================================
\section{Feasibility, Risks, and Ethical Aspects}

\subsection{Feasibility}

All core technologies are open-source and well-documented. The SEE syllabus is publicly available. School partnerships are underway. $n = 20$ students is achievable over a 4--6 week window (Weeks~15--20) with concurrent system development. Fine-tuning dataset acquisition: 500 synthetic examples via GPT-4o-mini (Weeks~4--5) and 200 teacher-authored dialogues (Week~5). Knowledge Graph validation: 5 teachers (Weeks~6--7, Cohen's $\kappa$ test). Skill gaps in LoRA and RAG will be addressed through Hugging~Face PEFT and LangChain documentation in Phase~1.

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
Augment with additional GPT-4o-mini examples; implement multi-layer Socratic enforcement (Layers 1--4) as fallback to compensate for weaker ROUGE. \\
\hline
RAG precision $<0.85$ on test queries &
M & H &
Tune chunk size (200/300/400 tokens); trial bge-base-en-v1.5 embedding; add cross-encoder re-ranking; iteratively expand test query set. \\
\hline
Study participants $<20$ &
M & M &
Begin recruitment Week~8; identify $n \geq 3$ backup schools; prepare remote/hybrid evaluation option; use stratified sampling if $n>20$ to ensure Physics/Chemistry/Biology balance. \\
\hline
Teacher validation for KG edges ($\kappa < 0.70$) &
M & H &
If consensus weak, reduce scope to core Physics concepts only; iterate with additional teachers. \\
\hline
GPU unavailable for fine-tuning &
L & H &
Use Colab Pro or Kaggle; schedule training off-peak (nights/weekends); prepare checkpoint restart. \\
\hline
School partner withdraws &
L & H &
Identify two backup schools by Week~7; prepare university-network recruitment fallback. \\
\hline
\end{tabular}
\end{table}

\subsection{Ethical Considerations}

\textbf{Student data and privacy.} All participants are minors (Class~10, aged ~15--16) requiring written informed consent from student and parent/guardian. Session transcripts and Knowledge Graph data are anonymised at collection; no personally identifiable information stored alongside analytics. Data retained per university policy and UK~GDPR, accessible only to student and their designated teacher.

\textbf{Algorithmic fairness and academic integrity.} Clariq's Socratic model structurally prevents academic passivity by never providing direct answers \citep{denzler2024}. Mastery assessments are diagnostic only---communicated to teachers as support data, not formal grades---and teachers retain full professional authority over assessment.

\textbf{AI literacy.} Following Whyte, onboarding explains Clariq is a curriculum-based AI with defined limits and potential for mistakes; students are encouraged to verify against textbooks, preventing anthropomorphism \citep{whyte2024}.

\textbf{Data governance.} Session transcripts, mastery scores, and confusion flags are stored separately from identifiable records (Zhu et al. framework). All outputs undergo ethical review before student deployment. Teacher digital rights---including the right to disregard recommendations---are documented in the teacher interface.

% ============================================================
%  BIBLIOGRAPHY
% ============================================================
\newpage
\addcontentsline{toc}{section}{References}
\bibliography{references}

\end{document}
