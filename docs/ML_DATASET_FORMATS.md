# Proper ML Training Data Structures

## ❌ What NOT to Do (Bad Format)

```csv
text
"The human eye is..."
"The eye lens..."
```

❌ **Problem:** Just text, no labels, no IDs, can't track anything

---

## ✅ Standard ML Dataset Formats

### 1️⃣ **CLASSIFICATION Dataset**

**Use for:** Text classification, Topic modeling, Subject identification

```csv
sample_id,text,label,topic,page,split
SAMPLE_00001,The human eye is one of...,biology,jesc110,1,train
SAMPLE_00002,Light enters the eye...,physics,jesc110,1,train
SAMPLE_00003,The lens is composed of...,physics,jesc110,2,test
```

**Key Columns:**

- `sample_id` - Unique identifier (for tracking)
- `text` - Input feature (what model learns from)
- `label` - Target output (what model predicts)
- `topic` - Metadata (source document)
- `page` - Metadata (where it came from)
- `split` - train/test/val (for proper evaluation)

**How to use:**

```python
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

df = pd.read_csv('dataset_supervised.csv')
train = df[df['split'] == 'train']

X = train['text']
y = train['label']

model = RandomForestClassifier()
model.fit(X, y)
```

---

### 2️⃣ **NER (Named Entity Recognition) Dataset**

**Use for:** Extracting concepts, entities, key terms

```csv
sample_id,text,entity_text,entity_type,start_index,end_index,bio_tag,document_id
NER_00001,The human eye is...,eye,ANATOMY,4,7,B-ANATOMY,jesc110.pdf_1_1
NER_00002,Light enters the eye...,light,CONCEPT,0,5,B-CONCEPT,jesc110.pdf_1_2
NER_00003,Myopia is a defect...,myopia,DEFECT,0,6,B-DEFECT,jesc110.pdf_2_1
```

**Key Columns:**

- `sample_id` - Unique ID
- `text` - Full sentence/document
- `entity_text` - The entity to extract
- `entity_type` - What kind of entity (ANATOMY, CONCEPT, DEFECT, etc.)
- `start_index`, `end_index` - Position in text (for model precision)
- `bio_tag` - BIO format (B=beginning, I=inside, O=outside)
- `document_id` - Source document

**How to use:**

```python
# Train NER model (spaCy, transformers)
from spacy.training import Example

examples = []
for idx, row in df.iterrows():
    doc = nlp.make_doc(row['text'])
    ents = [
        {
            'start': row['start_index'],
            'end': row['end_index'],
            'label': row['entity_type']
        }
    ]
    examples.append(Example.from_dict(doc, {'entities': ents}))
```

---

### 3️⃣ **SEMANTIC SIMILARITY Dataset**

**Use for:** Training embeddings, Similarity models, Retrieval systems

```csv
pair_id,text_1,text_2,similarity_score,label,doc_id_1,doc_id_2
PAIR_00001,The eye is an organ...,The human eye is...,0.85,similar,doc_1,doc_2
PAIR_00002,Light enters through cornea...,The retina detects light...,0.65,similar,doc_3,doc_4
PAIR_00003,Myopia is short-sightedness...,The iris controls pupil size...,0.15,dissimilar,doc_5,doc_6
```

**Key Columns:**

- `pair_id` - Unique pair identifier
- `text_1`, `text_2` - Two texts to compare
- `similarity_score` - Numeric score (0-1)
- `label` - Categorical (similar/dissimilar) or numeric
- `doc_id_1`, `doc_id_2` - Track source documents

**How to use:**

```python
# Train with siamese networks or triplet loss
from sentence_transformers import SentenceTransformer, losses

model = SentenceTransformer('distilroberta-base')
train_examples = [
    InputExample(texts=[row['text_1'], row['text_2']],
                 label=row['similarity_score'])
    for _, row in df.iterrows()
]
```

---

### 4️⃣ **SEQUENCE LABELING Dataset**

**Use for:** POS tagging, Chunking, Token classification

```csv
sequence_id,sentence,tokens,tags,num_tokens,source_doc
SEQ_0001_00,The eye is complex...,The | eye | is | complex,DET | NOUN | VERB | ADJ,4,doc_1
SEQ_0002_01,Light enters through cornea...,Light | enters | through | cornea,NOUN | VERB | PREP | NOUN,4,doc_2
```

**Key Columns:**

- `sequence_id` - Unique sequence ID
- `sentence` - Full sentence
- `tokens` - Individual tokens (separated by |)
- `tags` - Tag for each token (DET, NOUN, VERB, etc.)
- `num_tokens` - Number of tokens (for validation)
- `source_doc` - Track source

**How to use:**

```python
# Token-level classification
for _, row in df.iterrows():
    tokens = row['tokens'].split(' | ')
    tags = row['tags'].split(' | ')

    # Train token classifier
    for token, tag in zip(tokens, tags):
        model.train_on_example(token, tag)
```

---

### 5️⃣ **REGRESSION Dataset**

**Use for:** Predicting continuous values (scores, ratings, importance)

```csv
content_id,text,word_count,importance_score,page,source
CONTENT_00001,The human eye is...,147,8,1,jesc110.pdf
CONTENT_00002,Light enters through...,136,7,1,jesc110.pdf
CONTENT_00003,The lens becomes thicker...,137,9,2,jesc110.pdf
```

**Key Columns:**

- `content_id` - Unique ID
- `text` - Input text
- `word_count` - Feature (numeric)
- `importance_score` - Target (numeric value to predict)
- `page`, `source` - Metadata

**How to use:**

```python
# Predict continuous score
from sklearn.linear_model import LinearRegression

X = vectorizer.transform(df['text'])
y = df['importance_score']

model = LinearRegression()
model.fit(X, y)

# Predict importance of new content
prediction = model.predict(X_new)
```

---

### 6️⃣ **RANKING/RECOMMENDATION Dataset**

**Use for:** Learning to rank, Recommendation systems, Relevance scoring

```csv
ranking_id,query_id,query,doc_id,document,relevance_score,rank_label
RANK_00001,Q_01,How does eye work?,D_001,The eye is an organ...,5,highly_relevant
RANK_00002,Q_01,How does eye work?,D_002,Light enters cornea...,3,relevant
RANK_00003,Q_01,How does eye work?,D_003,Myopia is nearsighted...,1,not_relevant
```

**Key Columns:**

- `ranking_id` - Unique pair ID
- `query_id` - Query identifier (group by)
- `query` - The query/question
- `doc_id` - Document identifier
- `document` - Document text
- `relevance_score` - Numeric score (0-5)
- `rank_label` - Categorical label

**How to use:**

```python
# Train ranking model
from sklearn.preprocessing import LabelEncoder

X = df[['query', 'document']]
y = df['relevance_score']

# LambdaMART or other ranking loss
model.fit(X, y, group_by=df['query_id'])
```

---

## 📊 Comparison Table

| Format             | Best For             | Has ID?        | Has Label?          | Columns |
| ------------------ | -------------------- | -------------- | ------------------- | ------- |
| **Classification** | Text categorization  | ✅ sample_id   | ✅ label            | 6-8     |
| **NER**            | Entity extraction    | ✅ sample_id   | ✅ entity_type      | 8-10    |
| **Semantic**       | Similarity matching  | ✅ pair_id     | ✅ similarity_score | 8-10    |
| **Sequence**       | Token classification | ✅ sequence_id | ✅ tags             | 6-7     |
| **Regression**     | Numeric prediction   | ✅ content_id  | ✅ numeric_score    | 6-8     |
| **Ranking**        | Relevance ranking    | ✅ ranking_id  | ✅ relevance_score  | 8-10    |

---

## 🎯 Key Principles

### 1. **Always Include ID Columns**

```csv
❌ Bad:     text,label
✅ Good:    sample_id,text,label
```

Why? Helps track which samples produced errors or performed well

### 2. **Metadata is Important**

```csv
✅ sample_id,text,label,source,page,split
```

Why? Allows filtering (e.g., "show errors from page 2") and analysis

### 3. **Include Train/Test Split**

```csv
✅ sample_id,text,label,split
   SAMPLE_001,text here,physics,train
   SAMPLE_002,text here,biology,test
```

Why? Prevents data leakage and proper evaluation

### 4. **For Pairs/Ranking Include Both IDs**

```csv
✅ ranking_id,query_id,doc_id,query,document,relevance
```

Why? Allows grouping by query and analyzing per-query performance

### 5. **Numeric Scores > Categories**

```csv
❌ Bad:     similarity_label: "similar" / "dissimilar"
✅ Good:    similarity_score: 0.85
```

Why? More information for models, can convert back to categories

---

## 💾 Which Format for Your RAG System?

**For your conversational tutor, use ALL THREE:**

1. **Classification** - Categorize by subject (biology/physics)

   ```csv
   sample_id, text, label (subject), split
   ```

2. **Semantic** - Find similar documents for RAG

   ```csv
   pair_id, query, document, relevance_score
   ```

3. **Ranking** - Score documents by relevance to queries
   ```csv
   ranking_id, query_id, doc_id, query, document, relevance_score
   ```

---

## 🚀 Generate These Now

```bash
python create_proper_ml_datasets.py
```

Creates:

- `dataset_supervised.csv` (Classification)
- `dataset_ner.csv` (Entity Recognition)
- `dataset_semantic.csv` (Similarity)
- `dataset_sequences.csv` (Sequence Labeling)
- `dataset_regression.csv` (Regression)
- `dataset_ranking.csv` (Ranking)

Each has proper IDs, metadata, and labels for real ML training!
