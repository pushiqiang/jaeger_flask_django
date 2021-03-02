# -*- coding: utf-8 -*-
from django.shortcuts import HttpResponse
from django.views import View


class TestView(View):
    def get(self, request, *args, **kwargs):

        return HttpResponse('good')
