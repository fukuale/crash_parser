# Author = 'Vincent FUNG'
# Create = '2017/10/19'
#                       ::
#                      :;J7, :,                        ::;7:
#                      ,ivYi, ,                       ;LLLFS:
#                      :iv7Yi                       :7ri;j5PL
#                     ,:ivYLvr                    ,ivrrirrY2X,
#                     :;r;j5P.7r:                :ivuksxerfnli.
#                    :iL7::,:::iiirii:ii;::::,,irvF7rvvLujL7ur
#                   ri::,:,::i:iiiiiii:i:irrv177JX7rYXqZEkvv17
#                ;i:, , ::::iirrririi:i:::iiir2XXvii;L8OGJr71i
#              :,, ,,:   ,::irii:i:::.irii:i:::j1jri7ZBOS7ivv,
#                 ,::,    ::rv77iiiriii:iii:i::,rvLrYXqZEk.Li
#             ,,      ,, ,:ir7ir::,:::i;ir:::i:i::rSGGYri712:
#           :::  ,v7r:: ::rrv77:, ,, ,:i7rrii:::::, ir7ri7Lri
#          ,     2OBBOi,iiir;r::        ,irriiii::,, ,iv7Luur:
#        ,,     i78MBBi,:,:::,:,  :7FSL: ,iriii:::i::,,:rLqXv::
#        :      iuMMP: :,:::,:ii;YRDEBB0viiii:i:iii:i:::iJqL;::
#       ,     ::::i   ,,,,, ::LuBBu BBBBBErii:i:i:i:i:i:i:r77ii
#      ,       :       , ,,:::rruBZ1MBBqi, :,,,:::,::::::iiriri:
#     ,               ,,,,::::i:  :i:i:i:i.       ,:,, ,:::ii;i7:
#    :,       rjujLYLi   ,,:::::,:::::::::,,   ,:i,:,,,,,::i:iii
#    ::      BBBBBBBBB0,    ,,::: , ,:::::: ,      ,,,, ,,:::::::
#    i,  ,  ,8@VINCENTBBi     ,,:,,     ,,, , ,   , , , :,::ii::i::
#    :      iZMOMOMBBM2::::::::::,,,,     ,,,,,,:,,,::::i:irr:i:::,
#    i   ,,:;u0MBMOG1L:::i::::::  ,,,::,   ,,, ::::::i:i:iirii:i:i:
#    :    ,iuUuuXUkFu7i:iii:i:::, :,:,: ::::::::i:i:::::iirr7iiri::
#    :     :rkwwiBivf.i:::::, ,:ii:::::::i:::::i::,::::iirrriiiri::,
#     :      5BMBBBBBBSr:,::rv2kuii:::iii::,:i:,, , ,,:,:ia5wf88s5.,
#          , :r50EZLEAVEMEALONEP7::::i::,:::::,: :,:,::i;rrririiii::
#              :jujYY7LS0ujJL7r::,::i::,::::::::::::::iirirrrrrrr:ii:
#           ,:  :::,: :,,:,,,::::i:i:::::::::::,,:::::iir;ii;7v7;ii;i,
#           ,,,     ,,:,::::::i:iiiii:i::::,, ::::iiiii;L8OGJrf.r;7:i,
#        , , ,,,:,,::::::::iiiiiiiiii:,:,:::::::::iiir;ri7vL77rrirri::
#         :,, , ::::::::i:::i:::i:i::,,,,,:,::i:i:::iir;:::i:::i:ii:::
#                          _
#                      o _|_           __
#                      |  |      (__| (__) (__(_
#                                   |
import time
from jira import JIRA
import urllib


class CreateJIRAIssue(object):
    def __init__(self):
        self.jira_addr = 'http://192.168.1.118:8080'
        self.acc = 'zhaoyefeng'
        self.acc_pwd = 'lancelot0318'
        self.jira = JIRA(self.jira_addr, basic_auth=(self.acc, self.acc_pwd))

    def create(self, pjname, priority, summary, environment, description):
        issue_fields = self.gen_fields_dict(pjname, priority, summary, environment, description)
        new_issue = self.jira.create_issue(fields=issue_fields)
        return new_issue

    def gen_fields_dict(self, pjname, priority, summary, environment, description):
        issue_dict = {
            'project': self.project(pjname),
            'issuetype': {'name': 'bug', 'id': '1'},
            'customfield_10004': self.customfield_10004(),  # 问题归属
            'customfield_10003': self.customfield_10003(),  # bug分类
            'summary': summary,
            'versions': [{'name': '1.1.0'}, {'name': '1.0.0'}],
            'customfield_10002': {'id': '10014', 'child': {'id': '10018'}},  # 严重程度
            'priority': self.priority(priority),
            'assignee': {'name': 'zhaoyefeng'},
            'environment': environment,
            'description': description,
            'reporter': {'name': 'haixiazhang'}
        }

        return issue_dict

    def project(self, value):
        method_name = 'project_' + str(value).lower()
        method = getattr(self, method_name)
        return method()

    def project_gameim(self):
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

        # def version(self, value):
        #     if isinstance(value, list):


class ReadFromJIRA(CreateJIRAIssue):
    def __init__(self):
        super(ReadFromJIRA, self).__init__()

    def read_desc(self, jiraId):
        return self.jira.issue(jiraId).fields.description

    def read_version(self, jiraId):
        return self.jira.issue(jiraId).fields.versions


class UpdateJIRA(CreateJIRAIssue):
    def __init__(self):
        super(UpdateJIRA, self).__init__()

    def update_desc(self, jiraId, descs):
        self.jira.issue(jiraId).update(description=descs)


if __name__ == '__main__':
    cj = CreateJIRAIssue()
    rj = ReadFromJIRA()
    uj = UpdateJIRA()
    # re = cj.create(pjname='sa', summary='testse', environment='woief', description='dese\nfese\ncon: wefwoefi', priority='urgen')
    print(rj.read_version('SA-370'))
    # desc = rj.read_desc(re)
    # desc_l = list()
    # for i in desc.split('\n'):
    #     if i.startswith('con:'):
    #         desc_l.append('con: w654w6ef1')
    #     else:
    #         desc_l.append(i)
    # desc_m = '\n'.join(desc_l)
    # uj.update_desc(re, desc_m)

    # print(desc)

    # print(re)
