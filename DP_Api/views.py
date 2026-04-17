import json
import requests
from django.http import JsonResponse
from rest_framework.views import APIView
from .models import Profile
from .utils import get_age_group, get_top_country


class ProfileView(APIView):

    # -------------------
    # CREATE PROFILE
    # -------------------
    def post(self, request):

        name = request.data.get("name")
        print(name)
        print(request.data)

        # validation
        if not name or not isinstance(name, str):
            return JsonResponse(
                {"status": "error", "message": "Missing or invalid name"},
                status=400
            )

        name = name.lower()

        # idempotency check (single query)
        profile = Profile.objects.filter(name=name).first()
        if profile:
            return JsonResponse({
                "status": "success",
                "message": "Profile already exists",
                "data": self.serialize(profile)
            }, status=200)

        # -------------------
        # EXTERNAL API CALLS
        # -------------------
        try:
            gender_res = requests.get(
                "https://api.genderize.io",
                params={"name": name},
                timeout=5
            )

            age_res = requests.get(
                "https://api.agify.io",
                params={"name": name},
                timeout=5
            )

            nat_res = requests.get(
                "https://api.nationalize.io",
                params={"name": name},
                timeout=5
            )

        except requests.exceptions.RequestException:
            return JsonResponse(
                {"status": "error", "message": "Failed to reach external service"},
                status=502
            )

        gender_data = gender_res.json()
        age_data = age_res.json()
        nat_data = nat_res.json()

        # -------------------
        # VALIDATION
        # -------------------
        if not gender_data.get("gender") or not gender_data.get("count"):
            return JsonResponse(
                {"status": "error", "message": "Genderize returned an invalid response"},
                status=502
            )

        if age_data.get("age") is None:
            return JsonResponse(
                {"status": "error", "message": "Agify returned an invalid response"},
                status=502
            )

        if not nat_data.get("country"):
            return JsonResponse(
                {"status": "error", "message": "Nationalize returned an invalid response"},
                status=502
            )

        # -------------------
        # PROCESS DATA
        # -------------------
        gender = gender_data["gender"]
        gender_probability = gender_data["probability"]
        sample_size = gender_data["count"]

        age = age_data["age"]
        age_group = get_age_group(age)

        country_id, country_probability = get_top_country(nat_data["country"])

        # -------------------
        # SAVE
        # -------------------
        profile = Profile.objects.create(
            name=name,
            gender=gender,
            gender_probability=gender_probability,
            sample_size=sample_size,
            age=age,
            age_group=age_group,
            country_id=country_id,
            country_probability=country_probability
        )

        return JsonResponse({
            "status": "success",
            "data": self.serialize(profile)
        }, status=201)

    # -------------------
    # GET SINGLE / LIST
    # -------------------
    def get(self, request, id=None):

        # GET SINGLE
        if id:
            profile = Profile.objects.filter(id=id).first()

            if not profile:
                return JsonResponse(
                    {"status": "error", "message": "Profile not found"},
                    status=404
                )

            return JsonResponse({
                "status": "success",
                "data": self.serialize(profile)
            })

        # GET ALL + FILTER
        profiles = Profile.objects.all()

        gender = request.GET.get("gender")
        country_id = request.GET.get("country_id")
        age_group = request.GET.get("age_group")

        if gender:
            profiles = profiles.filter(gender__iexact=gender)

        if country_id:
            profiles = profiles.filter(country_id__iexact=country_id)

        if age_group:
            profiles = profiles.filter(age_group__iexact=age_group)

        return JsonResponse({
            "status": "success",
            "count": profiles.count(),
            "data": [self.serialize(p) for p in profiles]
        })

        if profile is None:
            return JsonResponse(
                {"status": "error", "message": "profile not found"},
                status=404
            )
    

    # -------------------
    # DELETE
    # -------------------
    def delete(self, request, id):

        profile = Profile.objects.filter(id=id).first()

        if not profile:
            return JsonResponse(
                {"status": "error", "message": "Profile not found"},
                status=404
            )

        profile.delete()

        return JsonResponse({}, status=204)

    # -------------------
    # SERIALIZER
    # -------------------
    def serialize(self, obj):
        return {
            "id": str(obj.id),
            "name": obj.name,
            "gender": obj.gender,
            "gender_probability": obj.gender_probability,
            "sample_size": obj.sample_size,
            "age": obj.age,
            "age_group": obj.age_group,
            "country_id": obj.country_id,
            "country_probability": obj.country_probability,
            "created_at": obj.created_at.isoformat().replace("+00:00", "Z")
        }