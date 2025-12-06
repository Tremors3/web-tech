from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from .models import User, Private, Shopkeeper, Buyer, Seller, Role


class UserRegistrationForm(UserCreationForm):
    ROLE_CHOICES = [('BUYER', 'Buyer'), ('SELLER', 'Seller')]
    
    role_types = forms.MultipleChoiceField(choices=ROLE_CHOICES, widget=forms.CheckboxSelectMultiple)
    
    # Private / Shopkeeper fields
    first_name = forms.CharField(required=False, min_length=5, max_length=100, strip=True)
    last_name = forms.CharField(required=False, min_length=5, max_length=100, strip=True)
    fiscal_code = forms.CharField(required=False, min_length=16, max_length=16, strip=True)

    business_name = forms.CharField(required=False, min_length=5, max_length=100, strip=True)
    headquarters_address = forms.CharField(required=False, min_length=5, max_length=100, strip=True)
    iva_number = forms.CharField(required=False, min_length=11, max_length=11, strip=True)

    # Buyer / Seller fields
    shipping_address = forms.CharField(required=False, min_length=5, max_length=100, strip=True)
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
        if 'SELLER' in selected_roles and not cleaned_data.get('collection_address'):
            self.add_error('collection_address', f'The collection address is required for seller users.')
        
        # The user must have at least one role
        if not selected_roles:
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


class UserProfileForm(forms.ModelForm):
    """Form to Update user's profile, and manage it's roles and extra fields."""

    ROLE_CHOICES = [('BUYER', 'Buyer'), ('SELLER', 'Seller')]
    role_types = forms.MultipleChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    # Private / Shopkeeper fields
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    fiscal_code = forms.CharField(required=False)

    business_name = forms.CharField(required=False)
    headquarters_address = forms.CharField(required=False)
    iva_number = forms.CharField(required=False)

    # Buyer / Seller fields
    shipping_address = forms.CharField(required=False)
    collection_address = forms.CharField(required=False)

    class Meta:
        model = User
        fields = [
            "email", "username", "bio", "legal_type", "role_types",
            "first_name", "last_name", "fiscal_code",
            "business_name", "headquarters_address", "iva_number",
            "shipping_address", "collection_address"
        ]
        widgets = {
            "legal_type": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        self.user_instance = kwargs.get("instance")
        super().__init__(*args, **kwargs)
        user = self.user_instance

        if user:
            # --- Private fields ---
            if user.legal_type == "PRIVATE":
                private = Private.objects.get(user=user)
                self.fields['first_name'].initial = private.first_name
                self.fields['last_name'].initial = private.last_name
                self.fields['fiscal_code'].initial = private.fiscal_code
            # --- Shopkeeper Fields ---
            else:
                shop = Shopkeeper.objects.get(user=user)
                self.fields['business_name'].initial = shop.business_name
                self.fields['headquarters_address'].initial = shop.headquarters_address
                self.fields['iva_number'].initial = shop.iva_number

            # --- Roles ---
            roles = Role.objects.filter(user=user, state="ACTIVE")
            self.fields['role_types'].initial = [r.type for r in roles]

            # --- Buyer / Seller ---
            if user.has_role("BUYER"):
                buyer = Buyer.objects.get(role__user=user)
                self.fields['shipping_address'].initial = buyer.shipping_address

            if user.has_role("SELLER"):
                seller = Seller.objects.get(role__user=user)
                self.fields['collection_address'].initial = seller.collection_address

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
        if 'SELLER' in selected_roles and not cleaned_data.get('collection_address'):
            self.add_error('collection_address', f'The collection address is required for seller users.')
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=commit)
        cleaned = self.cleaned_data
        legal_type = user.legal_type

        # --- PRIVATE ---
        if legal_type == "PRIVATE":
            private, _ = Private.objects.get_or_create(user=user)
            private.first_name = cleaned.get("first_name", private.first_name)
            private.last_name = cleaned.get("last_name", private.last_name)
            private.fiscal_code = cleaned.get("fiscal_code", private.fiscal_code)
            private.save()

        # --- SHOPKEEPER ---
        else:
            shop, _ = Shopkeeper.objects.get_or_create(user=user)
            shop.business_name = cleaned.get("business_name", shop.business_name)
            shop.headquarters_address = cleaned.get("headquarters_address", shop.headquarters_address)
            shop.iva_number = cleaned.get("iva_number", shop.iva_number)
            shop.save()

        # --- ROLES ---
        selected = cleaned.get("role_types", [])
        
        # BUYER
        if "BUYER" in selected:
            role, _ = Role.objects.get_or_create(user=user, type="BUYER")
            buyer, _ = Buyer.objects.get_or_create(role=role)
            buyer.shipping_address = cleaned.get("shipping_address", buyer.shipping_address)
            buyer.save()
        
        # SELLER
        if "SELLER" in selected:
            role, _ = Role.objects.get_or_create(user=user, type="SELLER")
            seller, _ = Seller.objects.get_or_create(role=role)
            seller.collection_address = cleaned.get("collection_address", seller.collection_address)
            seller.save()

        return user
