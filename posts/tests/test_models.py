from django.test import TestCase
from posts.models import Post
from django.contrib.auth import get_user_model as User
from django.core.exceptions import ValidationError
from lorem_text import lorem

class TestPost(TestCase):
    
    def setUp(self) -> None:
        x = User().objects.create(username="test", password='1234')
        self.post = Post(
            post_content='test content',
            creator=x,
        )
    
    def test_save_shared_post_with_image(self):
        self.post.shared_post = True
        self.post.image = "/media/default.jpg"
        with self.assertRaises(ValidationError) as error:
            self.post.save()
            self.assertEqual(error.exception.code, "image-shared-post")
    
    def test_save_empty_non_shared_post(self):
        self.post.post_content = ''
        self.post.shared_post = False
        with self.assertRaises(ValidationError) as error:
            self.post.save()
            self.assertEqual(error.exception.code, "shared-post-no-content")
    
    def test_save_not_shared_post_with_reference(self):
        self.post.shared_post = False
        self.post.original_post = self.post
        with self.assertRaises(ValidationError) as error:
            self.post.save()
            self.assertEqual(error.exception.code, "non-shared-post-reference")
    
    def test_save_self_referencing_posts(self):
        self.post.shared_post = True
        self.post.original_post = self.post
        with self.assertRaises(ValidationError) as error:
                self.post.save()
                self.assertEqual(error.exception.code, "self-referencing")
    
    def test_str_(self):
        paragraph = lorem.paragraph()
        self.post.post_content = paragraph

        self.assertEqual(str(self.post), paragraph[0:30] + f'..., Post ID: {self.post.id} for: {self.post.creator}')
