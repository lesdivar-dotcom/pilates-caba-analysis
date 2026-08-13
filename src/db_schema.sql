PRAGMA foreign_keys = ON;

-- ============================================================
-- MOTOR 4 — OBSERVATORIO PILATES TRANSVERSO
-- Esquema SQLite
-- ============================================================

-- ------------------------------------------------------------
-- FUENTES
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS fuentes (
    id_fuente INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_fuente TEXT NOT NULL,
    tipo_fuente TEXT,
    url TEXT,
    fecha_recoleccion TEXT,
    observaciones TEXT
);


-- ------------------------------------------------------------
-- ESTUDIOS
-- Entidad principal del Observatorio
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS estudios (
    id_estudio TEXT PRIMARY KEY,
    nombre_del_estudio TEXT NOT NULL,
    nombre_normalizado TEXT,
    direccion TEXT,
    barrio TEXT,
    comuna REAL,
    zona TEXT,
    telefono TEXT,
    email TEXT,
    web TEXT,
    instagram TEXT,
    app TEXT,

    tiene_instagram INTEGER NOT NULL DEFAULT 0,
    tiene_web INTEGER NOT NULL DEFAULT 0,
    tiene_email INTEGER NOT NULL DEFAULT 0,
    tiene_app INTEGER NOT NULL DEFAULT 0,
    tiene_telefono INTEGER NOT NULL DEFAULT 0,

    fecha_alta TEXT DEFAULT CURRENT_TIMESTAMP
);


-- ------------------------------------------------------------
-- RELEVAMIENTOS
-- Histórico de observaciones de cada estudio
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS relevamientos (
    id_relevamiento INTEGER PRIMARY KEY AUTOINCREMENT,

    id_estudio TEXT NOT NULL,
    id_fuente INTEGER,

    fecha_recoleccion TEXT,

    nombre_del_estudio TEXT,
    direccion TEXT,
    barrio TEXT,
    comuna REAL,
    zona TEXT,

    telefono TEXT,
    email TEXT,
    web TEXT,
    instagram TEXT,
    app TEXT,

    puntaje_google REAL,
    cantidad_resenas REAL,
    seguidores_instagram REAL,

    observaciones TEXT,

    fecha_carga TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (id_estudio)
        REFERENCES estudios(id_estudio),

    FOREIGN KEY (id_fuente)
        REFERENCES fuentes(id_fuente)
);


-- ------------------------------------------------------------
-- FEATURES DERIVADAS
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS estudio_features (
    id_feature INTEGER PRIMARY KEY AUTOINCREMENT,

    id_estudio TEXT NOT NULL,

    fecha_calculo TEXT DEFAULT CURRENT_TIMESTAMP,

    presencia_digital INTEGER,
    n_canales_contacto INTEGER,

    n_fabricantes INTEGER,
    fabricante_multiple INTEGER,

    FOREIGN KEY (id_estudio)
        REFERENCES estudios(id_estudio)
);


-- ------------------------------------------------------------
-- MARCAS / FABRICANTES
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS marcas (
    id_marca TEXT PRIMARY KEY,
    nombre_marca TEXT NOT NULL,
    observaciones TEXT
);


-- ------------------------------------------------------------
-- RELACIÓN ESTUDIO ↔ MARCA
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS estudios_marcas (
    id_estudio TEXT NOT NULL,
    id_marca TEXT NOT NULL,

    PRIMARY KEY (id_estudio, id_marca),

    FOREIGN KEY (id_estudio)
        REFERENCES estudios(id_estudio),

    FOREIGN KEY (id_marca)
        REFERENCES marcas(id_marca)
);


-- ------------------------------------------------------------
-- ÍNDICES
-- ------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_estudios_barrio
    ON estudios(barrio);

CREATE INDEX IF NOT EXISTS idx_estudios_comuna
    ON estudios(comuna);

CREATE INDEX IF NOT EXISTS idx_estudios_zona
    ON estudios(zona);

CREATE INDEX IF NOT EXISTS idx_relevamientos_estudio
    ON relevamientos(id_estudio);

CREATE INDEX IF NOT EXISTS idx_relevamientos_fecha
    ON relevamientos(fecha_recoleccion);

CREATE INDEX IF NOT EXISTS idx_features_estudio
    ON estudio_features(id_estudio);

CREATE INDEX IF NOT EXISTS idx_estudios_marcas_estudio
    ON estudios_marcas(id_estudio);

CREATE INDEX IF NOT EXISTS idx_estudios_marcas_marca
    ON estudios_marcas(id_marca);