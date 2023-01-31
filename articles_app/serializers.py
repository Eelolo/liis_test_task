from rest_framework import serializers
from articles_app.models import CustomUser, Article
from django.contrib.auth.password_validation import validate_password


class CreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True, validators=[validate_password])

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password']


class UpdateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True, validators=[validate_password])

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'password',
            'role', 'articles', 'subscribers'
        ]

    def validate(self, attrs):
        if 'role' in attrs and not self.context['request'].user.is_superuser:
            raise serializers.ValidationError('Only admin can update user role.')

        if 'subscribers' in attrs and not self.context['request'].user.is_superuser:
            raise serializers.ValidationError('Only admin can update user subscribers.')

        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email',
            'role', 'articles', 'subscribers'
        ]


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = [
            'id', 'author', 'title', 'text',
            'public', 'created_at', 'updated_at'
        ]

    def validate(self, attrs):
        if 'author' in attrs and not self.context['request'].user.is_superuser:
            raise serializers.ValidationError('Only admin can change article author.')
        return attrs


class CreateArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'author', 'title', 'text', 'public']

    def validate(self, attrs):
        if self.context['request'].user != attrs['author'] and \
                not self.context['request'].user.is_superuser:
            raise serializers.ValidationError('Invalid article author.')
        return attrs
