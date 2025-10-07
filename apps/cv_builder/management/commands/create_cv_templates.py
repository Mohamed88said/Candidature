from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from apps.cv_builder.models import CVTemplate, CVTemplateCategory
import os


class Command(BaseCommand):
    help = 'Créer des modèles de CV par défaut'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forcer la création même si les modèles existent déjà',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('📄 Initialisation du constructeur de CV...')
        )
        
        try:
            # Créer les catégories de modèles
            categories = self.create_template_categories(options['force'])
            
            # Créer les modèles de CV
            templates = self.create_cv_templates(options['force'])
            
            self.stdout.write(
                self.style.SUCCESS('\n✅ Initialisation terminée avec succès !')
            )
            self.stdout.write(f"📊 Catégories: {categories}")
            self.stdout.write(f"📊 Modèles: {templates}")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erreur lors de l\'initialisation: {e}')
            )

    def create_template_categories(self, force=False):
        """Créer les catégories de modèles de CV"""
        self.stdout.write("📁 Création des catégories de modèles...")
        
        categories_data = [
            {
                'name': 'Moderne',
                'description': 'Modèles modernes avec un design épuré et contemporain',
                'icon': 'fas fa-rocket',
                'color': '#007bff',
                'is_active': True
            },
            {
                'name': 'Classique',
                'description': 'Modèles classiques et professionnels',
                'icon': 'fas fa-briefcase',
                'color': '#6c757d',
                'is_active': True
            },
            {
                'name': 'Créatif',
                'description': 'Modèles créatifs pour les métiers artistiques',
                'icon': 'fas fa-palette',
                'color': '#e83e8c',
                'is_active': True
            },
            {
                'name': 'Minimaliste',
                'description': 'Modèles minimalistes et épurés',
                'icon': 'fas fa-minus',
                'color': '#28a745',
                'is_active': True
            },
            {
                'name': 'Professionnel',
                'description': 'Modèles professionnels pour le monde de l\'entreprise',
                'icon': 'fas fa-building',
                'color': '#343a40',
                'is_active': True
            },
            {
                'name': 'Académique',
                'description': 'Modèles adaptés au monde académique et de la recherche',
                'icon': 'fas fa-graduation-cap',
                'color': '#17a2b8',
                'is_active': True
            }
        ]
        
        created_count = 0
        for category_data in categories_data:
            category, created = CVTemplateCategory.objects.get_or_create(
                name=category_data['name'],
                defaults=category_data
            )
            if created:
                created_count += 1
                self.stdout.write(f"  ✅ Créé: {category.name}")
            else:
                self.stdout.write(f"  ⚠️  Existe déjà: {category.name}")
        
        self.stdout.write(f"📊 {created_count} nouvelles catégories créées")
        return CVTemplateCategory.objects.count()

    def create_cv_templates(self, force=False):
        """Créer les modèles de CV par défaut"""
        self.stdout.write("\n📄 Création des modèles de CV...")
        
        templates_data = [
            {
                'name': 'Moderne Simple',
                'description': 'Un modèle moderne et épuré avec une mise en page claire',
                'category': 'modern',
                'sections': ['personal_info', 'professional_summary', 'experience', 'education', 'skills', 'languages'],
                'layout_config': {
                    'header_style': 'centered',
                    'section_spacing': 'medium',
                    'font_family': 'Arial, sans-serif',
                    'color_scheme': 'blue'
                },
                'color_scheme': {
                    'primary': '#007bff',
                    'secondary': '#6c757d',
                    'accent': '#28a745',
                    'text': '#212529',
                    'background': '#ffffff'
                },
                'is_premium': False,
                'is_active': True
            },
            {
                'name': 'Classique Professionnel',
                'description': 'Un modèle classique et professionnel pour tous les secteurs',
                'category': 'classic',
                'sections': ['personal_info', 'experience', 'education', 'skills', 'certifications', 'references'],
                'layout_config': {
                    'header_style': 'left-aligned',
                    'section_spacing': 'large',
                    'font_family': 'Times New Roman, serif',
                    'color_scheme': 'black'
                },
                'color_scheme': {
                    'primary': '#000000',
                    'secondary': '#6c757d',
                    'accent': '#dc3545',
                    'text': '#212529',
                    'background': '#ffffff'
                },
                'is_premium': False,
                'is_active': True
            },
            {
                'name': 'Créatif Portfolio',
                'description': 'Un modèle créatif pour les métiers artistiques et créatifs',
                'category': 'creative',
                'sections': ['personal_info', 'professional_summary', 'experience', 'projects', 'skills', 'languages'],
                'layout_config': {
                    'header_style': 'creative',
                    'section_spacing': 'small',
                    'font_family': 'Helvetica, sans-serif',
                    'color_scheme': 'colorful'
                },
                'color_scheme': {
                    'primary': '#e83e8c',
                    'secondary': '#6f42c1',
                    'accent': '#fd7e14',
                    'text': '#212529',
                    'background': '#ffffff'
                },
                'is_premium': True,
                'is_active': True
            },
            {
                'name': 'Minimaliste Épuré',
                'description': 'Un modèle minimaliste avec un design épuré et moderne',
                'category': 'minimalist',
                'sections': ['personal_info', 'experience', 'education', 'skills'],
                'layout_config': {
                    'header_style': 'minimal',
                    'section_spacing': 'large',
                    'font_family': 'Arial, sans-serif',
                    'color_scheme': 'monochrome'
                },
                'color_scheme': {
                    'primary': '#28a745',
                    'secondary': '#6c757d',
                    'accent': '#17a2b8',
                    'text': '#212529',
                    'background': '#ffffff'
                },
                'is_premium': False,
                'is_active': True
            },
            {
                'name': 'Professionnel Entreprise',
                'description': 'Un modèle professionnel adapté au monde de l\'entreprise',
                'category': 'professional',
                'sections': ['personal_info', 'professional_summary', 'experience', 'education', 'skills', 'certifications', 'languages'],
                'layout_config': {
                    'header_style': 'corporate',
                    'section_spacing': 'medium',
                    'font_family': 'Calibri, sans-serif',
                    'color_scheme': 'corporate'
                },
                'color_scheme': {
                    'primary': '#343a40',
                    'secondary': '#6c757d',
                    'accent': '#007bff',
                    'text': '#212529',
                    'background': '#ffffff'
                },
                'is_premium': False,
                'is_active': True
            },
            {
                'name': 'Académique Recherche',
                'description': 'Un modèle adapté au monde académique et de la recherche',
                'category': 'academic',
                'sections': ['personal_info', 'education', 'experience', 'publications', 'research', 'skills', 'languages', 'references'],
                'layout_config': {
                    'header_style': 'academic',
                    'section_spacing': 'large',
                    'font_family': 'Times New Roman, serif',
                    'color_scheme': 'academic'
                },
                'color_scheme': {
                    'primary': '#17a2b8',
                    'secondary': '#6c757d',
                    'accent': '#28a745',
                    'text': '#212529',
                    'background': '#ffffff'
                },
                'is_premium': True,
                'is_active': True
            }
        ]
        
        created_count = 0
        for template_data in templates_data:
            template, created = CVTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults=template_data
            )
            if created:
                created_count += 1
                self.stdout.write(f"  ✅ Créé: {template.name}")
            else:
                self.stdout.write(f"  ⚠️  Existe déjà: {template.name}")
        
        self.stdout.write(f"📊 {created_count} nouveaux modèles créés")
        return CVTemplate.objects.count()
