CONN_ELEMENT = 'Region'
SHOW_EXPLANATIONS = 1
EXPL_RELEVANCY = 1
# 1: only top or bottom level
# 2: only ontology relevancy
# 3: top 3 top and bottom levels and then sort by ontology relevancy
SHOW_ATK = 0
FILTER = 'contr'
ATK_ID = ''
PMML_FILE = 'DM_results/Region x Loan amount.Task.LMWorkspace.pmml'
TKR_FILE = 'EKR/TKR_PROD.db'

#technical settings
proxies = {
  'http': 'proxy.czprg.atrema.deloitte.com:3128',
}