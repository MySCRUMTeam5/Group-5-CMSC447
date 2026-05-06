from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):
    bio = models.TextField(blank=True, default="")
    profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True)

    def __str__(self):
        return self.username


class Collection(models.Model):
    COLLECTION_TYPES = [
        ("video_games", "Video Games"),
        ("trading_cards", "Trading Cards"),
        ("comics", "Comics"),
        ("funko_pops", "Funko Pops"),
        ("lego_sets", "LEGO Sets"),
        ("sports_cards", "Sports Cards"),
        ("music", "Music"),
        ("movies", "Movies"),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="collections")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    category = models.CharField(max_length=100, blank=True, default="")
    collection_type = models.CharField(max_length=50, choices=COLLECTION_TYPES, default="video_games")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=False)
    shared_with = models.ManyToManyField(User, blank=True, related_name="shared_collections")

    class Meta:
        ordering = ["-updated_at"]
        unique_together = ["owner", "name"]

    def __str__(self):
        return f"{self.name} ({self.owner.username})"

    @property
    def item_count(self):
        return self.items.count()

    @property
    def total_value(self):
        return self.items.aggregate(total=models.Sum("purchase_price"))["total"] or 0


class CollectionRating(models.Model):
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name="ratings")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ratings_given")
    score = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["collection", "user"]


# Base Item Model (shared fields: condition, price, value are here)
class Item(models.Model):
    class Condition(models.TextChoices):
        MINT = "mint", "Mint"
        NEAR_MINT = "near_mint", "Near Mint"
        EXCELLENT = "excellent", "Excellent"
        GOOD = "good", "Good"
        FAIR = "fair", "Fair"
        POOR = "poor", "Poor"

    class UsageStatus(models.TextChoices):
        IN_USE = "in_use", "In Use"
        STORED = "stored", "Stored / Display"
        LENT_OUT = "lent_out", "Lent Out"
        NOT_USED = "not_used", "Not Used"

    class ListingStatus(models.TextChoices):
        NOT_FOR_SALE = "not_for_sale", "Not For Sale"
        FOR_SALE = "for_sale", "For Sale"
        SOLD = "sold", "Sold"

    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    category = models.CharField(max_length=100, blank=True, default="")
    condition = models.CharField(max_length=20, choices=Condition.choices, default=Condition.GOOD)
    quantity = models.PositiveIntegerField(default=1)
    image = models.ImageField(upload_to="item_images/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    barcode = models.CharField(max_length=100, blank=True, default="", db_index=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    current_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    purchase_date = models.DateField(blank=True, null=True)
    usage_status = models.CharField(max_length=20, choices=UsageStatus.choices, default=UsageStatus.STORED)
    listing_status = models.CharField(max_length=20, choices=ListingStatus.choices, default=ListingStatus.NOT_FOR_SALE)
    asking_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_special_edition = models.BooleanField(default=False)
    edition_details = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.collection.name})"


# Video Games
class VideoGameItem(models.Model):
    item = models.OneToOneField(Item, on_delete=models.CASCADE, related_name="video_game")
    platform = models.CharField(max_length=100, blank=True, default="")
    genre = models.CharField(max_length=100, blank=True, default="")
    completeness = models.CharField(max_length=100, blank=True, default="")
    play_status = models.CharField(max_length=50, blank=True, default="")

    def __str__(self):
        return f"Game: {self.item.name}"


# Trading Cards
class TradingCardItem(models.Model):
    item = models.OneToOneField(Item, on_delete=models.CASCADE, related_name="trading_card")
    series = models.CharField(max_length=255, blank=True, default="")
    set_name = models.CharField(max_length=255, blank=True, default="")
    card_number = models.CharField(max_length=50, blank=True, default="")
    grade = models.CharField(max_length=50, blank=True, default="")

    def __str__(self):
        return f"Card: {self.item.name}"


# Comics
class ComicItem(models.Model):
    item = models.OneToOneField(Item, on_delete=models.CASCADE, related_name="comic")
    publisher = models.CharField(max_length=255, blank=True, default="")
    issue_title = models.CharField(max_length=255, blank=True, default="")
    issue_number = models.CharField(max_length=20, blank=True, default="")
    grade = models.CharField(max_length=50, blank=True, default="")
    read_status = models.CharField(max_length=50, blank=True, default="")

    def __str__(self):
        return f"Comic: {self.item.name}"


# Funko Pops
class FunkoPopItem(models.Model):
    item = models.OneToOneField(Item, on_delete=models.CASCADE, related_name="funko_pop")
    series = models.CharField(max_length=255, blank=True, default="")
    box_number = models.CharField(max_length=50, blank=True, default="")
    completeness = models.CharField(max_length=100, blank=True, default="")
    exclusive = models.BooleanField(default=False)

    def __str__(self):
        return f"Funko: {self.item.name}"


# LEGO Sets
class LegoSetItem(models.Model):
    item = models.OneToOneField(Item, on_delete=models.CASCADE, related_name="lego_set")
    series = models.CharField(max_length=255, blank=True, default="")
    set_number = models.CharField(max_length=50, blank=True, default="")
    completeness = models.CharField(max_length=100, blank=True, default="")
    piece_count = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"LEGO: {self.item.name}"


# Sports Cards
class SportsCardItem(models.Model):
    item = models.OneToOneField(Item, on_delete=models.CASCADE, related_name="sports_card")
    sport = models.CharField(max_length=100, blank=True, default="")
    player_name = models.CharField(max_length=255, blank=True, default="")
    card_number = models.CharField(max_length=50, blank=True, default="")
    year = models.IntegerField(blank=True, null=True)
    grade = models.CharField(max_length=50, blank=True, default="")

    def __str__(self):
        return f"Sports Card: {self.item.name}"


# Music
class MusicItem(models.Model):
    item = models.OneToOneField(Item, on_delete=models.CASCADE, related_name="music")
    artist = models.CharField(max_length=255, blank=True, default="")
    album_title = models.CharField(max_length=255, blank=True, default="")
    format = models.CharField(max_length=50, blank=True, default="")
    genre = models.CharField(max_length=100, blank=True, default="")

    def __str__(self):
        return f"Music: {self.item.name}"


# Movies
class MovieItem(models.Model):
    item = models.OneToOneField(Item, on_delete=models.CASCADE, related_name="movie")
    title = models.CharField(max_length=255, blank=True, default="")
    format = models.CharField(max_length=50, blank=True, default="")
    genre = models.CharField(max_length=100, blank=True, default="")
    director = models.CharField(max_length=255, blank=True, default="")
    watched_status = models.CharField(max_length=50, blank=True, default="")

    def __str__(self):
        return f"Movie: {self.item.name}"


class WishlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlist")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    collection_type = models.CharField(max_length=50, choices=Collection.COLLECTION_TYPES, default="video_games")
    notes = models.TextField(blank=True, default="")
    price_target = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    link = models.URLField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.user.username})"


class DuplicateFlag(models.Model):
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name="duplicate_flags")
    item_a = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="duplicate_flags_as_a")
    item_b = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="duplicate_flags_as_b")
    confidence = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    is_resolved = models.BooleanField(default=False)
    is_confirmed_duplicate = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["item_a", "item_b"]