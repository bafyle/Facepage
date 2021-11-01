from datetime import tzinfo
import pytz
from django.test import TestCase
from django.utils import timezone
from users.models import NewAccountActivationLink, SendEmailRequest
from django.contrib.auth import get_user_model as User

class TestNewAccountActivationLink(TestCase):

    @classmethod
    def setUpTestData(cls):
        User().objects.create(username="test", password="12345667")

    def setUp(self) -> None:
        self.user = User().objects.first()
        NewAccountActivationLink.objects.create(user=self.user, link='112/23324', create_date=timezone.datetime(2021, 11, 1, 1, 8, 7))
    
    def test_expired_method(self):
        self.assertEqual(
            NewAccountActivationLink.objects.get(pk=1).expired(),
            True
        )

class TestSendEmailRequest(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        User().objects.create(username="test", password="12345667")
    
    def setUp(self) -> None:
        user = User().objects.first()
        x = SendEmailRequest(user=user, last_request=timezone.datetime(2021, 11, 1, 15, 54, 7))
        x.save()

    def test_is_still_soon(self):
        x = SendEmailRequest.objects.get(pk=1)
        self.assertEqual(True, x.is_still_soon())
        
    
    
