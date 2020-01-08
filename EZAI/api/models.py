from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_init
from django.dispatch import receiver
from oauth2_provider.models import AbstractApplication

from django.conf import settings
from django.core.files.storage import FileSystemStorage

from markdownx.models import MarkdownxField

from api.scaffold import doc_template 

class Customer(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    subscription = models.BooleanField(default=False)

    def __str__(self):
        return "%s" % (self.user.username)


@receiver(post_save, sender=get_user_model())
def create_customer_profile(sender, instance, created, **kwargs):
    if created:
        Customer.objects.create(user=instance)

@receiver(post_save, sender=get_user_model())
def save_customer_profile(sender, instance, **kwargs):  
    instance.customer.save()


#### Model to temporarly store the uploaded files before review 
class TemporaryFiles(models.Model):
    owner = models.TextField(max_length=100)
    file = models.FileField(upload_to='TempFiles/')

### Dummy models to populate the page ###
class MLModel(models.Model):
    owner = models.ForeignKey(Customer, on_delete=models.CASCADE) # When you remove a customer all models related to them will also be removed
    title = models.TextField(max_length=100)
    description = models.TextField(max_length=100)
    tempfileId = models.IntegerField(default=0)
    file = models.FileField(storage=FileSystemStorage(location=settings.MEDIA_ROOT),
                               upload_to='Models',
                               default='Models/NoName')
    reviewed = models.BooleanField(default=False)
    bucketurl = models.TextField(max_length=200,default="https://console.cloud.google.com/storage/browser/ezai-bucket")
    mlmodel = models.BinaryField(default=bytes("hello", 'utf-8'))
    def __str__(self):
        return "%s : %s" % (self.id, self.title)

@receiver(post_save, sender=MLModel)
def create_MLModel_doc(sender, instance, created, **kwargs):
    if created:
        ModelDocumentation.objects.get_or_create(mlmodel=instance)

### 1 to 1 relationship with Customer ###
class ApiKey(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    name = models.CharField(default='', max_length=30)
    model = models.ForeignKey(MLModel, on_delete=models.CASCADE, default="")
    key = models.CharField(default='', max_length=500)
    active = models.BooleanField(default=True)

### Model for oauth applications ###
#class MLApplication(AbstractApplication):
    #agreement = models.BooleanField()

### Model for markdown based documentation of an MLModel ### 
class ModelDocumentation(models.Model): 
    mlmodel = models.ForeignKey('MLModel', on_delete=models.CASCADE)
    documentation = MarkdownxField(default=doc_template)

    def __str__(self):
        return "%s : %s" % (self.id, self.mlmodel)