from django.db import models


class Test(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name


class Page(models.Model):
    name = models.CharField(max_length=50)
    test = models.ForeignKey(Test, related_name='pages')

    def __unicode__(self):
        return '{name} (from Test: {test})'.format(name=self.name,
                                                   test=self.test.name)


class Question(models.Model):
    name = models.CharField(max_length=100)
    page = models.ForeignKey(Page, related_name='questions')

    def __unicode__(self):
        return self.name


class Answer(models.Model):
    name = models.CharField(max_length=100)
    score = models.IntegerField()
    question = models.ForeignKey(Question, related_name='answers')

    def __unicode__(self):
        return self.name


class Result(models.Model):
    text = models.CharField(max_length=100)
    limit = models.IntegerField()
    test = models.ForeignKey(Test, related_name='results')

    def __unicode__(self):
        return self.text
