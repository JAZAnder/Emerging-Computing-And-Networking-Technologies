#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt

def generate_handoff_plot():
    #Check for file
    try:
        data = pd.read_csv("handoff_log.csv")
    except FileNotFoundError:
        print("[!] Error: handoff_log.csv not found. Run wireless_edge_handoff.py first.")
        return

    #Find handoff timestamp (first instance where associated AP shifts to ap2)
    handoff_events = data[data['associated_ap'] == 'ap2']
    if not handoff_events.empty:
        handoff_idx = handoff_events.index[0]
        handoff_time = data.loc[handoff_idx, 'elapsed_time']
    else:
        #If handoff time is not found, then assume half way
        handoff_time = data['elapsed_time'].median()

    #Create subplots sharing the X-axis
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 8), sharex=True)

    ax1.plot(
        data['elapsed_time'], 
        data['response_time_ms'], 
        color='#1f77b4', 
        marker='o', 
        markersize=3, 
        linestyle='-', 
        label='Response Latency'
    )
    ax1.axvline(
        x=handoff_time, 
        color='#d62728', 
        linestyle='--', 
        linewidth=1.8, 
        label=f'Physical Handoff ({handoff_time}s)'
    )
    ax1.set_ylabel('Latency (ms)')
    ax1.set_title('Response Latency & Packet Drop')
    ax1.grid(True)
    ax1.legend(loc='upper left')

    # Annotate the exact handoff event
    max_latency = data['response_time_ms'].max()


    #De-skewed Timeline (Latency Shift & Drops)
    #Filter successful responses
    data_success = data[data["status"] == "SUCCESS"].copy()
    data_drops = data[data["status"] == "DROP"].copy()

    #Plot success line segments colored by active ap
    ap1_success = data_success[data_success["associated_ap"] == "ap1"]
    ap2_success = data_success[data_success["associated_ap"] == "ap2"]

    ax2.plot(
        ap1_success["elapsed_time"],
        ap1_success["response_time_ms"],
        marker="o",
        linestyle="-",
        linewidth=1.5,
        markersize=4,
        color="#1f77b4",
        label="ap1 -> edge1",
    )
    ax2.plot(
    ap2_success["elapsed_time"],
    ap2_success["response_time_ms"],
    marker="o",
    linestyle="-",
    linewidth=1.5,
    markersize=4,
    color="#ff7f0e",
    label="ap2 -> edge2",
    )

    # Mark handoff point
    handoff_row = data[data["associated_ap"] == "ap2"].iloc[0]
    handoff_time = handoff_row["elapsed_time"]
    ax2.axvline(
        x=handoff_time, 
        color='#d62728', 
        linestyle='--', 
        linewidth=1.8, 
        label=f'Physical Handoff ({handoff_time}s)'
    )

    # Clip Y-axis to focus on delays (0 to 200ms)
    ax2.set_ylim(0, 180)

    # Plot DROPs at the top boundary y=170
    if not data_drops.empty:
        drop_y = [170] * len(data_drops)
        ax2.scatter(
            data_drops["elapsed_time"],
            drop_y,
            color="red",
            marker="X",
            s=70,
            zorder=5,
            label="Dropped Request (500ms Timeout)",
        )

        # Add red shaded vertical lines for drops
        for _, drop in data_drops.iterrows():
            ax2.axvline(
                x=drop["elapsed_time"], color="red", alpha=0.2, linestyle=":"
            )
    ax2.set_title(
        "Edge Response Time Timeline Across Handoff (De-skewed)",
        fontsize=12,
        pad=15,
    )
    ax2.set_xlabel("Elapsed Time (seconds)", labelpad=10)
    ax2.set_ylabel("HTTP Response Time (ms)", labelpad=10)
    ax2.legend(loc="upper left", frameon=True)
    ax2.grid(True)
    
    plt.tight_layout()

    # 4. Open interactive GUI window
    print("[*] Launching interactive plot GUI window...")
    plt.show()

if __name__ == '__main__':
    generate_handoff_plot()