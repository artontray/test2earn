from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django_extensions.db.fields import AutoSlugField
from cloudinary.models import CloudinaryField
from django.utils.functional import cached_property
from django.conf import settings


# Status User :
# - 0 : Normal User
# - 1 : Normal User with Admin role
# - 2 : Blocked User, cannot do anything on the app
STATUS = ((0, "User"), (1, "Admin"), (2, "Blocked"))
# Notification Status
# - 0 :  Unread Notification : so can be transfered to "Read"
# - 1 :  Read Notification : cannot be transfered to "Unread" again
READ = ((0, "Unread"), (1, "Read"))
# Testnet Status :
# 0 : Published on the app
# 2 : Reported, so not available for copy or edit
STATUS_TESTNET = ((0, "published"), (2, "Reported"))


class Testnet(models.Model):
    """
    Model for Testnet Table
    """
    testnet_name = models.CharField(
        max_length=60, unique=True, blank=False, null=False, db_index=True)
    slug = AutoSlugField(populate_from='testnet_name', unique=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="testnet_author")
    testnet_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="testnet_user")
    slug_original = models.CharField(max_length=60, blank=False, null=False)
    network_name = models.CharField(max_length=55, blank=False, null=False)
    network_status = models.CharField(max_length=25, blank=False, null=False)
    description = models.TextField(db_index=True, blank=False, null=False)
    category = models.CharField(max_length=35, blank=False, null=False)
    twitter = models.CharField(max_length=255, blank=True)
    facebook = models.CharField(max_length=255, blank=True)
    website = models.CharField(max_length=255, blank=True)
    github = models.CharField(max_length=255, blank=True)
    discord = models.CharField(max_length=255, blank=True)
    telegram = models.CharField(max_length=255, blank=True)
    instagram = models.CharField(max_length=255, blank=True)
    youtube = models.CharField(max_length=255, blank=True)
    whitepaper = models.CharField(max_length=255, blank=True)
    browser = models.CharField(max_length=25, blank=True)
    tasks_description = models.TextField()
    wallet1_name = models.CharField(max_length=25, blank=True)
    wallet1_type = models.CharField(max_length=25, blank=True)
    wallet1_link = models.CharField(max_length=255, blank=True)
    wallet1_adress = models.CharField(max_length=255, blank=True)
    wallet1_seed = models.CharField(max_length=255, blank=True)
    wallet1_priv_key = models.CharField(max_length=255, blank=True)
    wallet1_password = models.CharField(max_length=30, blank=True)
    wallet1_session = models.CharField(max_length=30, blank=True)
    wallet1_clue = models.TextField(blank=True)
    wallet2_name = models.CharField(max_length=25, blank=True)
    wallet2_type = models.CharField(max_length=25, blank=True)
    wallet2_link = models.CharField(max_length=255, blank=True)
    wallet2_adress = models.CharField(max_length=255, blank=True)
    wallet2_seed = models.CharField(max_length=255, blank=True)
    wallet2_priv_key = models.CharField(max_length=255, blank=True)
    wallet2_password = models.CharField(max_length=30, blank=True)
    wallet2_session = models.CharField(max_length=30, blank=True)
    wallet2_clue = models.TextField(blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    copied_nb = models.IntegerField(default=0, blank=True)
    twitter_user = models.CharField(max_length=21, blank=True)
    email_user = models.EmailField(blank=True)
    website_user = models.CharField(max_length=255, blank=True)
    github_user = models.CharField(max_length=25, blank=True)
    discord_user = models.CharField(max_length=25, blank=True)
    telegram_user = models.CharField(max_length=25, blank=True)
    tasks_results = models.TextField(blank=True)
    status_testnet = models.IntegerField(choices=STATUS_TESTNET, default=0)

    class Meta:
        """
        To display the testnet order by created_on
        """
        ordering = ['-created_on']

    def __str__(self):
        return f"{self.testnet_name}"

    @property
    def time_copied(self):
        return self.copied_nb


class Notifications(models.Model):
    """
    Model for Notifications Table
    """
    notification_owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notification_owner")
    title = models.CharField(max_length=35)
    message = models.TextField()
    created_on = models.DateTimeField(auto_now=True)
    read = models.IntegerField(choices=READ, default=0)

    class Meta:
        """
        To display the user notifications order by created_on
        """
        ordering = ['-created_on']

    def __str__(self):
        return f"{self.title}"


class UserInfo(models.Model):
    """
    Model for User Info Table
    """
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="user_info")
    bio = models.TextField()
    exp = models.IntegerField(default=100)
    status = models.IntegerField(choices=STATUS, default=0)
    debank = models.CharField(max_length=255, blank=True)
    avatar = CloudinaryField('image', default='placeholder')
    following = models.ManyToManyField(
        User, related_name='following', blank=True)

    class Meta:
        """
        To display the user Info by created_on in descending order
        """
        ordering = ['-user__date_joined']

    @property
    def user_follows(self):
        return self.user.following

    @property
    def is_admin(self):
        """
        To display is User is admin or not
        """
        if self.status == 1:
            return True
        else:
            return False

    @property
    def created_on(self):
        return self.user.date_joined

    @property
    def get_object_user(self):
        return self.user

    @property
    def user_status(self):
        return self.status

    @property
    def nb_following(self):
        """
        Return following Users numbers for a User
        """
        if not hasattr(self, "_nb_following"):
            self._nb_following = self.following.count()
        return self._nb_following

    @property
    def nb_followers(self):
        """
        Return Followers Users number
        """
        if not hasattr(self, "_nb_followers"):
            self._nb_followers = UserInfo.objects.all().filter(
                following=self.user.id).count()
        return self._nb_followers

    @property
    def nb_testnet(self):
        """
        Return number of Testnet for the current user
        """
        if not hasattr(self, "_nb_testnet"):
            self._nb_testnet = Testnet.objects.exclude(
                status_testnet=1).all().filter(
                    author=self.user.id, testnet_user=self.user.id
                    ).count()

        return self._nb_testnet

    # If user has more than 1 Testnet Registered we display a Button
    # "Show More" on Dashboard section
    @property
    def show_testnet_user(self):
        """
        To display all Testnet with Testnet User == Current User
        """
        if not hasattr(self, "_show_testnet_user"):
            self._show_testnet_user = Testnet.objects.exclude(
                testnet_user__user_info__status=2).all().filter(
                        testnet_user=self.user.id).all()
        return self._show_testnet_user

    @property
    def nb_copied_testnet(self):
        """
        Return number of time user copied a Testnet from other User
        """
        if not hasattr(self, "_nb_copied_testnet"):
            self._nb_copied_testnet = Testnet.objects.all().exclude(
                author=self.user.id).filter(
                    testnet_user=self.user.id).count()

        return self._nb_copied_testnet

    @property
    def nb_copied_original_testnet_from_user(self):
        """
        Return number of original Testnet created by a User
        """
        if not hasattr(self, "_nb_copied_original_testnet_from_user"):
            self._nb_copied_original_testnet_from_user = Testnet.objects.all(
                ).exclude(testnet_user=self.user.id).filter(
                        author=self.user.id).count()

        return self._nb_copied_original_testnet_from_user

    @property
    def nb_testnet_copied_from_this_author(self):
        """
        Return Number of copies that Users made from a specific
        testnet from current user as an author
        """
        if not hasattr(self, "_nb_testnet_copied_from_this_author"):
            self._nb_testnet_copied_from_this_author = Testnet.objects.all(
                ).exclude(
                    testnet_user=self.user.id).filter(
                            author=self.user.id).count()

        return self._nb_testnet_copied_from_this_author

    @property
    def nb_notifications(self):
        """
        Return Number of notifications from a User
        """
        if not hasattr(self, "_nb_notifications"):
            self._nb_notifications = Notifications.objects.all(
                ).filter(
                        notification_owner=self.user.id, read=0).count()

        return self._nb_notifications

    @property
    def last_testnet(self):
        """
        Return Last testnet's name created by a User ,
        If none -> "Not created yet"
        """
        if not hasattr(self, "_last_testnet"):
            self._last_testnet = Testnet.objects.all(
                ).filter(
                    author=self.user, testnet_user=self.user,
                    status_testnet=0).first()
            if self._last_testnet:
                self._last_testnet = self._last_testnet.testnet_name
            else:
                self._last_testnet = 'Not created yet'
        return self._last_testnet

    @property
    def last_testnet_slug(self):
        """
        Return Last testnet slug
        """
        if not hasattr(self, "_last_testnet_slug"):
            self._last_testnet_slug = Testnet.objects.all(
                ).filter(
                    author=self.user, testnet_user=self.user,
                    status_testnet=0).first()
            if self._last_testnet_slug:
                self._last_testnet_slug = self._last_testnet_slug.slug
            else:
                self._last_testnet_slug = ''
        return self._last_testnet_slug

    @property
    def get_level_user(self):
        """
        Return the level of a User (int)
        """
        Level_user = 1
        Current_Level_XP = settings.EXP_FOR_LEVEL1
        exp = self.exp
        if exp > settings.EXP_FOR_LEVEL1:
            Current_Level_XP = (
                settings.EXP_FOR_LEVEL1 * settings.COEFF_FOR_LEVEL_UP)
            while exp > Current_Level_XP:
                Level_user += 1
                Current_Level_XP = (
                    Current_Level_XP * settings.COEFF_FOR_LEVEL_UP)

        if not hasattr(self, "_get_level_user"):
            self._get_level_user = Level_user

        return self._get_level_user

    @property
    def current_nb_testnet_to_do(self):
        """
        Return the current number of Testnet to do for a User to for Level Up
        """
        if not hasattr(self, "_current_nb_testnet_to_do"):
            self._current_nb_testnet_to_do = int(
                settings.TESTNET_CREATED_FOR_LEVEL1+(
                    settings.COEFF_FOR_LEVEL_UP**self.get_level_user))
        return self._current_nb_testnet_to_do

    @property
    def current_level_xp_max(self):
        """
        Return the current Level of EXP to reach for a User to Level up
        """
        if not hasattr(self, "_current_level_xp_max"):
            self._current_level_xp_max = int(
                settings.EXP_FOR_LEVEL1*(
                    settings.COEFF_FOR_LEVEL_UP**self.get_level_user))

        return self._current_level_xp_max

    @property
    def pourc_accomplished_exp(self):
        """
        Return the % of accomplishment to reah Level Up
        """
        return (self.exp/self.current_level_xp_max)*100

    @property
    def pourc_accomplished_testnet(self):
        """
        Return the % of accomplishment of number of Testnet a User
        need to get mission accomplish
        """
        result = int((self.nb_testnet / self.current_nb_testnet_to_do)*100)
        if result >= 100:
            return 100
        return result

    @property
    def current_follow_max(self):
        """
        Return the current number of followers a User need
        to get mission accomplish
        """
        return int(settings.FOLLOWERS_FOR_LEVEL1+(
            settings.COEFF_FOR_LEVEL_UP**self.get_level_user)
            )

    @property
    def pourc_accomplished_followers(self):
        """
        Return the % of accomplishment of number of Followers
        a User need to get mission accomplish
        """
        result = int((self.nb_followers / self.current_follow_max)*100)
        if result >= 100:
            return 100
        return result

    @property
    def current_copied_testnet_max(self):
        """
        Return the current number of copied Testnet from a User
        """
        return int(settings.TESTNET_TO_COPY_FOR_LEVEL1+(
            settings.COEFF_FOR_LEVEL_UP**self.get_level_user)
                )

    @property
    def pourc_accomplished_copied_testnet(self):
        """
        Return the % of accomplishment of number of Copied Testnet a
        User need to get mission accomplish
        """
        nb_copied = self.nb_copied_original_testnet_from_user
        result = int((
            nb_copied / self.current_copied_testnet_max)*100
            )
        if result >= 100:
            return 100
        return result

    def __str__(self):
        return f"{self.user}"


class CheckList(models.Model):
    """
    Model for CheckList Info Table
    """
    checklist_owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="checklist_owner")
    title = models.CharField(max_length=35)
    message = models.TextField()
    created_on = models.DateTimeField(auto_now=True)

    class Meta:
        """
        To display the user checklist order by created_on
        """
        ordering = ['-created_on']

    def __str__(self):
        return f"{self.title}"
