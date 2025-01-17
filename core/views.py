from django.contrib.auth import login,logout
from django.db.models import Q
from django.shortcuts import render,redirect
from .forms import SignUpForm
from products.models import Product,Category
# Create your views here.
def frontpage(request):
	products = Product.objects.all()[0:8]
	return render(request, 'core/frontpage.html',{'products':products})
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in after signup
            return redirect('/')  # Redirect to homepage or another page
    else:
        form = SignUpForm()

    return render(request, 'core/signup.html', {'form': form})

def login_old(request):
    return render(request,'core/login.html')
def shop(request):
	categories = Category.objects.all()
	products = Product.objects.all()
	active_category = request.GET.get('category','')

	if active_category:
		products = products.filter(category__slug=active_category)


	query = request.GET.get('search', '')

	if query:
		products = products.filter(Q(name__icontains =query) | Q(description__icontains = query))

	context = {
	     'categories':categories,
	     'products':products,
	     'active_category':active_category,
	     'query': query
	}
	return render(request, 'core/shop.html',context)

def user_logout(request):
    logout(request)  # Log the user out
    return redirect('frontpage')