# Author = 'Vincent FUNG'
# Create = '2017/10/19'
import re

from jira import JIRA
from jira import JIRAError


class JIRAHandler(object):
    def __init__(self):
        super(JIRAHandler, self).__init__()
        self.jira_addr = 'http://192.168.1.107:8080'
        self.acc = 'CrashParser'
        self.acc_pwd = 'qwer1234'
        self.jira = JIRA(self.jira_addr, basic_auth=(self.acc, self.acc_pwd))

    def create(self, pjname, priority, summary, environment, description, version):
        try:
            return self.jira.create_issue(
                fields=self.gen_fields_dict(
                    pjname, priority, summary, environment, description, version
                )
            )
        except JIRAError as jira:
            return jira.text

    def gen_fields_dict(self, pjname, priority, summary, environment, description, version):
        issue_dict = {
            'project': self.project(pjname),
            'issuetype': {'name': 'bug', 'id': '1'},
            'customfield_10004': self.customfield_10004(),  # 问题归属
            'customfield_10003': self.customfield_10003(),  # bug分类
            'summary': summary,
            'versions': self.version(version),
            'customfield_10002': {'id': '10014', 'child': {'id': '10018'}},  # 严重程度, A-崩溃
            'priority': self.priority(priority),
            'assignee': {'name': 'zhaoyefeng'},
            'environment': environment,
            'description': description,
        }

        return issue_dict

    def udpate_exist_issue(self, jira_id, desc, vers):
        issue = self.read_issue(jira_id)
        issue.fields.description(desc)
        if vers:
            issue.fields.versions(vers)

    def project(self, value):
        method_name = 'project_' + str(value).lower()
        method = getattr(self, method_name)
        return method()

    def project_wegamers(self):
        return {'id': '10400'}

    def project_welive(self):
        return {'id': '10500'}

    def project_messenger(self):
        return {'id': '10200'}

    def project_sa(self):
        return {'id': '10100'}

    def customfield_10004(self):
        return {'id': '10068'}

    def customfield_10003(self):
        return {'id': '10029'}

    def priority(self, value):
        method_name = 'priority_' + str(value).lower()
        method = getattr(self, method_name)
        return method()

    def priority_urgen(self):
        return {'id': '1'}

    def priority_normal(self):
        return {'id': '3'}

    def priority_later(self):
        return {'id': '4'}

    def version(self, value):
        versions = list()
        if isinstance(value, list):
            for i in value:
                versions.append({
                    'name': i
                })
        else:
            versions.append({
                'name': value
            })
        return versions

    def read_issue(self, jira_id):
        return self.jira.issue(jira_id)

    def update_issue(self, issue, version=False, summary=False):
        if version and summary:
            self.version(version)
            return issue.update(fields={'versions': self.version(version), 'summary': summary})
        elif version and not summary:
            return issue.update(fields={'versions': self.version(version)})
        elif summary and not version:
            return issue.update(fields={'summary': summary})

    def read_project_versions(self, project):
        _temp_l = list()
        for vert in self.jira.project_versions(project=project):
            vers = re.compile(r'\d+(\.\d+){0,5}').search(vert.name)
            if vers:
                if len(vers.group(0)) == len(vert.name):
                    _temp_l.append(vert.name)
        if _temp_l:
            _temp_l.sort(key=lambda x: tuple(int(v) for v in x.split('.')))
            if _temp_l.__len__() < 3:
                return _temp_l
            else:
                return _temp_l[-3], _temp_l[-2], _temp_l[-1]

    def get_projects(self):
        pjs = list()
        for pj in self.jira.projects():
            pjs.append((pj.key, pj.id))
        return pjs


if __name__ == '__main__':
    jh = JIRAHandler()
    for i in jh.get_projects():
        print(i)
        print(jh.read_project_versions(i[0]))
