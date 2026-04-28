import pdfplumber
import json
import csv
import os
import re

def extract_and_chunk_pdfs(pdf_folder, output_file):
    all_chunks = []
    chunk_counter = 0
    
    # Check if folder exists
    if not os.path.exists(pdf_folder):
        print(f"❌ ERROR: Folder '{pdf_folder}' not found!")
        print("   Please check the path and try again.")
        return

    # List all PDF files
    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith('.pdf')]
    
    if not pdf_files:
        print(f"❌ No PDF files found in {pdf_folder}")
        return
    
    print(f"📚 Found {len(pdf_files)} PDF files. Starting extraction...\n")
    
    for pdf_name in pdf_files:
        pdf_path = os.path.join(pdf_folder, pdf_name)
        print(f"📖 Processing: {pdf_name}")
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                print(f"   Pages: {total_pages}")
                
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    
                    if not text or len(text.strip()) < 10:
                        continue
                    
                    # Clean text
                    text = re.sub(r'\s+', ' ', text).strip()
                    sentences = text.split('. ')
                    
                    chunk = ""
                    word_count = 0
                    
                    for sentence in sentences:
                        sentence = sentence.strip()
                        if not sentence:
                            continue
                        
                        words_in_sentence = len(sentence.split())
                        
                        # Group into ~150 word chunks
                        if word_count + words_in_sentence < 150:
                            chunk += sentence + ". "
                            word_count += words_in_sentence
                        else:
                            if chunk.strip():
                                chunk_counter += 1
                                all_chunks.append({
                                    "chunk_id": f"{pdf_name}_{page_num}_{chunk_counter}",
                                    "source_pdf": pdf_name,
                                    "page": page_num,
                                    "content": chunk.strip(),
                                    "word_count": len(chunk.split())
                                })
                            chunk = sentence + ". "
                            word_count = words_in_sentence
                    
                    if chunk.strip():
                        chunk_counter += 1
                        all_chunks.append({
                            "chunk_id": f"{pdf_name}_{page_num}_{chunk_counter}",
                            "source_pdf": pdf_name,
                            "page": page_num,
                            "content": chunk.strip(),
                            "word_count": len(chunk.split())
                        })
                
                print(f"   ✅ Extracted {chunk_counter} chunks so far...\n")
        
        except Exception as e:
            print(f"   ❌ Error with {pdf_name}: {e}\n")
    
    # Save to JSON
    print(f"\n💾 Saving {len(all_chunks)} chunks to {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)
    
    # Also save to CSV for model training
    csv_file = output_file.replace('.json', '.csv')
    print(f"💾 Also saving to CSV: {csv_file}...")
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['chunk_id', 'source_pdf', 'page', 'word_count', 'content']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for chunk in all_chunks:
            writer.writerow({
                'chunk_id': chunk['chunk_id'],
                'source_pdf': chunk['source_pdf'],
                'page': chunk['page'],
                'word_count': chunk['word_count'],
                'content': chunk['content']
            })
    
    print(f"✅ Done! Total chunks: {len(all_chunks)}")
    print(f"📊 Files created:")
    print(f"   • JSON: {output_file}")
    print(f"   • CSV: {csv_file}")
    return all_chunks

# ===== CONFIGURATION =====
# Update this path to match your folder exactly
PDF_FOLDER = "/home/shekhar/Downloads/jesc1dd" 
OUTPUT_FILE = "../../data/raw/curriculum_chunks.json"

# Run
if __name__ == "__main__":
    print("="*60)
    print("🚀 CLARIQ CURRICULUM EXTRACTOR")
    print("="*60 + "\n")
    
    chunks = extract_and_chunk_pdfs(PDF_FOLDER, OUTPUT_FILE)
    
    print("\n" + "="*60)
    print("✨ Extraction Complete!")
    print(f"📁 Output: {OUTPUT_FILE}")
    print("="*60)