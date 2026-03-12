from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):
    bio = models.TextField(blank=True, default="")
    profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True)

    def __str__(self):
        return self.username


class Collection(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="collections")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    category = models.CharField(max_length=100, blank=True, default="")
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