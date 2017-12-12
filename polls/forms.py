# encoding:utf-8
# Author:Richie
# Date:12/11/2017


from django import forms
from .models import User

class LoginForm(forms.Form):
   username =  forms.CharField(widget=forms.TextInput,label='用户名')
   password =  forms.CharField(widget=forms.TextInput,label='密码')
