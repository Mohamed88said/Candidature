from django.core.management.base import BaseCommand
from apps.core.models import PageContent, SiteSettings


class Command(BaseCommand):
    help = 'Configure le contenu initial des pages'

    def handle(self, *args, **options):
        # CrÃ©er le contenu de la page ÃGNF propos
        about_content = """
        <h2>Notre Mission</h2>
        <p>Nous connectons les talents aux opportunités depuis plus de 10 ans, en révolutionnant le processus de recrutement grâce à la technologie.</p>
        
        <h2>Notre Vision</h2>
        <p>Devenir la plateforme de référence pour le recrutement en France, en offrant une expérience exceptionnelle aux candidats et aux recruteurs.</p>
        
        <h2>Nos Valeurs</h2>
        <ul>
            <li><strong>Transparence :</strong> Communication claire et honnête</li>
            <li><strong>Innovation :</strong> Technologies de pointe</li>
            <li><strong>Équité :</strong> Égalité des chances pour tous</li>
            <li><strong>Excellence :</strong> Service de qualité supérieure</li>
        </ul>
        """
        
        PageContent.objects.update_or_create(
            page_type='about',
            defaults={
                'title': 'À propos de RecrutementPro',
                'content': about_content,
                'is_active': True,
                'show_in_menu': True,
                'order': 1,
                'slug': 'a-propos'
            }
        )

        # CrÃ©er le contenu de la politique de confidentialitÃ©
        privacy_content = """
        <h2>1. Responsable du traitement</h2>
        <p>Le responsable du traitement de vos données personnelles est RecrutementPro SAS.</p>
        
        <h2>2. Données collectées</h2>
        <p>Nous collectons les données suivantes :</p>
        <ul>
            <li>Données d'identification (nom, prénom, email)</li>
            <li>Données professionnelles (CV, expériences)</li>
            <li>Données techniques (IP, cookies)</li>
        </ul>
        
        <h2>3. Finalités du traitement</h2>
        <p>Vos données sont utilisées pour :</p>
        <ul>
            <li>Gestion de votre compte</li>
            <li>Mise en relation avec les employeurs</li>
            <li>Amélioration de nos services</li>
            <li>Communications importantes</li>
        </ul>
        
        <h2>4. Vos droits</h2>
        <p>Vous disposez des droits suivants :</p>
        <ul>
            <li>Droit d'accès à vos données</li>
            <li>Droit de rectification</li>
            <li>Droit d'effacement</li>
            <li>Droit à la portabilité</li>
        </ul>
        
        <h2>5. Contact</h2>
        <p>Pour exercer vos droits : privacy@recrutementpro.com</p>
        """
        
        PageContent.objects.update_or_create(
            page_type='privacy',
            defaults={
                'title': 'Politique de confidentialité',
                'content': privacy_content,
                'is_active': True,
                'show_in_menu': True,
                'order': 2,
                'slug': 'politique-confidentialite'
            }
        )

        # CrÃ©er le contenu des conditions d'utilisation
        terms_content = """
        <h2>1. Acceptation des conditions</h2>
        <p>En utilisant cette plateforme, vous acceptez ces conditions d'utilisation.</p>
        
        <h2>2. Description du service</h2>
        <p>Notre plateforme met en relation candidats et employeurs pour faciliter le recrutement.</p>
        
        <h2>3. Inscription et compte</h2>
        <p>Vous devez :</p>
        <ul>
            <li>Être âgé d'au moins 16 ans</li>
            <li>Fournir des informations exactes</li>
            <li>Maintenir la sécurité de votre compte</li>
        </ul>
        
        <h2>4. Utilisation acceptable</h2>
        <p>Il est interdit de :</p>
        <ul>
            <li>Publier du contenu faux ou illégal</li>
            <li>Harceler d'autres utilisateurs</li>
            <li>Utiliser le service pour du spam</li>
        </ul>
        
        <h2>5. Résiliation</h2>
        <p>Nous pouvons suspendre votre compte en cas de violation de ces conditions.</p>
        
        <h2>6. Contact</h2>
        <p>Pour toute question : legal@recrutementpro.com</p>
        """
        
        PageContent.objects.update_or_create(
            page_type='terms',
            defaults={
                'title': 'Conditions d\'utilisation',
                'content': terms_content,
                'is_active': True,
                'show_in_menu': True,
                'order': 3,
                'slug': 'conditions-utilisation'
            }
        )

        self.stdout.write(
            self.style.SUCCESS('Contenu initial des pages créé avec succès!')
        )

