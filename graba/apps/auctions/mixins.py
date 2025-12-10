from django.core.exceptions import PermissionDenied

class SellerRequiredMixin:
    
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            raise PermissionDenied("You must be authenticated to create an auction.")
        
        if not user.has_role("SELLER"):
            raise PermissionDenied("Only sellers can create an auction.")
        
        return super().dispatch(request, *args, **kwargs)
