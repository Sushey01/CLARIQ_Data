import json
import csv
from pathlib import Path

def json_to_csv(json_file, csv_file):
    """
    Convert curriculum chunks from JSON to CSV format.
    Creates a CSV suitable for model training with the following columns:
    - chunk_id: Unique identifier for each chunk
    - source_pdf: Source PDF file name
    - page: Page number from the PDF
    - word_count: Number of words in the chunk
    - content: The actual text content
    """
    
    print(f"📖 Reading JSON file: {json_file}")
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
        
        print(f"✓ Loaded {len(chunks)} chunks")
        
        # Write to CSV
        print(f"💾 Writing to CSV: {csv_file}")
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            # Define CSV columns
            fieldnames = ['chunk_id', 'source_pdf', 'page', 'word_count', 'content']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            # Write header
            writer.writeheader()
            
            # Write data rows
            for chunk in chunks:
                writer.writerow({
                    'chunk_id': chunk['chunk_id'],
                    'source_pdf': chunk['source_pdf'],
                    'page': chunk['page'],
                    'word_count': chunk['word_count'],
                    'content': chunk['content']
                })
        
        print(f"✅ Successfully created CSV with {len(chunks)} rows!")
        print(f"📊 CSV file: {csv_file}")
        
        # Print sample
        print("\n📋 Sample CSV content (first 3 rows):")
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                if i < 3:
                    print(f"  {row[:4]}...")  # Print first 4 columns as preview
        
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

if __name__ == "__main__":
    # Input and output file paths
    JSON_FILE = "curriculum_chunks.json"
    CSV_FILE = "curriculum_chunks.csv"
    
    json_to_csv(JSON_FILE, CSV_FILE)
