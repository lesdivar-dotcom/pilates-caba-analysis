# Observatorio Pilates Transverso

Proyecto de análisis de datos desarrollado en Python para construir el primer Observatorio del mercado de estudios de Pilates de la Ciudad Autónoma de Buenos Aires (CABA).

El objetivo es generar una base de datos propia, confiable y reproducible que permita estudiar la oferta de estudios de Pilates desde una perspectiva territorial, tecnológica y de equipamiento.

---

# Objetivos

El Observatorio busca responder preguntas como:

- ¿Dónde se concentran los estudios de Pilates?
- ¿Qué barrios presentan mayor o menor oferta?
- ¿Cómo es la presencia digital del sector?
- ¿Qué fabricantes de equipamiento predominan?
- ¿Qué características presenta el mercado?

---

# Tecnologías

- Python
- Pandas
- SQLite (próxima etapa)
- Matplotlib
- Streamlit (futuro dashboard)
- Git y GitHub

---

# Arquitectura del proyecto

```text
pilates-caba-analysis/

├── data/
│   ├── raw/
│   ├── interim/
│   └── processed/
│
├── notebooks/
├── reports/
├── dashboard/
├── src/
│   ├── cleaning.py
│   ├── constants.py
│   ├── features.py
│   └── analysis.py
│
├── README.md
├── roadmap.md
├── diccionario_datos.md
├── requirements.txt
└── .gitignore
```

---

# Estado del proyecto

## ✅ Motor 1 — Limpieza de datos (completado)

Normalización de:

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

Salida:

```
data/interim/estudios_limpios.csv
```

---

## ✅ Motor 2 — Ingeniería de variables (completado)

Generación de variables analíticas:

### Geografía

- barrio
- comuna
- zona

### Presencia digital

- presencia_digital

### Contactabilidad

- n_canales_contacto

### Equipamiento

- n_fabricantes
- fabricante_multiple

Salida:

```
data/processed/estudios_features.csv
```

---

# Próxima etapa

## Motor 3 — Análisis

Se desarrollará el módulo `analysis.py`, encargado de transformar las variables analíticas en indicadores, tablas, visualizaciones y conocimiento sobre el mercado.

---

# Roadmap

Las próximas etapas incluyen:

- análisis territorial
- análisis digital
- análisis de fabricantes
- migración a SQLite
- carga manual de nuevos estudios
- dashboard interactivo
- expansión a otras ciudades
- expansión internacional

---

# Autor

**Leandro Estupiñán**

Proyecto desarrollado para **Transverso – Observatorio Pilates**.