import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
from country_dict import country_dict

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

# Convertir les abréviations de pays en noms complets
df['employee_residence'] = df['employee_residence'].map(country_dict)
df['company_location'] = df['company_location'].map(country_dict)

# Renommer les valeurs de remote_ratio
df['remote_ratio'] = df['remote_ratio'].map({0: 'no remote', 50: 'semi remote', 100: 'full remote'})

# Trier les salaires moyens par localisation par ordre croissant
average_salaries_by_location = df.groupby('company_location')['salary_in_usd'].mean().reset_index()
average_salaries_by_location = average_salaries_by_location.sort_values(by='salary_in_usd')

# Calculer le nombre de réponses par pays (localisation de l'entreprise)
response_count_by_location = df['company_location'].value_counts().reset_index()
response_count_by_location.columns = ['company_location', 'response_count']

# Regrouper les pays représentant moins de 1% des réponses dans une catégorie "Autres"
total_responses = response_count_by_location['response_count'].sum()
response_count_by_location['percentage'] = response_count_by_location['response_count'] / total_responses

# Calculer le nombre de pays regroupés
num_countries_other = (response_count_by_location['percentage'] < 0.01).sum()

# Mettre à jour les labels pour inclure le nombre de pays dans "Autres"
response_count_by_location['company_location'] = response_count_by_location.apply(
    lambda row: f'Autres {num_countries_other}' if row['percentage'] < 0.01 else row['company_location'], axis=1)

# Recalculer le nombre de réponses après regroupement
response_count_by_location = response_count_by_location.groupby('company_location').sum().reset_index()

# Calculer les salaires moyens par pays
average_salaries_by_country = df.groupby('employee_residence')['salary_in_usd'].mean().reset_index()
average_salaries_by_country.columns = ['country', 'average_salary']

# Calculer le nombre de réponses par pays
response_count_by_country = df['employee_residence'].value_counts().reset_index()
response_count_by_country.columns = ['country', 'response_count']

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
                   title=f'Répartition des réponses par localisation (Autres {num_countries_other} pays)', hole=0.3)
pie_chart.update_traces(textinfo='percent+label', 
                        textposition='inside',
                        texttemplate='%{label}: %{percent:.1%f}',
                        hovertemplate='%{label}: %{percent:.2%f} (%{value})',
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

# Initialiser l'application Dash
app = dash.Dash(__name__)

# Définir la disposition de l'application
app.layout = html.Div(children=[
    html.H1(children='Analyse des salaires des développeurs en 2024'),
    dcc.Graph(id='remote_salary_boxplot', figure=remote_salary_boxplot),
    dcc.Graph(id='boxplot', figure=boxplot),
    dcc.Graph(id='choropleth_salary', figure=choropleth_salary),
    dcc.Graph(id='barplot', figure=barplot),
    dcc.Graph(id='histogram', figure=histogram),
    dcc.Graph(id='pie_chart', figure=pie_chart),
    dcc.Graph(id='choropleth_responses', figure=choropleth_responses),
], style={'width': '95%', 'margin': 'auto'})

# Exécuter l'application
if __name__ == '__main__':
    app.run_server(debug=True)
