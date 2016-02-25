from django.contrib import admin
from commonapp.models import UserProfile, Role, Permission, Host

# Register your models here.


admin.site.register(UserProfile)
admin.site.register(Role)
admin.site.register(Permission)
admin.site.register(Host)
