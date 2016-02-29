from django.contrib import admin
from commonapp.models import UserProfile, Role, Url

# Register your models here.


admin.site.register(UserProfile)
admin.site.register(Role)
admin.site.register(Url)
