import pandas as pd
import matplotlib.pyplot as plt


# --- only function with hydro, biomass and electric car battery implemented ---
def plot_energy_balance(n, start_date, end_date, plot_market_price=True):
    """
    Plots an energy balance chart for a defined period.

    This function generates a single figure showing the time evolution
    of energy flows (production, consumption, grid exchanges, hydro)
    and the grid price between a start and end date.

    Args:
        n (pypsa.Network): The optimized PyPSA network containing the time-series data.
        start_date (pd.Timestamp): The start date of the period to plot.
        end_date (pd.Timestamp): The end date of the period to plot.
    """
    # --- 1. Data Preparation and Filtering ---
    # NOTE: We assume the hydro storage reservoir is named 'Hydro Reservoir' and the
    # EV battery is 'Electric Car Battery'. Adjust here if your names differ.
    hydro_name = 'Hydro Reservoir'
    electric_car_battery_name = 'Electric Car Battery'

    # Create a complete DataFrame with all necessary data
    all_data = pd.DataFrame({
        'Solar': n.generators_t.p['Solar'],
        'Wind': n.generators_t.p['Wind'],
        'Consumption': n.loads_t.p['Consumption'],
        'Grid Sale': -n.links_t.p0['Grid Export'],
        'Grid Purchase': -n.links_t.p1['Grid Import'],
        'Biomass ORC': n.generators_t.p.get('Biomass ORC'),
        # ---- Additions for Hydro ----
        'Hydro Dispatch': n.storage_units_t.p_dispatch[hydro_name],
        'Reservoir Pumping': n.storage_units_t.p_store[hydro_name],
        'Reservoir Inflow': n.storage_units_t.inflow[hydro_name],
        # ---- Additions for EV Battery ----
        'EV Battery Dispatch': n.storage_units_t.p_dispatch[electric_car_battery_name],
        'EV Battery Charge': n.storage_units_t.p_store[electric_car_battery_name],
        # ------------------------------------
        'Grid Price': n.links_t.marginal_cost['Grid Import']
    })

    # Select only the specified date range
    plot_data = all_data.loc[start_date:end_date]

    # --- 2. Figure Creation ---
    fig, ax = plt.subplots(figsize=(15, 7))

    # Dynamic title based on the provided dates
    title_str = f"Energy Balance from {start_date.strftime('%d/%m/%Y')} to {end_date.strftime('%d/%m/%Y')}"
    fig.suptitle(title_str, fontsize=18, y=0.95)

    # --- 3. Plotting Power Data (Main Y-Axis) ---
    # Data for the stacked area plot (Power Sources)
    to_stack = pd.DataFrame({
        'Solar': plot_data['Solar'],
        'Wind': plot_data['Wind'],
        'Hydro Dispatch': plot_data['Hydro Dispatch'],
        'Grid Purchase': plot_data['Grid Purchase'],
        'Biomass ORC': plot_data['Biomass ORC'],
        'EV Battery Dispatch': plot_data['EV Battery Dispatch'],
    })

    # Stacked area for production and purchase
    to_stack.plot.area(ax=ax, stacked=True, linewidth=0, alpha=0.7,
                       color=['gold', 'skyblue', 'royalblue', 'grey', 'darkgreen', 'darkorange'])

    # Area for grid sales (plotted as a negative value)
    (plot_data['Grid Sale']).plot.area(ax=ax, stacked=True, linewidth=0, alpha=0.6,
                                       color='lightgreen', label='Grid Sale')

    # Area for EV battery charging (plotted as a negative value, representing a load)
    (-plot_data['EV Battery Charge']).plot.area(ax=ax, stacked=True, linewidth=0, alpha=0.6,
                                                color='lightcoral', label='EV Battery Charge')

    # Line for consumption
    plot_data['Consumption'].plot(ax=ax, color='black', linewidth=2.5, label="Consumption")

    # Line for reservoir inflow
    plot_data['Reservoir Inflow'].plot(ax=ax, color='c', linestyle=':',
                                       linewidth=2, label='Reservoir Inflow')

    # Dynamically calculate Y-axis limits to ensure all data is visible
    y_max = max(to_stack.sum(axis=1).max(), plot_data['Consumption'].max())
    y_min = min(plot_data['Grid Sale'].min(), -plot_data['EV Battery Charge'].max())
    ax.set_ylim(y_min * 1.05, y_max * 1.05)

    # --- 4. Secondary Y-Axis (Right) for PRICE ---
    ax2 = ax.twinx()
    color_price = 'darkred'

    # Plot the price
    if plot_market_price:
        plot_data['Grid Price'].plot(ax=ax2, color=color_price, linewidth=2,
                                     linestyle='--', label="Grid Price (€/MWh)")

    ax2.set_ylabel('Grid Price (€/MWh)', color=color_price, fontsize=12)
    ax2.tick_params(axis='y', labelcolor=color_price)
    ax2.set_ylim(bottom=0)

    # --- 5. Formatting and Legends ---
    ax.set_xlabel('Date and Time', fontsize=12)
    ax.set_ylabel('Power (MW)', fontsize=12)
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.axhline(0, color='black', linewidth=0.5)

    # Merge legends from both axes for a unified display
    lines, labels = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines + lines2, labels + labels2, loc='upper left', ncol=2)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()


def plot_storage_operation(n, storage_name, start_date=None, end_date=None):
    """
    Affiche les données opérationnelles pour une unité de stockage d'énergie spécifique.

    Cette fonction visualise la charge, la décharge, l'apport (si existant) et
    l'état de charge pour une période donnée.

    Paramètres :
    -----------
    n : pypsa.Network
        Un objet réseau PyPSA résolu.
    storage_name : str
        Le nom de l'unité de stockage à afficher.
    start_date : str, optionnel
        La date de début pour filtrer les données (ex: '2022-03-10').
    end_date : str, optionnel
        La date de fin pour filtrer les données (ex: '2022-03-15').
    """
    # --- 1. Récupération et préparation des données ---
    fig, ax = plt.subplots(figsize=(15, 7))

    soc = n.storage_units_t.state_of_charge[storage_name]
    dispatch = n.storage_units_t.p[storage_name]
    dispatch_kw = dispatch * 1000

    discharge = dispatch_kw.where(dispatch_kw > 0, 0)
    charge = -dispatch_kw.where(dispatch_kw < 0, 0)

    data = {
        "Discharge (kW)": discharge,
        "Charge (kW)": charge,
        "State of Charge (kWh)": soc * 1000
    }

    plot_columns = ["Discharge (kW)", "Charge (kW)"]

    if storage_name in n.storage_units_t.inflow.columns:
        inflow = n.storage_units_t.inflow[storage_name]
        data["Inflow (kW)"] = inflow * 1000
        plot_columns.append("Inflow (kW)")

    stats_df = pd.DataFrame(data)

    # NOUVEAU : Filtrer le DataFrame en fonction des dates fournies
    if start_date or end_date:
        stats_df = stats_df.loc[start_date:end_date]
        if stats_df.empty:
            print(f"Attention : Aucune donnée trouvée pour la plage de dates spécifiée pour '{storage_name}'.")
            return

    # --- 2. Génération du graphique ---

    # NOUVEAU : Palette de couleurs améliorée
    plot_colors = {
        "Discharge (kW)": "#E57373",  # Rouge doux
        "Charge (kW)": "#64B5F6",  # Bleu doux
        "Inflow (kW)": "#81C784"  # Vert doux
    }

    colors_to_use = [plot_colors[col] for col in plot_columns if col in plot_colors]

    stats_df[plot_columns].plot(ax=ax, kind='area', alpha=0.8, color=colors_to_use, linewidth=0)

    stats_df['State of Charge (kWh)'].plot(ax=ax, secondary_y=True, color='#424242',
                                           style='--', label='State of Charge (kWh)')

    # --- 3. Personnalisation et affichage ---
    ax.set_title(f"Opération de '{storage_name}': Charge/Décharge, Apport et État de charge")
    ax.set_xlabel("Date")
    ax.set_ylabel("Puissance (kW)")
    ax.right_ax.set_ylabel("Énergie (kWh)")
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Améliorer la légende
    lines, labels = ax.get_legend_handles_labels()
    lines2, labels2 = ax.right_ax.get_legend_handles_labels()
    ax.right_ax.legend(lines + lines2, labels + labels2, loc='upper right', frameon=True)
    ax.get_legend().remove()

    plt.tight_layout()
    plt.show()
