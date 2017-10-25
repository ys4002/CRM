from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import User
from .models import Agent,Customer,log,Relation,Company


class UserForm(ModelForm):
    password = forms.CharField(max_length=40,
                               min_length=6,
                               widget=forms.PasswordInput,label="Password")
    password2 = forms.CharField(max_length=40,
                               min_length=6,
                               widget=forms.PasswordInput,label="Renter Password")
    class Meta:
        model=User
        fields = ['username','first_name','last_name','email','password','password2']



    def clean_password2(self):

        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')

        if password != password2:
            raise forms.ValidationError("Passwords must match")
        return password


class User_Form(ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class AgentForm(ModelForm):
    class Meta:
        model = Agent
        fields = ('bio', 'location','contact_no','avatar','birth_date')


class CustForm(ModelForm):
    class Meta:
        model = Customer
        fields = ('first_name','last_name','address','avatar','phone','email')

class updatem(ModelForm):
    class Meta:
        model = Relation
        fields = ('agen',)



class updatea(ModelForm):
    class Meta:
        model = Customer
        fields = ('first_name','last_name','address','avatar','phone','email','dtc','dta')

class updateagc(ModelForm):
    class Meta:
        model = Customer
        fields = ('dta',)



class RelationA(ModelForm):
    class Meta:
        model = Relation
        fields = ('agen',)

class LogF(ModelForm):
    class Meta:
        model = log
        fields = ('data',)


class import_csv(ModelForm):
    file = forms.FileField()
    class Meta:
        model = Customer
        fields = ()

class Validate_Admin(ModelForm):
    class Meta:
        model = User
        fields = ('is_staff',)

class Company_Form(ModelForm):
    class Meta:
        model = Company
        fields = ('Company_Image','Company_Name',)


class pass_form(ModelForm):
    old_password = forms.CharField(max_length=40,
                               min_length=6,
                               widget=forms.PasswordInput, label="Enter Old Password")
    password = forms.CharField(max_length=40,
                               min_length=6,
                               widget=forms.PasswordInput,label="Password")
    password2 = forms.CharField(max_length=40,
                               min_length=6,
                               widget=forms.PasswordInput,label="Renter Password")

    class Meta:
        model = User
        fields = ['old_password','password', 'password2',]

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')

        if password != password2:
            raise forms.ValidationError("Passwords must match")
        return password
