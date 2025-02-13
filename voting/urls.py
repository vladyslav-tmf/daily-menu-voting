from django.urls import path

from voting.views import CreateVoteView, TodayResultsView, UserVoteHistoryView

app_name = "voting"

urlpatterns = [
    path("", CreateVoteView.as_view(), name="create-vote"),
    path("my/", UserVoteHistoryView.as_view(), name="vote-history"),
    path("results/today/", TodayResultsView.as_view(), name="today-results"),
]
