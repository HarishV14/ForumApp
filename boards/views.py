from django.shortcuts import render,get_object_or_404,redirect
from .forms import NewTopicForm
from django.http import HttpResponse
from .models import Board,Post
from django.contrib.auth.models import User


def home(request):
    boards = Board.objects.all()
    return render(request, 'home.html', {'boards': boards})


def board_topics(request, pk):
    board = get_object_or_404(Board, pk=pk)
    return render(request, 'topics.html', {'board': board})


def new_topic(request, pk):
    board = get_object_or_404(Board, pk=pk)
    user = User.objects.first()  # TODO: get the currently logged in user
    if request.method == 'POST':
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)   # This saves only the 'subject' from the form
            topic.board = board  # Set the board instance
            topic.starter = user
            topic.save() 
            post = Post.objects.create(
                # This gets the message field from the form we cannot acess by the topic because not intergrated with topic model
                message=form.cleaned_data.get('message'), 
                topic=topic,
                created_by=user
            ) 
            return redirect('board_topics', pk=board.pk)
    else:
        form = NewTopicForm() 
    return render(request, 'new_topic.html', {'form': form, 'board': board})  
