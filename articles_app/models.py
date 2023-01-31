from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import UnicodeUsernameValidator
from collections.abc import Iterable


class CustomUserManager(BaseUserManager):
    def create(self, email, password, username='', role=None, subscribers=None):
        kwargs = {
            'email': self.normalize_email(email).lower(),
            'username': username
        }

        if subscribers and not isinstance(subscribers, Iterable):
            raise ValueError('Subscribers must be iterable.')

        if isinstance(subscribers, Iterable):
            kwargs['subscribers'] = subscribers

        if role is not None:
            if role not in (self.model.SUBSCRIBER, self.model.AUTHOR):
                raise ValueError('Role can be only subscriber or author.')
            kwargs['role'] = role

        user = self.model(**kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, username, password):
        user = self.model(
            email=self.normalize_email(email).lower(),
            username=username, password=password,
        )
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.model(
            email=self.normalize_email(email).lower(),
            username=username, password=password,
            is_staff=True, is_superuser=True
        )
        user.save(using=self._db)
        return user


class CustomUser(AbstractUser):
    SUBSCRIBER = 1
    AUTHOR = 2

    ROLE_CHOICES = (
        (SUBSCRIBER, 'Subscriber'),
        (AUTHOR, 'Author'),
    )
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _("username"),
        max_length=150,
        blank=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={
            "unique": _("A user with that email already exists."),
        }
    )
    password = models.CharField(
        _("password"),
        max_length=128,
        help_text=_(
            "At least 8 characters, can’t be a commonly, "
            "can’t be entirely numeric, can’t be entirely alphabetic."
        )
    )

    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, default=SUBSCRIBER)
    subscribers = models.ManyToManyField('CustomUser', related_name='subscriptions', blank=True)

    objects = CustomUserManager()
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'password')


class Article(models.Model):
    author = models.ForeignKey(CustomUser, related_name='articles', on_delete=models.CASCADE)
    title = models.CharField(max_length=500)
    text = models.TextField()
    public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.pk}. {self.author.email}. {self.title}.'
