DM-005_indice_oportunidad.md
# Decisión Metodológica DM-005

# Índice de Oportunidad del Observatorio

**Versión:** 1.0

**Estado:** Aprobada

**Fecha:** Agosto 2026

---

## Propósito

El Índice de Oportunidad constituye la metodología oficial del Observatorio Pilates Transverso para estimar el potencial relativo de apertura de un nuevo estudio de Pilates dentro de una ciudad.

El índice busca responder una pregunta concreta:

> **¿En qué barrios conviene abrir hoy un estudio de Pilates?**

No pretende predecir el éxito comercial de un emprendimiento, sino identificar territorios donde el equilibrio entre competencia existente y mercado disponible resulta comparativamente más favorable.

---

# Principios metodológicos

El índice se construye bajo cinco principios.

## 1. La unidad territorial es el barrio

El análisis se realiza sobre barrios oficiales de la ciudad.

En CABA se utilizan los 48 barrios reconocidos oficialmente.

Cada futura ciudad incorporará su propia división territorial oficial.

---

## 2. La oportunidad es relativa

Un barrio no es "bueno" o "malo".

Su oportunidad depende de la relación entre:

- oferta instalada,
- población,
- fortaleza competitiva,
- concentración de marcas.

---

## 3. La competencia pesa más que la oferta absoluta

El Observatorio prioriza la presión competitiva relativa.

La variable principal del índice es:

<math value="\\frac{\\text{Estudios}}{10000\\text{ habitantes}}" block/>

Esta decisión deriva directamente de la DM-002.

---

## 4. La oportunidad combina múltiples dimensiones

El índice no depende de una única variable.

Cada dimensión representa un aspecto distinto del mercado.

---

## 5. La metodología es reproducible

Todas las variables provienen de datasets versionados dentro del proyecto.

No existen cálculos manuales.

Cada ejecución produce resultados reproducibles.

---

# Variables (Versión 1)

| Variable | Fuente | Peso |
|----------|---------|------:|
| Saturación invertida | Motor 5.3 | 50% |
| Población | Catálogo Territorial CABA v1 | 20% |
| Fortaleza digital | `estudios_features.csv` | 15% |
| Concentración de marcas | SQLite | 15% |

**Total:** 100%.

---

# Definición de variables

## Saturación invertida

Se calcula como:

<math value="1-S" block/>

donde:

- <math value="S"/> representa el Índice de Saturación del barrio.

Cuanto menor sea la saturación, mayor será la oportunidad.

---

## Población

La población corresponde al Censo Nacional.

En CABA se utiliza el Censo 2010 como referencia oficial.

La población se normaliza para permitir comparaciones entre barrios.

---

## Fortaleza digital

Representa la intensidad competitiva online.

Se construye mediante la agregación de seguidores de Instagram de los estudios del barrio.

Una fortaleza digital muy elevada reduce la oportunidad relativa.

---

## Concentración de marcas

Evalúa cuánto del mercado local pertenece a marcas con múltiples sedes.

Mercados muy concentrados suelen presentar mayores barreras de entrada.

---

# Fórmula

La puntuación se calcula como:

<math value="O=0.50(1-S)+0.20P+0.15(1-F)+0.15(1-C)" block/>

donde:

- <math value="O"/> = oportunidad.
- <math value="S"/> = saturación.
- <math value="P"/> = población normalizada.
- <math value="F"/> = fortaleza digital normalizada.
- <math value="C"/> = concentración de marcas normalizada.

El resultado final se expresa sobre una escala de **0 a 100 puntos**.

---

# Clasificación

| Puntaje | Categoría |
|---------:|-----------|
| 75–100 | 🟢 Alta oportunidad |
| 50–74 | 🟡 Oportunidad media |
| 25–49 | 🟠 Mercado maduro |
| 0–24 | 🔴 Alta competencia |

---

# Interpretación

El índice debe interpretarse como una herramienta comparativa.

### Alta oportunidad

- baja saturación,
- población significativa,
- competencia digital moderada.

Interpretación:

> Existe espacio relativo para la entrada de un nuevo emprendimiento.

### Alta competencia

- elevada saturación,
- fuerte presencia digital,
- alta concentración empresarial.

Interpretación:

> El ingreso requerirá una propuesta claramente diferenciada.

---

# Alcances

El índice resulta especialmente útil para:

- emprendedores,
- marcas en expansión,
- consultoras,
- inversores,
- análisis territoriales.

---

# Limitaciones

La versión 1 todavía no incorpora:

- ingresos por barrio,
- alquileres comerciales,
- crecimiento inmobiliario,
- población flotante,
- movilidad,
- variables etarias.

Estas dimensiones podrán incorporarse en futuras versiones sin modificar la estructura metodológica.

---

# Relación con otras decisiones metodológicas

| DM | Relación |
|----|----------|
| DM-001 | Sede ≠ Marca |
| DM-002 | Índice de Saturación |
| DM-003 | Catálogo Territorial |
| DM-004 | Normalización Territorial |
| **DM-005** | Índice de Oportunidad |

---

# Resultado esperado

El Motor 5.4 generará como producto principal:

`data/intelligence/oportunidad_barrios.csv`

Cada barrio contará con:

- puntuación de oportunidad,
- categoría,
- variables utilizadas,
- explicación resumida del resultado.

Este documento establece la metodología oficial del Observatorio para evaluar oportunidades territoriales de apertura de estudios de Pilates.