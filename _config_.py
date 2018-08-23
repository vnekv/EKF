CONN_ELEMENT = 'District' #District #Region
SHOW_EXPLANATIONS = 1
EXPL_RELEVANCY = 3
# 1: only top or bottom level
# 2: only ontology relevancy
# 3: top 3 top and bottom levels and then sort by ontology relevancy
SHOW_ATK = 1
FILTER = 'cons'
RAISE_HIERARCHY = 1 #0 raise level of hierarchy of connecting attribute
ATK_ID = ''
PMML_FILE = 'DM_results/1  Client( )   =} Loan(Bad) .Task.LMWorkspace.pmml' #Region x Loan amount.Task.LMWorkspace.pmml
# DM_results/1  Client( )   =} Loan(Bad) .Task.LMWorkspace.pmml
TKR_FILE = 'EKR/EKR_PROD.db'

#technical settings
proxies = {
  'http': 'proxy.czprg.atrema.deloitte.com:3128',
}