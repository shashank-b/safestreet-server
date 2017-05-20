from django.http import JsonResponse
from rest_framework import generics

from ride.api.serializers import RideSerializer
from ride.models import Ride, User, Grid, PotholeCluster


class RideCreateView(generics.CreateAPIView):
    queryset = Ride.objects.all()
    serializer_class = RideSerializer

    def perform_create(self, serializer):
        email = self.request.POST['rider']
        try:
            rider = User.objects.get(email=email)
        except User.DoesNotExist:
            rider = User(email=email)
            rider.save()
        serializer.save(rider=rider)


def get_row_col(grid_id):
    row, col = grid_id.split(',')
    row = int(row)
    col = int(col)
    return row, col


def list_pothole_cluster(request):
    row = request.GET.get('r')
    col = request.GET.get('c')
    grid_id = request.GET.get('gid')
    if 'count' in request.GET:
        count = PotholeCluster.objects.count()
        return JsonResponse([{'count': count}], safe=False)
    if grid_id is not None:
        grid_id = int(grid_id)
        pcs = PotholeCluster.objects.filter(grid_id=grid_id)
        response_list = []
        for pc in pcs:
            potholes = pc.pothole_set.all()
            for pothole in potholes:
                d = {
                    'bearing': pothole.location.bearing,
                    'lat': pothole.location.lattitude,
                    'lon': pothole.location.longitude,
                    'intensity': pothole.intensity,
                    'speed': pothole.location.speed,
                    'max_min': pothole.max_min,
                    'trip_id': pothole.ride_id
                }
                response_list.append(d)
        return JsonResponse(response_list, safe=False)

    if row is not None and col is not None:
        row = int(row)
        col = int(col)
        grid = Grid.objects.filter(row=row, col=col)
        if grid.exists():
            pothole_cluster_list = grid[0].potholecluster_set.all().values(
                'id', 'center_lat', 'center_lon', 'snapped_lat', 'snapped_lon', 'bearing', 'speed', 'accuracy'
            )
            return JsonResponse(list(pothole_cluster_list), safe=False)
        else:
            return JsonResponse({'error': "no object found with grid id row={}, col={}".format(row, col)})
    if 'range' in request.GET:
        i = int(request.GET.get('range'))
        query_set = PotholeCluster.objects.all()[1000*i:1000*(i+1)]
        response_list = []
        for pc in query_set:
            d = {}
            d['center_lat'] = pc.center_lat
            d['center_lon'] = pc.center_lon
            d['grid_id'] = pc.grid_id
            d['bearing'] = pc.get_bearing()
            d['size'] = pc.pothole_set.all().count()
            response_list.append(d)
    return JsonResponse(response_list, safe=False)


def list_potholes_by_grid_id(request):
    grid_id = request.GET.get('gid')
    if grid_id is not None:
        pass


def list_potholes(request):
    row = request.GET.get('r')
    col = request.GET.get('c')
    if row is not None and col is not None:
        row = int(row)
        col = int(col)
        grid = Grid.objects.filter(row=row, col=col)
        if grid.exists():
            pothole_cluster_list = grid[0].potholecluster_set.all()
            pothole_query_set_list = []
            for pothole_cluster in pothole_cluster_list:
                query_set = pothole_cluster.pothole_set.all().values('id', 'location__lattitude', 'location__longitude',
                                                                     'location__bearing')
                pothole_query_set_list.append(query_set)

            pothole_list = []

            for pothole_query_set in pothole_query_set_list:
                pothole_list += list(pothole_query_set)

            return JsonResponse(pothole_list, safe=False)
        else:
            return JsonResponse({'error': "no object found with grid id row={}, col={}".format(row, col)})
    return JsonResponse({'error': 'invalid request'})


def list_grids(request):
    query_set = Grid.objects.all().values('id')
    return JsonResponse(list(query_set), safe=False)
