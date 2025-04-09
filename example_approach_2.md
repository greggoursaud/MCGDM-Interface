# Approach 2: Apply HIVES First, Then Optimize

## Scenario
Imagine you're designing a product, and you need to balance **cost**, **durability**, and **performance**. You have three decision-makers (DMs) who will evaluate these criteria.

---

## Regular HIVES Method (Recap)

### Input Data
- Decision-makers provide weights for criteria.
- Alternatives (products) are manually defined.
- HIVES ranks the predefined alternatives.

---

## Approach 2: Apply HIVES First, Then Optimize

### Step 1: Collect Decision-Maker Preferences
- Decision-makers provide importance weights for each criterion.

### Step 2: Apply HIVES to Determine Consensus Weights
- The HIVES algorithm processes these preferences:
  - Calculates statistical measures (Q1, Q3, SICP, etc.).
  - Applies the Score Bell function to transform values.
  - Calculates the percentage score matrix.
  - Computes final consensus weights with correction factor.

#### Result
- Final consensus weights after HIVES processing:
  - **Cost**: 41.3%
  - **Durability**: 29.7%
  - **Performance**: 29.0%

### Step 3: Define the Optimization Problem
- Create a mathematical model for the product design:
  - **Decision Variables**: Material thickness, component quality, etc.
  - **Objective Functions**:
    - **Cost**: f₁(x) = material cost + production cost
    - **Durability**: f₂(x) = expected lifespan
    - **Performance**: f₃(x) = efficiency rating

### Step 4: Scalarize Using HIVES Weights
- Convert multiple objectives into a single objective using the Tchebycheff method.

### Step 5: Find the Optimal Solution
- Use a single-objective optimization algorithm (e.g., differential evolution).

### Step 6: Final Solution
- The algorithm returns the optimal design parameters that best satisfy the weighted objectives:
  - **Optimal Design Parameters**: [12.5mm thickness, 85% quality rating, ...]
  - **Resulting Performance**: Cost=$275, Durability=8.3 years, Performance=92%

---

## Key Differences

| **Aspect**              | **Regular HIVES**                          | **Approach 1**                                      | **Approach 2**                                      |
|-------------------------|--------------------------------------------|----------------------------------------------------|----------------------------------------------------|
| **Process Flow**         | Evaluate predefined alternatives           | Generate alternatives → Apply HIVES               | Apply HIVES → Generate optimal solution            |
| **Number of Solutions**  | Limited by predefined set                  | Many (Pareto front)                                | Single optimal solution                            |
| **Decision-Maker Input** | Evaluate criteria and alternatives         | Evaluate criteria only                             | Evaluate criteria only                             |
| **Solution Quality**     | Limited by predefined alternatives         | All Pareto-optimal                                 | Single best solution based on weights             |
| **When to Use**          | Well-defined alternative set               | Need to explore solution space                    | Need single "best" solution                       |

---

## Conclusions
- **Regular HIVES**: Best when alternatives are already well-defined.
- **Approach 1**: Best when you want to explore trade-offs among many good solutions.
- **Approach 2**: Best when you need a single optimal solution that perfectly matches consensus priorities.

Approach 2 is particularly valuable when:
- The problem has many decision variables making manual alternative creation impractical.
- A single optimal solution is required rather than a selection process.
- The mathematical formulation of the problem is well-understood.

By letting HIVES determine the weights first, you ensure the final solution reflects the group's consensus priorities while leveraging the power of optimization algorithms to find the best possible design.