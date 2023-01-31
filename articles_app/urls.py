from django.urls import path
from articles_app.views import UserViewSet, ArticleViewSet


app_name = 'articles_app'


methods = {'get': 'list', 'post': 'create'}
pk_methods = {'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}


urlpatterns = [
    path('users/', UserViewSet.as_view(methods), name='users-list'),
    path('users/<int:pk>/', UserViewSet.as_view(pk_methods), name='users-detail'),
    path('users/subscribe/<int:pk>/', UserViewSet.as_view({'get': 'subscribe'}), name='users-subscribe'),
    path('users/unsubscribe/<int:pk>/', UserViewSet.as_view({'get': 'unsubscribe'}), name='users-unsubscribe'),
    path('articles/', ArticleViewSet.as_view(methods), name='articles-list'),
    path('articles/<int:pk>/', ArticleViewSet.as_view(pk_methods), name='articles-detail')
]
