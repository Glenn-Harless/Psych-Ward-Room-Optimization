# Inpatient Psych Ward Space Optimization

## Project Overview

This project aims to model the most efficient use of space for an inpatient psych ward certified to hold up to 26 patients. The objective is to find an optimal combination of double and single rooms to minimize wasted space and ensure efficient utilization of beds.

## Methodology

The project includes two main scripts
1. `optimizer.py`: Uses linear programming to find the optimal number of double and single rooms that minimize wasted beds.
2. `tracker.py`: Evaluates all possible combinations of double and single rooms and tracks the efficiency of each combination.


`main.py` Runs them together.

### Optimization Approach

- **Decision Variables**: Number of double rooms (D) and single rooms (S).
- **Constraints**: 
  - Total number of beds (2D + S) must equal 26.
  - Ensure enough rooms for patients requiring single rooms and double rooms.
- **Objective Function**: Minimize the total number of wasted beds.

### Tracking Efficiency

- Evaluates each possible combination of double and single rooms.
- Calculates the number of wasted beds for each combination across all days.
- Identifies the combination with the least wasted beds.

## Results

### Optimization Results

The optimization script (`optimizer.py`) provided the following results:

- Optimal number of double rooms: **6**
- Optimal number of single rooms: **14**

### Efficiency Tracking Results

The efficiency tracker script (`tracker.py`) evaluated all combinations and found that the configuration with the least wasted beds is:

- **0 double rooms** and **26 single rooms** with **44** wasted beds.

**Calculating Wasted Beds**
Wasted beds are calculated to measure inefficiencies in room allocation. Here is how wasted beds are determined:

1. Single Room Patients in Double Rooms:
    - If the number of patients requiring single rooms exceeds the available single rooms, the excess patients are placed in double rooms.
    - Each single room patient in a double room wastes one bed.

2. Double Room Utilization:
    - The number of double rooms used is calculated based on the number of double room patients and any excess single room patients placed in double rooms.
    - Wasted double room beds are the difference between the total double room beds and the beds actually used.

3. Closed Rooms:
    - Closed rooms directly contribute to wasted beds since they are unavailable for use.

4. Total Wasted Beds:
    - The total wasted beds for a day are the sum of the wasted single room beds in double rooms, wasted double room beds, and closed rooms.

## Conclusion

#### Linear Programming Optimization Results
The linear programming optimization (optimizer.py) suggests having 6 double rooms and 14 single rooms. This result is based on minimizing the total number of wasted beds while satisfying the constraints of room availability and patient needs.

#### Exhaustive Combination Results
The exhaustive combination evaluation implies the best route is 0 Double rooms, and 26 single rooms, with the wasted space visualized as:

![Alt text](image.png)


##### Why Different Answers?

The discrepancy between the linear programming optimization and the exhaustive combination evaluation arises due to the different methodologies and objectives:

- Optimizer.py focuses on finding a balance between double and single rooms to minimize wasted beds over a given period.
- Tracker.py evaluates all possible combinations and identifies the setup with the absolute minimum number of wasted beds for each specific day, without considering the overall distribution of room types.


The optimizer aims to balance the room allocation over the entire dataset, which might result in a more practical solution for everyday operations, while the tracker identifies the configuration that results in the least wasted beds for each day individually, potentially leading to a solution that is optimal for the dataset but not necessarily practical for day-to-day variability.

Pros and Cons of Each Approach
1. Linear Programming Optimization (6 Double Rooms, 14 Single Rooms)

**Pros**:

- Balanced Approach: The solution balances the needs for single and double rooms, providing flexibility to accommodate different patient types.
- Operational Feasibility: Having a mix of room types can be more practical for day-to-day operations, as it provides flexibility for different patient needs and can adapt to varying daily requirements.
- Scalability: This approach can be more easily scaled to different ward sizes or different patient flow scenarios without drastic changes in room configuration.

**Cons**:

- Potential for Wasted Beds: Although it minimizes wasted beds on average, there might still be some days with more wasted beds compared to the optimal setup identified by the tracker.
- Complexity in Allocation: Managing a mix of single and double rooms can be more complex, requiring careful daily planning to ensure efficient usage.


2. Exhaustive Combination Evaluation (0 Double Rooms, 26 Single Rooms)

**Pros**:

- Minimal Wasted Beds: This setup results in the absolute minimum number of wasted beds (44) over the evaluated period, ensuring maximum efficiency.
- Simplicity: Having all single rooms simplifies room allocation, as each patient gets a single room regardless of their needs, eliminating the complexity of deciding which patients can share rooms.


**Cons**:

- Lack of Flexibility: This setup lacks the flexibility to accommodate patients who can share rooms, potentially leading to underutilization if there are many patients who can be paired.
- Operational Constraints: Hospitals may have operational constraints that require a mix of room types to handle different patient flows, making an all-single-room setup impractical.
- Increased Costs: Single rooms typically require more resources (space, utilities, staffing), potentially increasing operational costs compared to a balanced mix of room types.
Recommendation


#### Based on these findings, the hospital should consider the trade-offs between flexibility and operational constraints:

If the priority is to minimize wasted beds, the hospital might lean towards the all-single-room setup (26 single rooms).
If operational flexibility and practical day-to-day management are more critical, the mix of 6 double rooms and 14 single rooms might be more appropriate.

Ultimately, the decision should also factor in other operational considerations such as staffing, patient preferences, and cost implications. Implementing a dynamic allocation system that can adjust room assignments based on daily patient inflow and needs could also be beneficial.

