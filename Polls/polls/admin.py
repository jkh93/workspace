from django.contrib import admin
from polls.models import Question, Choice
from django.contrib.admin import AdminSite

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3

class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['question_text']}),
        ('Date information', {'fields': ['pub_date']}),
    ]
    inlines = [ChoiceInline]
    list_display = ('question_text', 'pub_date', 'was_published_recently')
    list_filter = ['pub_date']
    search_fields = ['question_text']

admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)

# admin site customization
AdminSite.site_header = "POLLS ADMIN"
AdminSite.site_title = "POLLS ADMIN PAGE"
AdminSite.index_title = "SITE ADMINISTRATION"