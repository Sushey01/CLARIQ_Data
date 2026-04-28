import json
import csv
import random
from pathlib import Path

def create_qna_dataset(json_file, csv_file):
    """
    Generate Question-Answer pairs from curriculum chunks.
    Useful for training Q&A models or fine-tuning retrievers.
    """
    print(f"📖 Reading JSON file: {json_file}")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    print(f"✓ Loaded {len(chunks)} chunks")
    
    qna_pairs = []
    
    for chunk in chunks:
        content = chunk['content']
        
        # Generate different types of questions from the content
        questions = generate_questions(content, chunk['source_pdf'], chunk['page'])
        
        for q in questions:
            qna_pairs.append({
                'question': q,
                'answer': content,
                'source_pdf': chunk['source_pdf'],
                'page': chunk['page'],
                'chunk_id': chunk['chunk_id']
            })
    
    # Write to CSV
    print(f"\n💾 Writing {len(qna_pairs)} Q&A pairs to CSV: {csv_file}")
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['question', 'answer', 'source_pdf', 'page', 'chunk_id']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for pair in qna_pairs:
            writer.writerow(pair)
    
    print(f"✅ Created Q&A dataset with {len(qna_pairs)} pairs!")
    return qna_pairs

def generate_questions(content, pdf_name, page):
    """Generate multiple question types from content."""
    questions = []
    
    # Extract first 10 words to use as basis
    words = content.split()[:10]
    
    # Question type 1: What/How questions
    if len(words) > 3:
        main_topic = ' '.join(words[1:4])
        questions.append(f"What is {main_topic}?")
        questions.append(f"Explain {main_topic}")
        questions.append(f"How does {main_topic} work?")
    
    # Question type 2: Definition questions
    if 'is' in content.lower():
        questions.append(f"Define the topic from {pdf_name}")
    
    # Question type 3: Descriptive questions
    if len(words) > 2:
        questions.append(f"Describe {words[0]} {words[1]}")
    
    # Question type 4: General comprehension
    questions.append("What does this text discuss?")
    questions.append("Summarize the key points")
    
    return [q for q in questions if q]  # Remove any empty questions

def create_classification_dataset(json_file, csv_file, label_rules=None):
    """
    Create labeled dataset for text classification.
    You need to define rules to assign labels.
    """
    print(f"📖 Reading JSON file: {json_file}")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    # Default label rules for science curriculum
    if label_rules is None:
        label_rules = {
            'physics': ['light', 'lens', 'refraction', 'focal', 'force', 'motion', 'energy'],
            'biology': ['eye', 'vision', 'retina', 'cornea', 'nerve', 'cell', 'organ'],
            'chemistry': ['atom', 'molecule', 'compound', 'element', 'reaction'],
            'general': []
        }
    
    print(f"✓ Loaded {len(chunks)} chunks")
    print(f"\n📋 Assigning labels based on keywords...")
    
    # Assign labels
    for chunk in chunks:
        content_lower = chunk['content'].lower()
        label = 'general'
        
        for category, keywords in label_rules.items():
            if category != 'general':
                if any(keyword in content_lower for keyword in keywords):
                    label = category
                    break
        
        chunk['label'] = label
    
    # Show distribution
    label_counts = {}
    for chunk in chunks:
        label = chunk['label']
        label_counts[label] = label_counts.get(label, 0) + 1
    
    print("\n📊 Label distribution:")
    for label, count in label_counts.items():
        print(f"   {label}: {count} chunks")
    
    # Write to CSV
    print(f"\n💾 Writing to CSV: {csv_file}")
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['text', 'label', 'source_pdf', 'page']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for chunk in chunks:
            writer.writerow({
                'text': chunk['content'],
                'label': chunk['label'],
                'source_pdf': chunk['source_pdf'],
                'page': chunk['page']
            })
    
    print(f"✅ Created classification dataset!")
    return chunks

def create_similarity_pairs(json_file, csv_file):
    """
    Create pairs for similarity/retrieval training.
    Format: query, positive_document, negative_document, label
    """
    print(f"📖 Reading JSON file: {json_file}")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    print(f"✓ Loaded {len(chunks)} chunks")
    
    pairs = []
    
    # Create triplets: query, positive match, negative match
    for i, query_chunk in enumerate(chunks):
        # Positive: randomly choose another chunk (could improve by similarity)
        if len(chunks) > 1:
            positive_idx = random.choice([j for j in range(len(chunks)) if j != i])
            positive_chunk = chunks[positive_idx]
            
            # Negative: choose random chunk far from query
            negative_idx = random.choice([j for j in range(len(chunks)) if j != i and j != positive_idx])
            negative_chunk = chunks[negative_idx]
            
            pairs.append({
                'query': query_chunk['content'],
                'positive': positive_chunk['content'],
                'negative': negative_chunk['content'],
                'query_id': query_chunk['chunk_id'],
                'positive_id': positive_chunk['chunk_id'],
                'negative_id': negative_chunk['chunk_id']
            })
    
    print(f"\n💾 Writing {len(pairs)} similarity pairs to CSV: {csv_file}")
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['query', 'positive', 'negative', 'query_id', 'positive_id', 'negative_id']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for pair in pairs:
            writer.writerow(pair)
    
    print(f"✅ Created similarity pairs dataset!")
    return pairs

if __name__ == "__main__":
    JSON_FILE = "curriculum_chunks.json"
    
    print("=" * 70)
    print("PROPER MODEL TRAINING DATASETS")
    print("=" * 70)
    
    print("\n[1] Creating Q&A Dataset (for Question-Answering models)...")
    print("-" * 70)
    create_qna_dataset(JSON_FILE, "curriculum_qna.csv")
    
    print("\n[2] Creating Classification Dataset (for Text Classification)...")
    print("-" * 70)
    create_classification_dataset(JSON_FILE, "curriculum_classification.csv")
    
    print("\n[3] Creating Similarity Pairs (for Retrieval/Semantic Search)...")
    print("-" * 70)
    create_similarity_pairs(JSON_FILE, "curriculum_similarity.csv")
    
    print("\n" + "=" * 70)
    print("✅ All training datasets created successfully!")
    print("=" * 70)
