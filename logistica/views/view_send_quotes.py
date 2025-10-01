from django.shortcuts import render, redirect
from django.contrib import messages
from utils.request import RequestClient
from setup.local_settings import STOCK_API_URL


def send_quotes(request):
    if "enviar_cotacao" in request.POST:
        pass
