# EKF
External Knowledge Framework
----------------------------
Parameter in code |	Parameter name |	Description
--- | --- | ---
CONN_ATTRIBUTE |	Connecting Attribute |	Name of the Connecting Attribute
--- | --- | ---
SHOW_EXPLANATIONS |	Show Explanations |	1 = YES, 0 = NO
--- | --- | ---
EXPL_RELEVANCY |	Relevancy Criterion for Explanations |	1 = only TOP/BOTTOM; 2 = only OBRC; 3 = TOP/BOTTOM and sort by OBRC
--- | --- | ---
OBRC_THRESHOLD	Threshold for Ontology Based Relevancy Criterion	Threshold for considering an Explanation to be relevant according to OBRC
--- | --- | ---
SHOW_SEI	Rule filtering according to SEI-formulas	1 = YES, 0 = NO
--- | --- | ---
FILTER	Filter used for filtering the rules, when SHOW_SEI = 1	cons = filter consequences, contr = filter contradictions, no_cons = filter rules which are not consequences
--- | --- | ---
RAISE_HIERARCHY	Raise level of hierarchy of Connecting Attribute	1 = YES, 0 = NO
Whether the Connecting Attribute categories should be mapped on the higher level in the hierarchy. For example, the Districts (lower in the hierarchy) are mapped to the Regions (higher in the hierarchy)
--- | --- | ---
CONN_LEVEL	Approach used for creating levels for the Connecting Attribute	rank = Rank-based levels, width = Equal-width levels
--- | --- | ---
LEVELS	Number of Levels used in the EKF	3 = low, medium, high   5 = very low, low, medium, high, very high
--- | --- | ---
SEI_ID	ID of the SEI-formula 	ID of the SEI-formula which should be used for rules’ filtering
--- | --- | ---
PMML_FILE	PMML file with the resulting association rules 	The relative path to the PMML file with the results of a data mining task from the LISp-Miner System
--- | --- | ---
EKR_FILE	File with the External Knowledge Repository	The relative path to the SQLite database which contains EKR-related data
