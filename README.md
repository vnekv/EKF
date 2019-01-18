# EKF
External Knowledge Framework
----------------------------
Parameter in code |	Parameter name |	Description
--- | --- | ---
CONN_ATTRIBUTE |	Connecting Attribute |	Name of the Connecting Attribute
SHOW_EXPLANATIONS |	Show Explanations |	1 = YES, 0 = NO
EXPL_RELEVANCY |	Relevancy Criterion for Explanations |	1 = only TOP/BOTTOM; 2 = only OBRC; 3 = TOP/BOTTOM and sort by OBRC
OBRC_THRESHOLD	| Threshold for Ontology Based Relevancy Criterion |	Threshold for considering an Explanation to be relevant according to OBRC
SHOW_SEI | Rule filtering according to SEI-formulas	| 1 = YES, 0 = NO
FILTER	| Filter used for filtering the rules, when SHOW_SEI = 1 |	cons = filter consequences, contr = filter contradictions, no_cons = filter rules which are not consequences
RAISE_HIERARCHY	| Raise level of hierarchy of Connecting Attribute |	1 = YES, 0 = NO.   Whether the Connecting Attribute categories should be mapped on the higher level in the hierarchy. For example, the Districts (lower in the hierarchy) are mapped to the Regions (higher in the hierarchy)
CONN_LEVEL	| Approach used for creating levels for the Connecting Attribute	| rank = Rank-based levels, width = Equal-width levels
LEVELS	| Number of Levels used in the EKF	| 3 = low, medium, high   5 = very low, low, medium, high, very high
SEI_ID	| ID of the SEI-formula 	| ID of the SEI-formula which should be used for rules’ filtering
PMML_FILE |	PMML file with the resulting association rules |	The relative path to the PMML file with the results of a data mining task from the LISp-Miner System
EKR_FILE |	File with the External Knowledge Repository	| The relative path to the SQLite database which contains EKR-related data

The first parameter CON_ATTRIBUTE contains the name of Connecting Attribute. According to this parameter, the resulting association rules are searched to find the Connecting Attribute category. Parameter SHOW_EXPLANATIONS indicates whether the user wants to get Explanations for the resulting rules. EXPL_RELEVANCY indicates, which relevancy criterion RC should be used for explanations. SHOW_SEI indicates whether the user wants to use the SEI-formulas or not. Parameter FILTER indicates, which way of applying SEI-formulas will be used (consequences, no consequences, contradictions).
RAISE_HIERARCHY indicates, whether the need is to raise hierarchy of Connecting Attribute, that is if the Connecting Attribute categories should be mapped on the higher level in the hierarchy. This proves to be helpful in case there are Resulting Patterns with more detailed Connecting Attribute (Districts), but only External Knowledge on the higher level of detail (Regions) is available. Parameter CONN_LEVEL determines, which approach of creating Levels is used (RB approach or EW approach). The Expert-based approach is not supported in the implementation. If parameter SEI_ID is not blank, only the specified SEI_ID is taken into consideration when applying consequences or contradictions. Parameters PMML_FILE and EKR_FILE contains relative paths to the resulting association rules (PMML_FILE) and EKR database (EKR_FILE).
