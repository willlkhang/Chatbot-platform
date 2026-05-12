import requests

# NOTE on verification (per discussion with Claude):
# - All YouTube video IDs were checked for *existence* via web search.
# - Durations could not be reliably verified remotely (YouTube direct fetches
#   were rate-limited). Where the original list's "(Xm)" annotation was clearly
#   wrong (e.g. the Uncle Bob video tagged "12m" is actually ~1 hour),
#   the video was replaced.
# - "VERIFIED" = ID confirmed to exist in search results matching topic.
# - "TRUSTED" = ID not directly confirmed, but channel reputation suggests
#   typical video length is within your 20-min budget.
# - "UNVERIFIED" = could not confirm existence; worth manual spot-check.

resources_db = {
    "BINARY_SEARCH_TREES": [
        "https://www.geeksforgeeks.org/binary-search-tree-data-structure/",
        "https://www.youtube.com/watch?v=pYT9F8_LFTM"  # mycodeschool - VERIFIED
    ],
    "CLASSES_AND_OBJECTS": [
        "https://www.learncpp.com/cpp-tutorial/classes-and-class-members/",
        "https://www.youtube.com/watch?v=2BP8NhxjrO0"  # The Cherno "CLASSES in C++" - VERIFIED (was 2BP8PoVjcCA, which doesn't exist)
    ],
    "CODING_STANDARDS": [
        "https://llvm.org/docs/CodingStandards.html",
        "https://www.youtube.com/watch?v=wSDyiEjhp8k"  # "My 10 Clean Code Principles" - VERIFIED (replaced Uncle Bob 7EmboKQH8lM, which is ~1hr, not 12m)
    ],
    "COMPOSITION_AND_AGGREGATION": [
        "https://www.learncpp.com/cpp-tutorial/composition/",
        "https://www.youtube.com/watch?v=B46RqPYhEys"  # "Association | Composition | Aggregation | OOP C++" - VERIFIED (replaced broken MPvlyvipSxw)
    ],
    "CONTROL_FLOW": [
        "https://www.learncpp.com/cpp-tutorial/control-flow-introduction/",
        "https://www.youtube.com/watch?v=a3IZ8WaIFAA"  # VERIFIED
    ],
    "DESIGN_PATTERNS": [
        "https://refactoring.guru/design-patterns",
        "https://www.youtube.com/watch?v=v9ejT8FO-7I"  # Christopher Okhravi - TRUSTED
    ],
    "DOCUMENTATION": [
        "https://www.doxygen.nl/manual/docblocks.html",
        "https://www.youtube.com/watch?v=tLPHQMosF9M"  # Mike Shah "Doxygen ... in 20 minutes!" - VERIFIED (replaced mD0eU3_rXz0, which I could not find)
    ],
    "DYNAMIC_MEMORY": [
        "https://www.learncpp.com/cpp-tutorial/dynamic-memory-allocation-with-new-and-delete/",
        "https://www.youtube.com/watch?v=R0qIYWo8igs",
        "https://www.youtube.com/watch?v=fc19HhHKtrA" #The Cherno - TRUSTED
    ],
    "ENCAPSULATION": [
        "https://www.learncpp.com/cpp-tutorial/access-functions-and-encapsulation/",
        "https://www.youtube.com/watch?v=pTB0EiLXUC8"  # Programming with Mosh - TRUSTED
    ],
    "EXCEPTION_HANDLING": [
        "https://en.cppreference.com/w/cpp/language/exceptions",
        "https://www.youtube.com/watch?v=5nCXSDv6e4I"  # The Cherno - TRUSTED
    ],
    "FILE_IO": [
        "https://www.learncpp.com/cpp-tutorial/basic-file-io/",
        "https://www.youtube.com/watch?v=HQNsriyMhtY"  # The Cherno - TRUSTED
    ],
    "FUNCTIONS_AND_MODULARITY": [
        "https://www.learncpp.com/cpp-tutorial/introduction-to-functions/",
        "https://www.youtube.com/watch?v=NGQoKF2Ggt8",
        "https://www.youtube.com/watch?v=V9zuox47zr0" # Caleb Curry - TRUSTED
    ],
    "GRAPHS": [
        "https://www.geeksforgeeks.org/graph-data-structure-and-algorithm/",
        "https://www.youtube.com/watch?v=-VgHk7UMPP4"  # WilliamFiset - TRUSTED
    ],
    "HASH_TABLES": [
        "https://en.wikipedia.org/wiki/Hash_table",
        "https://www.youtube.com/watch?v=shs0KM3wKv8"  # HackerRank - VERIFIED
    ],
    "INHERITANCE": [
        "https://www.learncpp.com/cpp-tutorial/basic-inheritance-in-c/",
        "https://www.youtube.com/watch?v=5HYIFFuGcvk"  # The Cherno - TRUSTED
    ],
    "LINKED_LIST": [
        "https://www.geeksforgeeks.org/data-structures/linked-list/",
        "https://www.youtube.com/watch?v=F8AbOfQwl1c"  # mycodeschool - TRUSTED
    ],
    "MAPS_AND_SETS": [
        "https://en.cppreference.com/w/cpp/container/map",
        "https://www.youtube.com/watch?v=gmIb-qZhTDQ"  # The Cherno - TRUSTED
    ],
    "MULTIWAY_TREES": [
        "https://www.thedshandbook.com/multiway-trees/",
        "https://www.youtube.com/watch?v=yVsFYZQJenw&t=322s"  # GATE CSE - VERIFIED
    ],
    "POINTERS": [
        "https://www.learncpp.com/cpp-tutorial/introduction-to-pointers/",
        "https://www.youtube.com/watch?v=2ybLD6_2gKM"  # mycodeschool - TRUSTED
    ],
    "POLYMORPHISM": [
        "https://www.learncpp.com/cpp-tutorial/pointers-and-references-to-the-base-class-of-derived-objects/",
        "https://www.youtube.com/watch?v=tIWm3I_Zu7I"  # The Cherno - TRUSTED
    ],
    "QUEUES": [
        "https://www.geeksforgeeks.org/queue-data-structure/",
        "https://www.youtube.com/watch?v=D6gu-_tmEpQ"  # mycodeschool - TRUSTED
    ],
    "SEARCHING": [
        "https://www.geeksforgeeks.org/searching-algorithms/",
        "https://www.youtube.com/watch?v=P3YID7liBug"  # HackerRank "Algorithms: Binary Search" by Gayle Laakmann - VERIFIED (replaced Wide1CGhkkU, which I could not confirm; original was tagged CS50 but CS50 full lectures are 1hr+)
    ],
    "SEPARATION_OF_INTERFACE_AND_IMPLEMENTATION": [
        "https://martinfowler.com/eaaCatalog/separatedInterface.html",
        "https://www.youtube.com/watch?v=hv0lv783KqQ"  # Mark Gingrass - VERIFIED
    ],
    "SOLID_PRINCIPLES": [
        "https://en.wikipedia.org/wiki/SOLID",
        "https://www.youtube.com/watch?v=yxf2spbpTSw"  # WebDevSimplified - TRUSTED
    ],
    "SORTING": [
        "https://www.geeksforgeeks.org/sorting-algorithms/",
        "https://www.youtube.com/watch?v=5d1pyghLs3M"  # UNVERIFIED - could not confirm; if broken, consider HackerRank/mycodeschool sorting videos
    ],
    "STACKS": [
        "https://www.geeksforgeeks.org/stack-data-structure/",
        "https://www.youtube.com/watch?v=KcT3aVgrrpU"  # mycodeschool - TRUSTED
    ],
    "STRINGS": [
        "https://en.cppreference.com/w/cpp/string/basic_string",
        "https://www.youtube.com/watch?v=60OI5tzmkCw"  # The Cherno - TRUSTED
    ],
    "TEMPLATES_AND_GENERICS": [
        "https://www.learncpp.com/cpp-tutorial/function-templates/",
        "https://www.youtube.com/watch?v=mQqzP9EWu58&t=1s",
        "https://www.youtube.com/watch?v=8IgXzTNgQdo&t=8s"# The Cherno - TRUSTED
    ],
    "TESTING_AND_DEBUGGING": [
        "https://learn.microsoft.com/en-us/visualstudio/debugger/debugger-feature-tour",
        "https://www.youtube.com/watch?v=9H6muyZjms0"  # The Cherno - TRUSTED
    ],
    "UML_AND_CLASS_DIAGRAMS": [
        "https://www.lucidchart.com/pages/uml-class-diagram",
        "https://www.youtube.com/watch?v=6XrL5jXmTwM"  # Lucidchart Official - TRUSTED
    ],
    "VARIABLES_AND_TYPES": [
        "https://www.learncpp.com/cpp-tutorial/fundamental-data-types/",
        "https://www.youtube.com/watch?v=zPObUTmiCzk"  # The Cherno - TRUSTED
    ],
    "VECTORS_AND_DYNAMIC_ARRAYS": [
        "https://en.cppreference.com/w/cpp/container/vector",
        "https://www.youtube.com/watch?v=_KSKH8C9Gf0",
        "https://www.youtube.com/watch?v=dQG41m6vf3A" # The Cherno - TRUSTED
    ]
}

for topic, materials in resources_db.items():
    for i, material in enumerate(materials):
        try:
            response = requests.post(
                "http://localhost:8011/add_resources",
                json={
                    "topic": topic,
                    "resource": material
                }
            )

            if response.status_code in [200, 201]:
                print(f"Success: Added resource {i+1} for {topic}")
            else:
                print(f"Failed: Resource {i+1} for {topic} returned status {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"Error connecting to server for {topic}: {e}")