from django.shortcuts import render
from django.db.models import F, Value, Max, Min
from .models import Designer1
from .serializers import Designer1Serializer, OpsPlan1Serializer, UAVDesignSerializer, UAVDesign2Serializer, UAVDesign2TrajSerializer
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from random import shuffle

# Create your views here.

class Designer1List(generics.ListAPIView):
    serializer_class = Designer1Serializer

    def get_queryset(self):
        # queryset = Designer1.objects.all()
        max_range = Designer1.objects.all().aggregate(Max('range')).get('range__max')
        # min_range = Designer1.objects.all().aggregate(Min('range')).get('range__min')
        max_payload = Designer1.objects.all().aggregate(Max('payload')).get('payload__max')
        # min_payload = Designer1.objects.all().aggregate(Min('payload')).get('payload__min')
        max_cost = Designer1.objects.all().aggregate(Max('cost')).get('cost__max')
        # min_cost = Designer1.objects.all().aggregate(Min('cost')).get('cost__min')
        range = self.request.query_params.get('range', 6)
        cost = self.request.query_params.get('cost', 5000)
        payload = self.request.query_params.get('payload', 20)
        queryset = list(Designer1.objects.order_by(((F('range')-range)/max_range)**2+((F('cost')-cost)/max_cost)**2+((F('payload')-payload)/max_payload)**2))
        best10 = queryset[:10]
        shuffle(best10)
        return best10[:5]

class OpsPlan1(generics.CreateAPIView):
    """
    Generate an Ops Plan given an input string.
    """
    serializer_class = OpsPlan1Serializer

class UAVDesignAsses(generics.CreateAPIView):
    """
    Assess a given UAV designer
    """
    serializer_class = UAVDesignSerializer

class UAVDesign2Asses(generics.CreateAPIView):
    """
    Assess a given UAV designer
    """
    serializer_class = UAVDesign2Serializer

class UAVDesign2Traj(generics.CreateAPIView):
    """
    Asses a given UAV design and return its performance and GetUAVTrajectory
    """
    serializer_class = UAVDesign2TrajSerializer
