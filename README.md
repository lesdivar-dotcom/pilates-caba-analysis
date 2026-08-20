# Observatorio Pilates Transverso

**Versión 2.0 — Motor 11**

Proyecto de análisis de datos desarrollado en Python para construir el primer **Observatorio Pilates Transverso**, una plataforma de inteligencia territorial diseñada para medir, comparar y seguir en tiempo real la evolución del mercado de estudios de Pilates.

El proyecto nació con la Ciudad Autónoma de Buenos Aires (CABA) y evolucionó hacia una arquitectura multipaís y multiterritorial que permite aplicar una metodología única, reproducible y comparable entre distintos mercados.

Su objetivo no es únicamente registrar estudios, sino **medir el progreso del mercado** mediante indicadores territoriales, digitales, tecnológicos y empresariales, permitiendo comparar la evolución entre ciudades, provincias y países.

Actualmente el desarrollo operativo se concentra en **Argentina**, mientras que el repositorio ya incorpora la estructura territorial para España, Uruguay y Puerto Rico, con ciudades ya mapeadas para su futura activación.

---

# Objetivos

El Observatorio busca responder preguntas como:

- ¿Dónde se concentran los estudios de Pilates?
- ¿Qué territorios presentan mayor o menor desarrollo del mercado?
- ¿Cómo evoluciona la presencia digital del sector?
- ¿Qué fabricantes de equipamiento predominan?
- ¿Qué características presenta el mercado?
- ¿Qué marcas poseen múltiples sedes?
- ¿Dónde existen oportunidades de expansión territorial?

---

# Tecnologías

- Python
- Pandas
- SQLite
- Folium
- Matplotlib
- Git y GitHub

---

# Arquitectura del proyecto

La arquitectura actual distingue tres niveles de conocimiento:

- **Institucional:** catálogos compartidos por todo el Observatorio.
- **País:** organización nacional.
- **Territorio:** activos específicos de cada ciudad o provincia.

```text
pilates-caba-analysis/

├── data/
│
├── reference/                      ← Catálogos institucionales
│   ├── fabricantes.csv
│   ├── fabricantes_alias.csv
│   ├── equipamiento.csv
│   ├── address_dictionary.json
│   └── countries.json
│
└── countries/
    ├── argentina/
    │   ├── caba/
    │   │   ├── database/
    │   │   ├── dashboard/
    │   │   ├── drafts/
    │   │   ├── processed/
    │   │   ├── reports/
    │   │   └── reference/
    │   │       ├── barrios.geojson
    │   │       ├── territory_profile.json
    │   │       └── schema_map.json
    │   │
    │   └── buenos_aires_provincia/
    │       ├── database/
    │       ├── dashboard/
    │       ├── drafts/
    │       ├── processed/
    │       ├── reports/
    │       └── reference/
    │           ├── municipios.geojson
    │           ├── territory_profile.json
    │           ├── schema_map.json
    │           └── localidad_municipio.csv
    │
    ├── espana/
    │   ├── madrid/
    │   └── valencia/
    │
    ├── uruguay/
    │   └── montevideo/
    │
    └── puerto_rico/
        └── san_juan/

├── notebooks/
├── reports/
├── docs/
├── src/
│   ├── cleaning.py
│   ├── features.py
│   ├── analysis.py
│   ├── build_database_city_v2.py
│   ├── load_database.py
│   ├── rebuild_estudios_marcas.py
│   ├── city_config.py
│   ├── geo_adapter.py
│   ├── map_builder.py
│   ├── dashboard_builder.py
│   ├── dashboard_builder_v3.py
│   ├── pilot_metrics.py
│   └── feature_engine.py
│
├── README.md
├── roadmap.md
├── diccionario_datos.md
├── requirements.txt
└── .gitignore
```

## Principio arquitectónico

Los catálogos compartidos viven en `data/reference`, mientras que cada territorio mantiene su propia cartografía, base SQLite, dashboards y reportes.

Esta separación permite incorporar nuevos territorios sin modificar el resto del sistema.

---

# Estado del proyecto

## Motor 1 — Limpieza de datos (completado)

Normalización de:

- columnas
- seguidores
- puntajes
- teléfonos
- emails
- territorios (barrios y localidades)
- fabricantes
- sitios web
- Instagram
- aplicaciones de reservas

Salida:

```text
data/.../interim/estudios_limpios.csv
```

---

## Motor 2 — Ingeniería de variables (completado)

Generación de variables analíticas.

### Geografía

- territorio
- comuna (CABA)
- zona

### Presencia digital

- presencia_digital

### Contactabilidad

- n_canales_contacto

### Equipamiento

- n_fabricantes
- fabricante_multiple

Salida:

```text
data/.../processed/estudios_features.csv
```

---

## Motor 3 — Análisis (completado)

Implementación del motor analítico del Observatorio.

Incluye:

- análisis territorial
- indicadores digitales
- equipamiento
- rankings
- cruces analíticos
- indicadores compuestos
- exportación automática de resultados

Salida principal:

```text
data/.../analysis/
```

---

## Motor 4 — SQLite (completado)

Implementación del modelo relacional del Observatorio.

Incluye:

- base SQLite reproducible
- carga automática
- validaciones
- integridad referencial
- reconstrucción automática de la relación sede–marca

Salida principal:

```text
data/.../database/observatorio_pilates.db
```

---

## Motor 4.3 — Carga Manual / Curación (completado)

El Observatorio incorpora una capa de curación manual para registrar conocimiento verificado sin modificar directamente la base SQLite.

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
build_database_city_v2.py
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
- `schema_map.json`
- `territory_profile.json`

Esto garantiza trazabilidad y reproducibilidad del Observatorio.

---

## Motor 5 — Inteligencia del mercado (consolidado en CABA)

El quinto motor transformó el relevamiento en inteligencia estratégica mediante:

- densidad competitiva
- cobertura territorial
- concentración de marcas
- oportunidades de expansión
- mapas de saturación
- radar de expansión

---

## Motor 10 — Arquitectura Territorial (completado)

El Observatorio incorpora una arquitectura territorial universal que permite observar distintos mercados sin modificar la lógica del sistema.

### Componentes institucionales

- `city_config.py`
- `GeoAdapter`
- `schema_map.json`
- `territory_profile.json`

Cada territorio define:

- unidad territorial
- cartografía
- cobertura
- configuración de procesamiento

### Estado actual

| Territorio | Unidad |
|------------|---------|
| CABA | Barrio |
| Buenos Aires Provincia | Municipio |

---

## Motor 10.3 — Cartografía Territorial (en consolidación)

Implementación del sistema cartográfico universal mediante Folium.

### Capacidades

- coropletas territoriales
- escala cromática institucional Transverso
- adaptación automática entre barrios y municipios
- integración con `GeoAdapter`

### Estado actual

| Territorio | Estado |
|------------|--------|
| CABA | Coropleta operativa |
| Buenos Aires Provincia | Piloto La Plata operativo |

---

## Motor 11 — Dashboard Universal (en consolidación)

El Dashboard conserva la identidad visual original del Observatorio mientras incorpora la nueva arquitectura territorial.

### Capacidades

- Hero institucional.
- KPIs universales.
- Paneles editoriales.
- Mapas territoriales.
- Cobertura piloto automática.
- Integración con `GeoAdapter`.
- Compatibilidad entre barrios y municipios.

### Referencias

| Archivo | Rol |
|---------|-----|
| `dashboard_builder.py` | Referencia visual estable. |
| `dashboard_builder_v3.py` | Evolución multiterritorial. |

---

# Cobertura territorial del Observatorio

## Territorios operativos

| Territorio | Estado |
|------------|---------|
| Ciudad Autónoma de Buenos Aires | Operativo |
| Provincia de Buenos Aires | Operativo (piloto La Plata) |

## Territorios incorporados

El repositorio ya dispone de estructura territorial preparada para futuras activaciones.

| País | Territorios incorporados |
|------|--------------------------|
| Argentina | CABA · Buenos Aires Provincia |
| España | Madrid · Valencia |
| Uruguay | Montevideo |
| Puerto Rico | San Juan |

La incorporación al repositorio no implica necesariamente que el pipeline completo (Cleaning → Features → SQLite → Dashboard → Cartografía) se encuentre activado en todos esos territorios.

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
| Sedes CABA | **402** |
| Barrios activos | **40** |
| Marcas verificadas (histórico CABA) | **389** |
| Marcas multisede | **10** |
| Municipios Provincia | **143** |
| Cobertura piloto | **La Plata** |

## Principios metodológicos

- El relevamiento siempre contabiliza sedes físicas.
- Las sucursales no eliminan registros.
- Una marca puede operar una o múltiples sedes.
- La condición de marca multisede se asigna exclusivamente mediante verificación manual.
- Todas las relaciones entre sedes y marcas son reproducibles mediante `estudios_marcas.csv`.

## Escalas de análisis

### Nivel sede

- distribución territorial
- presencia digital
- reseñas
- equipamiento
- indicadores individuales

### Nivel marca

- expansión territorial
- cantidad de sucursales
- posicionamiento comercial
- análisis de cadenas

---

# Decisión Metodológica DM-002 — Territorialidad Universal

Todo territorio que ingresa al Observatorio debe recorrer exactamente el mismo pipeline institucional.

```text
Raw
 ↓
Cleaning
 ↓
Features
 ↓
Curación
 ↓
SQLite canónica
 ↓
GeoAdapter
 ↓
Dashboard
```

Esto garantiza que futuros territorios (Mar del Plata, Bahía Blanca y los demás territorios ya estructurados) ingresen sin modificar el resto del sistema.

---

# Próxima etapa

## Motor 11.1 — Feature Engine Territorial Universal

El siguiente motor incorporará:

- generación universal de features;
- métricas compartidas entre territorios;
- alimentación automática de dashboards y cartografía;
- consolidación del Observatorio multiterritorial.

---

# Roadmap


## Motor 11.4 — Refinamiento Visual Institucional

Checkpoint visual vigente del Dashboard Único.

- Dashboard universal multiterritorial.
- Identidad visual Transverso.
- Buscador y editor integrados.
- Separación entre unidad operativa y unidad institucional.
- Sin alteración de los datasets consolidados.

## Motor 11.5 — Cartografía Territorial Universal

Implementación del motor cartográfico universal del Observatorio.

### Capacidades

- Lectura de `territory_profile.json`.
- Uso explícito del GeoJSON institucional.
- Compatibilidad entre unidad operativa y unidad cartográfica.
- Bridges territoriales explícitos.
- Agregación cartográfica derivada sin modificar datos fuente.
- Encuadre automático mediante `fit_bounds`.
- Territorios sin cobertura diferenciados de territorios observados.

### Provincia de Buenos Aires — BA Norte

Checkpoint validado:

| Indicador | Valor |
|---|---:|
| Estudios preservados | 51 |
| Localidades operativas | 5 |
| Municipios cartográficos | 4 |
| Municipios enlazados con GeoJSON | 4/4 |
| Features del GeoJSON provincial | 143 |

Bridge territorial:

`reference/localidad_municipio.csv`

Relaciones vigentes:

- Olivos → Vicente López
- Vicente López → Vicente López
- San Isidro → San Isidro
- San Fernando → San Fernando
- Tigre → Tigre

## Motor 11.5.1 — Escala Cromática Territorial Continua

Refinamiento exclusivamente visual de Motor 11.5.

La cartografía utiliza una escala continua basada en la paleta
institucional Transverso:

borgoña → terracota → arena → verde

El gris queda reservado exclusivamente para territorios sin
cobertura observada.

No modifica datasets, bridges, agregaciones ni contratos
territoriales.

## Próxima etapa

### Motor 11.6 — Navegación Multiterritorial

Previsto:

- selector universal de territorio;
- navegación directa entre CABA y Provincia;
- navegación entre lotes activos;
- identificación del estado de cobertura;
- futura vista Atlas Transverso.

La incorporación estructural de un territorio no implica que su
pipeline se encuentre operativo.
---

# Autor

**Leandro Estupiñán**

Proyecto desarrollado para **Transverso – Observatorio Pilates**.