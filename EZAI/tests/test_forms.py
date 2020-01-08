from django.test import TestCase
from api.forms import UserCreationForm, ChangeEmail

class TestUserCreation(TestCase): 
  def testUserCreationForm(self):
    form_data = {'username': "BobTheBuilder", 'first_name': "Bob", 'last_name': "Builder", 'email': 'bob@building.fi', 'password1': "ProjectCourse", 'password2': "ProjectCourse"}
    form = UserCreationForm(data=form_data)
    self.assertTrue(form.is_valid())
  
  def testUserCreationFailForm(self):
    form_data = {'username': "BobTheBuilder", 'first_name': "Bob", 'last_name': "Builder", 'email': 'bob@building.fi', 'password1': "ProjectCourse", 'password2': "ProjectCourse2"}
    form = UserCreationForm(data=form_data)
    self.assertFalse(form.is_valid())

class TestChangeEmail(TestCase):
  def testChangeEmail(self):
    form_data = {'email1': 'bob@asd.fi', 'email2': 'bobi@asd.fi'}
    form = ChangeEmail(data=form_data)
    self.assertTrue(form.is_valid())

  def testChangeFailEmail(self):
    form_data = {'email1': 'bob@asd.fi'}
    form = ChangeEmail(data=form_data)
    self.assertFalse(form.is_valid())

