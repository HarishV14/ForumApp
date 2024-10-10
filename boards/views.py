from django.shortcuts import render,get_object_or_404,redirect
from .forms import NewTopicForm,PostForm
from django.http import HttpResponse
from .models import Board,Post,Topic
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Count


def home(request):
    boards = Board.objects.all()
    return render(request, 'home.html', {'boards': boards})


def board_topics(request, pk):
    board = get_object_or_404(Board, pk=pk)
    topics = board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
    return render(request, 'topics.html', {'board': board,'topics': topics})

@login_required
def new_topic(request, pk):
    board = get_object_or_404(Board, pk=pk)
    if request.method == 'POST':
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)   # This saves only the 'subject' from the form
            topic.board = board  # Set the board instance
            topic.starter = request.user
            topic.save() 
            post = Post.objects.create(
                # This gets the message field from the form we cannot acess by the topic because not intergrated with topic model
                message=form.cleaned_data.get('message'), 
                topic=topic,
                created_by=request.user
            ) 
            return redirect('topic_posts', pk=pk, topic_pk=topic.pk)
    else:
        form = NewTopicForm() 
    return render(request, 'new_topic.html', {'form': form, 'board': board})  


def topic_posts(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    topic.views += 1
    topic.save()
    return render(request, 'topic_posts.html', {'topic': topic})

@login_required
def reply_topic(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()
            return redirect('topic_posts', pk=pk, topic_pk=topic_pk)
    else:
        form = PostForm()
    return render(request, 'reply_topic.html', {'topic': topic, 'form': form})