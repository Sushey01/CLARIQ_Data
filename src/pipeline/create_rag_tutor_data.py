import json
import csv
import random
from datetime import datetime, timedelta

def create_rag_knowledge_base(json_file, csv_file):
    """
    Create the knowledge base for RAG system.
    This is what the system retrieves from when answering questions.
    """
    print(f"📖 Reading JSON file: {json_file}")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    print(f"✓ Loaded {len(chunks)} chunks\n")
    
    # Extract topics from content
    topic_mapping = {
        'eye': 'The Human Eye',
        'light': 'Light and Refraction',
        'lens': 'Lenses',
        'vision': 'Vision Defects',
        'accommodation': 'Eye Accommodation',
        'refraction': 'Light and Refraction',
        'cornea': 'The Human Eye',
        'retina': 'The Human Eye',
        'pupil': 'The Human Eye',
        'iris': 'The Human Eye',
    }
    
    knowledge_base = []
    
    for chunk in chunks:
        content_lower = chunk['content'].lower()
        
        # Determine topic
        topic = 'General Science'
        subtopic = 'Curriculum Content'
        difficulty = 'medium'
        
        for keyword, topic_name in topic_mapping.items():
            if keyword in content_lower:
                topic = topic_name
                if keyword in ['eye', 'vision']:
                    subtopic = 'Biology - Human Eye'
                    difficulty = 'medium'
                elif keyword in ['light', 'lens', 'refraction']:
                    subtopic = 'Physics - Optics'
                    difficulty = 'hard'
                break
        
        knowledge_base.append({
            'doc_id': chunk['chunk_id'],
            'source_pdf': chunk['source_pdf'],
            'page': chunk['page'],
            'topic': topic,
            'subtopic': subtopic,
            'difficulty': difficulty,
            'content': chunk['content'],
            'word_count': chunk['word_count'],
            'doc_type': 'explanatory'  # Can be: explanatory, example, definition, etc.
        })
    
    # Write to CSV
    print(f"💾 Writing {len(knowledge_base)} documents to knowledge base CSV: {csv_file}\n")
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['doc_id', 'source_pdf', 'page', 'topic', 'subtopic', 
                     'difficulty', 'doc_type', 'content', 'word_count']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(knowledge_base)
    
    print(f"✅ Created RAG Knowledge Base CSV!")
    print(f"📊 Total documents: {len(knowledge_base)}\n")
    return knowledge_base

def create_question_bank(json_file, csv_file):
    """
    Create question bank for the tutor to ask students.
    Different difficulty levels and question types.
    """
    print(f"📖 Creating Question Bank...")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    questions = []
    question_id = 1
    
    question_templates = {
        'definition': [
            "What is {topic}?",
            "Define {topic}",
            "Explain what {topic} means",
        ],
        'explanation': [
            "How does {topic} work?",
            "Explain the process of {topic}",
            "Describe {topic} in detail",
        ],
        'application': [
            "Give an example of {topic}",
            "How would you apply {topic} in real life?",
            "Why is {topic} important?",
        ],
        'comparison': [
            "What is the difference between {topic} and {related}?",
            "Compare {topic} with {related}",
        ]
    }
    
    topics_map = {
        'eye': ('The Human Eye', 'biology', 'medium'),
        'light': ('Light and Refraction', 'physics', 'hard'),
        'lens': ('Lenses', 'physics', 'hard'),
        'vision': ('Vision Defects', 'biology', 'medium'),
    }
    
    for chunk in chunks:
        content = chunk['content'].lower()
        
        # Find matching topic
        topic = 'General Concept'
        subject = 'general'
        base_difficulty = 'medium'
        
        for keyword, (topic_name, subj, diff) in topics_map.items():
            if keyword in content:
                topic = topic_name
                subject = subj
                base_difficulty = diff
                break
        
        # Generate questions from this chunk
        for qtype, templates in question_templates.items():
            if random.random() < 0.7:  # 70% chance to include this question type
                template = random.choice(templates)
                question_text = template.replace('{topic}', topic)
                question_text = question_text.replace('{related}', 'related concepts')
                
                # Difficulty increases by question type
                difficulty_map = {
                    'definition': 'easy',
                    'explanation': 'medium',
                    'application': 'hard',
                    'comparison': 'hard'
                }
                
                questions.append({
                    'question_id': f"Q{question_id}",
                    'question_text': question_text,
                    'question_type': qtype,
                    'topic': topic,
                    'subject': subject,
                    'difficulty': difficulty_map[qtype],
                    'related_doc_id': chunk['chunk_id'],
                    'expected_answer_context': chunk['content'][:200] + '...'
                })
                question_id += 1
    
    # Write to CSV
    print(f"💾 Writing {len(questions)} questions to CSV: {csv_file}\n")
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['question_id', 'question_text', 'question_type', 'topic', 
                     'subject', 'difficulty', 'related_doc_id', 'expected_answer_context']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(questions)
    
    print(f"✅ Created Question Bank CSV!")
    print(f"📊 Total questions: {len(questions)}\n")
    return questions

def create_student_interactions_template(csv_file):
    """
    Create template for tracking student interactions.
    This will be filled as students interact with the system.
    """
    print(f"📖 Creating Student Interactions Template...")
    
    interactions = []
    student_ids = [f"STU{i:03d}" for i in range(1, 6)]  # Sample 5 students
    
    for student_id in student_ids:
        base_date = datetime.now() - timedelta(days=30)
        
        for day_offset in range(0, 30, 3):  # Interactions every 3 days
            interaction_date = base_date + timedelta(days=day_offset)
            
            interaction = {
                'interaction_id': f"{student_id}_INT_{day_offset}",
                'student_id': student_id,
                'timestamp': interaction_date.strftime("%Y-%m-%d %H:%M:%S"),
                'question_id': f"Q{random.randint(1, 50)}",
                'student_answer': '',  # To be filled by student
                'correct': '',  # To be filled: yes/no
                'answer_quality': '',  # excellent/good/poor
                'time_taken_seconds': random.randint(30, 300),
                'hints_used': random.randint(0, 3),
                'topic_covered': 'The Human Eye',
                'difficulty_level': 'medium'
            }
            interactions.append(interaction)
    
    print(f"💾 Writing interaction template to CSV: {csv_file}\n")
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['interaction_id', 'student_id', 'timestamp', 'question_id',
                     'student_answer', 'correct', 'answer_quality', 'time_taken_seconds',
                     'hints_used', 'topic_covered', 'difficulty_level']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(interactions)
    
    print(f"✅ Created Student Interactions Template!")
    print(f"📊 Template rows: {len(interactions)} (sample interactions)\n")
    return interactions

def create_student_performance_tracking(csv_file):
    """
    Create student performance summary for curriculum adaptation.
    """
    print(f"📖 Creating Student Performance Tracking...")
    
    students = []
    topics = ['The Human Eye', 'Light and Refraction', 'Lenses', 'Vision Defects']
    
    for i in range(1, 6):
        student_id = f"STU{i:03d}"
        
        for topic in topics:
            performance = {
                'student_id': student_id,
                'topic': topic,
                'questions_attempted': random.randint(5, 20),
                'questions_correct': random.randint(2, 18),
                'accuracy_percent': random.randint(40, 100),
                'average_time_seconds': random.randint(60, 300),
                'mastery_level': 'beginner',  # Will be calculated: beginner/intermediate/advanced
                'last_attempted': (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d"),
                'readiness_for_next_topic': 'yes' if random.randint(40, 100) > 70 else 'no'
            }
            
            # Calculate mastery level
            if performance['accuracy_percent'] > 85:
                performance['mastery_level'] = 'advanced'
            elif performance['accuracy_percent'] > 70:
                performance['mastery_level'] = 'intermediate'
            else:
                performance['mastery_level'] = 'beginner'
            
            students.append(performance)
    
    print(f"💾 Writing performance tracking to CSV: {csv_file}\n")
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['student_id', 'topic', 'questions_attempted', 'questions_correct',
                     'accuracy_percent', 'average_time_seconds', 'mastery_level',
                     'last_attempted', 'readiness_for_next_topic']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(students)
    
    print(f"✅ Created Student Performance Tracking!")
    print(f"📊 Total performance records: {len(students)}\n")
    return students

def create_curriculum_paths(csv_file):
    """
    Create curriculum learning paths with prerequisites and sequences.
    """
    print(f"📖 Creating Curriculum Learning Paths...")
    
    paths = [
        {
            'path_id': 'PATH001',
            'topic_name': 'Understanding Light',
            'description': 'Learn about light, refraction, and lenses',
            'order': 1,
            'prerequisite_topics': 'None',
            'estimated_hours': 4,
            'target_difficulty': 'easy',
            'required_accuracy_percent': 80
        },
        {
            'path_id': 'PATH002',
            'topic_name': 'The Human Eye',
            'description': 'Learn about eye anatomy and how vision works',
            'order': 2,
            'prerequisite_topics': 'Understanding Light',
            'estimated_hours': 3,
            'target_difficulty': 'medium',
            'required_accuracy_percent': 75
        },
        {
            'path_id': 'PATH003',
            'topic_name': 'Vision Defects and Corrections',
            'description': 'Learn about common vision problems and corrections',
            'order': 3,
            'prerequisite_topics': 'The Human Eye, Understanding Light',
            'estimated_hours': 3,
            'target_difficulty': 'medium',
            'required_accuracy_percent': 75
        },
        {
            'path_id': 'PATH004',
            'topic_name': 'Advanced Optics',
            'description': 'Advanced concepts in light and vision',
            'order': 4,
            'prerequisite_topics': 'Vision Defects and Corrections',
            'estimated_hours': 5,
            'target_difficulty': 'hard',
            'required_accuracy_percent': 85
        }
    ]
    
    print(f"💾 Writing curriculum paths to CSV: {csv_file}\n")
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['path_id', 'topic_name', 'description', 'order', 
                     'prerequisite_topics', 'estimated_hours', 'target_difficulty',
                     'required_accuracy_percent']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(paths)
    
    print(f"✅ Created Curriculum Paths!")
    print(f"📊 Total learning paths: {len(paths)}\n")
    return paths

if __name__ == "__main__":
    JSON_FILE = "data/raw/curriculum_chunks.json"
    
    print("=" * 70)
    print("CREATING RAG CONVERSATIONAL TUTOR SYSTEM DATA")
    print("=" * 70)
    print()
    
    print("=" * 70)
    print("[1] KNOWLEDGE BASE - For RAG Retrieval")
    print("=" * 70)
    create_rag_knowledge_base(JSON_FILE, "data/processed/rag_knowledge_base.csv")
    
    print("=" * 70)
    print("[2] QUESTION BANK - For Student Assessment")
    print("=" * 70)
    create_question_bank(JSON_FILE, "data/processed/question_bank.csv")
    
    print("=" * 70)
    print("[3] STUDENT INTERACTIONS - Tracking Student Responses")
    print("=" * 70)
    create_student_interactions_template("data/processed/student_interactions.csv")
    
    print("=" * 70)
    print("[4] STUDENT PERFORMANCE - For Curriculum Adaptation")
    print("=" * 70)
    create_student_performance_tracking("data/processed/student_performance.csv")
    
    print("=" * 70)
    print("[5] CURRICULUM PATHS - Learning Sequence Design")
    print("=" * 70)
    create_curriculum_paths("curriculum_paths.csv")
    
    print("=" * 70)
    print("✅ ALL RAG TUTOR DATA CREATED SUCCESSFULLY!")
    print("=" * 70)
    print("\n📁 Files created:")
    print("   1. rag_knowledge_base.csv - Document store for RAG")
    print("   2. question_bank.csv - Questions to ask students")
    print("   3. student_interactions.csv - Track Q&A interactions")
    print("   4. student_performance.csv - Performance metrics")
    print("   5. curriculum_paths.csv - Learning sequences")
