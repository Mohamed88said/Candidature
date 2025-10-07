# Generated manually for matching system

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0003_award_award_certificate_and_more'),
        ('jobs', '0003_job_job_description_file_alter_job_company_logo'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MatchingAlgorithm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('experience_weight', models.PositiveIntegerField(default=25)),
                ('skills_weight', models.PositiveIntegerField(default=30)),
                ('location_weight', models.PositiveIntegerField(default=15)),
                ('salary_weight', models.PositiveIntegerField(default=10)),
                ('education_weight', models.PositiveIntegerField(default=10)),
                ('company_culture_weight', models.PositiveIntegerField(default=10)),
                ('minimum_match_score', models.PositiveIntegerField(default=60)),
                ('high_match_threshold', models.PositiveIntegerField(default=80)),
                ('use_ai_analysis', models.BooleanField(default=True)),
                ('consider_soft_skills', models.BooleanField(default=True)),
                ('location_radius_km', models.PositiveIntegerField(default=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Algorithme de Matching',
                'verbose_name_plural': 'Algorithmes de Matching',
            },
        ),
        migrations.CreateModel(
            name='JobMatch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('overall_score', models.PositiveIntegerField()),
                ('experience_score', models.PositiveIntegerField()),
                ('skills_score', models.PositiveIntegerField()),
                ('location_score', models.PositiveIntegerField()),
                ('salary_score', models.PositiveIntegerField()),
                ('education_score', models.PositiveIntegerField()),
                ('culture_score', models.PositiveIntegerField()),
                ('matching_skills', models.JSONField(default=list)),
                ('missing_skills', models.JSONField(default=list)),
                ('strengths', models.JSONField(default=list)),
                ('concerns', models.JSONField(default=list)),
                ('recommendations', models.TextField(blank=True)),
                ('is_viewed_by_candidate', models.BooleanField(default=False)),
                ('is_viewed_by_recruiter', models.BooleanField(default=False)),
                ('candidate_interest', models.CharField(blank=True, choices=[('not_interested', 'Pas intéressé'), ('interested', 'Intéressé'), ('very_interested', 'Très intéressé'), ('applied', 'A postulé')], max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('algorithm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='matching.matchingalgorithm')),
                ('candidate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_matches', to='accounts.candidateprofile')),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='candidate_matches', to='jobs.job')),
            ],
            options={
                'verbose_name': 'Match Emploi',
                'verbose_name_plural': 'Matches Emploi',
                'ordering': ['-overall_score', '-created_at'],
                'unique_together': {('candidate', 'job', 'algorithm')},
            },
        ),
        migrations.CreateModel(
            name='CandidatePreference',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('preferred_locations', models.JSONField(default=list, help_text='Liste des villes/régions préférées')),
                ('max_commute_time', models.PositiveIntegerField(default=60, help_text='Temps de trajet max en minutes')),
                ('willing_to_relocate', models.BooleanField(default=False)),
                ('remote_work_preference', models.CharField(choices=[('office_only', 'Bureau uniquement'), ('remote_only', 'Télétravail uniquement'), ('hybrid', 'Hybride'), ('flexible', 'Flexible')], default='flexible', max_length=20)),
                ('min_salary', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('max_salary', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('salary_negotiable', models.BooleanField(default=True)),
                ('preferred_company_sizes', models.JSONField(default=list)),
                ('preferred_industries', models.JSONField(default=list)),
                ('preferred_company_cultures', models.JSONField(default=list)),
                ('preferred_job_types', models.JSONField(default=list)),
                ('preferred_experience_levels', models.JSONField(default=list)),
                ('career_goals', models.TextField(blank=True)),
                ('excluded_companies', models.JSONField(default=list)),
                ('excluded_locations', models.JSONField(default=list)),
                ('excluded_industries', models.JSONField(default=list)),
                ('alert_frequency', models.CharField(choices=[('immediate', 'Immédiat'), ('daily', 'Quotidien'), ('weekly', 'Hebdomadaire'), ('monthly', 'Mensuel')], default='daily', max_length=20)),
                ('min_match_score', models.PositiveIntegerField(default=70)),
                ('only_high_matches', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('candidate', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='matching_preferences', to='accounts.candidateprofile')),
            ],
            options={
                'verbose_name': 'Préférence de Matching',
                'verbose_name_plural': 'Préférences de Matching',
            },
        ),
        migrations.CreateModel(
            name='MatchingHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('algorithm_version', models.CharField(max_length=50)),
                ('overall_score', models.PositiveIntegerField()),
                ('experience_score', models.PositiveIntegerField()),
                ('skills_score', models.PositiveIntegerField()),
                ('location_score', models.PositiveIntegerField()),
                ('salary_score', models.PositiveIntegerField()),
                ('education_score', models.PositiveIntegerField()),
                ('culture_score', models.PositiveIntegerField()),
                ('candidate_action', models.CharField(blank=True, choices=[('viewed', 'Vu'), ('interested', 'Intéressé'), ('applied', 'A postulé'), ('ignored', 'Ignoré'), ('saved', 'Sauvegardé')], max_length=20)),
                ('recruiter_action', models.CharField(blank=True, choices=[('viewed', 'Vu'), ('contacted', 'Contacté'), ('interviewed', 'Entretien'), ('hired', 'Embauché'), ('rejected', 'Rejeté')], max_length=20)),
                ('final_outcome', models.CharField(blank=True, choices=[('hired', 'Embauché'), ('rejected', 'Rejeté'), ('withdrawn', 'Retiré'), ('pending', 'En cours')], max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('candidate', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='matching_history', to='accounts.candidateprofile')),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='matching_history', to='jobs.job')),
            ],
            options={
                'verbose_name': 'Historique de Matching',
                'verbose_name_plural': 'Historiques de Matching',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='SkillSimilarity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('skill1', models.CharField(max_length=100)),
                ('skill2', models.CharField(max_length=100)),
                ('similarity_score', models.FloatField(help_text='Score de similarité entre 0 et 1')),
            ],
            options={
                'verbose_name': 'Similarité de Compétence',
                'verbose_name_plural': 'Similarités de Compétences',
                'unique_together': {('skill1', 'skill2')},
            },
        ),
        migrations.CreateModel(
            name='IndustrySimilarity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('industry1', models.CharField(max_length=100)),
                ('industry2', models.CharField(max_length=100)),
                ('similarity_score', models.FloatField(help_text='Score de similarité entre 0 et 1')),
            ],
            options={
                'verbose_name': "Similarité d'Industrie",
                'verbose_name_plural': "Similarités d'Industries",
                'unique_together': {('industry1', 'industry2')},
            },
        ),
    ]

