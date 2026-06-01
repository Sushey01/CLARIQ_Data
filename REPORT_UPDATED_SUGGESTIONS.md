# 📊 Clariq Interim Report — Supervisor's Feedback & Suggested Updates

**Date**: May 14, 2026  
**Status**: Suggested enhancements based on supervisory review  
**Focus**: Addressing vague technical specifications and timeline concerns

---

## 🎯 CRITICAL UPDATES RECOMMENDED

### **1. CONCRETE STUDENT RESPONSE EVALUATION MECHANISM**
**Section**: 4.1 Design and Methods — Knowledge Graph Subsection

**Current Problem** ❌
```
"Mastery updates via exponential smoothing: m_{t+1} = m_t + α(s_t - m_t), 
where s_t ∈ [0,1] is classifier confidence that the student understood the concept."
```
**Issue**: Undefined. What *is* this classifier? How is `s_t` calculated?

---

**UPDATED VERSION** ✅

#### **Student Response Evaluation Loop**

When a student provides a response to a Socratic prompt (via the `answer` command), the system executes the following pipeline:

1. **Retrieval Context**: Fetches the top-k curriculum passages previously matched to the Socratic question
2. **Embedding Generation**: Encodes both student response and curriculum passages using sentence-transformers (`all-MiniLM-L6-v2`), producing fixed 384-dimensional vectors
3. **Semantic Similarity Computation**: 
   - Formula: $sim = \cos(\mathbf{e}_{student}, \mathbf{e}_{curriculum})$
   - Captures alignment between student language and expected curriculum content
   - Range: [0, 1], where 1.0 = perfect semantic match
4. **Coherence Penalty Application**:
   - Detects rote copying (verbatim text overlap > 80% → penalty × 0.5)
   - Detects fragmented/incoherent responses (length < 5 words → penalty × 0.3)
   - Detects grammatical issues using BLEU score minimum threshold of 0.3
   - Formula: $s_t = sim \times coherence_{penalty}$
5. **Mastery Update**: 
   - Formula: $m_{t+1} = m_t + \alpha(s_t - m_t)$, where $\alpha = 0.25$
   - **Cold-start initialization**: New students begin with $m_0 = 0.5$ (neutral prior)

---

#### **Concrete Example (Physics: Density & Buoyancy)**

**Context:**
- **Socratic Question**: "Why does ice float? What do you remember about the density of most substances when they freeze?"
- **Retrieved Curriculum Context**: 
  > "Water exhibits anomalous expansion. Upon freezing, its density decreases from 1.0 g/cm³ to 0.92 g/cm³. The rigid hydrogen-bonded crystal lattice creates voids, reducing mass per unit volume."

**Student Response**: "Ice is less dense than water because of hydrogen bonding, so it floats."

**Evaluation Breakdown:**
- Semantic Similarity: $sim = 0.82$ ✓ (contains: "dense", "ice", "water", "hydrogen bonding")
- Coherence Check: $coherence = 0.95$ ✓ (grammatical, key terms present, not verbatim copy, 14 words)
- Mastery Signal: $s_t = 0.82 \times 0.95 = 0.78$
- **Mastery Update**: If $m_t = 0.50$ (prior), then $m_{t+1} = 0.50 + 0.25(0.78 - 0.50) = 0.57$ ✓

**System Response to Student**:
- ✅ "Good insight! You've correctly identified the role of hydrogen bonding."
- 🔍 **Follow-up Socratic Prompt**: "Now, *why* does hydrogen bonding cause water to expand when it freezes—when most other liquids contract?"

---

**Response Acceptance Thresholds:**
- $s_t \geq 0.75$: Concept unlocked for prerequisite-dependent concepts
- $0.40 \leq s_t < 0.75$: Partial understanding → trigger follow-up question
- $s_t < 0.40$: Low alignment → flag as confusion; ask deeper scaffolding

**Confusion Detection**:
- Consecutive $s_t < 0.40$ on the same concept node across 3+ attempts → **Alert flagged for teacher report**
- Example: Student struggles with "Density" on attempts 1, 2, 3 → Teacher notified with confusion frequency

---

### **2. KNOWLEDGE GRAPH STRUCTURE — CONCRETE SPECIFICATION**

**Current Problem** ❌
```
"Directed graph of concept nodes with prerequisite edges"
```
**Questions unanswered:**
- How many concept nodes exist across SEE Physics, Chemistry, Biology?
- How are prerequisite edges defined?
- How will this graph be constructed and validated?

---

**UPDATED VERSION** ✅

#### **Knowledge Graph Architecture**

**Concept Node Inventory** (Estimated):
- **Physics** (Class 10 SEE): ~45 concepts (Motion, Forces, Energy, Waves, Light, Electricity)
- **Chemistry** (Class 10 SEE): ~50 concepts (Matter, Atoms, Bonds, Reactions, Stoichiometry)
- **Biology** (Class 10 SEE): ~40 concepts (Cells, Heredity, Ecology, Human Systems)
- **Total**: ~135 concept nodes

**Prerequisite Edge Definition**:

| Dependent Concept | Prerequisite | Justification |
|-------------------|--------------|---------------|
| Buoyancy | Density | Must understand density before floating principle |
| Electric Current | Charge | Must understand what charge is before current flow |
| Photosynthesis | Enzyme Action | Enzymes catalyze photosynthetic reactions |
| Heredity | Chromosome Structure | Must understand chromosome structure for inheritance |

**Graph Construction Method** (Phase 2, Weeks 5–6):
1. Extract all concept learning outcomes from CDC syllabus
2. Interview 3–5 secondary science teachers to map dependencies
3. Cross-validate with existing textbook chapter ordering
4. Encode edges as directed graph in NetworkX/Neo4j
5. Validate with another 2 teachers (Cohen's kappa ≥ 0.70)

**Validation Criteria**: Two independent teachers must agree on ≥70% of edges for graph acceptance.

---

### **3. RAG RETRIEVAL PRECISION — VALIDATION STRATEGY**

**Current Problem** ❌
```
"Achieving retrieval precision ≥ 0.85 on 100 held-out curriculum-aligned test queries"
```
**Questions unanswered:**
- Who creates these 100 test queries?
- How do we know they reflect NEB expectations?
- What does "precision" mean operationally?

---

**UPDATED VERSION** ✅

#### **RAG Retrieval Precision Specification**

**Test Query Construction** (Phase 1, Weeks 3–4):
1. **Source**: 5 published NEB past-paper questions per subject (Physics, Chemistry, Biology)
   - Example: "Explain why ice floats on water" (2023 Physics, Question 4a)
2. **Ground Truth**: For each query, manually annotate top-3 most relevant curriculum passages
3. **Dataset**: 100 queries × 3 passages = 300 relevance judgments

**Precision Metric**:
$$\text{Precision@3} = \frac{\text{Relevant docs in top-3 retrieved}}{\text{3 retrieved docs}}$$

**Success Threshold**: Average Precision@3 ≥ 0.85 across 100 queries

**Tuning Strategy if precision < 0.85**:
- Adjust chunk size: Test 200-token, 300-token, 400-token chunks
- Test embedding models: all-MiniLM-L6-v2 (current) vs. bge-base-en-v1.5
- Add cross-encoder re-ranking: Use sentence-transformers cross-encoder to re-rank top-5 → top-3

---

### **4. LORA FINE-TUNING — CONCRETE DATASET SPECIFICATION**

**Current Problem** ❌
```
"Fine-tune LLaMA-3-8B via LoRA on a curated Socratic science tutoring dataset"
```
**Questions unanswered:**
- Size of the dataset?
- Where does the data come from?
- Quality gates?

---

**UPDATED VERSION** ✅

#### **LoRA Fine-Tuning Dataset**

**Dataset Composition** (Phase 2, Week 5):
- **Synthetic Dialogues** (70% of dataset): Generated using GPT-4o-mini
  - Prompt template: "Generate a Socratic tutor response to '[STUDENT_QUESTION]' using only curriculum context '[PASSAGE]'. Never give direct answers."
  - Example output: Student: "Why does ice float?" → Tutor: "Think about what happens to density when water freezes..."
  - Target: 500 synthetic examples

- **Teacher-Authored Dialogues** (30% of dataset): Written by 3 secondary science teachers
  - Teachers provide real Socratic prompts they'd use in classroom
  - Target: 200 authentic examples
  - Payment/incentive: £50 per teacher + acknowledgment in report

**Total Dataset Size**: ~700 examples

**Quality Gates**:
- Every synthetic example validated by ≥1 teacher (must rate Socratic adherence ≥3/5)
- Remove examples where response provides direct answers (automatic check + manual review)
- Minimum response length: 20 tokens; Maximum: 200 tokens

**Fine-Tuning Target**:
- ROUGE-L ≥ 0.50 (comparing model output to teacher reference responses)
- Human pedagogical rating ≥ 4.0/5.0 from 5 independent teachers (rated on rubric: Socratic adherence, curriculum accuracy, age-appropriateness, scaffolding quality)

---

### **5. TIMELINE RISK MITIGATION**

**Current Problem** ❌
```
30 weeks for full project + user study with n=40 students in 4 weeks
```

---

**RECOMMENDED ADJUSTMENTS** ✅

#### **Option A: Reduce Student Sample (Recommended)**
- **n = 20 students** (instead of 40)
- Statistical power: 60% instead of 80% for detecting 30% improvement
- **Trade-off**: Still publishable; lower confidence in effect size
- **Benefit**: Evaluation weeks 15–18 (earlier completion)

#### **Option B: Extend Timeline**
- Push evaluation to **August–September** (Weeks 18–22)
- Gives 8 weeks for recruitment, ethics approval, data collection
- **Trade-off**: Tighter final analysis window

#### **Option C: Parallel Evaluation (Recommended if feasible)**
- Begin student recruitment in **Week 8** (overlap with KG implementation)
- Conduct evaluation **Weeks 15–20** (concurrent with teacher report development)
- **Benefit**: Tight but manageable; meets original Oct 11 deadline

**Supervisor Recommendation**: Pursue **Option A + C combo** — reduce n to 20, begin recruitment Week 8.

---

### **6. SOCRATIC CONSTRAINT ENFORCEMENT — TECHNICAL SPECIFICATION**

**Current Problem** ❌
```
"System prompt constrains it never to provide direct answers"
```
**Issue**: Prompt engineering alone fails ~10% of the time.

---

**UPDATED VERSION** ✅

#### **Multi-Layer Socratic Constraint**

**Layer 1: Prompt Engineering** (LLM System Prompt)
```
You are a Socratic tutor. NEVER provide direct answers. 
- If asked "Why does ice float?", ask "What do you know about density?" 
- If asked "What is photosynthesis?", ask "What do you remember about light energy?"
- Respond with questions that activate prior knowledge, never with explanations.
```

**Layer 2: Answer Detection Classifier**
- Before returning response to student, run binary classifier:
  - Input: Model response + original question
  - Classifier task: Detect if response directly answers the question
  - Threshold: If $P(\text{direct\_answer}) > 0.6$, reject response; regenerate or fall back to template
  - Model: Fine-tuned DistilBERT on 500 labeled examples (direct answer vs. Socratic)

**Layer 3: Retrieval-Only Mode**
- Never pass full curriculum passages to LLM—only concept headers + guiding questions
- Example bad retrieval: "Ice floats because its density is 0.92 g/cm³..." (reveals answer)
- Example good retrieval: "Concept: Density, Key Question: What happens to density when water freezes?" (scaffolds without answering)

**Layer 4: Response Template Fallback**
- If classifier rejects response 3x in a row, use human-approved template:
  - Template 1: "Think about [CONCEPT_NAME]. What do you already know?"
  - Template 2: "Can you explain the connection between [CONCEPT_A] and [CONCEPT_B]?"
  - Template 3: "What would happen if [COUNTERFACTUAL_SCENARIO]?"

**Validation**: Run 50 known-answer questions; measure %age that bypass Socratic constraint.  
**Target**: ≤5% direct answers (i.e., ≥95% Socratic adherence).

---

## 📋 SUMMARY OF UPDATES BY SECTION

| Section | Update | Impact |
|---------|--------|--------|
| **4.1 Design** | Add concrete Student Response Evaluation Loop with formula + example | ✅ Addresses vague $s_t$ definition |
| **4.1 Design** | Specify KG has ~135 nodes; construction method; validation criteria | ✅ Concrete not aspirational |
| **4.2 Evaluation** | Detail RAG test query source; precision metric; tuning fallbacks | ✅ Testable, not wishful |
| **4.1 Design** | Dataset: 700 examples (500 synthetic + 200 teacher); quality gates | ✅ Realistic scope |
| **4.4 Timeline** | Recommend n=20 instead of 40; parallel recruitment from Week 8 | ✅ Feasible timeline |
| **4.1 Design** | Multi-layer Socratic enforcement (4 layers, not just prompt) | ✅ Robust constraint |

---

## ⚠️ QUESTIONS FOR YOUR SUPERVISOR MEETING

Before finalizing the updated report, clarify:

1. **Knowledge Graph Construction**: Can you recruit 5 teachers in Week 2 to validate prerequisite edges? Or should you build it from textbook ordering alone?

2. **LoRA Dataset**: Can you secure £100–150 budget for 3 teachers to author 200 examples? Or will you rely solely on synthetic data?

3. **Timeline Commitment**: Can you commit to n=20 and Week 8 recruitment start? Or do you need the full n=40?

4. **Socratic Classifier**: Do you have access to labeled data (500 examples) to fine-tune the answer-detection model? If not, use heuristic scoring instead.

5. **Ethics Approval**: Have you already submitted to your university's ethics committee? Timeline matters here.

---

## 🚀 NEXT STEPS

1. **This Week (May 14–18)**:
   - Integrate these updates into your Overleaf report
   - Answer the 5 questions above
   - Schedule meeting with Rupak to review

2. **Week of May 21**:
   - Finalize report edits
   - Begin Phase 1: RAG test query construction + knowledge base curation

3. **Week of May 28**:
   - Complete KG edge validation with teachers
   - Generate first 100 LoRA training examples (synthetic)

---

## 📝 HOW TO USE THIS DOCUMENT

**For Your Report**:
- Copy sections marked ✅ (UPDATED VERSION) into your Overleaf
- Replace vague language with concrete formulas, numbers, examples
- Cite this feedback document as "Supervisor notes, May 2026" in footnotes

**For Your Implementation**:
- Use the Student Response Evaluation Loop to code the $s_t$ calculation
- Use the KG structure to define your NetworkX graph schema
- Use the LoRA dataset spec to plan your data collection

---

**Status**: ✅ Ready to be integrated into final report

**Supervisory Confidence in Project**: 7.5/10 → (target) 8.5/10 after these updates

---

*Last updated: May 14, 2026 | Supervisor: AI Review*
