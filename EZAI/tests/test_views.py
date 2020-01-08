from django.test import TestCase
from api.views import ApiGenerator

class ApiGenerationTest(TestCase):
	def test_api_generator(self):
		keys = []
		for _ in range(10000):
			keys.append(ApiGenerator())
		self.assertTrue(len(keys) == len(set(keys)))


class LogInTest(TestCase):
	fixtures = ['users.json']
	urls = [
		'/get_api_key',
		'/change_password/',
		'/api/predict',
		'/change_email/',
		'/create_model',
		'/myAccount',
	]

	def testLogin(self):
		login = self.client.login(username='John', password='ProjectCourse')
		for url in self.urls: 
			print("Testing login_required on url: " + url)
			response = self.client.get(url)
			self.assertEqual(response.status_code, 200)
	
	def testFailedLogin(self): 
		login = self.client.login(username="John", password="asd")
		response = self.client.get('/myAccount')
		self.assertEqual(response.status_code, 302)