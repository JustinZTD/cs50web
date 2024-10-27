from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Bid, Listing, User, Comment


def index(request):
    active_listings = Listing.objects.filter(active=True)
    return render(request, "auctions/index.html", {
        "active_listings": active_listings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
    
@login_required
def create_listing(request):
    user = request.user
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        category = request.POST["category"]
        image = request.POST["image"]
        starting_bid = request.POST["starting_bid"]

        new_listing = Listing(title=title, description=description, category=category, image=image, owner=user, starting_bid=starting_bid)
        new_listing.save()
        return HttpResponseRedirect(reverse("index"))
    return render(request, "auctions/create_listing.html")

@login_required
def listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    bids = listing.bids.all().order_by('-amount')
    comments = Comment.objects.filter(listing=listing)
    highest_bid = listing.bids.order_by('-amount').first()
    current_price = highest_bid.amount if highest_bid else listing.starting_bid
    in_watchlist = request.user.watchlist.filter(id=listing.id).exists()
    is_owner = request.user == listing.owner
    is_winner = listing.active == False and highest_bid and highest_bid.bidder == request.user

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "bids": bids,
        "comments": comments,
        "current_price": current_price,
        "in_watchlist": in_watchlist,
        "is_owner": is_owner,
        "is_winner": is_winner
    })

@login_required
def add_to_watchlist(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    request.user.watchlist.add(listing)
    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

@login_required
def remove_from_watchlist(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    request.user.watchlist.remove(listing)
    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

@login_required
def place_bid(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    bid_amount = float(request.POST["bid"])
    highest_bid = listing.bids.order_by('-amount').first()
    current_price = highest_bid.amount if highest_bid else listing.starting_bid

    if bid_amount <= current_price:
        messages.error(request, "Bid must be higher than the current price.")
    else:
        new_bid = Bid(amount=bid_amount, bidder=request.user, listing=listing)
        new_bid.save()
        messages.success(request, "Bid placed successfully.")

    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

@login_required
def close_auction(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    if request.user == listing.owner:
        listing.active = False
        listing.save()
    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

@login_required
def add_comment(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    text = request.POST["content"]
    comment = Comment(text=text, commenter=request.user, listing=listing)
    comment.save()
    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

@login_required
def watchlist(request):
    watchlist_items = request.user.watchlist.all()
    return render(request, "auctions/watchlist.html", {
        "watchlist_items": watchlist_items
    })

def categories(request):
    categories = Listing.objects.values_list('category', flat=True).distinct()
    return render(request, "auctions/categories.html", {
        "categories": categories
    })

def category(request, category_name):
    listings = Listing.objects.filter(category=category_name, active=True)
    return render(request, "auctions/category.html", {
        "category": category_name,
        "listings": listings
    })
