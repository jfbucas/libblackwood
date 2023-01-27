Strategies that can be used to improve the performance of the backtracking algorithm for solving the Eternity II puzzle:

- Selecting a subset of the edges to focus on early in the backtracking process can help to reduce the number of possibilities that need to be considered, which can make the algorithm more efficient.
- Introducing a growing non-linear constraint can help to guide the search by prioritizing the placement of certain tiles over others. As the algorithm progresses, the constraint can be made more strict, which can help to ensure that the best possible solution is found.
- The order in which tiles are placed on the board can have a significant impact on the performance of the algorithm, as it can help to avoid combinatorial dead-ends. By carefully selecting the order in which tiles are placed, it is possible to reduce the number of possibilities that need to be considered and make the algorithm more efficient.
- Allowing for "breaks" near the end of the backtracking process can help to reduce the number of possibilities that need to be considered and make the algorithm more efficient. However, the backtrack depth at which breaks are allowed to accumulate is critical, as allowing too many breaks too early in the process can make it more difficult to find a solution.
- Giving greater or lower priorirty to some specific tiles could also help significantly.
