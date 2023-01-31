from rest_framework import permissions
from articles_app.models import CustomUser


class UserPermission(permissions.BasePermission):
    def has_subscribe_permission(self, subscriber, author):
        if author.role != CustomUser.AUTHOR or \
                subscriber.role != CustomUser.SUBSCRIBER or \
                author in subscriber.subscriptions.all() or \
                author == subscriber:
            return False

        return True

    def has_unsubscribe_permission(self, subscriber, author):
        if subscriber.role != CustomUser.SUBSCRIBER or \
                author.role != CustomUser.AUTHOR or \
                author not in subscriber.subscriptions.all():
            return False

        return True

    def has_permission(self, request, view):
        if view.action == 'create':
            return not request.user.is_authenticated or request.user.is_superuser

        return True

    def has_object_permission(self, request, view, obj):
        if view.action == 'retrieve':
            return True

        if not request.user.is_authenticated:
            return False

        if view.action in ('update', 'partial_update', 'destroy'):
            return obj == request.user or request.user.is_superuser
        elif view.action == 'subscribe':
            return self.has_subscribe_permission(request.user, obj)
        elif view.action == 'unsubscribe':
            return self.has_unsubscribe_permission(request.user, obj)


class ArticlePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == 'create' and not request.user.is_authenticated:
            return False

        if view.action == 'create':
            return request.user.role == CustomUser.AUTHOR or request.user.is_superuser

        return True

    def has_object_permission(self, request, view, obj):
        if view.action == 'retrieve' and obj.public:
            return True

        if not request.user.is_authenticated:
            return False

        if view.action == 'retrieve':
            return request.user in obj.author.subscribers.all()
        elif view.action in ('update', 'partial_update', 'destroy'):
            return obj.author == request.user or request.user.is_superuser
