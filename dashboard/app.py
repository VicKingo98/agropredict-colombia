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


def crear_figura_historica(departamento=None, municipio=None, sistema=None):
    datos = df.copy()

    if departamento:
        datos = datos[datos["departamento"] == departamento]
    if municipio:
        datos = datos[datos["cod_municipio"] == municipio]
    if sistema:
        datos = datos[datos["sistema_productivo"] == sistema]

    historico = (
        datos.groupby(["anio", "semestre_b"], as_index=False)
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

    return px.line(
        historico,
        x="periodo",
        y="rendimiento_ponderado",
        markers=True,
        title="Evolución histórica del rendimiento del maíz",
        labels={
            "periodo": "Periodo agrícola",
            "rendimiento_ponderado": "Rendimiento (t/ha)",
        },
    )



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
    "padding": "12px 20px",
    "fontWeight": "600",
}

app.layout = html.Div(
    [
        html.H1("AgroPredict Colombia"),
        html.P("Estimación del rendimiento municipal del maíz en Colombia"),

        dcc.Store(id="ultima-prediccion", storage_type="memory"),

        dcc.Tabs(
            id="pestanas",
            value="historico",
            children=[
                dcc.Tab(label="Histórico", value="historico", style=ESTILO_PESTANA),
                dcc.Tab(label="Predicción", value="prediccion", style=ESTILO_PESTANA),
                dcc.Tab(label="Resultados", value="resultados", style=ESTILO_PESTANA),
                dcc.Tab(label="Modelo", value="modelo", style=ESTILO_PESTANA),
            ],
        ),

        html.Div(id="contenido-pestana", style={"padding": "30px 0"}),
    ],
    style={
        "fontFamily": "Arial, sans-serif",
        "maxWidth": "1100px",
        "margin": "40px auto",
        "padding": "20px",
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
            html.Div([
                html.Label("Departamento"),
                dcc.Dropdown(
                    id="filtro-departamento",
                    options=[
                        {"label": d, "value": d}
                        for d in sorted(df["departamento"].unique())
                    ],
                    placeholder="Todos los departamentos",
                    clearable=True,
                ),
                html.Br(),
                html.Label("Municipio"),
                dcc.Dropdown(
                    id="filtro-municipio",
                    placeholder="Todos los municipios",
                    clearable=True,
                ),
                html.Br(),
                html.Label("Sistema productivo"),
                dcc.Dropdown(
                    id="filtro-sistema",
                    options=[
                        {"label": "Tradicional", "value": "tradicional"},
                        {"label": "Tecnificado", "value": "tecnificado"},
                    ],
                    placeholder="Todos los sistemas",
                    clearable=True,
                ),
            ], style={"maxWidth": "500px"}),
            dcc.Graph(id="grafico-historico"),
        ),
        "prediccion": (
            "Generar predicción",
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
                html.Br(),
                html.Label("Municipio"),
                dcc.Dropdown(
                    id="pred-municipio",
                    placeholder="Seleccione un municipio",
                ),
                html.Br(),
                html.Label("Sistema productivo"),
                dcc.Dropdown(
                    id="pred-sistema",
                    options=[
                        {"label": "Tradicional", "value": "tradicional"},
                        {"label": "Tecnificado", "value": "tecnificado"},
                    ],
                    placeholder="Seleccione un sistema productivo",
                ),
                html.Br(),
                html.Label("Año"),
                dcc.Dropdown(
                    id="pred-anio",
                    options=[
                        {"label": str(a), "value": int(a)}
                        for a in sorted(df["anio"].unique())
                    ],
                    placeholder="Seleccione un año",
                ),
                html.Br(),
                html.Label("Semestre"),
                dcc.Dropdown(
                    id="pred-semestre",
                    options=[
                        {"label": "A", "value": 0},
                        {"label": "B", "value": 1},
                    ],
                    placeholder="Seleccione un semestre",
                ),
                html.Br(),
                html.Button(
                    "Generar predicción",
                    id="btn-predecir",
                    n_clicks=0,
                    style={
                        "backgroundColor": "#2563eb",
                        "color": "white",
                        "border": "none",
                        "borderRadius": "6px",
                        "padding": "12px 24px",
                        "fontWeight": "600",
                        "cursor": "pointer",
                    },
                ),
                html.Div(
                    id="resultado-prediccion",
                    style={"marginTop": "24px"},
                ),
            ], style={"maxWidth": "500px"}),
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
            "Información del modelo",
            html.Div([
                html.H3("XGBoost optimizado"),
                html.P(
                    "Modelo supervisado para estimar el rendimiento "
                    "municipal del maíz, expresado en toneladas por hectárea."
                ),
                html.H4("Variables predictoras"),
                html.Ul([
                    html.Li("Año"),
                    html.Li("Semestre agrícola"),
                    html.Li("Rendimiento del semestre anterior"),
                    html.Li("Departamento"),
                    html.Li("Sistema productivo"),
                ]),
                html.H4("Evaluación temporal"),
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
                    "maxWidth": "650px",
                    "textAlign": "left",
                    "borderSpacing": "15px",
                }),
                html.H4("Limitaciones"),
                html.P(
                    "El modelo necesita conocer el rendimiento del "
                    "semestre inmediatamente anterior. Las estimaciones "
                    "mostradas actualmente son retrospectivas y no "
                    "constituyen pronósticos futuros."
                ),
                html.P(
                    "XGBoost presenta un RMSE menor que persistencia, "
                    "pero un MAE mayor en el conjunto de prueba."
                ),
            ]),
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
    Input("filtro-departamento", "value"),
    Input("filtro-municipio", "value"),
    Input("filtro-sistema", "value"),
)
def actualizar_grafico(departamento, municipio, sistema):
    return crear_figura_historica(departamento, municipio, sistema)



@app.callback(
    Output("pred-municipio", "options"),
    Output("pred-municipio", "value"),
    Input("pred-departamento", "value"),
)
def actualizar_municipios_prediccion(departamento):
    if not departamento:
        return [], None

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

    return opciones, None



@app.callback(
    Output("pred-sistema", "options"),
    Output("pred-sistema", "value"),
    Input("pred-municipio", "value"),
)
def actualizar_sistemas_prediccion(municipio):
    if not municipio:
        return [], None

    sistemas = sorted(
        df.loc[
            (df["cod_municipio"] == municipio)
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

    datos = df.loc[
        (df["cod_municipio"] == municipio)
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

    datos = df.loc[
        (df["cod_municipio"] == municipio)
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




@app.callback(
    Output("resultado-prediccion", "children"),
    Output("ultima-prediccion", "data"),
    Input("btn-predecir", "n_clicks"),
    State("pred-departamento", "value"),
    State("pred-municipio", "value"),
    State("pred-sistema", "value"),
    State("pred-anio", "value"),
    State("pred-semestre", "value"),
    prevent_initial_call=True,
)
def generar_prediccion(
    n_clicks, departamento, municipio, sistema, anio, semestre
):
    if not n_clicks:
        raise PreventUpdate

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

    datos_resultado = {
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
        html.H3("Resultado de la estimación"),
        html.H2(f"{estimacion:.2f} t/ha"),
        html.P(
            f"Rendimiento del semestre anterior: "
            f"{registro['rendimiento_rezago']:.2f} t/ha"
        ),
        html.P(
            f"Municipio: {registro['municipio']} | "
            f"Periodo: {anio}-{'B' if semestre == 1 else 'A'}"
        ),
        html.Small(
            "Estimación retrospectiva basada en datos históricos. "
            "No representa un pronóstico futuro."
        ),
    ], style={
        "padding": "20px",
        "backgroundColor": "#f1f5f9",
        "borderRadius": "8px",
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

    comparacion = pd.DataFrame({
        "Referencia": ["XGBoost", "Persistencia", "Observado"],
        "Rendimiento": [estimado, persistencia, observado],
    })

    figura = px.bar(
        comparacion,
        x="Referencia",
        y="Rendimiento",
        text="Rendimiento",
        title="Comparación de rendimientos",
        labels={"Rendimiento": "Rendimiento (t/ha)"},
        color="Referencia",
        color_discrete_map={
            "XGBoost": "#2563eb",
            "Persistencia": "#94a3b8",
            "Observado": "#16a34a",
        },
    )

    figura.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside",
    )

    figura.update_layout(
        showlegend=False,
        yaxis_range=[
            0,
            max(estimado, persistencia, observado) * 1.2,
        ],
    )

    return html.Div([
        html.H3(
            f"{datos['municipio']}, {datos['departamento']} "
            f"— {datos['anio']}-"
            f"{'B' if datos['semestre'] == 1 else 'A'}"
        ),
        html.P(
            f"Sistema productivo: {datos['sistema'].capitalize()}"
        ),
        dcc.Graph(figure=figura),
        html.H4("Errores absolutos de esta observación"),
        html.P(f"XGBoost: {error_xgb:.4f} t/ha"),
        html.P(f"Persistencia: {error_persistencia:.4f} t/ha"),
        html.Small(
            "Comparación retrospectiva con el rendimiento observado. "
            "El valor observado no se utiliza como entrada del modelo."
        ),
    ])


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8050)
