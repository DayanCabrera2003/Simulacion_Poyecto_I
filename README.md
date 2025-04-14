# Simulación de Sistemas de Colas M/M/1 🕒📊

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)


Repositorio para simulación y análisis de colas M/M/1 mediante eventos discretos. Incluye validación teórica, generación de gráficos profesionales y análisis estadístico.

## Características Clave ✨
- Simulación precisa de colas con llegadas/servicios exponenciales
- Generación automática de:
  - Gráficos comparativos teoría vs simulación (`mm1_validation_final.png`)
  - Datos detallados en CSV (`full_simulation_data.csv`, `simulation_results.csv`)
  - Logs de depuración para réplicas seleccionadas
- Intervalos de confianza al 95% para métricas clave

## Requisitos 📋
- Python 3.8+
- Dependencias:
  ```bash
  pip install numpy scipy matplotlib pandas
