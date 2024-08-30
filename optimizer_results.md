# Inpatient Psych Ward Space Optimization Report

## Introduction

This report evaluates the efficiency of two different bed allocation methodologies in an inpatient psych ward setting. The goal is to optimize the use of available beds, minimizing wasted beds while ensuring patient needs are met. The comparison is made between the current bed allocation method and a new approach derived from a linear programming optimization.

## Linear Programming and Optimizer Solution

Linear programming (LP) is a mathematical method used for optimizing a given objective function subject to constraints. In this project, the optimizer script (`optimizer.py`) was developed to find the optimal number of double and single rooms to minimize the total number of wasted beds. The optimizer works by defining decision variables, constraints, and an objective function.

### Optimizer Solution

- **Optimal number of double rooms:** 10.0
- **Optimal number of single rooms:** 6.0
- **Total wasted beds:** 20.0
- **Total free beds:** 0.0
- **Efficiency:** 1.00
- **Solver status:** Optimal
- **Objective function value:** 20.0

The LP optimization ensured that the total number of beds remained 26, while also considering the specific needs of patients requiring single rooms. The solution minimizes wasted beds by allocating the optimal number of single and double rooms.

## Report Aim

This report aims to compare the efficiency of the current bed allocation method against the new optimized solution. The key metrics considered are wasted beds and overall efficiency.

## Results Discussion

The following visualizations and tables provide a comparison between the current and optimized models:

### Wasted Beds Comparison

![Wasted Beds Comparison](wasted_beds_comparison.png)

The graph shows the number of wasted beds over time for both the current and optimized models. As can be seen, the optimized model significantly reduces the number of wasted beds compared to the current model.

### Daily Efficiency Comparison

![Daily Efficiency Comparison](daily_efficiency_comparison.png)

This graph compares the daily efficiency of bed usage between the two models. The optimized model consistently shows higher efficiency, indicating better utilization of available beds.

### Cumulative Efficiency Comparison

![Cumulative Efficiency Comparison](cumulative_efficiency_comparison.png)

The cumulative efficiency graph provides an overview of how efficiency trends over time. The optimized model achieves and maintains higher cumulative efficiency compared to the current model.

## Conclusions

The optimized model clearly outperforms the current model in terms of minimizing wasted beds and maximizing efficiency. This suggests that adopting the new room allocation strategy could lead to better utilization of resources in the ward.

## Additional Considerations

While the optimized model provides significant improvements, there are other factors that need to be considered:

- **Patient Preferences:** Some patients might prefer double rooms even if single rooms are available.
- **Operational Constraints:** Changes in staffing or patient flow might affect the optimal room configuration.
- **Long-Term Trends:** The model could be further refined by analyzing long-term trends in patient needs and room utilization.

## Future Plans

To build on the success of this project, the following steps could be taken:

- **Dynamic Allocation:** Implement a system that dynamically adjusts room assignments based on real-time data.
- **Further Optimization:** Explore multi-objective optimization to balance patient preferences with bed utilization.
- **Expand Scope:** Consider expanding the model to optimize other resources, such as staff or medical equipment.
