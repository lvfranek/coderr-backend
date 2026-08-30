# Third-party
from rest_framework import serializers

# Local imports
from ..models import Offer, OfferDetail


class OfferDetailSerializer(serializers.ModelSerializer):
    """Full representation of one pricing tier, used for create/update and
    for the standalone GET /api/offerdetails/{id}/ endpoint."""

    class Meta:
        model = OfferDetail
        fields = [
            'id', 'title', 'revisions', 'delivery_time_in_days',
            'price', 'features', 'offer_type',
        ]


class OfferDetailLinkSerializer(serializers.ModelSerializer):
    """Just id + url, used inside the Offer list/detail response."""

    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']

    def get_url(self, obj):
        return f'/offerdetails/{obj.id}/'


class OfferSerializer(serializers.ModelSerializer):
    """Used for GET list/detail and PATCH of a single Offer."""

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
        return obj.details.order_by('price').values_list('price', flat=True).first()

    def get_min_delivery_time(self, obj):
        return obj.details.order_by('delivery_time_in_days').values_list(
            'delivery_time_in_days', flat=True
        ).first()

    def get_user_details(self, obj):
        return {
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'username': obj.user.username,
        }


class OfferCreateUpdateSerializer(serializers.ModelSerializer):
    """Used for POST (requires exactly 3 details) and PATCH (partial details)."""

    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']

    def validate_details(self, value):
        if self.instance is None and len(value) != 3:
            raise serializers.ValidationError(
                'An offer must contain exactly 3 details.')
        return value

    def create(self, validated_data):
        details_data = validated_data.pop('details')
        offer = Offer.objects.create(
            user=self.context['request'].user, **validated_data)
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)
        return offer

    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', None)
        instance = super().update(instance, validated_data)
        if details_data:
            self._update_details(instance, details_data)
        return instance

    def _update_details(self, instance, details_data):
        for detail_data in details_data:
            offer_type = detail_data.get('offer_type')
            detail = instance.details.filter(offer_type=offer_type).first()
            if detail:
                for attr, value in detail_data.items():
                    setattr(detail, attr, value)
                detail.save()
