from arkav.mainevent.models import Registrant
from datetime import datetime
from datetime import timedelta
from django.db.models import Count


def delete_inactive_registrants():
    yesterday = datetime.now() - timedelta(days=1)
    inactive_registrants = Registrant.objects \
        .annotate(task_responses_count=Count('task_responses')) \
        .filter(task_responses_count=0, created_at__lte=yesterday)
    inactive_registrants.delete()
