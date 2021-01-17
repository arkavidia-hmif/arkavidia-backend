from arkav.mainevent.models import Registrant
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.db.models import Count
from django.utils import timezone

class Command(BaseCommand):
    help = 'Delete registrants that are created before 1 day ago'

    def handle(self, *args, **kwargs):
        yesterday = timezone.now() - timedelta(days=1)
        inactive_registrants = Registrant.objects \
            .annotate(task_responses_count=Count('task_responses')) \
            .filter(task_responses_count=0, created_at__lte=yesterday)
        inactive_registrants.delete()
