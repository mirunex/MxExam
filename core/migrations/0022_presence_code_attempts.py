from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [('core', '0021_exam_end_time'), migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.AddField(model_name='examsession', name='last_seen_at', field=models.DateTimeField(blank=True, null=True, verbose_name='Last activity')),
        migrations.CreateModel(name='CodeSubmissionAttempt', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('code', models.TextField(blank=True)), ('passed', models.IntegerField(default=0)), ('total', models.IntegerField(default=0)), ('score', models.FloatField(default=0.0)), ('submitted_at', models.DateTimeField(auto_now_add=True)),
            ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='code_submission_attempts', to=settings.AUTH_USER_MODEL)),
            ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submission_attempts', to='core.codetask')),
        ], options={'ordering': ['submitted_at'], 'verbose_name': 'Code submission attempt', 'verbose_name_plural': 'Code submission attempts'}),
    ]
