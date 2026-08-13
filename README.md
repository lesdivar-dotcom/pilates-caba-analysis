# Observatorio Pilates Transverso

Proyecto de análisis de datos desarrollado en Python para construir el primer Observatorio del mercado de estudios de Pilates de la Ciudad Autónoma de Buenos Aires (CABA).

El objetivo es generar una base de datos propia, confiable y reproducible que permita estudiar la oferta de estudios de Pilates desde una perspectiva territorial, tecnológica y empresarial.

---

# Objetivos

El Observatorio busca responder preguntas como:

- ¿Dónde se concentran los estudios de Pilates?
- ¿Qué barrios presentan mayor o menor oferta?
- ¿Cómo es la presencia digital del sector?
- ¿Qué fabricantes de equipamiento predominan?
- ¿Qué características presenta el mercado?
- ¿Qué marcas poseen múltiples sedes?

---

# Tecnologías

- Python
- Pandas
- SQLite
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
│   ├── processed/
│   ├── analysis/
│   └── database/
│
├── notebooks/
├── reports/
├── dashboard/
├── src/
│   ├── cleaning.py
│   ├── features.py
│   ├── analysis.py
│   ├── database.py
│   ├── load_database.py
│   └── rebuild_estudios_marcas.py
│
├── README.md
├── roadmap.md
├── diccionario_datos.md
├── requirements.txt
└── .gitignore
```

---

# Estado del proyecto

## Motor 1 — Limpieza de datos (completado)

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

## Motor 2 — Ingeniería de variables (completado)

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

## Motor 3 — Análisis (completado)

Implementación del motor analítico del Observatorio.

Incluye:

- análisis territorial
- indicadores digitales
- equipamiento
- rankings
- cruces
- indicadores compuestos
- exportación automática de resultados

Salida principal:

```
data/analysis/
```

---

## Motor 4 — SQLite (completado)

Implementación del modelo relacional del Observatorio.

Incluye:

- base SQLite reproducible
- carga automática
- validaciones
- integridad referencial
- reconstrucción automática de la relación estudio-marca

Salida principal:

```
data/database/observatorio_pilates.db
```
## Motor 4.3 — Carga Manual / Curación (diseño completado)

El Observatorio incorpora una capa de curación manual para registrar conocimiento verificado sin modificar el código ni la base SQLite directamente.

### Principio

> El conocimiento humano entra por archivos maestros; el sistema reconstruye automáticamente el resto.

### Catálogos curados

| Archivo | Rol |
|---------|-----|
| `marcas_maestra.csv` | Catálogo oficial de marcas del Observatorio. |
| `estudios_marcas_verificado.csv` | Relaciones sede–marca verificadas manualmente. |

### Archivos generados

| Archivo | Origen |
|---------|--------|
| `estudios_marcas.csv` | Reconstruido automáticamente. |
| `observatorio_pilates.db` | Sincronizado automáticamente desde los archivos procesados. |

### Flujo oficial

```text
Curación manual
       │
       ▼
marcas_maestra.csv
       │
estudios_marcas_verificado.csv
       │
       ▼
rebuild_estudios_marcas.py
       │
       ▼
estudios_marcas.csv
       │
       ▼
load_database.py
       │
       ▼
observatorio_pilates.db
```

### Reglas de gobernanza

Nunca se editan manualmente:

- `estudios_features.csv`
- `estudios_marcas.csv`
- `observatorio_pilates.db`

Siempre se editan manualmente:

- `marcas_maestra.csv`
- `estudios_marcas_verificado.csv`

Esto garantiza trazabilidad y reproducibilidad del Observatorio.

---

# Decisión Metodológica DM-001 — Sede ≠ Marca

## Unidad de análisis del Observatorio

El Observatorio distingue dos niveles de análisis.

| Concepto | Definición |
|----------|------------|
| **Sede** | Establecimiento físico donde se dictan clases de Pilates. Cada sede constituye un registro independiente del relevamiento y posee un `id_estudio`. |
| **Marca** | Identidad comercial que puede operar una o múltiples sedes. Cada marca posee un `id_marca`. |

## Estado actual del relevamiento

| Indicador | Valor |
|-----------|------:|
| Sedes relevadas | **399** |
| Marcas identificadas | **389** |
| Marcas multisede verificadas | **10** |
| Marcas individuales | **379** |
| Sedes pertenecientes a marcas multisede | **20** |

## Principios metodológicos

- El relevamiento siempre contabiliza sedes físicas.
- Las sucursales no eliminan registros del relevamiento.
- Una marca puede operar una o múltiples sedes.
- La condición de marca multisede se asigna exclusivamente mediante verificación manual.
- Todas las relaciones entre sedes y marcas son reproducibles mediante `estudios_marcas.csv`.

## Escalas de análisis

**Nivel sede**

- distribución territorial
- presencia digital
- reseñas
- equipamiento
- indicadores individuales

**Nivel marca**

- expansión territorial
- cantidad de sucursales
- posicionamiento comercial
- análisis de cadenas

---

# Próxima etapa

## Motor 5 — Inteligencia del mercado

El siguiente motor incorporará análisis estratégicos sobre:

- densidad competitiva
- cobertura territorial
- concentración de marcas
- oportunidades de expansión
- mapas de saturación

---

# Roadmap

Próximas etapas:

- Motor 5 — Inteligencia del mercado
- Dashboard interactivo
- Automatización de actualizaciones
- Expansión a otras ciudades
- Expansión internacional

---

# Autor

**Leandro Estupiñán**

Proyecto desarrollado para **Transverso – Observatorio Pilates**.