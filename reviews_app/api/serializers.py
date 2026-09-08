from rest_framework import serializers

from ..models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """Used for list/create. reviewer is set automatically from the request."""

    class Meta:
        model = Review
        fields = [
            'id', 'business_user', 'reviewer', 'rating', 'description',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['reviewer', 'created_at', 'updated_at']

    def validate(self, attrs):
        """A reviewer may leave only one review per business user."""
        request = self.context['request']
        business_user = attrs.get('business_user')
        if self.instance is None and Review.objects.filter(
            business_user=business_user, reviewer=request.user
        ).exists():
            raise serializers.ValidationError(
                'You have already reviewed this business user.'
            )
        return attrs

    def create(self, validated_data):
        """The reviewer is always the requesting user, never client input."""
        validated_data['reviewer'] = self.context['request'].user
        return super().create(validated_data)


class ReviewUpdateSerializer(serializers.ModelSerializer):
    """Used for PATCH - only rating and description are editable.

    The response still returns the full review representation.
    """

    class Meta:
        model = Review
        fields = [
            'id', 'business_user', 'reviewer', 'rating', 'description',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'business_user', 'reviewer', 'created_at', 'updated_at',
        ]
