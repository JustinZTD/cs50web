from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    watchlist = models.ManyToManyField("Listing", related_name="watchers", blank=True)

class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    category = models.CharField(max_length=64)
    image = models.URLField(blank=True)
    active = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    starting_bid = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    def __str__(self):
        return self.title

    def get_highest_bid(self):
        return self.bids.order_by('-amount').first()

class Bid(models.Model):
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")

    def __str__(self):
        return f"{self.amount} by {self.bidder.username}"

class Comment(models.Model):
    text = models.TextField()
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")

    def __str__(self):
        return self.text
    