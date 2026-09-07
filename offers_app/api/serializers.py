# Third-party
from rest_framework import serializers

# Local imports
from ..models import Offer, OfferDetail


class OfferDetailSerializer(serializers.ModelSerializer):
    """Full representation of one pricing tier."""

    class Meta:
        model = OfferDetail
        fields = [
            'id', 'title', 'revisions', 'delivery_time_in_days',
            'price', 'features', 'offer_type',
        ]


class OfferDetailLinkSerializer(serializers.ModelSerializer):
    """Compact id + url reference used inside the Offer response."""

    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']

    def get_url(self, obj):
        # Build the relative URL to the detail endpoint.
        return f'/offerdetails/{obj.id}/'


class OfferSerializer(serializers.ModelSerializer):
    """Read serializer for GET list/detail and the PATCH response."""

    details = OfferDetailLinkSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description',
            'created_at', 'updated_at', 'details',
            'min_price', 'min_delivery_time', 'user_details',
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

    def get_min_price(self, obj):
        # Return the lowest price across all pricing tiers.
        return obj.details.order_by('price').values_list(
            'price', flat=True
        ).first()

    def get_min_delivery_time(self, obj):
        # Return the fastest delivery time across all pricing tiers.
        return obj.details.order_by('delivery_time_in_days').values_list(
            'delivery_time_in_days', flat=True
        ).first()

    def get_user_details(self, obj):
        # Expose a small subset of the offer creator's profile.
        return {
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'username': obj.user.username,
        }


class OfferCreateUpdateSerializer(serializers.ModelSerializer):
    """Write serializer for POST (exactly 3 details) and PATCH (partial)."""

    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']

    def validate_details(self, value):
        # A new offer must be created with exactly three pricing tiers.
        if self.instance is None and len(value) != 3:
            raise serializers.ValidationError(
                'An offer must contain exactly 3 details.')
        # On update every detail must carry its offer_type as identifier.
        if self.instance is not None and any(
            not detail.get('offer_type') for detail in value
        ):
            raise serializers.ValidationError(
                'Each detail must include its "offer_type".')
        return value

    def create(self, validated_data):
        # Create the offer for the requesting user plus its three details.
        details_data = validated_data.pop('details')
        offer = Offer.objects.create(
            user=self.context['request'].user, **validated_data)
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)
        return offer

    def update(self, instance, validated_data):
        # Update the offer fields, then patch any details that were sent.
        details_data = validated_data.pop('details', None)
        instance = super().update(instance, validated_data)
        if details_data:
            self._update_details(instance, details_data)
        return instance

    def _update_details(self, instance, details_data):
        # Patch each detail in place, matched by its offer_type.
        for detail_data in details_data:
            detail = instance.details.filter(
                offer_type=detail_data.get('offer_type')).first()
            if not detail:
                continue
            for attr, value in detail_data.items():
                setattr(detail, attr, value)
            detail.save()
