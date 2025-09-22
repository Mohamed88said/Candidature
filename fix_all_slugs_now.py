import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recruitment_platform.settings')
django.setup()

from django.utils.text import slugify
from apps.jobs.models import Job
import uuid

def fix_all_slugs():
    print("🔧 Correction de TOUS les slugs...")
    
    for job in Job.objects.all():
        print(f"\nTraitement: {job.title}")
        print(f"Slug actuel: {job.slug}")
        
        # Générer un nouveau slug basé sur le titre
        base_slug = slugify(job.title)
        if not base_slug:
            base_slug = "offre-emploi"
            print("⚠️  Titre vide, utilisation de 'offre-emploi'")
        
        if len(base_slug) > 50:
            base_slug = base_slug[:50]
        
        new_slug = f"{base_slug}-{str(uuid.uuid4())[:8]}"
        print(f"Nouveau slug généré: {new_slug}")
        
        # Vérifier l'unicité
        counter = 1
        original_slug = new_slug
        while Job.objects.filter(slug=new_slug).exclude(id=job.id).exists():
            new_slug = f"{original_slug}-{counter}"
            print(f"⚡ Slug existe, nouvelle tentative: {new_slug}")
            counter += 1
            if counter > 5:
                break
        
        job.slug = new_slug
        job.save()
        print(f"✅ Sauvegardé: {new_slug}")

if __name__ == "__main__":
    fix_all_slugs()
    print("\n🎯 Tous les slugs ont été corrigés!")
