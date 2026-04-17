from django.shortcuts import render
import requests
from django.http import JsonResponse
from rest_framework import status
from .models import Profile
# Create your views here.
def Post(request):
    if request.method == "POST":

        name = request.data.get('name') 
        if name is None or name.strip() == "":
            return JsonResponse(
                {"status": "error", "message": "Missing or empty name"},
                status = status.HTTP_400_BAD_REQUEST
            )
        
        if Profile.objects.filter(name=name).exists():
            profile = Profile.objects.get(name=name)
            id = profile.id
            gender = profile.gender
            gender_probability = profile.gender_probability
            sample_size = profile.sample_size
            age = profile.age
            age_group = profile.age_group
            country_id = profile.country_id
            country_probability = profile.country_probability
            created_at = profile.created_at

            return JsonResponse(
                {
                    "status": "success",
                    "message": "Profile already exists",
                    "data":{
                        "id": id,
                        "name": name.lower(),
                        "gender": gender,
                        "gender_probability": gender_probability,
                        "sample_size": sample_size,
                        "age": age,
                        "age_group": age_group,
                        "country_id": country_id,
                        "country_probability": country_probability,
                        "created_at": created_at,
                    }
                    
                },
                status = status.HTTP_200_OK
            )
        
        
        if not isinstance(name, str):
                return JsonResponse(
                    {"status": "error", "message": "Invalid type "},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY
                )
        
        try:
            url = "https://api.genderize.io"
            res = requests.get(url, params={"name":name}, timeout=5)

            if res.status_code != 200:
                return JsonResponse(
                    {"status": "error", "message": "Upstream error"},
                    status = status.HTTP_502_BAD_GATEWAY
                )
            

            agifyurl = "https://api.agify.io"
            agifyres = requests.get(agifyurl, params={"name":name}, timeout=5)

            if agifyres.status_code != 200:
                return JsonResponse(
                    {"status": "error", "message": "Upstream error"},
                    status = status.HTTP_502_BAD_GATEWAY
                )
            
            naturl = "https://api.nationalize.io"
            natres = requests.get(naturl, params={"name":name}, timeout=5)

            if natres.status_code != 200:
                return JsonResponse(
                    {"status": "error", "message": "Upstream error"},
                    status = status.HTTP_502_BAD_GATEWAY
                )
            
            data = res.json()
            agifydata = agifyres.json()
            natdata = natres.json()
            

        except requests.exceptions.RequestException:
            return JsonResponse(
                    {"status": "error", "message": "Failed to reach external service"},
                    status=status.HTTP_502_BAD_GATEWAY
                )
        
        gender = data.get("gender")
        gender_probability = data.get("probability")
        sample_size = data.get("count")

        if gender is None or sample_size == 0:
            return JsonResponse(
                {"status": "error", "message": "Genderize returned an invalid response"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        
        age = agifydata.get("age")

        if age is None:
            return JsonResponse(
                {"status": "error", "message": "Agify returned an invalid response"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        else:
            if age <= 12:
                age_group = "child"
            elif age <= 19:
                age_group = "teenager"
            elif age <= 59:
                age_group = "adult"
            else:
                age_group = "senior" 

        

        if not natdata.get("country"):
            return JsonResponse(
                {"status": "error", "message": "Nationalize returned an invalid response"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )

        top_country = max(natdata["country"], key=lambda x: x["probability"])
        country_id = top_country["country_id"]
        country_probability = top_country["probability"]

        new_profile = Profile(
            name = name.lower(),
            gender = gender,
            gender_probability = gender_probability,
            sample_size = sample_size,
            age = age,
            age_group = age_group,
            country_id = country_id,
            country_probability = country_probability,
        )
        new_profile.save()

        if Profile.objects.filter(name=name).exists():
            profile = Profile.objects.get(name=name)
            id = profile.id
            gender = profile.gender
            gender_probability = profile.gender_probability
            sample_size = profile.sample_size
            age = profile.age
            age_group = profile.age_group
            country_id = profile.country_id
            country_probability = profile.country_probability
            created_at = profile.created_at

            return JsonResponse(
                {
                    "status": "success",
                    "data":{
                        "id": id,
                        "name": name.lower(),
                        "gender": gender,
                        "gender_probability": gender_probability,
                        "sample_size": sample_size,
                        "age": age,
                        "age_group": age_group,
                        "country_id": country_id,
                        "country_probability": country_probability,
                        "created_at": created_at,
                    }
                    
                },
                status = status.HTTP_200_OK
            )
    
    if request.method == "GET":
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

        return JsonResponse(
            {
                "status": "success",
                "count": profiles.count(),
                "data": [
                    {
                        "id": str(p.id),
                        "name": p.name,
                        "gender": p.gender,
                        "age": p.age,
                         "age_group": p.age_group,
                         "country_id": p.country_id
                    }
                    for p in profiles
                ]
            }, status = status.HTTP_200_OK
        )    

    
def Get(request, id):
    if Profile.objects.filter(id=id).exists():
        profile = Profile.objects.get(id=id)
        name = profile.name
        gender = profile.gender
        gender_probability = profile.gender_probability
        sample_size = profile.sample_size
        age = profile.age
        age_group = profile.age_group
        country_id = profile.country_id
        country_probability = profile.country_probability
        created_at = profile.created_at

        return JsonResponse(
            {
                "status": "success",
                "data":{
                    "id": id,
                    "name": name.lower(),
                    "gender": gender,
                    "gender_probability": gender_probability,
                    "sample_size": sample_size,
                    "age": age,
                    "age_group": age_group,
                    "country_id": country_id,
                    "country_probability": country_probability,
                    "created_at": created_at,
                }
                
            },
            status = status.HTTP_200_OK
        )
    else: return JsonResponse(
        {"status": "error", "message": "Profile not found"},
        status = status.HTTP_404_NOT_FOUND

    )

def Delete(request, id):
    if request.method == "DELETE":
        if Profile.objects.filter(id=id).exists():
            profile = Profile.objects.get(id=id)
            profile.delete()

            return JsonResponse({},
                status = status.HTTP_204_NO_CONTENT
            )
        else: return JsonResponse(
            {"status": "error", "message": "Profile not found"},
             status = status.HTTP_404_NOT_FOUND
        )