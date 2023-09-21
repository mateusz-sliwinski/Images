# Django
from django.contrib import admin

# Project
from core.models import ExpiredLink
from core.models import Images
from core.models import Thumbnail
from core.models import Tier
from core.models import User


# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):  # noqa D101
    list_display = [
        'id',
        'username',
        'tier',
    ]
    list_filter = [
        'tier',
    ]
    list_display_links = (
        'id',
    )
    list_editable = [
        'username',
        'tier',
    ]


@admin.register(Tier)
class TierAdmin(admin.ModelAdmin):  # noqa D101
    list_display = [
        'id',
        'thumbnails',
        'name',
        'original_photo',
        'expiring_link'
    ]
    list_filter = [
        'name',
    ]
    list_display_links = (
        'id',
    )
    list_editable = [
        'original_photo',
        'expiring_link',
        'name',
        'thumbnails',
    ]


@admin.register(Images)
class ImagesAdmin(admin.ModelAdmin):
    pass


@admin.register(Thumbnail)
class ThumbAdmin(admin.ModelAdmin):
    pass


@admin.register(ExpiredLink)
class ExpiredAdmin(admin.ModelAdmin):
    pass
