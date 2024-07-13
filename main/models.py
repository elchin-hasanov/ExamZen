from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Subject(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Question(models.Model):
    PAPER_CHOICES = [
        ('1', 'Paper 1'),
        ('2', 'Paper 2'),
        ('3', 'Paper 3'),
    ]
    
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    text = models.TextField()
    answer = models.TextField(blank=True, null=True)
    paper = models.CharField(max_length=1, choices=PAPER_CHOICES)
    choices = models.CharField(max_length=10000, blank=True, null=True)
    topic = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return self.text

class Reward(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    received_at = models.DateTimeField(auto_now_add=True)

class Test(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    paper = models.CharField(max_length=1, choices=[('1', 'Paper 1'), ('2', 'Paper 2')], default='1')
    questions = models.ManyToManyField(Question, related_name='tests')
    answers = models.TextField(blank=True, null=True)  # Store answers for Paper 1 here
    paper1_correct_answers = models.IntegerField(default=0)  # To store the number of correct answers in Paper 1
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject.name} - Paper {self.paper}"
