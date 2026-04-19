"""
AI Service for EduSolve using Groq
Based on your ai_engine.py
"""

import os
import json
from groq import Groq
from django.conf import settings


class GroqAIService:
    """Service for Groq AI integration"""
    
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"  # Updated model
        
        self.system_prompt = """
You are EduSolve AI, a tutor for Indian Class 9 and 10 students.
You ONLY answer Science and Mathematics questions.
If the question is not about Science or Maths, reply:
"I only help with Science and Maths doubts!"

Always respond in this exact format:

EXPLANATION:
(explain clearly in simple language for a 15 year old)

KEY FORMULA / FACT:
(the most important formula or fact)

REAL EXAMPLE:
(one simple real life example)
"""
    
    def solve_doubt(self, question, subject=None, grade=None, context=None):
        """
        Solve student's doubt using Groq AI
        """
        # Build prompt
        prompt = f"[Class {grade or 9}] [{subject or 'General'}] Student doubt: {question}"
        
        # Build messages
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Add context if provided
        if context:
            for msg in context:
                messages.append({
                    "role": msg.get('role', 'user'),
                    "content": msg.get('content', '')
                })
        
        # Add current question
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            
            ai_response = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else 0
            
            return {
                'success': True,
                'response': ai_response,
                'tokens_used': tokens_used,
                'model': self.model
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response': 'Sorry, I encountered an error. Please try again.'
            }
    
    def get_practice_questions(self, ai_answer, subject, grade, count=3):
        """
        Generate practice questions based on the answer
        """
        prompt = f"""
Based on this explanation given to a Class {grade} {subject} student:
{ai_answer}

Generate exactly {count} challenging multiple-choice practice questions. 
The incorrect options (distractors) should be highly plausible common misconceptions to make it difficult to guess.
Return ONLY a JSON array in this exact format, nothing else:
[
  {{
    "question": "...",
    "option_a": "...",
    "option_b": "...",
    "option_c": "...",
    "option_d": "...",
    "correct_answer": "A", 
    "explanation": "Why this answer is correct..."
  }}
]
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Return only valid JSON. No markdown formatting, no backticks, no intro text."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            raw = response.choices[0].message.content
            start = raw.find("[")
            end = raw.rfind("]") + 1
            
            if start != -1 and end != 0:
                return json.loads(raw[start:end])
            return []
            
        except Exception as e:
            print(f"Error generating practice questions: {e}")
            return []

# Create singleton instance
ai_service = GroqAIService()