# Elevator 
Elevator System

## Installation
- Clone the Repository
```bash
git clone
cd <project dir>
```
- Install the project dependencies
```bash
pip install -r requirements.txt
```
## Run the project
- Flush the db before
```bash
python3 manage.py flush
```
- Make Migration
```bash
python3 manage.py makemigrations
```
- Migrate
```bash
python3 manage.py migrate
```
- Run Server
```bash
python3 manage.py runserver
```
## Thought Process and Design
At the outset, I tackled the elevator system by focusing on individual elevator units. After implementing the creation of a new elevator and configuring requests for each unit, I initially determined the assignment of an elevator to a request based on the straightforward metric of minimizing the distance between the elevator's current floor and the requested floor. However, I later refined this strategy by factoring in the elevator's ultimate destination as the floor it is progressing towards. To manage door operations and maintenance, I utilized the "not" operator to invert boolean values.

In real-world scenarios, three main elevator types exist: Full Collective, assigning lifts based on distance and direction; Up Collective, prioritizing upward requests and discarding downward ones unless necessary; and Down Collective, prioritizing downward requests while handling upward ones accordingly. These distinctions offer flexibility in catering to different operational scenarios and passenger preferences.


#### The implemented system follows a first-come, first-served approach, processing requests in the order of their arrival based on the "created_at" timestamp. Each request is completed by the elevator moving from its current floor to the requested starting floor and then proceeding to the requested destination floor. Upon completing the entire request, it is marked as finished.

## How does Elevator Allocation work ?

Within the "save_request" algorithm, the initial step involves checking for available elevators without ongoing maintenance and with closed doors. If none are found, the algorithm reports an error indicating elevator unavailability at that moment. Following this, the system calculates the distance between the new request's "requested_from" floor and the last requested "to" floor. This computation is crucial since, after marking the current request as complete, the elevator will reach its requested "to" floor, subsequently becoming its new current floor.

These distances, coupled with their respective elevator objects, are stored in a list. To optimize assignment, the list is then sorted in ascending order based on distances, ensuring the elevator with the shortest distance is given priority. The algorithm proceeds to select the closest elevator from this sorted list and associates the user request with that specific elevator. Lastly, the request details are saved in the database, capturing pertinent elevator and floor information. This methodical approach guarantees the efficient and optimal allocation of elevator resources for incoming user requests.

## API Reference

### System Initialization

- **URL:** /api/v1/elevators/setup
- **Method:** POST
- **Description:** Set up the elevator system with a specified number of elevators.
- **Request Body:**
```json
{
    "elevator_count": 4
}
```
- **Response:**
```json
{
    "status": "Success",
    "message": "Elevator system initialized with 4 elevators.",
    "elevators": [
        {"id": 1},
        {"id": 2},
        {"id": 3},
        {"id": 4}
    ]
}
```

### Request Submission

- **URL:** /api/v1/elevators/submit_request
- **Method:** POST
- **Description:** Submit a user request and allocate the most suitable elevator.
- **Request Body:**
```json
{
    "from_floor": 3,
    "to_floor": 7
}
```
- **Response:**
```json
{
    "status": "Success",
    "message": "User request saved successfully.",
    "assigned_elevator_id": 2
}
```

### Retrieve Requests

- **URL:** /api/v1/elevators/{elevator_id}/get_requests
- **Method:** GET
- **Description:** Retrieve all requests assigned to a specific elevator.
- **Response:**
```json
[
    {
        "id": 1,
        "elevator_id": 2,
        "from_floor": 3,
        "to_floor": 7,
        "timestamp": "2023-12-23T15:30:00Z",
        "completed": false
    },
    {
        "id": 2,
        "elevator_id": 2,
        "from_floor": 5,
        "to_floor": 2,
        "timestamp": "2023-12-23T15:45:00Z",
        "completed": false
    }
]
```

### Retrieve Next Floor

- **URL:** /api/v1/elevators/{elevator_id}/next_floor
- **Method:** GET
- **Description:** Get the next destination floor for a given elevator.
- **Response:**
```json
{
    "status": "Success",
    "message": "Next floor retrieved successfully.",
    "elevator_id": 3,
    "next_floor": 8
}
```

### Check Direction

- **URL:** /api/v1/elevators/{elevator_id}/direction
- **Method:** GET
- **Description:** Check the current direction of the elevator (up, down, or stationary).
- **Response:**
```json
{
    "status": "Success",
    "message": "Direction retrieved successfully.",
    "elevator_id": 1,
    "current_direction": "up"
}
```

### Toggle Door State

- **URL:** /api/v1/elevators/{elevator_id}/toggle_door
- **Method:** POST
- **Description:** Toggle the door state of the elevator (open or closed).
- **Response:**
```json
{
    "status": "Success",
    "door_state": "opened"
}
```

### Toggle Maintenance Mode

- **URL:** /api/v1/elevators/{elevator_id}/toggle_maintenance
- **Method:** POST
- **Description:** Toggle the maintenance mode of an elevator.
- **Response:**
```json
{
    "status": "Success",
    "message": "Elevator maintenance mode toggled."
}
```

### Move Elevator

- **URL:** /api/v1/elevators/{elevator_id}/move
- **Method:** POST
- **Description:** Move the elevator to the requested floors.
- **Response:**
```json
{
    "status": "Success",
    "message": "Elevator moved successfully.",
    "elevator_id": 4,
    "current_floor": 7,
    "previous_floor": 5
}
```