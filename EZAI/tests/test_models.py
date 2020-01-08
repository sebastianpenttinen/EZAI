from django.test import TestCase
from api.models import Customer, MLModel, ModelDocumentation
from django.contrib.auth.models import User
# Create your tests here
class CustomerTests(TestCase):
	fixtures = ['users.json']

	def testFirstName(self): 
	    c = User.objects.get(pk=2)
	    self.assertEqual(c.first_name, "John")
    

class CustomerCreation(TestCase):
    def testCustomerCreation(self):
        user = User.objects.create_user(username="Mommy", email="mommy@yeboi.fi", password="ProjectCourse", first_name="Mom", last_name="Mommy")
        customer = Customer.objects.get(user=user)
        self.assertEqual(user, customer.user)

class DocumentationCreation(TestCase):
    fixtures = ['users.json']
    ''' TODO: Test that model creation actually signals db and creates a documentation 
    def testCreatesDocumentation(self):
        user = User.objects.get(pk=2)
        c = Customer.objects.get(user=user)
        mlmodel = MLModel(c, title="my model", description="", tempfileId=2).save()
        doc = ModelDocumentation.objects.get(mlmodel=mlmodel)
        self.assertEquals(doc.mlmodel, mlmodel)
    '''

class YourTestClass(TestCase):
    @classmethod
    def setUpTestData(cls):
        print("setUpTestData: Run once to set up non-modified data for all class methods.")
        pass

    def setUp(self):
        print("setUp: Run once for every test method to setup clean data.")
        pass

    def test_false_is_false(self):
        print("Method: test_false_is_false.")
        self.assertFalse(False)

    def test_false_is_true(self):
        print("Method: test_false_is_true.")
        self.assertTrue(True)

    def test_one_plus_one_equals_two(self):
        print("Method: test_one_plus_one_equals_two.")
        self.assertEqual(1 + 1, 2)