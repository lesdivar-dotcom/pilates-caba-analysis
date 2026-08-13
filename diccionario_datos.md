# Decisión Metodológica DM-001 — Sede ≠ Marca

El Observatorio Pilates Transverso trabaja con dos entidades distintas.

## Definiciones

### Sede

Establecimiento físico donde se dictan clases de Pilates.

- Unidad primaria del relevamiento.
- Posee un `id_estudio`.
- Cada sede constituye un registro independiente.

### Marca

Identidad comercial que puede operar una o múltiples sedes.

- Posee un `id_marca`.
- Puede agrupar una o varias sedes.
- La condición de marca multisede solo se asigna mediante verificación manual.

## Estado actual

| Indicador | Valor |
|-----------|------:|
| Sedes | **399** |
| Marcas | **389** |
| Marcas multisede | **10** |
| Marcas individuales | **379** |

## Relación entre entidades

```text
Marca
 ├── Sede 1
 ├── Sede 2
 └── Sede 3
```

La relación entre ambas entidades queda registrada en:

```
data/processed/estudios_marcas.csv
```

y constituye la fuente utilizada por SQLite para mantener la integridad del modelo relacional.

## Catálogos Curados del Observatorio

El Observatorio distingue entre datos generados automáticamente y conocimiento verificado manualmente.

### `marcas_maestra.csv`

Catálogo oficial de marcas.

Campos:

- `id_marca`
- `nombre_marca`
- `marca_multisede`
- `sedes_verificadas`
- `estado_verificacion`
- `observaciones`

### `estudios_marcas_verificado.csv`

Registra únicamente relaciones verificadas manualmente entre una sede (`id_estudio`) y una marca (`id_marca`).

### `estudios_marcas.csv`

Archivo reconstruido automáticamente a partir de:

- `estudios_features.csv`
- `marcas_maestra.csv`
- `estudios_marcas_verificado.csv`

Este archivo nunca debe editarse manualmente.