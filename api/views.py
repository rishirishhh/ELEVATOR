from rest_framework.decorators import action
from api.models import Elevator, Request
from api.serializers import ElevatorSerializer, RequestSerializer
from rest_framework import viewsets, status
from rest_framework.response import Response

# Create your views here.
class ElevatorViewSet(viewsets.ModelViewSet):
    queryset = Elevator.objects.all()
    serializer_class = ElevatorSerializer

    @action(detail=False, methods=['post'])
    def initialize_system(self,request):
        num_elevators = request.data.get('num_elevators')
        if not num_elevators or not isinstance(num_elevators,int):
            return Response({"error": "Please provide the number of elevators to initialize the system"},status=status.HTTP_400_BAD_REQUEST)
        Elevator.objects.all().delete() # Delete all elevators if exists

        elevators = []
        for _ in range(num_elevators):
            elevator= Elevator.objects.create()
            elevators.append({'elevator_id': elevator.pk})

        return Response({"message": f"{num_elevators} elevators initialized successfully.","elevators": elevators},status=status.HTTP_200_OK) 
    
    @action(detail=False, methods=['post'])
    def save_request(self, request):
        """
        API to save a user request and assign the most optimal elevator to the request
        """
        requested_from_floor = request.data.get('requested_from_floor')
        requested_to_floor = request.data.get('requested_to_floor')

        if not requested_from_floor or not requested_to_floor or not isinstance(requested_from_floor, int) or not isinstance(requested_to_floor, int) or requested_from_floor <= 0 or requested_to_floor <= 0:
            return Response({'error': 'Invalid floor number provided.'}, status=status.HTTP_400_BAD_REQUEST)

        # Get all elevators
        elevators = Elevator.objects.filter(in_maintenance=False,door_opened=False)

        if not elevators:
            return Response({'error': 'No elevators available.'}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate the distances from each elevator to the requested floors
        distances = []
        for elevator in elevators:
            non_completed = Request.objects.filter(elevator=elevator,is_complete=False).order_by('created_at').first()
            if non_completed:
                distance = abs(requested_from_floor - non_completed.requested_to_floor)
            else:
                distance = abs(requested_from_floor - elevator.current_floor)
            distances.append({'elevator': elevator, 'distance': distance})

        # Sort the elevators based on distances in ascending order
        sorted_elevators = sorted(distances, key=lambda x: x['distance'])

        # Assign the closest elevator to the request
        elevator = sorted_elevators[0]['elevator']

        # Save the request
        Request.objects.create(elevator=elevator, current_floor=elevator.current_floor,requested_from_floor=requested_from_floor,requested_to_floor=requested_to_floor)

        return Response({'message': 'User request saved successfully.',
                        'elevator_id': elevator.pk,},
                        status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def get_requests(self, request, pk=None):
        """
        API to fetch all requests for a given elevator
        """
        try:
            elevator = self.get_object()
            requests = Request.objects.filter(elevator=elevator)
            serializer = RequestSerializer(requests, many=True)
            return Response(serializer.data)
        except Elevator.DoesNotExist:
            return Response({'error': 'Elevator not found.'}, status=status.HTTP_404_NOT_FOUND)
        
    @action(detail=True, methods=['get'])
    def get_next_floor(self, request, pk=None):
        """
        API to fetch the next destination floor for a given elevator
        """
        try:
            elevator = self.get_object()

            current_floor = elevator.current_floor

            # Get the requests for the elevator
            requests = Request. objects.filter(elevator=elevator,is_complete=False).order_by('created_at')

            if not requests:
                return Response({'error': 'No requests found for the elevator.'}, status=status.HTTP_400_BAD_REQUEST)

            # Get the first request from the queue
            request = requests.first()

            requested_from_floor = request.requested_from_floor
            requested_to_floor = request.requested_to_floor

            if current_floor == requested_from_floor:
                next_floor = requested_to_floor
            else:
                next_floor = requested_from_floor

            return Response({'message': 'Next floor retrieved successfully.',
                            'elevator_id': elevator.pk,
                            'next_floor': next_floor},
                            status=status.HTTP_200_OK)
        except Elevator.DoesNotExist:
            return Response({'error': 'Elevator not found.'}, status=status.HTTP_404_NOT_FOUND)
    
        
    @action(detail=True, methods=['get'])
    def direction(self, request, pk=None):
        """
         API to check the direction of elevaor
        """
        try:
            elevator = self.get_object()

            if elevator.in_maintenance:
                return Response({'error': 'Elevator is in maintenance.'}, status=status.HTTP_400_BAD_REQUEST)

            if elevator.door_opened:
                return Response({'error': 'Elevator door is open.'}, status=status.HTTP_400_BAD_REQUEST)

            current_floor = elevator.current_floor

            # Get the requests for the elevator
            requests = Request.objects.filter(elevator=elevator,is_complete=False).order_by('created_at')

            if not requests:
                return Response({'error': 'No requests found for the elevator.'}, status=status.HTTP_400_BAD_REQUEST)

            # Get the first request from the queue
            request = requests.first()

            requested_from_floor = request.requested_from_floor
            requested_to_floor = request.requested_to_floor

            if current_floor == requested_from_floor:
                next_floor = requested_to_floor
            else:
                next_floor = requested_from_floor

            if next_floor > current_floor:
                direction = "up"
            elif next_floor < current_floor:
                direction = "down"
            else:
                direction = "stationary"

            return Response({'message': 'Direction retrieved successfully.',
                            'elevator_id': elevator.pk,
                            'direction': direction},
                            status=status.HTTP_200_OK)
        except Elevator.DoesNotExist:
            return Response({'error': 'Elevator not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def toggle_door(self, request, pk=None):
        """
        to toggle the door of elevator
        """
        try:
            elevator = self.get_object()
            elevator.door_opened = not elevator.door_opened #Using the not operator to invert the boolean value
            elevator.save()
            return Response({'door_opened': elevator.door_opened})
        except Elevator.DoesNotExist:
            return Response({'error': 'Elevator not found.'}, status=status.HTTP_404_NOT_FOUND)
        
    
    @action(detail=True, methods=['post'])
    def toggle_maintenance(self, request, pk=None):
        """
        API to toggle the maintenance status of an elevator
        """
        try:
            elevator = self.get_object()
            elevator.in_maintenance = not elevator.in_maintenance #Using the not operator to invert the boolean value
            elevator.save()

            status_message = 'Elevator marked as in maintenance.' if elevator.in_maintenance else 'Elevator marked as not in maintenance.'
            return Response({'message': status_message})
        except Elevator.DoesNotExist:
            return Response({'error': 'Elevator not found.'}, status=status.HTTP_404_NOT_FOUND)
        

    @action(detail=True, methods=['post'])
    def move_elevator(self, request, pk=None):
        """
        API to move the elevator to the requested floors
        """
        try:
            elevator = self.get_object()

            if elevator.in_maintenance:
                return Response({'error': 'Elevator is in maintenance.'}, status=status.HTTP_400_BAD_REQUEST)

            if elevator.door_opened:
                return Response({'error': 'Elevator door is open.'}, status=status.HTTP_400_BAD_REQUEST)
            current_floor = elevator.current_floor
            old = current_floor

            requests = Request.objects.filter(elevator=elevator,is_complete=False).order_by('created_at')
            if not requests:
                return Response({'error': 'No more uncompleted requests found for this elevator.'}, status=status.HTTP_400_BAD_REQUEST)

            request = requests.first()

            requested_from_floor = request.requested_from_floor
            requested_to_floor = request.requested_to_floor

            if current_floor == requested_from_floor:
                elevator.current_floor = requested_to_floor
                request.is_complete = True
            else:
                elevator.current_floor = requested_from_floor
            elevator.save()
            request.save()
            return Response({'message': 'Elevator moved successfully.',
                             'elevator_id': elevator.pk,
                             'current_floor': elevator.current_floor,
                             'previos_floor': old},
                            status=status.HTTP_200_OK)
        except Elevator.DoesNotExist:
            return Response({'error': 'Elevator not found.'}, status=status.HTTP_404_NOT_FOUND)