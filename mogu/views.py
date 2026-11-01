import json

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .models import Money, Score

def index(request):
    account_state = {"authenticated": request.user.is_authenticated, "money": None, "scores": []}
    if request.user.is_authenticated:
        account_state["money"] = Money.objects.filter(user=request.user).values_list("amount", flat=True).first()
        account_state["scores"] = list(
            Score.objects.filter(user=request.user)
            .order_by("-score", "-created_at")
            .values_list("score", flat=True)[:8]
        )
    return render(request, "mogu/index.html", {"account_state": account_state})


@login_required
@require_POST
def sync_game_state(request):
    try:
        payload = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Invalid JSON."}, status=400)

    if not isinstance(payload, dict) or not payload:
        return JsonResponse({"error": "Expected a non-empty JSON object."}, status=400)

    for key in ("money", "score"):
        if key in payload and (
            isinstance(payload[key], bool)
            or not isinstance(payload[key], int)
            or payload[key] < 0
        ):
            return JsonResponse({"error": f"{key} must be a non-negative integer."}, status=400)

    if not set(payload).issubset({"money", "score"}):
        return JsonResponse({"error": "Unsupported game state field."}, status=400)

    with transaction.atomic():
        if "money" in payload:
            Money.objects.update_or_create(
                user=request.user,
                defaults={"amount": payload["money"]},
            )
        if "score" in payload:
            Score.objects.create(user=request.user, score=payload["score"])

    return JsonResponse({"ok": True})
