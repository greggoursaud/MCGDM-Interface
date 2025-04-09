# Approach 1: Generate Alternatives First, Then Apply HIVES

## Scenario
Imagine you're designing a product, and you need to balance **cost**, **durability**, and **performance**. You have three decision-makers (DMs) who will evaluate these criteria.

---

## Regular HIVES Method

### Input Data
- Decision-makers provide weights for the criteria (e.g., cost: 40%, durability: 30%, performance: 30%).
- Alternatives (products) are manually defined (e.g., Product A, B, C) with scores for each criterion.

### Example
#### Weights
- **DM1**: Cost=40%, Durability=30%, Performance=30%
- **DM2**: Cost=50%, Durability=20%, Performance=30%
- **DM3**: Cost=30%, Durability=40%, Performance=30%

#### Alternatives
- **Product A**: Cost=70, Durability=80, Performance=90
- **Product B**: Cost=60, Durability=70, Performance=85
- **Product C**: Cost=50, Durability=60, Performance=80

### HIVES Algorithm
- The weights are aggregated using the HIVES method.
- The alternatives are scored and ranked based on the aggregated weights.

### Output
- A ranked list of alternatives (e.g., Product A > Product B > Product C).

---

## Approach 1: Generate Alternatives First, Then Apply HIVES

### Step 1: Generate Alternatives
- Instead of manually defining alternatives, use a **multi-objective optimization algorithm** (e.g., NSGA-II) to generate a set of Pareto-optimal solutions.
- Each solution represents a trade-off between cost, durability, and performance.

#### Example
Using the `pymoo` library, you generate 100 alternatives:
- These alternatives are Pareto-optimal, meaning no alternative is strictly better in all criteria.

### Step 2: Visualize Alternatives
- Use scatter plots (for 2-3 objectives) or parallel coordinate plots (for 4+ objectives) to help decision-makers understand the trade-offs.

#### Example
- A scatter plot of **cost vs. performance** shows how improving performance increases cost.

### Step 3: Apply HIVES
- Decision-makers evaluate the generated alternatives using the HIVES method.
- The aggregated weights are applied to rank the Pareto-optimal alternatives.

### Output
- A ranked list of Pareto-optimal alternatives (e.g., Alternative 42 > Alternative 17 > Alternative 89).

---

## Key Differences

| **Aspect**              | **Regular HIVES**                          | **Approach 1**                                      |
|-------------------------|--------------------------------------------|----------------------------------------------------|
| **Alternatives**         | Manually defined by decision-makers.       | Automatically generated using optimization algorithms. |
| **Solution Space**       | Limited to predefined alternatives.        | Explores a broader set of Pareto-optimal solutions. |
| **Decision-Maker Effort**| Focused on evaluating predefined alternatives. | Focused on evaluating trade-offs between objectives. |
| **Visualization**        | Limited to predefined alternatives.        | Uses scatter/parallel plots to visualize trade-offs. |
| **Flexibility**          | Limited by the quality of predefined alternatives. | Allows exploration of diverse, high-quality solutions. |

---

## Conclusion
- **Regular HIVES** is suitable when you already have a well-defined set of alternatives.
- **Approach 1** is ideal when you want to explore a broader solution space and ensure the alternatives are Pareto-optimal.

By combining optimization with HIVES, you can make more informed decisions and provide decision-makers with better options.