from django.test import TestCase

# Create your tests here.
# https://ordinarycoders.com/blog/article/django-testing
from .models import Product
# https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Testing

class ModelTest(TestCase):
    def testProductModel(self):
        product = Product.objects.create(name="ToyCar", price=800)
        self.assertEquals(str(product), 'ToyCar')
        print("IsInstance : ",isinstance(product,Product))
        self.assertTrue(isinstance(product, Product))

    def testBookModel(self):
        pass