# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding Index 'PaymentInfo'
        db.create_index('gsocial_paymentinfo', ['osuser_id'])


    def backwards(self, orm):
        # Deleting Index 'PaymentInfo'
        db.delete_index('gsocial_paymentinfo', ['osuser_id'])


    models = {
        'gsocial.authdevice': {
            'Meta': {'object_name': 'AuthDevice'},
            'auth_id': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'is_authorized': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'osuser_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'user_grade': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
        },
        'gsocial.messageinfobase': {
            'Meta': {'object_name': 'MessageInfoBase'},
            'body': ('django.db.models.fields.TextField', [], {'max_length': '100'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '26'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'})
        },
        'gsocial.monthlypaymentinfo': {
            'Meta': {'object_name': 'MonthlyPaymentInfo'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'excute_time': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ordered_time': ('django.db.models.fields.DateTimeField', [], {}),
            'osuser_id': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'resubscribe': ('django.db.models.fields.IntegerField', [], {'max_length': '10'}),
            'service_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'status': ('django.db.models.fields.IntegerField', [], {'max_length': '10'}),
            'transaction_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'gsocial.opensocialuser': {
            'Meta': {'object_name': 'OpenSocialUser'},
            'age': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'birthday': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'bloodType': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'friend_userids': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'nickname': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'profileUrl': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'thumbnailUrl': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'userType': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'userid': ('django.db.models.fields.CharField', [], {'max_length': '255', 'primary_key': 'True'})
        },
        'gsocial.paymentinfo': {
            'Meta': {'object_name': 'PaymentInfo'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'device': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item_id': ('django.db.models.fields.IntegerField', [], {'max_length': '50'}),
            'osuser_id': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'point': ('django.db.models.fields.IntegerField', [], {}),
            'point_code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'point_date': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'point_url': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'recv_data': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'send_data': ('django.db.models.fields.TextField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
        }
    }

    complete_apps = ['gsocial']
