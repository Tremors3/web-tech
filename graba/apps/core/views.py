from django.views.generic import ListView
from django.db.models import Q


from auctions.models import Auction, Category
from favorites.models import FavoriteAuction


class HomePageView(ListView):
    model = Auction
    template_name = 'core/index.html'
    context_object_name = 'auctions'
    paginate_by = 15

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q', '')
        c = self.request.GET.get('c', '')

        if q:
            queryset = queryset.filter(title__icontains=q) | \
            queryset.filter(description__icontains=q)

        if c and c != "ALL":
            queryset = queryset.filter(category__name=c)

        return queryset

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)

        # Copy GET and remove 'page'
        params = self.request.GET.copy()
        params._mutable = True
        params.pop('page', None)

        # Querystring clear for pagination
        context['querystring'] = params.urlencode()
        
        # Add favorites to context ONLY if user is authenticated
        context['user_favorites'] = set(
            FavoriteAuction.objects.filter(user=self.request.user)
            .values_list('auction_id', flat=True)
        ) if self.request.user.is_authenticated else set()
        
        # Add categories and subcategories to the context
        context["categories"] = (
            Category.objects
            .filter(level=1)
            .prefetch_related("subcategories")
        )

        return context
