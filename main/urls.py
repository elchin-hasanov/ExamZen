from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'main'

urlpatterns = [
    path('', views.home, name='home'),
    path('test/', views.test, name='test'),
    path('lobby/', views.lobby, name='lobby'),
    path('questionbank/', views.questionbank, name='questionbank'),
    path('question/<int:question_id>/', views.question_answer, name='question_answer'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('zens/', views.zen, name='zens'),
    path('submit-exam/', views.submit_exam, name='submit_exam'),
    path('profile/', views.profile, name='profile'),
    path('rankings/', views.rankings, name="rankings")

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
