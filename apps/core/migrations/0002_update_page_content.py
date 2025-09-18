from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pagecontent',
            name='page_type',
            field=models.CharField(choices=[('about', 'À propos'), ('privacy', 'Politique de confidentialité'), ('terms', "Conditions d'utilisation"), ('faq', 'FAQ'), ('contact', 'Contact'), ('home', 'Accueil'), ('hero_section', 'Section héro'), ('footer_content', 'Contenu du footer'), ('custom', 'Page personnalisée')], max_length=20),
        ),
        migrations.AlterUniqueTogether(
            name='pagecontent',
            unique_together={('page_type', 'slug')},
        ),
        migrations.RemoveConstraint(
            model_name='pagecontent',
            name='core_pagecontent_page_type_key',
        ),
    ]