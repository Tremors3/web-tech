from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect


class RedirectAuthenticatedUserMixin(AccessMixin):
    """Redirects authenticated users away from certain views."""
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('core:home')
        return super().dispatch(request, *args, **kwargs)