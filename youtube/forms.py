from django import forms

class YoutubeUploadForm(forms.Form):
    video = forms.FileField()
