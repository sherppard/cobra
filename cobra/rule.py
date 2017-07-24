# -*- coding: utf-8 -*-

"""
    rule
    ~~~~

    Implements rule(languages/frameworks/vulnerabilities/rules)

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
import os
from .config import rules_path
from .log import logger
from .utils import to_bool
from xml.etree import ElementTree


def block(index):
    default_index_reverse = 'in-function'
    default_index = 0
    blocks = {
        'in-function-up': 0,
        'in-function-down': 1,
        'in-current-line': 2,
        'in-function': 3,
        'in-class': 4,
        'in-class-up': 5,
        'in-class-down': 6,
        'in-file': 7,
        'in-file-up': 8,
        'in-file-down': 9
    }
    if isinstance(index, int):
        blocks_reverse = dict((v, k) for k, v in blocks.iteritems())
        if index in blocks_reverse:
            return blocks_reverse[index]
        else:
            return default_index_reverse
    else:
        if index in blocks:
            return blocks[index]
        else:
            return default_index


class Rule(object):
    def __init__(self):
        self.rules_path = rules_path

    @property
    def languages(self):
        """
        Get all languages
        :return:
        {
            'php':{
                'chiefly': 'true',
                'extensions':[
                    '.php',
                    '.php3',
                    '.php4',
                    '.php5'
                ]
            }
        }
        """
        language_extensions = {}
        xml_languages = self._read_xml('languages.xml')
        if xml_languages is None:
            logger.critical('languages read failed!!!')
            return None
        for language in xml_languages:
            l_name = language.get('name').lower()
            l_chiefly = 'false'
            if language.get('chiefly') is not None:
                l_chiefly = language.get('chiefly')
            language_extensions[l_name] = {
                'chiefly': l_chiefly,
                'extensions': []
            }
            for lang in language:
                l_ext = lang.get('value').lower()
                language_extensions[l_name]['extensions'].append(l_ext)
        return language_extensions

    @property
    def frameworks(self):
        """
        Read all framework rules
        :return: dict
        """
        frameworks_rules = {}
        xml_frameworks = self._read_xml('frameworks.xml')
        if xml_frameworks is None:
            logger.critical('frameworks read failed!!!')
            return None
        for framework in xml_frameworks:
            f_name = framework.get('name').lower()
            f_lang = framework.get('language').lower()
            f_code = framework.get('code')
            framework_info = {
                f_name: {
                    'code': f_code,
                    'rules': []
                }
            }
            frameworks_rules[f_lang] = framework_info
            for rule in framework:
                rule_info = {rule.tag: rule.get('value')}
                frameworks_rules[f_lang][f_name]['rules'].append(rule_info)
        return frameworks_rules

    @property
    def vulnerabilities(self):
        """
        Read all vulnerabilities information
        :return:
        """
        vulnerabilities_info = {}
        xml_vulnerabilities = self._read_xml('vulnerabilities.xml')
        if xml_vulnerabilities is None:
            logger.critical('vulnerabilities read failed!!!')
            return None
        for vulnerability in xml_vulnerabilities:
            v_id = int(vulnerability.get('vid'))
            v_name = vulnerability.get('name').lower()
            v_level = int(vulnerability.get('level'))
            v_description = vulnerability[0].text.strip()
            v_repair = vulnerability[1].text.strip()
            vulnerabilities_info[str(v_id)] = {
                'name': v_name,
                'description': v_description,
                'level': v_level,
                'repair': v_repair,
            }
        return vulnerabilities_info

    @property
    def rules(self):
        """
        Get all rules
        :return: dict
        """
        vulnerabilities = []
        for vulnerability_name in os.listdir(self.rules_path):
            v_path = os.path.join(self.rules_path, vulnerability_name)
            if os.path.isfile(v_path) is not True or 'cvi-template' in v_path.lower():
                continue
            if 'cvi' not in v_path.lower() or '.xml' not in v_path.lower():
                logger.debug('Not rule file {f}'.format(f=v_path))
                continue

            # rule information
            rule_info = {
                'name': None,
                'file': v_path,
                'label': None,
                'language': None,
                'match': None,
                'match2': None,
                'match2-block': None,
                'repair': None,
                'repair-block': None,
                'test': {
                    'true': [],
                    'false': []
                },
                'status': False,
                'author': None
            }
            xml_rule = self._read_xml(v_path)
            if xml_rule is None:
                logger.critical('rule read failed!!! ({file})'.format(file=v_path))
                continue
            cvi = v_path.lower().split('cvi-')[1][:3]
            rule_info['label'] = cvi
            for x in xml_rule:
                if x.tag == 'name':
                    rule_info['name'] = x.get('value')
                if x.tag == 'language':
                    rule_info['language'] = x.get('value')
                if x.tag == 'status':
                    rule_info['status'] = to_bool(x.get('value'))
                if x.tag == 'author':
                    name = x.get('name')
                    email = x.get('email')
                    rule_info['author'] = '{name}<{email}>'.format(name=name, email=email)
                if x.tag in ['match', 'match2', 'repair']:
                    rule_info[x.tag] = x.text.strip()
                    if x.tag == 'repair':
                        rule_info['repair-block'] = block(x.get('block'))
                    elif x.tag == 'match2':
                        rule_info['match2-block'] = block(x.get('block'))
                if x.tag == 'test':
                    for case in x:
                        case_ret = case.get('assert').lower()
                        case_test = case.text.strip()
                        if case_ret in ['true', 'false']:
                            rule_info['test'][case_ret].append(case_test)
            vulnerabilities.append(rule_info)
        return vulnerabilities

    def _read_xml(self, filename):
        """
        Read XML
        :param filename:
        :return:
        """
        path = os.path.join(self.rules_path, filename)
        try:
            tree = ElementTree.parse(path)
            return tree.getroot()
        except Exception as e:
            logger.warning('parse xml failed ({file})'.format(file=path))
            return None
