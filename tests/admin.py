from django.core.urlresolvers import reverse
from django.contrib import admin

from models import Test, Page, Question, Answer, Result


class AnswerInline(admin.TabularInline):
	model = Answer


class QuestionAdmin(admin.ModelAdmin):
	inlines = [AnswerInline,]
admin.site.register(Question, QuestionAdmin)


class ResultInline(admin.TabularInline):
	model = Result


class PageInline(admin.TabularInline):
	model = Page


class TestAdmin(admin.ModelAdmin):
	inlines = [PageInline, ResultInline]
admin.site.register(Test, TestAdmin)