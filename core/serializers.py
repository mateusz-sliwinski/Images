# 3rd-party
from rest_framework import serializers

# Project
from core.models import Images


class ImageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Images model, customizing fields based on user's tier.

    This serializer customizes the serialization behavior of the Images model based on the user's
    membership tier. If the user is not in the 'Enterprise' tier, certain fields are excluded from
    serialization, such as 'expired_time', 'thumbnail', 'owner', and 'expired_link'.

    Attributes:
        Meta (class): A nested class defining metadata for the serializer, including the model and fields.

    Methods:
        __init__: Initializes the serializer and modifies the fields based on the user's membership tier.

    """
    class Meta:
        model = Images
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        """
        Initialize the serializer and modify fields based on the user's membership tier.

        If the user is not in the 'Enterprise' tier, specific fields are excluded from serialization.

        Args:
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        """
        super().__init__(*args, **kwargs)

        # Access the user and check if they are in the 'Enterprise' tier
        user = self.context['request'].user
        is_enterprise = user.tier.name == 'Enterprise'

        # Exclude certain fields based on the user's tier
        if not is_enterprise:
            self.fields.pop('expired_time')
            self.fields.pop('thumbnail')
            self.fields.pop('owner')
            self.fields.pop('expired_link')

        if is_enterprise:
            self.fields.pop('owner')
            self.fields.pop('thumbnail')
            self.fields.pop('expired_link')
