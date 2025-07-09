import pandas as pd
import matplotlib.pyplot as plt

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

# --- show the dam in, out and charge ---
def plot_hydro_reservoir_operation(n):
    # --- 2. Generate the Plot ---
    fig, ax = plt.subplots(figsize=(15, 7))
    # Combine the relevant time series into a single DataFrame
    hydro_soc = n.storage_units_t.state_of_charge['Hydro Reservoir']
    hydro_inflow = n.storage_units_t.inflow['Hydro Reservoir']
    hydro_dispatch = n.storage_units_t.p['Hydro Reservoir']
    hydro_stats = pd.DataFrame({
        "Discharge (kW)": hydro_dispatch * 1000,
        "Inflow (kW)": hydro_inflow * 1000,
        "State of Charge (kWh)": hydro_soc * 1000
    })
    # Plot power flows (MW) on the primary y-axis
    # An area plot helps visualize the volume of inflow versus discharge
    hydro_stats[['Discharge (kW)', 'Inflow (kW)']].plot(ax=ax, kind='area', alpha=0.7)

    # Plot energy level (MWh) on the secondary y-axis for scale
    hydro_stats['State of Charge (kWh)'].plot(ax=ax, secondary_y=True, color='dodgerblue',
                                              style='--', label='State of Charge (kWh)')

    # --- 3. Customize and Display the Plot ---
    ax.set_title("Hydro Reservoir Operation: Inflow, Discharge, and Stored Energy")
    ax.set_xlabel("Date")
    ax.set_ylabel("Power (kW)")
    ax.right_ax.set_ylabel("Energy (kWh)")  # Label for the secondary axis
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Improve the legend
    lines, labels = ax.get_legend_handles_labels()
    lines2, labels2 = ax.right_ax.get_legend_handles_labels()
    ax.right_ax.legend(lines + lines2, labels + labels2, loc='upper right')
    ax.get_legend().remove()  # Remove the old legend

    plt.tight_layout()
    plt.show()


# --- TODO: implement hydro, biomass and electric car battery  ---
def plot_typical_days(n):
    """
    Trace deux graphiques côte à côte du bilan énergétique pour une journée
    typique d'hiver et une journée typique d'été, en moyennant les données.

    Cette fonction génère une seule figure avec deux sous-graphiques :
    1. (Gauche) Un bilan énergétique pour une journée d'hiver moyenne.
    2. (Droite) Un bilan énergétique pour une journée d'été moyenne.

    Les axes Y sont en mode automatique pour s'adapter aux données. L'axe Y
    principal (Puissance) est partagé entre les deux graphiques pour faciliter
    la comparaison.

    Args:
        n (pypsa.Network): Le réseau PyPSA optimisé contenant les données temporelles.
    """

    # --- 1. Définition des saisons ---
    winter_months = [12, 1, 2]  # Hiver: Décembre, Janvier, Février
    summer_months = [6, 7, 8]  # Été: Juin, Juillet, Août

    # --- 2. Préparation des données ---
    all_data = pd.DataFrame({
        'Solar': n.generators_t.p['Solar'],
        'Wind': n.generators_t.p['Wind'],
        'Consumption': n.loads_t.p['Consumption'],
        'Grid Export': n.links_t.p0['Grid Export'],
        'Grid Import': -n.links_t.p1['Grid Import'],  # Achat, déjà positif
        'Grid Price': n.links_t.marginal_cost['Grid Import']
    })
    all_data['hour'] = all_data.index.hour
    all_data['month'] = all_data.index.month

    # --- 3. Calcul de la journée moyenne pour chaque saison ---
    avg_winter_day = all_data[all_data['month'].isin(winter_months)].groupby('hour').mean()
    avg_summer_day = all_data[all_data['month'].isin(summer_months)].groupby('hour').mean()

    # --- 4. Création de la figure avec deux sous-graphiques côte à côte ---
    # sharey=True lie l'axe Y de gauche (Puissance) pour les deux graphiques
    fig, axes = plt.subplots(1, 2, figsize=(15, 7), sharey=True)
    fig.suptitle("Bilan Énergétique Moyen à Castanheira de Pera", fontsize=18, y=0.97)

    # Liste des données et des titres pour la boucle
    seasons_data = [
        ('Hiver', avg_winter_day),
        ('Été', avg_summer_day)
    ]

    # Calculer le maximum global pour l'axe des prix
    max_price = max(avg_winter_day['Grid Price'].max(), avg_summer_day['Grid Price'].max())
    ylim_price = max_price * 1.05  # Ajoute une marge de 5%

    for ax, (season, data) in zip(axes, seasons_data):
        # Données pour le graphique empilé (Production et Achat)
        to_stack = pd.DataFrame({
            'Solaire': data['Solar'],
            'Éolien': data['Wind'],
            'Achat réseau': data['Grid Import']
        })
        p_grid_export = data['Grid Export']

        # Aire empilée pour la production et l'achat
        to_stack.plot.area(ax=ax, stacked=True, linewidth=0, alpha=0.7, color=['gold', 'skyblue', 'grey'])
        # Aire pour la vente (rendue négative pour le graphique)
        (-p_grid_export).plot.area(ax=ax, stacked=True, linewidth=0, alpha=0.6, color='lightgreen',
                                   label='Vente réseau')
        # Consommation
        data['Consumption'].plot(ax=ax, color='black', linewidth=2.5, label="Consommation")

        # --- Axe Y Secondaire (à droite) pour le PRIX ---
        ax2 = ax.twinx()
        color_price = 'darkgreen'

        # Le label de l'axe Y du prix est affiché sur les deux graphiques
        ax2.set_ylabel('Prix du Réseau (€/MWh)', color=color_price, fontsize=12)
        ax2.tick_params(axis='y', labelcolor=color_price)
        ax2.set_ylim(bottom=0, top=ylim_price)

        # Tracé du prix
        data['Grid Price'].plot(ax=ax2, color=color_price, linewidth=2, linestyle='--', label="Prix du Réseau (€/MWh)")

        # --- Mise en forme et légendes ---
        ax.set_title(f"Journée Typique d'{season}", fontsize=16)
        ax.set_xlabel('Heure de la journée', fontsize=12)
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        ax.axhline(0, color='black', linewidth=0.5)

        # Formater l'axe X pour afficher les heures
        ax.set_xticks(range(0, 24, 2))
        ax.set_xticklabels([f"{h:02d}:00" for h in range(0, 24, 2)])
        ax.set_xlim(0, 23)

        # Fusionner les légendes pour chaque sous-graphique
        lines, labels = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines + lines2, labels + labels2, loc='upper left')

    # --- Ajustements finaux ---
    # Le label de l'axe Y principal (Puissance) n'est affiché qu'une seule fois à gauche
    axes[0].set_ylabel('Puissance (MW)', fontsize=12)

    # plt.tight_layout(rect=[0, 0, 1, 0.95])  # Ajuste pour faire de la place au suptitle
    plt.show()


# --- TODO: implement hydro, biomass and electric car battery  ---
def plot_annual_view(n, resample_period='1M'):
    # --- 1. Préparation des données sur toute l'année ---
    # On s'assure que le nom du réservoir est correct
    hydro_name = 'Hydro Reservoir'

    # Création d'un DataFrame avec toutes les séries temporelles de l'année
    all_data = pd.DataFrame({
        'Solaire': n.generators_t.p.get('Solar', 0),
        'Éolien': n.generators_t.p.get('Wind', 0),
        'Hydraulique': n.storage_units_t.p_dispatch.get(hydro_name, 0),
        'Consommation': n.loads_t.p_set.get('Consumption', 0),
        'Achat réseau': -n.links_t.p1.get('Grid Import', 0),
        'Vente réseau': -n.links_t.p0.get('Grid Export', 0)
    })

    # --- 2. Rééchantillonnage en moyennes journalières ---
    # C'est l'étape clé : on regroupe les données par jour ('D') et on calcule la moyenne
    daily_avg_data = all_data.resample(resample_period).mean()

    # --- 3. Création du graphique ---
    fig, ax = plt.subplots(figsize=(18, 8))
    fig.suptitle("Bilan Énergétique Annuel (Moyennes Journalières)", fontsize=18)

    # --- Tracé des aires de production (empilées) ---
    sources_a_empiler = daily_avg_data[['Solaire', 'Éolien', 'Hydraulique', 'Achat réseau']]

    sources_a_empiler.plot.area(ax=ax, stacked=True, linewidth=0, alpha=0.8,
                                color={'Solaire': 'gold', 'Éolien': 'skyblue',
                                       'Hydraulique': 'royalblue', 'Achat réseau': 'grey'})

    # --- Tracé de l'aire de vente (en négatif) ---
    daily_avg_data[['Vente réseau']].plot.area(ax=ax, stacked=True, linewidth=0, alpha=0.7,
                                               color={'Vente réseau': 'lightgreen'})

    # --- Tracé de la ligne de consommation ---
    daily_avg_data['Consommation'].plot(ax=ax, color='black', linewidth=2.5, label='Consommation', ls='-')

    # --- 4. Mise en forme du graphique ---
    ax.set_ylabel('Puissance Moyenne Journalière (MW)', fontsize=14)
    ax.set_xlabel('Mois', fontsize=14)
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.axhline(0, color='black', linewidth=1)

    # Amélioration de la légende
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, loc='upper left', ncol=3, fontsize=12, frameon=True)

    # Ajustement des limites de l'axe Y pour une meilleure visualisation
    y_max = max(sources_a_empiler.sum(axis=1).max(), daily_avg_data['Consommation'].max())
    y_min = daily_avg_data['Vente réseau'].min()
    ax.set_ylim(y_min * 1.1, y_max * 1.1)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()
