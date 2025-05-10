from django.contrib import admin
from .models import *


admin.site.register([
    User, Role, Seller, Buyer, Private, Shopkeeper
])