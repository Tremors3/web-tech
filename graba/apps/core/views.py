from django.shortcuts import render


def home(request):
    return render(request, template_name='base/style_one_with_cards.html', context={})