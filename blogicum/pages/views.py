from django.http.response import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView


class AboutTemplateView(TemplateView):
    template_name = 'pages/about.html'


class RulesTemplateView(TemplateView):
    template_name = 'pages/rules.html'


def page_not_found(request, exception) -> HttpResponse:
    return render(request, 'pages/404.html', status=404)


def csfr_failure(request, reason='') -> HttpResponse:
    return render(request, 'pages/403csrf.html', status=403)


def permissions_denied(request, exception) -> HttpResponse:
    return render(request, 'pages/403csrf.html', status=403)


def server_error(request, reason='') -> HttpResponse:
    return render(request, 'pages/500.html', status=500)
