from lmkp.tests.moderation_activities import *
from lmkp.tests.create.create_activities import *
from lmkp.tests.create.create_stakeholders import *
from lmkp.tests.edit_activities import *

from pyramid.view import view_config

@view_config(route_name='moderation_tests', renderer='json', permission='administer')
def moderation_tests(request):

    # ['CA01'] / ['CS01'] / True / False
    doCreateTests = False
    # ['EA01'] / ['ES01'] / True / False
    doEditTests = False
    # ['MA01'] / ['MS01'] / True / False
    doModerationTests = False

    verbose = False

    print ""
    print ""
    print ""
    print ""
    print ""
    print ""
    print "********************************************************************"
    print "********************   Starting test suite   ***********************"
    print "********************************************************************"

    testCount = 0
    errorStack = []

    """
    Create
    """
    if (doCreateTests is True or (isinstance(doCreateTests, list)
        and len(doCreateTests) > 0)):

        createTests = [
            CreateActivities01(request),
            CreateActivities02(request),
            CreateActivities03(request),
            CreateActivities04(request),
            CreateActivities05(request),
            CreateActivities06(request),
            CreateActivities07(request),
            CreateActivities08(request),
            CreateActivities09(request),
            CreateActivities10(request),
            CreateActivities11(request),
            CreateActivities12(request),
            CreateActivities13(request),
            CreateActivities14(request),
            CreateStakeholders01(request),
            CreateStakeholders02(request),
            CreateStakeholders03(request),
            CreateStakeholders04(request),
            CreateStakeholders05(request),
            CreateStakeholders06(request),
            CreateStakeholders07(request),
            CreateStakeholders08(request),
            CreateStakeholders09(request),
            CreateStakeholders10(request),
            CreateStakeholders11(request),
            CreateStakeholders12(request),
            CreateStakeholders13(request)
        ]

        # Test the setup
        print ""
        print "-----------------   [Create] Testing the setup   -------------------"
        print ""
        validCreateSetup = True
        for test in createTests:

            if (isinstance(doCreateTests, list)
                and test.testId not in doCreateTests):
                continue

            log.debug('[Create] Testing setup of test case %s' % test.testId)
            success = test.testSetup()
            if not success:
                log.debug('[Create] Setup of test case %s is not valid!' % test.testId)
            validCreateSetup = success and validCreateSetup

        # If the setup is ok, do the tests
        if validCreateSetup is True:
            log.debug('Test setup is valid!')
            print ""
            print "-----------------   [Create] Running the tests   -------------------"
            print ""
            for test in createTests:

                if (isinstance(doCreateTests, list)
                    and test.testId not in doCreateTests):
                    continue

                log.debug('[Create] Running test case %s' % test.testId)
                success = test.doTest(verbose)
                if success is True:
                    testCount += len(test.results)
                if not success:
                    for r in test.results:
                        if r.success is not True:
                            errorMessage = ('[Create] A test of test case %s (%s) failed with message: \n%s'
                                % (test.testId, test.testDescription, r.msg))
                            log.debug(errorMessage)
                            errorStack.append(errorMessage)

    """
    Edit / Update
    """
    if (doEditTests is True or (isinstance(doEditTests, list)
        and len(doEditTests) > 0)):

        editTests = [
            EditActivities01(request),
            EditActivities02(request),
            EditActivities03(request)
        ]

        # Test the setup
        print ""
        print "------------------   [Edit] Testing the setup   --------------------"
        print ""
        validEditSetup = True
        for test in editTests:

            if (isinstance(doEditTests, list)
                and test.testId not in doEditTests):
                continue

            log.debug('[Edit] Testing setup of test case %s' % test.testId)
            success = test.testSetup()
            if not success:
                for r in test.results:
                    if r.success is not True:
                        errorMessage = ('[Edit] Setup of test case %s is not valid: %s'
                            % (test.testId, r.msg))
                        log.debug(errorMessage)
                        errorStack.append(errorMessage)
            validEditSetup = success and validEditSetup

        # If the setup is ok, do the tests
        if validEditSetup is True:
            log.debug('Test setup is valid!')
            print ""
            print "------------------   [Edit] Running the tests   --------------------"
            print ""
            for test in editTests:

                if (isinstance(doEditTests, list)
                and test.testId not in doEditTests):
                    continue

                log.debug('[Edit] Running test case %s' % test.testId)
                success = test.doTest(verbose)
                if success is True:
                    testCount += len(test.results)
                if not success:
                    for r in test.results:
                        if r.success is not True:
                            errorMessage = ('[Edit] A test of test case %s (%s) failed with message: \n%s'
                                % (test.testId, test.testDescription, r.msg))
                            log.debug(errorMessage)
                            errorStack.append(errorMessage)

    """
    Moderation / Review
    """
    if (doModerationTests is True or (isinstance(doModerationTests, list)
        and len(doModerationTests) > 0)):

        moderationTests = [
            ModerationActivities01(request)
        ]

        # Test the setup
        print ""
        print "---------------   [Moderation] Testing the setup   -----------------"
        print ""
        validModerationSetup = True
        for test in moderationTests:

            if (isinstance(doModerationTests, list)
                and test.testId not in doModerationTests):
                continue

            log.debug('[Moderation] Testing setup of test case %s' % test.testId)
            success = test.testSetup()
            if not success:
                for r in test.results:
                    if r.success is not True:
                        errorMessage = ('[Moderation] Setup of test case %s is not valid: %s'
                            % (test.testId, r.msg))
                        log.debug(errorMessage)
                        errorStack.append(errorMessage)
            validModerationSetup = success and validModerationSetup

        # If the setup is ok, do the tests
        if validModerationSetup is True:
            log.debug('Test setup is valid!')
            print ""
            print "---------------   [Moderation] Running the tests   -----------------"
            print ""
            for test in moderationTests:

                if (isinstance(doModerationTests, list)
                and test.testId not in doModerationTests):
                    continue

                log.debug('[Moderation] Running test case %s' % test.testId)
                success = test.doTest(verbose)
                if success is True:
                    testCount += len(test.results)
                if not success:
                    for r in test.results:
                        if r.success is not True:
                            errorMessage = ('[Moderation] A test of test case %s (%s) failed with message: \n%s'
                                % (test.testId, test.testDescription, r.msg))
                            log.debug(errorMessage)
                            errorStack.append(errorMessage)


    print ""
    print "********************************************************************"
    print "*********************   End of test suite   ************************"
    print "********************************************************************"
    print ""

    print "------------------------   Test results   --------------------------"
    print ""
    if ((doCreateTests is not False and validCreateSetup is True)
        or (doModerationTests is not False and validModerationSetup is True)
        or (doEditTests is not False and validEditSetup is True)):
        log.debug('Ran a total of %s tests, %s of them failed.'
            % (testCount, len(errorStack)))
    else:
        log.debug('Test setup is not valid!')

    if len(errorStack) > 0:
        print ""
        print "*** ERRORS ***"
        for e in errorStack:
            print e

    return {
        'tests': testCount,
        'errors': len(errorStack),
        'info': 'See log for details'
    }