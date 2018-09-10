import sqlite3
from sqlite3 import Error
import os
import xml.etree.ElementTree as etree
import requests
import pandas as pd
import io
from operator import itemgetter
from _config_ import *


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return None


def get_relevant_atk_formulas(conn, attribute_name):
    """ returns all ATK formulas in the Trusted knowledge repository relevant for the specified attribute
    :param conn: the connection object
    :param attribute_name: attribute for which atk formulas are searched
    """
    att_name = "%" + attribute_name[0].lower() + "%"
    cur = conn.cursor()
    cur.execute("select f.id, m.name, attribute_name, relationship "
                "from atk_formula f join measure m on f.id_measure=m.id "
                "where attribute_name like ?", (att_name,))
    curs = conn.cursor()
    curs.execute("select f.id, m.name, attribute_name, relationship "
                 "from atk_formula f join measure m on f.id_measure=m.id")
    atks_relevant = []
    from_atks = cur.fetchall()
    # if name of the attribute from association rule is the same as the name of the attribute in ATK
    for atk_one in from_atks:
        atks_relevant.append([atk_one[0], atk_one[2], attribute_name, atk_one[1]])
    from_ass = curs.fetchall()
    # if name of the attribute from association rule is contained in the name of the attribute in ATK
    for atk in from_ass:
        if (atk[2]) in attribute_name[0].lower():
            atks_relevant.append([atk[0], atk[2], attribute_name, atk[1]])
    return atks_relevant


def get_possible_assignment_rules(conn, categories=10):
    cur = conn.cursor()
    cur.execute("select id from assignment_rule where categories = ?", (categories,))
    possible_rules = []
    rules = cur.fetchall()
    for rule in rules:
        possible_rules.append(rule[0])
    return possible_rules


def get_association_rules(file):
    pmml_file = os.path.join(os.getcwd(), file)
    tree = etree.parse(pmml_file)
    all_assoc = tree.findall('.//AssociationRule')
    all_rules = []
    for ass in all_assoc:
        id_ass = ass.get('id')
        text_ass = ass.find('Text').text
        ims_values = []
        for im in ass.findall('IMValue'):
            if im.get('imSettingRef'):
                im_values = []
                im_values.append(im.get('name'))
                im_values.append(im.get('type'))
                im_values.append(im.text)
                ims_values.append(im_values)
        DBAslev1 = []
        antecedent = ass.get('antecedent')
        consequent = ass.get('consequent')
        DBAslev1.append(antecedent)
        DBAslev1.append(consequent)
        attributes = []
        literals = []
        categories_rank = []
        for DBAlev1 in DBAslev1:
            for dba in tree.findall('.//DBA'):
                if dba.attrib['id'] == DBAlev1:
                    BARefs1 = dba.findall('BARef')
                    for BARef1 in BARefs1:
                        DBAslev2 = []
                        DBAslev2.append(BARef1.text)
                        for DBAlev2 in DBAslev2:
                            for dba in tree.findall('.//DBA'):
                                if dba.attrib['id'] == DBAlev2:
                                    BARefs2 = dba.findall('BARef')
                                    for BARef2 in BARefs2:
                                        DBAslev3 = [BARef2.text]
                                        for DBAlev3 in DBAslev3:
                                            for dba in tree.findall('.//DBA'):
                                                if dba.attrib['id'] == DBAlev3:
                                                    BARefs3 = dba.findall('BARef')
                                                    for BARef3 in BARefs3:
                                                        BBAs = [BARef3.text]
                                                        for BBA in BBAs:
                                                            for bba in tree.findall('.//BBA'):
                                                                if bba.attrib['id'] == BBA:
                                                                    field_bba = bba.find('FieldRef').text
                                                                    categories_obj = bba.findall('CatRef')
                                                                    categories = []
                                                                    for category in categories_obj:
                                                                        categories.append(category.text)
                                                                    root = tree.getroot()
                                                                    for derived in root.findall('.//{http://www.dmg.org/PMML-4_0}DerivedField'):
                                                                        if derived.attrib['name'] == field_bba:
                                                                            der_categories = derived.findall('{http://www.dmg.org/PMML-4_0}Discretize/{http://www.dmg.org/PMML-4_0}DiscretizeBin')
                                                                            bins = []
                                                                            for bin in der_categories:
                                                                                bin_int = bin.findall('{http://www.dmg.org/PMML-4_0}Interval')
                                                                                bins.append([bin.attrib['binValue'], bin_int[0].attrib['leftMargin'], bin_int[0].attrib['rightMargin']])
                                                                            sorted_bins = sorted(bins, key=lambda bin0: bins[1]) # sort according to left margin
                                                                            sorted_bins_names = []
                                                                            for x in sorted_bins:
                                                                                sorted_bins_names.append(x[0])
                                                                            for category in categories_obj:
                                                                                for sb in sorted_bins_names:
                                                                                    if category.text == sb:
                                                                                        category_rank = sorted_bins_names.index(sb) + 1
                                                                                        categories_rank.append([field_bba, category.text, category_rank])
                                                                            if len(der_categories) == 0:
                                                                                der_categories = derived.findall(
                                                                                    '{http://www.dmg.org/PMML-4_0}MapValues/{http://www.dmg.org/PMML-4_0}InlineTable/{http://www.dmg.org/PMML-4_0}row')
                                                                            categories_no = len(der_categories)
                                                                    literal = [field_bba, categories]
                                                                    literals.append(literal)
                                                                    att_cat_no = [field_bba, categories_no]
                                                                    attributes.append(att_cat_no)
        assoc_rule = {
            'id': id_ass,
            'text': text_ass,
            'attributes': attributes,
            'literals': literals,
            'categories_rank': categories_rank,
            'ims': ims_values
        }
        all_rules.append(assoc_rule)
    return all_rules


def get_level(conn, id_assig_rule, ranks):
    conn.row_factory = sqlite3.Row
    levels = []
    level_name = ''
    level_fin = ''
    if id_assig_rule in (1, 3):
        cur = conn.cursor()
        cur.execute("select a.id, sort, categories, top_bottom_categories, categories_per_level, l.name, cnt "
                    "from assignment_rule a join level_group lg on a.id_level_group=lg.id "
                    "join level l on lg.id=l.id_level_group "
                    "where a.id = ? order by sort", (id_assig_rule,))
        rows = cur.fetchall()
        for rank in ranks:
            for row in rows:
                if rank <= row["sort"] * row["categories_per_level"]:
                    level_name = row["name"]
                    levels.append(level_name)
                    break
    if id_assig_rule == 2:
        lowest_lev = 12
        highest_lev = 3
        for rank in ranks:
            if rank > lowest_lev:
                level_name = 'very low'
            elif rank == lowest_lev:
                level_name = 'very low / low'
            elif rank < highest_lev:
                level_name = 'very high'
            elif rank == highest_lev:
                level_name = 'very high / high'
            elif rank in (4, 5):
                level_name = 'high'
            elif rank == 6:
                level_name = 'high / medium'
            elif rank in (7, 8):
                level_name = 'medium'
            elif rank == 9:
                level_name = 'medium / low'
            elif rank in (10, 11):
                level_name = 'low'
            levels.append(level_name)
    if id_assig_rule == 4:
        for rank in ranks:
            if rank  == 1:
                level_name = 'very high'
            elif rank  == 2:
                level_name = 'medium'
            elif rank == 3:
                level_name = 'very low'
            levels.append(level_name)
    if len(levels) == 1:
        level_fin = levels[0]
    else:
        for i in range(1, len(levels)):
            if levels[i-1] == levels[i]:
                i += 1
            else:
                level_fin = 'X'
                break
            if i == len(levels):
                level_fin = levels[0]
    return level_fin


def get_conn_rank(conn, cv_name, ca_name):
    if LEVELS == 'rank':
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("select measure_rank, d.id_measure  "
                    "from  data d "
                    "join conn_element_value cv on d.id_conn_element_value=cv.id "
                    "join conn_element c on cv.id_conn_element=c.id "
                    "where cv.name = ? and c.name = ? ", (cv_name, ca_name))
        rows = cur.fetchall()
    if LEVELS == 'width':
        sql = "select d.id_measure, measure_value, cv.name " \
              "from data d join conn_element_value cv on d.id_conn_element_value=cv.id " \
              "join conn_element c on cv.id_conn_element=c.id " \
              "join measure m on d.id_measure = m.id " \
              "where c.name = ? "
        df = pd.read_sql(sql, conn, params={ca_name})
        series = df.groupby('id_measure')['measure_value'].transform(
            lambda x: pd.cut(x, bins=5, labels=["5", "4", "3", "2", "1"]))
        df3 = df.merge(series.to_frame(), left_index=True, right_index=True)
        df4 = df3[df3.name == cv_name]
        df4 = df4.loc[:, ['measure_value_y', 'id_measure']]
        rows = df4.values.tolist()
    return rows


def apply_atk_formula(conn, atk_id=1, level_atr='very low', level_measure='low / very low'):
    cur = conn.cursor()
    cur.execute("select f.id, m.name, attribute_name, relationship "
                "from atk_formula f join measure m on f.id_measure=m.id "
                "where f.id = ?", (atk_id,))
    one = cur.fetchone()
    cons = 0
    contr = 0
    levels_measure = level_measure.split('/')  # strip
    levels_attribute = level_atr.split('/')  # strip
    if one[3] == 'direct_prop':

        for level_measure in levels_measure:
            for level_attribute in levels_attribute:
                if level_measure == level_attribute:
                    cons = 1
                if (level_measure == 'very low' and  level_attribute == 'very high') \
                        or (level_measure == 'low' and level_attribute == 'high') \
                        or (level_measure == 'very high' and  level_attribute == 'very low') \
                        or (level_measure == 'high' and  level_attribute == 'low'):
                    contr = 1
        applied_atk = {
            "id": one[0],
            "attribute": one[2],
            "relationship": one[3],
            "measure": one[1],
            "consequence": cons,
            "contradiction": contr
        }
    if one[3] == 'indirect_prop':
        for level_measure in levels_measure:
            for level_attribute in levels_attribute:
                if level_measure == level_attribute:
                    contr = 1
                if (level_measure == 'very low' and level_attribute == 'very high') \
                        or (level_measure == 'low' and level_attribute == 'high') \
                        or (level_measure == 'very high' and level_attribute == 'very low') \
                        or (level_measure == 'high' and level_attribute == 'low'):
                    cons = 1
        applied_atk = {
            "id": one[0],
            "attribute": one[2],
            "relationship": one[3],
            "measure": one[1],
            "consequence": cons,
            "contradiction": contr
            }
    return applied_atk


def get_distinct_atks(used_atks):
    used_atks_distinct = []
    try:
        used_atks_distinct.append(used_atks[0])  # take the first atk to enable comparison
        for i in range(1, len(used_atks) - 1):
            for uad in used_atks_distinct:
                if uad['id'] != used_atks[i]['id']:
                    used_atks_distinct.append(used_atks[i])
    except IndexError:
        used_atks_distinct = []
    return used_atks_distinct


def get_top_bottom_level_names(conn, assig_rule):
    cur = conn.cursor()
    cur.execute("select l.name "
                "from assignment_rule a join level_group lg on a.id_level_group=lg.id "
                "join level l on l.id_level_group=lg.id "
                "where a.id=? and (l.sort=cnt or l.sort=1) ", (assig_rule,))
    tb_levs = cur.fetchall()  # get top and bottom level names
    return tb_levs


def construct_explanation(explanation, conn_level, onto_cnt=''):
    expl = []
    expl.append(explanation[0])
    expl.append(conn_level)
    expl.append(explanation[1])
    expl.append(explanation[2])
    if onto_cnt != '':
        expl.append(onto_cnt)
    return expl


def get_explanations(conn, cv_name, ranks, ca_name, assig_rule=2):
    if LEVELS == 'rank':
        assig_rule = 2
    if LEVELS == 'width':
        assig_rule = 3
    explanations = []
    for tb_lev in get_top_bottom_level_names(conn, assig_rule):
        for row in ranks:
            conn_level=get_level(conn, assig_rule, [row[0], ])
            if tb_lev[0] == conn_level:
                cu = conn.cursor()
                cu.execute("select cv.name, m.name, measure_value "
                           "from conn_element_value cv join data d on d.id_conn_element_value=cv.id "
                           "join measure m on d.id_measure=m.id "
                           "join conn_element c on cv.id_conn_element=c.id "
                           "where cv.name = ? and c.name = ? and d.id_measure = ? ", (cv_name, ca_name, row[1]))
                db_explanations = cu.fetchall()
                for db_explanation in db_explanations:
                    t = construct_explanation(db_explanation, conn_level)
                explanations.append(t)
    return explanations[:3]


def get_storage_codes(session, word, collection='all2'):
    url = "https://owl.vse.cz/OOSPservices/api/v1/search3?word=" + word + "&collection=" + collection + \
          "&comparator=token&entities=7&scope=15"
    if proxies:
        r = session.get(url, proxies=proxies)
    else:
        r = session.get(url)
    if r.status_code == 201:
        try:
            s = r.content
            data = pd.read_csv(io.StringIO(s.decode('ISO-8859-1')), sep=',', skiprows=1,
                               usecols=['#storage_code', 'URL', 'IRI', 'resource'])
            storage_codes = data['#storage_code'].tolist()
        except pd.errors.EmptyDataError:  # in case no ontologies found
            storage_codes = []
        return storage_codes


def get_onto_expl_list(db_explanations, conn_level, att_names):
    with requests.Session() as session:
        onto_expl_list = []
        for db_explanation in db_explanations:
            obrc_all = []  # all single OBRC (for each attribute)
            m = get_storage_codes(session, db_explanation[1])  # hits for measure
            for att in att_names:
                if att[0] == 'Loan_amount':
                    a = get_storage_codes(session, 'loan')
                    g = set(m).intersection(a)
                    try:
                        obrc_single = len(g) / len(a)
                    except ZeroDivisionError:
                        obrc_single = 0
                    obrc_all.append(obrc_single)
                if att[0] != CONN_ELEMENT and att[0] != 'Loan_amount': #conn element changed?
                    a = get_storage_codes(session, att[0])  # hits for attribute
                    g = set(m).intersection(a)
                    try:
                        obrc_single = len(g) / len(a)
                    except ZeroDivisionError:
                        obrc_single = 0
                    obrc_all.append(obrc_single)
            try:
                obrc_final = sum(obrc_all) / len(obrc_all)
            except ZeroDivisionError:
                obrc_final = 0
            expl = construct_explanation(db_explanation, conn_level, obrc_final)
        onto_expl_list.append(expl)
    return onto_expl_list


def get_ontology_explanations(conn, cv_name, ranks, att_names, ca_name, assig_rule=2):
    sorted_list = []
    temp_list = []
    e_list = []
    if LEVELS == 'rank':
        assig_rule = 2
    if LEVELS == 'width':
        assig_rule = 3
    if EXPL_RELEVANCY == 2:  # only ontology relevancy
        cu = conn.cursor()
        for row in ranks:
            conn_level=get_level(conn, assig_rule, [row[0], ])
            cu.execute("select cv.name, m.name, measure_value "
                       "from conn_element_value cv join data d on d.id_conn_element_value=cv.id "
                       "join measure m on d.id_measure=m.id "
                       "join conn_element c on cv.id_conn_element=c.id "
                       "where cv.name = ? and c.name = ? and d.id_measure = ? ", (cv_name, ca_name, row[1]))
            db_explanations = cu.fetchall()  # all measures for selected connection element and connection value
            onto_expl_list = get_onto_expl_list(db_explanations, conn_level, att_names)
            temp_list.append(onto_expl_list)
        for ex in temp_list:
            for e in ex:
                a = tuple(e)
                e_list.append(a)
    if EXPL_RELEVANCY == 3:  # top and bottom levels and then sort by ontology relevancy
        for tb_lev in get_top_bottom_level_names(conn, assig_rule):
            for row in ranks:
                conn_level = get_level(conn, assig_rule, [row[0], ])
                if tb_lev[0] == conn_level:
                    cu = conn.cursor()
                    cu.execute("select cv.name, m.name, measure_value "
                               "from conn_element_value cv join data d on d.id_conn_element_value=cv.id "
                               "join measure m on d.id_measure=m.id "
                               "join conn_element c on cv.id_conn_element=c.id "
                               "where cv.name = ? and c.name = ? and d.id_measure = ? ", (cv_name, ca_name, row[1]))
                    db_explanations = cu.fetchall()
                    onto_expl_list = get_onto_expl_list(db_explanations, conn_level, att_names)
                    temp_list.append(onto_expl_list)
        for ex in temp_list:
            for e in ex:
                a = tuple(e)
                e_list.append(a)
    if OBRC_THRESHOLD > 0:
        for it in e_list:
            if it[4] >= OBRC_THRESHOLD:
                sorted_list.append(it)
    sorted_list = sorted(sorted_list, key=itemgetter(4), reverse=True)
    return sorted_list[:3]


def filter_rules(filter, assoc_rule, atk_id=''):
    hit = 0
    atk_out = []
    if 'atks' in assoc_rule:
        try:
            if len(assoc_rule['atks']) == 0 and filter == 'no_cons':  # special treatment for no relevant atks for rules -> show all rules
                atk_out.append('no_cons')
                hit += 1
        except KeyError:
            if filter == 'no_cons':
                atk_out.append('no_cons')
                hit += 1
        if atk_id == '':
            for a in assoc_rule['atks']:
                if filter == 'cons':
                    if a['consequence'] == 1:
                        atk_out.append(a)
                        hit += 1
                if filter == 'contr':
                    if a['contradiction'] == 1:
                        atk_out.append(a)
                        hit += 1
                if filter == 'no_cons':
                    if a['consequence'] == 0:
                        atk_out.append(a)
                        hit += 1
        else:
            for a in assoc_rule['atks']:
                if atk_id == a['id']:
                    if filter == 'cons':
                        if a['consequence'] == 1:
                            atk_out.append(a)
                            hit += 1
                    if filter == 'contr':
                        if a['contradiction'] == 1:
                            atk_out.append(a)
                            hit += 1
                    if filter == 'no_cons':
                        if a['consequence'] == 0:
                            atk_out.append(a)
                            hit += 1
    if hit == 0:
        pass
    if hit > 0:
        out = [assoc_rule]
        out.append(atk_out)
        return out


def print_explanations(rule):
    print('--------------------------------')
    print('EXPLANATIONS FOUND FOR THIS RULE:')
    # if len(rule['explanations']) == 0:
    #     print('No explanation found for this rule')
    # else:
    try:
        len(rule['explanations']) == 0
        i = 1
        for e in rule['explanations']:
            print('--- Explanation', i, '---')
            print('Connecting attribute name:', CONN_ELEMENT)
            for literal in rule["literals"]:
                if literal[0] == CONN_ELEMENT:
                    conn_value = literal[1][0]
                    print('Connecting attribute value:', conn_value)
            if RAISE_HIERARCHY == 1:
                print('Used parent connecting attribute: Region')
                print('Used parent connecting attribute value: ', e[0])
            print('Measure:', e[2])
            print('Level of the measure:', e[1])
            print('Value of the measure:', e[3])
            try:
                t = e[4]
                print('Ontology relevancy: '+'{:.2%}'.format(t))
            except IndexError:
                pass
            i += 1
    except KeyError:
        print('No explanation found for this rule')
    pass


def print_plain_rule(rule):
    print('--- RULE ID ', rule['id'], '---')
    print(rule['text'])
    for im in rule['ims']:
        print('Interest measure: ' + im[0] + ', type: ' + im[1] + ', value: ' + im[2])
    pass


def change_conn_att_hierarchy(conn, conn_lower='Praha'):
    cu = conn.cursor()
    cu.execute("select cv_high.name, ce.name "
               "from conn_element_value cv_low "
               "join conn_element_value cv_high on cv_low.id_parent_value = cv_high.id "
               "join conn_element ce on cv_high.id_conn_element=ce.id "
               "where cv_low.name=? ", (conn_lower,))
    conn_higher = cu.fetchone()
    return conn_higher


def main():
    database = os.path.join(os.getcwd(), TKR_FILE)
    conn = create_connection(database)  # create a database connection
    with conn:
        assoc_rules = get_association_rules(PMML_FILE)     # path to the PMML file
        used_atks = []
        for assoc_rule in assoc_rules:
            print(assoc_rule['text'])
            atks_res = []
            print('assoc_rule[attributes]', assoc_rule['attributes'])
            print('assoc rule 0',assoc_rule['attributes'][0])
            #print('join',' '.join(assoc_rule['attributes']))
            if CONN_ELEMENT not in assoc_rule['text']:
                print('No connecting attribute detected for association rule:', assoc_rule['text'])
                continue
            for att in assoc_rule['attributes']:
                print('CONN_ELEMENT', CONN_ELEMENT)
                print('att[0]',att[0])
                if att[0] == CONN_ELEMENT:
                    for lit in assoc_rule['literals']:
                        if lit[0] == CONN_ELEMENT:
                            conn_value = lit[1][0]
                            if RAISE_HIERARCHY == 1:
                                conn_value, conn_element_changed = change_conn_att_hierarchy(conn,conn_value)
                                conn_ranks = get_conn_rank(conn, conn_value, conn_element_changed)
                            if RAISE_HIERARCHY == 0:
                                conn_ranks = get_conn_rank(conn, conn_value, CONN_ELEMENT)
                            if SHOW_EXPLANATIONS:
                                if RAISE_HIERARCHY == 0:
                                    if EXPL_RELEVANCY == 1:
                                        explanations = get_explanations(conn, conn_value, conn_ranks, CONN_ELEMENT)
                                        assoc_rule.update({'explanations': explanations})
                                    if EXPL_RELEVANCY in (2, 3):
                                        explanations = get_ontology_explanations(conn, conn_value, conn_ranks, assoc_rule['attributes'], CONN_ELEMENT)
                                        assoc_rule.update({'explanations': explanations})
                                if RAISE_HIERARCHY == 1:
                                    if EXPL_RELEVANCY == 1:
                                        explanations = get_explanations(conn, conn_value, conn_ranks, conn_element_changed)
                                        assoc_rule.update({'explanations': explanations})
                                    if EXPL_RELEVANCY in (2, 3):
                                        explanations = get_ontology_explanations(conn, conn_value, conn_ranks,
                                                                                 assoc_rule['attributes'],
                                                                                 conn_element_changed)
                                        assoc_rule.update({'explanations': explanations})

            if SHOW_ATK:
                for att in assoc_rule['attributes']:
                    if get_relevant_atk_formulas(conn, att):
                        for atk in get_relevant_atk_formulas(conn, att):
                            possible_assig_rules = get_possible_assignment_rules(conn, att[1])
                            att_ranks = []
                            for category in assoc_rule['categories_rank']:
                                if category[0] == att[0]:
                                    att_ranks.append(category[2])
                            atr_level = get_level(conn, possible_assig_rules[0], att_ranks)
                            conn_level = get_level(conn, 2, [conn_ranks[0][0], ])
                            atk_res = apply_atk_formula(conn, atk[0], atr_level, conn_level)
                            atks_res.append(atk_res)
                            used_atks.append(atk_res)
            if SHOW_ATK:
                assoc_rule.update({'atks': atks_res})
        if SHOW_ATK:
            filtered_rules = []
            for a_rule in assoc_rules:
                fil_rule = filter_rules(FILTER, a_rule, ATK_ID)
                if fil_rule:
                    filtered_rules.append(fil_rule)
            used_atks_dist = get_distinct_atks(used_atks)
            print('RELEVANT ATK FORMULAS:')
            for a in used_atks_dist:
                print('id:', a['id'], ', attribute:', a['attribute'], ', relationship:', a['relationship'], ', measure:', a['measure'])
        if not SHOW_ATK:
            for a in assoc_rules:
                print_plain_rule(a)
                if SHOW_EXPLANATIONS:
                    print_explanations(a)
                print('-------------------------------------------------')
        if SHOW_ATK:
            if len(filtered_rules) > 0:
                print('--------------------------------')
                print('FILTERED RULES:')
                for a in filtered_rules:
                    print_plain_rule(a[0])
                    if FILTER == 'no_cons' and atk_id == '':
                        print('Rule is not a consequence of any ATK formula')
                    else:
                        for atk in a[1]:
                            print('Rule is ', FILTER, ' of the ATK formula: ', '\n'
                                                                               'attribute: ', atk['attribute'], ', relationship: ', atk['relationship'], ', measure: ', atk['measure'])
                    if SHOW_EXPLANATIONS:
                        print_explanations(a[0])
                    print('---------------------------------------------')
            else:
                print('No filtered rules match')


if __name__ == '__main__':
    main()
