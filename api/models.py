from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator
import decimal


class User(AbstractUser):
    """
    Custom user model with role-based access control.
    Roles: viewer < analyst < admin
    """
    class Role(models.TextChoices):
        VIEWER   = 'viewer',   'Viewer'
        ANALYST  = 'analyst',  'Analyst'
        ADMIN    = 'admin',    'Admin'

    role   = models.CharField(max_length=10, choices=Role.choices, default=Role.VIEWER)
    is_active = models.BooleanField(default=True)

    # Convenience properties used throughout views/permissions
    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_analyst(self):
        return self.role in (self.Role.ANALYST, self.Role.ADMIN)

    def __str__(self):
        return f"{self.username} ({self.role})"


class FinancialRecord(models.Model):
    """
    A single financial entry — income or expense.
    """
    class EntryType(models.TextChoices):
        INCOME  = 'income',  'Income'
        EXPENSE = 'expense', 'Expense'

    class Category(models.TextChoices):
        SALARY     = 'salary',     'Salary'
        INVESTMENT = 'investment', 'Investment'
        FOOD       = 'food',       'Food'
        TRANSPORT  = 'transport',  'Transport'
        UTILITIES  = 'utilities',  'Utilities'
        HEALTHCARE = 'healthcare', 'Healthcare'
        EDUCATION  = 'education',  'Education'
        OTHER      = 'other',      'Other'

    created_by  = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='records'
    )
    amount      = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(decimal.Decimal('0.01'))]
    )
    entry_type  = models.CharField(max_length=10, choices=EntryType.choices)
    category    = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHER)
    date        = models.DateField()
    description = models.TextField(blank=True, default='')
    is_deleted  = models.BooleanField(default=False)   # soft delete flag
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.entry_type} | {self.category} | {self.amount}"
    

