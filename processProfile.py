__author__ = 'adarsh'

'''
    This file will pick up the json files generated from the FB and Open Bank APi
    It will load these and process it to get the profile out.
'''

import json
import webbrowser

PROFILE_1_LIMIT=40000
PROFILE_2_LIMIT=60000
PROFILE_3_LIMIT=80000
MY_BANK_FILE_NAME = '121212.json'
MY_MORTGAGE_RESULTS_FILE = 'results.html'

def main():
    '''
    :writes the product output to file
    '''


    myBankInfo = json.load(open(MY_BANK_FILE_NAME))

    #extract info from the bank json
    # take it from the last transaction
    custName = myBankInfo['transactions'][0]['this_account']['holders'][0]['name']
    balanceDict = myBankInfo['transactions'][0]['details']['new_balance']
    myBalanceAmount = float(balanceDict['amount'])
    myCcy = balanceDict['currency']
    print str(myBalanceAmount) + ' ' + myCcy
    mySalary = myRent = myBasic = myDiscretionary = 0

    htmlMsg = """<html>
                <head></head>
                <body><p>
                """
    customerBankDetals = [('Customer Name', custName)]
    customerBankDetals.append(('Bank Balance',numFmt(myBalanceAmount, myCcy)))

    #extract salary info
    for i in range(0,len(myBankInfo['transactions'])):
        if myBankInfo['transactions'][i]['metadata']['tags'] in ['Salary']:
            mySalary = float(myBankInfo['transactions'][i]['details']['value']['amount'])
        if myBankInfo['transactions'][i]['metadata']['tags'] in ['Rent']:
            myRent = -1*float(myBankInfo['transactions'][i]['details']['value']['amount'])
        if myBankInfo['transactions'][i]['metadata']['tags'] in ['Basic']:
            myBasic = -1*float(myBankInfo['transactions'][i]['details']['value']['amount'])
        if myBankInfo['transactions'][i]['metadata']['tags'] in ['Discretionary']:
            myDiscretionary = -1*float(myBankInfo['transactions'][i]['details']['value']['amount'])

    print 'salary = ' + str(mySalary)
    print 'rent = ' + str(myRent)
    print 'basic = ' + str(myBasic)
    print 'discretionary = ' + str(myDiscretionary)
    currentSavings = (mySalary - myRent - myBasic - myDiscretionary)

    customerBankDetals.append(('Salary', numFmt(mySalary, myCcy)))
    customerBankDetals.append(('Rent', numFmt(myRent, myCcy)))
    customerBankDetals.append(('Basic',numFmt(myBasic, myCcy)))
    customerBankDetals.append(('Discretionary',numFmt(myDiscretionary, myCcy)))
    customerBankDetals.append(('Current Savings / month', numFmt(currentSavings,myCcy)))

    htmlMsg += makeHTMLTable('Item','Amount',customerBankDetals)
    #htmlMsg += '<br></br>'

    # Send this info to mortgage calculator
    myMortgageProduct = getMyMortgage(myBalanceAmount, mySalary, myRent, myBasic+myDiscretionary)
    monthlyMortgagePayments = getMortgagePayments(myMortgageProduct)
    print myMortgageProduct

    mortgageProductDetails =[('Est. Property Value in budget', numFmt(myMortgageProduct[0], myCcy))]
    mortgageProductDetails.append(('Downpayment required', numFmt(myMortgageProduct[1], myCcy)))
    mortgageProductDetails.append(('Mortgage Amount',numFmt(myMortgageProduct[2], myCcy)))
    mortgageProductDetails.append(('Rate (annualized)',numFmt(myMortgageProduct[3], '%')))
    mortgageProductDetails.append(('Term', numFmt(myMortgageProduct[4], 'years')))

    htmlMsg += makeHTMLTable('Item','Amount',mortgageProductDetails)

    futureSavings = (mySalary - monthlyMortgagePayments - myBasic - myDiscretionary)
    savingsDetails = [('New Bank Balance (after downpayment)', numFmt(myBalanceAmount - myMortgageProduct[1], myCcy))]
    savingsDetails.append(('Salary', numFmt(mySalary, myCcy)))
    savingsDetails.append(('Monthly Mortgage Payments',numFmt(monthlyMortgagePayments, myCcy)))
    savingsDetails.append(('Basic',numFmt(myBasic, myCcy)))
    savingsDetails.append(('Discretionary',numFmt(myDiscretionary, myCcy)))
    savingsDetails.append(('Future Savings / month', numFmt(futureSavings,myCcy)))
    savingsDetails.append(('Additional Savings', numFmt(myRent- monthlyMortgagePayments , myCcy)))

    htmlMsg += '<br>Future outlook, with a new house!</br>'
    htmlMsg += makeHTMLTable('Item','Amount',savingsDetails)

    #zoopla connection
    #to pull out house address/ price details
    houseDetails = [('36/8 Rodney St, Cannonmils - 3BR', numFmt(130000, 'GBP'))]
    houseDetails.append(('5/7 Dean Bank Lane, Stockbridge EH3 - 1BR',numFmt(135000,'GBP')))
    houseDetails.append(('Lothian Street, Old Town - 1BR',numFmt(129000,'GBP')))
    houseDetails.append(('2 Abbey Street EH7 5SJ - 2BR',numFmt(140000,'GBP')))
    houseDetails.append(('Dryden St. EH2 96G - 1BR',numFmt(140000,'GBP')))
    houseDetails.append(('Hawkhill Close, Lochend - 1BR',numFmt(130000,'GBP')))

    htmlMsg += '<br>Sample homes within your budget (from Zoopla)</br>'
    htmlMsg += makeHTMLTable('House details','Valuation',houseDetails)

    htmlMsg += """</p></body>
                </html>
              """
    writeHTML(htmlMsg)
    webbrowser.open(MY_MORTGAGE_RESULTS_FILE)


def getMyMortgage(balance, salary, rent, expenses):
    annualVal = (balance*1.2 + salary*12)

    if annualVal > PROFILE_1_LIMIT and annualVal < PROFILE_2_LIMIT:
        #propertyValuation =  annualVal*1.6
        propertyValuation = 110000
        rate = 4.6 #percent annual
    elif annualVal > PROFILE_2_LIMIT and annualVal < PROFILE_3_LIMIT:
        #propertyValuation= annualVal*2.3
        propertyValuation = 140000
        rate = 4.2
    else:
        #propertyValuation= annualVal*3.4
        propertyValuation  = 160000
        rate = 4.1
    downpaymentAmount = propertyValuation*0.2
    term = 25#25 years
    mortgageAmount = propertyValuation - downpaymentAmount
    stampDuty = propertyValuation * 0.01
    return (propertyValuation, downpaymentAmount, mortgageAmount, rate, term)

def getMortgagePayments(mortgageProduct):
    mRate = (mortgageProduct[3]/12)/100
    term = mortgageProduct[4]*12
    potentialMortgagePayments = mortgageProduct[2]*(mRate*(1+mRate)**term)/((1+mRate)**term-1)
    return round(potentialMortgagePayments,2)

def writeHTML(message):
    f = open(MY_MORTGAGE_RESULTS_FILE, 'w')
    f.write(message)
    f.close()

def makeHTMLTable(col1Name, col2Name, data):
    htmlTable = '<table border=1<tr> <th>{0}</th><th>{1}</th>'.format(col1Name, col2Name)
    for key, val in data:
        htmlTable += '<tr><td>{0}</td><td>{1}</td></tr>'.format(key, val)
    htmlTable+= '</table>'
    return htmlTable

def numFmt(number, ccy):
    '''
    number formatting for correct representation of money
    :param number: amount; ccy:currency code
    :return:string representation of the number for html
    '''
    str = '{0:,}'.format(number)
    str += ' ' + ccy
    return str

if __name__ == '__main__':
    ''' main routine entry '''
    main()