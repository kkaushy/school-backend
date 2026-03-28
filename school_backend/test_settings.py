from school_backend.settings import *  # noqa: F401, F403


class PassThroughAuthentication:
    """
    Test authentication backend that returns the user already set on the
    underlying Django request (e.g. a MagicMock set by a test), instead of
    running real JWT validation.
    """

    def authenticate(self, request):
        user = request._request.user
        if user is not None and getattr(user, 'is_authenticated', False):
            return (user, None)
        return None


REST_FRAMEWORK = {
    **REST_FRAMEWORK,  # noqa: F405
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'school_backend.test_settings.PassThroughAuthentication',
    ],
}
