# Roadmap — Observatorio Pilates Transverso

**Versión 1.1**

Este roadmap documenta la evolución técnica y estratégica del Observatorio Pilates Transverso.

---

# Estado del proyecto

| Componente | Estado |
|------------|--------|
| ✅ Cleaning | Completado |
| ✅ Features | Completado |
| ✅ Analysis | Completado |
| ✅ SQLite | Completado |
| 🚧 Inteligencia de mercado | En desarrollo |
| ⏳ Dashboard | Pendiente |
| ⏳ Carga manual (interfaz) | Pendiente |

---

# Motores del Observatorio

## Motor 1 — Limpieza (Completado)

Objetivo: normalizar y consolidar el dataset bruto.

- [x] Normalización de columnas
- [x] Limpieza de barrios
- [x] Normalización de fabricantes
- [x] Limpieza de teléfonos
- [x] Limpieza de emails
- [x] Normalización de Instagram
- [x] Normalización de sitios web
- [x] Validación de campos

**Salida principal**

```
data/interim/estudios_limpios.csv
```

---

## Motor 2 — Ingeniería de variables (Completado)

Objetivo: generar variables reutilizables para análisis posteriores.

### Geografía

- [x] Barrio
- [x] Comuna
- [x] Zona

### Presencia digital

- [x] Presencia digital

### Contactabilidad

- [x] Canales de contacto

### Equipamiento

- [x] Fabricantes
- [x] Fabricante múltiple

**Salida principal**

```
data/processed/estudios_features.csv
```

---

## Motor 3 — Análisis (Completado)

Objetivo: transformar las variables en indicadores del mercado.

Incluye:

- [x] Distribución territorial
- [x] Indicadores generales
- [x] Rankings
- [x] Cruces analíticos
- [x] Exportación automática de resultados

**Salida principal**

```
data/analysis/
```

---

## Motor 4 — Modelo de datos (Completado)

Objetivo: construir una base relacional reproducible del Observatorio.

### SQLite

- [x] Base SQLite reproducible
- [x] Integridad referencial
- [x] Validaciones automáticas

### Relación sede–marca

- [x] Relaciones estudio–marca
- [x] Reconstrucción automática (`rebuild_estudios_marcas.py`)
- [x] Sincronización automática SQLite (`load_database.py`)

### Gobernanza de datos

- [x] Decisión Metodológica DM-001 (Sede ≠ Marca)
- [x] Base Maestra de Marcas (v1)
- [x] Carga Manual / Curación del Observatorio
- [ ] Interfaz de carga manual

**Salidas principales**

```
data/database/observatorio_pilates.db
data/processed/estudios_marcas.csv
```

---

## Motor 5 — Inteligencia del mercado (En desarrollo)

Objetivo: convertir los datos del Observatorio en inteligencia estratégica.

### Estado actual

- [x] 5.1 Resumen Ejecutivo
- [x] 5.2 Densidad Territorial

### Próximos bloques

- [ ] 5.3 Índice de Saturación
- [ ] 5.4 Índice de Oportunidad
- [ ] 5.5 Poder de Marca
- [ ] 5.6 Concentración del Mercado
- [ ] 5.7 Vacíos Estratégicos
- [ ] 5.8 Informe Narrativo

**Salida principal**

```
data/intelligence/
```

---

# Roadmap del producto

## Versión 2.0

Expansión del Observatorio.

- [ ] Nuevas ciudades
- [ ] API del Observatorio
- [ ] Aplicación web
- [ ] Panel de administración

---

## Versión 3.0

Escalabilidad e inteligencia avanzada.

- [ ] Dashboard interactivo avanzado
- [ ] Aplicación móvil
- [ ] IA para detección de marcas y sedes
- [ ] Reportes automáticos
- [ ] Observatorio internacional

---

# Principios metodológicos

El crecimiento del proyecto debe mantener siempre la reproducibilidad del pipeline.

```text
Cleaning
   ↓
Features
   ↓
Curación manual
   ↓
Reconstrucción sede–marca
   ↓
SQLite
   ↓
Inteligencia de mercado
   ↓
Dashboard
```

## Decisiones metodológicas vigentes

- **DM-001:** Sede ≠ Marca.
- El relevamiento contabiliza siempre **sedes físicas**.
- Las **marcas** representan entidades comerciales que pueden operar una o múltiples sedes.
- Los catálogos curados (`marcas_maestra.csv` y `estudios_marcas_verificado.csv`) constituyen la fuente de verdad para las relaciones sede–marca.
- SQLite es una representación reproducible del estado procesado del Observatorio y nunca una fuente primaria de datos.