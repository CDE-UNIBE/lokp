from selenium.common.exceptions import NoSuchElementException     

BASE_URL = 'http://localhost:6543'
USERNAME = 'admin'
PASSWORD = 'asdf'

LOGIN_BUTTON = 'Login'.upper()
USERNAME_BUTTON = USERNAME.upper()
MAP_VIEW_TITLE = 'Map View'
DEAL_DETAILS_TITLE = 'Deal Details'
VIEW_DEAL_LINK = 'View the Deal.'
PENDING_VERSION = 'Pending version'.upper()
REVIEW_LINK = 'Review'
DEAL_MODERATION_TITLE = 'Deal Moderation'
APPROVE_BUTTON = 'Approve'
DEAL_EDITOR_TITLE = 'Deal Editor'
STAKEHOLDER_EDITOR_TITLE = 'Stakeholder Editor'
DEAL_STAKEHOLDER_LINK = 'View Stakeholder'
STAKEHOLDER_DETAILS_TITLE = 'Stakeholder Details'
STAKEHOLDER_DEAL_LINK = 'View Deal'
STAKEHOLDER_MODERATION_TITLE = 'Investor Moderation'

def createUrl(url):
    return '%s%s' % (BASE_URL, url)

def checkElExists(driver, by, element):
    try:
        if by == 'link_text':
            driver.find_element_by_link_text(element)
        elif by == 'tag_name':
            driver.find_element_by_tag_name(element)
        elif by == 'class_name':
            driver.find_element_by_class_name(element)
        else:
            return False
    except NoSuchElementException:
        return False
    return True

def checkIsPending(driver):
    try:
        pending = driver.find_element_by_tag_name('h4')
        if PENDING_VERSION not in pending.text:
            return False
    except NoSuchElementException:
        return False
    return True
    

def doLogin(driver):
    driver.get(createUrl('/login'))
    driver.find_element_by_name('login').send_keys(USERNAME)
    driver.find_element_by_name('password').send_keys(PASSWORD)
    driver.find_element_by_name('form.submitted').click()

def doCreateActivity(driver, dd1='[A] Value A1', nf1=123.45, noSubmit=False, 
    createSH=False, shValues={}):
    
    driver.get(createUrl('/activities/form'))
    driver.find_element_by_class_name('olMapViewport').click()
    driver.find_element_by_xpath("//select[@name='[A] Dropdown 1']/option[@value='%s']" % dd1).click()
    driver.find_element_by_id('activityformstep_2').click()
    driver.find_element_by_xpath("//input[@name='[A] Numberfield 1']").send_keys(str(nf1))
    
    if createSH is True:
        driver.find_element_by_id('activityformstep_3').click()
        shbtn = driver.find_elements_by_class_name('accordion-toggle')
        for el in shbtn:
            el.click()
        driver.find_element_by_name('createinvolvement_primaryinvestor').click()
        doCreateStakeholder(driver, shValues=shValues)
    
    if noSubmit is True:
        return
        
    driver.find_element_by_id('activityformsubmit').click()
    
    link = driver.find_element_by_link_text(VIEW_DEAL_LINK).get_attribute('href')
    uid = link.split('/')[len(link.split('/'))-1]
    
    return uid

    
def doCreateStakeholder(driver, tf1='Stakeholder Name', nf1=234.5, shValues={}):
    
    if shValues != {}:
        tf1 = shValues['tf1'] if 'tf1' in shValues else tf1
        nf1 = shValues['nf1'] if 'nf1' in shValues else nf1
    
    driver.find_element_by_xpath("//input[@name='[SH] Textfield 1']").send_keys(tf1)
    driver.find_element_by_id('stakeholderformstep_15').click()
    driver.find_element_by_xpath("//input[@name='[SH] Numberfield 1']").send_keys(str(nf1))
    driver.find_element_by_id('stakeholderformsubmit').click()


def doReview(driver, aOrSh, uid, reject=False, withInv=False):
    
    type = 'activities'
    if aOrSh == 'sh':
        type = 'stakeholders'
    
    driver.get(createUrl('/%s/review/%s' % (type, uid)))
    
    # withInv is only valid vor Activities
    if withInv is True and aOrSh == 'a':
        driver.find_element_by_xpath("//a[contains(@href, '/stakeholders/review/')]").click()
        driver.find_element_by_xpath("//button[contains(concat(' ', @class, ' '), ' btn-success ') and contains(text(), '%s')]" % APPROVE_BUTTON).click()
        driver.find_element_by_link_text('Click here to return to the Activity and review it.').click()
    
    if reject is False:
        driver.find_element_by_xpath("//button[contains(concat(' ', @class, ' '), ' btn-success ') and contains(text(), '%s')]" % APPROVE_BUTTON).click()
    else:
        # TODO
        pass
