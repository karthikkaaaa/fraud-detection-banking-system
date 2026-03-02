
from django.contrib import admin
from .models import CustomerProfile, Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'location', 'risk_score', 'status')
    list_filter = ('status',)
    search_fields = ('user__username',)


admin.site.register(CustomerProfile)