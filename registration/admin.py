def dashboard_data(self, request):
    from django.db.models import Q
    from booking.models import Booking
    from review.models import Review
    from registration.models import User

    category = request.GET.get('category')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    search = request.GET.get('search', '').strip()

    filters = {}
    review_filters = {}
    user_filters = Q()
    
    if category and category != 'all':
        filters['service_provider__category__category'] = category
        review_filters['service_provider__category__category'] = category

    if start_date:
        filters['date__gte'] = start_date
    if end_date:
        filters['date__lte'] = end_date

    if search:
        user_filters |= Q(first_name__icontains=search)
        user_filters |= Q(last_name__icontains=search)
        user_filters |= Q(contact__icontains=search)

    user_ids = User.objects.filter(user_filters).values_list('id', flat=True)
    filters['service_provider__id__in'] = user_ids

    bookings = Booking.objects.filter(**filters)
    reviews = Review.objects.filter(**review_filters)

    bookings_by_provider = bookings.values(
        'service_provider__first_name', 'service_provider__last_name'
    ).annotate(count=Count('id')).order_by('-count')[:10]

    ratings_by_provider = reviews.values(
        'service_provider__first_name', 'service_provider__last_name'
    ).annotate(avg_rating=Avg('rating')).order_by('-avg_rating')[:10]

    bookings_over_time = bookings.values('date').annotate(count=Count('id')).order_by('date')

    user_type_counts = User.objects.values('user_type').annotate(count=Count('id'))

    def full_name(obj):
        return f"{obj['service_provider__first_name']} {obj['service_provider__last_name']}"

    return JsonResponse({
        'bookings_by_provider': [{'name': full_name(b), 'count': b['count']} for b in bookings_by_provider],
        'ratings_by_provider': [{'name': full_name(r), 'avg_rating': r['avg_rating']} for r in ratings_by_provider],
        'bookings_over_time': list(bookings_over_time),
        'user_type_counts': list(user_type_counts),
    })
