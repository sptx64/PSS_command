import streamlit as st
import pandas as pd
import numpy as np
from streamlit_extras.metric_cards import style_metric_cards


"# Facture PSS"

"### 🏄‍ COMMANDE"
list_riders = ["Flo","Jerome", "Pierric", "Vincent"]
col1,col2,col3 = st.columns(3)
riders = col1.multiselect("Selectionner les acheteurs", list_riders)
nb_articles = col2.number_input("Nombre d'articles",1,50,1)

cfp_eur_conv = 119

""
"---"
""
"### 🚲 DETAIL COMMANDE"

if len(riders)>0 :
	prix_eur_xfp = st.radio("Prix des articles en euros ou xfp ?", ["EUR", "CFP"])
	""
	""
	col1,col2,col3 = st.columns(3)
	
	list_articles=[]
	list_propr=[]
	list_prix=[]

	for i in range(nb_articles) :
		article = col1.text_input(f"Article {i+1}", "Veste Leatt Gravity")
		proprietaire = col2.selectbox(f"Acheteur article {i+1}", riders)
		prix = col3.number_input(f"Prix article {i+1} ({prix_eur_xfp})", 0.00, 100000.00, 0.00)
		prix = prix if prix_eur_xfp == "CFP" else prix*cfp_eur_conv
		
		list_articles.append(article)
		list_propr.append(proprietaire)
		list_prix.append(prix)

	col1.write("")
	col1.write("")

	fdp = col1.number_input(f"Frais de port ({prix_eur_xfp})", 0.00, 100000.00, 0.00)
	
	""
	""

	fdp = fdp if prix_eur_xfp == "CFP" else fdp*cfp_eur_conv
	total_prix = sum(list_prix) + fdp

	col1,col2,col3=st.columns(3)
	col1.metric("Total commande (CFP)", total_prix)
	col2.metric("Total commande (EUR)", total_prix/cfp_eur_conv)
	col3.metric("Taux de change", cfp_eur_conv)

	style_metric_cards()

	"---"

	"### 👮‍ DOUANE"
	col1,col2,col3=st.columns(3)
	fixe_douane = col1.number_input("Fixe douane (CFP)", 0.00, 100000.00, 0.00)
	frais_douane = col2.number_input("Frais douane (CFP)", 0.00, 100000.00, 0.00)


	df = pd.DataFrame({"Article":list_articles+["Frais de port"], "Proprietaire":list_propr+["Tous"], "Prix CFP":list_prix+[fdp]})
	df["Fixe douane"] = fixe_douane/len(df)
	df["Frais douane"] = frais_douane * df["Prix CFP"]/(df["Prix CFP"].sum())
	df["Prix + douane"] = df["Prix CFP"] + df["Frais douane"] + df["Fixe douane"]
	df["Prix + douane + fdp"] = df["Prix + douane"] + float(df["Prix + douane"].iloc[-1])/(len(df)-1)
	df.loc[df["Article"] == "Frais de port", "Prix + douane + fdp"] = 0


	df_grp = df[df["Proprietaire"]!="Tous"].groupby(["Proprietaire"]).sum(numeric_only=True).reset_index()
	df_grp_prop, df_grp_pdf = df_grp["Proprietaire"].to_numpy(), df_grp["Prix + douane + fdp"].to_numpy()


	def convert_df(df):
		return df.to_csv(sep=";", index=False).encode('ISO-8859-1')

	csv = convert_df(df)
	full_command = st.download_button("Télécharger récapitulatif commande", data=csv, file_name=f'full_command.csv', mime='text/csv')





	"---"

	"### 💳 TOTAL"
	if len(df_grp_prop) == 4 :
		col1, col2, col3, col4 = st.columns(4)
		list_col = [col1,col2,col3,col4]
	elif len(df_grp_prop) == 3 :
		col1, col2, col3 = st.columns(3)
		list_col = [col1,col2,col3]
	elif len(df_grp_prop) == 2 :
		col1, col2, col3 = st.columns(2)
		list_col = [col1,col2]
	elif len(df_grp_prop) == 1 :
		list_col = [st]

	for i in range(len(df_grp_prop)) :
		list_col[i].metric(df_grp_prop[i]+ " (CFP)", np.round(df_grp_pdf[i], 2))

	csv2 = convert_df(df_grp[["Proprietaire", "Prix + douane + fdp"]])
	recap_command = st.download_button("Télécharger somme commande", data=csv2, file_name=f'recap_frais_command.csv', mime='text/csv')