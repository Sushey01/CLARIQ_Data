import json
import csv
import random
from pathlib import Path

def create_training_csv(json_file, csv_file, train_test_split=True, test_ratio=0.2, val_ratio=0.1):
    """
    Convert curriculum chunks to training-ready CSV with optional train/test/validation split.
    
    Args:
        json_file: Input JSON file with chunks
        csv_file: Output CSV file path
        train_test_split: If True, adds 'split' column (train/val/test)
        test_ratio: Ratio of data for testing (default 0.2)
        val_ratio: Ratio of data for validation (default 0.1)
    """
    
    print(f"📖 Reading JSON file: {json_file}")
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
        
        print(f"✓ Loaded {len(chunks)} chunks")
        
        # Assign train/test/val splits if requested
        if train_test_split:
            random.shuffle(chunks)
            total = len(chunks)
            test_size = int(total * test_ratio)
            val_size = int(total * val_ratio)
            
            for i, chunk in enumerate(chunks):
                if i < test_size:
                    chunk['split'] = 'test'
                elif i < test_size + val_size:
                    chunk['split'] = 'validation'
                else:
                    chunk['split'] = 'train'
            
            print(f"✓ Created train/validation/test split:")
            print(f"  - Training: {sum(1 for c in chunks if c['split'] == 'train')} chunks")
            print(f"  - Validation: {sum(1 for c in chunks if c['split'] == 'validation')} chunks")
            print(f"  - Testing: {sum(1 for c in chunks if c['split'] == 'test')} chunks")
        
        # Write to CSV
        print(f"\n💾 Writing to CSV: {csv_file}")
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            # Define CSV columns
            fieldnames = ['chunk_id', 'source_pdf', 'page', 'word_count', 'content']
            if train_test_split:
                fieldnames.append('split')
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            # Write data rows
            for chunk in chunks:
                row = {
                    'chunk_id': chunk['chunk_id'],
                    'source_pdf': chunk['source_pdf'],
                    'page': chunk['page'],
                    'word_count': chunk['word_count'],
                    'content': chunk['content']
                }
                if train_test_split:
                    row['split'] = chunk.get('split', 'train')
                
                writer.writerow(row)
        
        print(f"✅ Successfully created training CSV!")
        print(f"📊 File: {csv_file}")
        print(f"📈 Total rows: {len(chunks)}")
        
        return True
    
    except FileNotFoundError:
        print(f"❌ ERROR: {json_file} not found!")
        return False
    except json.JSONDecodeError:
        print(f"❌ ERROR: {json_file} is not valid JSON!")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def create_labeled_csv(json_file, csv_file, labels_dict=None):
    """
    Create CSV with optional labels for classification tasks.
    
    Args:
        json_file: Input JSON file
        csv_file: Output CSV file
        labels_dict: Dict mapping keywords to labels (e.g., {'eye': 'biology', 'light': 'physics'})
    """
    
    print(f"📖 Reading JSON file: {json_file}")
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
        
        print(f"✓ Loaded {len(chunks)} chunks")
        
        # Assign labels if provided
        if labels_dict:
            for chunk in chunks:
                content_lower = chunk['content'].lower()
                label = 'general'
                
                for keyword, category in labels_dict.items():
                    if keyword.lower() in content_lower:
                        label = category
                        break
                
                chunk['label'] = label
            
            print("✓ Labels assigned based on keywords")
        
        # Write to CSV
        print(f"\n💾 Writing to CSV: {csv_file}")
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['chunk_id', 'source_pdf', 'page', 'word_count', 'content']
            if labels_dict:
                fieldnames.append('label')
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for chunk in chunks:
                row = {
                    'chunk_id': chunk['chunk_id'],
                    'source_pdf': chunk['source_pdf'],
                    'page': chunk['page'],
                    'word_count': chunk['word_count'],
                    'content': chunk['content']
                }
                if labels_dict:
                    row['label'] = chunk.get('label', 'general')
                
                writer.writerow(row)
        
        print(f"✅ Successfully created labeled CSV!")
        print(f"📊 File: {csv_file}")
        
        return True
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    JSON_FILE = "curriculum_chunks.json"
    
    # Option 1: Simple CSV with train/test split
    print("=" * 60)
    print("Creating training-ready CSV with train/test/val split...")
    print("=" * 60)
    create_training_csv(
        JSON_FILE,
        "curriculum_chunks_training.csv",
        train_test_split=True,
        test_ratio=0.15,
        val_ratio=0.1
    )
    
    print("\n")
    
    # Option 2: CSV with labels (if applicable to your domain)
    print("=" * 60)
    print("Creating labeled CSV (example with subject labels)...")
    print("=" * 60)
    labels = {
        'eye': 'biology',
        'light': 'physics',
        'lens': 'physics',
        'vision': 'biology',
        'refraction': 'physics'
    }
    create_labeled_csv(
        JSON_FILE,
        "curriculum_chunks_labeled.csv",
        labels_dict=labels
    )
