# CSV Data Collection Setup Guide

## Overview

Your project now has **3 ways** to generate CSV files for model training from your curriculum data:

---

## Method 1: Simple JSON-to-CSV Converter

**File:** `json_to_csv.py`

Converts your existing `curriculum_chunks.json` to a basic CSV format.

**Usage:**

```bash
python json_to_csv.py
```

**Output:** `curriculum_chunks.csv`

**CSV Columns:**

- `chunk_id` - Unique identifier
- `source_pdf` - Source PDF file
- `page` - Page number
- `word_count` - Number of words in chunk
- `content` - The actual text content

---

## Method 2: Automatic CSV Export (Recommended)

**File:** `extract_curriculum.py` (Enhanced)

Now automatically generates **both JSON and CSV** when extracting PDFs.

**Usage:**

```bash
python extract_curriculum.py
```

**Output:**

- `curriculum_chunks.json` (original JSON format)
- `curriculum_chunks.csv` (new CSV for training)

**Benefit:** Single command extracts and creates both formats!

---

## Method 3: Advanced Training-Ready CSV

**File:** `create_training_csv.py`

Creates CSV with **train/validation/test splits** and optional **labels** for classification tasks.

**Usage:**

```bash
python create_training_csv.py
```

**Outputs:**

1. `curriculum_chunks_training.csv` - With automatic train/val/test split
2. `curriculum_chunks_labeled.csv` - With subject-based labels

**CSV Columns (Training):**

- `chunk_id`
- `source_pdf`
- `page`
- `word_count`
- `content`
- `split` - One of: `train`, `validation`, `test`

**CSV Columns (Labeled):**

- `chunk_id`
- `source_pdf`
- `page`
- `word_count`
- `content`
- `label` - Assigned label based on keywords

---

## CSV Format Details

### Standard Columns

All CSV files include these core columns:

```
chunk_id,source_pdf,page,word_count,content
jesc110.pdf_1_1,jesc110.pdf,1,147,"10 CHAPTER The Human Eye and the Colourful World..."
jesc110.pdf_1_2,jesc110.pdf,1,136,"10.1 THE HUMAN EYE The human eye is one of..."
```

### Usage for Model Training

**For Text Classification:**

```python
import pandas as pd
df = pd.read_csv('curriculum_chunks_labeled.csv')
X = df['content']
y = df['label']
```

**For Text Embeddings/Vector Training:**

```python
import pandas as pd
df = pd.read_csv('curriculum_chunks_training.csv')
train_data = df[df['split'] == 'train']['content']
val_data = df[df['split'] == 'validation']['content']
test_data = df[df['split'] == 'test']['content']
```

**For Named Entity Recognition (NER):**

```python
import pandas as pd
df = pd.read_csv('curriculum_chunks.csv')
texts = df['content'].tolist()
# Prepare for annotation/labeling
```

---

## Recommended Workflow

1. **Extract PDFs:**

   ```bash
   python extract_curriculum.py
   # Generates: curriculum_chunks.json + curriculum_chunks.csv
   ```

2. **Create Training Split:**

   ```bash
   python create_training_csv.py
   # Generates: curriculum_chunks_training.csv (with splits)
   ```

3. **Use in Your Model:**
   ```python
   import pandas as pd
   df = pd.read_csv('curriculum_chunks_training.csv')
   train = df[df['split'] == 'train']
   val = df[df['split'] == 'validation']
   test = df[df['split'] == 'test']
   ```

---

## Customization

### Modify Train/Test Ratio

In `create_training_csv.py`, adjust these parameters:

```python
create_training_csv(
    JSON_FILE,
    "curriculum_chunks_training.csv",
    train_test_split=True,
    test_ratio=0.20,      # 20% for testing (change this)
    val_ratio=0.10        # 10% for validation (change this)
)
```

### Modify Labels

In `create_training_csv.py`, update the labels dictionary:

```python
labels = {
    'eye': 'biology',
    'light': 'physics',
    # Add your own keywords and categories
}
```

---

## Next Steps

✅ Run one of the scripts above to generate your CSV  
✅ Verify the CSV in your preferred tool (Excel, Python, etc.)  
✅ Use the CSV for model training with scikit-learn, TensorFlow, PyTorch, etc.  
✅ Adjust splits/labels as needed for your specific use case

---

## Tips for Your Teacher

- **CSV is universal** - works with any ML framework (TensorFlow, PyTorch, scikit-learn, Keras)
- **Train/Val/Test split** - prevents overfitting and enables proper evaluation
- **Labels/Categories** - enables supervised learning (classification tasks)
- **Chunk metadata** - source_pdf and page help trace results back to original documents
