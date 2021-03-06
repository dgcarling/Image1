# Generated by Django 3.1.6 on 2021-02-12 17:09

from django.db import migrations, models
import django.db.models.deletion
import imagekit.models.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Album',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=70)),
                ('description', models.TextField(max_length=1024)),
                ('thumb', imagekit.models.fields.ProcessedImageField(upload_to='albums')),
                ('tags', models.CharField(max_length=250)),
                ('is_visible', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now_add=True)),
                ('slug', models.SlugField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='AlbumImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', imagekit.models.fields.ProcessedImageField(upload_to='albums')),
                ('thumb', imagekit.models.fields.ProcessedImageField(upload_to='albums')),
                ('alt', models.CharField(default=uuid.uuid4, max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('width', models.IntegerField(default=0)),
                ('height', models.IntegerField(default=0)),
                ('title', models.CharField(default='', max_length=100)),
                ('slug', models.SlugField(default=uuid.uuid4, editable=False, max_length=70)),
                ('album', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='gallery.album')),
            ],
        ),
        migrations.CreateModel(
            name='ImageTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='TagMapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('counter', models.IntegerField(default=0)),
                ('albumimage', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gallery.albumimage')),
                ('imagetag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gallery.imagetag')),
            ],
        ),
        migrations.AddField(
            model_name='imagetag',
            name='imagelink',
            field=models.ManyToManyField(through='gallery.TagMapping', to='gallery.AlbumImage'),
        ),
    ]
