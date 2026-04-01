from products.models import Category


def categories(request):
    """
    Context processor to make categories available in all templates.
    """
    return {
        'all_categories': Category.objects.all()
    }
