# Análisis del mercado de estudios de Pilates en CABA

Proyecto de análisis de datos desarrollado con Python para estudiar el mercado de los estudios de Pilates en la Ciudad Autónoma de Buenos Aires (CABA).

## Objetivo

El objetivo es construir una base de datos propia sobre estudios de Pilates, para la web Transverso Observatorio Pilates y analizar:

- Distribución geográfica por barrio.
- Presencia digital (Instagram, web, email y aplicaciones).
- Reputación online mediante Google.
- Equipamiento utilizado.
- Servicios adicionales.
- Indicadores del mercado.

## Tecnologías

- Python
- Pandas
- SQLite
- Matplotlib
- Streamlit
- Git y GitHub

## Estructura del proyecto

```text
pilates-caba-analysis/
│
├── data/
│   ├── raw/
│   ├── interim/
│   └── processed/
│
├── notebooks/
├── reports/
├── dashboard/
├── src/
│
├── README.md
├── requirements.txt
└── .gitignore
```

## Estado del proyecto

### ✅ Fase 1 - Limpieza de datos (completada)

Se normalizaron:

- columnas
- seguidores
- puntajes
- teléfonos
- emails
- barrios
- fabricantes
- sitios web
- Instagram
- aplicaciones de reservas

Se generó:

data/interim/estudios_limpios.csv

## Autor: Leandro Estupiñán

Proyecto 
