from django.db import models
from django.conf import settings


class Score(models.Model):
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="mushroom_scores",
	)
	score = models.PositiveIntegerField()
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-score", "-created_at"]


class Money(models.Model):
	user = models.OneToOneField(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		related_name="mushroom_money",
	)
	amount = models.PositiveIntegerField(default=200)
	updated_at = models.DateTimeField(auto_now=True)
