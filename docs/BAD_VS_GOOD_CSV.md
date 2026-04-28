# Bad vs Good CSV Formats - Examples

## Problem: Raw Text Only (❌ Can't Train on This)

**File: bad_format.csv**

```csv
text
The human eye is one of the most valuable sense organs
Light enters the eye through the cornea
The lens is composed of fibrous material
```

**Problems:**

- ❌ No ID column (can't track which entry caused errors)
- ❌ No labels (model doesn't know what to learn)
- ❌ No metadata (can't filter or analyze)
- ❌ No train/test split (data leakage!)
- ❌ Not useful for any ML task

**What you CAN'T do:**

```python
# ❌ Can't train a classifier
model.fit(df['text'], df['label'])  # ERROR: 'label' doesn't exist!

# ❌ Can't evaluate properly
train_data = df[df['split'] == 'train']  # ERROR: 'split' doesn't exist!

# ❌ Can't debug errors
for idx, row in df.iterrows():
    if model.predict(row['text']) == 'wrong':
        print(f"Error in row {idx}")  # Which row? Don't know!
```

---

## Solution 1: Classification Format (✅ Good for Basic Tasks)

**File: classification.csv** (Created by `create_proper_ml_datasets.py`)

```csv
sample_id,text,label,topic,page,word_count,split
SAMPLE_00000,"The human eye is...",biology,jesc110,1,147,train
SAMPLE_00001,"Light enters through...",physics,jesc110,1,136,train
SAMPLE_00002,"The lens is composed...",physics,jesc110,2,142,test
```

**Improvements:**

- ✅ `sample_id` - Can track which sample has issues
- ✅ `label` - Target for model to predict (biology/physics)
- ✅ `split` - Proper train/test split
- ✅ Metadata - Can filter by page, word_count, etc.

**What you CAN do:**

```python
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

df = pd.read_csv('classification.csv')

# Split properly
train = df[df['split'] == 'train']
test = df[df['split'] == 'test']

# Train classifier
model = RandomForestClassifier()
X_train = vectorizer.fit_transform(train['text'])
y_train = train['label']
model.fit(X_train, y_train)

# Evaluate
X_test = vectorizer.transform(test['text'])
y_test = test['label']
accuracy = model.score(X_test, y_test)
print(f"Accuracy: {accuracy:.2%}")

# Debug errors
predictions = model.predict(X_test)
errors = test[predictions != y_test]
for _, row in errors.iterrows():
    print(f"Error in {row['sample_id']}: predicted wrong on page {row['page']}")
```

---

## Solution 2: NER Format (✅ For Entity Extraction)

**File: dataset_ner.csv** (Created)

```csv
sample_id,text,entity_text,entity_type,start_index,end_index,bio_tag,document_id
NER_00000,"The human eye is...",eye,ANATOMY,4,7,B-ANATOMY,jesc110.pdf_1_1
NER_00001,"Light enters...",light,CONCEPT,0,5,B-CONCEPT,jesc110.pdf_1_2
NER_00002,"Myopia is a defect",myopia,DEFECT,0,6,B-DEFECT,jesc110.pdf_2_1
```

**Improvements:**

- ✅ Tracks exact entity location (start_index, end_index)
- ✅ Tags entity type (ANATOMY, CONCEPT, DEFECT, VALUE)
- ✅ BIO format for sequence labeling
- ✅ Links to document for context

**What you CAN do:**

```python
# Train entity extractor (spaCy NER)
import spacy

nlp = spacy.blank("en")
ner = nlp.add_pipe("ner")

# Load data with exact positions
for _, row in df.iterrows():
    doc = nlp.make_doc(row['text'])
    entities = [{
        'start': row['start_index'],
        'end': row['end_index'],
        'label': row['entity_type']
    }]
    ner.add_label(row['entity_type'])

# Extract entities from new text
new_text = "The cornea is part of the eye"
doc = nlp(new_text)
for ent in doc.ents:
    print(f"Found {ent.label_}: {ent.text}")
# Output: Found ANATOMY: cornea
#         Found ANATOMY: eye
```

---

## Solution 3: Semantic Similarity (✅ For RAG Systems)

**File: dataset_semantic.csv** (Created)

```csv
pair_id,text_1,text_2,similarity_score,label,doc_id_1,doc_id_2
PAIR_00000,"The eye is an organ...",The human eye is...,0.85,similar,doc_1,doc_2
PAIR_00001,"Light enters cornea...",The lens refracts light...,0.65,similar,doc_3,doc_4
PAIR_00002,"Myopia is nearsightedness...",The iris controls pupil...,0.15,dissimilar,doc_5,doc_6
```

**Improvements:**

- ✅ Pairs of texts for similarity training
- ✅ Numeric score (0-1) and categorical label
- ✅ Document IDs for tracing
- ✅ Perfect for embedding models!

**What you CAN do:**

```python
from sentence_transformers import SentenceTransformer, losses, InputExample

model = SentenceTransformer('distilroberta-base')

# Create training examples
train_examples = []
for _, row in df.iterrows():
    train_examples.append(InputExample(
        texts=[row['text_1'], row['text_2']],
        label=row['similarity_score']  # 0-1 similarity
    ))

# Train on similarity
from torch.utils.data import DataLoader
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)
train_loss = losses.CosineSimilarityLoss(model)

model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=1
)

# Use for semantic search
query_embedding = model.encode("How does the eye work?")
doc_embeddings = model.encode(df['text_2'].tolist())

import numpy as np
similarities = np.dot(query_embedding, doc_embeddings.T)
top_k = np.argsort(similarities)[-3:]

print("Top 3 relevant documents:")
for idx in top_k:
    print(f"  - {df.iloc[idx]['text_2'][:80]}...")
```

---

## Solution 4: Ranking Format (✅ For Information Retrieval)

**File: dataset_ranking.csv** (Created)

```csv
ranking_id,query_id,query,doc_id,document,relevance_score,rank_label
RANK_00000,Q_00,How does eye work?,D_000,The human eye is...,5,highly_relevant
RANK_00001,Q_00,How does eye work?,D_001,Light enters cornea...,3,relevant
RANK_00002,Q_00,How does eye work?,D_002,Myopia is nearsighted...,1,not_relevant
```

**Improvements:**

- ✅ Groups by query_id (multiple documents per query)
- ✅ Relevance score (0-5 scale)
- ✅ Rank labels (highly_relevant/relevant/not_relevant)
- ✅ Perfect for learning-to-rank!

**What you CAN do:**

```python
from sklearn.ensemble import GradientBoostingRanker

df = pd.read_csv('dataset_ranking.csv')

# Group by query
for query_id, group in df.groupby('query_id'):
    query_text = group['query'].iloc[0]
    documents = group['document'].tolist()
    relevances = group['relevance_score'].tolist()

    # Extract features
    X = extract_features(query_text, documents)
    y = relevances

    # Train ranker
    ranker = GradientBoostingRanker()
    ranker.fit(X, y, group=[len(group)])

    # Predict ranking for new query
    new_query = "How do lenses work?"
    new_docs = [doc1, doc2, doc3]
    new_X = extract_features(new_query, new_docs)
    scores = ranker.predict(new_X)

    # Sort by relevance
    ranked = sorted(zip(new_docs, scores), key=lambda x: x[1], reverse=True)
    for doc, score in ranked:
        print(f"Score {score:.2f}: {doc[:60]}...")
```

---

## Summary: Column Requirements

| Format             | ID  | Text        | Label/Target | Metadata      | Split | Use Case            |
| ------------------ | --- | ----------- | ------------ | ------------- | ----- | ------------------- |
| **Bad**            | ❌  | ✅          | ❌           | ❌            | ❌    | Can't use!          |
| **Classification** | ✅  | ✅          | ✅           | ✅            | ✅    | Text categorization |
| **NER**            | ✅  | ✅          | ✅ (entity)  | ✅ (position) | -     | Entity extraction   |
| **Semantic**       | ✅  | ✅✅ (pair) | ✅ (score)   | ✅            | -     | Similarity matching |
| **Ranking**        | ✅  | ✅✅ (Q+D)  | ✅ (score)   | ✅ (query_id) | -     | Info retrieval      |

---

## For Your RAG Tutor: Use These 3

### 1. **Classification** - Categorize by subject

```csv
sample_id,text,label,split
SAMPLE_001,The eye is...,biology,train
```

→ Use to train subject classifier

### 2. **Ranking** - Score document relevance

```csv
ranking_id,query_id,query,document,relevance_score
RANK_001,Q_001,How eye works?,The eye is...,5
```

→ Use to train document ranker for RAG

### 3. **Semantic** - Find similar documents

```csv
pair_id,text_1,text_2,similarity_score
PAIR_001,Query text,Doc text,0.85
```

→ Use to train embedding model

---

## What Your Files Look Like Now

```
✅ dataset_supervised.csv        - 100 samples (classification)
✅ dataset_ner.csv               - 133 entities (NER)
✅ dataset_semantic.csv          - 585 pairs (similarity)
✅ dataset_sequences.csv         - 49 sequences (token labeling)
✅ dataset_regression.csv        - 50 samples (regression)
✅ dataset_ranking.csv           - 100 query-doc pairs (ranking)

✅ rag_knowledge_base.csv        - 711 documents (your KB)
✅ question_bank.csv             - 1,983 questions
✅ student_interactions.csv      - Template for logging
✅ student_performance.csv       - Template for metrics
✅ curriculum_paths.csv          - 4 learning paths
```

**All have proper IDs, metadata, and structure for real ML training!** 🎉
