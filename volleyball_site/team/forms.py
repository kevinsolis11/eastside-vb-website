from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import AccessCode, GameVideo, PlayerStats, Player, PlayerProfile, AISummary, Announcement


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    access_code = forms.CharField(max_length=32, required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_access_code(self):
        code = self.cleaned_data.get("access_code")
        try:
            access_code = AccessCode.objects.get(code=code, is_used=False)
        except AccessCode.DoesNotExist:
            raise forms.ValidationError("Invalid or used access code.")
        # check expiry
        if getattr(access_code, 'is_expired', None) and access_code.is_expired():
            raise forms.ValidationError("This access code has expired.")
        # check allowed email if the code is tied to an address
        email = self.cleaned_data.get('email')
        if getattr(access_code, 'matches_email', None) and not access_code.matches_email(email):
            raise forms.ValidationError("This access code is reserved for a different email address.")
        # store the instance for use in the view
        self.cleaned_data['access_code'] = access_code
        return access_code


class GameVideoUploadForm(forms.ModelForm):
    """Form for coaches to upload game videos."""
    class Meta:
        model = GameVideo
        fields = ['title', 'description', 'game_type', 'game_date', 'opponent', 'video', 'thumbnail', 'is_featured']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., State Championship vs Lincoln High'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Game summary, key moments, notes...'}),
            'game_type': forms.Select(attrs={'class': 'form-control'}),
            'game_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'opponent': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Opponent team name'}),
            'video': forms.FileInput(attrs={'class': 'form-control', 'accept': 'video/*'}),
            'thumbnail': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_video(self):
        video = self.cleaned_data.get('video')
        if video:
            # Check file size (max 35GB)
            if video.size > 35 * 1024 * 1024 * 1024:  # 35GB
                raise forms.ValidationError('Video file is too large. Maximum size is 35GB.')
            # Check file extension
            allowed_extensions = ['.mp4', '.mov', '.mkv', '.avi', '.webm']
            file_name = video.name.lower()
            if not any(file_name.endswith(ext) for ext in allowed_extensions):
                raise forms.ValidationError(f'Invalid video format. Allowed: {", ".join(allowed_extensions)}')
        return video
    
    def clean_thumbnail(self):
        thumbnail = self.cleaned_data.get('thumbnail')
        if thumbnail:
            # Check file size (max 5MB)
            if thumbnail.size > 5 * 1024 * 1024:  # 5MB
                raise forms.ValidationError('Thumbnail is too large. Maximum size is 5MB.')
            # Check file extension
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp']
            file_name = thumbnail.name.lower()
            if not any(file_name.endswith(ext) for ext in allowed_extensions):
                raise forms.ValidationError(f'Invalid image format. Allowed: {", ".join(allowed_extensions)}')
        return thumbnail


class PlayerStatsForm(forms.ModelForm):
    """Form for coaches to input/edit player stats."""
    class Meta:
        model = PlayerStats
        fields = ['kills', 'blocks', 'aces', 'digs']
        widgets = {
            'kills': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': 'Number of kills'}),
            'blocks': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': 'Number of blocks'}),
            'aces': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': 'Number of aces'}),
            'digs': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': 'Number of digs'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        # Ensure all stats are non-negative
        for field in ['kills', 'blocks', 'aces', 'digs']:
            value = cleaned_data.get(field)
            if value is not None and value < 0:
                self.add_error(field, 'Stats must be non-negative.')
        return cleaned_data


class PlayerEditForm(forms.Form):
    """Form for coaches to edit player information."""
    first_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'})
    )
    last_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'})
    )
    number = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '99', 'placeholder': 'Jersey number'})
    )
    position = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Setter, Middle, Outside Hitter'})
    )
    height = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 5\'10"'})
    )

class AISummaryForm(forms.Form):
    """Form for generating AI performance summaries."""
    game_context = forms.CharField(
        label='Game Performance Context',
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Describe the game or player performance (e.g., "15 kills, 8 digs, 2 aces in state tournament final vs Lincoln High")'
        }),
        help_text='Provide details about the game, opponent, player stats, and any key moments.'
    )


class AnnouncementForm(forms.ModelForm):
    """Form for coaches to create announcements."""
    class Meta:
        model = Announcement
        fields = ['title', 'message', 'is_urgent']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Announcement title',
                'maxlength': '200'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Type your announcement here...'
            }),
            'is_urgent': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'title': 'Title',
            'message': 'Message',
            'is_urgent': 'Mark as urgent'
        }