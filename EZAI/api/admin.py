from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model

from api.models import Customer, MLModel, TemporaryFiles, ModelDocumentation, ApiKey

from markdownx.admin import MarkdownxModelAdmin

User = get_user_model()

# Register your models here.
class CustomerInLine(admin.StackedInline):
    model = Customer 
    can_delete = False 
    verbose_name_plural = 'customers'

class UserAdmin(BaseUserAdmin): 
    inlines = (CustomerInLine, )

### Not currently working and low priority ###
class AppAdmin(admin.ModelAdmin):
    list_display = ('owner','file_link')
    def file_link(self, obj):
        if obj.file:
            return "<a href='%s'>download</a>" % (obj.file.url,)
        else:
            return "No attachment"
    file_link.allow_tags = True
    file_link.short_description = 'File Download'

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(MLModel)
admin.site.register(TemporaryFiles, AppAdmin)
admin.site.register(ModelDocumentation, MarkdownxModelAdmin)
admin.site.register(Customer)
admin.site.register(ApiKey)