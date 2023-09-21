# Django
from django.apps import apps
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def create_tiers_and_superuser(sender, **kwargs):
    """
    Signal handler to create default tiers and a superuser after migrations.

    This function is a signal handler for the 'post_migrate' signal. It creates default membership tiers
    ('Basic', 'Premium', 'Enterprise') and a superuser ('admin') if they do not already exist in the database.

    Args:
        sender: The sender of the signal.
        kwargs: Additional keyword arguments.

    """
    User = apps.get_model('core', 'User')
    Tier = apps.get_model('core', 'Tier')

    # Create a superuser if no users exist
    if not User.objects.all():
        superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin')
        superuser.save()

    # Create default tiers if they don't exist
    if not Tier.objects.all():
        tier_basic = Tier.objects.create(
            name='Basic',
            thumbnails=False,
            original_photo=False,
            expiring_link=False,
        )
        tier_premium = Tier.objects.create(
            name='Premium',
            thumbnails=True,
            original_photo=True,
            expiring_link=False,
        )
        tier_enterprise = Tier.objects.create(
            name='Enterprise',
            thumbnails=True,
            original_photo=True,
            expiring_link=True,
        )
        tier_basic.save()
        tier_premium.save()
        tier_enterprise.save()
