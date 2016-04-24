from django import forms
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from passwords.fields import PasswordField  # django-password


class RegisterForm(forms.Form):

    username = forms.CharField(
        label="Username",
        max_length=30,
        min_length=3,
        required=True
    )
    password = PasswordField(
        label="Password"
    )
    first_name = forms.CharField(
        label="First name",
        max_length=30,
        required=False
    )
    last_name = forms.CharField(
        label="Last name",
        max_length=30,
        required=False
    )
    email = forms.EmailField(
        label="Email",
        required=False
    )

    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()
        username = cleaned_data.get('username')

        if User.objects.filter(username=username).count():
            self.add_error(
                'username',
                "This username is already in use."
            )

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)

        # Crispy Forms Helper
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_id = "register-form"

        # customize the layout
        self.helper.layout = Layout(
            'username',
            'password',
            'first_name',
            'last_name',
            'email'
        )
