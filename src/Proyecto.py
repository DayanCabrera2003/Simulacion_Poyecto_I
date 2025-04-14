# simulation_debug_complete.py
import heapq
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import csv
import pandas as pd

class SingleServerQueue:
    def __init__(self, arrival_rate, service_rate, T):
        self.arrival_rate = arrival_rate
        self.service_rate = service_rate
        self.T = T
        self.current_time = 0
        self.server_busy = False
        self.queue = []
        self.event_heap = []
        self.arrival_times = []
        self.departure_times = []
        self.total_customers = 0
        self.Tp = 0
        self.debug_log = []

    def schedule_event(self, event_time, event_type):
        if event_type == 'arrival' and event_time > self.T:
            return  # No programar llegadas después de T
        heapq.heappush(self.event_heap, (event_time, event_type))
        self.debug_log.append(f"Scheduled {event_type} at {event_time:.2f}")

    def run(self):
        first_arrival = np.random.exponential(1/self.arrival_rate)
        self.schedule_event(first_arrival, 'arrival')
        self.debug_log.append(f"First arrival scheduled at {first_arrival:.2f}")

        while self.event_heap:
            time, event_type = heapq.heappop(self.event_heap)
            self.current_time = time
            
            if self.current_time > self.T and event_type == 'arrival':
                continue  # Ignorar llegadas posteriores a T

            self.debug_log.append(f"\n--- Processing {event_type} at {time:.2f} ---")

            if event_type == 'arrival':
                if self.current_time <= self.T:
                    next_arrival = self.current_time + np.random.exponential(1/self.arrival_rate)
                    if next_arrival <= self.T:
                        self.schedule_event(next_arrival, 'arrival')
                
                self.total_customers += 1
                self.arrival_times.append(self.current_time)
                self.debug_log.append(f"Customer {self.total_customers} arrived at {self.current_time:.2f}")
                
                if not self.server_busy:
                    service_time = np.random.exponential(1/self.service_rate)
                    self.schedule_event(self.current_time + service_time, 'departure')
                    self.server_busy = True
                    self.debug_log.append(f"Service started. Service time: {service_time:.2f}")
                else:
                    self.queue.append(self.total_customers)
                    self.debug_log.append(f"Added to queue. Queue length: {len(self.queue)}")

            elif event_type == 'departure':
                self.departure_times.append(self.current_time)
                self.debug_log.append(f"Customer departed at {self.current_time:.2f}")
                
                if self.queue:
                    next_customer = self.queue.pop(0)
                    service_time = np.random.exponential(1/self.service_rate)
                    self.schedule_event(self.current_time + service_time, 'departure')
                    self.debug_log.append(f"Next customer {next_customer} from queue. Service time: {service_time:.2f}")
                else:
                    self.server_busy = False
                    self.debug_log.append("Server idle")

        if self.departure_times:
            last_departure = max(self.departure_times)
            self.Tp = max(last_departure - self.T, 0)
        else:
            self.Tp = 0

    def get_results(self):
        if len(self.departure_times) > 0:
            # Asegurar igual longitud de listas
            min_length = min(len(self.departure_times), len(self.arrival_times))
            valid_departures = self.departure_times[:min_length]
            valid_arrivals = self.arrival_times[:min_length]
            
            times_in_system = [d - a for d, a in zip(valid_departures, valid_arrivals)]
            avg_time = np.mean(times_in_system) if times_in_system else 0
            return avg_time, self.Tp
        return 0, 0

def run_experiment(arrival_rates, service_rate, T, num_replications):
    all_replicas_data = []
    detailed_results = []
    
    print("\nIniciando simulación...")
    print(f"Parámetros clave -> μ: {service_rate}, T: {T}, Réplicas: {num_replications}")
    print("="*70)
    
    for λ in arrival_rates:
        print(f"\n▶▶ Procesando λ = {λ} (ρ = {λ/service_rate:.2f})")
        avg_times = []
        Tps = []
        
        for rep in range(num_replications):
            sim = SingleServerQueue(λ, service_rate, T)
            sim.run()
            avg_time, Tp = sim.get_results()
            
            all_replicas_data.append({
                'λ': λ,
                'Réplica': rep + 1,
                'W': avg_time,
                'Tp': Tp
            })
            
            avg_times.append(avg_time)
            Tps.append(Tp)
            
            if rep < 2:
                with open(f'debug_log_λ{λ}_rep{rep}.txt', 'w') as f:
                    f.write("\n".join(sim.debug_log))

            if (rep + 1) % 10 == 0:
                print(f"    Réplica {rep + 1}/{num_replications} completada")
        
        mean_avg = np.mean(avg_times)
        ci_avg = stats.t.interval(0.95, len(avg_times)-1, loc=mean_avg, scale=stats.sem(avg_times))
        mean_Tp = np.mean(Tps)
        ci_Tp = stats.t.interval(0.95, len(Tps)-1, loc=mean_Tp, scale=stats.sem(Tps))
        
        detailed_results.append({
            'λ': λ,
            'avg_time': mean_avg,
            'ci_avg': ci_avg,
            'avg_Tp': mean_Tp,
            'ci_Tp': ci_Tp
        })
        
        print(f"\n►► Resultados para λ = {λ}:")
        print(f"    Tiempo en sistema: {mean_avg:.2f} (IC 95%: {ci_avg[0]:.2f} - {ci_avg[1]:.2f})")
        print(f"    Tp promedio: {mean_Tp:.2f} (IC 95%: {ci_Tp[0]:.2f} - {ci_Tp[1]:.2f})")
        print("-"*70)
    
    # Guardar todos los datos
    df = pd.DataFrame(all_replicas_data)
    df.to_csv('full_simulation_data.csv', index=False)
    
    with open('simulation_results.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['λ', 'Avg_Time', 'CI_Low', 'CI_High', 'Avg_Tp', 'Tp_CI_Low', 'Tp_CI_High'])
        for res in detailed_results:
            writer.writerow([
                res['λ'],
                res['avg_time'],
                res['ci_avg'][0],
                res['ci_avg'][1],
                res['avg_Tp'],
                res['ci_Tp'][0],
                res['ci_Tp'][1]
            ])
    
    # Generar gráfica
    generate_validation_plot(df)
    
    return detailed_results

def generate_validation_plot(df):
    plt.figure(figsize=(12, 7))
    
    # Teoría
    λ_values = np.linspace(min(df['λ']), max(df['λ']), 100)
    theoretical_W = [1/(1.0 - λ) if λ < 1.0 else np.nan for λ in λ_values]
    
    # Simulación
    simulated_means = df.groupby('λ')['W'].mean().reset_index()
    
    # Gráficos
    plt.plot(λ_values, theoretical_W, 'r--', lw=2, label='Teoría M/M/1')
    plt.scatter(
        simulated_means['λ'], 
        simulated_means['W'], 
        s=100, 
        color='blue', 
        edgecolor='black',
        label='Media Simulada'
    )
    
    # Puntos individuales
    plt.scatter(
        df['λ'] + np.random.uniform(-0.01, 0.01, size=len(df)),  # Jitter para visualización
        df['W'],
        alpha=0.4,
        color='green',
        label='Réplicas Individuales'
    )
    
    plt.title('Validación del Modelo M/M/1\nTiempo Promedio en el Sistema vs. Intensidad de Tráfico', pad=20)
    plt.xlabel('λ (tasa de llegadas)', fontsize=12)
    plt.ylabel('W (tiempo en el sistema)', fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xlim(0, 1.0)
    plt.ylim(0, 25)
    
    plt.savefig(
        'mm1_validation_final.png',
        dpi=300,
        bbox_inches='tight',
        facecolor='white'
    )
    print("\nGráfica de validación guardada como: mm1_validation_final.png")

if __name__ == "__main__":
    # Configuración recomendada para resultados estables
    arrival_rates = [0.1, 0.3, 0.5, 0.7, 0.9]  # Múltiples valores de λ
    service_rate = 1.0
    T = 10_000  # Tiempo de simulación aumentado
    num_replications = 30
    
    results = run_experiment(arrival_rates, service_rate, T, num_replications)