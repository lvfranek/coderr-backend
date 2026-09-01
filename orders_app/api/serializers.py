# Third-party
from rest_framework import serializers

# Local imports
from offers_app.models import OfferDetail
from profile_app.models import UserProfile
from ..models import Order


class OrderSerializer(serializers.ModelSerializer):
    """Full representation of an order, used for list/retrieve/patch."""

    class Meta:
        model = Order
        fields = [
            'id', 'customer_user', 'business_user', 'title', 'revisions',
            'delivery_time_in_days', 'price', 'features', 'offer_type',
            'status', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'customer_user', 'business_user', 'title', 'revisions',
            'delivery_time_in_days', 'price', 'features', 'offer_type',
            'created_at', 'updated_at',
        ]


class OrderCreateSerializer(serializers.Serializer):
    """Creates an Order as a snapshot of the chosen OfferDetail."""

    offer_detail_id = serializers.IntegerField()

    def validate_offer_detail_id(self, value):
        if not OfferDetail.objects.filter(id=value).exists():
            raise serializers.ValidationError('OfferDetail not found.')
        return value

    def create(self, validated_data):
        detail = OfferDetail.objects.get(id=validated_data['offer_detail_id'])
        customer = self.context['request'].user
        return Order.objects.create(
            customer_user=customer,
            business_user=detail.offer.user,
            title=detail.title,
            revisions=detail.revisions,
            delivery_time_in_days=detail.delivery_time_in_days,
            price=detail.price,
            features=detail.features,
            offer_type=detail.offer_type,
        )
