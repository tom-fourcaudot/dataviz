import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
from country_dict import country_dict
from dash.dependencies import Input, Output

# Charger le dataset
df = pd.read_csv('data.csv')

# Filtrer les lignes avec des données nulles ou non renseignées
df = df.dropna()
df = df[df.applymap(lambda x: x != 'Non renseigné' and x != '').all(axis=1)]

# Vérifier et convertir les types de données si nécessaire
df['work_year'] = df['work_year'].astype(int)
df['salary'] = df['salary'].astype(float)
df['salary_in_usd'] = df['salary_in_usd'].astype(float)
df['remote_ratio'] = df['remote_ratio'].astype(int)

# Calculer le pourcentage de données provenant des US vs autres pays
total_count = len(df)
us_count = len(df[df['company_location'].str.upper() == 'US'])
other_count = total_count - us_count

# Créer les données pour le diagramme en camembert
data = {
    'Location': ['US', 'Other'],
    'Count': [us_count, other_count]
}
df_pie = pd.DataFrame(data)

# Convertir les abréviations de pays en noms complets
df['employee_residence'] = df['employee_residence'].map(country_dict)
df['company_location'] = df['company_location'].map(country_dict)

# Renommer les valeurs de remote_ratio
df['remote_ratio'] = df['remote_ratio'].map({0: 'no remote', 50: 'semi remote', 100: 'full remote'})


# Trier les salaires moyens par localisation par ordre croissant
average_salaries_by_location = df.groupby('company_location')['salary_in_usd'].mean().reset_index()
average_salaries_by_location = average_salaries_by_location.sort_values(by='salary_in_usd').tail(25)

# Calculer les salaires moyens par métier
average_salaries_by_job = df.groupby('job_title')['salary_in_usd'].mean().reset_index()

# Trier par salaire moyen
average_salaries_by_job = average_salaries_by_job.sort_values(by='salary_in_usd')

# Calculer le nombre de réponses par pays (localisation de l'entreprise)
response_count_by_location = df['company_location'].value_counts().reset_index()
response_count_by_location.columns = ['company_location', 'response_count']

# Calculer les salaires moyens par pays
average_salaries_by_country = df.groupby('company_location')['salary_in_usd'].mean().reset_index()
average_salaries_by_country.columns = ['country', 'average_salary']

# Calculer le nombre de réponses par pays
response_count_by_country = df['company_location'].value_counts().reset_index()
response_count_by_country.columns = ['country', 'response_count']

pie_us_vs_other = px.pie(df_pie, values='Count', names='Location', title='Pourcentage de données provenant des US vs autres pays', color_discrete_sequence=['blue', 'red'])

# Graphique 1: Boxplot des salaires par niveau d'expérience
boxplot = px.box(df, x='experience_level', y='salary_in_usd', title='Salaires par niveau d\'expérience')

# Graphique 2: Barplot horizontal des salaires moyens par localisation
barplot = px.bar(average_salaries_by_location, y='company_location', x='salary_in_usd', 
                 title='Salaires moyens par localisation (Ordre croissant)', orientation='h')
barplot.update_layout(
    height=800,  # Augmenter la hauteur de la figure pour plus d'espace pour les barres
    bargap=0.1  # Réduire l'espacement entre les barres
)

# Graphique 3: Histogramme des salaires
histogram = px.histogram(df, x='salary_in_usd', nbins=50, title='Distribution des salaires')

# Graphique 4: Pie chart du nombre de réponses par localisation avec regroupement
pie_chart = px.pie(response_count_by_location, values='response_count', names='company_location',
                   title=f'Répartition des réponses par localisation', hole=0.3)
pie_chart.update_traces(textinfo='none',
                        pull=[0.05]*len(response_count_by_location))

# Graphique 5: Boxplot des salaires par taux de télétravail
remote_salary_boxplot = px.box(df, x='remote_ratio', y='salary_in_usd', title='Salaires par taux de télétravail')

# Graphique 6: Heatmap du salaire moyen par pays
choropleth_salary = px.choropleth(average_salaries_by_country, locations='country', locationmode='country names',
                                  color='average_salary', 
                                  hover_name='country', 
                                  color_continuous_scale=px.colors.sequential.Plasma,
                                  title='Salaire moyen par pays')
choropleth_salary.update_layout(
    width=1200,  # Augmenter la largeur de la figure
    margin=dict(l=0, r=0, t=50, b=0)  # Ajuster les marges pour plus d'espace
)

# Graphique 7: Heatmap du nombre de réponses par pays
choropleth_responses = px.choropleth(response_count_by_country, locations='country', locationmode='country names',
                                     color='response_count', 
                                     hover_name='country', 
                                     color_continuous_scale=px.colors.sequential.Plasma,
                                     title='Nombre de réponses par pays')
choropleth_responses.update_layout(
    width=1200,  # Augmenter la largeur de la figure
    margin=dict(l=0, r=0, t=50, b=0)  # Ajuster les marges pour plus d'espace
)

# Graphique 8: Histogramme des salaires par metiers
job_bar = px.bar(average_salaries_by_job, y='job_title', x='salary_in_usd', 
                 title='Salaires moyens par emploie (Ordre croissant)', orientation='h')
job_bar.update_layout(
    height=800,  # Augmenter la hauteur de la figure pour plus d'espace pour les barres
    bargap=0.1  # Réduire l'espacement entre les barres
)

# Initialiser l'application Dash
app = dash.Dash(__name__)

# Définir la disposition de l'application
passion_layout = html.Div(children=[
    html.Div([
        html.Img(src='assets/logo.png', style={'width': '3`00px'}),  # Afficher le logo
        html.H1(children='Analyse des salaires des développeurs en 2024')
    ], style={'display': 'flex', 'alignItems': 'center'}),  # Alignement horizontal et centrage
    dcc.Graph(id='remote_salary_boxplot', figure=remote_salary_boxplot),
    dcc.Graph(id='boxplot', figure=boxplot),
    dcc.Graph(id='choropleth_salary', figure=choropleth_salary),
    dcc.Graph(id='barplot', figure=barplot),
], style={'width': '95%', 'margin': 'auto'})

trust_layout = html.Div(children=[
     html.Div([
        html.Img(src='assets/trustData.png', style={'width': '3`00px'}),  # Afficher le logo
        html.H1(children='Dev for pa$$ion, manipulateurs...')
    ], style={'display': 'flex', 'alignItems': 'center'}),  # Alignement horizontal et centrage
    dcc.Graph(id='choropleth_responses', figure=choropleth_responses),
    html.Div([
        dcc.Graph(id='us_vs_other', figure=pie_us_vs_other),

        dcc.Graph(id='pie_chart', figure=pie_chart),
    ]),
    dcc.Graph(id='histogram', figure=histogram),
    dcc.Graph(id='job_bar', figure=job_bar),
], style={'width': '95%', 'margin': 'auto'})

# Layout principal avec le gestionnaire d'URL
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Callback pour mettre à jour le contenu de la page en fonction de l'URL
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/trustData':
        return trust_layout
    else:
        return passion_layout

# Exécuter l'application
if __name__ == '__main__':
    app.run_server(debug=False)
