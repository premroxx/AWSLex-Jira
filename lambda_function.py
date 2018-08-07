import sys
import json
import requests
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def create_jira(jira_server, jira_user, jira_pw, data):
    print('creating new Jira issue')
    url = 'https://' + jira_server + '/rest/api/2/issue/'

    headers = {'Content-type': 'application/json'}

    try:
        req = requests.post(url, auth=(jira_user, jira_pw), data=data, headers=headers, verify=False)

        # check return
        if not req.status_code in range(200, 206):
            print('Error connecting to Jira.. check config file')
            sys.exit()
        jira = req.json()
        return jira['key']
    except requests.exceptions.Timeout:
        print('Timeout trying to connect to jira')
    except requests.exceptions.RequestException as exep:
        # catastrophic error. bail.
        print('error connecting to jira: ' + str(exep))
    except:
        print('error creating new Jira ticket')


def update_jira(jira_server, jira_user, jira_pw, data, jira_key):
    print('updating Jira issue %s' % jira_key)
    headers = {'Content-type': 'application/json'}
    url = 'https://' + jira_server + '/rest/api/2/issue/' + jira_key

    try:
        req = requests.put(url, auth=(jira_user, jira_pw), data=data, headers=headers, verify=False)
        print req.status_code

        # check return
        if not req.status_code in range(200,206):
            print('Error connecting to Jira.. check config file')
            sys.exit()
        else:
            print('Jira ticket %s updated successfully' % jira_key)
    except requests.exceptions.Timeout:
        print('Timeout trying to connect to jira')
    except requests.exceptions.RequestException as exep:
        # catastrophic error. bail.
        print('error connecting to jira: ' + str(exep))


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }
    print(response)

    return response


def lambda_handler(event, context):

    data = '{"fields":{"project":{"key":"PT1"}, "summary": "Summary2","description":"my Desc","issuetype":{"name":"Story"}}}'
    data = json.loads(data)
    data['fields']['summary'] = event['currentIntent']['slots']['TicketName']
    #data['fields']['summary'] = 'Summary3'
    data = json.dumps(data, ensure_ascii=False)
    jira = create_jira('.atlassian.net', '', '', data)

    data = '{"fields":{"assignee":{"name":""}}}'
    data = json.loads(data)
    data['fields']['assignee']['name'] = event['currentIntent']['slots']['JiraUserName']
    #data['fields']['assignee']['name'] = 'premxkumar'
    data = json.dumps(data, ensure_ascii=False)
    update_jira('', '', '', data, str(jira))

    #data = '{"dialogAction": {"type": "Close", "fulfillmentState": "Fulfilled", "message": {"contentType": "PlainText","content": ""}}}'
    #data = json.loads(data)
    #data = 'Ticket ' + str(jira) + 'created and assigned to ' + event['currentIntent']['slots']['JiraUserName']
    data = "Ticket " + str(jira) + " created and assigned to " + event['currentIntent']['slots']['JiraUserName']
    #data['dialogAction']['message']['content'] = 'Ticket ' + str(jira) + ' and assigned to ' + 'premxkumar'
    #data = 'Ticket ' + str(jira) + ' and assigned to ' + 'premxkumar'
    #data = json.dumps(data, ensure_ascii=False)
    #print data
    #return data

    #return close(event['sessionAttributes'], 'Fulfilled', {'contentType': 'PlainText', 'content': json.parse(data)})
    return close(event['sessionAttributes'], 'Fulfilled', {'contentType': 'PlainText', 'content': data})


if __name__ == '__main__':
    lambda_handler(event=None, context=None)