from pathlib import Path

import dash
import pandas as pd
import skops.io as sio
import plotly.express as px
from dash import dcc, html, Input, Output, State
from dash.exceptions import PreventUpdate

ROOT = Path(__file__).resolve().parents[1]

app = dash.Dash(
    __name__,
    title="AgroPredict Colombia",
    suppress_callback_exceptions=True,
)

# Datos históricos del proyecto
df = pd.read_parquet(ROOT / "data/processed/features_secuencial.parquet")


def crear_figura_historica(departamento=None, municipio=None, sistema=None, anio=None):
    datos = df.copy()

    if departamento:
        datos = datos[datos["departamento"] == departamento]
    if municipio:
        datos = datos[datos["cod_municipio"] == municipio]
    if sistema:
        datos = datos[datos["sistema_productivo"] == sistema]
    if anio is not None and anio != "todos":
        datos = datos[datos["anio"] == int(anio)]

    historico = (
        datos.groupby(
            ["anio", "semestre_b", "sistema_productivo"],
            as_index=False,
        )
        .agg(
            produccion_total=("produccion", "sum"),
            area_total=("area_cosechada", "sum"),
        )
    )

    historico = historico[historico["area_total"] > 0].copy()

    historico["rendimiento_ponderado"] = (
        historico["produccion_total"] / historico["area_total"]
    )

    historico["periodo"] = (
        historico["anio"].astype(str)
        + "-"
        + historico["semestre_b"].map({0: "A", 1: "B"})
    )

    historico["sistema"] = historico["sistema_productivo"].map({
        "tradicional": "Tradicional",
        "tecnificado": "Tecnificado",
    }).fillna(historico["sistema_productivo"])

    figura = px.line(
        historico,
        x="periodo",
        y="rendimiento_ponderado",
        color="sistema",
        markers=True,
        title="Evolución del rendimiento medio por sistema productivo",
        labels={
            "periodo": "Periodo agrícola",
            "rendimiento_ponderado": "Rendimiento (t/ha)",
            "sistema": "Sistema productivo",
        },
        color_discrete_map={
            "Tecnificado": "#286A3B",
            "Tradicional": "#D58A25",
        },
    )

    figura.update_layout(
        template="plotly_white",
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        font=dict(color="#27352B"),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.25,
            xanchor="left",
            x=0,
        ),
        margin=dict(l=45, r=20, t=65, b=85),
        hovermode="x unified",
    )

    figura.update_traces(
        line=dict(width=2.5),
        hovertemplate=(
            "<b>%{fullData.name}</b>"
            "<extra></extra>"
            "<br>Rendimiento: %{y:.2f} t/ha"
        ),
    )

    return figura



def calcular_promedios_historicos(departamento, municipio, sistema, anio, semestre):
    """Calcula referencias históricas anteriores al período consultado."""

    periodo_objetivo = int(anio) * 2 + int(semestre)

    datos = df.loc[
        (df["sistema_productivo"] == sistema)
        & ((df["anio"] * 2 + df["semestre_b"]) < periodo_objetivo)
    ].copy()

    def rendimiento_ponderado(subconjunto):
        datos_validos = subconjunto.loc[
            subconjunto["area_cosechada"].notna()
            & subconjunto["produccion"].notna()
            & (subconjunto["area_cosechada"] > 0)
        ]

        if datos_validos.empty:
            return None

        area = datos_validos["area_cosechada"].sum()

        if area <= 0:
            return None

        return float(datos_validos["produccion"].sum() / area)

    municipal = datos.loc[
        (datos["departamento"] == departamento)
        & (datos["cod_municipio"] == municipio)
    ]

    departamental = datos.loc[
        datos["departamento"] == departamento
    ]

    return {
        "municipal": rendimiento_ponderado(municipal),
        "departamental": rendimiento_ponderado(departamental),
        "nacional": rendimiento_ponderado(datos),
    }


# Modelo optimizado y validado con datos de 2025
RUTA_MODELO = ROOT / "models/xgboost_maiz_optimizado.skops"

TIPOS_PERMITIDOS = [
    "xgboost.core.Booster",
    "xgboost.sklearn.XGBRegressor",
]

modelo_predictivo = sio.load(
    RUTA_MODELO,
    trusted=TIPOS_PERMITIDOS,
)

VARIABLES_MODELO = [
    "anio",
    "semestre_b",
    "rendimiento_rezago",
    "departamento",
    "sistema_productivo",
]


ESTILO_PESTANA = {
    "padding": "14px 18px",
    "backgroundColor": "#1D3B2A",
    "color": "#FFFFFF",
    "border": "none",
    "fontWeight": "500",
    "fontSize": "13px",
}

ESTILO_PESTANA_ACTIVA = {
    **ESTILO_PESTANA,
    "backgroundColor": "#FFFFFF",
    "color": "#1D3B2A",
    "borderRadius": "5px",
    "fontWeight": "700",
}

app.layout = html.Div(
    [
        html.Header(
            html.Div(
                [
                    html.Div(
                        html.Img(
                            src=app.get_asset_url(
                                "logo_agro_predict_colombia.png"
                            ),
                            alt="Logo Agro-Predict Colombia",
                            style={
                                "width": "260px",
                                "maxWidth": "100%",
                                "height": "auto",
                                "display": "block",
                            },
                        ),
                        style={
                            "backgroundColor": "#FFFFFF",
                            "borderRadius": "8px",
                            "padding": "6px 12px",
                            "flexShrink": "0",
                        },
                    ),
                    dcc.Tabs(
                        id="pestanas",
                        value="historico",
                        children=[
                            dcc.Tab(
                                label="Consulta histórica",
                                value="historico",
                                style=ESTILO_PESTANA,
                                selected_style=ESTILO_PESTANA_ACTIVA,
                            ),
                            dcc.Tab(
                                label="Predicción",
                                value="prediccion",
                                style=ESTILO_PESTANA,
                                selected_style=ESTILO_PESTANA_ACTIVA,
                            ),
                            dcc.Tab(
                                label="Resultados",
                                value="resultados",
                                style=ESTILO_PESTANA,
                                selected_style=ESTILO_PESTANA_ACTIVA,
                            ),
                            dcc.Tab(
                                label="Acerca del modelo",
                                value="modelo",
                                style=ESTILO_PESTANA,
                                selected_style=ESTILO_PESTANA_ACTIVA,
                            ),
                        ],
                        colors={
                            "border": "#1D3B2A",
                            "primary": "#FFFFFF",
                            "background": "#1D3B2A",
                        },
                        style={"flex": "1", "maxWidth": "530px"},
                    ),
                ],
                style={
                    "maxWidth": "1250px",
                    "margin": "0 auto",
                    "padding": "12px 24px",
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "space-between",
                    "gap": "24px",
                },
            ),
            style={"backgroundColor": "#1D3B2A"},
        ),

        dcc.Store(id="ultima-prediccion", storage_type="memory"),

        html.Main(
            html.Div(
                id="contenido-pestana",
                style={"padding": "24px 0"},
            ),
            style={
                "maxWidth": "1250px",
                "margin": "0 auto",
                "padding": "0 24px",
            },
        ),
    ],
    style={
        "fontFamily": "Arial, sans-serif",
        "backgroundColor": "#F7F6F2",
        "minHeight": "100vh",
        "color": "#1F2922",
    },
)

@app.callback(
    Output("contenido-pestana", "children"),
    Input("pestanas", "value"),
)
def mostrar_contenido(pestana):
    contenidos = {
        "historico": (
            "Consulta histórica",
            html.P(
                "Rendimiento del cultivo de maíz según las Evaluaciones "
                "Agropecuarias Municipales (EVA), 2019–2025.",
                style={"color": "#68736C", "marginTop": "0"},
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Label("Departamento"),
                            dcc.Dropdown(
                                id="filtro-departamento",
                                options=[
                                    {"label": d, "value": d}
                                    for d in sorted(df["departamento"].unique())
                                ],
                                placeholder="Todos",
                                clearable=True,
                            ),
                        ],
                        style={"flex": "1", "minWidth": "180px"},
                    ),
                    html.Div(
                        [
                            html.Label("Municipio"),
                            dcc.Dropdown(
                                id="filtro-municipio",
                                placeholder="Todos",
                                clearable=True,
                            ),
                        ],
                        style={"flex": "1", "minWidth": "180px"},
                    ),
                    html.Div(
                        [
                            html.Label("Sistema productivo"),
                            dcc.Dropdown(
                                id="filtro-sistema",
                                options=[
                                    {"label": "Tradicional", "value": "tradicional"},
                                    {"label": "Tecnificado", "value": "tecnificado"},
                                ],
                                placeholder="Todos",
                                clearable=True,
                            ),
                        ],
                        style={"flex": "1", "minWidth": "180px"},
                    ),
                    html.Div(
                        [
                            html.Label("Años"),
                            dcc.Dropdown(
                                id="filtro-anios",
                                options=[
                                    {"label": "2019–2025", "value": "todos"},
                                    *[
                                        {"label": str(a), "value": a}
                                        for a in sorted(df["anio"].unique())
                                    ],
                                ],
                                value="todos",
                                clearable=False,
                            ),
                        ],
                        style={"flex": "1", "minWidth": "180px"},
                    ),
                ],
                style={
                    "display": "flex",
                    "gap": "14px",
                    "flexWrap": "wrap",
                    "backgroundColor": "#FFFFFF",
                    "border": "1px solid #E0E4DE",
                    "borderRadius": "7px",
                    "padding": "18px",
                    "marginBottom": "16px",
                },
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(titulo, style={
                                "fontSize": "12px",
                                "color": "#657168",
                            }),
                            html.Div(
                                "—",
                                id=identificador,
                                style={
                                    "fontSize": "25px",
                                    "fontWeight": "700",
                                    "marginTop": "10px",
                                },
                            ),
                        ],
                        style={
                            "flex": "1",
                            "minWidth": "170px",
                            "padding": "18px",
                            "backgroundColor": "#FFFFFF",
                            "border": "1px solid #E0E4DE",
                            "borderRadius": "7px",
                        },
                    )
                    for titulo, identificador in [
                        ("Registros", "kpi-registros"),
                        ("Municipios", "kpi-municipios"),
                        ("Rendimiento medio", "kpi-media"),
                        ("Rendimiento mediano", "kpi-mediana"),
                    ]
                ],
                style={
                    "display": "flex",
                    "gap": "14px",
                    "flexWrap": "wrap",
                    "marginBottom": "16px",
                },
            ),
            html.Div(
                dcc.Graph(id="grafico-historico"),
                style={
                    "backgroundColor": "#FFFFFF",
                    "border": "1px solid #E0E4DE",
                    "borderRadius": "7px",
                    "padding": "12px",
                },
            ),
            html.Div(
                [
                    html.H3(
                        "Ranking de territorios por rendimiento medio",
                        style={"fontSize": "16px", "marginTop": "0"},
                    ),
                    html.Div(id="ranking-territorios"),
                ],
                style={
                    "backgroundColor": "#FFFFFF",
                    "border": "1px solid #E0E4DE",
                    "borderRadius": "7px",
                    "padding": "20px",
                    "marginTop": "16px",
                },
            ),
        ),
        "prediccion": (
            "Generar predicción",
            html.Div([
                html.H3(
                    "Configuración de la predicción",
                    style={
                        "marginTop": "0",
                        "marginBottom": "8px",
                        "color": "#193B2A",
                    },
                ),
                html.P(
                    "Seleccione el territorio, sistema productivo y "
                    "período para estimar el rendimiento municipal del maíz.",
                    style={
                        "color": "#64748B",
                        "fontSize": "14px",
                        "marginBottom": "24px",
                    },
                ),
                html.Div([
                    html.Label(
                        "Modalidad de predicción",
                        style={
                            "display": "block",
                            "fontWeight": "600",
                            "marginBottom": "10px",
                        },
                    ),
                    dcc.RadioItems(
                        id="pred-modalidad",
                        options=[
                            {
                                "label": " Individual",
                                "value": "individual",
                            },
                            {
                                "label": " Múltiples municipios",
                                "value": "multiple",
                            },
                        ],
                        value="individual",
                        inline=True,
                        inputStyle={"marginRight": "6px"},
                        labelStyle={"marginRight": "24px"},
                    ),
                ], style={"marginBottom": "24px"}),
                html.Div([
                    html.Div([
                        html.Label("Departamento"),
                        dcc.Dropdown(
                            id="pred-departamento",
                            options=[
                                {"label": d, "value": d}
                                for d in sorted(df["departamento"].unique())
                            ],
                            placeholder="Seleccione un departamento",
                        ),
                    ]),
                    html.Div([
                        html.Label("Municipio"),
                        dcc.Dropdown(
                            id="pred-municipio",
                            placeholder="Seleccione un municipio",
                            multi=False,
                        ),
                    ]),
                    html.Div([
                        html.Label("Sistema productivo"),
                        dcc.Dropdown(
                            id="pred-sistema",
                            options=[
                                {"label": "Tradicional", "value": "tradicional"},
                                {"label": "Tecnificado", "value": "tecnificado"},
                            ],
                            placeholder="Seleccione un sistema productivo",
                        ),
                    ]),
                    html.Div([
                        html.Label("Año"),
                        dcc.Dropdown(
                            id="pred-anio",
                            options=[
                                {"label": str(a), "value": int(a)}
                                for a in sorted(df["anio"].unique())
                            ],
                            placeholder="Seleccione un año",
                        ),
                    ]),
                    html.Div([
                        html.Label("Semestre"),
                        dcc.Dropdown(
                            id="pred-semestre",
                            options=[
                                {"label": "A", "value": 0},
                                {"label": "B", "value": 1},
                            ],
                            placeholder="Seleccione un semestre",
                        ),
                    ]),
                ], style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(240px, 1fr))",
                    "gap": "20px",
                    "marginBottom": "24px",
                }),
                html.Button(
                    "Generar predicción",
                    id="btn-predecir",
                    n_clicks=0,
                    style={
                        "backgroundColor": "#286A3B",
                        "color": "white",
                        "border": "none",
                        "borderRadius": "7px",
                        "padding": "12px 24px",
                        "fontWeight": "600",
                        "cursor": "pointer",
                    },
                ),
            ], style={
                "backgroundColor": "#FFFFFF",
                "border": "1px solid #E0E4DE",
                "borderRadius": "10px",
                "padding": "24px",
                "marginBottom": "20px",
            }),
            html.Div(
                id="resultado-prediccion",
                style={"width": "100%"},
            ),
            dcc.Download(id="descarga-predicciones-csv"),
            dcc.Download(id="descarga-predicciones-excel"),
        ),
        "resultados": (
            "Resultados de predicción",
            html.Div(
                id="panel-resultados",
                children=html.P(
                    "Genere primero una predicción para visualizar los resultados."
                ),
            ),
        ),
        "modelo": (
            "Acerca del modelo",

            html.Div([
                html.H3(
                    "XGBoost optimizado",
                    style={"color": "#193B2A", "marginTop": "0"},
                ),
                html.P(
                    "Modelo de aprendizaje supervisado para estimar el "
                    "rendimiento municipal del maíz en Colombia, expresado "
                    "en toneladas por hectárea (t/ha)."
                ),
                html.P(
                    "El prototipo utiliza información agrícola histórica "
                    "y permite realizar estimaciones retrospectivas "
                    "para combinaciones disponibles en el conjunto de datos.",
                    style={"color": "#64748B"},
                ),
            ], style={
                "backgroundColor": "#FFFFFF",
                "border": "1px solid #E0E4DE",
                "borderRadius": "10px",
                "padding": "24px",
                "marginBottom": "20px",
            }),

            html.Div([
                html.H3(
                    "Variables predictoras",
                    style={"color": "#193B2A", "marginTop": "0"},
                ),
                html.Div([
                    html.Div("Año", style={"padding": "12px"}),
                    html.Div("Semestre agrícola", style={"padding": "12px"}),
                    html.Div("Rendimiento del semestre anterior",
                             style={"padding": "12px"}),
                    html.Div("Departamento", style={"padding": "12px"}),
                    html.Div("Sistema productivo",
                             style={"padding": "12px"}),
                ], style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(200px, 1fr))",
                    "gap": "10px",
                    "backgroundColor": "#F7FAF7",
                    "borderRadius": "8px",
                }),
            ], style={
                "backgroundColor": "#FFFFFF",
                "border": "1px solid #E0E4DE",
                "borderRadius": "10px",
                "padding": "24px",
                "marginBottom": "20px",
            }),

            html.Div([
                html.H3(
                    "Evaluación temporal",
                    style={"color": "#193B2A", "marginTop": "0"},
                ),
                html.P("Entrenamiento: 2019–2024 (10.304 registros)."),
                html.P("Prueba independiente: 2025 (1.841 registros)."),

                html.Table([
                    html.Thead(html.Tr([
                        html.Th("Métrica"),
                        html.Th("XGBoost"),
                        html.Th("Persistencia"),
                    ])),
                    html.Tbody([
                        html.Tr([
                            html.Td("MAE (t/ha)"),
                            html.Td("0,2342"),
                            html.Td("0,1530"),
                        ]),
                        html.Tr([
                            html.Td("RMSE (t/ha)"),
                            html.Td("0,4064"),
                            html.Td("0,4246"),
                        ]),
                        html.Tr([
                            html.Td("R²"),
                            html.Td("0,9134"),
                            html.Td("0,9054"),
                        ]),
                    ]),
                ], style={
                    "width": "100%",
                    "borderCollapse": "separate",
                    "borderSpacing": "0 14px",
                    "textAlign": "left",
                }),

                html.P(
                    "XGBoost obtuvo menor RMSE y mayor R² que persistencia, "
                    "mientras que persistencia presentó menor MAE.",
                    style={
                        "backgroundColor": "#F7FAF7",
                        "padding": "14px",
                        "borderLeft": "4px solid #286A3B",
                        "borderRadius": "5px",
                    },
                ),
            ], style={
                "backgroundColor": "#FFFFFF",
                "border": "1px solid #E0E4DE",
                "borderRadius": "10px",
                "padding": "24px",
                "marginBottom": "20px",
            }),

            html.Div([
                html.H3(
                    "Limitaciones y alcance",
                    style={"color": "#193B2A", "marginTop": "0"},
                ),
                html.P(
                    "El modelo requiere el rendimiento del semestre "
                    "anterior como variable de entrada."
                ),
                html.P(
                    "Las estimaciones presentadas en este prototipo son "
                    "retrospectivas y no constituyen pronósticos futuros."
                ),
                html.P(
                    "Los resultados de evaluación corresponden al conjunto "
                    "de prueba temporal y no garantizan el mismo desempeño "
                    "para todas las observaciones individuales."
                ),
            ], style={
                "backgroundColor": "#FFFFFF",
                "border": "1px solid #E0E4DE",
                "borderRadius": "10px",
                "padding": "24px",
            }),
        ),

    }

    titulo, *componentes = contenidos[pestana]

    return html.Div([
        html.H2(titulo),
        *[
            html.P(componente) if isinstance(componente, str) else componente
            for componente in componentes
        ],
    ])



@app.callback(
    Output("filtro-municipio", "options"),
    Output("filtro-municipio", "value"),
    Input("filtro-departamento", "value"),
)
def actualizar_municipios(departamento):
    datos = df if not departamento else df[df["departamento"] == departamento]

    municipios = (
        datos[["cod_municipio", "municipio"]]
        .drop_duplicates()
        .sort_values("municipio")
    )

    opciones = [
        {"label": fila.municipio, "value": fila.cod_municipio}
        for fila in municipios.itertuples()
    ]

    return opciones, None


@app.callback(
    Output("grafico-historico", "figure"),
    Output("kpi-registros", "children"),
    Output("kpi-municipios", "children"),
    Output("kpi-media", "children"),
    Output("kpi-mediana", "children"),
    Output("ranking-territorios", "children"),
    Input("filtro-departamento", "value"),
    Input("filtro-municipio", "value"),
    Input("filtro-sistema", "value"),
    Input("filtro-anios", "value"),
)
def actualizar_grafico(departamento, municipio, sistema, anio):
    datos = df.copy()

    if departamento:
        datos = datos[datos["departamento"] == departamento]
    if municipio:
        datos = datos[datos["cod_municipio"] == municipio]
    if sistema:
        datos = datos[datos["sistema_productivo"] == sistema]
    if anio != "todos" and anio is not None:
        datos = datos[datos["anio"] == int(anio)]

    registros = len(datos)
    municipios = datos["cod_municipio"].nunique()

    rendimientos = datos["rendimiento"].dropna()
    media = rendimientos.mean()
    mediana = rendimientos.median()

    def formato(valor):
        return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    figura = crear_figura_historica(departamento, municipio, sistema, anio)


    # Ranking territorial con rendimiento ponderado por área cosechada.
    if departamento:
        columnas = ["cod_municipio", "municipio"]
        nombre_columna = "municipio"
    else:
        columnas = ["departamento"]
        nombre_columna = "departamento"

    ranking = (
        datos.groupby(columnas, as_index=False)
        .agg(
            registros=("rendimiento", "size"),
            produccion=("produccion", "sum"),
            area=("area_cosechada", "sum"),
        )
    )

    ranking = ranking[ranking["area"] > 0].copy()
    ranking["rendimiento_medio"] = (
        ranking["produccion"] / ranking["area"]
    )
    ranking = ranking.sort_values(
        "rendimiento_medio", ascending=False
    ).head(10)

    estilo_celda = {
        "padding": "11px 14px",
        "borderBottom": "1px solid #E8EBE7",
        "textAlign": "left",
        "fontSize": "13px",
    }

    filas = [
        html.Tr([
            html.Td(posicion, style=estilo_celda),
            html.Td(
                fila[nombre_columna],
                style=estilo_celda,
            ),
            html.Td(
                formato(fila["rendimiento_medio"]),
                style=estilo_celda,
            ),
            html.Td(
                f'{int(fila["registros"]):,}'.replace(",", "."),
                style=estilo_celda,
            ),
        ])
        for posicion, (_, fila) in enumerate(
            ranking.iterrows(), start=1
        )
    ]

    tabla_ranking = html.Table(
        [
            html.Thead(html.Tr([
                html.Th("#", style=estilo_celda),
                html.Th(nombre_columna.capitalize(), style=estilo_celda),
                html.Th("Rendimiento (t/ha)", style=estilo_celda),
                html.Th("Registros", style=estilo_celda),
            ])),
            html.Tbody(filas),
        ],
        style={
            "width": "100%",
            "borderCollapse": "collapse",
        },
    ) if filas else html.P("No hay datos para esta selección.")

    return (
        figura,
        f"{registros:,}".replace(",", "."),
        f"{municipios:,}".replace(",", "."),
        f"{formato(media)} t/ha" if pd.notna(media) else "Sin datos",
        f"{formato(mediana)} t/ha" if pd.notna(mediana) else "Sin datos",
        tabla_ranking,
    )


@app.callback(
    Output("pred-municipio", "options"),
    Output("pred-municipio", "value"),
    Output("pred-municipio", "multi"),
    Output("pred-municipio", "placeholder"),
    Input("pred-departamento", "value"),
    Input("pred-modalidad", "value"),
)
def actualizar_municipios_prediccion(departamento, modalidad):
    multiple = modalidad == "multiple"
    valor_vacio = [] if multiple else None

    placeholder = (
        "Seleccione uno o varios municipios"
        if multiple else "Seleccione un municipio"
    )

    if not departamento:
        return [], valor_vacio, multiple, placeholder

    municipios = (
        df.loc[
            df["departamento"] == departamento,
            ["cod_municipio", "municipio"]
        ]
        .drop_duplicates()
        .sort_values("municipio")
    )

    opciones = [
        {
            "label": f"{fila.municipio} ({fila.cod_municipio})",
            "value": fila.cod_municipio,
        }
        for fila in municipios.itertuples()
    ]

    return opciones, valor_vacio, multiple, placeholder



@app.callback(
    Output("pred-sistema", "options"),
    Output("pred-sistema", "value"),
    Input("pred-municipio", "value"),
)
def actualizar_sistemas_prediccion(municipio):
    if not municipio:
        return [], None

    municipios = municipio if isinstance(municipio, list) else [municipio]

    sistemas = sorted(
        df.loc[
            df["cod_municipio"].isin(municipios)
            & df["rendimiento_rezago"].notna(),
            "sistema_productivo"
        ].unique()
    )

    etiquetas = {
        "tradicional": "Tradicional",
        "tecnificado": "Tecnificado",
    }

    opciones = [
        {"label": etiquetas.get(s, s.title()), "value": s}
        for s in sistemas
    ]

    return opciones, None



@app.callback(
    Output("pred-anio", "options"),
    Output("pred-anio", "value"),
    Input("pred-municipio", "value"),
    Input("pred-sistema", "value"),
)
def actualizar_anios_prediccion(municipio, sistema):
    if not municipio or not sistema:
        return [], None

    municipios = municipio if isinstance(municipio, list) else [municipio]

    datos = df.loc[
        df["cod_municipio"].isin(municipios)
        & (df["sistema_productivo"] == sistema)
        & df["rendimiento_rezago"].notna()
    ]

    anios = sorted(datos["anio"].unique())

    opciones = [
        {"label": str(int(anio)), "value": int(anio)}
        for anio in anios
    ]

    return opciones, None



@app.callback(
    Output("pred-semestre", "options"),
    Output("pred-semestre", "value"),
    Input("pred-municipio", "value"),
    Input("pred-sistema", "value"),
    Input("pred-anio", "value"),
)
def actualizar_semestres_prediccion(municipio, sistema, anio):
    if not municipio or not sistema or anio is None:
        return [], None

    municipios = municipio if isinstance(municipio, list) else [municipio]

    datos = df.loc[
        df["cod_municipio"].isin(municipios)
        & (df["sistema_productivo"] == sistema)
        & (df["anio"] == anio)
        & df["rendimiento_rezago"].notna()
    ]

    semestres = sorted(datos["semestre_b"].unique())

    etiquetas = {0: "Semestre A", 1: "Semestre B"}

    opciones = [
        {"label": etiquetas[int(s)], "value": int(s)}
        for s in semestres
    ]

    return opciones, None






def preparar_exportacion_multiple(departamento, municipios, sistema, anio, semestre):
    """Prepara una tabla exportable con las predicciones múltiples."""

    if not departamento or not municipios or not sistema or anio is None or semestre is None:
        return pd.DataFrame()

    resultados, _ = calcular_predicciones_multiples(
        departamento, municipios, sistema, anio, semestre
    )

    if resultados.empty:
        return pd.DataFrame()

    exportacion = resultados.rename(columns={
        "cod_municipio": "Codigo DANE",
        "municipio": "Municipio",
        "departamento": "Departamento",
        "sistema": "Sistema productivo",
        "anio": "Anio",
        "semestre": "Semestre",
        "estimado": "Estimacion XGBoost (t/ha)",
        "persistencia": "Persistencia (t/ha)",
        "observado": "Rendimiento observado (t/ha)",
    }).copy()

    exportacion["Codigo DANE"] = (
        exportacion["Codigo DANE"].astype(str).str.zfill(5)
    )

    exportacion["Semestre"] = exportacion["Semestre"].map({
        0: "A",
        1: "B",
    })

    return exportacion


@app.callback(
    Output("descarga-predicciones-csv", "data"),
    Input("btn-descargar-csv", "n_clicks"),
    State("pred-departamento", "value"),
    State("pred-municipio", "value"),
    State("pred-sistema", "value"),
    State("pred-anio", "value"),
    State("pred-semestre", "value"),
    prevent_initial_call=True,
)
def descargar_predicciones_csv(n_clicks, departamento, municipios, sistema, anio, semestre):
    if not n_clicks:
        raise PreventUpdate

    tabla = preparar_exportacion_multiple(
        departamento, municipios, sistema, anio, semestre
    )

    if tabla.empty:
        raise PreventUpdate

    return dcc.send_data_frame(
        tabla.to_csv,
        f"agropredict_predicciones_{anio}_{'B' if semestre == 1 else 'A'}.csv",
        index=False,
        encoding="utf-8-sig",
    )


@app.callback(
    Output("descarga-predicciones-excel", "data"),
    Input("btn-descargar-excel", "n_clicks"),
    State("pred-departamento", "value"),
    State("pred-municipio", "value"),
    State("pred-sistema", "value"),
    State("pred-anio", "value"),
    State("pred-semestre", "value"),
    prevent_initial_call=True,
)
def descargar_predicciones_excel(n_clicks, departamento, municipios, sistema, anio, semestre):
    if not n_clicks:
        raise PreventUpdate

    tabla = preparar_exportacion_multiple(
        departamento, municipios, sistema, anio, semestre
    )

    if tabla.empty:
        raise PreventUpdate

    return dcc.send_data_frame(
        tabla.to_excel,
        f"agropredict_predicciones_{anio}_{'B' if semestre == 1 else 'A'}.xlsx",
        index=False,
        sheet_name="Predicciones",
    )


def calcular_predicciones_multiples(
    departamento, municipios, sistema, anio, semestre
):
    """Genera estimaciones retrospectivas para varios municipios."""

    if not municipios:
        return pd.DataFrame(), []

    seleccionados = list(dict.fromkeys(municipios))

    registros = df.loc[
        (df["departamento"] == departamento)
        & df["cod_municipio"].isin(seleccionados)
        & (df["sistema_productivo"] == sistema)
        & (df["anio"] == anio)
        & (df["semestre_b"] == semestre)
        & df["rendimiento_rezago"].notna()
    ].copy()

    # Solo se procesan municipios con un registro único.
    conteos = registros.groupby("cod_municipio").size()
    codigos_validos = conteos[conteos == 1].index

    validos = registros.loc[
        registros["cod_municipio"].isin(codigos_validos)
    ].copy()

    if validos.empty:
        return pd.DataFrame(), seleccionados

    validos["estimado"] = modelo_predictivo.predict(
        validos[VARIABLES_MODELO]
    )

    validos = validos.loc[
        pd.notna(validos["estimado"])
    ].copy()

    resultados = validos[[
        "cod_municipio",
        "municipio",
        "departamento",
        "sistema_productivo",
        "anio",
        "semestre_b",
        "estimado",
        "rendimiento",
        "rendimiento_rezago",
    ]].rename(columns={
        "sistema_productivo": "sistema",
        "semestre_b": "semestre",
        "rendimiento": "observado",
        "rendimiento_rezago": "persistencia",
    })

    resultados = resultados.sort_values("municipio")

    procesados = set(resultados["cod_municipio"])
    omitidos = [
        codigo for codigo in seleccionados
        if codigo not in procesados
    ]

    return resultados, omitidos


@app.callback(
    Output("resultado-prediccion", "children"),
    Output("ultima-prediccion", "data"),
    Input("btn-predecir", "n_clicks"),
    State("pred-departamento", "value"),
    State("pred-municipio", "value"),
    State("pred-sistema", "value"),
    State("pred-anio", "value"),
    State("pred-semestre", "value"),
    State("pred-modalidad", "value"),
    prevent_initial_call=True,
)
def generar_prediccion(
    n_clicks, departamento, municipio, sistema, anio, semestre, modalidad
):
    if not n_clicks:
        raise PreventUpdate

    if modalidad == "multiple":
        if (
            not departamento
            or not municipio
            or not sistema
            or anio is None
            or semestre is None
        ):
            return html.P(
                "Complete todos los campos antes de generar las predicciones.",
                style={"color": "#b45309"},
            ), None

        resultados, omitidos = calcular_predicciones_multiples(
            departamento, municipio, sistema, anio, semestre
        )

        if resultados.empty:
            return html.P(
                "No se encontraron registros válidos para los municipios "
                "y el período seleccionados.",
                style={"color": "#b45309"},
            ), None

        columnas = [
            ("municipio", "Municipio"),
            ("estimado", "Estimación XGBoost (t/ha)"),
            ("persistencia", "Persistencia (t/ha)"),
            ("observado", "Observado (t/ha)"),
        ]

        encabezado = html.Tr([
            html.Th(
                etiqueta,
                style={
                    "padding": "12px",
                    "textAlign": "left",
                    "borderBottom": "2px solid #DCE8DC",
                },
            )
            for _, etiqueta in columnas
        ])

        filas = [
            html.Tr([
                html.Td(
                    f"{fila[columna]:.2f}"
                    if columna != "municipio"
                    else str(fila[columna]),
                    style={
                        "padding": "10px 12px",
                        "borderBottom": "1px solid #E2E8F0",
                    },
                )
                for columna, _ in columnas
            ])
            for _, fila in resultados.iterrows()
        ]

        contenido = html.Div([
            html.H3(
                "Resultados de predicción múltiple",
                style={"color": "#193B2A"},
            ),
            html.P(
                f"Municipios procesados: {len(resultados)}. "
                f"Municipios omitidos: {len(omitidos)}.",
                style={"color": "#475569"},
            ),
            html.Div(
                html.Table(
                    [html.Thead(encabezado), html.Tbody(filas)],
                    style={
                        "width": "100%",
                        "borderCollapse": "collapse",
                    },
                ),
                style={"overflowX": "auto"},
            ),
            html.Div([
                html.Button(
                    "Descargar CSV",
                    id="btn-descargar-csv",
                    n_clicks=0,
                    style={
                        "backgroundColor": "#286A3B",
                        "color": "#FFFFFF",
                        "border": "none",
                        "borderRadius": "7px",
                        "padding": "11px 18px",
                        "cursor": "pointer",
                        "fontWeight": "600",
                    },
                ),
                html.Button(
                    "Descargar Excel",
                    id="btn-descargar-excel",
                    n_clicks=0,
                    style={
                        "backgroundColor": "#FFFFFF",
                        "color": "#286A3B",
                        "border": "1px solid #286A3B",
                        "borderRadius": "7px",
                        "padding": "11px 18px",
                        "cursor": "pointer",
                        "fontWeight": "600",
                    },
                ),
            ], style={
                "display": "flex",
                "gap": "12px",
                "flexWrap": "wrap",
                "marginTop": "20px",
                "marginBottom": "16px",
            }),
            html.P(
                "Estimaciones retrospectivas basadas en registros históricos. "
                "No representan pronósticos futuros.",
                style={
                    "color": "#64748B",
                    "fontSize": "12px",
                    "marginTop": "16px",
                },
            ),
        ], style={
            "backgroundColor": "#FFFFFF",
            "border": "1px solid #E0E4DE",
            "borderRadius": "10px",
            "padding": "24px",
        })

        return contenido, None

    if (
        not departamento
        or not municipio
        or not sistema
        or anio is None
        or semestre is None
    ):
        return html.P(
            "Complete todos los campos antes de generar la predicción.",
            style={"color": "#b45309"},
        ), None

    registros = df.loc[
        (df["departamento"] == departamento)
        & (df["cod_municipio"] == municipio)
        & (df["sistema_productivo"] == sistema)
        & (df["anio"] == anio)
        & (df["semestre_b"] == semestre)
    ]

    if len(registros) != 1:
        return html.P(
            "No existe un registro único para la combinación seleccionada."
        ), None

    registro = registros.iloc[0]

    if pd.isna(registro["rendimiento_rezago"]):
        return html.P(
            "No existe rendimiento del semestre anterior para esta selección."
        ), None

    entrada = registros[VARIABLES_MODELO]
    estimacion = float(modelo_predictivo.predict(entrada)[0])

    if not pd.notna(estimacion):
        return html.P("El modelo no produjo una estimación válida."), None

    promedios = calcular_promedios_historicos(
        departamento, municipio, sistema, anio, semestre
    )

    datos_resultado = {
        "promedio_municipal": promedios["municipal"],
        "promedio_departamental": promedios["departamental"],
        "promedio_nacional": promedios["nacional"],
        "municipio": str(registro["municipio"]),
        "departamento": str(departamento),
        "sistema": str(sistema),
        "anio": int(anio),
        "semestre": int(semestre),
        "estimado": estimacion,
        "observado": float(registro["rendimiento"]),
        "persistencia": float(registro["rendimiento_rezago"]),
    }

    contenido = html.Div([
        html.P(
            "RENDIMIENTO ESTIMADO",
            style={
                "fontSize": "12px",
                "fontWeight": "700",
                "letterSpacing": "1px",
                "color": "#64748b",
                "marginBottom": "8px",
            },
        ),
        html.H2(
            f"{estimacion:.2f} t/ha",
            style={
                "fontSize": "38px",
                "fontWeight": "700",
                "color": "#286A3B",
                "margin": "0 0 12px 0",
            },
        ),
        html.P(
            f"{registro['municipio']}, {departamento} · "
            f"{sistema.capitalize()} · "
            f"{anio}-{'B' if semestre == 1 else 'A'}",
            style={"color": "#475569", "fontSize": "14px"},
        ),
        html.Hr(style={"border": "none", "borderTop": "1px solid #E2E8F0"}),
        html.P(
            f"Rendimiento del semestre anterior: "
            f"{registro['rendimiento_rezago']:.2f} t/ha",
            style={"fontSize": "14px", "color": "#334155"},
        ),
        html.Small(
            "Estimación retrospectiva basada en datos históricos. "
            "No representa un pronóstico futuro.",
            style={"color": "#64748b"},
        ),
    ], style={
        "padding": "24px",
        "backgroundColor": "#F7FAF7",
        "border": "1px solid #DCE8DC",
        "borderLeft": "4px solid #286A3B",
        "borderRadius": "10px",
    })

    return contenido, datos_resultado



@app.callback(
    Output("panel-resultados", "children"),
    Input("ultima-prediccion", "data"),
)
def mostrar_resultados(datos):
    if not datos:
        return html.P(
            "Genere primero una predicción en la pestaña Predicción."
        )

    estimado = float(datos["estimado"])
    observado = float(datos["observado"])
    persistencia = float(datos["persistencia"])

    error_xgb = abs(observado - estimado)
    error_persistencia = abs(observado - persistencia)

    if error_xgb < error_persistencia:
        conclusion = "XGBoost presentó el menor error en esta observación."
    elif error_persistencia < error_xgb:
        conclusion = "La persistencia presentó el menor error en esta observación."
    else:
        conclusion = "Ambos métodos presentaron el mismo error absoluto."

    def tarjeta(titulo, valor, color):
        return html.Div([
            html.P(
                titulo,
                style={
                    "fontSize": "12px",
                    "fontWeight": "700",
                    "color": "#64748B",
                    "margin": "0 0 10px 0",
                },
            ),
            html.H2(
                f"{valor:.2f} t/ha",
                style={
                    "color": color,
                    "fontSize": "30px",
                    "margin": "0",
                },
            ),
        ], style={
            "backgroundColor": "#FFFFFF",
            "border": "1px solid #E0E4DE",
            "borderRadius": "9px",
            "padding": "22px",
        })

    comparacion = pd.DataFrame({
        "Referencia": ["XGBoost", "Persistencia", "Observado"],
        "Rendimiento": [estimado, persistencia, observado],
    })

    figura = px.bar(
        comparacion,
        x="Referencia",
        y="Rendimiento",
        text="Rendimiento",
        color="Referencia",
        color_discrete_map={
            "XGBoost": "#286A3B",
            "Persistencia": "#D58A25",
            "Observado": "#64748B",
        },
        labels={
            "Referencia": "",
            "Rendimiento": "Rendimiento (t/ha)",
        },
        template="plotly_white",
    )

    figura.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside",
        hovertemplate="%{x}: %{y:.2f} t/ha<extra></extra>",
    )

    figura.update_layout(
        showlegend=False,
        margin=dict(l=30, r=30, t=35, b=30),
        yaxis_range=[
            0,
            max(estimado, persistencia, observado, 0.1) * 1.25,
        ],
        height=380,
    )


    # Comparación con referencias históricas anteriores al período consultado
    promedio_municipal = datos.get("promedio_municipal")
    promedio_departamental = datos.get("promedio_departamental")
    promedio_nacional = datos.get("promedio_nacional")

    referencias = [
        ("Municipio", promedio_municipal),
        ("Departamento", promedio_departamental),
        ("Colombia", promedio_nacional),
    ]

    comparacion_historica = pd.DataFrame(
        [
            {"Territorio": nombre, "Rendimiento": valor}
            for nombre, valor in referencias
            if valor is not None and pd.notna(valor)
        ]
    )

    if not comparacion_historica.empty:
        figura_historica = px.bar(
            comparacion_historica,
            x="Territorio",
            y="Rendimiento",
            text="Rendimiento",
            color="Territorio",
            color_discrete_map={
                "Municipio": "#286A3B",
                "Departamento": "#D58A25",
                "Colombia": "#64748B",
            },
            labels={
                "Territorio": "",
                "Rendimiento": "Rendimiento histórico (t/ha)",
            },
            template="plotly_white",
        )

        figura_historica.update_traces(
            texttemplate="%{text:.2f}",
            textposition="outside",
            hovertemplate="%{x}: %{y:.2f} t/ha<extra></extra>",
        )

        figura_historica.update_layout(
            showlegend=False,
            height=360,
            margin=dict(l=30, r=30, t=35, b=30),
            yaxis_range=[
                0,
                max(comparacion_historica["Rendimiento"].max(), 0.1) * 1.25,
            ],
        )

        grafica_historica = dcc.Graph(figure=figura_historica)
    else:
        grafica_historica = html.P(
            "No hay registros históricos disponibles para esta selección."
        )

    if promedio_municipal is not None and promedio_municipal > 0:
        variacion = (
            (estimado - promedio_municipal) / promedio_municipal
        ) * 100

        signo = "+" if variacion > 0 else ""

        texto_variacion = f"{signo}{variacion:.2f}%"
        explicacion_variacion = (
            "Variación de la estimación XGBoost frente al "
            "rendimiento histórico municipal."
        )
    else:
        texto_variacion = "No disponible"
        explicacion_variacion = (
            "No existen datos suficientes para calcular "
            "la variación frente al promedio municipal."
        )

    seccion_historica = html.Div([
        html.H3(
            "Comparación con rendimientos históricos",
            style={"color": "#193B2A", "marginTop": "0"},
        ),
        html.P(
            "Referencias calculadas con registros anteriores al "
            "período consultado y del mismo sistema productivo. "
            "Rendimientos ponderados por área cosechada.",
            style={"color": "#64748B", "fontSize": "13px"},
        ),
        grafica_historica,
        html.Div([
            html.P(
                "VARIACIÓN FRENTE AL PROMEDIO MUNICIPAL",
                style={
                    "fontSize": "12px",
                    "fontWeight": "700",
                    "color": "#64748B",
                },
            ),
            html.H2(
                texto_variacion,
                style={"color": "#286A3B", "margin": "8px 0"},
            ),
            html.P(
                explicacion_variacion,
                style={"color": "#475569", "fontSize": "13px"},
            ),
        ], style={
            "padding": "20px",
            "backgroundColor": "#F7FAF7",
            "border": "1px solid #DCE8DC",
            "borderRadius": "9px",
        }),
    ], style={
        "backgroundColor": "#FFFFFF",
        "border": "1px solid #E0E4DE",
        "borderRadius": "10px",
        "padding": "24px",
        "marginTop": "20px",
    })

    periodo = f"{datos['anio']}-{'B' if datos['semestre'] == 1 else 'A'}"

    return html.Div([
        html.P(
            f"{datos['municipio']}, {datos['departamento']} · "
            f"{datos['sistema'].capitalize()} · {periodo}",
            style={
                "color": "#64748B",
                "fontSize": "15px",
                "marginBottom": "20px",
            },
        ),

        html.Div([
            tarjeta("ESTIMACIÓN XGBOOST", estimado, "#286A3B"),
            tarjeta("PERSISTENCIA", persistencia, "#D58A25"),
            tarjeta("RENDIMIENTO OBSERVADO", observado, "#334155"),
        ], style={
            "display": "grid",
            "gridTemplateColumns": "repeat(auto-fit, minmax(220px, 1fr))",
            "gap": "16px",
            "marginBottom": "20px",
        }),

        html.Div([
            html.H3(
                "Comparación de rendimientos",
                style={"color": "#193B2A", "marginTop": "0"},
            ),
            dcc.Graph(
                figure=figura,
                config={"displayModeBar": False},
            ),
        ], style={
            "backgroundColor": "#FFFFFF",
            "border": "1px solid #E0E4DE",
            "borderRadius": "9px",
            "padding": "22px",
            "marginBottom": "20px",
        }),

        html.Div([
            html.H3(
                "Errores absolutos de la observación",
                style={"color": "#193B2A", "marginTop": "0"},
            ),
            html.Div([
                html.P(f"XGBoost: {error_xgb:.4f} t/ha"),
                html.P(f"Persistencia: {error_persistencia:.4f} t/ha"),
            ]),
            html.P(
                conclusion,
                style={
                    "fontWeight": "600",
                    "color": "#286A3B",
                },
            ),
            html.Small(
                "Comparación retrospectiva con el rendimiento observado. "
                "El valor observado no se utiliza como entrada del modelo. "
                "Estos errores corresponden únicamente a la observación "
                "seleccionada y no representan métricas globales.",
                style={"color": "#64748B"},
            ),
        ], style={
            "backgroundColor": "#FFFFFF",
            "border": "1px solid #E0E4DE",
            "borderRadius": "9px",
            "padding": "22px",
        }),
                        seccion_historica,
    ])


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8050)
