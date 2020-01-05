from django.views.generic import TemplateView

class MainSiteHomeView(TemplateView):
    template_name = "public/index_public.html"