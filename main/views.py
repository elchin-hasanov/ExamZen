from io import BytesIO
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import SignUpForm, LoginForm
from .forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from main.models import *
from django.db.models import Sum
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Question, Subject
import random
from .models import User, Reward

def home(request):
    top_users_with_points = User.objects.annotate(total_points=Sum('reward__points')).order_by('-total_points')[:3]
    context = {
        'first_place_user': top_users_with_points[0].username if top_users_with_points else None,
        'first_place_points': top_users_with_points[0].total_points if top_users_with_points else None,
        'second_place_user': top_users_with_points[1].username if len(top_users_with_points) > 1 else None,
        'second_place_points': top_users_with_points[1].total_points if len(top_users_with_points) > 1 else None,
        'third_place_user': top_users_with_points[2].username if len(top_users_with_points) > 2 else None,
        'third_place_points': top_users_with_points[2].total_points if len(top_users_with_points) > 2 else None,
    }
    return render(request, 'main/home.html', context)

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('main:zens')
            else:
                messages.error(request, 'Invalid username or password.')
                print("Invalid login attempt")
        else:
            print("Form is not valid")
    else:
        form = LoginForm()
    return render(request, 'main/login.html', {'form': form})

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
            login(request, user)
            return redirect('main:home')
        else:
            print("Form is not valid")
    else:
        form = SignUpForm()
    return render(request, 'main/signup.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('main:home')

@login_required
def zen(request):
    return render(request, 'main/zens.html')

@login_required
def lobby(request):
    subject = request.GET.get('subject', '')
    return render(request, 'main/lobby.html', {'subject': subject})

@login_required
def questionbank(request):
    subject_name = request.GET.get('subject_name', '')
    if subject_name:
        subject = get_object_or_404(Subject, name=subject_name)
        questions = Question.objects.filter(subject=subject)
    else:
        questions = Question.objects.all()  # Handle if no subject_name provided
    return render(request, 'main/questionbank.html', {'questions': questions, 'subject_name': subject_name})

@login_required
def question_answer(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    choices = question.choices.split('\\n') if question.choices else []
    return render(request, 'main/question_answer.html', {'question': question, 'choices': choices})



@login_required
def test(request):
    subject_name = request.GET.get('subject', '')
    paper = request.GET.get('paper', '1')
    context = {}

    if subject_name:
        subject = get_object_or_404(Subject, name=subject_name)
        
        if subject_name in ["Math", "Physics"]:
            if paper == '1':
                questions_paper1 = list(Question.objects.filter(subject=subject, paper='1'))
                selected_questions_paper1 = random.sample(questions_paper1, min(11 if subject_name == "Math" else 40, len(questions_paper1)))
                test_instance_paper1 = Test.objects.create(user=request.user, subject=subject, paper='1')
                for question in selected_questions_paper1:
                    test_instance_paper1.questions.add(question)
                
                questions_paper2 = list(Question.objects.filter(subject=subject, paper='2'))
                selected_questions_paper2 = random.sample(questions_paper2, min(6, len(questions_paper2)))
                test_instance_paper2 = Test.objects.create(user=request.user, subject=subject, paper='2')
                for question in selected_questions_paper2:
                    test_instance_paper2.questions.add(question)
                
                context = {
                    'subject': subject,
                    'questions_paper1': selected_questions_paper1,
                    'questions_paper2': selected_questions_paper2,
                    'paper': '1',
                    'test_instance_paper1': test_instance_paper1,
                    'test_instance_paper2': test_instance_paper2,
                }

        elif subject_name == "History":
            questions = list(Question.objects.filter(subject=subject))
            questions_by_topic = {}
            for question in questions:
                topic = question.topic
                if topic not in questions_by_topic:
                    questions_by_topic[topic] = []
                questions_by_topic[topic].append(question)
            selected_questions_by_topic = {topic: random.sample(questions, min(2, len(questions))) for topic, questions in questions_by_topic.items()}
            test_instance_paper2 = Test.objects.create(user=request.user, subject=subject, paper='2')
            for question in questions:
                test_instance_paper2.questions.add(question)
            context = {'subject': subject, 'questions_by_topic': selected_questions_by_topic}

        elif subject_name == "English":
            questions = list(Question.objects.filter(subject=subject))
            selected_questions = random.sample(questions, min(4, len(questions)))
            test_instance_paper2 = Test.objects.create(user=request.user, subject=subject, paper='2')
            for question in selected_questions:
                test_instance_paper2.questions.add(question)
            context = {'subject': subject, 'questions': selected_questions}

        if context:  # Check if context is not empty
            for key in ['questions_paper1', 'questions_paper2', 'questions']:
                if key in context:
                    for question in context[key]:
                        question.choices_list = question.choices.split('\\n') if question.choices else []
            return render(request, 'main/test.html', context)

    return redirect('main:zens')  # Default redirect if subject_name is missing or no valid context

@login_required
def submit_exam(request):
    if request.method == 'POST':
        paper1_instance = Test.objects.filter(user=request.user, paper='1').order_by('-created_at').first()
        paper2_instance = Test.objects.filter(user=request.user, paper='2').order_by('-created_at').first()

        if paper1_instance:
            paper1_answers = request.POST.get('answers_paper1', '')
            paper1_instance.answers = paper1_answers
            paper1_instance.save()

            # Count correct Paper 1 answers
            correct_answers_count = 0
            for question in paper1_instance.questions.all():
                user_answer = request.POST.get(f'answers_{question.id}')
                if user_answer == question.answer:
                    correct_answers_count += 1
            paper1_instance.paper1_correct_answers = correct_answers_count

            paper1_instance.save()

            Reward.objects.create(user=request.user, points=correct_answers_count)


        if paper2_instance:
            paper2_answers = request.POST.get('answers_paper2', '')
            paper2_instance.answers = paper2_answers
            paper2_instance.save()

        context = {
            'paper1_instance': paper1_instance,
            'paper2_instance': paper2_instance,
        }

        return render(request, 'main/submit_exam.html', context)

    return redirect('main:zens')

def rankings(request):
    # Calculate rankings for all users
    users = User.objects.annotate(total_points=Sum('reward__points')).order_by('-total_points')
    
    user_rankings = []
    for idx, user in enumerate(users, start=1):
        user_rankings.append({
            'rank': idx,
            'username': user.username,
            'points': user.total_points or 0,
        })
    
    context = {
        'user_rankings': user_rankings,
    }
    
    return render(request, 'main/ranking.html', context)

@login_required
def profile(request):
    user = request.user
    recent_tests = Test.objects.filter(user=user).order_by('-created_at')[:5]
    total_points = Reward.objects.filter(user=user).aggregate(Sum('points'))['points__sum'] or 0
    total_tests = Test.objects.filter(user=user, paper=1, subject__name="Physics").count()
    if total_tests == 0:
        average_score = total_points / 1
    else:
        average_score = total_points / total_tests
    

    context = {
        'username': user.username,
        'total_points': total_points,
        'total_tests': total_tests,
        'average_score': average_score,
        'recent_tests': recent_tests,
    }
    
    return render(request, 'main/profile.html', context)
