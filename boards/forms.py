from django import forms
from .models import Topic

class NewTopicForm(forms.ModelForm):
    # we dont have the message field in model so we created message
    message = forms.CharField(widget=forms.Textarea(), max_length=4000, help_text='The max length of the text is 4000.')
    
    # subject field as in model so we directly mention in the fiels in meta
    class Meta:
        model = Topic
        fields = ['subject', 'message']