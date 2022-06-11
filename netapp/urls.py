from django.urls import path
from .views import RegisterUser, UserView, LoginUser, LogoutView, LoadMovies, LoadCollections, LoadCollectionItem, GetCount, ResetCount

urlpatterns = [
    path('register/', RegisterUser.as_view()),
    path('user/', UserView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('movies/', LoadMovies.as_view()),
    path('collection/', LoadCollections.as_view()),
    path('collection/<int:uuid>/', LoadCollectionItem.as_view()),
    path('request-count/', GetCount.as_view()),
    path('request-count/reset/', ResetCount.as_view()),
]
