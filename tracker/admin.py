from django.contrib import admin

from tracker.models import Cart, Item


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    pass


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    pass
