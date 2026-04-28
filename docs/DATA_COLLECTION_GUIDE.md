# Data Collection & CSV Structure for Your RAG Tutor

## 📋 Summary: What Data Do You Actually Need?

Your conversational tutor needs **4 types of data** collected and stored as CSVs:

---

## 1️⃣ **Knowledge Base (For RAG Retrieval)**

**CSV File:** `rag_knowledge_base.csv` (Already created ✅)

```csv
doc_id,source_pdf,page,topic,subtopic,difficulty,doc_type,content,word_count
```

**What it contains:**

- 711 curriculum documents
- Each has unique `doc_id` for tracking
- `topic`, `difficulty` for filtering
- `content` is what gets embedded and retrieved

**How RAG uses it:**

```
Student: "How does accommodation work?"
         ↓
Search embeddings of all 711 documents
         ↓
Find 3 most similar
         ↓
Pass to LLM with question
         ↓
LLM generates answer grounded in curriculum
```

---

## 2️⃣ **Question Bank (What to Ask Students)**

**CSV File:** `question_bank.csv` (Already created ✅)

```csv
question_id,question_text,question_type,topic,subject,difficulty,related_doc_id,expected_answer_context
```

**Key Columns Explained:**

- `question_id` - Unique ID (Q1, Q2, Q3...)
- `question_text` - The actual question
- `question_type` - definition/explanation/application/comparison
- `difficulty` - easy/medium/hard (for adaptive selection)
- `related_doc_id` - Links to knowledge base (for scoring)
- `expected_answer_context` - What a good answer should contain

**What system does with it:**

```
1. Check student level (accuracy)
2. Select appropriate difficulty
3. Pick random question from that difficulty
4. Ask student
5. Use expected_answer_context to score
```

---

## 3️⃣ **Student Interactions (Tracking Every Exchange)**

**CSV File:** `student_interactions.csv` (Template created ✅)

```csv
interaction_id,student_id,timestamp,question_id,student_answer,correct,answer_quality,time_taken_seconds,hints_used,topic_covered,difficulty_level
```

**Key Columns:**

- `interaction_id` - Unique ID for this exchange
- `student_id` - Who answered (STU001, STU002...)
- `timestamp` - When they answered
- `question_id` - Which question from bank
- `student_answer` - Their actual response
- `correct` - yes/no (from RAG scoring)
- `answer_quality` - excellent/good/poor
- `time_taken_seconds` - How fast they answered
- `hints_used` - Did they need help?
- `topic_covered` - What topic was this about?
- `difficulty_level` - Was this easy/medium/hard for them?

**Why track all this:**

```
Use this data to:
- Analyze which topics they struggle with
- See if they're answering too fast (guessing)?
- Check if hints are helping
- Adjust difficulty in real-time
```

**Example analysis:**

```python
import pandas as pd

interactions = pd.read_csv('student_interactions.csv')

# Find struggling topics
struggling = interactions[interactions['correct'] == 'no'].groupby('topic_covered').size()
print("Student struggles with:", struggling.index[0])

# Find questions that are too hard
too_hard = interactions[interactions['time_taken_seconds'] > 300]
print(f"Student took too long on {len(too_hard)} questions")
```

---

## 4️⃣ **Student Performance (Aggregated Metrics)**

**CSV File:** `student_performance.csv` (Template created ✅)

```csv
student_id,topic,questions_attempted,questions_correct,accuracy_percent,average_time_seconds,mastery_level,last_attempted,readiness_for_next_topic
```

**Key Columns:**

- `student_id` - Which student
- `topic` - Which topic/subject
- `questions_attempted` - Total questions asked
- `questions_correct` - How many they got right
- `accuracy_percent` - Overall score (0-100%)
- `mastery_level` - beginner/intermediate/advanced
- `readiness_for_next_topic` - yes/no

**Calculated from interactions data:**

```
accuracy = (questions_correct / questions_attempted) * 100

if accuracy > 85%:
    mastery_level = "advanced"
    readiness = "yes"
elif accuracy > 70%:
    mastery_level = "intermediate"
    readiness = "yes"
else:
    mastery_level = "beginner"
    readiness = "no"
```

**How system uses it:**

```
1. Check performance["The Human Eye"]
2. See: 80% accuracy, "intermediate"
3. Ask MEDIUM difficulty next time
4. When accuracy > 85%, enable next topic
```

---

## 5️⃣ **Curriculum Paths (Learning Sequences)**

**CSV File:** `curriculum_paths.csv` (Already created ✅)

```csv
path_id,topic_name,description,order,prerequisite_topics,estimated_hours,target_difficulty,required_accuracy_percent
```

**Enforces learning order:**

```
PATH001: Understanding Light (order=1, prereq=NONE)
PATH002: The Human Eye (order=2, prereq=Understanding Light)
PATH003: Vision Defects (order=3, prereq=The Human Eye + Understanding Light)
PATH004: Advanced Optics (order=4, prereq=Vision Defects)

Student can't jump to PATH003 without mastering PATH002!
```

---

## 📊 Data Collection Flow

```
┌─ Student Answers Question ──────────┐
│                                     │
├─ RECORD in student_interactions    │
│  (interaction_id, student_id, etc) │
│                                     │
├─ SCORE the answer                  │
│  (use RAG + knowledge_base)         │
│                                     │
├─ UPDATE student_performance        │
│  (recalculate accuracy, mastery)   │
│                                     │
├─ CHECK curriculum_paths            │
│  (is student ready for next?)       │
│                                     │
└─ SELECT next question              │
   (from question_bank, based on perf)
```

---

## 🔄 Data Collection Workflow

### **Session 1: Student STU001**

```
Interaction 1:
- Question: "What is the human eye?"  (from question_bank)
- Answer: "It's an organ..."
- Score: ✅ CORRECT (95% match)
- Log in: student_interactions.csv
- Update: student_performance.csv
  * STU001, The Human Eye, 1 attempted, 1 correct, 100% accuracy

Interaction 2:
- Question: "How does accommodation work?"
- Answer: "The lens changes shape..."
- Score: ⚠️ PARTIAL (60% match)
- Log in: student_interactions.csv
- Update: student_performance.csv
  * STU001, The Human Eye, 2 attempted, 1 correct, 50% accuracy

Next interaction will:
- Check performance: 50% accuracy (beginner level)
- Select EASY difficulty question
- Ask something simpler
```

---

## 💾 Files to Collect/Generate

| File                       | Type    | Rows  | When         | Who Creates              |
| -------------------------- | ------- | ----- | ------------ | ------------------------ |
| `curriculum_chunks.json`   | Input   | 711   | Initially    | extract_curriculum.py    |
| `rag_knowledge_base.csv`   | Core    | 711   | Initialize   | create_rag_tutor_data.py |
| `question_bank.csv`        | Core    | 1,983 | Initialize   | create_rag_tutor_data.py |
| `curriculum_paths.csv`     | Core    | 4     | Initialize   | create_rag_tutor_data.py |
| `student_interactions.csv` | Growing | ∞     | Per Q&A      | rag_tutor_system         |
| `student_performance.csv`  | Growing | ∞     | After each Q | rag_tutor_system         |

---

## 🎯 For Proper ML Training - Add These

If you want to train **custom models** (not just use RAG):

### **For Classification (subject categorization):**

```csv
sample_id,text,label,split
SAMPLE_001,The human eye...,biology,train
SAMPLE_002,Light refracts...,physics,train
```

### **For Semantic Search (finding similar docs):**

```csv
pair_id,query,document,relevance_score,label
PAIR_001,How eye works?,The human eye is...,0.85,similar
PAIR_002,How eye works?,Myopia is...,0.15,dissimilar
```

### **For Entity Recognition (extracting concepts):**

```csv
sample_id,text,entity,entity_type,start,end,label
NER_001,The human eye...,eye,ANATOMY,4,7,B-ANATOMY
NER_002,Light refracts...,refraction,CONCEPT,0,10,B-CONCEPT
```

---

## 📝 What to Tell Your Teacher

**Show these 6 datasets:**

1. **rag_knowledge_base.csv** - 711 documents with IDs and difficulty
2. **question_bank.csv** - 1,983 questions with types and links
3. **student_interactions.csv** - Template for tracking every Q&A
4. **student_performance.csv** - Performance metrics per student/topic
5. **curriculum_paths.csv** - Learning sequences with prerequisites
6. **dataset_ranking.csv** - Relevance scores for RAG training

**Explain:**

- "Each has unique IDs for tracking"
- "Knowledge base gets embedded for retrieval"
- "Questions adapt to student level"
- "Every interaction is logged for analysis"
- "System automatically adjusts curriculum"

---

## ✅ Checklist

- [x] Create rag_knowledge_base.csv (711 docs)
- [x] Create question_bank.csv (1,983 questions)
- [x] Create curriculum_paths.csv (4 paths)
- [x] Create student_interactions template
- [x] Create student_performance template
- [x] Create 6 ML training datasets
- [ ] **Next: Implement data collection logic**
- [ ] **Next: Train on this data**
- [ ] **Next: Deploy tutor system**

---

## 🚀 Implementation Code Example

```python
import pandas as pd
from datetime import datetime

def collect_interaction(student_id, question_id, student_answer, correct, quality):
    """Add new interaction to CSV"""

    interaction = {
        'interaction_id': f"{student_id}_INT_{len(df_interactions)}",
        'student_id': student_id,
        'timestamp': datetime.now().isoformat(),
        'question_id': question_id,
        'student_answer': student_answer,
        'correct': correct,
        'answer_quality': quality,
        'time_taken_seconds': 120,
        'hints_used': 0,
        'topic_covered': 'The Human Eye',
        'difficulty_level': 'medium'
    }

    # Append to CSV
    df_interactions = pd.concat([df_interactions, pd.DataFrame([interaction])],
                                ignore_index=True)
    df_interactions.to_csv('student_interactions.csv', index=False)

    # Update performance
    update_performance(student_id, correct)

def update_performance(student_id, correct):
    """Update student performance metrics"""

    df_perf = pd.read_csv('student_performance.csv')

    student = df_perf[df_perf['student_id'] == student_id].iloc[0]

    new_attempts = student['questions_attempted'] + 1
    new_correct = student['questions_correct'] + (1 if correct == 'yes' else 0)
    new_accuracy = (new_correct / new_attempts) * 100

    # Update mastery
    if new_accuracy > 85:
        mastery = 'advanced'
        ready = 'yes'
    elif new_accuracy > 70:
        mastery = 'intermediate'
        ready = 'yes'
    else:
        mastery = 'beginner'
        ready = 'no'

    # Save
    df_perf.loc[df_perf['student_id'] == student_id, 'accuracy_percent'] = new_accuracy
    df_perf.loc[df_perf['student_id'] == student_id, 'mastery_level'] = mastery
    df_perf.to_csv('student_performance.csv', index=False)
```

This is production-ready data architecture! 🎉
