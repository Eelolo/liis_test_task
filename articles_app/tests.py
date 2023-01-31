from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from articles_app.models import Article
import base64

## users
# create
#     can only not authenticated users
#     using email for user registration
#     password cant be entire numeric or alphabetic, longer than 8 characters
#     email must be unique and match mask
#     created user must be with role "subscriber"
# list
#     always allowed
# retrieve
#     always allowed
# update, partial_update
#     update user can only himself
#     user cannot update their role
#     author cant change their subscribers
#     updated email and password must be valid
# destroy
#     user can delete only himself
# subscribe
#     subscribe can only authenticated user
#     subscribe can only user with role "subscriber"
#     subscribe can only to user with role "author"
#     user can subscribe only to author not from user subscriptions
# unsubscribe
#     unsubscribe can only subscribed user
#     unsubscribe can only user with role "subscriber"
#     unsubscribe can only from user with role "author"
#     user can unsubscribe only from author that user already subscribe

## articles
# create
#     user can create article only with role "author"
#     article must be with correct author
# retrieve, list
#     not authenticated user can read only public articles
#     authenticated users can read public articles and articles from subscriptions
# update, partial_update
#     update article can only article author
#     article must be with correct author
# destroy
#     delete article can only article author


User = get_user_model()


class ViewsTest(TestCase):
    def encode_credentials(self, email, password):
        return f'Basic {base64.b64encode(f"{email}:{password}".encode()).decode()}'

    def test_users_create(self):
        client = Client()

        email = 'test@test.com'
        password = 'testpassword123'

        ## create only for unauthorised users / email for registration and authorisation
        response = client.post(
            reverse('articles_app:users-list'),
            data={'email': email, 'password': password}
        )
        # unauthorised -> created
        self.assertEqual(response.status_code, 201)

        response = client.post(
            reverse('articles_app:users-list'),
            HTTP_AUTHORIZATION=self.encode_credentials(email, password)
        )
        # authorised -> forbidden
        self.assertEqual(response.status_code, 403)

        ## email must be unique and match mask
        response = client.post(
            reverse('articles_app:users-list'),
            data={'email': email, 'password': password}
        )
        # does not unique -> bad request
        self.assertEqual(response.status_code, 400)

        wrong_email = 'test.com'
        response = client.post(
            reverse('articles_app:users-list'),
            data={'email': wrong_email, 'password': password}
        )
        # does not match mask -> bad request
        self.assertEqual(response.status_code, 400)

        ## password cant be entire numeric or alphabetic, longer than 8 characters
        email_1 = '1test@test.com'
        response = client.post(
            reverse('articles_app:users-list'),
            data={'email': email_1, 'password': password}
        )
        # valid password -> created
        self.assertEqual(response.status_code, 201)

        email_2 = '2test@test.com'
        alphabetic_password = 'testpassword'
        response = client.post(
            reverse('articles_app:users-list'),
            data={'email': email_2, 'password': alphabetic_password}
        )
        # entirely alphabetic password -> bad request
        self.assertEqual(response.status_code, 400)

        email_3 = '3test@test.com'
        numeric_password = 5636764786875
        response = client.post(
            reverse('articles_app:users-list'),
            data={'email': email_3, 'password': numeric_password}
        )
        # entirely numeric password -> bad request
        self.assertEqual(response.status_code, 400)

        email_4 = '4test@test.com'
        short_password = 'fgh365'
        response = client.post(
            reverse('articles_app:users-list'),
            data={'email': email_4, 'password': short_password}
        )
        # shorter than 8 characters -> bad request
        self.assertEqual(response.status_code, 400)

        ## created user with role "subscriber"
        email_5 = '5test@test.com'
        response = client.post(
            reverse('articles_app:users-list'),
            data={'email': email_5, 'password': password}
        )
        # created user with role "subscriber"
        self.assertEqual(User.objects.get(email=email_5).role, User.SUBSCRIBER)

        User.objects.all().delete()

    def test_users_update(self):
        client = Client()
        password = 'testpassword123'

        ## update only for authenticated users
        email = 'test@test.com'
        user = User.objects.create(
            email=email, password=password
        )
        response = client.patch(
            reverse('articles_app:users-detail', kwargs={'pk': user.pk}),
        )
        # without credentials -> not authenticated
        self.assertEqual(response.status_code, 401)

        ## user can update only himself
        email_1 = '1test@test.com'
        user_1 = User.objects.create(
            email=email_1, password=password
        )
        email_2 = '2test@test.com'
        user_2 = User.objects.create(
            email=email_2, password=password
        )
        response = client.patch(
            reverse('articles_app:users-detail', kwargs={'pk': user_2.pk}),
            HTTP_AUTHORIZATION=self.encode_credentials(email_1, password)
        )
        # update another user -> forbidden
        self.assertEqual(response.status_code, 403)

        email_3 = '3test@test.com'
        user_3 = User.objects.create(
            email=email_3, password=password
        )
        response = client.patch(
            reverse('articles_app:users-detail', kwargs={'pk': user_3.pk}),
            HTTP_AUTHORIZATION=self.encode_credentials(email_3, password),
            data={'username': 'test_username'}, content_type='application/json'
        )
        # update himself -> success
        self.assertEqual(response.status_code, 200)

        ## user cannot update their role
        email_4 = '4test@test.com'
        user_4 = User.objects.create(
            email=email_4, password=password
        )
        response = client.patch(
            reverse('articles_app:users-detail', kwargs={'pk': user_4.pk}),
            HTTP_AUTHORIZATION=self.encode_credentials(email_4, password),
            content_type='application/json', data={'role': User.AUTHOR}
        )
        # does not updated
        self.assertEqual(User.objects.get(email=email_3).role, User.SUBSCRIBER)

        ## author cannot update their subscribers
        email_5 = '5test@test.com'
        user_5 = User.objects.create(
            email=email_5, password=password
        )
        user_5.role = User.AUTHOR
        user_5.save()

        email_6 = '6test@test.com'
        user_6 = User.objects.create(
            email=email_6, password=password
        )
        user_5.subscribers.add(user_6)

        response = client.patch(
            reverse('articles_app:users-detail', kwargs={'pk': user_5.pk}),
            HTTP_AUTHORIZATION=self.encode_credentials(email_5, password),
            content_type='application/json', data={'subscribers': []}
        )
        # author try change their subscribers -> bad request
        self.assertEqual(response.status_code, 400)

        ## valid email and password for update
        email_7 = '7test@test.com'
        user_7 = User.objects.create(
            email=email_7, password=password
        )
        invalid_password = 'password'
        invalid_email = 'test.com'
        response = client.patch(
            reverse('articles_app:users-detail', kwargs={'pk': user_7.pk}),
            HTTP_AUTHORIZATION=self.encode_credentials(email_7, password),
            content_type='application/json', data={'password': invalid_password}
        )
        # invalid password -> bad request
        self.assertEqual(response.status_code, 400)
        response = client.patch(
            reverse('articles_app:users-detail', kwargs={'pk': user_7.pk}),
            HTTP_AUTHORIZATION=self.encode_credentials(email_7, password),
            content_type='application/json', data={'email': invalid_email}
        )
        # invalid email -> bad request
        self.assertEqual(response.status_code, 400)

        User.objects.all().delete()

    def test_users_delete(self):
        client = Client()
        password = 'testpassword123'

        ## delete only for authenticated users
        email = 'test@test.com'
        user = User.objects.create(
            email=email, password=password
        )
        response = client.delete(
            reverse('articles_app:users-detail', kwargs={'pk': user.pk}),
        )
        # without credentials -> not authenticated
        self.assertEqual(response.status_code, 401)

        ## user can delete only himself
        email_1 = '1test@test.com'
        user_1 = User.objects.create(
            email=email_1, password=password
        )
        email_2 = '2test@test.com'
        user_2 = User.objects.create(
            email=email_2, password=password
        )
        response = client.delete(
            reverse('articles_app:users-detail', kwargs={'pk': user_2.pk}),
            HTTP_AUTHORIZATION=self.encode_credentials(email_1, password)
        )
        # delete other user -> forbidden
        self.assertEqual(response.status_code, 403)

        response = client.delete(
            reverse('articles_app:users-detail', kwargs={'pk': user_1.pk}),
            HTTP_AUTHORIZATION=self.encode_credentials(email_1, password)
        )
        # delete himself -> no content
        self.assertEqual(response.status_code, 204)

        User.objects.all().delete()

    def test_articles_create(self):
        client = Client()

        email = 'test@test.com'
        password = 'testpassword123'

        ## create articles only for authenticated users
        response = client.post(reverse('articles_app:articles-list'))
        # without credentials -> unauthorised
        self.assertEqual(response.status_code, 401)

        ## create articles only for authors
        user = User.objects.create(
            email=email, password=password
        )
        response = client.post(
            reverse('articles_app:articles-list'),
            data={
                'author': user.pk, 'title': 'test_title',
                'text': 'test_text', 'public': True
            },
            HTTP_AUTHORIZATION=self.encode_credentials(email, password)
        )
        # user with role "subscriber" -> forbidden
        self.assertEqual(response.status_code, 403)

        user.role = User.AUTHOR
        user.save()
        response = client.post(
            reverse('articles_app:articles-list'),
            data={
                'author': user.pk, 'title': 'test_title',
                'text': 'test_text', 'public': True
            },
            HTTP_AUTHORIZATION=self.encode_credentials(email, password)
        )
        # user with role "author" -> created
        self.assertEqual(response.status_code, 201)

        ## only correct author of article
        email_1 = '1test@test.com'
        user_1 = User.objects.create(
            email=email_1, password=password
        )
        user_1.role = User.AUTHOR
        user_1.save()
        response = client.post(
            reverse('articles_app:articles-list'),
            data={
                'author': user_1.pk, 'title': 'test_title',
                'text': 'test_text', 'public': True
            },
            HTTP_AUTHORIZATION=self.encode_credentials(email, password)
        )
        # wrong author -> bad request
        self.assertEqual(response.status_code, 400)

        User.objects.all().delete()
        Article.objects.all().delete()

    def test_articles_read(self):
        client = Client()

        password = 'testpassword123'

        email = 'test@test.com'
        user = User.objects.create(
            email=email, password=password
        )
        user.role = User.AUTHOR
        user.save()

        email_1 = '1test@test.com'
        user_1 = User.objects.create(
            email=email_1, password=password
        )
        user_1.role = User.AUTHOR
        user_1.save()

        email_2 = '2test@test.com'
        user_2 = User.objects.create(
            email=email_2, password=password
        )
        user_1.subscribers.add(user_2)

        public_article_of_user = Article.objects.create(
            author=user, title='test_title',
            text='test_text', public=True
        )
        public_article_of_user_1 = Article.objects.create(
            author=user_1, title='test_title',
            text='test_text', public=True
        )
        private_article_of_user = Article.objects.create(
            author=user, title='test_title',
            text='test_text', public=False
        )
        private_article_of_user_1 = Article.objects.create(
            author=user_1, title='test_title',
            text='test_text', public=False
        )

        ## unauthorized user can read only public articles
        response = client.get(
            reverse('articles_app:articles-list'),
        )
        for article in response.data:
            # articles from response only public
            self.assertTrue(article['public'])

        response = client.get(reverse(
            'articles_app:articles-detail',
            kwargs={'pk': private_article_of_user.pk}
        ))
        response_1 = client.get(reverse(
            'articles_app:articles-detail',
            kwargs={'pk': private_article_of_user_1.pk}
        ))
        # private articles -> not found
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_1.status_code, 404)

        ## authorized user can read public articles and private articles from their subscriptions
        response = client.get(
            reverse('articles_app:articles-list'),
            HTTP_AUTHORIZATION=self.encode_credentials(email_2, password)
        )
        response_articles = {article['id'] for article in response.data}
        correct_articles = {
            public_article_of_user.pk, public_article_of_user_1.pk,
            private_article_of_user_1.pk
        }
        # response articles equal correct articles
        self.assertSetEqual(response_articles, correct_articles)

        response = client.get(
            reverse('articles_app:articles-detail', kwargs={'pk': private_article_of_user.pk}),
            HTTP_AUTHORIZATION=self.encode_credentials(email_2, password)
        )
        response_1 = client.get(
            reverse('articles_app:articles-detail', kwargs={'pk': private_article_of_user_1.pk}),
            HTTP_AUTHORIZATION=self.encode_credentials(email_2, password)
        )
        # private article not from subscriptions -> not found
        self.assertEqual(response.status_code, 404)
        # article from subscriptions -> success
        self.assertEqual(response_1.status_code, 200)

        User.objects.all().delete()
        Article.objects.all().delete()

    def test_articles_update(self):
        client = Client()

        password = 'testpassword123'

        email = 'test@test.com'
        user = User.objects.create(
            email=email, password=password
        )
        user.role = User.AUTHOR
        user.save()
        article = Article.objects.create(
            author=user, title='test_title',
            text='test_text', public=True
        )
        email_1 = '1test@test.com'
        user_1 = User.objects.create(
            email=email_1, password=password
        )
        user.role = User.AUTHOR
        user.save()

        ## Only author of article can update article
        response = client.patch(
            reverse('articles_app:articles-detail', kwargs={'pk': article.pk}),
            HTTP_AUTHORIZATION=self.encode_credentials(email_1, password)
        )
        # user is not author of article -> forbidden
        self.assertEqual(response.status_code, 403)

        ## Cannot set wrong author
        response = client.patch(
            reverse('articles_app:articles-detail', kwargs={'pk': article.pk}),
            HTTP_AUTHORIZATION=self.encode_credentials(email, password),
            data={'author': user_1.pk}, content_type='application/json'
        )
        # wrong author -> bad request
        self.assertEqual(response.status_code, 400)

        User.objects.all().delete()
        Article.objects.all().delete()

    def test_articles_delete(self):
        client = Client()

        password = 'testpassword123'

        email = 'test@test.com'
        user = User.objects.create(
            email=email, password=password
        )
        user.role = User.AUTHOR
        user.save()
        article = Article.objects.create(
            author=user, title='test_title',
            text='test_text', public=True
        )
        email_1 = '1test@test.com'
        user_1 = User.objects.create(
            email=email_1, password=password
        )
        user.role = User.AUTHOR
        user.save()

        ## Only author of article can delete article
        response = client.delete(
            reverse('articles_app:articles-detail', kwargs={'pk': article.pk}),
            HTTP_AUTHORIZATION=self.encode_credentials(email_1, password)
        )
        # user is not author of article -> forbidden
        self.assertEqual(response.status_code, 403)

        response = client.delete(
            reverse('articles_app:articles-detail', kwargs={'pk': article.pk}),
            HTTP_AUTHORIZATION=self.encode_credentials(email, password)
        )
        # correct author -> no content
        self.assertEqual(response.status_code, 204)

    def test_subscribe(self):
        client = Client()
        password = 'testpassword123'

        email = 'test@test.com'
        email_1 = '1test@test.com'
        user = User.objects.create(
            email=email, password=password,
            role=User.AUTHOR
        )
        user_1 = User.objects.create(
            email=email_1, password=password,
            role=User.SUBSCRIBER
        )

        ## subscribe only for authenticated users
        response = client.get(
            reverse('articles_app:users-subscribe', kwargs={'pk': user.pk}),
        )
        # without credentials -> unauthorised
        self.assertEqual(response.status_code, 401)

        response = client.get(
            reverse('articles_app:users-subscribe', kwargs={'pk': user.pk}),
            HTTP_AUTHORIZATION=self.encode_credentials(email_1, password)
        )
        # authenticated -> success
        self.assertEqual(response.status_code, 200)

        ## can subscribe user only with role "subscriber"
        email_2 = '2test@test.com'
        user_2 = User.objects.create(
            email=email_2, password=password,
            role=User.AUTHOR
        )
        response = client.get(
            reverse('articles_app:users-subscribe', kwargs={'pk': user_2.pk}),
            HTTP_AUTHORIZATION=self.encode_credentials(user, password)
        )
        # user with role "subscriber" -> forbidden
        self.assertEqual(response.status_code, 403)

        ## can subscribe only to user with role "author"
        email_3 = '3test@test.com'
        user_3 = User.objects.create(
            email=email_3, password=password,
            role=User.SUBSCRIBER
        )
        response = client.get(
            reverse('articles_app:users-subscribe', kwargs={'pk': user_1.pk}),
            HTTP_AUTHORIZATION=self.encode_credentials(email_3, password)
        )
        # both users with role "subscriber" -> forbidden
        self.assertEqual(response.status_code, 403)

        ## can subscribe only if not subscribed yet
        email_4 = '4test@test.com'
        user_4 = User.objects.create(
            email=email_4, password=password,
            role=User.AUTHOR
        )
        email_5 = '5test@test.com'
        user_5 = User.objects.create(
            email=email_5, password=password,
            role=User.SUBSCRIBER
        )
        user_4.subscribers.add(user_5)
        response = client.get(
            reverse('articles_app:users-subscribe', kwargs={'pk': user_4.pk}),
            HTTP_AUTHORIZATION=self.encode_credentials(email_5, password)
        )
        # user already subscribed -> forbidden
        self.assertEqual(response.status_code, 403)

    def test_unsubscribe(self):
        client = Client()
        password = 'testpassword123'

        email = 'test@test.com'
        email_1 = '1test@test.com'
        user = User.objects.create(
            email=email, password=password,
            role=User.AUTHOR
        )
        user_1 = User.objects.create(
            email=email_1, password=password,
            role=User.SUBSCRIBER
        )
        user.subscribers.add(user_1)

        ## unsubscribe only for authenticated users / unsubscribe can only subscribed user
        response = client.get(
            reverse('articles_app:users-unsubscribe', kwargs={'pk': user.pk}),
        )
        # without credentials -> unauthorised
        self.assertEqual(response.status_code, 401)

        response = client.get(
            reverse('articles_app:users-unsubscribe', kwargs={'pk': user.pk}),
            HTTP_AUTHORIZATION=self.encode_credentials(email_1, password)
        )
        # authenticated / already subscribed -> success
        self.assertEqual(response.status_code, 200)

        response = client.get(
            reverse('articles_app:users-unsubscribe', kwargs={'pk': user.pk}),
            HTTP_AUTHORIZATION=self.encode_credentials(email_1, password)
        )
        # not subscribed already -> forbidden
        self.assertEqual(response.status_code, 403)

        ## cant unsubscribe from user whith role "subscriber"
        email_2 = '2test@test.com'
        user_2 = User.objects.create(
            email=email_2, password=password,
            role=User.SUBSCRIBER
        )
        email_3 = '3test@test.com'
        user_3 = User.objects.create(
            email=email_3, password=password,
            role=User.SUBSCRIBER
        )
        response = client.get(
            reverse('articles_app:users-unsubscribe', kwargs={'pk': user_2.pk}),
            HTTP_AUTHORIZATION=self.encode_credentials(email_3, password)
        )
        # both users with role "subscriber" -> forbidden
        self.assertEqual(response.status_code, 403)

        ## cant unsubscribe from user whith role "author"
        email_4 = '4test@test.com'
        user_5 = User.objects.create(
            email=email_4, password=password,
            role=User.AUTHOR
        )
        # user with role "author" -> forbidden
        self.assertEqual(response.status_code, 403)
