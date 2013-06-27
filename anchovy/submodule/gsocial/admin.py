# -*- coding: utf-8 -*-
from django.contrib import admin
from gsocial.models import MessageInfoBase
from gsocial.log import Log

class MessageInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'sent', 'title', 'body', 'url', 'created_at')

    fieldsets = (
        (None, {
            'fields': ('title', 'body', 'url', 'sent'),
        }),
    )

    def send_action(self, request, queryset):
        if len(queryset) == 1:
            # 送信？
            message_info = queryset[0]
            Log.debug(queryset[0])
            message_info.send_message(request)
            url = message_info.url
            if not url:
                url = '/m/'
            self.message_user(request, u'メッセージ[%s:%s](%s)は送信されました。' % (message_info.title, message_info.body, url))
        else:
            self.message_user(request, u'メッセージは一つだけ選択してください。')
        pass
    send_action.short_description = u'選択したメッセージをAPIで全員に送信'

    actions = [send_action]

    def get_actions(self, request):
        '''
        削除アクションを使用できないように
        '''
        actions = super(MessageInfoAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions


admin.site.register(MessageInfoBase, MessageInfoAdmin)


