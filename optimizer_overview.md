
# Optimizer Description

## Introduction

This document provides a detailed yet accessible explanation of how the optimizer works in the context of the inpatient psych ward space optimization project. The purpose of the optimizer is to find the most efficient way to allocate beds in the ward, minimizing wasted beds while ensuring all patients' needs are met.

## What is a Wasted Bed?

A "wasted bed" is a bed that could be used by another patient but isn’t, due to specific needs of the patients.

### Current Method

- Currently, all rooms are double rooms (each with two beds).
- If a patient needs to be alone in a room due to their condition, they occupy one bed in a double room, leaving the other bed unused. This unused bed is considered "wasted."

### Optimized Method

- The optimized method proposes a mix of single and double rooms.
- Single rooms are given to patients who need to be alone. If there are no single rooms left, these patients are placed in a double room, possibly leaving one bed in that room wasted.

## What is Linear Programming?

Linear programming is a mathematical method used to find the best possible outcome in a given situation, where you have specific goals (like minimizing wasted beds) and certain constraints (like the total number of beds).

### How Does Linear Programming Work?

At the core of linear programming is the **objective function**, which represents the goal you're trying to achieve—this could be minimizing costs, maximizing profits, or optimizing resource allocation. The objective function is a linear equation that you want to either maximize or minimize.

To find the best outcome, you must also define **constraints**, which are conditions that your solution must satisfy. These constraints are usually expressed as linear inequalities or equations and represent the limitations or requirements of the problem (e.g., the number of available beds, staffing limitations, or room availability).

When you plot these constraints on a graph, they form a feasible region—this is the area where all the constraints overlap and represents all possible solutions that meet the conditions. The optimal solution lies at one of the vertices (corners) of this feasible region. Any solution outside of this region is considered infeasible because it does not satisfy all the constraints.

In summary, linear programming helps you identify the optimal solution by finding the point on the feasible region that maximizes or minimizes your objective function while satisfying all the constraints.

## How the Optimizer Solves the Problem

### 1. Understanding the Problem

We have a total of 26 beds in the ward. The optimizer needs to decide how many of these beds should be in single rooms and how many should be in double rooms.

### 2. Defining the Goal

The goal is to minimize the number of wasted beds while meeting the patients’ needs. This goal is translated into an "objective function," which the optimizer tries to minimize.

### 3. Setting the Rules (Constraints)

- **Total Bed Constraint:** The total number of beds must always equal 26.
- **Single Room Constraint:** There must be enough single rooms or double rooms to accommodate all patients who need to be alone.
- **Double Room Constraint:** There must be enough double rooms to accommodate patients who can share a room.

### 4. Testing Combinations

- The optimizer tests different combinations of single and double rooms. For example, it might test having 6 single rooms and 10 double rooms, then calculate how many beds would be wasted with this setup.
- For each combination, the optimizer considers:
  - How many single rooms are needed for patients who must be alone.
  - How many double rooms are needed for patients who can share.
  - Whether any single-room patients would end up in double rooms, and if so, how many beds would be wasted.

### 5. Using Linear Programming to Solve

- The optimizer uses linear programming to systematically go through all possible combinations of single and double rooms.
- It calculates the total number of wasted beds for each combination, always following the rules (constraints).
- Linear programming helps ensure that the optimizer finds the absolute best combination that results in the fewest wasted beds.

### 6. Choosing the Best Option

- After testing all combinations, the optimizer selects the one that results in the fewest wasted beds.
- In this case, it found that having 10 double rooms and 6 single rooms was the most efficient setup, leading to the least waste.

## Are Constraints Flexible?

Constraints in linear programming are the rules that must be satisfied for a solution to be valid. They are not flexible in the sense that they must be met. However, the optimizer handles situations where it’s impossible to perfectly meet all constraints, which is why the concept of "wasted beds" comes into play.

### Handling Constraints

- **Single Room Constraint:** The model tries to allocate single rooms to patients who need them. If there aren’t enough single rooms, some patients will have to go into double rooms, resulting in wasted beds.
- **Wasted Beds:** Even though the optimizer works within rigid constraints, it calculates how many beds are wasted if it can’t perfectly satisfy all patient needs.
- **Optimization:** The optimizer then works to find the best possible combination that minimizes these wasted beds, even if it can’t eliminate them entirely.

### Summary

- Constraints are not flexible—they must be satisfied.
- Wasted beds arise because, while the constraints are met as much as possible, the ward’s real-world limitations mean that some beds may end up being unused.
- The optimizer tries to minimize these wasted beds while adhering to the constraints, even if it can’t meet all needs perfectly.

This is a common aspect of optimization problems: the solution may not be perfect but is the best possible under the given constraints.
