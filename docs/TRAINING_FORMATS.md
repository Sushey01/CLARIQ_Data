# Proper ML Training Data Formats

## ❌ What NOT to Do (Your Original Issue)

```csv
chunk_id,source_pdf,page,word_count,content
jesc110.pdf_1_1,jesc110.pdf,1,147,"The human eye is..."
```

❌ **Problem:** Just raw text with metadata - can't train a model on this alone!
❌ **No targets/labels** - models need something to learn from
❌ **No task definition** - what should the model actually do?

---

## ✅ Option 1: Question-Answering Dataset

**File:** `curriculum_qna.csv`

**Format:**

```csv
question,answer,source_pdf,page,chunk_id
"What is the human eye?","The human eye is one of the most valuable...",jesc110.pdf,1,jesc110.pdf_1_1
"Explain the eye","The human eye is one of the most valuable...",jesc110.pdf,1,jesc110.pdf_1_1
"How does the human eye work?","The human eye is one of the most valuable...",jesc110.pdf,1,jesc110.pdf_1_1
```

**What You Can Train:**

- Question-Answering models (like ChatGPT)
- Semantic search engines
- Retrieval systems

**What You Gain:**
✅ Model learns to match questions to relevant answers
✅ Can answer student questions automatically
✅ Build a chatbot for curriculum help
✅ Better than keyword search

**Example Usage:**

```python
import pandas as pd
from transformers import pipeline

df = pd.read_csv('curriculum_qna.csv')

# Train on this data
qa_pipeline = pipeline("question-answering", model="bert-base-uncased")

for _, row in df.iterrows():
    question = row['question']
    context = row['answer']
    answer = qa_pipeline(question=question, context=context)
    print(f"Q: {question} → A: {answer['answer']}")
```

---

## ✅ Option 2: Classification Dataset

**File:** `curriculum_classification.csv`

**Format:**

```csv
text,label,source_pdf,page
"The human eye is one of the most valuable...",biology,jesc110.pdf,1
"Light enters the eye through a thin membrane...",physics,jesc110.pdf,1
"The iris is a muscular diaphragm...",biology,jesc110.pdf,2
```

**What You Can Train:**

- Text classification models
- Subject/topic categorization
- Automatic curriculum organization

**What You Gain:**
✅ Automatically categorize educational content
✅ Organize curriculum by subject
✅ Recommend relevant sections
✅ Content tagging

**Example Usage:**

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import pandas as pd

df = pd.read_csv('curriculum_classification.csv')

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(df['text'])
y = df['label']

model = MultinomialNB()
model.fit(X, y)

# Predict on new text
new_text = "The retina detects light"
X_new = vectorizer.transform([new_text])
prediction = model.predict(X_new)
print(f"Category: {prediction[0]}")  # Output: "biology"
```

---

## ✅ Option 3: Semantic Similarity/Retrieval

**File:** `curriculum_similarity.csv`

**Format:**

```csv
query,positive,negative,query_id,positive_id,negative_id
"The human eye is valuable","The eye is significant",some other random text,jesc110.pdf_1_1,jesc110.pdf_1_2,jesc110.pdf_3_1
```

**What You Can Train:**

- Fine-tune embedding models (sentence-transformers)
- Semantic search engines
- Similarity matching

**What You Gain:**
✅ Semantic understanding of text similarity
✅ Find related curriculum content
✅ Better than keyword matching
✅ Build intelligent search

**Example Usage:**

```python
from sentence_transformers import SentenceTransformer, losses, models
from torch.utils.data import DataLoader
import pandas as pd

model = SentenceTransformer('all-MiniLM-L6-v2')

df = pd.read_csv('curriculum_similarity.csv')

# Find similar content
query = "What is the function of the eye?"
corpus = df['positive'].tolist()

embeddings = model.encode(corpus)
query_embedding = model.encode([query])

# Find most similar
similarities = model.util.semantic_search(query_embedding, embeddings, top_k=3)
print(f"Found related content: {similarities}")
```

---

## 🎯 Comparison Table

| Dataset Type       | CSV Columns               | Use Case           | Model Gain                  |
| ------------------ | ------------------------- | ------------------ | --------------------------- |
| **Q&A**            | question, answer          | ChatBot, QA system | Answers student questions   |
| **Classification** | text, label               | Categorization     | Organize content by subject |
| **Similarity**     | query, positive, negative | Search engine      | Find related content        |

---

## 📊 Dataset Statistics

### Classification Example Output:

```
📊 Label distribution:
   physics: 145 chunks
   biology: 203 chunks
   chemistry: 87 chunks
   general: 65 chunks
```

### Q&A Example:

```
Created Q&A dataset with 1,240 pairs
(Multiple questions per chunk = more training data)
```

### Similarity Example:

```
Created 500 similarity triplets
(query, relevant, irrelevant)
```

---

## 🚀 Recommended: What to Use Your Data For

Given you're building with **Chroma + sentence-transformers**, I recommend:

### Best Fit: **Semantic Search + Q&A System**

```python
# Step 1: Use Q&A dataset
python create_labeled_datasets.py  # Creates curriculum_qna.csv

# Step 2: Build retrieval system
from transformers import pipeline

qa_system = pipeline("question-answering", model="distilbert-base-uncased")

# Step 3: When student asks a question
question = "How does the eye lens work?"
for idx, row in df.iterrows():
    if row['chunk_id'] in relevant_chunks:  # Use Chroma to find similar
        answer = qa_system(question=question, context=row['answer'])
        print(answer['answer'])
```

---

## 💡 Next Steps

**Choose based on your teacher's requirement:**

1. **"Create a search system"** → Use **Similarity dataset**
2. **"Categorize content"** → Use **Classification dataset**
3. **"Build Q&A for students"** → Use **Q&A dataset**
4. **"Recommendation system"** → Use **Classification + Similarity**

**Generate all three:**

```bash
python create_labeled_datasets.py
```

Then discuss with your teacher which one to train on!
