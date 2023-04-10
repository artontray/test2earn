from django.shortcuts import render, get_object_or_404, reverse, redirect
from django.views import generic, View
from django.db.models import F, Q
from django.http import HttpResponseRedirect
from .models import Testnet
from .models import Notifications, UserInfo
from django.contrib.auth.models import User
from django.template import loader, RequestContext
from django.contrib import messages
from django.views.generic.base import TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from .forms import TestnetForm, EditUserForm
from functools import reduce
from django.conf import settings
from django.template.defaultfilters import slugify
from django.utils.html import strip_tags
import re


class StatistiqueApp(generic.ListView):
    """
    This view is used to display some statistics from the app
    """
    def get(self, request):
        """
        Get the Testnet Total number and the User total number
        """
        nb_testnet_total = Testnet.objects.all().count()
        nb_user_total = User.objects.all().count()
        return render(
            request,
            "index.html",
            {
                "nb_testnet": nb_testnet_total,
                "nb_user": nb_user_total
            },
        )


def manage_exp_user(user, action):
    """
    Add or substract Exp from user
    """
    exp = settings.EXP_PER_ACTION*settings.COEFF_FOR_LEVEL_UP
    user_info = UserInfo.objects.get(user=user)
    if action == "add":
        user_info.exp += exp
    elif action == "subtract":
        user_info.exp -= exp
    else:
        pass
    return user_info.save()


def check_user_exist(object_user):
    """
    return True if user exist
    """
    return User.objects.filter(id=object_user.id).exists()


def add_notification_user(user, message, title):
    """
    Add a Notification to user
    """
    if check_user_exist(user):
        creation_notification = Notifications.objects.create(
                notification_owner=user,
                message=message,
                title=title
                )
        return creation_notification.save()


class DeleteTestnet(generic.CreateView):
    """
    Delete a Testnet
    """
    model = Testnet

    def get(self, request, slug, *args, **kwargs):
        """
        Get slug and current user info
        """
        queryset = UserInfo.objects.all()
        current_user = get_object_or_404(queryset, user=request.user.id)
        queryset = Testnet.objects.all()
        testnet_to_delete = get_object_or_404(queryset, slug=slug)
        if (testnet_to_delete.testnet_user == current_user.user) or (
                current_user.status == 1):
            html_pattern = "<(?:\"[^\"]*\"['\"]*|'[^']*'['\"]*|[^'\">])+>"
            '''
            This regex been taken from
            https://uibakery.io/regex-library/html-regex-python
            '''
            all_testnet_to_delete = Testnet.objects.all().filter(
                Q(slug_original=testnet_to_delete.slug)
                | Q(slug=testnet_to_delete.slug)
                )
            # Before Deleting a Testnet we send the Testnet user info
            # into Notification
            # If user/admin delete a Testnet which have been copied
            # by other user, original and copy will be deleted
            for testnet in all_testnet_to_delete:
                message = (
                    "The Testnet : " + re.sub(
                        html_pattern, '', testnet.testnet_name
                        ) + "<br>"
                    )
                message += "have been deleted by the Author or an Admin<br>"
                message += "Here is your informations about this testnet :<br>"
                # In case a user incoporate malicious script code into Testnet,
                # we dont want this code
                # to be executed while displaying on Notification : re.sub
                # function will extract some tags
                message += (
                    "Your telegram : " + re.sub(
                        html_pattern, '', testnet.telegram_user
                        ) + "<br>"
                    )
                message += (
                    "Your Github : " + re.sub(
                        html_pattern, '', testnet.github_user)
                        ) + "<br>"
                message += (
                    "Your discord : " + re.sub(
                        html_pattern, '', testnet.discord_user)
                        ) + "<br>"
                message += (
                    "Your twitter : " + re.sub(
                        html_pattern, '', testnet.twitter_user)
                        ) + "<br>"
                message += (
                    "Your email : " + re.sub(
                        html_pattern, '', testnet.email_user)
                        ) + "<br>"
                message += (
                    "The link : " + re.sub(
                        html_pattern, '', testnet.website_user)
                        ) + "<br>"
                message += (
                    "Your wallet 1 : " + re.sub(
                        html_pattern, '', testnet.wallet1_adress)
                        ) + "<br>"
                message += (
                    "Private key Wallet 1 : " + re.sub(
                        html_pattern, '', testnet.wallet1_priv_key)
                        ) + "<br>"
                message += (
                    "Seed Wallet 1 : " + re.sub(
                        html_pattern, '', testnet.wallet1_seed)
                        ) + "<br>"
                message += (
                    "Clue Wallet 1 : " + re.sub(
                        html_pattern, '', testnet.wallet1_clue)
                        ) + "<br>"
                message += (
                    "password Wallet 1 : " + re.sub(
                        html_pattern, '', testnet.wallet1_password)
                        ) + "<br>"
                message += (
                    "Session Wallet 1 : " + re.sub(
                        html_pattern, '', testnet.wallet1_session)
                        ) + "<br>"
                message += (
                    "Your wallet 2 : " + re.sub(
                        html_pattern, '', testnet.wallet2_adress)
                        ) + "<br>"
                message += (
                    "Private key Wallet 2 : " + re.sub(
                        html_pattern, '', testnet.wallet2_priv_key)
                        ) + "<br>"
                message += (
                    "Seed Wallet 2 : " + re.sub(
                        html_pattern, '', testnet.wallet2_seed)
                        ) + "<br>"
                message += (
                    "Clue Wallet 2 : " + re.sub(
                        html_pattern, '', testnet.wallet2_clue)
                        ) + "<br>"
                message += (
                    "password Wallet 2 : " + re.sub(
                        html_pattern, '', testnet.wallet2_password)
                        ) + "<br>"
                message += (
                    "Session Wallet 2 : " + re.sub(
                        html_pattern, '', testnet.wallet2_session)
                        ) + "<br>"
                message += (
                    "Tasks description : " + re.sub(
                        html_pattern, '', testnet.tasks_description)
                        ) + "<br>"
                message += (
                    "Tasks Results : " + re.sub(
                        html_pattern, '', testnet.tasks_results)
                        ) + "<br>"
                add_notification_user(
                        testnet.testnet_user, message, "Testnet -1")
                testnet.delete()
                #   If testnet_user and author is same we substract exp
                if testnet_to_delete.author == testnet_to_delete.testnet_user:
                    manage_exp_user(testnet_to_delete.testnet_user, "subtract")
                    messages.add_message(
                        self.request, messages.SUCCESS, (
                            "You deleted a Testnet successfully and all" +
                            " users who copied this Testnet will receive a" +
                            "Notification about it!"))
                else:
                    add_notification_user(
                        current_user.user, (
                            "The Testnet {testnet_to_delete.testnet_name}" +
                            " have been deleted"), "Testnet -1")
                    messages.add_message(
                        self.request, messages.SUCCESS, (
                            "You deleted a Testnet successfully"))
                #   If user is admin
                if current_user.status == 1:
                    add_notification_user(current_user.user, (
                        "The Testnet called  %s have been deleted" % (
                            testnet_to_delete.testnet_name)
                            ), "Testnet -1")
                    return HttpResponseRedirect(
                        reverse('administrate_testnet'))
            return HttpResponseRedirect(reverse('dashboard'))

        else:
            add_notification_user(current_user.user, (
                "You cannot delete this Testnet : <code>%s</code>" +
                ", it's proprety of an other User!" % (
                    testnet_to_delete.testnet_name)
                    ), "Testnet -1")
            messages.add_message(self.request, messages.SUCCESS, (
                "You cannot delete this Testnet! Action Aborted..."))
            return HttpResponseRedirect(reverse('dashboard'))


class CopyTestnet(generic.CreateView):
    """
    Copy a Testnet
    """
    model = Testnet

    def get(self, request, slug, *args, **kwargs):
        """
        Get slug and current user info
        """
        queryset = UserInfo.objects.all()
        current_user = get_object_or_404(queryset, user=request.user.id)
        queryset = Testnet.objects.all()
        author_testnet = get_object_or_404(queryset, slug=slug)
        # looking after the published original testnet to copy
        queryset = Testnet.objects.all(
            ).filter(
                testnet_user=author_testnet.author,
                author=author_testnet.author, status_testnet=0)
        testnet_to_copy = get_object_or_404(queryset, slug=slug)
        t = Testnet.objects.get(pk=testnet_to_copy.id)
        # When copy a Testnet we generated a none existing slug
        # as slug should be unique
        base_slug = slugify(t.testnet_name)
        suffix = 0
        while True:
            if not suffix:
                slug = base_slug
            else:
                slug = "%s-%d" % (base_slug, suffix)
                # When copy, a testnet_name and slug is unique,
                # lets check integrity of this
                # Otherwise loop will try a new suffix until name is available
                # for adding both slug and testnet_name into database
            if not Testnet.objects.filter(slug=slug).exists():
                if not Testnet.objects.filter(testnet_name=slug).exists():
                    break
            suffix += 1
        t.testnet_name = slug
        t.slug = slug
        t.testnet_user = request.user
        #   We empty the copied testnet info
        t.telegram_user = ''
        t.github_user = ''
        t.discord_user = ''
        t.twitter_user = ''
        t.email_user = ''
        t.wallet1_adress = ''
        t.wallet1_priv_key = ''
        t.wallet1_seed = ''
        t.wallet1_clue = ''
        t.wallet1_password = ''
        t.wallet1_session = ''
        t.tasks_results = ''
        t.wallet2_adress = ''
        t.wallet2_priv_key = ''
        t.wallet2_seed = ''
        t.wallet2_clue = ''
        t.wallet2_password = ''
        t.wallet2_session = ''
        t.pk = None
        t.save()
        testnet_to_copy.copied_nb += 1
        testnet_to_copy.save()
        # If user is the author of the expected copied Testnet
        if request.user == testnet_to_copy.author:
            url = reverse('showtestnet', args=[t.slug])
            add_notification_user(
                request.user,
                "You have duplicate one of your Testnet successfully" +
                f": <a href='{url}' target='_blank'>" +
                testnet_to_copy.testnet_name + "</a>",
                "Testnet duplicated +1"
                    )
        else:
            testnet_to_copy.save()
            manage_exp_user(testnet_to_copy.author, "add")
            url = reverse('showtestnet', args=[testnet_to_copy.slug])
            add_notification_user(
                testnet_to_copy.author,
                f"{request.user} has copied this <a href='{url}' " +
                "target='_blank'>" +
                "<code>Testnet</code></a> from you!",
                "New Copied Testnet +1"
                    )
            add_notification_user(
                request.user, (
                    f"As <code>{t.copied_nb+1} Users</code> " +
                    "on the app, You have copied " +
                    f"a Testnet from <code> {testnet_to_copy.author}" +
                    " </code>called " +
                    f"{testnet_to_copy.testnet_name}"), "Testnet copied +1"
                    )
        return HttpResponseRedirect(reverse('update_testnet', args=[slug]))


class FormEditUserMixin:
    """
    Class to deal with profile edition user form
    """
    model = UserInfo
    success_url = '/dashboard/'
    form_class = EditUserForm

    def get_form_kwargs(self):
        """
        Get user from the URL
        """
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        """
        If form is valid, User Profile will be updated
        """
        messages.add_message(self.request, messages.SUCCESS, self.success_msg)
        return super().form_valid(form)


class GiveAdmin(generic.UpdateView):
    """
    Class to give admin status to a user
    If already an Admin, it will loose the admin role
    """
    def get(self, request, id, *args, **kwargs):
        """
        Get id from the user to give admin from URL and current User logged
        """
        current_user = UserInfo.objects.filter(user=request.user.id)
        # We make sure is admin connected
        admin = get_object_or_404(current_user, status=1)
        queryset = UserInfo.objects.all()
        user_to_update = get_object_or_404(queryset, id=id)
        if user_to_update.status == 1 and request.user.id != id:
            #   if user already admin and not call himself through URL'''
            user_to_update.status = 0
            user_to_update.save()
            add_notification_user(
                user_to_update.user, (
                    f"<code>{self.request.user.username}</code>" +
                    "deleted you as an " +
                    "admin", "Admin -1"
                ))
            add_notification_user(
                self.request.user, (
                    f"You deleted {user_to_update.user.username}" +
                    " as an admin of " +
                    "the App"), "Admin -1")
            messages.add_message(
                self.request, messages.SUCCESS, (
                    "You deleted a User from Admin Role successfully")
                )
            return HttpResponseRedirect(reverse('administrate_users'))
        if user_to_update.status == 0:
            user_to_update.status = 1
            user_to_update.save()
            add_notification_user(
                user_to_update.user, (
                    f"<code>{self.request.user.username}</code> added " +
                    "you as admin on the App," +
                    "Welcome!"), "Admin +1")
            add_notification_user(
                self.request.user, (
                    f"You added <code>{user_to_update.user.username}</code>" +
                    " as an admin " +
                    "of the App"), "Admin +1")
            messages.add_message(
                self.request, messages.SUCCESS, (
                    "You added a User with Admin Role successfully")
                )
            return HttpResponseRedirect(reverse(
                'show_notifications', args=[self.request.user.username]))
        return HttpResponseRedirect(reverse('dashboard'))


class UpdateProfile(FormEditUserMixin, LoginRequiredMixin,
                    UserPassesTestMixin, generic.UpdateView):
    """
    Update Profile from the FromEditUserMixin class
    """
    def test_func(self):
        """
        Avoiding updating others user Profiles
        """
        user = self.get_object()
        return user.id == self.request.user.user_info.id
    success_msg = "Congratulation, your Profile is Updated!"


class FormTestnetMixin:
    """
    Class use to generate Testnet form for adding or editing
    """
    model = Testnet
    success_url = '/dashboard/'
    form_class = TestnetForm
    success_msg = "Testnet have been registered successfully"
    action = "none"

    def get_form_kwargs(self):
        """
        Get user from the URL
        """
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        """
        If form is valid and follow the rules given from Testnet Models
        the testnet will be created or Updated with new data
        """
        if self.action == 'AddTestnet':
            manage_exp_user(self.request.user, "add")
            add_notification_user(self.request.user, (
                "You add a new testnet, Good Job!"), "Testnet +1")
            all_users_following_this_user = UserInfo.objects.all(
                ).filter(following=self.request.user.id)
            url = reverse('dashboard', args=[self.request.user])
            # All users that follow the User who create
            # this testnet will receive a Notification
            for user in all_users_following_this_user:
                add_notification_user(
                    user.user, "{self.request.user.username} just created" +
                    f"a new Testnet, <a href='{url}' target='_blank'>" +
                    "Check it out now</a>", "Following Testnet +1")
        # self.test_if_author()
        if self.action == 'UpdateTestnet':
            add_notification_user(self.request.user, (
                "You edited one of your Testnet"), "Update Testnet +1")
            self.update_all_copied_testnet(form)
        messages.add_message(self.request, messages.SUCCESS, self.success_msg)
        return super().form_valid(form)

    def update_all_copied_testnet(self, form):
        """
        Update all the copied testnet from the updated Testnet
        Of course We update only the Testnet information,
        each user keep their personal info on each Testnet
        """
        testnet = self.get_object()
        if testnet.author == self.request.user:
            testnet_original = Testnet.objects.get(slug=testnet.slug)
            # We seek after all the Testnet with
            # slug_original = slug of the Updated Testnet
            testnet_to_update = Testnet.objects.filter(
                slug_original=testnet_original.slug
                )
            for each_testnet in testnet_to_update:
                each_testnet.tasks_description = (
                    form.instance.tasks_description
                )
                each_testnet.network_name = form.instance.network_name
                each_testnet.network_status = form.instance.network_status
                each_testnet.description = form.instance.description
                each_testnet.category = form.instance.category
                each_testnet.twitter = form.instance.twitter
                each_testnet.facebook = form.instance.facebook
                each_testnet.website = form.instance.website
                each_testnet.github = form.instance.github
                each_testnet.discord = form.instance.discord
                each_testnet.telegram = form.instance.telegram
                each_testnet.instagram = form.instance.instagram
                each_testnet.youtube = form.instance.youtube
                each_testnet.whitepaper = form.instance.whitepaper
                each_testnet.save()
                url = reverse('showtestnet', args=[each_testnet.slug])
                add_notification_user(
                    each_testnet.testnet_user,
                    "Update has been deployed " +
                    "to one of the Testnet you use : " +
                    f"{each_testnet.testnet_name}, <a href='{url}' " +
                    "target='_blank'><code>Check it out here</code></a>",
                    "Updated testnet +1")
            messages.add_message(self.request, messages.SUCCESS, (
                "Updated Testnet : All copies of this Testnet have " +
                "been updated and all User using this testnet got a " +
                "Notification about it!")
                )


class AddTestnet(FormTestnetMixin, generic.CreateView):
    """
    Add new Testnet
    """
    action = "AddTestnet"
    success_msg = "Testnet have been created successfully"


class UpdateTestnet(FormTestnetMixin, LoginRequiredMixin,
                    UserPassesTestMixin, generic.UpdateView):
    """
    Update a Testnet
    """
    action = 'UpdateTestnet'

    def test_func(self):
        """
        Avoiding Updating an other user's Testnet
        """
        testnet = self.get_object()
        return testnet.testnet_user.username == self.request.user.username
    success_msg = "Testnet updated successfully"


class AddFavoriteUser(generic.DetailView):
    """
    Add Favorite user : Follow a new user
    """
    def get(self, request, id, *args, **kwargs):
        """
        Get the id from user to follow and current logged user
        """
        queryset = UserInfo.objects.all()
        current_user = get_object_or_404(queryset, user=request.user.id)
        queryset = User.objects.all()
        user_to_follow = get_object_or_404(queryset, id=id)
        current_user.following.add(user_to_follow)
        current_user.save()
        manage_exp_user(user_to_follow, "add")
        url = reverse('dashboard', args=[self.request.user])
        add_notification_user(
            user_to_follow,
            f"<a href='{url}' target='_blank'>" +
            self.request.user.username + "</a> is following you!",
            "Follower +1")
        url = reverse('dashboard', args=[user_to_follow])
        add_notification_user(
            self.request.user, "You are now following " +
            f"<a href='{url}'" + "target='_blank'>" +
            user_to_follow.username + "</a>", "Following +1"
            )

        messages.add_message(self.request, messages.SUCCESS, (
                "You add a New User as Favorite"
                ))
        return HttpResponseRedirect(
            reverse('dashboard', args=[user_to_follow])
        )


class DeleteFavoriteUser(generic.DeleteView):
    """
    Delete Favorite user : Unfollow a user
    """
    def get(self, request, id, *args, **kwargs):
        """
        Get the id from user to follow and current logged user
        """
        queryset = UserInfo.objects.all()
        current_user = get_object_or_404(queryset, user=request.user.id)
        queryset = User.objects.all()
        user_to_unfollow = get_object_or_404(queryset, id=id)
        manage_exp_user(user_to_unfollow, "subtract")
        current_user.following.remove(user_to_unfollow)
        current_user.save()
        url = reverse('dashboard', args=[self.request.user])
        add_notification_user(
            user_to_unfollow, f"<a href='{url}' target='_blank'>" +
            self.request.user.username +
            "</a> is not following you anymore!", "follower -1")
        url = reverse('dashboard', args=[user_to_unfollow])
        add_notification_user(
            self.request.user, f"You are not following <a href='{url}'" +
            "target='_blank'>" +
            user_to_unfollow.username + "</a>", "Following -1")
        messages.add_message(self.request, messages.SUCCESS, (
            "You unfollowed a User"))
        return HttpResponseRedirect(
            reverse('dashboard', args=[user_to_unfollow])
        )


class DeleteUser(generic.DeleteView):
    """
    Delete User
    """
    def get(self, request, id, *args, **kwargs):
        """
        Get the id from user to delete and current logged user
        """
        current_user = UserInfo.objects.filter(user=request.user.id)
        admin = get_object_or_404(current_user, status=1)
        queryset = User.objects.all()
        user_to_delete = get_object_or_404(queryset, id=id)
        if request.user.id == id:
            #   Trying to delete yourself as a user, aborted
            add_notification_user(self.request.user, (
                "You are trying to delete yourself from the app, aborted"
                ), "Aborted -1")
            messages.add_message(self.request, messages.ERROR, (
                "Aborted Action : Cannot delete yourself!")
                )
            return HttpResponseRedirect(reverse('dashboard'))

        # If user deleted, we delete all Testnet from this user
        all_testnet_to_delete = Testnet.objects.all().filter(author__id=id)
        for testnet in all_testnet_to_delete:
            testnet.delete()
            # In this case, Its Admin that deleted this user
            # Testnet contents from Deleted user by admin
            # are not considered as legit
            # So we just deleted all copies and original Testnet from this user
            # We send notifications to all copied Testnet users
            add_notification_user(testnet.testnet_user, (
                "A Testnet you copied have been " +
                f"deleted : <code>{testnet.testnet_name}</code>" +
                "! Reason : The author have been deleted from the app by " +
                "an Admin "), "Testnet -1")
        user_to_delete.delete()
        add_notification_user(self.request.user, (
            "You deleted the following user : %s " % (user_to_delete.username)
                ), "User -1")
        messages.add_message(self.request, messages.SUCCESS, (
            "You delete a User from the App!"))
        return HttpResponseRedirect(reverse('administrate_users'))


class BlockUser(generic.DetailView):
    """
    Block a User
    If Testnet from this user are reported, Admin can decide to block this user
    Consequences : Any Testnet from this user are not available for
    copying or displaying
    """
    def get(self, request, id, *args, **kwargs):
        """
        Get the id from user to block and current logged user
        """
        current_user = UserInfo.objects.filter(user=request.user.id)
        admin = get_object_or_404(current_user, status=1)
        request = UserInfo.objects.all()
        user_to_block = get_object_or_404(request, id=id)

        if user_to_block.status == 2:
            user_to_block.status = 0
            user_to_block.save()

            add_notification_user(self.request.user, (
                "The following user : <code> {user_to_block.user.username} " +
                "</code> is not blocked " +
                "anymore"), "User +1")
            messages.add_message(self.request, messages.SUCCESS, (
                "A user account is now active!")
                )
        else:
            if admin.id == id:
                '''user cannot block himself'''
                add_notification_user(self.request.user, (
                    "You are trying to block yourself : aborted"), "Action -1"
                    )
                messages.add_message(self.request, messages.SUCCESS, (
                    "You cannot block yourself!")
                    )
            else:
                user_to_block.status = 2
                user_to_block.save()

                add_notification_user(self.request.user, (
                    "You blocked : %s " % (user_to_block.user.username)),
                    "User -1")
                messages.add_message(self.request, messages.SUCCESS, (
                    "You blocked a user successfully")
                    )

        return HttpResponseRedirect(reverse('administrate_users'))


class ReportTestnet(generic.DetailView):
    """
    Report Testnet
    All users on the app can report a Testnet
    If happening, all admin from the app will receive a notification
    Any admin can cancel the report
    A reported Testnet is not available for copying
    """
    def get(self, request, slug, *args, **kwargs):
        """
        Get the slug from testnet to report and current logged user
        """
        queryset = UserInfo.objects.all()
        current_user = get_object_or_404(queryset, user=request.user.id)
        queryset = Testnet.objects.all()
        testnet_to_report = get_object_or_404(queryset, slug=slug)
        url = reverse('showtestnet', args=[testnet_to_report.slug])
        if testnet_to_report.status_testnet == 2:
            # If normal User, redirect to dashboard because Testnet
            # is already Reported
            if not request.user.user_info.is_admin:
                return HttpResponseRedirect(reverse('dashboard'))
            #   If admin we cancel the report to this testnet
            testnet_to_report.status_testnet = 0
            testnet_to_report.save()
            all_testnet_to_report = Testnet.objects.filter(slug_original=slug)

            for testnets in all_testnet_to_report:
                testnets.status_testnet = 0
                testnets.save()
            add_notification_user(
                testnet_to_report.author, f"{self.request.user.username}" +
                "have cancelled the report" +
                "on your testnet <a href='{url}' target='_blank'>" +
                testnet_to_report.testnet_name + "</a>", "Testnet +1")
            add_notification_user(
                current_user.user, f"You have cancelled the report on" +
                " your testnet " +
                f"<a href='{url}' target='_blank'>" +
                testnet_to_report.testnet_name + "</a>", "Testnet +1")
            messages.add_message(self.request, messages.SUCCESS, (
                "You have cancelled the report on a Testnet successfully")
            )
        else:
            # Testnet original and all copies will be reported status
            all_testnet_to_report = Testnet.objects.filter(slug_original=slug)

            for testnets in all_testnet_to_report:
                testnets.status_testnet = 2
                testnets.save()

            # We inform the Author
            add_notification_user(
                testnet_to_report.author, f"{self.request.user.username}" +
                "reported " +
                f"your testnet : <a href='{url}' target='_blank'>" +
                testnet_to_report.testnet_name + "</a>", "Testnet -1")
            add_notification_user(self.request.user, (
                "You reported a " +
                "testnet <code>%s</code>" % (testnet_to_report.testnet_name)),
                "Reported +1")
            all_admin = UserInfo.objects.all().filter(status=1)
            # Send to all admin of the platform about this reported Testnet
            for admin in all_admin:
                add_notification_user(
                    admin.user, "The Testnet called <a href='{url}'" +
                    "target='_blank'>" +
                    testnet_to_report.testnet_name +
                    f"</a> got reported by " +
                    f"<code>{self.request.user.username}</code>",
                    "Testnet -1")
            messages.add_message(self.request, messages.SUCCESS, (
                "You reported a Testnet successfully")
                )

        if request.user.user_info.is_admin:
            return HttpResponseRedirect(reverse('administrate_testnet'))
        return HttpResponseRedirect(reverse('dashboard'))


class UpdateNotifications(LoginRequiredMixin, View):
    """
    Update Notifications from Unread to read
    """
    def get(self, request, id, *args, **kwargs):
        """
        Get the id notification to update and current logged user
        """
        queryset = Notifications.objects.filter(
            notification_owner=request.user.id)
        notif = get_object_or_404(queryset, id=id)
        if notif.read == 0:
            notif.read = 1
            notif.save()
        return HttpResponseRedirect(
            reverse('show_notifications', args=[request.user.username])
        )


class ShowTestnet(LoginRequiredMixin, generic.DetailView):
    """
    This view is used to display User Testnet
    """
    model = Testnet
    template_name = "showtestnet.html"
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_object(self, queryset=None):
        if self.slug_url_kwarg in self.kwargs:
            queryset = Testnet.objects.exclude(status_testnet=1).all()
            testnet = get_object_or_404(queryset, slug=self.kwargs['slug'])
            return super().get_object(queryset)
        else:
            return self.request.user


class ShowNotifications(LoginRequiredMixin, generic.DetailView):
    """
    This view is used to display All User Notifications
    """
    model = User
    template_name = "shownotifications.html"
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_object(self, queryset=None):
        if self.slug_url_kwarg in self.kwargs:
            return super().get_object(queryset)
        else:
            return self.request.user

    def get_context_data(self, **context):
        """
        return an updated context to shownotifications.html with
        unread/read notifications
        """
        notifications_user_unread = Notifications.objects.filter(
            notification_owner=self.request.user, read=0)[:10]
        notifications_user_read = Notifications.objects.filter(
            notification_owner=self.request.user, read=1)[:25]
        context.update({
                "notifications_user_unread": notifications_user_unread,
                "notifications_user_read": notifications_user_read,
            }
        )
        return context


class AdminitrateTestnet(generic.ListView):
    """
    This view is used to display all Testnet blocked
    If searching is called on URL, we display a searching on Testnet Table
    """
    model = Testnet
    template_name = "administratetestnet.html"
    paginate_by = 8

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        """
        Return query result about searching Testnet or display
        all original blocked Testnet
        """
        qs = super().get_queryset()
        search = self.request.GET.get("searching", None)
        if search:
            qs = qs.filter(
                Q(testnet_name__icontains=search)
                | Q(description__icontains=search)
                | Q(testnet_user__username__icontains=search)
                )
        else:
            qs = qs.filter(Q(author=F('testnet_user'))).filter(
                status_testnet=2
            )
        return qs

    def get_context_data(self, **context):
        """
        Return updated context to display the current search
        on administratetestnet.html
        """
        context = super().get_context_data(**context)
        context.update({
                "searching": self.request.GET.get("searching", None),
            }
        )
        return context


class AdminitrateUsers(generic.ListView):
    """
    This view is used to display all users blocked
    """
    model = UserInfo
    template_name = "administrateusers.html"
    paginate_by = 8

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        """
        Return query result about searching User or display all blocked Users
        """
        qs = super().get_queryset()
        search = self.request.GET.get("searching", None)
        if search:
            qs = qs.filter(user__username__icontains=search)
        else:
            qs = qs.filter(status=2)
        return qs

    def get_context_data(self, **context):
        """
        Return updated context to display the current search
        on administrateusers.html
        """
        context = super().get_context_data(**context)
        context.update({
                "searching": self.request.GET.get("searching", None),
            }
        )
        return context


class ShowNewTestnetAll(LoginRequiredMixin, generic.ListView):
    """
    This view is used to display All new Testnet or freshly updated
    """
    model = Testnet
    template_name = "shownewtestnetall.html"
    paginate_by = 8

    def get_queryset(self):
        """
        Get the informations for the form on shownewtestnetall.html
        Return the result of query on Testnet Table depending if
        "popular" exists
        if not, we display all Original Testnet registered on the app
        """
        qs = super().get_queryset()
        popular = self.request.GET.get("PopularTestnet", None)
        if popular:
            # Displaying only most popular Original Testnet from Not
            # Blocked Users
            qs = qs.exclude(testnet_user__user_info__status=2).all(
                ).filter(Q(author=F('testnet_user'))).order_by('-copied_nb')
        else:
            # Displaying only Original Testnet from Not Blocked Users
            qs = qs.exclude(testnet_user__user_info__status=2).all(
                ).filter(Q(author=F('testnet_user'))).order_by('-updated_on')
        return qs

    def get_context_data(self, **context):
        """
        Return context with PopularTestnet to get it into URL for paginate_by
        """
        context = super().get_context_data(**context)
        context.update({
                "PopularTestnet": 'ok',
            }
        )
        return context


class ShowTestnetall(LoginRequiredMixin, generic.ListView):
    """
    This view is used to display All Testnet from username on URL
    """
    model = Testnet
    template_name = "showtestnetall.html"
    paginate_by = 8

    def get(self, request, *args, **kwargs):
        """
        Retrives the user
        """
        self.testnet_user = self.get_user()
        return super().get(request, *args, **kwargs)

    def get_user(self):
        """
        Get the user into database from username from URL
        """
        if "username" in self.kwargs:
            return get_object_or_404(User, username=self.kwargs["username"])
        return self.request.user

    def get_queryset(self):
        """
        Get the informations for the form on showtestnetall.html
        Return the result of query on Testnet Table depending if "search"
        exists
        if not, we display all Testnet (copy and original) from the user on URL
        """
        qs = super().get_queryset()
        search = self.request.GET.get("searching", None)

        if search:
            '''If user/author of the testnet is blocked we exclude it'''
            qs = qs.exclude(testnet_user__user_info__status=2).filter(
                (Q(author=F('testnet_user'))) | Q(
                    testnet_user=self.testnet_user)
                )
            qs = qs.filter(
                Q(testnet_name__icontains=search)
                | Q(description__icontains=search)
                | Q(testnet_user__username__icontains=search)
            )
        else:
            qs = qs.exclude(testnet_user__user_info__status=2).filter(
                testnet_user=self.testnet_user)
        return qs

    def get_context_data(self, **context):
        """
        Return context with informations as searching (to keep the search
        if paginate_by)
        """
        context = super().get_context_data(**context)
        context.update({
                "testnet_username": self.kwargs["username"],
                "testnet_user": self.testnet_user,
                "searching": self.request.GET.get("searching", None),
            }
        )
        return context


class ShowUsers(LoginRequiredMixin, generic.DetailView):
    """
    This view is used to display User from the app (most active order_by 'exp')
    """
    model = User
    template_name = "users.html"
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_object(self, queryset=None):
        """
        Get the info of current logged user
        """
        if self.slug_url_kwarg in self.kwargs:
            return super().get_object(queryset)
        else:
            return self.request.user

    def get_context_data(self, **context):
        """
        Return context to the page users.html to display :
         - users most active on the app
         - result of searching
        """
        request = self.request
        object_user = self.request.user
        search = self.request.GET.get("searching_user", None)
        if search:
            show_users = UserInfo.objects.all(
                ).exclude(status=2).filter(
                    user__username__icontains=search)
        else:
            show_users = UserInfo.objects.exclude(
                status=2).all().order_by('-exp')[:20]
        context.update({
                "show_users": show_users,
                "searching_user": search,
            }
        )
        return context


class ShowDashboard(LoginRequiredMixin, generic.DetailView):
    """
    This view is used to display User Dashboard informations
    """
    model = User
    template_name = "dashboard.html"
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_object(self, queryset=None):
        """
        Get the info of current logged user
        """
        request = self.request
        object_user = self.request.user

        def check_user_info_exist(object_user):
            """
            return True if user info exist on Table UserInfo
            """
            user_info_exist = UserInfo.objects.filter(
                user_id=object_user.id).exists()
            return user_info_exist

        if not check_user_info_exist(object_user):
            # Creating user info table with basic value
            # We fill up the table with comun avatar image,
            # basic bio and 100 exp
            exp = 100
            bio = 'I just signed up to the App....'
            avatar = (
                "https://res.cloudinary.com/dqnhlza2r/image/upload/" +
                "v1674941682/ubcbtybbvu9b1zmvgiza.png")
            Creation_User_Info = UserInfo.objects.create(
                user_id=self.request.user.id,
                bio=bio,
                exp=exp,
                avatar=avatar
                )
            Creation_User_Info.save()
            # We make an welcome message to this new user
            messages.add_message(self.request, messages.SUCCESS, (
                "Welcome to our Dashboard, Please Edit your Profile!")
            )
            queryset = UserInfo.objects.all()
            # We identify the new User
            new_user = get_object_or_404(queryset, user_id=object_user.id)
            # We send a Notification to this new User
            add_notification_user(
                new_user.user, "Welcome to Test2Earn, " +
                "Your account has been " +
                "created successfully ",
                "Welcome Message +1")
        if self.slug_url_kwarg in self.kwargs:
            return super().get_object(queryset)
        else:
            return self.request.user
