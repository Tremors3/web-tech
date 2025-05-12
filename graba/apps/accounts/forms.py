from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from .models import User, Private, Shopkeeper


class UserRegistrationForm(UserCreationForm):
    ROLE_CHOICES = [('BUYER', 'Buyer'), ('SELLER', 'Seller')]
    
    role_types = forms.MultipleChoiceField(choices=ROLE_CHOICES, widget=forms.CheckboxSelectMultiple)
    
    # Private user fields
    first_name = forms.CharField(required=False, min_length=5, max_length=100, strip=True)
    last_name = forms.CharField(required=False, min_length=5, max_length=100, strip=True)
    fiscal_code = forms.CharField(required=False, min_length=16, max_length=16, strip=True)

    # Shopkeeper fields
    business_name = forms.CharField(required=False, min_length=5, max_length=100, strip=True)
    headquarters_address = forms.CharField(required=False, min_length=5, max_length=100, strip=True)
    iva_number = forms.CharField(required=False, min_length=11, max_length=11, strip=True)

    # Buyer fields
    shipping_address = forms.CharField(required=False, min_length=5, max_length=100, strip=True)
    
    # Seller fields
    collection_address = forms.CharField(required=False, min_length=5, max_length=100, strip=True)

    class Meta:
        model = User
        fields = [
            'email', 'username', 'bio', 'password1', 'password2', 'legal_type', 'role_types',
            'first_name', 'last_name', 'fiscal_code',
            'business_name', 'headquarters_address', 'iva_number',
            'shipping_address', 'collection_address'
        ]

    def clean(self):
        cleaned_data = super().clean()
        legal_type = cleaned_data.get('legal_type')
        selected_roles = cleaned_data.get('role_types', [])

        # Check private user fields
        if legal_type == 'PRIVATE':
            for field in ['first_name', 'last_name', 'fiscal_code']:
                if not cleaned_data.get(field):
                    self.add_error(field, f'This field is required for private users.')
        
        # Check shopkeeper fields
        elif legal_type == 'SHOPKEEPER':
            for field in ['business_name', 'iva_number', 'headquarters_address']:
                if not cleaned_data.get(field):
                    self.add_error(field, f'This field is required for shopkeepers.')
        
        # The user must select the legal type
        else:
            self.add_error('legal_type', 'You must select one legal type.')

        # Check buyer user fields
        if 'BUYER' in selected_roles and not cleaned_data.get('shipping_address'):
            self.add_error('shipping_address', f'The shipping address is required for buyer users.')
        
        # Check seller user fields
        elif 'SELLER' in selected_roles and not cleaned_data.get('collection_address'):
            self.add_error('collection_address', f'The collection address is required for seller users.')
        
        # The user must have at least one role
        elif not selected_roles:
            self.add_error('role_types', 'You must select at least one role.')
            

        return cleaned_data


class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'autofocus': True})
    )

    def confirm_login_allowed(self, user):
        if user.state != 'ACTIVE':
            raise forms.ValidationError("The account has been suspended.", code='inactive')