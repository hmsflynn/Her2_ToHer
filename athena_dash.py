# -*- coding: utf-8 -*-
import dash
from dash.dependencies import Input, Output
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import io
import base64
# Her2_Her
import requests, sys
from ensemblrest import EnsemblRest
import random
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

def rand_pt_genes(standards, mutations, pt_genes):
    brca1_pt = random.choice(brca1)
    pt_genes.append(brca1_pt)
    brca2_pt = random.choice(brca2)
    pt_genes.append(brca2_pt)
    chek2_pt = random.choice(chek2)
    pt_genes.append(chek2_pt)
    pten_pt = random.choice(pten)
    pt_genes.append(pten_pt)
    tp53_pt = random.choice(tp53)
    pt_genes.append(tp53_pt)
    return pt_genes


ensRest = EnsemblRest()


server = "http://rest.ensembl.org"

# standard sequence API data
standards = []
brca1_seq = ensRest.getSequenceById(id='ENSG00000012048')
brca2_seq = ensRest.getSequenceById(id='ENSG00000139618')
chek2_seq = ensRest.getSequenceById(id='ENSG00000183765')
pten_seq = ensRest.getSequenceById(id='ENSG00000171862')
tp53_seq = ensRest.getSequenceById(id='ENSG00000141510')

for i in (brca1_seq, brca2_seq, chek2_seq, pten_seq, tp53_seq):
    standards.append(i['seq'])

#mutation dash_table
mutations = []
brca1_mut = ensRest.getSequenceById(id =  'ENST00000357654?content-type=text/x-fasta;type=cdna')
brca2_mut = ensRest.getSequenceById(id = 'ENST00000380152?content-type=text/x-fasta;type=cdna')
chek2_mut = ensRest.getSequenceById(id = 'ENST00000382580?content-type=text/x-fasta;type=cdna')
pten_mut = ensRest.getSequenceById(id = 'ENST00000371953?content-type=text/x-fasta;type=cdna')
tp53_mut = ensRest.getSequenceById(id = 'ENST00000269305?content-type=text/x-fasta;type=cdna')

for i in (brca1_mut, brca2_mut, chek2_mut, pten_mut, tp53_mut):
    mutations.append(i['seq'])

random.randint(1, 20)
brca1 = [standards[0], mutations[0]]
brca2 = [standards[1], mutations[1]]
chek2 = [standards[2], mutations[2]]
pten = [standards[3], mutations[3]]
tp53 = [standards[4], mutations[4]]


pt_genes = []
pt_genes = rand_pt_genes(standards, mutations, pt_genes)
pt_genes_NaN = []


for i in range(len(pt_genes)):
    x = random.randint(1, 10)
    if x < 7:
        pt_genes_NaN.append('NaN')
    else:
        pt_genes_NaN.append('MUT')


df = pd.read_csv('C:\\Users\\Helen Flynn\\Documents\\GitHub\\Her2_ToHer\\cBioPortal_data (1).txt', sep = '\t' ,names = ('Common', 'BRCA1', 'BRCA2', 'CHEK2', 'PTEN', 'TP53'))
df = df[2:]
id = 'MB-0350'

def return_muts(id):
    target = df.loc[id].notnull()
    return (list(df.columns[target]))


print(return_muts('MB-0062'))

df = df.reset_index()

path = "C:\\Users\\Helen Flynn\\Documents\\Github\\Her2_ToHer\\"

def column_get(mut_name):
    mut_fil = pd.read_csv(path+mut_name+".csv")
    df_1 = mut_fil[['Drug', 'Effect size']]
    return df_1

list_name =["BRCA1","BRCA2"] ## this is the list of mutations present in the data
def calc_col(list_name):
    d = pd.DataFrame(columns = ['Drug', 'Effect size'])
    for x in list_name:
        temp = column_get(x)
        temp = temp.groupby('Drug', as_index=False).mean()
        d= pd.merge(d, temp, how = 'outer', on='Drug')
    d.to_csv(path+"out.csv")

calc_col(list_name)

out=pd.read_csv(path+"out.csv")
out['sum'] = out['Effect size_y'] + out['Effect size']

drug_suggested= out.nsmallest(5,'sum')
drug_harm = out.nlargest(5,'sum')

drug_suggested[['Drug','sum']].to_csv(path+"suggested.csv")
drug_harm[['Drug','sum']].to_csv(path+"harm.csv")

df2 = pd.read_csv('C:\\Users\\Helen Flynn\\Documents\\GitHub\\Her2_ToHer\\suggested.csv')


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H1(children = "HER2her",
    style = {
        'textAlign' : 'center',
        'color' : 'black'
    }
    ),
    dcc.Upload(id='upload-data',
        children=html.Div([
            'Drag and Drop Single Patient Data (.txt or .csv) or ',
            html.A('Select File')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'backgroundColor' : 'pink',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        }),
    dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict("rows"),
        style_table={
            'maxHeight' : '300',
            'overflowY' : 'scroll',
            'border':0,
            'align' : 'center'},
        style_cell_conditional=[{
        'if': {'row_index': 'odd'},
        'backgroundColor': '#FFDFD3'
    }],
    ),
    html.Div([
        html.P("For patients with mutations in the "+str(list_name)+" genes, we recommend the following medicines."
        )
    ]),
    dash_table.DataTable(
        id='medtable',
        columns=[{"name": i, "id": i} for i in df2.columns],
        data=df2.to_dict("rows")
    ),
        html.P('We would like to provide you with an interactive map of available cancer care providers.'
        ),
    html.Iframe(
      width="600",
      height="450",
      style={
        'border':0,
        'padding' : '50px',
       },
      src="https://www.google.com/maps/embed/v1/search?key=AIzaSyACU8QODHAUXs0igLHiqeFgUQaiNPNUGQ0&q=oncology+center"
      )
    ])



# callback table creation
@app.callback(Output('table', 'data'),
              [Input('upload-data', 'contents'),
               Input('upload-data', 'filename')])
def update_output(contents, filename):
    if contents is None:
        print("contents is None")
        df = pd.read_csv(io.StringIO(base64.b64decode(filename).decode('utf-8')), sep='\t', names=('Common', 'BRCA1', 'BRCA2', 'CHEK2', 'PTEN', 'TP53'))
        df=df[2:]
        df=df.reset_index()
        print(df,contents)
        if df is not None:
            print("df is not None")
            return df.to_dict('rows')
        else:
            print("df is None")
            return [{}]
    else:
        print("contents is not None")
        return [{}]

if __name__ == '__main__':
    app.run_server(debug=True)
