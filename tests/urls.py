from django.conf.urls.defaults import patterns, include, url

from views import index, view, result


urlpatterns = patterns('',
	url(r'^$', index),
	url(r'^(\d+)/$', view),
	url(r'^(\d+)/result/$', result),
)