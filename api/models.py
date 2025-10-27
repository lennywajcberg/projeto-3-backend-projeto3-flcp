from django.db import models

class Favorite(models.Model):
    client_id = models.CharField(max_length=36) 
    symbol = models.CharField(max_length=16)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["client_id", "symbol"], name="uniq_client_symbol")
        ]

    def __str__(self):
        return f"{self.client_id}:{self.symbol}"
