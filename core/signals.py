# Django
from django.apps import apps
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def create_tiers_and_superuser(sender, **kwargs):
    User = apps.get_model('core', 'User')
    Tier = apps.get_model('core', 'Tier')

    if not User.objects.all():
        superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin')
        superuser.save()

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
