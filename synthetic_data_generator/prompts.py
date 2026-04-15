categories = {
    "SOLID Principles": "SOLID, single responsibility, open-closed principle, liskov substitution, interface segregation, dependency inversion, software architecture, class design",
    "MVC Pattern": "MVC Pattern, model view controller, separation of concerns, decoupling UI from data logic, user interface design pattern, preventing jelly effect",
    "Coupling and Cohesion": "Coupling and Cohesion, low coupling high cohesion, modular programming, minimizing inter-dependencies between classes, single responsibility of methods",
    "Encapsulation": "Encapsulation, information hiding, private variables, public getters and setters, protecting class invariants, access modifiers, preventing direct data access",
    "Design Patterns": "Design Patterns, factory pattern, dependency injection, adapter pattern, repository pattern, software design templates, gang of four",
    "Anti-Patterns": "Anti-Patterns, constant interface antipattern, god object, spaghetti code, design flaws, software development pitfalls, monolithic classes",

    "Assignment 1": "Assignment 1",
    "Assignment 2": "Assignment 2",
    "ICT283": "ICT283",

    # C++ Technical Concepts & Constraints
    "Prohibited C++ Features": "Prohibited C++ Features, avoid auto type deduction, no range-based for loops, restrict move semantics, trailing return types prohibited, STL algorithms restricted",
    "Memory Management": "Memory Management, dynamic memory allocation, new and delete operators, avoid memory leaks, shallow vs deep copy, raw pointers, avoiding realloc and memcpy",
    "Template Classes": "Template Classes, generic programming, parameterized types, custom vector implementation, container classes, C++ templates, compile-time type binding",
    "Keyword Usage": "const correctness, explicit constructors, read-only parameters, strict type conversion, static keyword limitations",
    "Operator Overloading": "overload binary operators, istream and ostream overloading as non-members, custom class comparison, changing operator semantics",

    "Trees": "binary search tree, BST traversal, B-Trees, AVL trees, Patricia trie, balancing trees, root nodes, recursive node insertion",
    "Graphs": "directed acyclic graph, DAG, topological sort, detecting cycles, strongly connected components, nodes and edges, networkx",
    "Collections": "hash tables, maps, multimaps, custom vectors, linked lists, STL containers, dynamic arrays, collision handling",
    "Complexity": "Big-O notation, time complexity, space complexity, asymptotic analysis, algorithm efficiency, empirical computational complexity",

    "Java": "Java concurrency, Future, TimeUnit, default interface methods, annotations, @Override, type erasure, Spring Framework",
    "C# / .NET": "async await, C# asynchronous programming, COM interfaces, covariance and contravariance, WCF serialization, dependency injection in .NET",
    "TypeScript": "generic interfaces in TS, union types, partial types, inline interface implementation, anonymous implementations, static typing",
    "Swift": "Swift protocols, protocol conformance, iOS development, replace interfaces with protocols, Swift structs and classes, blueprints",

    "Test Plan": "software testing, manual calculation of expected results, stress testing, boundary edge cases, validating program console output",
    "Rationale/Justification": "defend design decisions, architectural rationale, code documentation, explaining pros and cons of trade-offs, design choices",
    "Data Validation": "handling NA fields, sanitizing input, CSV parsing, range checking, exception handling, data integrity, handling missing sensor data",
    "Demonstration": "code walkthrough, technical interview, explaining algorithms, defending codebase to tutor, oral assessment, explaining data structures"
}

generation_prompt = """You are a synthetic data generator. Generate 30 unique, diverse, and realistic students' questions for the category: "{category}".

                    Context keywords to inspire you: {keywords}

                    Rules:
                    1. The requests must sound like REAL customers (some angry, some polite, some urgent, some short, some detailed).
                    2. Do NOT number the list.
                    3. Output ONLY the requests, one per line.
                    4. Do not start lines with "I need" every time. Vary the phrasing.
                    5. Do not use the category name in the request.
                    """