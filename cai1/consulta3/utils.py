import time
import random


def generate_random_name():
    """
    Generate a random full name for testing purposes.

    Returns:
        str: A random first and last name.
    """
    first_names = [
        "James",
        "Mary",
        "John",
        "Patricia",
        "Robert",
        "Jennifer",
        "Michael",
        "Linda",
        "William",
        "Elizabeth",
        "David",
        "Barbara",
        "Richard",
        "Susan",
        "Joseph",
        "Jessica",
        "Thomas",
        "Sarah",
        "Charles",
        "Karen",
        "Christopher",
        "Nancy",
        "Daniel",
        "Lisa",
        "Matthew",
        "Betty",
        "Anthony",
        "Margaret",
        "Mark",
        "Sandra",
        "Donald",
        "Ashley",
        "Steven",
        "Kimberly",
        "Paul",
        "Emily",
        "Andrew",
        "Donna",
        "Joshua",
        "Michelle",
        "Kenneth",
        "Dorothy",
        "Kevin",
        "Carol",
        "Brian",
        "Amanda",
        "George",
        "Melissa",
    ]

    last_names = [
        "Smith",
        "Johnson",
        "Williams",
        "Brown",
        "Jones",
        "Garcia",
        "Miller",
        "Davis",
        "Rodriguez",
        "Martinez",
        "Hernandez",
        "Lopez",
        "Gonzalez",
        "Wilson",
        "Anderson",
        "Thomas",
        "Taylor",
        "Moore",
        "Jackson",
        "Martin",
        "Lee",
        "Perez",
        "Thompson",
        "White",
        "Harris",
        "Sanchez",
        "Clark",
        "Ramirez",
        "Lewis",
        "Robinson",
        "Walker",
        "Young",
        "Allen",
        "King",
        "Wright",
        "Scott",
        "Torres",
        "Nguyen",
        "Hill",
        "Flores",
        "Green",
        "Adams",
        "Nelson",
        "Baker",
        "Hall",
        "Rivera",
        "Campbell",
        "Mitchell",
    ]

    return f"{random.choice(first_names)} {random.choice(last_names)}"


def generate_dataset(size, existing_set=None):
    """
    Generate a dataset of random names.

    Args:
        size (int): The number of names to generate.
        existing_set (set, optional): An existing set to avoid duplicates.

    Returns:
        set: A set of randomly generated names.
    """
    result = set()
    existing = existing_set or set()

    while len(result) < size:
        name = generate_random_name()
        if name not in existing and name not in result:
            result.add(name)

    return result


def time_function(func, *args, **kwargs):
    """
    Measure the execution time of a function.

    Args:
        func: The function to measure.
        *args, **kwargs: Arguments to pass to the function.

    Returns:
        tuple: A tuple containing (result, execution_time_in_seconds).
    """
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()

    return result, end_time - start_time


def generate_benchmark_data(passenger_size, poi_size, overlap_size):
    """
    Generate benchmark data for testing PSI performance.

    Args:
        passenger_size (int): The size of the passenger list.
        poi_size (int): The size of the persons of interest list.
        overlap_size (int): The size of the overlap between the two sets.

    Returns:
        tuple: A tuple containing (passenger_list, poi_list, expected_intersection).
    """
    # Generate the overlap first
    overlap = generate_dataset(overlap_size)

    # Generate the rest of the datasets
    remaining_passengers = generate_dataset(passenger_size - overlap_size, overlap)
    remaining_poi = generate_dataset(
        poi_size - overlap_size, overlap.union(remaining_passengers)
    )

    # Combine the sets
    passenger_list = list(overlap.union(remaining_passengers))
    poi_list = list(overlap.union(remaining_poi))

    # Shuffle the lists
    random.shuffle(passenger_list)
    random.shuffle(poi_list)

    return passenger_list, poi_list, overlap


def buscaComunes(Set_de_delincuentes_Confiden, Set_de_pasajeros_vuelo_Confiden):
    """
    Implementation of the buscaComunes function as specified in the requirements.
    This function finds the intersection between two sets using PSI.

    Args:
        Set_de_delincuentes_Confiden (set): Confidential set of persons of interest.
        Set_de_pasajeros_vuelo_Confiden (set): Confidential set of flight passengers.

    Returns:
        set: The intersection of the two sets.
    """
    import openmined.psi as psi

    # Convert sets to lists for PSI
    poi_list = list(Set_de_delincuentes_Confiden)
    pax_list = list(Set_de_pasajeros_vuelo_Confiden)

    # Create a PSI client
    psi_client = psi.client.CreateWithNewKey(reveal_intersection=True)

    # Create a PSI server
    psi_server = psi.server.CreateWithNewKey(reveal_intersection=True)

    # Create a request from the passenger list
    request = psi_client.CreateRequest(pax_list)

    # Process the request with our persons of interest
    psi_server.ProcessRequest(request, poi_list)

    # Get the intersection
    intersection_indices = psi_client.GetIntersection(psi_server.GetResponse())

    # Convert indices to actual names
    Set_de_Comunes = {pax_list[i] for i in intersection_indices}

    return Set_de_Comunes
