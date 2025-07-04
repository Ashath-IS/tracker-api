import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Case, When, F, FloatField, ExpressionWrapper
from api.models import Option, Question, Topic, User, UserAnswer

def test_api(request):
    return JsonResponse({"message": "Hello from Django backend"})

def fetch_user_by_email(request):
    email = request.GET.get('email')  # ?email=someone@example.com

    if not email:
        return JsonResponse({'error': 'Email is required as query param'}, status=400)

    try:
        user = User.objects.get(email=email)
        return JsonResponse({
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'created_at': user.created_at
        })
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

@csrf_exempt
def create_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            email = data.get('email')

            print("name", name, email)

            if not name or not email:
                return JsonResponse({"error": "name and email are required"}, status=400)

            user = User.objects.create(name=name, email=email)
            return JsonResponse({
                "message": "User created successfully",
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "created_at": user.created_at,
                }
            }, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Only POST method allowed"}, status=405)

@csrf_exempt
def create_question(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)

    try:
        data = json.loads(request.body)
        topic_name = data.get('topic')
        question_text = data.get('question')
        options = data.get('options', [])

        if not topic_name or not question_text or not options:
            return JsonResponse({'error': 'Missing topic, question, or options'}, status=400)

        # Get or create topic by name
        topic, created = Topic.objects.get_or_create(name=topic_name)

        # Create the question
        question = Question.objects.create(topic=topic, text=question_text)

        # Create each option
        for opt in options:
            Option.objects.create(
                question=question,
                text=opt['text'],
                is_correct=opt.get('is_correct', False)
            )

        return JsonResponse({
            'message': 'Question created successfully',
            'question_id': question.id
        }, status=201)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
def get_questions_by_topic(request):
    topic_name = request.GET.get('topic')
    user_id = request.GET.get('user_id')

    if not topic_name:
        return JsonResponse({'error': 'Topic name is required: ?topic=React'}, status=400)

    try:
        topic = Topic.objects.get(name__iexact=topic_name)
    except Topic.DoesNotExist:
        return JsonResponse({'error': 'Topic not found'}, status=404)

    # Get all questions and related options for this topic
    questions = Question.objects.filter(topic=topic).prefetch_related('options')

    # Get answered question IDs by user (if provided)
    answered_question_ids = set()
    if user_id:
        try:
            user = User.objects.get(id=user_id)
            answered_question_ids = set(
                UserAnswer.objects.filter(user=user, question__topic=topic).values_list('question_id', flat=True)
            )
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

    # Build response
    data = []
    for q in questions:
        is_answered = q.id in answered_question_ids
        data.append({
            'id': q.id,
            'text': q.text,
            'answered': is_answered,
            'options': [
                {
                    'id': opt.id,
                    'text': opt.text,
                    'disabled': is_answered  # 🔒 Mark options disabled if already answered
                } for opt in q.options.all()
            ]
        })

    return JsonResponse(data, safe=False)

@csrf_exempt
def submit_answer(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)

    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        question_id = data.get('question_id')
        selected_option_id = data.get('selected_option_id')

        if not all([user_id, question_id, selected_option_id]):
            return JsonResponse({'error': 'user_id, question_id and selected_option_id are required'}, status=400)

        user = User.objects.get(id=user_id)
        question = Question.objects.get(id=question_id)
        selected_option = Option.objects.get(id=selected_option_id)

        # Check correctness
        is_correct = selected_option.is_correct

        # Save or update the answer
        answer, created = UserAnswer.objects.update_or_create(
            user=user,
            question=question,
            defaults={
                'selected_option': selected_option,
                'is_correct': is_correct
            }
        )

        return JsonResponse({
            'message': 'Answer submitted',
            'is_correct': is_correct,
            'updated': not created
        })

    except (User.DoesNotExist, Question.DoesNotExist, Option.DoesNotExist):
        return JsonResponse({'error': 'Invalid user/question/option'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

def get_user_progress(request):
    user_id = request.GET.get('user_id')

    if not user_id:
        return JsonResponse({'error': 'user_id is required'}, status=400)

    try:
        user = User.objects.get(id=user_id)

        # Step 1: Annotate basic progress
        topics = Topic.objects.annotate(
            total_questions=Count('question'),
            completed=Count(
                Case(
                    When(question__useranswer__user=user, then=1)
                )
            )
        ).annotate(
            percent=ExpressionWrapper(
                F('completed') * 100.0 / F('total_questions'),
                output_field=FloatField()
            )
        )

        result = []
        for topic in topics:
            item = {
                'id': topic.id,
                'name': topic.name,
                'total_questions': topic.total_questions,
                'completed': topic.completed,
                'percent': round(topic.percent, 2),
            }

            # Step 2: If fully completed, show correct & wrong counts
            if topic.completed == topic.total_questions:
                user_answers = UserAnswer.objects.filter(
                    user=user, question__topic=topic
                )
                item['correct_count'] = user_answers.filter(is_correct=True).count()
                item['wrong_count'] = user_answers.filter(is_correct=False).count()

            result.append(item)

        return JsonResponse({'progress': result})

    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)