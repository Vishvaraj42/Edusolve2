from django.db import models
from django.conf import settings
from doubts.models import DoubtSession


class PracticeQuestion(models.Model):
    """
    AI-generated practice questions related to doubts
    
    Just like Hitesh's e-commerce example - products have categories,
    our questions are linked to doubt sessions
    """
    
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    ANSWER_CHOICES = [
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D'),
    ]
    
    # Link to the doubt session this question is based on
    related_session = models.ForeignKey(
        DoubtSession,
        on_delete=models.CASCADE,
        related_name='practice_questions',
        help_text="The doubt session this question is based on"
    )
    
    # Question content
    question_text = models.TextField(
        help_text="The question text"
    )
    
    # Multiple choice options
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    
    correct_answer = models.CharField(
        max_length=1, 
        choices=ANSWER_CHOICES,
        help_text="The correct answer (A, B, C, or D)"
    )
    
    explanation = models.TextField(
        help_text="Detailed explanation of the answer"
    )
    
    # Metadata
    difficulty = models.CharField(
        max_length=10, 
        choices=DIFFICULTY_CHOICES
    )
    
    topic = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Specific topic covered"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Statistics
    times_attempted = models.IntegerField(
        default=0,
        help_text="How many times this question was attempted"
    )
    
    times_correct = models.IntegerField(
        default=0,
        help_text="How many times it was answered correctly"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Practice Question"
        verbose_name_plural = "Practice Questions"
    
    def __str__(self):
        return f"Q: {self.question_text[:50]}... ({self.difficulty})"
    
    @property
    def accuracy_rate(self):
        """
        Property decorator - Hitesh teaches this!
        Calculate accuracy percentage
        """
        if self.times_attempted == 0:
            return 0
        return round((self.times_correct / self.times_attempted) * 100, 2)


class StudentAnswer(models.Model):
    """
    Track student attempts at practice questions
    
    This is a MANY-TO-MANY relationship through a custom model
    (Student <-> Question with extra data)
    """
    
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='practice_attempts'
    )
    
    question = models.ForeignKey(
        PracticeQuestion,
        on_delete=models.CASCADE,
        related_name='student_attempts'
    )
    
    selected_answer = models.CharField(
        max_length=1,
        help_text="The answer the student selected"
    )
    
    is_correct = models.BooleanField(
        help_text="Whether the answer was correct"
    )
    
    time_taken_seconds = models.IntegerField(
        null=True,
        blank=True,
        help_text="Time taken to answer in seconds"
    )
    
    attempted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # Unique together - prevent duplicate attempts at same time
        unique_together = ['student', 'question', 'attempted_at']
        ordering = ['-attempted_at']
        verbose_name = "Student Answer"
        verbose_name_plural = "Student Answers"
    
    def __str__(self):
        checkmark = '✓' if self.is_correct else '✗'
        return f"{self.student.username} - {checkmark}"
    
    def save(self, *args, **kwargs):
        """
        Override save method
        Update question stats and award points (only on FIRST correct attempt!)
        """
        # 1. Check if this is a brand new attempt being saved for the first time
        is_new = self.pk is None
        
        # 2. Check if the student has ALREADY answered this correctly in the past
        already_mastered = False
        if is_new and self.is_correct:
            already_mastered = StudentAnswer.objects.filter(
                student=self.student,
                question=self.question,
                is_correct=True
            ).exists()
            
        # 3. Save the answer to the database
        super().save(*args, **kwargs)
        
        # 4. Update stats and award points
        if is_new:
            self.question.times_attempted += 1
            
            if self.is_correct:
                self.question.times_correct += 1
                
                # THE FIX: Only award points if they haven't gotten it right before!
                if not already_mastered:
                    points_map = {
                        'easy': 5,
                        'medium': 10,
                        'hard': 15
                    }
                    points = points_map.get(self.question.difficulty, 5)
                    self.student.add_points(points)
            
            # Save the updated question statistics
            self.question.save()