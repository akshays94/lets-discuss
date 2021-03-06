from django.conf import settings
from django.urls import path, re_path, include, reverse_lazy
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic.base import RedirectView
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views

from .users.views import UserViewSet, UserCreateViewSet, CustomAuthToken, UserReputationViewSet, UserLeaderboardViewSet
from .qna.viewsets.answers import AnswerViewSet

from .qna.viewsets.questions import QuestionViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'users', UserCreateViewSet)

router.register(r'reputations', UserReputationViewSet, basename='reputations')
router.register(r'leaderboard', UserLeaderboardViewSet, basename='leaderboard')
router.register(r'questions', QuestionViewSet, basename='questions')
router.register(r'answers', AnswerViewSet, basename='answers')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    # path('login/', views.obtain_auth_token),
    path('login/', CustomAuthToken.as_view()),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # the 'api-root' from django rest-frameworks default router
    # http://www.django-rest-framework.org/api-guide/routers/#defaultrouter
    re_path(r'^$', RedirectView.as_view(url=reverse_lazy('api-root'), permanent=False)),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
