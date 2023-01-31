from rest_framework import viewsets, status
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from articles_app.models import CustomUser, Article
from articles_app.serializers import (
    CreateUserSerializer, UpdateUserSerializer, UserSerializer,
    ArticleSerializer, CreateArticleSerializer
)
from articles_app.permissions import UserPermission, ArticlePermission


class UserViewSet(viewsets.ModelViewSet):
    authentication_classes = [BasicAuthentication]
    permission_classes = [UserPermission]
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateUserSerializer
        elif self.request.method == 'PATCH':
            return UpdateUserSerializer

        return self.serializer_class

    @action(detail=True, methods=['get'])
    def subscribe(self, request, pk=None):
        author = self.get_object()
        subscriber = self.request.user

        author.subscribers.add(subscriber)

        return Response(
            status=status.HTTP_200_OK,
            data={'detail': 'Subscription success.'}
        )

    @action(detail=True, methods=['get'])
    def unsubscribe(self, request, pk=None):
        author = self.get_object()
        subscriber = self.request.user

        author.subscribers.remove(subscriber)

        return Response(
            status=status.HTTP_200_OK,
            data={'detail': 'Unsubscription success.'}
        )


class ArticleViewSet(viewsets.ModelViewSet):
    authentication_classes = [BasicAuthentication]
    permission_classes = [ArticlePermission]
    serializer_class = ArticleSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Article.objects.filter(
                Q(public=True) | Q(author__in=self.request.user.subscriptions.all())
            )

        return Article.objects.filter(public=True)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateArticleSerializer

        return self.serializer_class
