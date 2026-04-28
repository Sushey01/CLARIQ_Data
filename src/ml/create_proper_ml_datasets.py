"""
Proper ML Training Dataset Formats
Shows different CSV structures used in industry for model training
"""

import json
import csv
import pandas as pd
from datetime import datetime, timedelta
import random

def create_supervised_training_dataset(json_file, csv_file):
    """
    Standard supervised learning dataset format.
    Used for: Classification, Regression, NER tasks
    
    Columns needed for ML:
    - Unique ID (for tracking)
    - Input feature (text, image, etc.)
    - Target label (what to predict)
    - Metadata (source, split, etc.)
    """
    print("📊 Creating SUPERVISED LEARNING Dataset")
    print("=" * 70)
    
    with open(json_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    dataset = []
    
    for idx, chunk in enumerate(chunks[:100]):  # Sample for demo
        # Classify into subjects based on keywords
        content_lower = chunk['content'].lower()
        
        if any(word in content_lower for word in ['eye', 'vision', 'retina', 'cornea']):
            label = 'biology'
        elif any(word in content_lower for word in ['light', 'refraction', 'lens', 'focal']):
            label = 'physics'
        else:
            label = 'general'
        
        dataset.append({
            'sample_id': f"SAMPLE_{idx:05d}",
            'text': chunk['content'],
            'label': label,
            'topic': chunk['source_pdf'].replace('.pdf', ''),
            'page': chunk['page'],
            'word_count': chunk['word_count'],
            'split': 'train' if random.random() > 0.2 else 'test'
        })
    
    df = pd.DataFrame(dataset)
    df.to_csv(csv_file, index=False)
    
    print(f"✅ Created: {csv_file}")
    print(f"📈 Total samples: {len(df)}")
    print(f"📊 Class distribution:\n{df['label'].value_counts()}\n")
    return df

def create_ner_training_dataset(json_file, csv_file):
    """
    Named Entity Recognition (NER) dataset format.
    Used for: Entity extraction, Concept identification
    
    Columns:
    - ID
    - Text
    - Entity tags (BIO format or similar)
    - Entity type
    - Start index, End index
    """
    print("📊 Creating NER (Named Entity Recognition) Dataset")
    print("=" * 70)
    
    with open(json_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    dataset = []
    
    # Define entities to extract
    entity_patterns = {
        'ANATOMY': ['eye', 'lens', 'retina', 'cornea', 'iris', 'pupil', 'optic nerve'],
        'CONCEPT': ['refraction', 'accommodation', 'focal length', 'vision', 'light'],
        'DEFECT': ['myopia', 'hypermetropia', 'presbyopia', 'cataract', 'astigmatism'],
        'VALUE': ['25 cm', '2.3 cm', '150 word', 'diopter']
    }
    
    sample_id = 0
    for chunk in chunks[:50]:
        content = chunk['content']
        
        # Find entities in text
        for entity_type, keywords in entity_patterns.items():
            for keyword in keywords:
                if keyword.lower() in content.lower():
                    start_idx = content.lower().find(keyword.lower())
                    end_idx = start_idx + len(keyword)
                    
                    dataset.append({
                        'sample_id': f"NER_{sample_id:05d}",
                        'text': content,
                        'entity_text': keyword,
                        'entity_type': entity_type,
                        'start_index': start_idx,
                        'end_index': end_idx,
                        'bio_tag': f'B-{entity_type}',
                        'document_id': chunk['chunk_id']
                    })
                    sample_id += 1
    
    df = pd.DataFrame(dataset)
    df.to_csv(csv_file, index=False)
    
    print(f"✅ Created: {csv_file}")
    print(f"📈 Total entities: {len(df)}")
    print(f"📊 Entity types:\n{df['entity_type'].value_counts()}\n")
    return df

def create_semantic_matching_dataset(json_file, csv_file):
    """
    Semantic similarity/matching dataset.
    Used for: Embedding models, Similarity search, Duplicate detection
    
    Columns:
    - ID
    - Sentence/Text 1
    - Sentence/Text 2
    - Similarity score (0-1)
    - Label (similar/dissimilar)
    """
    print("📊 Creating SEMANTIC MATCHING Dataset")
    print("=" * 70)
    
    with open(json_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    dataset = []
    pair_id = 0
    
    for i, chunk1 in enumerate(chunks[:30]):
        for j, chunk2 in enumerate(chunks[i+1:35]):
            # Determine similarity based on topic overlap
            topics1 = set(chunk1['content'].lower().split()[:20])
            topics2 = set(chunk2['content'].lower().split()[:20])
            
            overlap = len(topics1 & topics2) / max(len(topics1 | topics2), 1)
            
            # Convert overlap to similarity score and label
            similarity_score = overlap
            label = 'similar' if similarity_score > 0.4 else 'dissimilar'
            
            dataset.append({
                'pair_id': f"PAIR_{pair_id:05d}",
                'text_1': chunk1['content'][:200],
                'text_2': chunk2['content'][:200],
                'similarity_score': round(similarity_score, 3),
                'label': label,
                'doc_id_1': chunk1['chunk_id'],
                'doc_id_2': chunk2['chunk_id'],
                'source_1': chunk1['source_pdf'],
                'source_2': chunk2['source_pdf']
            })
            pair_id += 1
    
    df = pd.DataFrame(dataset)
    df.to_csv(csv_file, index=False)
    
    print(f"✅ Created: {csv_file}")
    print(f"📈 Total pairs: {len(df)}")
    print(f"📊 Label distribution:\n{df['label'].value_counts()}\n")
    return df

def create_sequence_labeling_dataset(json_file, csv_file):
    """
    Sequence labeling dataset.
    Used for: POS tagging, Chunking, Tagging tasks
    
    Columns:
    - ID
    - Sentence
    - Tokens
    - Tags (for each token)
    """
    print("📊 Creating SEQUENCE LABELING Dataset")
    print("=" * 70)
    
    with open(json_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    dataset = []
    
    for idx, chunk in enumerate(chunks[:20]):
        # Split into sentences
        sentences = chunk['content'].split('.')
        
        for sent_idx, sentence in enumerate(sentences[:3]):
            if len(sentence.strip()) < 10:
                continue
            
            # Simple token tagging (could be POS, BIO, etc.)
            tokens = sentence.strip().split()[:15]  # First 15 tokens
            
            # Assign simple tags (just for demo)
            tags = []
            for token in tokens:
                if token.lower() in ['the', 'a', 'an', 'is', 'are']:
                    tags.append('DET')
                elif token.lower() in ['eye', 'lens', 'light', 'retina']:
                    tags.append('NOUN')
                else:
                    tags.append('OTHER')
            
            dataset.append({
                'sequence_id': f"SEQ_{idx:04d}_{sent_idx:02d}",
                'sentence': sentence.strip(),
                'tokens': ' | '.join(tokens),
                'tags': ' | '.join(tags),
                'num_tokens': len(tokens),
                'source_doc': chunk['chunk_id']
            })
    
    df = pd.DataFrame(dataset)
    df.to_csv(csv_file, index=False)
    
    print(f"✅ Created: {csv_file}")
    print(f"📈 Total sequences: {len(df)}")
    print(f"📊 Average tokens: {df['num_tokens'].mean():.1f}\n")
    return df

def create_regression_dataset(json_file, csv_file):
    """
    Regression dataset.
    Used for: Predicting continuous values
    Example: Predict importance/relevance score of content
    
    Columns:
    - ID
    - Features (text)
    - Target (numeric value to predict)
    """
    print("📊 Creating REGRESSION Dataset")
    print("=" * 70)
    
    with open(json_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    dataset = []
    
    for idx, chunk in enumerate(chunks[:50]):
        # Generate importance score based on length and keywords
        word_count = chunk['word_count']
        content = chunk['content'].lower()
        
        # Calculate importance (0-10 scale)
        importance = 0
        
        # Length matters
        if word_count > 150:
            importance += 3
        elif word_count > 100:
            importance += 2
        else:
            importance += 1
        
        # Key concepts matter
        if any(word in content for word in ['definition', 'important', 'concept', 'fundamental']):
            importance += 2
        
        if any(word in content for word in ['example', 'demonstrate']):
            importance += 1
        
        importance = min(importance, 10)  # Cap at 10
        
        dataset.append({
            'content_id': f"CONTENT_{idx:05d}",
            'text': chunk['content'][:300],
            'word_count': chunk['word_count'],
            'importance_score': importance,  # Target value
            'page': chunk['page'],
            'source': chunk['source_pdf']
        })
    
    df = pd.DataFrame(dataset)
    df.to_csv(csv_file, index=False)
    
    print(f"✅ Created: {csv_file}")
    print(f"📈 Total samples: {len(df)}")
    print(f"📊 Importance scores: min={df['importance_score'].min()}, max={df['importance_score'].max()}, avg={df['importance_score'].mean():.1f}\n")
    return df

def create_ranking_dataset(json_file, csv_file):
    """
    Ranking/Recommendation dataset.
    Used for: Learning to rank, Recommendation systems
    
    Columns:
    - Query ID
    - Query
    - Document ID
    - Document
    - Relevance score (0-5 rating)
    """
    print("📊 Creating RANKING Dataset")
    print("=" * 70)
    
    with open(json_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    queries = [
        "How does the eye work?",
        "What is light refraction?",
        "What are vision defects?",
        "How do lenses correct vision?",
        "Explain accommodation"
    ]
    
    dataset = []
    pair_id = 0
    
    for q_idx, query in enumerate(queries):
        for d_idx, doc in enumerate(chunks[:20]):
            # Calculate relevance based on keyword overlap
            query_words = set(query.lower().split())
            doc_words = set(doc['content'].lower().split()[:50])
            
            overlap = len(query_words & doc_words)
            relevance = min(overlap, 5)  # Scale 0-5
            
            dataset.append({
                'ranking_id': f"RANK_{pair_id:05d}",
                'query_id': f"Q_{q_idx:02d}",
                'query': query,
                'doc_id': f"D_{d_idx:03d}",
                'document': doc['content'][:200],
                'relevance_score': relevance,
                'rank_label': 'highly_relevant' if relevance >= 4 else 'relevant' if relevance >= 2 else 'not_relevant'
            })
            pair_id += 1
    
    df = pd.DataFrame(dataset)
    df.to_csv(csv_file, index=False)
    
    print(f"✅ Created: {csv_file}")
    print(f"📈 Total ranking pairs: {len(df)}")
    print(f"📊 Relevance distribution:\n{df['rank_label'].value_counts()}\n")
    return df

if __name__ == "__main__":
    JSON_FILE = "curriculum_chunks.json"
    
    print("\n" + "=" * 70)
    print("PROPER ML TRAINING DATASET FORMATS")
    print("=" * 70 + "\n")
    
    print("[1] SUPERVISED LEARNING (Classification)")
    print("-" * 70)
    create_supervised_training_dataset(JSON_FILE, "dataset_supervised.csv")
    
    print("[2] NAMED ENTITY RECOGNITION (NER)")
    print("-" * 70)
    create_ner_training_dataset(JSON_FILE, "dataset_ner.csv")
    
    print("[3] SEMANTIC MATCHING")
    print("-" * 70)
    create_semantic_matching_dataset(JSON_FILE, "dataset_semantic.csv")
    
    print("[4] SEQUENCE LABELING")
    print("-" * 70)
    create_sequence_labeling_dataset(JSON_FILE, "dataset_sequences.csv")
    
    print("[5] REGRESSION")
    print("-" * 70)
    create_regression_dataset(JSON_FILE, "dataset_regression.csv")
    
    print("[6] RANKING/RECOMMENDATION")
    print("-" * 70)
    create_ranking_dataset(JSON_FILE, "dataset_ranking.csv")
    
    print("\n" + "=" * 70)
    print("✅ ALL PROPER ML TRAINING DATASETS CREATED!")
    print("=" * 70)
