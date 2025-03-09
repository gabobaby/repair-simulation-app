import random
import simpy
import streamlit as st
import matplotlib.pyplot as plt

def repair_process(env, container, repair_cycle_time, counters):
    """
    Process representing the repair cycle.
    A part is out of service for 'repair_cycle_time' before returning to the supply.
    """
    counters["in_repair"] += 1
    yield env.timeout(repair_cycle_time)
    # Return the repaired part back to the supply
    yield container.put(1)
    counters["in_repair"] -= 1

def vehicle(env, container, repair_cycle_time, counters):
    """
    Process representing a vehicle arrival.
    The vehicle requests a spare part. If available, it is served immediately.
    The served part is then sent to repair.
    """
    counters["total_arrivals"] += 1
    # Request one spare part; if not available, the process waits in the get queue (backlog)
    yield container.get(1)
    counters["served"] += 1
    # Start the repair process for the removed (now broken) part
    env.process(repair_process(env, container, repair_cycle_time, counters))

def vehicle_generator(env, container, repair_cycle_time, demand_rate, counters):
    """
    Continuously generate vehicles using an exponential interarrival time.
    """
    while True:
        yield env.timeout(random.expovariate(demand_rate))
        env.process(vehicle(env, container, repair_cycle_time, counters))

def metrics_observer(env, container, counters, record_interval, timeseries):
    """
    Observer process that records simulation metrics at regular intervals.
    """
    while True:
        snapshot = {
            "time": env.now,
            "available_supply": container.level,
            "backlog": len(container.get_queue),
            "in_repair": counters["in_repair"],
            "total_arrivals": counters["total_arrivals"],
            "served": counters["served"],
            "satisfaction_rate": (counters["served"] / counters["total_arrivals"]) if counters["total_arrivals"] > 0 else 0,
        }
        timeseries.append(snapshot)
        yield env.timeout(record_interval)

def run_simulation(initial_supply, demand_rate, repair_cycle_time, sim_time, record_interval=1.0):
    """
    Run the repair process simulation.
    
    Parameters:
        initial_supply (int): Initial number of spare parts available.
        demand_rate (float): Rate at which vehicles arrive (per time unit).
        repair_cycle_time (float): Fixed time a part spends in repair.
        sim_time (float): Total simulation time.
        record_interval (float): Interval at which to record state metrics.
    
    Returns:
        tuple: (final_metrics, timeseries) where final_metrics is a dict of final counts,
               and timeseries is a list of snapshots recorded over time.
    """
    env = simpy.Environment()
    # Container representing the available working spare parts
    container = simpy.Container(env, init=initial_supply, capacity=initial_supply)
    counters = {"total_arrivals": 0, "served": 0, "in_repair": 0}
    timeseries = []
    
    env.process(vehicle_generator(env, container, repair_cycle_time, demand_rate, counters))
    env.process(metrics_observer(env, container, counters, record_interval, timeseries))
    env.run(until=sim_time)
    
    # Final metrics calculation
    backlog = len(container.get_queue)
    satisfaction_rate = (counters["served"] / counters["total_arrivals"]) if counters["total_arrivals"] > 0 else 0
    final_metrics = {
        "demand_satisfaction_rate": satisfaction_rate,
        "total_arrivals": counters["total_arrivals"],
        "served": counters["served"],
        "backlog": backlog,
        "available_supply": container.level,
        "in_repair": counters["in_repair"],
    }
    
    return final_metrics, timeseries

# --- Streamlit Frontend ---
st.title("Repair Process Simulation with Time Series Metrics")

# Sidebar for simulation parameters
st.sidebar.header("Simulation Parameters")
initial_supply = st.sidebar.number_input("Initial Part Supply Level", value=10, min_value=1, step=1)
demand_rate = st.sidebar.slider("Part Demand Rate (arrivals per time unit)", min_value=0.1, max_value=5.0, value=1.0, step=0.1)
repair_cycle_time = st.sidebar.slider("Repair Cycle Time (time units)", min_value=1.0, max_value=20.0, value=5.0, step=0.5)
sim_time = st.sidebar.number_input("Simulation Time (time units)", value=100, min_value=10, step=10)
record_interval = st.sidebar.number_input("Record Interval (time units)", value=1.0, min_value=0.1, step=0.1)

if st.button("Run Simulation"):
    final_metrics, timeseries = run_simulation(initial_supply, demand_rate, repair_cycle_time, sim_time, record_interval)
    
    st.write("### Final Simulation Metrics")
    st.write(f"**Total Vehicle Arrivals:** {final_metrics['total_arrivals']}")
    st.write(f"**Vehicles Served (Demand Satisfied):** {final_metrics['served']}")
    satisfaction_rate_percent = final_metrics["demand_satisfaction_rate"] * 100
    st.write(f"**Demand Satisfaction Rate:** {satisfaction_rate_percent:.2f}%")
    st.write(f"**Demand Backlog Queue:** {final_metrics['backlog']}")
    st.write(f"**Available Supply:** {final_metrics['available_supply']}")
    st.write(f"**Units in Repair Cycle:** {final_metrics['in_repair']}")
    
    # Convert timeseries data into lists for plotting
    times = [entry["time"] for entry in timeseries]
    supply = [entry["available_supply"] for entry in timeseries]
    backlog = [entry["backlog"] for entry in timeseries]
    in_repair = [entry["in_repair"] for entry in timeseries]
    satisfaction_rate_ts = [entry["satisfaction_rate"] for entry in timeseries]
    
    # Create a 2x2 grid of subplots for time series metrics
    fig, axs = plt.subplots(2, 2, figsize=(12, 10))
    
    # Plot Available Supply over Time
    axs[0, 0].plot(times, supply, label="Available Supply", color="green")
    axs[0, 0].set_title("Available Supply Over Time")
    axs[0, 0].set_xlabel("Time")
    axs[0, 0].set_ylabel("Supply Level")
    axs[0, 0].legend()
    
    # Plot Demand Backlog over Time
    axs[0, 1].plot(times, backlog, label="Demand Backlog", color="red")
    axs[0, 1].set_title("Demand Backlog Over Time")
    axs[0, 1].set_xlabel("Time")
    axs[0, 1].set_ylabel("Backlog")
    axs[0, 1].legend()
    
    # Plot Units in Repair over Time
    axs[1, 0].plot(times, in_repair, label="Units in Repair", color="blue")
    axs[1, 0].set_title("Units in Repair Over Time")
    axs[1, 0].set_xlabel("Time")
    axs[1, 0].set_ylabel("In Repair")
    axs[1, 0].legend()
    
    # Plot Demand Satisfaction Rate over Time
    axs[1, 1].plot(times, satisfaction_rate_ts, label="Demand Satisfaction Rate", color="purple")
    axs[1, 1].set_title("Demand Satisfaction Rate Over Time")
    axs[1, 1].set_xlabel("Time")
    axs[1, 1].set_ylabel("Satisfaction Rate")
    axs[1, 1].legend()
    
    st.pyplot(fig)
