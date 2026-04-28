"""
RAG CONVERSATIONAL TUTOR - Implementation Guide
This shows how to use the CSV files to build an actual working system
"""

import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb
import random

class RAGConversationalTutor:
    """
    Complete RAG-based conversational tutor system
    Uses 5 CSV files for knowledge, questions, tracking, and adaptation
    """
    
    def __init__(self, kb_csv, questions_csv, interactions_csv, 
                 performance_csv, curriculum_csv):
        """Initialize the tutor with data files"""
        
        print("🚀 Initializing RAG Conversational Tutor...")
        
        # Load all data
        self.knowledge_base = pd.read_csv(kb_csv)
        self.question_bank = pd.read_csv(questions_csv)
        self.interactions = pd.read_csv(interactions_csv)
        self.student_perf = pd.read_csv(performance_csv)
        self.curriculum = pd.read_csv(curriculum_csv)
        
        # Initialize embedding model (same as your Chroma setup)
        print("📚 Loading embedding model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Build embeddings for knowledge base
        print("🔗 Creating embeddings for knowledge base...")
        self.kb_embeddings = self.model.encode(
            self.knowledge_base['content'].tolist()
        )
        
        print(f"✅ Ready! Loaded {len(self.knowledge_base)} documents")
        print(f"✅ Ready! Loaded {len(self.question_bank)} questions")
    
    def retrieve_context(self, query, top_k=3, difficulty='medium'):
        """
        RAG retrieval: Find most relevant documents for a query
        Also filters by difficulty level
        """
        print(f"\n🔍 Searching knowledge base for: '{query}'")
        
        # Encode the query
        query_embedding = self.model.encode(query)
        
        # Calculate similarity scores
        similarities = np.dot(self.kb_embeddings, query_embedding)
        
        # Filter by difficulty if specified
        if difficulty != 'all':
            mask = self.knowledge_base['difficulty'] == difficulty
            similarities = similarities * mask.values
        
        # Get top-k most relevant
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        retrieved_docs = self.knowledge_base.iloc[top_indices][
            ['doc_id', 'topic', 'content', 'difficulty']
        ]
        
        print(f"✅ Found {len(retrieved_docs)} relevant documents\n")
        
        return retrieved_docs
    
    def select_next_question(self, student_id):
        """
        Select appropriate question based on student's performance
        and learning path
        """
        print(f"\n👤 Analyzing performance for student: {student_id}")
        
        # Get student's current performance
        student_data = self.student_perf[
            self.student_perf['student_id'] == student_id
        ]
        
        if len(student_data) == 0:
            print("   ℹ️  New student detected - starting with easy questions")
            current_level = 'easy'
        else:
            # Determine current level based on accuracy
            avg_accuracy = student_data['accuracy_percent'].mean()
            
            if avg_accuracy >= 85:
                current_level = 'hard'
                print(f"   ⭐ Excellent! ({avg_accuracy:.1f}% accuracy)")
            elif avg_accuracy >= 70:
                current_level = 'medium'
                print(f"   👍 Good progress! ({avg_accuracy:.1f}% accuracy)")
            else:
                current_level = 'easy'
                print(f"   💪 Keep practicing! ({avg_accuracy:.1f}% accuracy)")
        
        # Select question from appropriate difficulty
        matching_questions = self.question_bank[
            self.question_bank['difficulty'] == current_level
        ]
        
        if len(matching_questions) > 0:
            question = matching_questions.sample(1).iloc[0]
        else:
            question = self.question_bank.sample(1).iloc[0]
        
        print(f"   📝 Selected {current_level} level question:")
        print(f"      {question['question_text']}")
        
        return question, current_level
    
    def score_student_answer(self, student_answer, question, student_id):
        """
        Score student answer using RAG (semantic similarity)
        Compare with expected answer from knowledge base
        """
        print(f"\n✍️  Scoring answer: '{student_answer[:100]}...'")
        
        # Get expected answer from knowledge base
        expected_doc = self.knowledge_base[
            self.knowledge_base['doc_id'] == question['related_doc_id']
        ]
        
        if len(expected_doc) == 0:
            print("   ⚠️  Could not find expected answer")
            return 'unknown', 'poor', 0.0
        
        expected_answer = expected_doc.iloc[0]['content']
        
        # Score using semantic similarity
        student_emb = self.model.encode(student_answer)
        expected_emb = self.model.encode(expected_answer)
        
        # Calculate cosine similarity
        similarity = np.dot(student_emb, expected_emb) / (
            np.linalg.norm(student_emb) * np.linalg.norm(expected_emb)
        )
        
        # Convert to score interpretation
        if similarity > 0.75:
            is_correct = 'yes'
            quality = 'excellent'
            print(f"   ✅ EXCELLENT! ({similarity:.1%} match)")
        elif similarity > 0.55:
            is_correct = 'yes'
            quality = 'good'
            print(f"   ✓ GOOD! ({similarity:.1%} match)")
        elif similarity > 0.35:
            is_correct = 'no'
            quality = 'poor'
            print(f"   ⚠️  POOR ({similarity:.1%} match)")
        else:
            is_correct = 'no'
            quality = 'poor'
            print(f"   ❌ INCORRECT ({similarity:.1%} match)")
        
        return is_correct, quality, similarity
    
    def log_interaction(self, student_id, question, student_answer, 
                       is_correct, quality, time_taken=60, hints_used=0):
        """
        Log student-tutor interaction for tracking and adaptation
        """
        interaction = {
            'interaction_id': f"{student_id}_INT_{len(self.interactions)}",
            'student_id': student_id,
            'timestamp': pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            'question_id': question['question_id'],
            'student_answer': student_answer,
            'correct': is_correct,
            'answer_quality': quality,
            'time_taken_seconds': time_taken,
            'hints_used': hints_used,
            'topic_covered': question['topic'],
            'difficulty_level': question['difficulty']
        }
        
        # Append to interactions
        new_row = pd.DataFrame([interaction])
        self.interactions = pd.concat([self.interactions, new_row], ignore_index=True)
        
        print(f"   📝 Logged interaction")
        
        return interaction
    
    def update_student_performance(self, student_id, question, is_correct, time_taken):
        """
        Update student's performance metrics
        This drives the adaptive curriculum
        """
        topic = question['topic']
        
        # Find existing performance record
        student_topic_perf = self.student_perf[
            (self.student_perf['student_id'] == student_id) &
            (self.student_perf['topic'] == topic)
        ]
        
        if len(student_topic_perf) > 0:
            # Update existing record
            idx = student_topic_perf.index[0]
            
            current_attempts = self.student_perf.loc[idx, 'questions_attempted']
            current_correct = self.student_perf.loc[idx, 'questions_correct']
            
            self.student_perf.loc[idx, 'questions_attempted'] = current_attempts + 1
            
            if is_correct == 'yes':
                self.student_perf.loc[idx, 'questions_correct'] = current_correct + 1
            
            # Recalculate metrics
            new_accuracy = (
                self.student_perf.loc[idx, 'questions_correct'] / 
                self.student_perf.loc[idx, 'questions_attempted']
            ) * 100
            
            self.student_perf.loc[idx, 'accuracy_percent'] = new_accuracy
            
            # Update mastery level
            if new_accuracy > 85:
                mastery = 'advanced'
                ready = 'yes'
            elif new_accuracy > 70:
                mastery = 'intermediate'
                ready = 'yes'
            else:
                mastery = 'beginner'
                ready = 'no'
            
            self.student_perf.loc[idx, 'mastery_level'] = mastery
            self.student_perf.loc[idx, 'readiness_for_next_topic'] = ready
            self.student_perf.loc[idx, 'last_attempted'] = (
                pd.Timestamp.now().strftime("%Y-%m-%d")
            )
            
            print(f"   📊 Updated performance: {new_accuracy:.1f}% accuracy")
        else:
            # Create new performance record
            new_perf = {
                'student_id': student_id,
                'topic': topic,
                'questions_attempted': 1,
                'questions_correct': 1 if is_correct == 'yes' else 0,
                'accuracy_percent': 100 if is_correct == 'yes' else 0,
                'average_time_seconds': time_taken,
                'mastery_level': 'beginner',
                'last_attempted': pd.Timestamp.now().strftime("%Y-%m-%d"),
                'readiness_for_next_topic': 'no'
            }
            
            self.student_perf = pd.concat(
                [self.student_perf, pd.DataFrame([new_perf])], 
                ignore_index=True
            )
            
            print(f"   📊 Created new performance record")
    
    def get_personalized_curriculum(self, student_id):
        """
        Generate personalized curriculum path based on student performance
        """
        print(f"\n🎯 Generating personalized curriculum for {student_id}")
        
        student_perf = self.student_perf[
            self.student_perf['student_id'] == student_id
        ]
        
        print("\n📚 Student Progress:")
        for _, row in student_perf.iterrows():
            print(f"   • {row['topic']}: {row['accuracy_percent']:.1f}% "
                  f"({row['mastery_level']})")
        
        print("\n🗺️  Recommended Learning Path:")
        
        for _, path in self.curriculum.iterrows():
            print(f"\n   {path['order']}. {path['topic_name']}")
            
            # Check prerequisites
            if path['prerequisite_topics'] != 'None':
                prereqs = [p.strip() for p in path['prerequisite_topics'].split(',')]
                
                student_topics = student_perf['topic'].tolist()
                met_prereqs = all(p in student_topics for p in prereqs)
                
                if not met_prereqs:
                    print(f"      ⏳ Prerequisites not met: {path['prerequisite_topics']}")
                    continue
            
            # Check if student is ready
            ready_topics = student_perf[
                student_perf['readiness_for_next_topic'] == 'yes'
            ]['topic'].tolist()
            
            if path['topic_name'] in ready_topics or len(ready_topics) == 0:
                print(f"      ✅ READY! Target: {path['target_difficulty']} difficulty")
                print(f"      ⏱️  Estimated: {path['estimated_hours']} hours")
            else:
                print(f"      ⏸️  Come back after mastering prerequisites")

    def run_tutoring_session(self, student_id, num_questions=3):
        """
        Run a complete tutoring session with a student
        """
        print("\n" + "="*70)
        print(f"🎓 TUTORING SESSION for {student_id}")
        print("="*70)
        
        for i in range(num_questions):
            print(f"\n{'='*70}")
            print(f"Question {i+1}/{num_questions}")
            print(f"{'='*70}")
            
            # 1. Select question based on student level
            question, level = self.select_next_question(student_id)
            
            # 2. Retrieve relevant context for RAG
            context = self.retrieve_context(
                question['question_text'], 
                difficulty=level
            )
            
            print(f"\n📖 Context Documents:")
            for _, doc in context.iterrows():
                print(f"   • {doc['topic']}: {doc['content'][:100]}...")
            
            # 3. Simulate student answer (in real system, get from user input)
            print(f"\nStudent's answer: (simulated for demo)")
            student_answer = f"Based on the curriculum, {question['expected_answer_context'][:80]}"
            print(f"'{student_answer}...'")
            
            # 4. Score the answer using RAG
            is_correct, quality, similarity = self.score_student_answer(
                student_answer, question, student_id
            )
            
            # 5. Log interaction
            self.log_interaction(student_id, question, student_answer, 
                               is_correct, quality)
            
            # 6. Update performance
            self.update_student_performance(
                student_id, question, is_correct, time_taken=100
            )
        
        # 7. Show personalized curriculum
        self.get_personalized_curriculum(student_id)
        
        print("\n" + "="*70)
        print("✅ Session Complete!")
        print("="*70)


# Example Usage
if __name__ == "__main__":
    # Initialize tutor
    tutor = RAGConversationalTutor(
        kb_csv='rag_knowledge_base.csv',
        questions_csv='question_bank.csv',
        interactions_csv='student_interactions.csv',
        performance_csv='student_performance.csv',
        curriculum_csv='curriculum_paths.csv'
    )
    
    # Run a tutoring session
    tutor.run_tutoring_session('STU001', num_questions=3)
    
    # Save updated data
    print("\n💾 Saving updated data...")
    tutor.interactions.to_csv('student_interactions.csv', index=False)
    tutor.student_perf.to_csv('student_performance.csv', index=False)
    print("✅ Done!")
