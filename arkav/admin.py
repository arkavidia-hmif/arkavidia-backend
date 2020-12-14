from django.contrib import admin
from django.shortcuts import render
from arkav.utils.services import UtilityService
import django_rq


_admin_site_get_urls = admin.site.get_urls


def send_custom_email_view(request):
    if 'apply' in request.POST:
        addresses = request.POST['to'].splitlines()
        for address in addresses:
            django_rq.enqueue(
                UtilityService().send_custom_email,
                [address],
                request.POST['subject'],
                request.POST['mail_text_message'],
                request.POST['mail_html_message'],
                request.FILES.getlist('attachments')
            )
        context = {
            'addresses': len(addresses)
        }
        return render(request, 'send_custom_email_success.html', context=context)
    return render(request, 'send_custom_email.html')


def get_urls():
    from django.conf.urls import url
    urls = _admin_site_get_urls()
    urls += [
        url(r'^send-email/$', admin.site.admin_view(send_custom_email_view))
    ]
    return urls
