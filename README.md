# Repair Process Simulation Dashboard

This project is a simulation app built using [Simpy](https://simpy.readthedocs.io/) and [Streamlit](https://streamlit.io/). The simulation models a repair process where vehicles arrive for a spare part replacement. When a vehicle is served, a working part is removed from the supply and replaced with a broken part that enters a repair cycle before returning to the supply pool.

The app dynamically records and visualizes key metrics over time, including:

- **Demand Satisfaction Rate:** The ratio of vehicles served (demand satisfied) to total vehicle arrivals.
- **Demand Backlog Queue:** The number of vehicles waiting for a spare part.
- **Available Supply:** The count of spare parts available.
- **Units in Repair:** The count of parts currently undergoing repair.

## Features

- **Stochastic Vehicle Arrivals:** Vehicles arrive following an exponential distribution.
- **Repair Cycle Modeling:** Simulates the time a broken part is unavailable during repair.
- **Dynamic Metrics Collection:** Records simulation state at fixed intervals.
- **Interactive Dashboard:** Adjust simulation parameters via a sidebar and view time series plots for each metric.

## Installation

Ensure you have Python 3.7 or later installed. Then, clone this repository and install the required packages:

```bash
git clone https://github.com/yourusername/repair-process-simulation.git
cd repair-process-simulation
pip install simpy streamlit matplotlib
```

## Usage

Run the app using Streamlit:

```bash
streamlit run app.py
```

Once the app launches in your web browser, use the sidebar to set the following simulation parameters:
- **Initial Part Supply Level**
- **Part Demand Rate (arrivals per time unit)**
- **Repair Cycle Time (time units)**
- **Simulation Time (time units)**
- **Record Interval (time units)**

Click the **"Run Simulation"** button to start the simulation. The dashboard will display final aggregate metrics along with time series plots that visualize:

- Available Supply over time
- Demand Backlog over time
- Units in Repair over time
- Demand Satisfaction Rate over time

## How It Works
1. **Simulation Model:**

- A **Container** represents the pool of working spare parts.
- **Vehicle Processes** simulate vehicles arriving and requesting a spare part. If a spare is available, it is allocated; otherwise, the vehicle waits in a backlog.
- When a vehicle is served, its removed part enters a **Repair Process** that holds the part for a fixed duration (repair cycle time) before returning it to the supply.

2. **Metrics Collection:**

- A dedicated **Observer Process** records simulation metrics at regular intervals. These snapshots include available supply, backlog length, parts in repair, and cumulative demand satisfaction rate.

3. **Visualization:**

- The collected data is plotted as time series using Matplotlib, offering insights into how the system evolves over the simulation period.

## Contributing
Contributions are welcome! Please open issues or submit pull requests for improvements, bug fixes, or additional features.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.

## Acknowledgments
Simpy for the simulation framework.
Streamlit for the interactive dashboard.
Matplotlib for the visualization library.
