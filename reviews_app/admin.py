# Third-party
from django.contrib import admin

# Local imports
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('business_user', 'reviewer', 'rating', 'updated_at')
    list_filter = ('rating',)
