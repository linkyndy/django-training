from django.db import models


class Test(models.Model):
	name = models.CharField(max_length=50)
	description = models.CharField(max_length=200)


class Page(models.Model):
	test = models.ForeignKey(Test)


class Question(models.Model):
	name = models.CharField(max_length=100)
	page = models.ForeignKey(Page)


class Answer(models.Model):
	name = models.CharField(max_length=100)
	score = models.IntegerField()
	question = models.ForeignKey(Question)


class Result(models.Model):
	text = models.CharField(max_length=100)
	limit = models.IntegerField()
	test = models.ForeignKey(Test)