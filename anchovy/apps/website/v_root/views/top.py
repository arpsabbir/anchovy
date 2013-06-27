# -*- coding:utf-8 -*-

from django.views.generic import TemplateView


class RootTopView(TemplateView):
    """
    TOPページ
    """
    template_name = "root/top.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        is_fp = request.device.is_featurephone
        is_sp = request.device.is_smartphone
        is_pc = request.device.is_pc


        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        return {
            'is_pc': 1,
        }
