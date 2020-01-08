from django.urls import path, re_path
from api.views import Index, GetAPIKey, ManageUsers, change_password, signup, change_email, createMlModel, getMLModel, confirm, MLModelCreated, AllModels, DummyModel, cleanTemp, myAccount, api_request, welcome
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', Index.as_view(), name="index"),
    path('help/', views.HelpPage.as_view(), name="help"),
    path('manual/', views.ManualPage.as_view(), name="manual"),
    path('signup/', signup, name="signup"),
    path('get_api_key', GetAPIKey.as_view(),name="get_api_key"),
    path('manage_users', ManageUsers.as_view(),name="manage_users"),
    path('change_password/', change_password,name="change_password"),
    path('api/predict', views.predict),
    path('change_email/', change_email,name="change_email"),
    re_path(r'activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$'
            , views.activate, name='activate'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name=r'registration/password_reset.html', success_url='/password_reset/sent/'), name="password_reset"),
    path('password_reset/sent/', auth_views.PasswordResetDoneView.as_view(template_name=r'registration/sent.html'), name="sent"),
    re_path(r'accounts/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',auth_views.PasswordResetConfirmView.as_view(template_name=r'registration/confirm.html',success_url='/accounts/reset/done/'),name="confirm"),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name=r'registration/complete.html'), name="complete"),
    path('model_zoo/', AllModels.as_view(),name="model_zoo"),
    path('model/docs/<int:pk>', views.modelPage, name="model_docs"),
    path('model/docs/edit/<int:pk>', views.documentationEditor, name="docs_editor"),
    # TODO: REMOVE DUMMY DOCS
    path('model/docs/dummy', DummyModel, name="dummy_docs"),
    path('create_model',createMlModel,name="create_model"),
    re_path(r'model_zoo/(?P<id1>\d+)/$',getMLModel, name='get_model'),
    path('confirm_model',confirm,name="confirm_model"),
    path('model_created',MLModelCreated,name="model_created"),
    path('api/models/predict/<int:pk>', views.modelEndpoint),
    path('myAccount', myAccount, name="myAccount"),
    path('search/', views.search, name='search'),
    path('welcome/', welcome, name='welcome'),

    path('api/request', api_request,name="api_request"),

]
cleanTemp()
