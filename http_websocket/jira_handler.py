# Author = 'Vincent FUNG'
# Create = '2017/10/19'
import re

from jira import JIRA, JIRAError
import regular_common

class JIRAHandler(object):
    """JIRA handler"""
    def __init__(self):
        super(JIRAHandler, self).__init__()
        self.jira_addr = 'http://10.0.13.12:32774'
        self.acc = 'CrashParser'
        self.acc_pwd = 'qwer1234'
        self.jira = JIRA(self.jira_addr, basic_auth=(self.acc, self.acc_pwd))

    def create(self, pjname, priority, summary, environment, description, version):
        """Create a JIRA ticket.

        Arguments:
            pjname {String} -- [The project want to create to.]
            priority {Dictionary} -- [The priority want to set.]
            summary {String} -- [The ticket summary.]
            environment {String} -- [The env. of this ticket.]
            description {String} -- [The ticket description.]
            version {String} -- [The version want to ceate.]

        Returns:
            [String] -- [The result of create perform.]
        """

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

        try:
            return self.jira.create_issue(fields=issue_dict)
        except JIRAError as jira:
            return jira.text

    def project(self, value):
        """Get project id via project name.

        Arguments:
            value {String} -- [The name of project.]

        Returns:
            [Dictionary] -- [The id of project.]
        """
        method_name = 'project_' + str(value).lower()
        method = getattr(self, method_name)
        return method()

    def project_wegamers(self):
        """WeGamers id.
        """
        return {'id': '10400'}

    def project_gamelive(self):
        """StreamCraft id.
        """
        return {'id': '10500'}

    def project_streamcraft(self):
        """StreamCraft id.
        """
        return {'id': '10500'}

    def project_messenger(self):
        """LINKMESSENGER id.
        """
        return {'id': '10200'}

    def project_sa(self):
        """5KROSE id.
        """
        return {'id': '10100'}

    def customfield_10004(self):
        """The id of issue belongs.
        """
        return {'id': '10068'}

    def customfield_10003(self):
        """The id of issue category
        """
        return {'id': '10029'}

    def priority(self, value):
        """The priority of issue.

        Arguments:
            value {String} -- [The follow value will be accept. 0)urgen 1)normal 2)later]

        Returns:
            [Dictionary] -- [The id of priority in JIRA.]
        """
        method_name = 'priority_' + str(value).lower()
        method = getattr(self, method_name)
        return method()

    def priority_urgen(self):
        """Urgen
        """
        return {'id': '1'}

    def priority_normal(self):
        """Normal
        """
        return {'id': '3'}

    def priority_later(self):
        """Later
        """
        return {'id': '4'}

    def version(self, value):
        """Make version list or string to dictionary type.

        Arguments:
            value {List, String} -- [The(se) versions set in this issue.]

        Returns:
            [Dictionary] -- [The(se) versions has releationship with this issue.]
        """
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
        """Read issue from JIRA with jira_id.

        Arguments:
            jira_id {Stirng} -- [The id of issue.]

        Returns:
            [jira.resources.Issue] -- [The issue instance.]
        """
        return self.jira.issue(jira_id)

    def update_issue(self, issue, version=False, summary=False):
        """Update a existing issue to JIRA

        Arguments:
            issue {jira.resources.Issue} -- [The issue instance.]

        Keyword Arguments:
            version {List} -- [The versions want to update.] (default: {False})
            summary {String} -- [The summary want to udpate.] (default: {False})

        Returns:
            [] -- [description]
        """
        # TODO: Merge udpate dict.
        if version and summary:
            self.version(version)
            return issue.update(fields={'versions': self.version(version), 'summary': summary})
        elif version and not summary:
            return issue.update(fields={'versions': self.version(version)})
        elif summary and not version:
            return issue.update(fields={'summary': summary})

    def read_project_versions(self, project_name):
        """Get all versions with the specified project.

        Arguments:
            project_name {String} -- [The name of the project.]

        Returns:
            [List] -- [The biggest 5 versons of getting versions. all if not enough.]
        """
        _versions_l = list()
        for ver_jira in self.jira.project_versions(project=project_name):
            # Filter the truthly version number.
            ver_aft = regular_common.version_number(ver_jira.name)
            if ver_aft:
                # Ensure the completeness of version number.
                # This is an invalid version number if does not match.
                if len(ver_aft.group(0)) == len(ver_jira.name):
                    _versions_l.append(ver_jira.name)
        if _versions_l.__len__() > 0:
            _versions_l.sort(key=lambda x: tuple(int(v) for v in x.split('.')))
            if _versions_l.__len__() < 5:
                return _versions_l
            else:
                return _versions_l[-5:]

    def get_projects(self):
        """Get projects from JIRA server.

        Returns:
            [List] -- [The list of projects.]
        """
        _l_projects = list()
        for project in self.jira.projects():
            _l_projects.append((project.key, project.id))
        return _l_projects
