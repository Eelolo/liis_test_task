from django.forms import ValidationError


class CharacterPasswordValidator:
    def validate(self, password, user=None):
        if password.isalpha():
            raise ValidationError('This password is entirely alphabetic.')

    def get_help_text(self):
        return 'Your password can’t be entirely alphabetic.'
