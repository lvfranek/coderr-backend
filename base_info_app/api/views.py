# Third-party
from django.db.models import Avg
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

# Local imports
from offers_app.models import Offer
from profile_app.models import UserProfile
from reviews_app.models import Review


class BaseInfoView(APIView):
    """GET /api/base-info/ - public platform-wide statistics."""

    permission_classes = [AllowAny]

    def get(self, request):
        review_count = Review.objects.count()
        average_rating = Review.objects.aggregate(
            avg=Avg('rating'))['avg'] or 0
        business_profile_count = UserProfile.objects.filter(
            type=UserProfile.UserType.BUSINESS
        ).count()
        offer_count = Offer.objects.count()
        return Response({
            'review_count': review_count,
            'average_rating': round(average_rating, 1),
            'business_profile_count': business_profile_count,
            'offer_count': offer_count,
        })
