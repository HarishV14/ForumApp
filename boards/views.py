from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse
from .forms import NewTopicForm,PostForm
from django.http import HttpResponse
from .models import Board,Post,Topic
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.views.generic import UpdateView,ListView
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

#Function based view 
def home(request):
    boards = Board.objects.all()
    return render(request, 'home.html', {'boards': boards})

# Class based view
class BoardListView(ListView):
    model = Board
    context_object_name = 'boards'
    template_name = 'home.html'
 
 #Function based View 
def board_topics(request, pk):
    board = get_object_or_404(Board, pk=pk)
    queryset = board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
    page = request.GET.get('page', 1)

    paginator = Paginator(queryset, 4)

    try:
        topics = paginator.page(page)
    except PageNotAnInteger:
        # fallback to the first page
        topics = paginator.page(1)
    except EmptyPage:
        # probably the user tried to add a page number
        # in the url, so we fallback to the last page
        topics = paginator.page(paginator.num_pages)

    return render(request, 'topics.html', {'board': board, 'topics': topics})

# class based view
class TopicListView(ListView):
    model = Topic
    context_object_name = 'topics'
    template_name = 'topics.html'
    paginate_by = 4

    def get_context_data(self, **kwargs):
        # It adds the board object to the context, allowing the template to access information about the specific board 
        kwargs['board'] = self.board
        # retrieve default context data and combine with it
        return super().get_context_data(**kwargs)
    
    # queryset value is named as topics in templated because it is using model topic so ..
    def get_queryset(self):
        self.board = get_object_or_404(Board, pk=self.kwargs.get('pk'))
        queryset = self.board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
        return queryset
    
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

class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'topic_posts.html'
    paginate_by = 2
    
    # it provide additional context data
    def get_context_data(self, **kwargs):
        session_key = 'viewed_topic_{}'.format(self.topic.pk)
        if not self.request.session.get(session_key, False):
            self.topic.views += 1
            self.topic.save()
            self.request.session[session_key] = True
        
        kwargs['topic'] = self.topic
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.topic = get_object_or_404(Topic, board__pk=self.kwargs.get('pk'), pk=self.kwargs.get('topic_pk'))
        queryset = self.topic.posts.order_by('created_at')
        return queryset

# def topic_posts(request, pk, topic_pk):
#     topic = get_object_or_40  4(Topic, board__pk=pk, pk=topic_pk)
#     topic.views += 1
#     topic.save()
#     return render(request, 'topic_posts.html', {'topic': topic})

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
            topic.last_updated = timezone.now()  
            topic.save()
            topic_url = reverse('topic_posts', kwargs={'pk': pk, 'topic_pk': topic_pk})
            # this is to mention the page number for pointing the page
            topic_post_url = '{url}?page={page}#{id}'.format(
                url=topic_url,
                id=post.pk,
                page=topic.get_page_count()
            )
            return redirect(topic_post_url)

    else:
        form = PostForm()
    return render(request, 'reply_topic.html', {'topic': topic, 'form': form})


# this is for class based view login required
# dipatch method is responsible incoming http request
@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Post
    # it is used to create the model form
    fields = ('message', )
    template_name = 'edit_post.html'
    # identify the name of the keyword argument used to retrive the Post Object
    pk_url_kwarg = 'post_pk'
    # context variable that will be used in template to acess the post object
    context_object_name = 'post'
    
    # getting the current user
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)
    
    def form_valid(self, form):
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.save()
        return redirect('topic_posts', pk=post.topic.board.pk, topic_pk=post.topic.pk)