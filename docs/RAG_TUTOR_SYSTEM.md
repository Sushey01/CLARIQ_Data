# RAG Conversational Tutor System Architecture

## Overview

Build a ChatGPT-like conversational tutor that:

- ✅ Answers student questions about science
- ✅ Asks questions to assess understanding
- ✅ Tracks student performance over time
- ✅ Personalizes learning based on progress
- ✅ Adapts curriculum to student needs

---

## 5 CSV Files You Need

### 1️⃣ **RAG Knowledge Base** (`rag_knowledge_base.csv`)

**Purpose:** The document store that the RAG model retrieves from.

**Columns:**

```csv
doc_id,source_pdf,page,topic,subtopic,difficulty,doc_type,content,word_count
jesc110.pdf_1_1,jesc110.pdf,1,The Human Eye,Biology - Human Eye,medium,explanatory,"The human eye is...",147
jesc110.pdf_1_2,jesc110.pdf,1,The Human Eye,Biology - Human Eye,medium,explanatory,"The eye lens...",136
```

**Why This Format:**

- `topic` + `subtopic` - for semantic search and filtering
- `difficulty` - to match student's current level
- `doc_type` - distinguish definitions from examples
- `content` - what gets embedded and retrieved

**How RAG Uses It:**

```
Student Question: "How does the eye focus on objects?"
                       ↓
            Embed the question
                       ↓
        Search knowledge base for similar docs
                       ↓
      Retrieve top 3 most relevant documents
                       ↓
     Pass documents + question to LLM (like GPT)
                       ↓
  LLM generates answer based on documents
```

**Example Retrieval:**

```python
from sentence_transformers import SentenceTransformer
import pandas as pd

model = SentenceTransformer('all-MiniLM-L6-v2')
kb = pd.read_csv('rag_knowledge_base.csv')

question = "How does the eye lens work?"
question_embedding = model.encode(question)

# Find most relevant documents
for idx, doc in kb.iterrows():
    similarity = model.util.pytorch_cos_sim(question_embedding,
                                           model.encode(doc['content']))
    # Retrieve top-3 most relevant docs
```

---

### 2️⃣ **Question Bank** (`question_bank.csv`)

**Purpose:** Questions the tutor asks students for assessment.

**Columns:**

```csv
question_id,question_text,question_type,topic,subject,difficulty,related_doc_id,expected_answer_context
Q1,What is the Human Eye?,definition,The Human Eye,biology,easy,jesc110.pdf_1_1,"The human eye is one of..."
Q5,How does the eye lens work?,explanation,The Human Eye,biology,medium,jesc110.pdf_1_2,"The eye lens is composed of..."
Q12,Give an example of accommodation,application,The Human Eye,biology,hard,jesc110.pdf_1_3,"The eye lens adjusts..."
```

**Question Types:**

- `definition` - "What is X?" (easy)
- `explanation` - "How does X work?" (medium)
- `application` - "Give examples of X" (hard)
- `comparison` - "Compare X and Y" (hard)

**How Tutor Uses It:**

```
System Flow:
1. Analyze student performance → "Student mastered easy topics"
2. Select MEDIUM difficulty question from Question Bank
3. Ask: "How does the eye lens work?"
4. Student answers
5. Compare with expected_answer_context in knowledge base
6. Score the answer using RAG (semantic matching)
7. Update student performance
```

---

### 3️⃣ **Student Interactions** (`student_interactions.csv`)

**Purpose:** Log every Q&A interaction for analysis and personalization.

**Columns:**

```csv
interaction_id,student_id,timestamp,question_id,student_answer,correct,answer_quality,time_taken_seconds,hints_used,topic_covered,difficulty_level
STU001_INT_0,STU001,2026-04-26 10:30:00,Q1,The eye is an organ for vision,yes,excellent,45,0,The Human Eye,easy
STU001_INT_1,STU001,2026-04-29 14:15:00,Q5,The lens... makes light focus,yes,good,120,1,The Human Eye,medium
STU001_INT_2,STU001,2026-05-02 09:45:00,Q12,Example of accommodation...,no,poor,180,2,The Human Eye,hard
```

**Tracked Data:**

- `student_answer` - What student actually answered
- `correct` - Was it right/wrong
- `answer_quality` - How good is the answer (excellent/good/poor)
- `time_taken_seconds` - How long they took
- `hints_used` - How many hints did they need
- `difficulty_level` - Was this question suited to them?

**Analysis Examples:**

```python
import pandas as pd

interactions = pd.read_csv('student_interactions.csv')

# Find struggling topics
struggling = interactions[interactions['correct'] == 'no'].groupby('topic_covered').size()
print("Student needs help with:", struggling.index[0])

# Check if student is ready for next level
easy_accuracy = interactions[interactions['difficulty_level'] == 'easy']['correct'].value_counts()['yes'] / len(interactions)
if easy_accuracy > 0.80:
    next_question_difficulty = 'medium'
```

---

### 4️⃣ **Student Performance** (`student_performance.csv`)

**Purpose:** Aggregated metrics to guide curriculum adaptation.

**Columns:**

```csv
student_id,topic,questions_attempted,questions_correct,accuracy_percent,average_time_seconds,mastery_level,last_attempted,readiness_for_next_topic
STU001,The Human Eye,15,12,80,120,intermediate,2026-05-02,yes
STU001,Light and Refraction,8,5,62,180,beginner,2026-04-28,no
STU002,The Human Eye,10,10,100,90,advanced,2026-05-02,yes
STU002,Light and Refraction,0,0,0,0,beginner,2026-03-01,no
```

**Mastery Levels:**

- `beginner` - accuracy < 70%
- `intermediate` - accuracy 70-85%
- `advanced` - accuracy > 85%

**Real-World Usage:**

```python
perf = pd.read_csv('student_performance.csv')

student = perf[perf['student_id'] == 'STU001']

# Create personalized curriculum
for topic in student.sort_values('mastery_level'):
    if topic['mastery_level'] == 'beginner':
        print(f"Ask more EASY questions on {topic['topic']}")
    elif topic['mastery_level'] == 'intermediate':
        print(f"Challenge with MEDIUM questions on {topic['topic']}")
    elif topic['mastery_level'] == 'advanced':
        print(f"Move to NEXT TOPIC - prerequisite met!")
```

---

### 5️⃣ **Curriculum Paths** (`curriculum_paths.csv`)

**Purpose:** Define the learning sequence and prerequisites.

**Columns:**

```csv
path_id,topic_name,description,order,prerequisite_topics,estimated_hours,target_difficulty,required_accuracy_percent
PATH001,Understanding Light,Learn about light and refraction,1,None,4,easy,80
PATH002,The Human Eye,Learn eye anatomy and vision,2,Understanding Light,3,medium,75
PATH003,Vision Defects,Learn about vision problems,3,"The Human Eye, Understanding Light",3,medium,75
PATH004,Advanced Optics,Advanced concepts,4,Vision Defects,5,hard,85
```

**How System Uses It:**

```
Student STU001 Performance:
├─ PATH001 (Understanding Light): 85% ✅ PASS
├─ PATH002 (The Human Eye): 78% ⚠️  Borderline
└─ PATH003 (Vision Defects): Prerequisites not fully met

System Decision:
→ Recommend: "Review Understanding Light concepts"
→ Then: "Practice medium difficulty questions on The Human Eye"
→ When ready (>75%): "Advance to Vision Defects"
```

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│         CONVERSATIONAL TUTOR SYSTEM (RAG-Based)             │
└─────────────────────────────────────────────────────────────┘

                    Student Input
                         ↓
        ┌────────────────────────────────┐
        │  Determine Student Level       │
        │ (student_performance.csv)      │
        └────────────────────────────────┘
                         ↓
        ┌────────────────────────────────┐
        │  Select Question               │
        │ (question_bank.csv)            │
        │  - Matched to current level    │
        │  - Covers weak topics          │
        └────────────────────────────────┘
                         ↓
        ┌────────────────────────────────┐
        │  Ask Question to Student       │
        └────────────────────────────────┘
                         ↓
                 Student Answer
                         ↓
        ┌────────────────────────────────┐
        │  RAG Scoring System            │
        │ 1. Retrieve relevant docs      │
        │    (rag_knowledge_base.csv)    │
        │ 2. Embed student answer        │
        │ 3. Compare with expected ans   │
        │ 4. Generate score/feedback     │
        └────────────────────────────────┘
                         ↓
        ┌────────────────────────────────┐
        │  Log Interaction               │
        │ (student_interactions.csv)     │
        └────────────────────────────────┘
                         ↓
        ┌────────────────────────────────┐
        │  Update Performance            │
        │ (student_performance.csv)      │
        └────────────────────────────────┘
                         ↓
        ┌────────────────────────────────┐
        │  Adapt Curriculum              │
        │ (curriculum_paths.csv)         │
        │  - Stay on current path?       │
        │  - Move to next level?         │
        │  - Review prerequisites?       │
        └────────────────────────────────┘
                         ↓
              Personalized Next Step
```

---

## How to Build This System

### Step 1: Create Data CSVs

```bash
python create_rag_tutor_data.py
```

### Step 2: Set Up RAG with LangChain/LlamaIndex

```python
from sentence_transformers import SentenceTransformer
import pandas as pd

# Load knowledge base
kb = pd.read_csv('rag_knowledge_base.csv')
model = SentenceTransformer('all-MiniLM-L6-v2')

# Build embeddings
embeddings = model.encode(kb['content'].tolist())

# Store in vector DB (Chroma, which you already use!)
import chromadb
client = chromadb.Client()
collection = client.create_collection("curriculum")
collection.add(embeddings=embeddings.tolist(),
               documents=kb['content'].tolist(),
               ids=kb['doc_id'].tolist())
```

### Step 3: Scoring Student Answers

```python
def score_student_answer(student_answer, question_id, model):
    # Get the question
    questions = pd.read_csv('question_bank.csv')
    question = questions[questions['question_id'] == question_id].iloc[0]

    # Get expected answer from knowledge base
    kb = pd.read_csv('rag_knowledge_base.csv')
    expected = kb[kb['doc_id'] == question['related_doc_id']]['content'].iloc[0]

    # Score using semantic similarity
    student_emb = model.encode(student_answer)
    expected_emb = model.encode(expected)

    similarity = model.util.pytorch_cos_sim(student_emb, expected_emb)

    if similarity > 0.8:
        return 'yes', 'excellent'
    elif similarity > 0.6:
        return 'yes', 'good'
    else:
        return 'no', 'poor'
```

### Step 4: Adaptive Curriculum

```python
def get_next_step(student_id):
    perf = pd.read_csv('student_performance.csv')
    paths = pd.read_csv('curriculum_paths.csv')

    student = perf[perf['student_id'] == student_id]

    # Find highest completed path
    completed = student[student['readiness_for_next_topic'] == 'yes']

    if len(completed) > 0:
        current_order = paths[paths['path_id'].isin(completed['topic'])]['order'].max()
        next_path = paths[paths['order'] == current_order + 1]

        return f"Ready to learn: {next_path.iloc[0]['topic_name']}"
    else:
        return "Review fundamentals"
```

---

## Sample Workflow

**Interaction 1: Easy Assessment**

```
Tutor: "What is the human eye?"
Student: "It's an organ for vision"
System: ✅ CORRECT (90% match)
        Score: excellent
        Accuracy: 100% on easy questions
```

**Interaction 2: Medium Challenge**

```
Tutor: "How does the eye lens focus on objects at different distances?"
Student: "The lens changes shape to focus"
System: ⚠️  PARTIALLY CORRECT (65% match)
        Score: good
        Accuracy: 50% on medium questions → "Needs more practice"
```

**Performance Summary:**

```
STU001 Progress:
├─ Easy questions: 100% accuracy ✅
├─ Medium questions: 50% accuracy ⚠️
└─ Recommendation: "Keep practicing medium questions before hard level"
```

---

## Benefits of This System

✅ **RAG-based answers** - Answers grounded in curriculum, not hallucinations  
✅ **Adaptive learning** - Questions match student's current level  
✅ **Performance tracking** - See where each student struggles  
✅ **Personalized curriculum** - Each student gets custom learning path  
✅ **Scalable** - Works for any number of students  
✅ **Explainable** - Can show which document answered each question

---

## Next: Implement with Your Teacher

Show your teacher:

1. The 5 CSV files generated
2. How they connect in the system
3. The learning architecture
4. Real student performance examples

This is production-grade RAG system design! 🚀
