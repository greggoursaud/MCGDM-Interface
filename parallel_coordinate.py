import plotly.express as px
from hives import hives_algorithm
import pandas as pd

# data = {
#     'Candidates': ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10', 'A11', 'A12', 'A13', 'A14', 'A15'],
#     'Criteria_1': [246.560614, 2062.143314, 1658.680492, 1725.924295, 1143.144663, 2017.314112, 717.267240, 1950.070308, 1501.778283, 1232.803068, 358.633620, 627.608835, 1322.461473, 1860.411903, 1075.900860],
#     'Criteria_2': [281.577203, 921.525391, 627.149225, 1113.509848, 1036.716065, 870.329536, 985.520210, 191.984456, 575.953369, 1011.118138, 1139.107775, 1228.700522, 998.319174, 383.968913, 742.339898],
#     'Criteria_3': [191.429393, 119.643370, 179.465056, 861.432268, 155.536382, 143.572045, 155.536382, 442.680471, 454.644808, 167.500719, 957.146964, 131.607708, 897.325279, 813.574919, 406.787460],
#     'Criteria_4': [1710.011494, 768.266033, 148.696652, 2329.580875, 223.044977, 99.131101, 198.262202, 148.696652, 247.827753, 817.831584, 570.003831, 1833.925370, 2230.449774, 2329.580875, 693.917708],
#     'Criteria_5': [1159.169985, 778.547005, 346.020891, 605.536559, 363.321936, 986.159540, 882.353272, 69.204178, 1608.997144, 709.342827, 224.913579, 328.719847, 865.052228, 674.740738, 519.031337],
#     'Criteria_6': [171.812450, 386.578012, 451.007W681, 1052.351256, 805.370859, 418.792847, 966.445031, 332.886622, 451.007681, 655.034965, 483.222515, 182.550728, 998.659865, 139.597616, 214.765562],
#     'Total Score': [3760.561138, 5036.703126, 3411.019996, 7688.335101, 3727.134882, 4535.299180, 3905.384337, 3135.522687, 4840.209038, 4593.631300, 3733.028285, 4333.113008, 7312.267793, 6201.874964, 3652.742824],
#     'Ranking': [10, 4, 14, 1, 12, 7, 9, 15, 5, 6, 11, 8, 2, 3, 13]
# }

data = hives_algorithm('candidates_scores.csv', 'criteria_weights.csv')

df = pd.DataFrame(data)

import plotly.express as px

def parallel_coordinates_plot(data):
    criteria_cols = [col for col in data.columns if col not in ["Candidates", "Total Score", "Ranking"]]

    fig = px.parallel_coordinates(
        data, 
        dimensions=criteria_cols + ["Total Score"],
        color="Ranking", 
        labels={col: col.replace("_", " ") for col in data.columns},
        color_continuous_scale=px.colors.diverging.Tealrose[::-1],
        color_continuous_midpoint=data["Ranking"].median(),
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="black",
        plot_bgcolor="black",
        font=dict(size=16, color="white"),
        title=dict(
            text="Parallel Coordinates Plot - Decision Criteria",
            font=dict(size=20, color="white"),
            x=0.5
        ),
        margin=dict(l=120, r=120, t=80, b=60),
        width=1500,
        height=700
    )
    #fig.show()
    return fig


parallel_coordinates_plot(df)



