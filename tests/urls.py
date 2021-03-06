from django.conf.urls import patterns, include, url

from views import index, view, give_up, result


test_patterns = patterns('',
    url(r'^$', index, name='index'),
    url(r'^(\d+)/$', view, name='view'),
    url(r'^give-up/$', give_up, name='give_up'),
    url(r'^(\d+)/result/$', result, name='result'),
)

urlpatterns = patterns('',
    url(r'^tests/', include(test_patterns, namespace='tests')),
)
