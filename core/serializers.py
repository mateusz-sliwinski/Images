# 3rd-party
from rest_framework import serializers

# Project
from core.models import Images


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Images
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        user = self.context['request'].user
        is_enterprise = user.tier.name == 'Enterprise'

        if not is_enterprise:
            self.fields.pop('expired_time')
            self.fields.pop('thumbnail')
            self.fields.pop('owner')

        if is_enterprise:
            self.fields.pop('owner')
            self.fields.pop('thumbnail')
