from django.http import HttpResponse
from django.shortcuts import render, redirect

from cart.models import CartItem
from .forms import OrderForm


def place_order(request):
    current_user = request.user

    # If the cart items count is less than or equal to 0,
    # redirect to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect("store")

    if request.method == "POST":
        form = OrderForm(request.POST)
