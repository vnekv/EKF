CONN_ELEMENT = 'District' #District #Region
SHOW_EXPLANATIONS = 1
EXPL_RELEVANCY = 3
# 1: only top or bottom level
# 2: only ontology relevancy (top 3 explanations)
# 3: top and bottom levels and then sort by ontology relevancy (top 3 explanations)
OBRC_THRESHOLD = 0.1  # threshold for Ontology based relevancy criterion
SHOW_ATK = 0
FILTER = 'cons'
RAISE_HIERARCHY = 1 #0 raise level of hierarchy of connecting attribute
LEVELS = 'width' #width rank
ATK_ID = ''
PMML_FILE = 'DM_results/1  Client( )   =} Loan(Bad) .Task.LMWorkspace.pmml' #Region x Loan amount.Task.LMWorkspace.pmml
# DM_results/1  Client( )   =} Loan(Bad) .Task.LMWorkspace.pmml
TKR_FILE = 'EKR/EKR_PROD.db'

#technical settings
proxies = {
  'http': 'proxy.czprg.atrema.deloitte.com:3128',
  'https': 'proxy.czprg.atrema.deloitte.com:3128',
}