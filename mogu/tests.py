import json
import re

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .models import Money, Score


class GameDataSyncTests(TestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(username="player", password="test-pass-123")
		self.client.force_login(self.user)

	def test_authenticated_user_can_sync_money_and_score(self):
		response = self.client.post(
			reverse("game_sync"),
			data=json.dumps({"money": 275, "score": 48}),
			content_type="application/json",
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(Money.objects.get(user=self.user).amount, 275)
		self.assertEqual(Score.objects.get(user=self.user).score, 48)

	def test_invalid_sync_payload_does_not_partially_update(self):
		response = self.client.post(
			reverse("game_sync"),
			data=json.dumps({"money": 275, "score": -1}),
			content_type="application/json",
		)

		self.assertEqual(response.status_code, 400)
		self.assertFalse(Money.objects.filter(user=self.user).exists())
		self.assertFalse(Score.objects.filter(user=self.user).exists())

	def test_home_displays_account_data_and_auth_controls(self):
		Money.objects.create(user=self.user, amount=310)
		Score.objects.create(user=self.user, score=92)

		response = self.client.get(reverse("index"))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context["account_state"]["money"], 310)
		self.assertEqual(response.context["account_state"]["scores"], [92])

	def test_anonymous_home_shows_login_and_register_links(self):
		self.client.logout()

		response = self.client.get(reverse("index"))

		self.assertContains(response, 'href="/accounts/login/"')
		self.assertContains(response, 'href="/accounts/register/"')

	def test_rendered_csrf_token_allows_sync_and_homepage_restores_data(self):
		csrf_client = Client(enforce_csrf_checks=True)
		csrf_client.force_login(self.user)
		page = csrf_client.get(reverse("index"))
		token_match = re.search(
			r'name="csrfmiddlewaretoken" value="([^"]+)"',
			page.content.decode(),
		)
		self.assertIsNotNone(token_match)

		response = csrf_client.post(
			reverse("game_sync"),
			data=json.dumps({"money": 525, "score": 137}),
			content_type="application/json",
			HTTP_X_CSRFTOKEN=token_match.group(1),
		)

		self.assertEqual(response.status_code, 200)
		reloaded_page = csrf_client.get(reverse("index"))
		self.assertEqual(reloaded_page.context["account_state"]["money"], 525)
		self.assertEqual(reloaded_page.context["account_state"]["scores"], [137])
