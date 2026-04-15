"""
Core models for users and tenants.
"""
import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class Tenant(models.Model):
    """
    Tenant model for multi-tenancy support.
    Each organization/company using the platform is a tenant.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100, unique=True)
    nit = models.CharField("NIT/RUT", max_length=50, blank=True, help_text="Tax identification number")
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)

    # Subscription
    is_active = models.BooleanField(default=True)
    subscription_plan = models.CharField(
        max_length=50,
        choices=[
            ("free", "Free"),
            ("starter", "Starter"),
            ("professional", "Professional"),
            ("enterprise", "Enterprise"),
        ],
        default="free",
    )
    subscription_expires_at = models.DateTimeField(null=True, blank=True)

    # Settings
    settings = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Tenant"
        verbose_name_plural = "Tenants"

    def __str__(self) -> str:
        return self.name

    def is_subscription_valid(self) -> bool:
        """Check if tenant subscription is still valid."""
        if self.subscription_plan == "free":
            return True
        if not self.subscription_expires_at:
            return False
        return self.subscription_expires_at > timezone.now()


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication."""

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user."""
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model with email-based authentication.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )

    # Authentication
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, blank=True)

    # Profile
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)

    # Roles
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Roles within the tenant
    ROLE_CHOICES = [
        ("owner", "Owner"),
        ("admin", "Admin"),
        ("manager", "Manager"),
        ("operator", "Operator"),
        ("viewer", "Viewer"),
    ]
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="viewer",
    )

    # Notifications
    notification_preferences = models.JSONField(default=dict, blank=True)

    # Timestamps
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ["email"]
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self) -> str:
        return self.email

    @property
    def full_name(self) -> str:
        """Return user's full name."""
        return f"{self.first_name} {self.last_name}".strip() or self.email

    @property
    def short_name(self) -> str:
        """Return user's first name or email prefix."""
        return self.first_name or self.email.split("@")[0]

    def is_owner(self) -> bool:
        """Check if user is tenant owner."""
        return self.role == "owner"

    def is_admin(self) -> bool:
        """Check if user has admin privileges."""
        return self.role in ("owner", "admin")

    def has_tenant_access(self, tenant) -> bool:
        """Check if user has access to given tenant."""
        if self.is_superuser:
            return True
        return self.tenant == tenant


class UserActivityLog(models.Model):
    """Log of user activities for audit purposes."""

    ACTION_TYPES = [
        ("login", "Login"),
        ("logout", "Logout"),
        ("create", "Create"),
        ("update", "Update"),
        ("delete", "Delete"),
        ("view", "View"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="activity_logs",
    )
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.SET_NULL,
        null=True,
        related_name="activity_logs",
    )

    action = models.CharField(max_length=20, choices=ACTION_TYPES)
    model_type = models.CharField(max_length=100, blank=True)
    model_id = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    metadata = models.JSONField(default=dict, blank=True)

    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "User Activity Log"
        verbose_name_plural = "User Activity Logs"
        indexes = [
            models.Index(fields=["user", "-timestamp"]),
            models.Index(fields=["tenant", "-timestamp"]),
        ]

    def __str__(self) -> str:
        return f"{self.user} - {self.action} @ {self.timestamp}"