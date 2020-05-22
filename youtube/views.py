from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.urls import reverse
from django.conf import settings

from django.db import IntegrityError

from .forms import YoutubeUploadForm
from django.views.generic.edit import FormView
from django.views.generic import View

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from google_auth_oauthlib.flow import Flow
from google.oauth2 import credentials

from .models import GoogleOAuthCredential
from django.forms.models import model_to_dict

import os
#WE ARE RUNNING THIS PROJECT ON LOCALHOST HTTP, THATS WHY WE NEED TO TELL OAUTH THAT THIS IS INSECURE TRANSPORT
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' 
# Create your views here.

# WE CAN SPECIFY WHAT DO WE WANT FUSING THIS API IN scopes  LIST
scopes = ["https://www.googleapis.com/auth/youtube.upload","https://www.googleapis.com/auth/youtube"]

class HomeView(FormView):
    template_name = 'home.html'
    form_class = YoutubeUploadForm

    def form_valid(self,form):
        file_name = form.cleaned_data['video'].temporary_file_path()
        print(file_name)
        credentials_dict = model_to_dict(GoogleOAuthCredential.objects.get(client_secret=settings.YT_CLIENT_SECRET))
        credential = credentials.Credentials(**credentials_dict)
        youtube = build('youtube', 'v3', credentials=credential)
        body = {
            'snippet': {
                'title': 'Video uploaded using django',
                'description': 'This video has been uploaded using Django and Youtube Data API.',
                'tags': 'django,api',
                'categoryId': '27'
            },
            'status': {
                'privacyStatus': 'unlisted'
            }
        }

        insert_request = youtube.videos().insert(part=','.join(body.keys()),body=body,media_body=MediaFileUpload(file_name, chunksize=-1, resumable=True))
        response = insert_request.execute()

        return HttpResponse('<h1>Hooray! It worked!</h1>')


class AuthView(View):
    def get(self,request,*args,**kwargs):
        flow = Flow.from_client_secrets_file(settings.YT_JSON_FILE, scopes)
        flow.redirect_uri = request.build_absolute_uri(reverse('auth_callback'))
        authorization_url, state = flow.authorization_url(access_type='offline',login_hint='gauravsharma727545@gmail.com',prompt='consent')

        return redirect(authorization_url)


class AuthCallbackView(View):
    def get(self,request,*args,**kwargs):
        state = request.GET.get('state')
        flow = Flow.from_client_secrets_file(settings.YT_JSON_FILE, scopes=scopes,state=state)
        flow.redirect_uri = request.build_absolute_uri(reverse('auth_callback'))
        authorization_response = request.build_absolute_uri()
        flow.fetch_token(authorization_response=authorization_response)
        credential = flow.credentials

        try:
            GoogleOAuthCredential.objects.create(token=credential.token,refresh_token=credential.refresh_token,token_uri=credential.token_uri,client_id= credential.client_id,client_secret=credential.client_secret,scopes=credential.scopes)
        except Exception as e:
            pass
        
        return redirect('/')
