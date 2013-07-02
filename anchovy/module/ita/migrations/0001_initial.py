# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Ita'
        db.create_table(u'ita_ita', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('is_enable', self.gf('django.db.models.fields.BooleanField')(default=True, db_index=True)),
            ('group', self.gf('django.db.models.fields.IntegerField')()),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('sure_number', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('ita', ['Ita'])

        # Adding unique constraint on 'Ita', fields ['url']
        db.create_unique(u'ita_ita', ['url'])


    def backwards(self, orm):
        # Removing unique constraint on 'Ita', fields ['url']
        db.delete_unique(u'ita_ita', ['url'])

        # Deleting model 'Ita'
        db.delete_table(u'ita_ita')


    models = {
        'ita.ita': {
            'Meta': {'unique_together': "(('url',),)", 'object_name': 'Ita'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'group': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_enable': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'sure_number': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['ita']