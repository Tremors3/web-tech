from django.views.generic import ListView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render
from django.utils.http import urlencode
from django.db.models import Q
from auctions.models import Auction


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

        # if c:
        #     queryset = queryset.filter(category=c)

        return queryset

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)

        # Copy GET and remove 'page'
        params = self.request.GET.copy()
        params._mutable = True
        params.pop('page', None)

        # Querystring clear for pagination
        context['querystring'] = params.urlencode()

        return context
