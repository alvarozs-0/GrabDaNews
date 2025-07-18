from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Article, CustomUser, Newsletter, Publisher


class ArticleForm(forms.ModelForm):
    """
    Form for creating and editing articles.
    """
    class Meta:
        model = Article
        fields = ['title', 'content', 'publisher']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter article title'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 15,
                'placeholder': 'Write your article content here...'
            }),
            'publisher': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make publisher field optional for independent journalists
        self.fields['publisher'].required = False
        self.fields['publisher'].empty_label = "Independent (No Publisher)"


class UserRegistrationForm(UserCreationForm):
    """
    Form for user registration with role selection.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name'
        })
    )
    
    role = forms.ChoiceField(
        choices=CustomUser.ROLE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        initial='reader'
    )
    
    publisher = forms.ModelChoiceField(
        queryset=Publisher.objects.all(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        empty_label="Select a publisher (optional)"
    )
    
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'role', 'publisher', 'password1', 'password2'
        ]
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose a username'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to password fields
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    
    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        publisher = cleaned_data.get('publisher')
        
        # Require publisher for editors and journalists
        if role in ['editor', 'journalist'] and not publisher:
            raise forms.ValidationError(
                "Editors and journalists must be associated with a publisher."
            )
        
        # Readers shouldn't have a publisher
        if role == 'reader' and publisher:
            cleaned_data['publisher'] = None
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.role = self.cleaned_data['role']
        user.publisher = self.cleaned_data.get('publisher')
        
        if commit:
            user.save()
        return user


class NewsletterForm(forms.ModelForm):
    """
    Form for creating and editing newsletters.
    """
    class Meta:
        model = Newsletter
        fields = ['title', 'content', 'publisher']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter newsletter title'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 12,
                'placeholder': 'Write your newsletter content here...'
            }),
            'publisher': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make publisher field optional for independent journalists
        self.fields['publisher'].required = False
        self.fields['publisher'].empty_label = "Independent (No Publisher)"


class SearchForm(forms.Form):
    """
    Form for searching articles.
    """
    q = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search articles...',
            'autocomplete': 'off'
        }),
        label='Search'
    )
