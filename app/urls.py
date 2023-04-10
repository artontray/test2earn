from . import views
from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path("", views.StatistiqueApp.as_view(), name="home"),
    path('dashboard/', views.ShowDashboard.as_view(), name='dashboard'),
    path('dashboard/<slug:username>', views.ShowDashboard.as_view(
        ), name='dashboard'),
    path('users/', views.ShowUsers.as_view(), name='showusers'),
    path('notifications/<slug:username>', views.ShowNotifications.as_view(
        ), name='show_notifications'),
    path('showtestnet/<slug:slug>', views.ShowTestnet.as_view(
        ), name='showtestnet'),
    path('showtestnetall/<slug:username>', views.ShowTestnetall.as_view(
        ), name='showtestnetall'),
    path('shownewtestnetall/', views.ShowNewTestnetAll.as_view(
        ), name='show_new_testnet_all'),
    path('addfavorite/<int:id>', views.AddFavoriteUser.as_view(
        ), name='add_favorite_user'),
    path('updateuserprofile/<slug:pk>', views.UpdateProfile.as_view(
        ), name='update_profile_user'),
    path('deletefavorite/<int:id>', views.DeleteFavoriteUser.as_view(
        ), name='delete_favorite_user'),
    path('blockuser/<int:id>', views.BlockUser.as_view(
        ), name='block_user'),
    path('deleteuser/<int:id>', views.DeleteUser.as_view(
        ), name='delete_user'),
    path('notification/<int:id>/update', views.UpdateNotifications.as_view(
        ), name='updatenotification'),
    path('addtestnet/', views.AddTestnet.as_view(
        ), name='addtestnet'),
    path('copytestnet/<slug:slug>', views.CopyTestnet.as_view(
        ), name='copy_testnet'),
    path('deletetestnet/<slug:slug>', views.DeleteTestnet.as_view(
        ), name='delete_testnet'),
    path('edittestnet/<slug:slug>', views.UpdateTestnet.as_view(
        ), name='update_testnet'),
    path('reporttestnet/<slug:slug>', views.ReportTestnet.as_view(
        ), name='report_testnet'),
    path('administrateusers/', views.AdminitrateUsers.as_view(
        ), name='administrate_users'),
    path('administratetestnet/', views.AdminitrateTestnet.as_view(
        ), name='administrate_testnet'),
    path('giveadmin/<int:id>', views.GiveAdmin.as_view(
        ), name='give_admin')
]
