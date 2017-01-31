import datetime
import os

import numpy as np
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from sklearn.externals import joblib

from serverPothole import settings
from user.models import User
from .serializers import *


def get_smooth_data(data, winsize):
    smooth_size = winsize / 2
    smooth_data = []
    d = []

    for i in range(smooth_size):
        d.append([0, 9.8, data[0][2], data[0][3], data[0][4], data[0][5]])

    data = d + data
    window = []

    for i in range(len(data)):
        xy = data[i][0]
        z = data[i][1]
        window.append([xy, z])

        if len(window) >= smooth_size:
            Z = [p[1] for p in window]
            XY = [p[0] for p in window]
            smooth_data.append(
                [sum(XY) / len(XY), sum(Z) / len(Z), data[i][2], data[i][3],
                 data[i][4], data[i][5]])
            window = window[1:]

    start_time = 0
    for i in range(len(smooth_data)):
        if (smooth_data[i][4] != ''):
            start_time = int(smooth_data[i][4]) - 500

    final_smoothdata = []
    for i in range(len(smooth_data)):
        if (smooth_data[i][4] != ''):
            final_smoothdata.append(
                [smooth_data[i][0], smooth_data[i][1], smooth_data[i][2],
                 smooth_data[i][3], smooth_data[i][4],
                 smooth_data[i][5]])
        else:
            final_smoothdata.append(
                [smooth_data[i][0], smooth_data[i][1], smooth_data[i][2],
                 smooth_data[i][3], str(start_time),
                 smooth_data[i][5]])

    return final_smoothdata


def get_max_min(Z):
    return max(Z) - min(Z)


def get_variance(Z):
    meanz = sum(Z) / len(Z)
    varz = sum([(p - meanz) * (p - meanz) for p in Z]) / len(Z)
    return varz


def get_features(data):
    Z = [p[1] for p in data]
    return [get_max_min(Z), get_variance(Z)]


def cal_features(data, winsize):
    """

    :param data:
    :type data:
    :param winsize:
    :type winsize:
    :return:
    :rtype:
    """
    start_index = 0
    half_sec_index = ""

    for i in range(len(data)):
        if (data[start_index][4] != data[i][4]):
            half_sec_index = i
            break

    finaldata = []
    for i in range(len(data)):
        if data[half_sec_index][4] != data[i][4] and data[i][4] != \
                data[start_index][4]:
            feature = get_features(data[start_index:i])
            finaldata.append(
                [feature[0], feature[1], data[start_index][2],
                 data[start_index][3], data[i][4], data[i][5]])

            start_index = half_sec_index
            half_sec_index = i

    feature = get_features(data[start_index:i])
    finaldata.append(
        [feature[0], feature[1], data[start_index][2], data[start_index][3],
         data[start_index][4],
         data[start_index][5]])

    return finaldata


def get_parsed_data(line, winsize):
    line = line[1:len(line) - 1]
    values = line.split(";")
    data = []
    lat = ""
    lon = ""
    time = ""
    speed = ""

    for i in range(len(values)):
        if values[i][1:2].isalpha():
            key_val = values[i].split(":")
            key = key_val[0]
            val = key_val[1]

            if key == "Lat":
                lat = val

            if key == "Lon":
                lon = val

            if key == "Speed" or key == " Speed":
                speed = val

            if key == "TIME":
                time = val
        else:
            val = values[i].split(",")
            data.append([float(val[0]), float(val[1]), lat, lon, time, speed])
    return data


#############################################################
class AddPothole(APIView):
    def get(self, request):
        # last 5000 rows from autopotholes table
        automated_potholes = AutomatedPotholes.objects.all()
        serializer = AutomatedPotholeEntrySerializer(automated_potholes,
                                                     many=True)
        return Response(serializer.data)

    """
    APIView for adding automated potholes
    """

    def post(self, request):
        """
        Add pothole using POST data
        """

        reporter_id = request.data.get('reporter_id')
        # need filtering for pothole_event_data
        pothole_event_data = request.data.get('pothole_event_data')
        vehicle_type = request.data.get('vehicle_type')
        win_size = request.data.get('win_size')
        partial_distance = request.data.get('partial_distance')
        reporters_time = request.data.get('CurrentTime')
        server_time = int(datetime.datetime.now().strftime("%s")) * 1000

        offsetTime = int(server_time) - int(reporters_time)

        if not partial_distance:
            partial_distance = 0

        if not reporter_id or not pothole_event_data:
            print('Invalid post data')
            return Response({"success": False, "error": "Invalid POST data"},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            reporter = User.objects.get(pk=reporter_id)
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            print('invalid reporter_id')
            return Response({"success": False, "error": "Invalid Reporter ID"},
                            status=status.HTTP_400_BAD_REQUEST)

        values = pothole_event_data.split('Details:-')

        print("Reporter = ", reporter)

        if values[0] == 'Ride':
            line = values[1]
            values = line[1:len(line) - 1]
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
                if key == "StartTime":
                    start_time = datetime.datetime.fromtimestamp(
                        (int(value) + offsetTime) / 1000.0)

                if key == "StopTime":
                    stop_time = datetime.datetime.fromtimestamp(
                        (int(value) + offsetTime) / 1000.0)

                if key == "Distance":
                    distance = float(value)

                if key == "AvgRideSpeed":
                    speed = float(value)

                if key == "Version":
                    version = value

                if key == "PhoneModel":
                    phone_model = value

            print('inserting RideDetails')
            RideDetails(reporter=reporter, vehicle_type=vehicle_type,
                        start_time=start_time, stop_time=stop_time,
                        speed=speed, distance=distance, app_version=version,
                        pothole_count=0,
                        phone_model=phone_model).save()
        else:
            parsed_data = get_parsed_data(values[1], int(win_size))
            smooth_data = get_smooth_data(parsed_data, int(win_size))
            #
            features_data = cal_features(smooth_data, int(win_size))

            file_path = os.path.join(settings.STATIC_ROOT, 'model/model.pkl')
            clf = joblib.load(file_path)
            flag = False

            features = [[p[0], p[1]] for p in features_data]
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

                if int(predicted[0]) == 1:
                    flag = True

            index_of_max_intensity = 0
            max_intensity = -1
            for i in range(len(intensities)):
                if max_intensity < intensities[i]:
                    max_intensity = intensities[i]
                    index_of_max_intensity = i

            lat = features_data[index_of_max_intensity][2]
            lon = features_data[index_of_max_intensity][3]
            time = features_data[index_of_max_intensity][4]
            probability = probabilities[index_of_max_intensity]
            speed = sum([float(p[5]) for p in features_data]) / len(
                features_data)

            if not vehicle_type:
                vehicle_type = 'D'

            dt = datetime.datetime.fromtimestamp(
                (int(time) + offsetTime) / 1000.0)

            if not flag:
                AutomatedPotholes(reporter=reporter,
                                  event_data=pothole_event_data,
                                  vehicle_type=vehicle_type,
                                  win_size=win_size, classifier_output='0',
                                  detection_time=dt, latitude=lat,
                                  longitude=lon,
                                  classifier_intensity=max_intensity,
                                  partial_distance=partial_distance,
                                  classifier_probability=probability,
                                  event_speed=speed).save()
            else:
                AutomatedPotholes(reporter=reporter,
                                  event_data=pothole_event_data,
                                  vehicle_type=vehicle_type,
                                  win_size=win_size, classifier_output='1',
                                  detection_time=dt, latitude=lat,
                                  longitude=lon,
                                  classifier_intensity=max_intensity,
                                  partial_distance=partial_distance,
                                  classifier_probability=probability,
                                  event_speed=speed).save()

        return Response({"success": True}, status=status.HTTP_201_CREATED)


class AllRideDetail(APIView):
    """
    retrieve, update ridedetails
    """

    def get(self, request, pk):
        ride_details = RideDetails.objects.filter(reporter=pk)
        serializer = RideDetailsEntrySerializer(ride_details, many=True)
        data = serializer.data
        total_distance = 0
        total_time = 0
        pothole_count = 0

        for i in range(len(data)):
            total_distance = total_distance + data[i]["distance"]
            d1 = datetime.datetime.strptime(data[i]["start_time"][0:19],
                                            '%Y-%m-%dT%H:%M:%S')
            d2 = datetime.datetime.strptime(data[i]["stop_time"][0:19],
                                            '%Y-%m-%dT%H:%M:%S')
            total_time += (d2 - d1).total_seconds()
            pothole_count = pothole_count + data[i]["pothole_count"]

        total_time *= 1000
        return Response({"id": pk, "total_time": int(
            total_time), "total_distance": total_distance,
                         "pothole_count": pothole_count},
                        status=status.HTTP_200_OK)


class DummyPost(APIView):
    def post(self, request):
        pothole_id = request.data.get('pothole_id')
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
