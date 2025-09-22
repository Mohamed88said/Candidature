from django.core.management.base import BaseCommand
from apps.jobs.models import Job
from django.utils.text import slugify
import uuid

class Command(BaseCommand):
    help = 'Corriger les slugs invalides des jobs'

    def handle(self, *args, **options):
        jobs = Job.objects.all()
        for job in jobs:
            if not job.slug or job.slug.startswith('company-') or job.slug.startswith('ccccccccc-'):
                base_slug = slugify(job.title)
                if not base_slug:
                    base_slug = "offre-emploi"
                job.slug = f"{base_slug}-{str(uuid.uuid4())[:8]}"
                job.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Slug corrigé pour {job.title}: {job.slug}')
                )
