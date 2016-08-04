from .models import AutomatedPotholes
from .models import RideDetails
from django.contrib.gis.db import models
from django.contrib.gis.geos import GEOSGeometry, Point
from user.models import User

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import *
from django.core.files.base import ContentFile
from django.shortcuts import render
import datetime
import numpy as np
import os
from serverPothole import settings
from sklearn import preprocessing

############################################################
import sys,math
from sklearn.externals import joblib

def getSmoothData(data,winsize):
    smoothSize  = winsize / 2
    smoothData = []
    d = []

    for i in range(smoothSize):
        d.append([0,9.8, data[0][2], data[0][3], data[0][4], data[0][5]])

    data = d + data
    window = []

    for i in range(len(data)):
        xy = data[i][0]
        z = data[i][1]
        window.append([xy,z])

        if(len(window) >= smoothSize):
            Z = map(lambda p:p[1], window)
            XY = map(lambda p:p[0], window)
            smoothData.append([sum(XY)/len(XY), sum(Z)/len(Z), data[i][2], data[i][3], data[i][4],data[i][5]])            
            window = window[1:]

    starttime = 0
    for i in range(len(smoothData)):
        if(smoothData[i][4] != ''):
            starttime = long(smoothData[i][4]) - 500

    finalSmoothdata = []
    for i in range(len(smoothData)):
        if(smoothData[i][4] != ''):
            finalSmoothdata.append([smoothData[i][0],smoothData[i][1],smoothData[i][2],smoothData[i][3],smoothData[i][4],smoothData[i][5]])
        else:
            finalSmoothdata.append([smoothData[i][0],smoothData[i][1],smoothData[i][2],smoothData[i][3],str(starttime),smoothData[i][5]])

    return finalSmoothdata


def getMaxMin(Z):
    return max(Z) - min(Z)

def getVariance(Z):
    
    meanz = sum(Z)/len(Z)
    varz = sum(map(lambda p:(p-meanz)*(p-meanz), Z))/len(Z)
    return varz

def getFeatures(data):
    Z = map(lambda p:p[1], data)
    return [getMaxMin(Z),getVariance(Z)]

def cal_features(data,winsize):
    features = []
    
    startIndex = 0
    half_sec_index = ""

    for i in range(len(data)):
        if (data[startIndex][4] != data[i][4]):
            half_sec_index = i
            break

    finaldata = []
    for i in range(len(data)):
        if ( data[half_sec_index][4] != data[i][4] and data[i][4] != data[startIndex][4]):
            feature = getFeatures( data[startIndex:i] )
            finaldata.append([feature[0], feature[1], data[startIndex][2], data[startIndex][3], data[i][4], data[i][5]])
            
            startIndex = half_sec_index
            half_sec_index = i

    feature = getFeatures( data[startIndex:i] )
    finaldata.append([feature[0], feature[1], data[startIndex][2], data[startIndex][3], data[startIndex][4],data[startIndex][5]])

    return finaldata



def getParsedData(line,winsize):
    line = line[1:len(line)-1]
    values = line.split(";")
    data = []
    lat = ""
    lon = ""
    time = ""
    speed = ""

    for i in range(len(values)):
        if( values[i][1:2].isalpha() ):
            key_val = values[i].split(":")
            key = key_val[0]
            val = key_val[1]

            if(key == "Lat"):
                lat = val

            if(key == "Lon"):                
                lon = val

            if(key == "Speed" or key == " Speed"):
                speed = val

            if(key == "TIME"):
                time = val
        else:
            val = values[i].split(",")
            data.append([float(val[0]),float(val[1]), lat, lon, time, speed])

    return data

#############################################################
class AddPothole(APIView):

    def get(self, request):
        automated_potholes = AutomatedPotholes.objects.all().order_by('-id')[:5000]
        serializer = AutomatedPotholeEntrySerializer(automated_potholes, many=True)
        return Response(serializer.data)

    """
    APIView for adding automated potholes
    """    
    def post(self, request):
        """
        Add pothole using POST data
        """

        reporter_id = request.data.get('reporter_id')
        pothole_event_data = request.data.get('pothole_event_data')
        vehicle_type = request.data.get('vehicle_type')
        win_size = request.data.get('win_size')
        partial_distance = request.data.get('partial_distance')
        reporters_time = request.data.get('CurrentTime')
        server_time = int(datetime.datetime.now().strftime("%s")) * 1000

        offsetTime = long(server_time) - long(reporters_time)

    
        if not partial_distance:
            partial_distance = 0

        if not reporter_id or not pothole_event_data:
            print 'Invalid post data'
            return Response({"success": False, "error": "Invalid POST data"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            reporter = User.objects.get(pk=reporter_id)
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            print 'invalid reporter_id'
            return Response({"success": False, "error": "Invalid Reporter ID"}, status=status.HTTP_400_BAD_REQUEST)

        values = pothole_event_data.split('Details:-')

        print "Reporter = ",reporter

        if(values[0] == 'Ride'):
            line = values[1]
            values = line[1:len(line)-1]
            keys_values = values.split(';')
            
            start_time = ""
            stop_time = ""
            speed = 0
            version = ""
            distance = 0
            phone_model = ""
           
            for i in range(len(keys_values)):
                key_value = keys_values[i].split(":")
                key = key_value[0]
                value = key_value[1]
                if(key == "StartTime"):
                    start_time = datetime.datetime.fromtimestamp((long(value)+offsetTime)/1000.0)
                    
                if(key == "StopTime"):
                    stop_time = datetime.datetime.fromtimestamp((long(value)+offsetTime)/1000.0)

                if(key == "Distance"):
                    distance =  float(value)
                   
                if(key == "AvgRideSpeed"):
                    speed = float(value)
                    
                if(key == "Version"):
                    version = value

                if(key == "PhoneModel"):
                    phone_model = value

            print 'inserting RideDetails'
            RideDetails(reporter=reporter, vehicle_type=vehicle_type, start_time=start_time, stop_time=stop_time, speed=speed,distance = distance, app_version=version, pothole_count = 0, phone_model = phone_model ).save()
        else:
            parsedData = getParsedData(values[1], int(win_size))
            smoothData = getSmoothData(parsedData,int(win_size))
            featuresData = cal_features(smoothData,int(win_size))

            file_path = os.path.join(settings.STATIC_ROOT, 'model/model.pkl')
            clf = joblib.load(file_path)
            flag = False
            
            features = map(lambda p:[p[0],p[1]], featuresData)
            intensities = []
            probabilities = []

            for i in range(len(features)):
                feature_vector = features[i]
                feature_vector = np.array(feature_vector).reshape((1, -1))
                predicted = clf.predict(feature_vector)
                probability = clf.predict_proba(feature_vector)
                probability = probability.tolist()
                probabilities.append(probability[0][1])

                y = clf.decision_function(feature_vector)
                w_norm = np.linalg.norm(clf.coef_)
                dist = y / w_norm
                dist = dist.tolist()
                intensities.append(float(dist[0]))

                if(int(predicted[0]) == 1):
                    flag = True

            indexOfMaxIntensity = 0
            maxIntensity = -1
            for i in range(len(intensities)):
                if(maxIntensity < intensities[i]):
                    maxIntensity = intensities[i]
                    indexOfMaxIntensity = i

            lat = featuresData[indexOfMaxIntensity][2]
            lon = featuresData[indexOfMaxIntensity][3]
            time = featuresData[indexOfMaxIntensity][4]
            probability = probabilities[indexOfMaxIntensity]
            speed = sum(map(lambda p:float(p[5]), featuresData))/ len(featuresData)
            
            if not vehicle_type:
                vehicle_type = 'D'        
                
            dt = datetime.datetime.fromtimestamp((long(time) + offsetTime)/1000.0)

            if(flag == False):
                AutomatedPotholes(reporter=reporter, event_data=pothole_event_data, vehicle_type=vehicle_type, win_size=win_size, classifier_output='0', detection_time=dt, latitude=lat, longitude=lon, classifier_intensity = maxIntensity, partial_distance = partial_distance, classifier_probability = probability, event_speed = speed ).save()
            else:
                AutomatedPotholes(reporter=reporter, event_data=pothole_event_data, vehicle_type=vehicle_type, win_size=win_size, classifier_output='1', detection_time=dt,latitude=lat, longitude=lon, classifier_intensity = maxIntensity, partial_distance = partial_distance, classifier_probability = probability, event_speed = speed ).save()
                

        return Response({"success": True}, status=status.HTTP_201_CREATED)

                     
class AllRideDetail(APIView):
    """
    retrieve, update ridedetails
    """
    def get(self, request, pk):
        ride_details = RideDetails.objects.filter(reporter = pk)
        serializer = RideDetailsEntrySerializer(ride_details, many=True)
        data = serializer.data
        total_distance = 0
        total_time = 0
        pothole_count = 0
        
        for i in range(len(data)):
            total_distance = total_distance + data[i]["distance"]
            d1 = datetime.datetime.strptime(data[i]["start_time"][0:19], '%Y-%m-%dT%H:%M:%S')
            d2 = datetime.datetime.strptime(data[i]["stop_time"][0:19], '%Y-%m-%dT%H:%M:%S')
            total_time = total_time + (d2-d1).total_seconds()
            pothole_count = pothole_count + data[i]["pothole_count"]

        total_time = total_time*1000
        return Response({"id":pk,"total_time":long(total_time),"total_distance":total_distance,"pothole_count":pothole_count},status=status.HTTP_200_OK)
class DummyPost(APIView):
    def post(self, request):
        pothole_id =  request.data.get('pothole_id')   
        classifier_intensity = request.data.get('classifier_intensity')
        classifier_output = request.data.get('classifier_output')
        classifier_probability = request.data.get('classifier_probability')
        event_speed = request.data.get('event_speed')
        # print classifier_output[1:len(classifier_output)-1],classifier_intensity,pothole_id
        try:
            obj = AutomatedPotholes.objects.get(id=pothole_id)
            obj.classifier_output = classifier_output[1]
            obj.classifier_intensity = classifier_intensity
            obj.classifier_probability = classifier_probability
            obj.event_speed = event_speed
            obj.save()            
        except AutomatedPotholes.DoesNotExist:
            obj = AutomatedPotholes.objects.create(field=new_value)
        return Response({"success": True}, status=status.HTTP_201_CREATED)
