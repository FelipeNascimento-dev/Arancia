from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def print_serial(request, serial):
    return render(
        request,
        "logistica/templates_checkin_checkout/print_serial.html",
        {
            "serial": serial
        }
    )
