from datetime import timedelta
from lmkp.models.database_objects import *
from lmkp.models.meta import DBSession
import logging
from pyramid.renderers import render
from pyramid.response import Response
from pyramid.view import view_config
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message

log = logging.getLogger(__name__)

class BaseView(object):
    """
    Base class for all view classes that need to be aware of the requested locale.
    """

    def __init__(self, request):
        self.request = request

    def _handle_parameters(self):
        # Check if language (_LOCALE_) is set
        if self.request is not None:
            response = self.request.response
            if '_LOCALE_' in self.request.params:
                response.set_cookie('_LOCALE_', self.request.params.get('_LOCALE_'), timedelta(days=90))
            elif '_LOCALE_' in self.request.cookies:
                pass


        # Check if profile (_PROFILE_) is set
        if self.request is not None:
            response = self.request.response
            if '_PROFILE_' in self.request.params:
                response.set_cookie('_PROFILE_', self.request.params.get('_PROFILE_'), timedelta(days=90))
            elif '_PROFILE_' in self.request.cookies:
                # Profile already set, leave it
                pass
            else:
                # If no profile is set, set 'global' profile
                response.set_cookie('_PROFILE_', 'global', timedelta(days=90))

    def _send_email(self, recipients, subject, body):
        """
        Sends an email message to all recipients using the SMTP host and default
        sender configured in the .ini file.
        """

        mailer = get_mailer(self.request)
        message = Message(subject=subject, recipients=recipients, body=body)
        mailer.send(message)

class MainView(BaseView):

    @view_config(route_name='db_test', renderer='lmkp:templates/db_test.pt')
    def db_test(self, request):

        from sqlalchemy import func, select
        from sqlalchemy import or_
        session1 = DBSession()

        #===========================================================================
        # # START OF TEST CASE to test database trigger preventing multiple 'active' activities
        # """
        # status1 = Status(id=1, name='status1')
        # status2 = Status(id=2, name='status2')
        # DBSession.add_all([status1, status2])
        # """
        # """
        # s1 = DBSession.query(Status).get(1)
        # s2 = DBSession.query(Status).get(2)
        # id1 = "c32212f8-e704-48e3-94bc-5670cfd01884"
        # id2 = "a6780ba4-bbd3-47e6-b739-6b7f29584272"
        # """
        # # add activity1 with status=1
        # """
        # a1 = Activity(activity_identifier=id1, version=1, point="POINT (10 20)")
        # a1.status = s1
        # DBSession.add(a1)
        # """
        # # update activity1 to status=2
        # """
        # a1 = DBSession.query(Activity).get(2)
        # a1.status = s2
        # import transaction
        # transaction.commit()
        # """
        # # add activity2 directly with status=2
        # """
        # a2 = Activity(activity_identifier=id2, version=1, point="POINT (10 20)")
        # a2.status = s2
        # DBSession.add(a2)
        # """
        # # try to add new version of activity1, also with status=2 (SHOULD FAIL)
        # """
        # a3 = Activity(activity_identifier=id1, version=2, point="POINT (10 20)")
        # a3.status = s2
        # DBSession.add(a3)
        # """
        # # the same version can be inserted if status != 2
        # """
        # a3 = Activity(activity_identifier=id1, version=2, point="POINT (10 20)")
        # a3.status = s1
        # DBSession.add(a3)
        # """
        # # it cannot be updated afterwards to status=2
        # """
        # a3 = DBSession.query(Activity).get(5)
        # a3.status = s2
        # import transaction
        # transaction.commit()
        # """
        # # END OF TEST CASE
        #===========================================================================

        #===========================================================================
        # # START OF TEST CASE to test main_tags
        # # some test values
        # id1 = "c32212f8-e704-48e3-94bc-5670cfd01884"
        # s1 = DBSession.query(Status).get(1)
        # k1 = DBSession.query(A_Key).get(1)
        # k2 = DBSession.query(A_Key).get(2)
        # v1 = DBSession.query(A_Value).get(1)
        # v2 = DBSession.query(A_Value).get(2)
        #
        # # add an activity with a tag group that contains a main tag
        # """
        # t1 = A_Tag()
        # t1.key = k1
        # t1.value = v1
        #
        # t2 = A_Tag()
        # t2.key = k2
        # t2.value = v2
        #
        # tg1 = A_Tag_Group()
        # tg1.tags = [t1, t2]
        # tg1.main_tag = t1
        #
        # a1 = Activity(activity_identifier=id1, version=1, point="POINT (10 20)")
        # a1.status = s1
        # a1.tag_groups = [tg1]
        #
        # DBSession.add(a1)
        # """
        #
        # # test it by querying it
        # """
        # q = DBSession.query(Activity).filter(Activity.activity_identifier == id1).first()
        # object = q.tag_groups[0].main_tag
        # """
        #===========================================================================

        object = "done"
        return {'object': object}

    @view_config(route_name='index', renderer='lmkp:templates/index.mak')
    def index(self):
        """
        Returns the main HTML page
        """

        self._handle_parameters()
        
        return {}

    @view_config(route_name='embedded_index', renderer='lmkp:templates/embedded.mak')
    def embedded_version(self):
        """
        Returns a version of the Land Observatory that can be embedded in other
        website or land portals. The main (and currently the only) difference to
        the normal index view is the missing combobox to select another profile.
        """

        # Get the requested profile from the URL
        profile = self.request.matchdict.get('profile', 'global')

        # Custom handling of the standard parameters: don't use method _handle_parameters
        # since we get the profile parameter from the routing and not as URL parameter.
        if self.request is not None:
            response = self.request.response
            # Manipulate the cookies of the request object to make sure, that
            # method get_current_profile in lmkp.views.profile gets the correct
            # profile.
            self.request.cookies['_PROFILE_'] = profile
            # Set the cookie with a validity of three months
            self.request.response.set_cookie('_PROFILE_', profile, timedelta(days=90))

            # Check if language (_LOCALE_) is set
            if '_LOCALE_' in self.request.params:
                response.set_cookie('_LOCALE_', self.request.params.get('_LOCALE_'), timedelta(days=90))
            elif '_LOCALE_' in self.request.cookies:
                pass

        return {}

    @view_config(route_name='enclosing_demo_site')
    def enclosing_demo_site(self):
        """
        This view provides a *very* simple example how the Land Observatory can
        be embedded in any website with a fixed profile and a hidden profile combobox.
        """

        html = """
<html>
    <head>
        <title>Embedded Land Observatory</title>
    </head>
    <body>
        <div style="width: 100%;">
            <div style="height: 10%;">
                This is a very basic example of how to embed the Land Observatory
                platform in a custom website using a HTML iframe:
                <pre>
&lt;iframe style="height: 90%; width: 100%; border: 0;" src="http://localhost:6543/embedded/Madagascar?_LOCALE_=fr"&gt;
&lt;/iframe&gt;
                </pre>
            </div>
            <div>
                <iframe style="height: 90%; width: 100%; border: 0;" src="http://localhost:6543/embedded/Madagascar?_LOCALE_=fr">
                </iframe>
            </div>
        </div>
    </body>
</html>
    """

        return Response(html, content_type='text/html', status_int=200)

    @view_config(route_name='moderation_html', renderer='lmkp:templates/moderation.mak', permission='moderate')
    def moderation_html(self):
        """
        Returns the moderation HTML page
        """

        self._handle_parameters()

        return {}

    @view_config(route_name='administration', renderer='lmkp:templates/administration.mak', permission='administer')
    def administration(self):
        """
        Returns the administration HTML page
        """

        self._handle_parameters()

        return {}

    @view_config(route_name='privileges_test', renderer='lmkp:templates/privilegestest.mak')
    def privileges_test(self):
        """
        Simple view to output the current privileges
        """
        return {}