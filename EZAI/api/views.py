### Imports ###
import secrets
import base64
import shutil
import threading
import os
import schedule
import time
import pickle
import json
import hashlib
import six
import urllib

from dummymodel import get_model

import keras
from keras.models import load_model
from keras.utils import CustomObjectScope
from keras.initializers import glorot_uniform

from rest_framework import viewsets
from rest_framework.views import APIView
from api.serializers import UserSerializer
from django.contrib.auth import (
    get_user_model,
    update_session_auth_hash,
    authenticate,
    login,
)
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.views.generic import TemplateView, CreateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

### Email verification imports ###
from .forms import SignUpForm, CreateModelForm, DocsEditor, ManageUsersForm
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from django.middleware.csrf import get_token

###################################

from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from api.forms import SignUpForm, ChangeEmail, CreateClientForm
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from django.views import generic
from .serializers import MLModelSerializer

### Import the Ml Model
from .models import MLModel, TemporaryFiles, ModelDocumentation, Customer, ApiKey


from google.cloud import storage


# Placeholder before storage!!!
keys = ["7hrHVCoEVvsqXKUsXyMjiPRNNqqAeK6N2NF4u74UHrY="]

# Create your views here.
class Index(TemplateView):
    template_name = "api/index.html"


class HelpPage(TemplateView):
    template_name = "api/guide.html"


class ManualPage(TemplateView):
    template_name = "api/general_guide.html"


### Sign Up With Email Confirmation Activation ###
def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = "Activate your EZAI account."
            message = render_to_string(
                "registration/acc_active_email.html",
                {
                    "user": user,
                    "domain": current_site.domain,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                    "token": account_activation_token.make_token(user),
                },
            )
            to_email = form.cleaned_data.get("email")
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            return HttpResponse(
                "Please confirm your email address to complete the registration"
            )
    else:
        form = SignUpForm()
    return render(request, "registration/signup.html", {"form": form})


### Activate the User Accounts ###
def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64).decode())
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, user.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        # return redirect('/') #TODO: Make a better redirect page
        return redirect("welcome")
    else:
        return HttpResponse("Activation link is invalid!")


@login_required
def welcome(request):
    return render(request, "registration/welcome.html")


### Get a API KEY View ###
# class GetAPIKey(TemplateView):
# template_name = "api/get_api_key.html"


class UserViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all().order_by("-date_joined")
    serializer_class = UserSerializer


@api_view(["GET", "POST"])
@permission_classes((IsAuthenticated,))
def predict(request):
    # TODO: Test against api tokens
    answ = None
    if request.method == "POST":
        model_parameters = request.data.get("model_params")
        print(model_parameters)

        mlmodel = get_model("dummy_model.pkl")
        answ = mlmodel.predict(model_parameters)
    return Response(
        {
            "prediction": answ,
            "api_token": request.data.get("API_token"),
            "model_params": request.data.get("model_params"),
        }
    )


## Model endpoint ##
# TODO: Authenticate usage based on API-keys
# sample input for the keras model.{"model_params": [[[1.483887,1.865988,2.234620,1.018782,-2.530891,-1.604642,0.774676,-0.465148,-0.495225]]]}
@api_view(["POST"])
def modelEndpoint(request, pk):
    answ = None
    kerasModel = False

    if request.method == "POST":
        model_parameters = request.data.get("model_params")

        print(model_parameters)

        curr_model = MLModel.objects.get(id=pk)

        if str(curr_model.file).endswith(".h5"):
            filepath = "TempFiles/" + str(curr_model.id) + ".h5"
            kerasModel = True
        else:
            filepath = "TempFiles/" + str(curr_model.id) + ".pkl"

        with open(filepath, "wb") as f:
            f.write(curr_model.mlmodel)

        with open(filepath, "rb") as f:
            if kerasModel:
                with CustomObjectScope({"GlorotUniform": glorot_uniform()}):
                    model = load_model(filepath)

                answ = model.predict(model_parameters)

            else:
                model = modelUnpickler(request, f)
                answ = model.predict(model_parameters)

        os.remove(filepath)

        return Response(
            {
                "prediction": answ,
                "api_token": request.data.get("API_token"),
                "model_params": request.data.get("model_params"),
            }
        )


### Generating API keys ###
def ApiGenerator():
    hex = secrets.token_bytes(32)  # Hex value with 32 bytes
    new_key = base64.b64encode(hex).decode()  # Convert to base64 String
    for key in keys:
        if key == new_key:
            new_key = ApiGenerator()
            break
    return new_key


### Hashing API keys ###
### Uses sha256 for hashing and returns a hex value ###
def hash_key(key):
    return hashlib.sha256(bytes(key, "utf-8")).hexdigest()


### Storing API keys ###
def store_key(request, key, name, model):
    api_key = hash_key(key)
    try:
        current_customer = Customer.objects.get(user=request.user)
        p = ApiKey(customer=current_customer, key=api_key, name=name, model=model)

        p.save()
        return True
    except:
        return False


### Allow Users To Change Password ###
@login_required
def change_password(request):
    form = PasswordChangeForm(user=request.user)

    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, "Password changed!")
            return redirect("/myAccount")  # TODO: Change this to a better page

    return render(request, "change/change_password.html", {"form": form,})


### Allow Users To Change Email ###
@login_required
def change_email(request):
    if request.method == "POST":
        user = request.user
        form = ChangeEmail(request.POST)
        if form.is_valid():
            if form.cleaned_data["email1"] == form.cleaned_data["email2"]:
                user.email = form.cleaned_data["email1"]
                user.save()
                messages.success(request, "Email changed!")
                return redirect(
                    "/myAccount"
                )  # TODO: Make this redirect to somewhere that makes sense
            else:
                messages.error(request, "Email addresses must match.")
        else:
            messages.error(request, "Please correct the error.")
    else:
        form = ChangeEmail()
    return render(request, "change/change_email.html", {"form": form})


### Render the Model zoo page ###
class ModelZoo(TemplateView):
    template_name = "api/model_zoo.html"


def DummyModel(request):
    return render(request, "api/docs.html")


### Account page that lets you change email, password and list you own models
@login_required
def myAccount(request):
    currentCustomer = Customer.objects.get(user=request.user)
    userModels = MLModel.objects.filter(owner=currentCustomer)
    print(userModels)
    return render(request, "api/myAccount.html", {"ModelList": userModels})


### Model documentation page
def modelPage(request, pk):
    mlmodel = get_object_or_404(MLModel, pk=pk)

    doc = ModelDocumentation.objects.get(mlmodel=mlmodel)

    isOwner = True if mlmodel.owner.user == request.user else False

    return render(
        request, "api/modeldocs.html", {"model": mlmodel, "doc": doc, "owner": isOwner}
    )


### Documentation editor view ###
@login_required
def documentationEditor(request, pk):
    doc = get_object_or_404(ModelDocumentation, id=pk)
    if request.user != doc.mlmodel.owner.user:
        return HttpResponse("FORBIDDEN")

    if request.POST:
        form = DocsEditor(request.POST)
        if form.is_valid():
            cleaned = form.cleaned_data

            # Update manually because it did not work otherwise?
            obj = ModelDocumentation.objects.get(pk=cleaned["id"])
            obj.documentation = cleaned["documentation"]
            obj.save()

            pk = obj.mlmodel.pk

            return redirect("model_docs", pk)
            # return render(request, "api/docs_edit.html", {"form": form})
    else:
        form = DocsEditor(instance=doc)

        return render(request, "api/docs_edit.html", {"form": form})


### Create the ML Models
@login_required
def createMlModel(request):
    if request.method == "POST":
        form = CreateModelForm(request.POST, request.FILES)
        if form.is_valid():
            # Save in session to ask for confirmation before saving
            request.session["title"] = form.cleaned_data["title"]
            request.session["description"] = form.cleaned_data["description"]
            tempFile = TemporaryFiles(
                owner=str(request.user), file=form.files["docfile"]
            )
            tempFile.save()
            request.session[
                "tempfileId"
            ] = tempFile.pk  # store the primary key of the tempfile

            request.session["fileName"] = form.cleaned_data["docfile"].name

            request.session.save()
            return redirect("confirm_model")

        else:
            messages.error(
                request, "Please fix"
            )  # TODO: Make descriptive error messages
    else:
        form = CreateModelForm()
    return render(request, "api/create_model.html", {"form": form})


### Stores the Model in the database ###
@login_required
def MLModelCreated(request):
    if "owner" and "title" and "description" in request.session:
        customer = Customer.objects.get(user=request.user)
        theModel = MLModel(
            owner=customer,
            title=request.session["title"],
            description=request.session["description"],
            tempfileId=request.session["tempfileId"],
        )
        theModel.save()

        url = moveModelFiles(request, theModel.id, theModel.tempfileId)
        theModel.file = url
        theModel.save()  # FIXME: It should be enough with one save location.

        theModel.mlmodel = modelToBinary(request, theModel)
        theModel.save()

        return render(request, "api/model_created.html")


@login_required
def modelToBinary(request, theModel):
    # FIXME: This is a POC, please don't push me to production

    modelUrl = theModel.file  # url to model file
    binaryFile = bytearray()

    with open(str(modelUrl), "rb") as file:
        fileBytes = file.read()
        binaryFile = bytearray(fileBytes)

    return binaryFile


@login_required
def confirm(request):
    # TODO: remove the placeholder
    return render(
        request,
        "api/confirm_model.html",
        {
            "title": request.session["title"],
            "description": request.session["description"],
            "file": request.session["fileName"],
        },
    )


### Moves the model from temp storage to the final place ###
@login_required
def moveModelFiles(request, mlModelId, tempFileId):
    # TODO: Make this fail silently
    tempFileModel = get_object_or_404(TemporaryFiles, id=tempFileId)
    tempFileUrl = tempFileModel.file.url
    print(tempFileUrl)
    if tempFileUrl.endswith(".h5"):  # if the file is a saved keras model
        mlModelUrl = "Models/" + str(mlModelId) + ".h5"
    else:
        mlModelUrl = (
            "Models/" + str(mlModelId) + ".pkl"
        )  # in case of other types, at this point mainly sklearn

    shutil.move(tempFileUrl, mlModelUrl)
    return mlModelUrl


### Get a model ###
def getMLModel(request, id1):
    theModel = get_object_or_404(MLModel, id=id1)
    request.session["id"] = theModel.id
    return render(
        request,
        "api/model.html",
        {
            "owner": theModel.owner,
            "title": theModel.title,
            "description": theModel.description,
        },
    )


### List all models on the site ###
class AllModels(generic.ListView):
    model = MLModel
    template_name = "api/model_zoo.html"

    def get_queryset(self):
        return MLModel.objects.all()


class MLModelViewSet(viewsets.ModelViewSet):
    queryset = MLModel.objects.all()
    serializer_class = MLModelSerializer


@login_required
def pickleMagic(filename, model):
    with open(filename, "wb") as file:
        pickle.dump(model, file)


@login_required
def modelUnpickler(request, model):
    return pickle.load(model)


### Uploads the models to the Ezai bucket located at GCS
def uploadFileToBucket(file, fileName):
    with open("secrets.json") as f:
        conf = json.load(f)

    client = storage.Client(conf["PROJECTNAME"])
    bucket = client.get_bucket(conf["BUCKETNAME"])
    blob = bucket.blob(fileName)

    blob.upload_from_string(file, content_type="application/*")

    url = blob.public_url
    if isinstance(url, six.binary_type):
        url = url.decode("utf-8")

    return url


def loadFromBucket(fileName):
    with open("secrets.json") as f:
        conf = json.load(f)

    client = storage.Client(conf["PROJECTNAME"])
    bucket = client.get_bucket(conf["BUCKETNAME"])
    blob = bucket.get_blob(fileName)
    blob.download_to_filename("DownloadedModels/" + fileName)


def search(request):
    query = request.POST["usr_query"]
    if query:
        model = MLModel.objects.filter(title__icontains=query)
        print(model)
        return render(request, "api/search.html", {"models": model, "query": query})
    return HttpResponse("Please enter a search term")


### Runs in the background and deletes all Files in the TempFiles folder every 10 minutes ###
def backgroundProcessCleanTemp():  # TODO: Test this implementation. If the timing is wrong it will delete all the files before they have been moved.
    def job():
        folder = "TempFiles"
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(e)

    schedule.every(10).minutes.do(job)
    while 1:
        schedule.run_pending()
        time.sleep(30)


### Start the background thread ###
def cleanTemp():
    # need to make thread to continue running main program
    t = threading.Thread(target=backgroundProcessCleanTemp, args=(), kwargs={})
    t.setDaemon(True)
    t.start()


### Create client API keys###
@method_decorator(login_required, name="dispatch")
class GetAPIKey(TemplateView):
    template_name = "api/get_api_key.html"

    def get(self, request):
        register_form = CreateClientForm()
        revoke_key_form = ManageUsersForm()
        keys = ApiKey.objects.filter(customer=request.user.customer)

        return render(
            request,
            "api/get_api_key.html",
            {
                "register_form": register_form,
                "api_keys": keys,
                "revoke_key_form": revoke_key_form,
            },
        )

    def post(self, request):
        if "register" in request.POST:
            user = request.user
            form = CreateClientForm(request.POST)
            if form.is_valid():
                key = ApiGenerator()
                secret_key = hash_key(key)
                store_key(
                    request,
                    secret_key,
                    form.cleaned_data["client_name"],
                    form.cleaned_data["ml_model"],
                )
                register_form = CreateClientForm()
                revoke_key_form = ManageUsersForm()
                keys = ApiKey.objects.filter(customer=request.user.customer)
                return render(
                    request,
                    "api/get_api_key.html",
                    {
                        "register_form": register_form,
                        "api_keys": keys,
                        "revoke_key_form": revoke_key_form,
                    },
                )
            else:
                return Response(
                    status=status.HTTP_406_NOT_ACCEPTABLE
                )  # Needs a better solution !!!
        elif "revoke_key" in request.POST:
            api_key = ApiKey.objects.filter(key=request.POST.get("revoke")).first()
            api_key.active = False
            api_key.save()
            register_form = CreateClientForm()
            revoke_key_form = ManageUsersForm()
            keys = ApiKey.objects.filter(customer=request.user.customer)
            return render(
                request,
                "api/get_api_key.html",
                {
                    "register_form": register_form,
                    "api_keys": keys,
                    "revoke_key_form": revoke_key_form,
                },
            )
        else:
            return Response(status=status.HTTP_409_CONFLICT)


### Lets superusers manage other users keys ###
@method_decorator(user_passes_test(lambda u: u.is_superuser), name="dispatch")
class ManageUsers(TemplateView):
    template_name = "api/manage_users.html"

    def get(self, request):
        form = ManageUsersForm()
        keys = ApiKey.objects.exclude(active=False)
        return render(request, "api/manage_users.html", {"form": form, "keys": keys})

    def post(self, request):
        api_key = ApiKey.objects.filter(key=request.POST.get("revoke")).first()
        api_key.active = False
        api_key.save()
        form = ManageUsersForm()
        keys = ApiKey.objects.exclude(active=False)
        return render(request, "api/manage_users.html", {"form": form, "keys": keys})


### Api endpoint ###
@method_decorator(csrf_exempt, name="dispatch")
def api_request(request):
    if request.method == "POST":
        request.META["HTTP_AUTHORIZATION"]
    else:
        return HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED)
