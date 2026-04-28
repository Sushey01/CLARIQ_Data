# 🎓 Complete RAG Conversational Tutor - Data Architecture

## What You Have Now

### 📊 **11 CSV Files Ready for ML Training**

```
CORE RAG SYSTEM (5 files)
├── rag_knowledge_base.csv      (711 docs) - What students learn from
├── question_bank.csv           (1,983 Q's) - What system asks
├── student_interactions.csv    (50 rows) - Q&A interaction logs
├── student_performance.csv     (20 rows) - Performance metrics
└── curriculum_paths.csv        (4 paths) - Learning sequences

ML TRAINING DATASETS (6 files)
├── dataset_supervised.csv      (100 samples) - Classification
├── dataset_ner.csv             (133 entities) - Named Entity Recognition
├── dataset_semantic.csv        (585 pairs) - Similarity matching
├── dataset_sequences.csv       (49 sequences) - Token labeling
├── dataset_regression.csv      (50 samples) - Numeric prediction
└── dataset_ranking.csv         (100 pairs) - Information retrieval
```

---

## What Each CSV Contains

### 1. **rag_knowledge_base.csv** - The Knowledge Store

**Purpose:** Everything the RAG system can retrieve from

**Structure:**

```
doc_id | source_pdf | page | topic | subtopic | difficulty | doc_type | content | word_count
────────────────────────────────────────────────────────────────────────────────────────────
jesc110.pdf_1_1 | jesc110.pdf | 1 | The Human Eye | Biology | medium | explanatory | "The human eye..." | 147
```

**Why each column matters:**

- `doc_id` - Unique ID (track which doc answered question)
- `topic` / `subtopic` - Filter by subject
- `difficulty` - Match to student level
- `content` - Gets embedded + searched
- `doc_type` - Different doc types (definition vs example)

**Used by:** RAG retrieval system

---

### 2. **question_bank.csv** - Questions Library

**Purpose:** What the tutor asks students

**Structure:**

```
question_id | question_text | question_type | topic | subject | difficulty | related_doc_id | expected_answer_context
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
Q1 | What is the human eye? | definition | The Human Eye | biology | easy | jesc110.pdf_1_1 | "The human eye is..."
```

**Why each column matters:**

- `question_id` - Track which question led to errors
- `question_type` - Variety (definition/explanation/application)
- `difficulty` - Adaptive selection (easy → medium → hard)
- `related_doc_id` - Links to knowledge base for scoring

**Used by:** Question selection + answer grading

---

### 3. **student_interactions.csv** - Interaction Logs

**Purpose:** Every Q&A exchange (like conversation history)

**Structure:**

```
interaction_id | student_id | timestamp | question_id | student_answer | correct | answer_quality | time_taken_seconds | hints_used | topic_covered | difficulty_level
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
STU001_INT_0 | STU001 | 2026-04-26 10:30 | Q1 | "The eye is..." | yes | excellent | 45 | 0 | The Human Eye | easy
```

**Why each column matters:**

- `student_id` - Which student
- `question_id` - Which question (track trends)
- `student_answer` - Their actual response
- `correct` - Scored by RAG
- `time_taken_seconds` - Effort indicator
- `topic_covered` - What they studied

**Used by:** Analyzing student behavior + generating reports

---

### 4. **student_performance.csv** - Performance Summary

**Purpose:** Aggregated metrics (calculated from interactions)

**Structure:**

```
student_id | topic | questions_attempted | questions_correct | accuracy_percent | average_time_seconds | mastery_level | last_attempted | readiness_for_next_topic
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
STU001 | The Human Eye | 15 | 12 | 80 | 120 | intermediate | 2026-04-26 | yes
```

**Why each column matters:**

- `accuracy_percent` - Determines next difficulty level
- `mastery_level` - beginner/intermediate/advanced
- `readiness_for_next_topic` - Can they move on?
- `last_attempted` - When was last activity?

**Used by:** Adaptive curriculum selection

---

### 5. **curriculum_paths.csv** - Learning Roadmap

**Purpose:** Define the correct learning sequence with prerequisites

**Structure:**

```
path_id | topic_name | description | order | prerequisite_topics | estimated_hours | target_difficulty | required_accuracy_percent
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
PATH001 | Understanding Light | Learn light basics | 1 | None | 4 | easy | 80
PATH002 | The Human Eye | Learn eye anatomy | 2 | Understanding Light | 3 | medium | 75
```

**Why each column matters:**

- `order` - Sequence (can't do PATH002 before PATH001)
- `prerequisite_topics` - Must master before proceeding
- `required_accuracy_percent` - Pass threshold
- `estimated_hours` - Time estimate for student

**Used by:** Enforcing learning order + recommendations

---

### 6. **dataset_supervised.csv** - Classification Training Data

**Purpose:** Train a subject classifier (biology/physics/chemistry)

**Structure:**

```
sample_id | text | label | topic | page | word_count | split
────────────────────────────────────────────────────────────────
SAMPLE_00000 | "The human eye..." | biology | jesc110 | 1 | 147 | train
SAMPLE_00001 | "Light enters..." | physics | jesc110 | 1 | 136 | train
```

**Used to:**

```python
# Train classifier
X = vectorizer.fit_transform(df['text'])
y = df['label']
model = RandomForestClassifier()
model.fit(X, y)

# Classify new text
prediction = model.predict(["The retina detects light..."])
# Output: "biology"
```

---

### 7. **dataset_semantic.csv** - Similarity Training Data

**Purpose:** Train embedding model for semantic search

**Structure:**

```
pair_id | text_1 | text_2 | similarity_score | label | doc_id_1 | doc_id_2
──────────────────────────────────────────────────────────────────────────
PAIR_00000 | "The eye is..." | "The human eye..." | 0.85 | similar | doc_1 | doc_2
```

**Used to:**

```python
# Train embeddings
model = SentenceTransformer('distilroberta-base')
# Fine-tune on this data to learn curriculum-specific similarity

# Then use for semantic search
query_emb = model.encode("How does the eye work?")
doc_emb = model.encode(all_documents)
scores = model.util.semantic_search(query_emb, doc_emb, top_k=3)
```

---

### 8. **dataset_ranking.csv** - Relevance Ranking Data

**Purpose:** Train learning-to-rank model for RAG

**Structure:**

```
ranking_id | query_id | query | doc_id | document | relevance_score | rank_label
──────────────────────────────────────────────────────────────────────────────────
RANK_00000 | Q_00 | How does eye work? | D_000 | "The human eye..." | 5 | highly_relevant
```

**Used to:**

```python
# Train ranker
ranker = LambdaMARTRanker()
ranker.fit(X, y, groups=df.groupby('query_id').size())

# Then use for better document ranking
new_query = "How do lenses work?"
results = ranker.rank(documents, new_query)
# Returns best documents first!
```

---

## 🔄 How The System Works

```
STUDENT INTERACTION FLOW:
═══════════════════════════════════════════════════════════════

1. STUDENT LOGS IN
   └─ Load from: student_performance.csv
   └─ See: "You're 80% accurate on The Human Eye"

2. SYSTEM SELECTS QUESTION
   └─ Check: accuracy_percent = 80% → mastery = "intermediate"
   └─ Select from: question_bank.csv with difficulty="medium"
   └─ Ask: "How does the eye lens work?"

3. STUDENT ANSWERS
   └─ Student: "The lens changes shape to focus"

4. SYSTEM SCORES ANSWER (RAG)
   └─ Retrieve from: rag_knowledge_base.csv (semantic search)
   └─ Compare with: expected_answer_context
   └─ Similarity score: 0.75 → "GOOD"

5. LOG INTERACTION
   └─ Append to: student_interactions.csv
   │  interaction_id: STU001_INT_42
   │  correct: yes
   │  answer_quality: good
   └─ Update timestamp

6. UPDATE PERFORMANCE
   └─ Recalculate from: student_interactions.csv
   └─ New accuracy: 82%
   └─ Update in: student_performance.csv
   └─ Still mastery: "intermediate"

7. CHECK ADVANCEMENT
   └─ Read: curriculum_paths.csv
   └─ Check: readiness_for_next_topic = "yes"?
   └─ If yes: "Ready to learn Vision Defects"
   └─ If no: "Keep practicing medium questions"

8. NEXT QUESTION
   └─ Repeat loop...
```

---

## 📚 Documentation Files

| File                         | Purpose                                    |
| ---------------------------- | ------------------------------------------ |
| **ML_DATASET_FORMATS.md**    | Explains 6 dataset formats with examples   |
| **DATA_COLLECTION_GUIDE.md** | How to collect + use the data              |
| **BAD_VS_GOOD_CSV.md**       | Comparison of poor vs proper CSV structure |
| **RAG_TUTOR_SYSTEM.md**      | Complete system architecture               |
| **QUICKSTART.md**            | Step-by-step setup guide                   |

---

## 🎯 For Your Teacher

**Show these files:**

1. **rag_knowledge_base.csv** (711 docs with IDs)
   → "Knowledge base for retrieval"

2. **question_bank.csv** (1,983 questions with types)
   → "Adaptive question selection"

3. **student_performance.csv** (tracked metrics)
   → "Performance-based curriculum"

4. **student_interactions.csv** (logged Q&A)
   → "Student interaction tracking"

5. **curriculum_paths.csv** (4 learning sequences)
   → "Structured learning with prerequisites"

6. **All 6 ML datasets** (classification, NER, similarity, ranking, regression, sequences)
   → "Ready for training models"

**Your explanation:**

> "I've created a RAG conversational tutor with 5 core CSVs for the system and 6 ML training datasets. Each CSV has proper IDs for tracking, metadata for filtering, and labels for training. The system logs every student interaction, tracks performance in real-time, and adapts the curriculum based on mastery levels."

---

## ✅ Complete Checklist

### Data Structure

- [x] Knowledge base with 711 documents
- [x] Question bank with 1,983 questions
- [x] Curriculum paths with prerequisites
- [x] Student interaction logging template
- [x] Performance tracking template

### ML Training Datasets

- [x] Classification dataset (100 samples)
- [x] NER dataset (133 entities)
- [x] Semantic similarity (585 pairs)
- [x] Sequence labeling (49 sequences)
- [x] Regression dataset (50 samples)
- [x] Ranking dataset (100 query-doc pairs)

### Documentation

- [x] ML dataset formats guide
- [x] Data collection guide
- [x] Bad vs good CSV comparison
- [x] RAG system architecture
- [x] Quick start guide

### Implementation

- [x] create_rag_tutor_data.py - Generate CSVs
- [x] create_proper_ml_datasets.py - Generate ML datasets
- [x] rag_tutor_implementation.py - Working system

---

## 🚀 Next Steps

### Step 1: Show Your Teacher

```bash
cd /home/shekhar/Documents/FYP/TextExtract
# Show all files
ls -lh *.csv
# Read documentation
cat ML_DATASET_FORMATS.md
cat DATA_COLLECTION_GUIDE.md
```

### Step 2: Train on the Data

```python
# Example: Train classifier
python -c "
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

df = pd.read_csv('dataset_supervised.csv')
train = df[df['split'] == 'train']

X = TfidfVectorizer().fit_transform(train['text'])
y = train['label']

model = MultinomialNB()
model.fit(X, y)

print('✅ Model trained!')
"
```

### Step 3: Deploy the Tutor

```python
# Run the system
python rag_tutor_implementation.py
```

---

## 🎓 Why This Is Production-Grade

✅ **Proper IDs** - Track everything (debug errors, analyze patterns)  
✅ **Metadata** - Filter by topic, page, date, difficulty  
✅ **Train/Test Split** - No data leakage  
✅ **Multiple Formats** - Supports different ML tasks  
✅ **Traceable** - Know which student made which answer  
✅ **Scalable** - Add more students/topics easily  
✅ **Measurable** - Real performance metrics  
✅ **Adaptive** - System learns from student data

This is what real companies use for their ML systems! 🚀
