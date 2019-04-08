from service import Service
from multiprocessing.pool import ThreadPool
import csv, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

settingsInfo = []

# // exceptions to 0 seat rule. format is 'partner name, domain'
excludeddomains = ['partner-name, domain.com',]

adjusted_list = []

def main():
    serv = Service()
    partners = serv.reseller_list("partner")

    # // multithread
    pool = ThreadPool(20)
    pool.map(process_customers, partners['reseller'])

    # // single thread
    # for i in partners['reseller']:
    #     print(i)
    #     process_customers(i)
    # # process_customers('single_customer')

    # // remove special case 0 seats from list
    compare = set(settingsInfo) - set(excludeddomains)
    for each in compare:
        adjusted_list.append(each)

    print(adjusted_list)

    fill('userlist.csv', adjusted_list)

    # send_email('userlist.csv')

    return


def process_customers(partner):
    partner_id = partner['name']
    # partner_id = 'single_customer'
    serv = Service()
    try:
        customer_list = serv.customer_list(partner_id)['customer']
    except:
        return "No customers"
    if type(customer_list) == dict:
        process_customer(customer_list, serv, partner_id)
        # results.append(result)
    elif type(customer_list) == list:
        for customer in customer_list:
            process_customer(customer, serv, partner_id)
            # results.append(result)
    return


def process_customer(customer_list, serv, partner):
    domains = serv.domain_list(customer_list['name'])
    if not domains:
        return
    return process_mail(domains, serv, partner)


def process_mail(domains, serv, partner):
    '''response:
    {'relaycheckserver': '', 'filtertype': 0, 'mailboxsize': 100, 'relayserver': '1.1.1.1',
    'usercount': 2, 'domainname': 'domain.com', 'advancedrouting': 0, 'spamhandling': 1,
    'destinationtype': 1, 'relaycheck': 0, 'bouncemanagement': 1, 'phrase': '',
    'destinationserver': 'mailserver.net:2501#1'}
    '''

    data = []
    if not domains:
        return
    if type(domains['domain']) == list:
            data.append(process_domain(domains['domain'], serv, partner))

    elif type(domains['domain']) == dict:
        if domains['domain']['type'] == 1:
            # print(data)
            data.append(process_domain(domains['domain'], serv, partner))
    return

def process_domain(domain, serv, partner):
    # domain name from list vs dict
    try:
        domain_name = domain['name']
    except:
        domain_name = domain[0]['name']
    config_settings = serv.get_mail_config(domain_name)
    print(domain_name)
    # print(config_settings)
    try:
        print(config_settings['usercount'])
        if config_settings['usercount'] == 0:
            settingsInfo.append(partner + ', ' + domain_name)
    except:
        print('0 users')
        settingsInfo.append(partner + ', ' + domain_name)
    # settingsInfo['domain_name'] = domain_name
    # settingsInfo['config_settings'] = config_settings
    # if 'destinationserver' in config_settings:
    #     settingsInfo['inbound_ip'] = config_settings['destinationserver']
    # if 'relayserver' in config_settings:
    #     settingsInfo['outbound_ip'] = config_settings['relayserver']
    # if 'usercount' in config_settings:
    #     settingsInfo['seats'] = config_settings['usercount']
    # settingsInfo['product_code'] = format_product(ec.get_config_continuity(domain_name))
    return

def fill(csvname, info):
    with open(csvname, 'w+', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter='\n')
        # print(info)
        for i in info:
            writer.writerow([i])

def send_email(domainscsv):
    fromaddr = "xxxx@xxxxxxx.com"
    toaddr = ["xxxx@xxxxxxx.com"]
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = "  ,".join(toaddr)
    msg['Subject'] = "Customers with 0 seats"
    body = 'Please see attached csv for customers with 0 seats'
    msg.attach(MIMEText(body, 'plain'))

    part = MIMEBase('application', "octet-stream")
    part.set_payload(open(domainscsv, "rb").read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="userlist.csv"')
    msg.attach(part)

    server = smtplib.SMTP('outboundrelay.server.com', 25)
    server.ehlo()
    server.starttls()
    server.ehlo()
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    print('email sent')

if __name__ == "__main__":
    main()
