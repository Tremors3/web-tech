from django.contrib import admin
from .models import *


class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'bio']


admin.site.register([
    User
], UserAdmin)


admin.site.register([
    Role, Seller, Buyer, Private, Shopkeeper
])